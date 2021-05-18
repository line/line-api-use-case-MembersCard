import os
import json
import math
import random
import datetime
from decimal import Decimal

from dateutil.tz import gettz
from dateutil.relativedelta import relativedelta
import logging

import send_message
from common import (utils, line)
from validation.members_card_param_check import MembersCardParamCheck
from members_card.members_card_user_info import MembersCardUserInfo
from members_card.members_card_product_info import MembersCardProductInfo
from common.channel_access_token import ChannelAccessToken

# 環境変数の宣言
OA_CHANNEL_ID = os.getenv('OA_CHANNEL_ID')
LOGGER_LEVEL = os.getenv('LOGGER_LEVEL')
LIFF_CHANNEL_ID = os.getenv('LIFF_CHANNEL_ID', None)

# ログ出力の設定
logger = logging.getLogger()
if LOGGER_LEVEL == 'DEBUG':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# テーブル操作クラスの初期化
user_info_table_controller = MembersCardUserInfo()
product_info_table_controller = MembersCardProductInfo()
access_token_table_controller = ChannelAccessToken()


def lambda_handler(event, context):
    logger.info(event)

    req_param = json.loads(event['body'])

    # パラメータのバリデーションチェック
    param_checker = MembersCardParamCheck(req_param)
    if error_msg := param_checker.check_api_members_card():
        error_msg_disp = ('\n').join(error_msg)
        logger.error(error_msg_disp)
        return utils.create_error_response(error_msg_disp, status=400)  # noqa: E501

    # idTokenよりユーザーIDを取得
    try:
        user_profile = line.get_profile(
            req_param['idToken'], LIFF_CHANNEL_ID)
        if 'error' in user_profile and 'expired' in user_profile['error_description']:  # noqa 501
            return utils.create_error_response('Forbidden', 403)
        else:
            req_param['userId'] = user_profile['sub']
    except Exception:
        logger.exception('不正なIDトークンが使用されています')
        return utils.create_error_response('Error')

    user_id = user_profile['sub']

    mode = req_param['mode']
    # modeによって振り分ける
    try:
        if mode == 'init':
            result = init(user_id)
        elif mode == 'buy':
            result = buy(
                user_id, req_param['language'])

    except Exception as e:
        logger.error(e)
        return utils.create_error_response('ERROR')
    success_response = json.dumps(result,
                                  default=utils.decimal_to_int,
                                  ensure_ascii=False)
    return utils.create_success_response(success_response)


def init(user_id):
    """
    初期表示時、新規ユーザーの場合会員データを作成する。

    Parameters
    ----------
    user_id : str
        LINEのユーザーID

    Returns
    -------
    dict
        更新後のユーザー情報
    """
    user_info = user_info_table_controller.get_item(user_id)
    # ログインユーザーのデータが無い場合、ユーザーデータを作成する
    if not user_info:
        return create_new_user(user_id)

    return user_info


def buy(user_id, language):
    """
    商品を購入し、ポイント付与のDB更新と電子レシートの送信を行う。
    Parameters
    ----------
    user_id : str

    Returns
    -------
    dict
        更新後のユーザー情報

    """
    # 購入商品のランダム取得
    table_size = product_info_table_controller.get_table_size()
    # NOTE:サンプル商品を増やさないと決まった場合、tableSize部分に直接数値を入れた方が良い(パフォーマンス向上)
    product_id = random.randint(1, table_size)
    product_info = product_info_table_controller.get_item(product_id)

    # 付与ポイントの取得
    user_info = user_info_table_controller.get_item(user_id)
    before_awarded_point = user_info['point']
    add_point = math.floor(product_info['unitPrice'] * Decimal(0.05))
    after_awarded_point = before_awarded_point + add_point

    # 更新期限日の取得
    today = datetime.datetime.now(gettz('Asia/Tokyo'))
    expiration_date = (today + relativedelta(years=1)
                       ).strftime('%Y/%m/%d')

    # DB更新
    user_info_table_controller.update_point_expiration_date(
        user_id, after_awarded_point, expiration_date)

    user_info['pointExpirationDate'] = expiration_date
    user_info['point'] = after_awarded_point

    # メッセージ送信
    oa_channel_access_token = access_token_table_controller.get_item(
        OA_CHANNEL_ID)['channelAccessToken']
    send_message.send_push_message(
        oa_channel_access_token, user_id, product_info, language)

    return user_info


def create_new_user(user_id):
    """
    新規ユーザーの作成

    Parameters
    ----------
    user_id : str
        LINEユーザーID

    Returns
    -------
    dict
        ユーザー情報
    """
    barcode_num = create_barcode_num()
    # バーコードが重複した場合、１回までリトライしバーコード生成を行う。
    if not barcode_num:
        barcode_num = create_barcode_num()

    expiration_date = ''
    point = 0
    item = {
        'userId': user_id,
        'barcodeNum': barcode_num,
        'pointExpirationDate': expiration_date,
        'point': point,
    }
    user_info_table_controller.put_item(
        user_id, barcode_num, expiration_date, point)

    return item


def create_barcode_num():
    """
    バーコードを生成する。

    Returns
    -------
    str
        生成したバーコード
        重複する場合空文字を返す
    """
    barcode_num = random.randrange(10**12, 10**13)
    items = user_info_table_controller.query_index_barcode_num(barcode_num)
    if items:
        return ''

    return barcode_num

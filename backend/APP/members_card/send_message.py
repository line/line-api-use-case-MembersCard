import os
import logging
import datetime
from dateutil.tz import gettz
import math
from decimal import Decimal


from common import (line, utils)
import members_card_const


# 環境変数の宣言
LIFF_ID = os.getenv('LIFF_ID')
LOGGER_LEVEL = os.getenv("LOGGER_LEVEL")

# ログ出力の設定
logger = logging.getLogger()
if LOGGER_LEVEL == 'DEBUG':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


def send_push_message(channel_access_token, user_id, product_obj, language):
    """
    プッシュメッセージを送信する

    Parameters
    ----------
    channel_access_token : str
        OAのチャネルアクセストークン
    user_id : str
        送信対象のユーザーID
    product_obj : dict
        データベースより取得した商品データ
    language : str
        多言語化対応用のパラメータ
    """
    logger.info('productObj: %s', product_obj)
    modified_product_obj = modify_product_obj(product_obj, language)

    flex_dict = make_flex_recept(**modified_product_obj, language=language)

    line.send_push_message(
        channel_access_token, flex_dict, user_id)


def send_service_message(channel_access_token, notification_token, product_obj, language):  # noqa: E501
    """
    サービスメッセージを送信

    Parameters
    ----------
    channel_access_token : str
        MINIアプリのチャネルアクセストークン
    notification_token : str
        MINIアプリの通知用トークン
    product_obj : dict
        データベースより取得した商品データ
    language : str
        多言語化対応用のパラメータ

    """
    # サービスメッセ―ジで代引き手数料と支払手数料を表示させないため以下を0にする
    product_obj['fee'] = 0
    product_obj['postage'] = 0
    modified_product_obj = modify_product_obj(product_obj)
    params = {
        "sum": modified_product_obj['total'] + '円',
        "tax": modified_product_obj['tax'] + '円',
        "date": modified_product_obj['date'],
        "price": modified_product_obj['product_price'] + '円',
        "btn1_url": "https://line.me",
        "discount": modified_product_obj['discount'] + '円',
        "quantity": "1点",
        "shop_name": "Use Case STORE",
        # "payment_fee": modifiedProductObj['fee'] + '円',
        "product_name": modified_product_obj['product_name'],
        # "delivery_cash": modifiedProductObj['postage'] + '円'
    }

    line.send_service_message(
        channel_access_token, 'ec_comp_d_s_ja', params, notification_token)


def modify_product_obj(product_obj, language, discount=0):
    """
    データベースより取得した商品データをメッセージ送信に適した状態のdict型に加工する

    Parameters
    ----------
    product_obj : dict
        データベースより取得した商品データ
    language : str
        多言語化対応用のパラメータ
    discount : int, optional
        値引き率。
        指定が無い場合0とする。

    Returns
    -------
    dict
        加工後の商品データ
    """
    now = datetime.datetime.now(
        gettz('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')
    subtotal = product_obj['unitPrice'] + \
        product_obj['postage'] + product_obj['fee'] - discount
    tax = math.floor(subtotal * Decimal(0.10))
    total = subtotal + tax
    point = math.floor(product_obj['unitPrice'] * Decimal(0.05))
    logger.info('point: %s', point)
    modified_product_obj = {
        'date': now,
        'product_name': product_obj['productName'][language],
        'product_price': utils.separate_comma(product_obj['unitPrice']),
        'postage': utils.separate_comma(product_obj['postage']),
        'fee': utils.separate_comma(product_obj['fee']),
        'discount': utils.separate_comma(discount),
        'subtotal': utils.separate_comma(subtotal),
        'tax': utils.separate_comma(tax),
        'total': utils.separate_comma(total),
        'point': utils.separate_comma(point),
        'img_url': product_obj['imgUrl'],
    }

    return modified_product_obj


def make_flex_recept(date, product_name, product_price, postage,
                     fee, discount, subtotal, tax, total,
                     point, img_url, language):
    """
    電子レシートのフレックスメッセージのdict型データを作成する

    Parameters
    ----------
    date: str
        yyyy/MM/dd hh:mm:ss形式の日付時刻
    product_name: str
        商品名
    product_price: str
        商品代金
    postage: str
        送料
    commission: str
        手数料
    discount: str
        値下げ料
    subtotal: str
        小計
    tax: str
        消費税
    total: str
        合計
    point: str
        付与ポイント
    img_url: str
        商品画像のURL
    language: str
        言語設定

    Returns
    -------
    result : dict
        Flexmessageの元になる辞書型データ
    """
    return {
        "type": "flex",
        "altText": members_card_const.const.MESSAGE_ALT_TEXT[language],
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "Use Case STORE",
                        "size": "xxl",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": date,
                        "color": "#767676"
                    },
                    {
                        "type": "text",
                        "wrap": True,
                        "text": members_card_const.const.MESSAGE_NOTES[language],  # noqa: E501
                        "color": "#ff6347"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": product_name,
                                        "color": "#5B5B5B",
                                        "size": "sm",
                                        "flex": 5
                                    },
                                    {
                                        "type": "text",
                                        "text": product_price,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 2,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": members_card_const.const.MESSAGE_POSTAGE[language],  # noqa: E501
                                        "color": "#5B5B5B",
                                        "size": "sm",
                                        "flex": 5
                                    },
                                    {
                                        "type": "text",
                                        "text": postage,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 2,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": members_card_const.const.MESSAGE_FEE[language],  # noqa: E501
                                        "color": "#5B5B5B",
                                        "size": "sm",
                                        "flex": 5
                                    },
                                    {
                                        "type": "text",
                                        "text": fee,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 2,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": members_card_const.const.MESSAGE_DISCOUNT[language],  # noqa: E501
                                        "color": "#5B5B5B",
                                        "size": "sm",
                                        "flex": 5
                                    },
                                    {
                                        "type": "text",
                                        "text": discount,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 2,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": members_card_const.const.MESSAGE_SUBTOTAL[language],  # noqa: E501
                                        "color": "#5B5B5B",
                                        "size": "sm",
                                        "flex": 5
                                    },
                                    {
                                        "type": "text",
                                        "text": subtotal,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 2,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": members_card_const.const.MESSAGE_TAX[language],  # noqa: E501
                                        "color": "#5B5B5B",
                                        "size": "sm",
                                        "flex": 5
                                    },
                                    {
                                        "type": "text",
                                        "text": tax,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 2,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": members_card_const.const.MESSAGE_TOTAL[language],  # noqa: E501
                                        "color": "#5B5B5B",
                                        "size": "sm",
                                        "flex": 5
                                    },
                                    {
                                        "type": "text",
                                        "text": total,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 2,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": members_card_const.const.MESSAGE_AWARD_POINTS[language],  # noqa: E501
                                        "color": "#5B5B5B",
                                        "size": "sm",
                                        "flex": 5
                                    },
                                    {
                                        "type": "text",
                                        "text": point,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 2,
                                        "align": "end"
                                    }
                                ]
                            },
                        ],
                        "paddingBottom": "xxl"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": members_card_const.const.MESSAGE_THANKS[language],  # noqa: E501
                                "wrap": True,
                                "size": "sm",
                                "color": "#767676"
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "image",
                                "url": img_url,
                                "size": "lg"
                            }
                        ],
                        "margin": "xxl"
                    }
                ],
                "paddingTop": "0%"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": members_card_const.const.MESSAGE_VIEW[language],  # noqa: E501
                            "uri": "https://liff.line.me/{liff_id}?lang={language}".format(liff_id=LIFF_ID, language=language)  # noqa: E501
                        },
                        "color": "#0033cc"
                    },
                    {
                        "type": "spacer",
                        "size": "md"
                    }
                ],
                "flex": 0
            }
        }
    }

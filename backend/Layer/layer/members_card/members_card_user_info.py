"""
MembersCardUserInfo操作用モジュール

"""
import os
from datetime import datetime
from dateutil.tz import gettz

from aws.dynamodb.base import DynamoDB


class MembersCardUserInfo(DynamoDB):
    """MembersCardUserInfo操作用クラス"""
    __slots__ = ['_table']

    def __init__(self):
        """初期化メソッド"""
        table_name = os.getenv('MEMBERS_INFO_DB', 'MembersCardUserInfo')
        super().__init__(table_name)
        self._table = self._db.Table(table_name)

    def put_item(self, user_id, barcode_num, expiration_date, point):
        """
        データ登録

        Parameters
        ----------
        user_id : str
            ユーザーID
        barcode_num : int
            バーコード番号
        expiration_date : str
            ポイント期限日
        point : int
            ポイント

        Returns
        -------
        response : dict
            レスポンス情報

        """
        item = {
            'userId': user_id,
            'barcodeNum': barcode_num,
            'pointExpirationDate': expiration_date,
            'point': point,
            'createdTime': datetime.now(
                gettz('Asia/Tokyo')).strftime("%Y/%m/%d %H:%M:%S"),
            'updatedTime': datetime.now(
                gettz('Asia/Tokyo')).strftime("%Y/%m/%d %H:%M:%S"),
        }

        try:
            response = self._put_item(item)
        except Exception as e:
            raise e
        return response

    def update_point_expiration_date(self, user_id, point, expiration_date):
        """
        ポイントと期限日を更新する

        Parameters
        ----------
        user_id : str
            ユーザーID
        point : int
            ポイント
        expiration_date : str
            ポイント期限日

        Returns
        -------
        response : dict
            レスポンス情報

        """
        key = {'userId': user_id}
        expression = "set point=:point, pointExpirationDate=:expiration_date, updatedTime=:updated_time"  # noqa: E501
        expression_value = {
            ':point': point,
            ':expiration_date': expiration_date,
            ':updated_time': datetime.now(
                gettz('Asia/Tokyo')).strftime("%Y/%m/%d %H:%M:%S")
        }
        return_value = "UPDATED_NEW"

        try:
            response = self._update_item(key, expression,
                                         expression_value, return_value)
        except Exception as e:
            raise e
        return response

    def get_item(self, user_id):
        """
        データ取得

        Parameters
        ----------
        user_id : str
            ユーザーID

        Returns
        -------
        item : dict
            会員ユーザー情報

        """
        key = {'userId': user_id}

        try:
            item = self._get_item(key)
        except Exception as e:
            raise e
        return item

    def query_index_barcode_num(self, barcode_num):
        """
        queryメソッドでbarcodeNum-indexよりデータ取得

        Parameters
        ----------
        barcode_num : int
            バーコード番号

        Returns
        -------
        items : list
            バーコード番号のリスト

        """
        index = 'barcodeNum-index'
        expression = 'barcodeNum = :barcode_num'
        expression_value = {':barcode_num': barcode_num}

        try:
            items = self._query_index(index, expression, expression_value)
        except Exception as e:
            raise e
        return items

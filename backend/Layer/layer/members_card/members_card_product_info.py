"""
MembersCardProductInfo操作用モジュール

"""
import os


from aws.dynamodb.base import DynamoDB


class MembersCardProductInfo(DynamoDB):
    """MembersCardProductInfo操作用クラス"""
    __slots__ = ['_table']

    def __init__(self):
        """初期化メソッド"""
        table_name = os.getenv('PRODUCT_INFO_DB',
                               'MembersCardProductInfo')
        super().__init__(table_name)
        self._table = self._db.Table(table_name)

    def get_item(self, product_id):
        """
        データ取得

        Parameters
        ----------
        product_id : int
            商品ID

        Returns
        -------
        item : dict
            商品情報

        """
        key = {'productId': product_id}

        try:
            item = self._get_item(key)
        except Exception as e:
            raise e
        return item

    def get_table_size(self):
        """
        テーブルのアイテム数を取得する

        Returns
        -------
        count : int
            アイテム数

        """
        try:
            count = self._get_table_size()
        except Exception as e:
            raise e
        return count

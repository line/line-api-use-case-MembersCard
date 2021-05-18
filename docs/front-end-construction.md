# フロントエンド環境構築

## members_card.jsの修正
front -> members_card.jsにて、環境ごとに変更が必要な値があるため、そちらを修正してください。
修正箇所は以下の2点です。
1. const API_GATEWAY_URL = "【バックエンドの構築 -> 会員証アプリのデプロイ(APP)】でデプロイ時に表示されたAPIGatewayのURL"  
1. const liffId = "【LINEチャネルの作成 -> チャネルの作成 -> LIFFアプリの追加】にて追加したLIFFアプリのLIFFID"  

## S3にフロントエンドのモジュールを配置
 frontフォルダ内の全てのファイルを、バックエンド構築手順にて作成した対象のS3バケットに配置してください。


[次の頁へ](test-data-charge.md)

[目次へ戻る](../README.md)

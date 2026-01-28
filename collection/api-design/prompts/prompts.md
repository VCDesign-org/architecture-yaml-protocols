あなたは [Go] のスペシャリストです。
添付のAPI設計書に基づき、[Gin] フレームワークを用いたサーバーの共通ミドルウェア実装コードを作成してください。

### 要件
- **エラーハンドリング**: 設計書の `error_handling` に従い、RFC7807形式のJSONを返すError Handlerミドルウェア。
- **冪等性チェック**: 設計書の `safety_and_idempotency` に従い、`Idempotency-Key` ヘッダーを検証・保存するミドルウェア（Redis利用を想定）。
- **パニック回復**: スタックトレースをレスポンスに出さない（設計書の `sensitive_data_leakage` 設定準拠）Recoveryミドルウェア。

### 出力イメージ
- Middleware初期化コード
- Handlerへの適用例

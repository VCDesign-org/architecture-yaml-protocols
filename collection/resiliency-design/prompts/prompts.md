あなたは [Java/Spring Boot] エンジニアです。
設計書に基づき、[Resilience4j] を用いた在庫APIクライアントの実装コードを作成してください。

### 要件
- アノテーション (`@CircuitBreaker`, `@Retry`) を用いて、設計書のパラメータを適用してください。
- フォールバックメソッド (`fallbackForInventory`) を実装し、設計書の `fallback.behavior` に従った処理（例：空リスト返却）を書いてください。
- `application.yml` の設定記述も含めてください。

### 出力イメージ
- Client Class Code
- Fallback Method
- application.yml (config)

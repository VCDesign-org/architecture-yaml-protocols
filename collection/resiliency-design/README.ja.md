# レジリエンス設計プロンプト集 (Resiliency Design Collection)

分散システムにおける障害対策パターン（Circuit Breaker, Retry, Timeout, Bulkhead）を適用し、システム全体の堅牢性を高めるためのプロンプト例です。

---

## 1. レジリエンスポリシーのドラフト作成

システム間の依存関係に基づき、適切な防御策を設定します。

**Input:**
1. `specs/resiliency-design-template.v1.yaml` の内容
2. 以下のプロンプト

```text
あなたは信頼性エンジニアです。以下の「BFF (Backend Aor Frontend) サービス」のレジリエンス設計を行ってください。

### 依存関係と要件
- 依存先: [レガシーな在庫管理API]。レスポンスが遅く、たまに503エラーを返す。
- 要件:
  - 在庫APIがダウンしても、商品詳細ページ自体は表示させたい（在庫情報は「確認中」表示でOK）。
  - リトライによってレガシーAPIにとどめを刺さないようにしたい。

### 指示
- `circuit_breaker`: しきい値を設定し、障害時は素早くFailするようにしてください。
- `fallback`: 在庫APIエラー時のフォールバック挙動（キャッシュ表示 or デフォルト値）を定義してください。
- `retries`: `jitter_factor` (ゆらぎ) を設定し、Thundering Herd（再試行の集中）を防いでください。
```

---

## 2. 障害対策レビュー

設定されたパラメータが適切か、むしろ障害を拡大させる（ストームを起こす）リスクがないかチェックさせます。

**Input:**
1. 記入済みの `resiliency-design-template.v1.yaml`
2. 以下のプロンプト

```text
あなたはシニアアーキテクトです。
レジリエンス設計書をレビューし、設定値の妥当性を評価してください。

### リスク診断（Acceptance Criteria参照）
1. **無限リトライ**: リトライ回数やタイムアウトが無制限になっていませんか？
2. **ジッター忘れ (R01)**: リトライ間隔が固定値で、同期的な再送攻撃になっていませんか？
3. **タイムアウト設定 (R02)**: 接続タイムアウト(Connect Timeout)が長すぎませんか（数秒以上など）？
4. **サーキットブレーカー (R04)**: そもそも導入されていますか？

### 出力
- 危険度判定（Low/Medium/High）
- パラメータ修正案
```

---

## 3. 実装コード (Resilience Library) の生成

ライブラリ（Resilience4j, Polly, Go-Resiliency等）を用いた実装コードを生成させます。

**Input:**
1. 記入済みの `resiliency-design-template.v1.yaml`
2. 以下のプロンプト

```text
あなたは [Java/Spring Boot] エンジニアです。
設計書に基づき、[Resilience4j] を用いた在庫APIクライアントの実装コードを作成してください。

### 実装要件
- アノテーション (`@CircuitBreaker`, `@Retry`) を用いて、設計書のパラメータを適用してください。
- フォールバックメソッド (`fallbackForInventory`) を実装し、設計書の `fallback.behavior` に従った処理（例：空リスト返却）を書いてください。
- `application.yml` の設定記述も含めてください。
```

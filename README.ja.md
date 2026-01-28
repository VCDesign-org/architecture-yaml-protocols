# Design YAML Collection

システム設計、特にクラウドネイティブ、IoT、マイクロサービスアーキテクチャにおける設計標準を定義するためのYAMLテンプレート集です。
AIエージェントに設計書や実装コードを生成させるための「Input」として使用することを想定しています。

## Catalog

| Collection | Description | Links |
| :--- | :--- | :--- |
| **ai-data-readiness** | AIデータ活用準備度チェック。推論可能なデータ基盤のための品質基準。 | [README](collection/ai-data-readiness/README.ja.md) |
| **api-design** | Web API設計標準。エラーハンドリング、冪等性、セキュリティポリシーなど。 | [README](collection/api-design/README.ja.md) |
| **data-shape-design** | データシェイプ設計。IoTデータの「縦持ち vs 横持ち」の使い分け戦略。 | [README](collection/data-shape-design/README.ja.md) |
| **db-layer-responsibility** | DB責務と疎結合設計。「DBは通過点」という原則に基づくアーキテクチャ。 | [README](collection/db-layer-responsibility/README.ja.md) |
| **logger** | 構造化ロギング標準。検索性、監視、PII保護を考慮したログ設計。 | [README](collection/logger/README.ja.md) |
| **messaging-design** | 非同期メッセージング設計。順序保証、冪等性、DLQ戦略。 | [README](collection/messaging-design/README.ja.md) |
| **ot-it-boundary-design** | OT/IT 境界設計。物理制御と情報システムの安全な連携プロトコル。 | [README](collection/ot-it-boundary-design/README.ja.md) |
| **persistence-design** | 永続化層設計。RDBMS/NoSQL選定、スキーマ管理、バックアップ戦略。 | [README](collection/persistence-design/README.ja.md) |
| **release-strategy** | リリース戦略。CI/CDパイプライン、Blue/Greenデプロイ、品質ゲート。 | [README](collection/release-strategy/README.ja.md) |
| **resiliency-design** | レジリエンス設計。Circuit Breaker, Retry, Bulkhead等の障害対策。 | [README](collection/resiliency-design/README.ja.md) |

## Usage
各ディレクトリの `README.ja.md` に、AIへの指示プロンプト例が記載されています。

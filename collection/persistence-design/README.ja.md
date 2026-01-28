# 永続化層設計プロンプト集 (Persistence Design Collection)

データベース（RDBMS, NoSQL）のスキーマ設計、非機能要件（バックアップ、暗号化）、運用設計（マイグレーション）を定義するためのプロンプト例です。

---

## 1. DB/スキーマ設計のドラフト作成

アプリのデータ特性に合わせたストア選定と、運用を考慮したテーブル設計方針を策定します。

**Input:**
1. `specs/persistence-design-template.v1.yaml` の内容
2. 以下のプロンプト

```text
あなたはDBA(Database Administrator)です。添付のテンプレートに基づき、新規SNSアプリのDB設計標準を作成してください。

### システム概要
- アプリ名: [TimelineApp]
- データ特性: [ユーザー投稿(Write)も多いが、閲覧(Read)が圧倒的に多い。古いデータはあまり見られない]
- 運用要件: [法規制により、退会済みユーザーデータも30日間は物理削除せず保持が必要]

### 指示
- `store_selection`: RDBMSにするかNoSQLにするか、Read/Write比率を考慮して決定し、理由を述べてください。
- `modeling.soft_delete`: 退会ユーザーの扱い（論理削除）について、`is_active` フラグか `deleted_at` か、あるいは別テーブル退避か、最適な戦略を選んでください。
- `schema_management`: マイグレーションツール(Flyway/Prisma等)を選定してください。
```

---

## 2. 設計レビュー（データ保全・セキュリティ）

データ損失や情報漏洩のリスクがないか、受け入れ基準に基づいてチェックさせます。

**Input:**
1. 記入済みの `persistence-design-template.v1.yaml`
2. 以下のプロンプト

```text
あなたはセキュリティコンサルタントです。
設計書をレビューし、データ保護の観点から問題がないか診断してください。

### 診断項目
1. **暗号化(D04)**: 保存データの暗号化(At Rest)は有効化されていますか？
2. **バックアップ(D02)**: オペミスでデータを全消去してしまった場合、特定の時点(PITR)に戻せる設定になっていますか？目標復旧時点(RPO)は妥当ですか？
3. **破壊的変更**: `destructive_changes` ポリシーで、カラム削除などの危険な操作が禁止あるいは制限されていますか？

### 出力
- コンプライアンス判定（OK/NG）
- NG項目の修正案
```

---

## 3. インフラコード(IaC) / マイグレーションの生成

設計に基づき、TerraformやDDLを生成させます。

**Input:**
1. 記入済みの `persistence-design-template.v1.yaml`
2. 以下のプロンプト

```text
あなたはインフラエンジニアです。
設計書の要件を満たす、[Terraform (AWS provider)] のRDSリソース定義コードを作成してください。

### 実装要件
- リソース: `aws_db_instance`
- **バックアップ**: 設計書の `backup_and_recovery` に従い、`backup_retention_period` などを設定してください。
- **暗号化**: `storage_encrypted = true` とし、KMSキーを指定可能にしてください。
- **削除保護**: うっかり削除を防ぐため、`deletion_protection` を有効にしてください。
```

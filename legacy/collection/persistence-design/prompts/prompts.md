あなたはインフラエンジニアです。
設計書の要件を満たす、[Terraform (AWS provider)] のRDSリソース定義コードを作成してください。

### 要件
- リソース: `aws_db_instance`
- **バックアップ**: 設計書の `backup_and_recovery` に従い、`backup_retention_period` などを設定してください。
- **暗号化**: `storage_encrypted = true` とし、KMSキーを指定可能にしてください。
- **削除保護**: うっかり削除を防ぐため、`deletion_protection` を有効にしてください。

### 出力イメージ
- main.tf (RDS Resource)
- variables.tf

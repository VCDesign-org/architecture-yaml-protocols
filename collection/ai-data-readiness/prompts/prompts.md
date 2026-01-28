あなたはデータエンジニアです。
添付の設計書に基づき、センサーデータを取り込むための [BigQuery] のテーブル定義(DDL)を作成してください。

### 要件
- 設計書の `fact_vs_hypothesis` に従い、生データと推論結果のカラム/テーブルを分けてください。
- `explicit_labeling` で定義された必須メタデータ（信頼度スコア、生成モデル名など）をカラムとして定義してください。
- `quality_transparency` に従い、Quality Flag用のカラムを含めてください。

### 出力イメージ
- CREATE TABLE 文
- カラム詳細（Description含む）

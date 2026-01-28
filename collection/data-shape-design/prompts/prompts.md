あなたはAnalytics Engineerです。
設計書の `transformations` セクションに基づき、[dbt (Data Build Tool)] で使用する変換SQLモデルを作成してください。

### 要件
- ソース: Canonical層の `S04_long_quality` (タイムスタンプ, タグID, 値, 品質フラグ)
- ターゲット: Serving層の `S05_pivot` (タイムスタンプを軸に、タグごとにカラム化)
- ロジック:
  1. タイムスタンプでGROUP BYする。
  2. タグIDごとに値をピボットし、カラム名は `tag_{id}` とする。
  3. 設計書の制約 `constraints` に従い、品質フラグが 'Bad' のデータが含まれる場合は、集計値のカラムに加え `is_reliable` カラムも生成して false にする等のロジックを入れてください。

### 出力イメージ
- dbt model (.sql)
- schema.yml (metrics definitions)

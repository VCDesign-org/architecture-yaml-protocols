# Components (Where)

このディレクトリは、**「どのコード（Where）」** に **「どのルール（Bre/Con/Clo）」** を適用するかを定義します。

## 役割
- **Decisions / Boundaries / Connections / Closures** は **「何（What/Why/How）」** を定義します（場所には依存しません）。
- **Components** は **「どこ（Where）」** を定義し、それらをコードベース上の物理的なパスにマッピングします。

## 構造
`components.yaml` に定義します。
- **paths**: glob形式で適用範囲を指定（include/exclude）
- **applies**: 適用する Boundary, Connection, Closure のIDリスト

## 運用ルール
1. **Globは粗く**: 複雑な正規表現を用いず、ディレクトリ単位で指定する。
2. **例外は最小**: exclude は乱用しない。構造が複雑ならコンポーネント自体を分割する。
3. **ID命名**: `comp-<domain>-<seq>` （例: `comp-api-01`）

## Glob運用ルール
- **Includeは「粗く」**: `src/api/**` のように広く取る。ファイル単位の指定は避ける。
- **Excludeは「例外最小」**: どうしても除外したいテストデータやデバッグ用コードのみ記述する。
- **深掘り禁止**: `src/api/v1/user/handlers/create/**` のような深い指定が必要な場合、それはコンポーネントの責務が混ざっている証拠です。コンポーネント分割を検討してください。

## コンポーネント分割基準（1行ルール）
- **原則**: 1 component は 1 責務・1 境界単位。paths を増やしたくなったら component を分割する

## ID命名規則（統一）
- 形式: `comp-<domain>-<seq>`
- 例: `comp-api-01`, `comp-payment-01`
- 理由: `b-`/`c-`/`cl-` と同様に、IDだけで役割と順序を識別可能にするため。

## 適用上限（目安）
1コンポーネントあたり、Boundaries は 10件程度を目安とする。多すぎる場合はコンポーネントが肥大化している可能性があります。

## 変更フロー
1. **Decision変更**: アーキテクチャ判断を変更・追加する (`decisions/`)
2. **Definition更新**: 判断に基づき Boundary/Connection/Closure を更新する (`boundaries/`, `connections/`, `closures/`)
3. **Assignment更新**: `components.yaml` の `applies` を更新して適用範囲を変える

## 「どこに書くか」迷った時のルール
- **原則**（Why/What）: **Decisions**
- **必須/禁止**（Must/Must Not）: **Boundaries**
- **越境/接続**（Flow/Interface）: **Connections**
- **事故処理**（Recovery/Handling）: **Closures**
- **適用範囲**（Where）: **Components**



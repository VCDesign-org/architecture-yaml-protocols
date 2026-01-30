# Architecture YAML Protocols

Value-Continuous AI Development (VC-AD) のためのコアプロトコル集です。
このリポジトリは、AIによる自律的なコーディングと、人間によるガバナンスを両立させるための「決定」「境界」「接続」などを定義・管理します。

## Core Protocols

このリポジトリは以下の5つの主要コンポーネントで構成されています。

| Protocol | Description | Links |
| :--- | :--- | :--- |
| **Decisions** | **Why / What**. アーキテクチャ上の重要な意思決定、ポリシー、推奨/非推奨の技術スタックなどを記録します。 | [README](decisions/README.md) |
| **Boundaries** | **Must / Must Not**. 決して破ってはいけない制約、所有権の境界、変えてはいけないルールを定義します。 | [README](boundaries/README.md) |
| **Connections** | **How / Interface**. コンポーネント間の接続方法、データフロー、APIコントラクトを定義します。 | [README](connections/README.md) |
| **Closures** | **If fails**. エラー処理、リカバリ手順、責任の完結（Closure）を定義します。 | [README](closures/README.md) |
| **Components** | **Where**. 上記のルールを実際のコードベース（ファイルパス）にマッピングします。 | [README](components/README.md) |

## Legacy Collections

以前のデザインパターン集（Logger設計、API設計など）は `legacy/collection` に移動しました。

- [Legacy Collections](legacy/collection/)

## Usage

AIエージェントを用いて開発を行う際は、以下の流れでプロトコルを参照・適用します。

1. **Decide**: `decisions` を参照し、アーキテクチャの方針を確認する。
2. **Define**: `boundaries`, `connections`, `closures` で具体的なルールを定義する。
3. **Assign**: `components` で対象のファイルパスにルールを紐付ける。

これにより、AIは「どこに」「どのようなルールで」コードを書くべきかを理解できます。

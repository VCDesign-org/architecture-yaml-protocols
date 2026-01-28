# リリース戦略プロンプト集 (Release Strategy Collection)

CI/CDパイプライン、デプロイ方式（Blue/Green, Canary）、ロールバック戦略を定義し、安全なリリースプロセスを構築するためのプロンプト例です。

---

## 1. リリース戦略・CI/CD設計のドラフト作成

開発フローと本番環境への適用戦略を定義します。

**Input:**
1. `specs/release-strategy-template.v1.yaml` の内容
2. 以下のプロンプト

```text
あなたはDevOpsエンジニアです。以下のミッションクリティカルな金融系アプリのためのリリース戦略を策定してください。

### プロジェクト要件
- 稼働率: [99.99%が必須。デプロイ時のダウンタイムは許容されない]
- 安全性: [バグ混入時、即座に旧バージョンに戻す必要がある]
- 環境: [Kubernetes / ArgoCD]

### 指示
- `deployment_strategy`: ダウンタイムゼロを実現するために、Blue/Green または Canary デプロイを選択し、詳細な切り替えロジックを記述してください。
- `rollback.automation`: エラー率スパイクを検知して自動でロールバックする仕組みを定義してください。
- `continuous_integration.artifact_building`: コンテナイメージの `latest` タグ利用を禁止し、Immutableなビルドを行う設定にしてください。
```

---

## 2. パイプライン設計のレビュー

CI/CDがセキュリティや品質担保のゲートとして機能しているかチェックします。

**Input:**
1. 記入済みの `release-strategy-template.v1.yaml`
2. 以下のプロンプト

```text
あなたはQAマネージャーです。
リリース戦略書をレビューし、品質保証プロセスとしての妥当性を採点してください。

### チェック項目
1. **Immutable Artifact (REL01)**: ビルドされた成果物が、QA〜本番まで変わらないことが保証されていますか？再ビルドによる混入リスクはありませんか？
2. **セキュリティスキャン (REL03)**: 脆弱性診断(Trivy等)がデプロイ前に必須化されていますか？
3. **メインブランチ保護 (REL04)**: CIが通っていないコードがマージされる穴はありませんか？

### 出力
- Pass/Fail 判定
- 不足しているテストプロセスやスキャンの指摘
```

---

## 3. CI設定ファイル(GitHub Actions)の生成

戦略に基づき、実際のパイプライン設定ファイルを生成させます。

**Input:**
1. 記入済みの `release-strategy-template.v1.yaml`
2. 以下のプロンプト

```text
あなたはCIエンジニアです。
設計書の `continuous_integration` および `deployment_strategy` に基づき、[GitHub Actions] のワークフローファイル(.yml)を作成してください。

### ワークーフローのステップ
1. **Test & Lint**: 単体テストとLintを実行。
2. **Security Scan**: Trivyによるコンテナスキャンを実行。
3. **Build & Push**: Dockerイメージをビルドし、GitコミットハッシュをタグとしてECRにPush。
4. **Deploy**: マージ時に、ArgoCDのリポジトリ(k8sマニフェスト)のimageタグを更新してPRを作成（GitOps）。
```

あなたはCIエンジニアです。
設計書の `continuous_integration` および `deployment_strategy` に基づき、[GitHub Actions] のワークフローファイル(.yml)を作成してください。

### 要件
- ワークーフローのステップ:
  1. **Test & Lint**: 単体テストとLintを実行。
  2. **Security Scan**: Trivyによるコンテナスキャンを実行。
  3. **Build & Push**: Dockerイメージをビルドし、GitコミットハッシュをタグとしてECRにPush。
  4. **Deploy**: マージ時に、ArgoCDのリポジトリ(k8sマニフェスト)のimageタグを更新してPRを作成（GitOps）。

### 出力イメージ
- .github/workflows/ci-cd.yml

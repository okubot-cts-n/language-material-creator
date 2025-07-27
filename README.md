# 🎯 語学教材作成ツール - Language Material Creator

**AI教材作成の業務効率化ツール** - ChatGPTのコピペ作業を完全自動化

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)

## 🌟 特徴

- 🤖 **AI教材生成**: Claude APIでロールプレイ・ディスカッション・表現練習を自動作成
- 🎨 **テンプレート管理**: サンプルテキスト入力で柔軟なカスタマイズ
- ⚡ **一括生成**: 複数教材の同時作成で業務効率化
- 🔍 **品質チェック**: コンテキスト準拠・重複・レベル調整の自動検証
- 📊 **図表生成**: リアルタイム図表作成とAIプロンプト生成
- 🔔 **完了通知**: 音付きポップアップで作業完了をお知らせ

## 🚀 デモ

**🌐 [ライブデモを試す](https://your-app.streamlit.app/)**

## 📋 使用方法

### 1. テンプレート設定
- 教材タイプ選択（ロールプレイ・ディスカッション・表現練習）
- サンプルテキスト入力で品質向上
- パーツごとの詳細設定

### 2. コンテキスト入力
- カウンセリングメモ
- 教材作成方針
- 受講者情報

### 3. トピック管理
- 手動入力またはAI自動生成
- 複数選択で一括処理

### 4. 一括生成
- 設定に基づいて複数教材を同時作成
- 品質チェック自動実行

## 🛠️ 技術スタック

- **Frontend**: Streamlit
- **AI**: Claude API (Anthropic)
- **図表**: Plotly
- **外部連携**: Google Docs API
- **デプロイ**: Docker対応

## ⚙️ ローカル実行

```bash
# 1. リポジトリクローン
git clone https://github.com/your-username/language-material-creator.git
cd language-material-creator

# 2. 依存関係インストール
pip install -r requirements.txt

# 3. 環境変数設定
cp env_sample.txt .env
# .env ファイルでANTHROPIC_API_KEYを設定

# 4. アプリ起動
streamlit run app_practical.py
```

## 🌐 外部公開

複数のプラットフォームに対応:

- **Streamlit Cloud** (無料) - 推奨
- **Railway** ($5/月)
- **Heroku** ($7/月)
- **AWS EC2** (本格運用)

詳細は [`deployment_guide.md`](deployment_guide.md) を参照

## 📊 パフォーマンス

- **効率化**: 手動作業時間を **80%削減**
- **品質**: AI生成 + 自動チェックで **一貫性確保**
- **スケール**: **20件/2週間** の教材作成が可能

## 🤝 貢献

プルリクエストや課題報告を歓迎します。

## 📄 ライセンス

MIT License

## 📞 サポート

- 📖 詳細ガイド: [`README_deployment.md`](README_deployment.md)
- 🐳 Docker: [`docker_setup.py`](docker_setup.py) 実行
- 🔧 トラブルシューティング: Issues タブで報告

---

**業務効率化で語学教育をより良く！** 🎓 
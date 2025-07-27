# 🚀 語学教材作成ツール - 外部公開ガイド

## ⚡ 最速デプロイ (推奨)

### Streamlit Cloud (無料)
1. GitHubリポジトリ作成・プッシュ
2. https://share.streamlit.io/ でアカウント作成
3. リポジトリ連携 → `app_practical.py` 指定
4. Secrets管理で `ANTHROPIC_API_KEY` 設定
5. 🎉 公開完了！

---

## 🐳 Docker デプロイ

### ローカルテスト
```bash
# セットアップファイル実行
python3 docker_setup.py

# Docker ビルド・起動
docker build -t 語学教材作成ツール .
docker run -p 8501:8501 -e ANTHROPIC_API_KEY=your_key 語学教材作成ツール
```

### 本格デプロイ
```bash
# 環境変数設定
export ANTHROPIC_API_KEY=your_key_here

# 自動デプロイ実行
./docker-deploy.sh
```

---

## ☁️ クラウドプラットフォーム

| プラットフォーム | 月額 | 特徴 | 設定ファイル |
|------------------|------|------|--------------|
| **Streamlit Cloud** | 無料 | 最簡単 | GitHub連携のみ |
| **Railway** | $5〜 | バランス良好 | `railway.json` |
| **Render** | $7〜 | 安定性重視 | `render.yaml` |
| **Heroku** | $7〜 | 実績豊富 | `Procfile` |

---

## 🔐 セキュリティ設定

### 環境変数 (必須)
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_APPLICATION_CREDENTIALS=./google_credentials.json  # オプション
```

### 認証機能追加 (推奨)
```python
# app_practical.py の先頭に追加
import streamlit_authenticator as stauth

# 認証チェック
if not authenticate_user():
    st.stop()
```

---

## 📊 監視・ログ

### アクセス制限
- IP制限: Nginx設定
- レート制限: アプリ内実装
- 使用量監視: ログ分析

### ヘルスチェック
- エンドポイント: `/_stcore/health`
- 監視間隔: 30秒
- 復旧処理: 自動再起動

---

## 🎯 推奨デプロイメント戦略

### **個人・プロトタイプ**
→ **Streamlit Cloud** (無料)

### **小規模ビジネス**
→ **Railway** ($5/月)

### **企業・本格運用**
→ **AWS EC2 + Docker** ($20/月〜)

---

## 📞 サポート

**問題が発生した場合:**
1. `deployment_guide.md` で詳細確認
2. ログファイル確認: `docker-compose logs`
3. ヘルスチェック: `http://your-domain/_stcore/health`

**即座に公開したい場合:**
```bash
git add . && git commit -m "deploy" && git push
# → Streamlit Cloud で自動デプロイ
``` 
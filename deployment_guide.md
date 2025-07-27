# 語学教材作成ツール - 外部公開ガイド

## 🚀 外部公開の選択肢

### 1. 🎯 Streamlit Cloud (推奨・無料)

#### 手順:
1. **GitHubにリポジトリ作成**
   ```bash
   git init
   git add .
   git commit -m "初回コミット"
   git remote add origin https://github.com/ユーザー名/語学教材作成ツール.git
   git push -u origin main
   ```

2. **Streamlit Cloudでデプロイ**
   - https://share.streamlit.io/ にアクセス
   - GitHubアカウントでログイン
   - "New app" → リポジトリ選択
   - メインファイル: `app_practical.py`
   - デプロイ完了

3. **環境変数設定**
   - Streamlit Cloud管理画面で `ANTHROPIC_API_KEY` を設定
   - Secrets管理で安全に管理

#### セキュリティ対策:
```python
# secrets.toml (Streamlit Cloud用)
[secrets]
ANTHROPIC_API_KEY = "your_api_key_here"
```

---

### 2. 🏢 Railway (簡単・有料)

#### 特徴:
- 月額$5〜
- 自動スケーリング
- カスタムドメイン対応
- プライベートリポジトリ対応

#### 手順:
1. Railway.app でアカウント作成
2. GitHubリポジトリを連携
3. 環境変数設定
4. 自動デプロイ

---

### 3. ☁️ Heroku (従来型・有料)

#### 特徴:
- 月額$7〜
- 豊富なアドオン
- 実績豊富

#### 手順:
```bash
# Procfile作成
echo "web: streamlit run app_practical.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# requirements.txt更新
pip freeze > requirements.txt

# Heroku CLI設定
heroku create 語学教材作成ツール
heroku config:set ANTHROPIC_API_KEY=your_key_here
git push heroku main
```

---

### 4. 🔒 AWS EC2 (企業向け・本格運用)

#### 特徴:
- 完全制御可能
- 高セキュリティ
- スケーラブル
- 月額$10〜$50

#### 手順:
1. **EC2インスタンス作成**
   - Ubuntu 22.04 LTS
   - t3.micro (無料枠) または t3.small

2. **サーバー設定**
   ```bash
   # SSH接続後
   sudo apt update && sudo apt install python3-pip nginx -y
   pip3 install streamlit anthropic python-dotenv
   
   # アプリケーション配置
   git clone https://github.com/ユーザー名/語学教材作成ツール.git
   cd 語学教材作成ツール
   
   # 環境変数設定
   echo "ANTHROPIC_API_KEY=your_key_here" > .env
   
   # Streamlit起動（システムサービス化）
   sudo systemctl enable streamlit
   sudo systemctl start streamlit
   ```

3. **Nginx設定（リバースプロキシ）**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

---

## 🔐 セキュリティ強化

### 1. 認証機能追加
```python
# auth.py
import streamlit_authenticator as stauth

def add_authentication():
    names = ['管理者', 'ユーザー1']
    usernames = ['admin', 'user1']
    passwords = ['admin123', 'user123']  # 実際は暗号化必要
    
    hashed_passwords = stauth.Hasher(passwords).generate()
    
    authenticator = stauth.Authenticate(
        names, usernames, hashed_passwords,
        'cookie_name', 'signature_key', cookie_expiry_days=30
    )
    
    name, authentication_status, username = authenticator.login('ログイン', 'main')
    
    if authentication_status == True:
        st.sidebar.success(f'{name} としてログイン中')
        authenticator.logout('ログアウト', 'sidebar')
        return True
    elif authentication_status == False:
        st.error('ユーザー名/パスワードが間違っています')
        return False
    else:
        st.warning('ユーザー名とパスワードを入力してください')
        return False
```

### 2. API使用量制限
```python
# rate_limiter.py
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=10, time_window=3600):  # 1時間に10回
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
    
    def allow_request(self, user_id):
        now = time.time()
        user_requests = self.requests[user_id]
        
        # 古いリクエストを削除
        self.requests[user_id] = [req_time for req_time in user_requests 
                                  if now - req_time < self.time_window]
        
        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(now)
            return True
        return False
```

---

## 💾 データ永続化

### 1. データベース連携
```python
# database.py
import sqlite3
import json
from datetime import datetime

class MaterialDatabase:
    def __init__(self, db_path="materials.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            topic TEXT,
            material_type TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        conn.close()
    
    def save_material(self, user_id, topic, material_type, content):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO materials (user_id, topic, material_type, content) VALUES (?, ?, ?, ?)",
            (user_id, topic, material_type, json.dumps(content))
        )
        conn.commit()
        conn.close()
    
    def get_user_materials(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT * FROM materials WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        materials = cursor.fetchall()
        conn.close()
        return materials
```

---

## 🌐 ドメイン・SSL設定

### 1. カスタムドメイン設定
```bash
# DNS設定例
A レコード: 教材作成ツール.example.com → サーバーIP

# Let's Encrypt SSL証明書
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d 教材作成ツール.example.com
```

---

## 📊 監視・ログ

### 1. アクセス監視
```python
# monitoring.py
import logging
from datetime import datetime

# ログ設定
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_usage(user_id, action, details=None):
    logging.info(f"User: {user_id}, Action: {action}, Details: {details}")

def log_error(error_msg, user_id=None):
    logging.error(f"Error: {error_msg}, User: {user_id}")
```

---

## 💰 コスト比較

| 方法 | 月額コスト | 特徴 | 推奨用途 |
|------|------------|------|----------|
| Streamlit Cloud | 無料 | 簡単、制限あり | 個人・プロトタイプ |
| Railway | $5〜 | バランス良好 | 小規模ビジネス |
| Heroku | $7〜 | 実績豊富 | 中規模ビジネス |
| AWS EC2 | $10〜$50 | 高性能・高制御 | 企業・大規模 |

---

## 🎯 推奨デプロイメント戦略

### **段階的展開**

1. **Phase 1**: Streamlit Cloud で無料公開（テスト運用）
2. **Phase 2**: Railway/Heroku で本格運用開始
3. **Phase 3**: AWS等で企業向け機能追加

### **即座に始める場合**
```bash
# 1. GitHub リポジトリ作成・プッシュ
git init && git add . && git commit -m "initial"

# 2. Streamlit Cloud でデプロイ
# → https://share.streamlit.io/

# 3. 環境変数設定
# → ANTHROPIC_API_KEY をSecrets管理で設定

# 4. 公開URL取得
# → https://your-app.streamlit.app/
```

---

**最速で公開するなら Streamlit Cloud、本格運用なら Railway、企業向けなら AWS EC2 をお勧めします！** 
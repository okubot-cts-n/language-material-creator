# Docker化セットアップスクリプト
import os
import subprocess

def create_docker_files():
    """Docker関連ファイルを生成"""
    
    # Dockerfile
    dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# 依存関係のコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルのコピー
COPY . .

# ポート公開
EXPOSE 8501

# ヘルスチェック
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Streamlit設定
RUN mkdir -p ~/.streamlit
RUN echo "[server]" > ~/.streamlit/config.toml
RUN echo "address = '0.0.0.0'" >> ~/.streamlit/config.toml
RUN echo "port = 8501" >> ~/.streamlit/config.toml
RUN echo "enableCORS = false" >> ~/.streamlit/config.toml
RUN echo "enableXsrfProtection = false" >> ~/.streamlit/config.toml

# アプリケーション起動
CMD ["streamlit", "run", "app_practical.py"]
'''

    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    # docker-compose.yml
    compose_content = '''version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data:/app/data  # データ永続化用
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 将来のデータベース用
  # db:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_DB: materials
  #     POSTGRES_USER: app
  #     POSTGRES_PASSWORD: ${DB_PASSWORD}
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   restart: unless-stopped

# volumes:
#   postgres_data:
'''

    with open('docker-compose.yml', 'w') as f:
        f.write(compose_content)
    
    # .dockerignore
    dockerignore_content = '''__pycache__
*.pyc
*.pyo
*.pyd
.Python
.env
.git
.gitignore
README.md
Dockerfile
.dockerignore
.pytest_cache
.coverage
.vscode
*.log
'''

    with open('.dockerignore', 'w') as f:
        f.write(dockerignore_content)
    
    # docker-deploy.sh (デプロイスクリプト)
    deploy_script = '''#!/bin/bash

# 環境変数チェック
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "エラー: ANTHROPIC_API_KEY が設定されていません"
    exit 1
fi

# Docker イメージのビルド
echo "🔨 Docker イメージをビルド中..."
docker build -t 語学教材作成ツール:latest .

# 既存コンテナの停止・削除
echo "🛑 既存コンテナを停止中..."
docker-compose down

# 新しいコンテナの起動
echo "🚀 新しいコンテナを起動中..."
docker-compose up -d

# ヘルスチェック
echo "🏥 ヘルスチェック中..."
for i in {1..30}; do
    if docker-compose exec app curl -f http://localhost:8501/_stcore/health; then
        echo "✅ アプリケーションが正常に起動しました"
        echo "🌐 http://localhost:8501 でアクセス可能です"
        exit 0
    fi
    echo "待機中... ($i/30)"
    sleep 2
done

echo "❌ アプリケーションの起動に失敗しました"
docker-compose logs app
exit 1
'''

    with open('docker-deploy.sh', 'w') as f:
        f.write(deploy_script)
    
    # 実行権限付与
    os.chmod('docker-deploy.sh', 0o755)
    
    print("✅ Docker関連ファイルを作成しました:")
    print("  - Dockerfile")
    print("  - docker-compose.yml") 
    print("  - .dockerignore")
    print("  - docker-deploy.sh")

def create_cloud_deployment_configs():
    """クラウドデプロイ用設定ファイル生成"""
    
    # Railway用 railway.json
    railway_config = '''{
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "startCommand": "streamlit run app_practical.py --server.port=$PORT --server.address=0.0.0.0",
    "healthcheckPath": "/_stcore/health"
  }
}'''

    with open('railway.json', 'w') as f:
        f.write(railway_config)
    
    # Render用 render.yaml
    render_config = '''services:
  - type: web
    name: 語学教材作成ツール
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app_practical.py --server.port=$PORT --server.address=0.0.0.0
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false  # セキュアな環境変数として設定
    healthCheckPath: /_stcore/health
'''

    with open('render.yaml', 'w') as f:
        f.write(render_config)
    
    # Heroku用 Procfile
    with open('Procfile', 'w') as f:
        f.write('web: streamlit run app_practical.py --server.port=$PORT --server.address=0.0.0.0')
    
    print("✅ クラウドデプロイ用設定ファイルを作成しました:")
    print("  - railway.json (Railway)")
    print("  - render.yaml (Render)")
    print("  - Procfile (Heroku)")

def setup_nginx_config():
    """Nginx設定ファイル生成"""
    
    nginx_config = '''server {
    listen 80;
    server_name 教材作成ツール.example.com;  # 実際のドメインに変更
    
    # HTTP to HTTPS redirect
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 教材作成ツール.example.com;  # 実際のドメインに変更
    
    # SSL証明書（Let's Encryptで自動設定）
    ssl_certificate /etc/letsencrypt/live/教材作成ツール.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/教材作成ツール.example.com/privkey.pem;
    
    # セキュリティヘッダー
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Streamlitアプリへのプロキシ
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
    
    # 静的ファイルのキャッシュ
    location /_stcore/static {
        proxy_pass http://localhost:8501;
        proxy_cache_valid 200 1h;
        add_header Cache-Control "public, max-age=3600";
    }
}'''

    os.makedirs('nginx', exist_ok=True)
    with open('nginx/app.conf', 'w') as f:
        f.write(nginx_config)
    
    print("✅ Nginx設定ファイルを作成しました:")
    print("  - nginx/app.conf")

if __name__ == "__main__":
    print("🐳 Docker化セットアップを開始します...")
    
    create_docker_files()
    print()
    
    create_cloud_deployment_configs() 
    print()
    
    setup_nginx_config()
    print()
    
    print("🎉 セットアップ完了！")
    print()
    print("📋 次のステップ:")
    print("1. Docker でローカルテスト:")
    print("   docker build -t 語学教材作成ツール .")
    print("   docker run -p 8501:8501 -e ANTHROPIC_API_KEY=your_key 語学教材作成ツール")
    print()
    print("2. クラウドにデプロイ:")
    print("   - Streamlit Cloud: GitHubリポジトリを連携")
    print("   - Railway: railway.json を使用") 
    print("   - Heroku: Procfile を使用")
    print()
    print("3. 本格運用:")
    print("   ./docker-deploy.sh でDockerデプロイ")
    print("   nginx/app.conf でリバースプロキシ設定") 
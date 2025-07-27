FROM python:3.11-slim

WORKDIR /app

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    git \
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

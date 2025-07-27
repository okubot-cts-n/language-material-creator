#!/bin/bash

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

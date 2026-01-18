#!/bin/bash

# Update and restart the Dead Man's Switch project

echo "🔄 Pulling latest changes from GitHub..."
git pull origin main

echo "🔨 Rebuilding Docker containers..."
docker compose build --no-cache

echo "🛑 Stopping containers..."
docker compose down

echo "🚀 Starting containers..."
docker compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 5

echo "📊 Checking container status..."
docker compose ps

echo "✅ Update complete!"
echo ""
echo "📝 To view logs: docker compose logs -f web"
echo "🌐 API available at: http://localhost:8000"
echo "📚 Docs available at: http://localhost:8000/docs"

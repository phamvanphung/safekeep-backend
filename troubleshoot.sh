#!/bin/bash

echo "🔍 Checking Docker containers status..."
docker compose ps

echo ""
echo "📋 Checking web service logs..."
docker compose logs web --tail=50

echo ""
echo "🔧 Attempting to start web service..."
docker compose up -d web

echo ""
echo "⏳ Waiting 5 seconds..."
sleep 5

echo ""
echo "📊 Checking status again..."
docker compose ps web

echo ""
echo "📋 Latest logs:"
docker compose logs web --tail=20

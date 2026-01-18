# Update and restart the Dead Man's Switch project (PowerShell)

Write-Host "🔄 Pulling latest changes from GitHub..." -ForegroundColor Cyan
git pull origin main

Write-Host "🔨 Rebuilding Docker containers..." -ForegroundColor Yellow
docker compose build --no-cache

Write-Host "🛑 Stopping containers..." -ForegroundColor Red
docker compose down

Write-Host "🚀 Starting containers..." -ForegroundColor Green
docker compose up -d

Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "📊 Checking container status..." -ForegroundColor Cyan
docker compose ps

Write-Host "✅ Update complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 To view logs: docker compose logs -f web" -ForegroundColor White
Write-Host "🌐 API available at: http://localhost:8000" -ForegroundColor White
Write-Host "📚 Docs available at: http://localhost:8000/docs" -ForegroundColor White

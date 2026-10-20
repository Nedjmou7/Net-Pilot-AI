Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host " Starting TopoGemma: Local Cisco Packet Tracer AI Assistant" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan

# 1. Start Backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Starting TopoGemma Backend...' -ForegroundColor Green; cd '$PSScriptRoot/backend'; $env:PYTHONPATH = '.'; ../venv/Scripts/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# 2. Start Frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Starting TopoGemma Frontend...' -ForegroundColor Cyan; cd '$PSScriptRoot/frontend'; npm run dev"

Write-Host "`nTopoGemma is launching!" -ForegroundColor Green
Write-Host "Backend API docs:  http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "Frontend web app:  http://localhost:5173" -ForegroundColor Yellow

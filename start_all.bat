@echo off
echo ==============================================================
echo  Starting TopoGemma: Local Cisco Packet Tracer AI Assistant
echo ==============================================================

echo [1/2] Starting FastAPI Backend on http://localhost:8000 ...
start "TopoGemma Backend" cmd /k "cd backend && ..\venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Starting React Frontend on http://localhost:5173 ...
start "TopoGemma Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo TopoGemma is launching!
echo Backend API:  http://localhost:8000/docs
echo Frontend App: http://localhost:5173
echo.
pause

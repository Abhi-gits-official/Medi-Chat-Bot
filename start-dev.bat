@echo off
echo Starting Medical Assistance Chatbot...
echo ===========================================

echo Starting backend server...
start "Backend Server" cmd /k "cd backend && python main.py"

timeout /t 2 /nobreak >nul

echo Starting frontend server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo ===========================================
echo Both servers are starting up!
echo Frontend: http://localhost:5173 or http://localhost:5174
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul

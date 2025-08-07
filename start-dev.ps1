# Medical Chatbot Development Startup Script
# This script starts both the frontend and backend servers for development

Write-Host "Starting Medical Assistance Chatbot..." -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green

# Check if required dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow

# Check Node.js
if (Get-Command "node" -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host "✓ Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Node.js not found. Please install Node.js." -ForegroundColor Red
    exit 1
}

# Check Python
if (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (Test-Path "backend\.env") {
    Write-Host "✓ Backend environment file found" -ForegroundColor Green
} else {
    Write-Host "⚠ Backend .env file not found. Please create backend\.env and add your GEMINI_API_KEY" -ForegroundColor Yellow
    Write-Host "  Copy backend\.env.example to backend\.env and add your API key" -ForegroundColor Yellow
}

Write-Host "`nStarting servers..." -ForegroundColor Yellow

# Start backend server
Write-Host "Starting backend server on http://localhost:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python main.py" -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 2

# Start frontend server
Write-Host "Starting frontend server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -WindowStyle Normal

Write-Host "`n===========================================" -ForegroundColor Green
Write-Host "Both servers are starting up!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173 or http://localhost:5174" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`nPress any key to exit this script..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

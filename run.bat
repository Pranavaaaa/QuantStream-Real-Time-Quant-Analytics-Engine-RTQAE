@echo off
echo ========================================
echo QuantStream RTQAE - Starting Services
echo ========================================
echo.

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from python.org
    pause
    exit /b 1
)
echo Python found!
echo.

echo [2/3] Starting Backend API Server...
start "QuantStream Backend" cmd /k "cd backend && python app.py"
timeout /t 3 /nobreak >nul
echo Backend started on http://localhost:8000
echo.

echo [3/3] Starting Frontend Dashboard...
start "QuantStream Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 3 /nobreak >nul
echo.

echo ========================================
echo  QuantStream RTQAE is now running!
echo ========================================
echo.
echo  Backend API: http://localhost:8000
echo  API Docs:    http://localhost:8000/docs
echo  Dashboard:   http://localhost:5173
echo.
echo  Press any key to stop all services...
pause >nul

echo.
echo Stopping services...
taskkill /FI "WINDOWTITLE eq QuantStream Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq QuantStream Frontend*" /F >nul 2>&1
echo Services stopped.

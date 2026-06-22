@echo off
chcp 65001 >nul
title EBM Real API Server

echo ========================================
echo    EBM Real Physics API Server
echo    Based on CODATA 2018 & IPCC AR5
echo ========================================
echo.

REM Check Python environment
echo [1/3] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not detected
    echo Please install Python 3.9+
    pause
    exit /b 1
)
echo [OK] Python environment ready
echo.

REM Install dependencies
echo [2/3] Checking dependencies...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing FastAPI...
    pip install fastapi uvicorn
)
pip show numpy >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing NumPy...
    pip install numpy
)
echo [OK] Dependencies ready
echo.

REM Start server
echo [3/3] Starting API server...
echo Server address: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn real_api:app --host 0.0.0.0 --port 8000 --reload

pause

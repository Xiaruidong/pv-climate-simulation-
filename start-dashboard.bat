@echo off
chcp 65001 >nul
title PV Thermal Effect Simulator - Professional Dashboard

echo ========================================
echo    PV Thermal Effect Simulator
echo    Professional Dashboard v2.0
echo    Dark Tech UI Edition
echo ========================================
echo.

REM Check Node.js environment
echo [1/2] Checking Node.js environment...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found, please install Node.js 16+
    pause
    exit /b 1
)
echo OK: Node.js environment detected
echo.

REM Check and install frontend dependencies
echo [2/2] Checking frontend dependencies...
if not exist "node_modules" (
    echo Installing frontend dependencies for the first time...
    call npm install
    echo.
)
echo OK: Frontend dependencies ready
echo.

echo ========================================
echo    Starting Dashboard...
echo ========================================
echo.

echo Starting Professional Dashboard...
echo Dashboard: http://localhost:3000
echo.
echo Features:
echo - Dark Tech UI Design
echo - Real-time 3D Visualization
echo - Interactive Parameter Controls
echo - Live Metrics Display
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev

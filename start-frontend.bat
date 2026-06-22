@echo off
chcp 65001 >nul
echo Starting PV Climate Effect Simulation Frontend Service
echo.

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found
    pause
    exit /b 1
)

cd /d "%~dp0"

echo Checking dependencies...
if not exist "node_modules" (
    echo First time run, installing dependencies...
    call npm install
)

echo.
echo Starting Vite development server...
echo Frontend address: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev

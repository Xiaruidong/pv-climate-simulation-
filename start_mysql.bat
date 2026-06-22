@echo off
chcp 65001
echo ================================================
echo  Starting PV Climate Simulation System
echo ================================================
echo.

echo [1/3] Checking MySQL service...
sc query mysql >nul 2>&1
if %errorlevel% neq 0 (
    echo MySQL service is not running
    echo Please start MySQL service first:
    echo   - Windows: net start mysql
    echo   - Or use MySQL Workbench
    echo.
    echo Continuing with frontend only...
) else (
    echo MySQL service is running
)
echo.

echo [2/3] Starting MySQL API service...
cd /d %~dp0backend
if exist mysql_api.py (
    echo Starting MySQL API on http://localhost:5000
    start "MySQL API" cmd /k "python mysql_api.py"
    timeout /t 2 /nobreak >nul
) else (
    echo MySQL API file not found
    echo Please make sure mysql_api.py exists in backend folder
)
echo.

echo [3/3] Starting Vue frontend...
cd /d %~dp0
echo Starting Vue application on http://localhost:3000
start "Vue Frontend" cmd /k "npm run dev"

echo.
echo ================================================
echo  All services started successfully!
echo ================================================
echo.
echo Service addresses:
echo   - MySQL API:  http://localhost:5000/api/health
echo   - Vue App:    http://localhost:3000
echo.
echo Please wait a few seconds for services to fully start...
echo.
pause
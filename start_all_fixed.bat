@echo off
chcp 65001
echo ================================================
echo  Starting PV Climate Simulation System
echo ================================================
echo.

echo Checking MySQL service...
sc query mysql >nul 2>&1
if %errorlevel% neq 0 (
    echo MySQL service is not running
    echo Please start MySQL service:
    echo   Windows: net start mysql
    echo   Or restart MySQL from MySQL Workbench
    echo.
    echo Continuing with frontend only...
) else (
    echo MySQL service is running OK
)
echo.

echo Starting MySQL API service...
cd /d %~dp0backend
if exist mysql_api.py (
    echo Starting MySQL API on http://localhost:5000
    start cmd /k "python mysql_api.py"
    timeout /t 2 /nobreak >nul
) else (
    echo MySQL API not found, skipping...
)
echo.

echo Starting Vue frontend...
cd /d %~dp0
echo Starting Vue application on http://localhost:3000
start cmd /k "npm run dev"

echo.
echo ================================================
echo  Services started!
echo ================================================
echo.
echo Access the application at: http://localhost:3000
echo MySQL API health check: http://localhost:5000/api/health
echo.
echo Both services are running in separate windows.
echo Close those windows to stop the services.
echo.
pause

@echo off
echo Starting PV Climate Simulation System...
echo.

echo Step 1: Check MySQL
sc query mysql >nul 2>&1
if %errorlevel% neq 0 (
    echo MySQL is not running. Starting frontend only...
)
echo.

echo Step 2: Start MySQL API
cd backend
start mysql-api-server.cmd
timeout /t 2
echo.

echo Step 3: Start Vue Frontend
start vue-app.cmd
echo.

echo All services started!
echo Vue App: http://localhost:3000
echo MySQL API: http://localhost:5000/api/health
echo.
pause
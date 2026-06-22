@echo off
echo Starting MySQL from Anaconda installation...
echo.

REM Set MySQL path
set MYSQL_PATH=D:\software_install\Anaconda\Library\bin
set DATA_DIR=D:\software_install\Anaconda\Library\data

echo MySQL Path: %MYSQL_PATH%
echo Data Directory: %DATA_DIR%
echo.

REM Initialize MySQL database
echo Initializing MySQL database...
"%MYSQL_PATH%\mysql.exe" --user=root --skip-password < "CREATE DATABASE IF NOT EXISTS pv_climate_simulation; SHOW DATABASES;"

echo.
echo MySQL initialized successfully!
echo.
echo Next steps:
echo 1. Keep this window open (MySQL server running)
echo 2. In another window, run: python backend/mysql_api.py
echo 3. Then open: http://localhost:3000
echo.
pause
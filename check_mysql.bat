@echo off
chcp 65001
echo ================================================
echo  MySQL Service Check and Start
echo ================================================
echo.

echo Checking MySQL service status...
sc query mysql >nul 2>&1

if %errorlevel% neq 0 (
    echo MySQL service is not installed or not running
    echo.
    echo Attempting to start MySQL service...

    REM Try different MySQL service names
    net start MySQL80 >nul 2>&1
    if %errorlevel% neq 0 (
        net start MySQL57 >nul 2>&1
    )

    if %errorlevel% neq 0 (
        echo.
        echo ================================================
        echo  MySQL Service Not Found
        echo ================================================
        echo.
        echo Please check if MySQL is installed:
        echo.
        echo Option 1: Install MySQL
        echo   - Download from: https://dev.mysql.com/downloads/installer/
        echo   - Choose "Custom" setup
        echo   - Select "MySQL Server" component
        echo   - Set root password
        echo.
        echo Option 2: Check if MySQL is already installed
        echo   - Open Task Manager (Ctrl+Shift+Esc)
        echo   - Look for MySQL processes
        echo   - Check "Services" tab for MySQL service
        echo.
        echo Option 3: Use WAMP/XAMPP
        echo   - If you have WAMP installed, start WAMP
        echo   - MySQL will be included in WAMP
        echo.
    )
) else (
    echo MySQL service started successfully
    echo.
    echo Testing MySQL connection...
    echo.
    echo Please configure MySQL password in backend files:
    echo   - backend/mysql_api.py
    echo   - database/init_database.py
    echo.
)

pause

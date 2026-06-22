@echo off
chcp 65001
echo ================================================
echo  MySQL Installation Checker
echo ================================================
echo.

echo Searching for MySQL installation...
echo.

REM Check if MySQL is in PATH
where mysql >nul 2>&1
if %errorlevel% equ 0 (
    echo Found MySQL in PATH:
    where mysql
    echo.
)

REM Check common installation locations
set "found=0"

echo Checking Program Files...
if exist "C:\Program Files\MySQL\" (
    echo   Found: C:\Program Files\MySQL\
    set "found=1"
    dir /b "C:\Program Files\MySQL\"
)

if exist "C:\Program Files (x86)\MySQL\" (
    echo   Found: C:\Program Files (x86)\MySQL\
    set "found=1"
    dir /b "C:\Program Files (x86)\MySQL\"
)

if exist "D:\Program Files\MySQL\" (
    echo   Found: D:\Program Files\MySQL\
    set "found=1"
    dir /b "D:\Program Files\MySQL\"
)

if exist "C:\xampp\mysql\bin\" (
    echo   Found: C:\xampp\mysql\ (XAMPP)
    set "found=1"
    dir /b "C:\xampp\mysql\bin\"
)

if exist "C:\wamp64\bin\mysql.exe" (
    echo   Found: C:\wamp64\ (WAMP Server)
    set "found=1"
    dir "C:\wamp64\bin\mysql.exe"
)

if exist "C:\wamp\bin\mysql.exe" (
    echo   Found: C:\wamp\ (WAMP Server)
    set "found=1"
    dir "C:\wamp\bin\mysql.exe"
)

echo.
if %found%==0 (
    echo MySQL installation not found in common locations.
    echo.
    echo Please check:
    echo   1. Download MySQL Installer from: https://dev.mysql.com/downloads/installer/
    echo   2. Check default installation directories
    echo   3. Check if you have XAMPP or WAMP installed
) else (
    echo MySQL installation found!
)

echo.
echo Checking MySQL Service...
sc query MySQL80 >nul 2>&1
if %errorlevel% equ 0 (
    echo MySQL80 service exists
    sc query MySQL80 | find "STATE"
) else (
    echo MySQL80 service not found
)

sc query MySQL57 >nul 2>&1
if %errorlevel% equ 0 (
    echo MySQL57 service exists
    sc query MySQL57 | find "STATE"
) else (
    echo MySQL57 service not found
)

echo.
echo ================================================
echo  Next Steps:
echo ================================================
echo.
echo If MySQL service exists but not running:
echo   - Start: net start MySQL80
echo.
echo If MySQL is installed but no service:
echo   - Look for mysqld.exe in installation directory
echo   - Run: mysqld --console (for testing)
echo.
echo If using XAMPP/WAMP:
echo   - Start the XAMPP/WAMP control panel
echo   - MySQL will start automatically
echo.
echo For full instructions, see: MYSQL_SOLUTION.md
echo.

pause
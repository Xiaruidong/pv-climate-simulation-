@echo off
chcp 65001 >nul
title PV Simulation - Database Environment

echo ============================================
echo  光伏气候模拟系统 - 数据库环境一键启动
echo ============================================
echo.

set MYSQL_BIN=D:\software_install\Anaconda\Library\bin\mysqld.exe
set MYSQL_DATA=D:\vue_project\huaneng2\database\mysql_data
set MYSQL_MSG=D:\software_install\Anaconda\Library\share\mysql
set MYSQL_CLIENT=D:\software_install\Anaconda\Library\bin\mysql.exe

REM 1. 检查MySQL是否已运行
curl -s -m 2 -o nul http://localhost:5000/api/health
if %errorlevel%==0 (
    echo [OK] MySQL API 已在运行，无需重复启动
    pause
    exit /b 0
)

REM 2. 启动MySQL服务器（如未运行）
echo [1/3] 启动MySQL服务器...
"%MYSQL_CLIENT%" -u root --skip-password -e "SELECT 1" >nul 2>&1
if not %errorlevel%==0 (
    start "MySQL Server" "%MYSQL_BIN%" --console --datadir="%MYSQL_DATA%" --lc-messages-dir="%MYSQL_MSG%" --port=3306
    timeout /t 6 /nobreak >nul
)

REM 3. 确保数据库存在
echo [2/3] 检查/初始化数据库...
"%MYSQL_CLIENT%" -u root --skip-password --default-character-set=utf8mb4 -e "CREATE DATABASE IF NOT EXISTS pv_climate_simulation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci" 2>nul

REM 4. 启动MySQL API服务
echo [3/4] 启动MySQL API服务（端口5000）...
cd /d D:\vue_project\huaneng2\backend
start "MySQL API" python mysql_api.py
timeout /t 3 /nobreak >nul

REM 5. 启动EBM精确计算服务
echo [4/4] 启动EBM计算服务（端口8001）...
start "EBM API" python real_api.py
timeout /t 3 /nobreak >nul

curl -s -m 3 http://localhost:5000/api/health
echo.
curl -s -m 3 -o nul -w "EBM API: HTTP %{http_code}" http://localhost:8001/
echo.
echo.
echo [OK] 数据库环境启动完成！前端会自动检测并使用MySQL存储 + EBM精确计算。
pause

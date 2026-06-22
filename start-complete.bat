@echo off
chcp 65001 >nul
title 光伏热效应模拟器 - 完整版启动

echo ========================================
echo    光伏热效应模拟器 - 完整版
echo    专业仪表板 v2.0
echo    包含模拟、历史、设置功能
echo ========================================
echo.

REM 检查Node.js环境
echo [1/3] 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未检测到Node.js
    echo 请访问 https://nodejs.org/ 下载安装
    pause
    exit /b 1
)
echo [OK] Node.js环境正常
echo.

REM 检查并安装前端依赖
echo [2/3] 检查前端依赖...
if not exist "node_modules" (
    echo 首次启动，正在安装依赖包...
    call npm install
    echo.
)
echo [OK] 前端依赖检查完成
echo.

REM 检查Python环境（可选，用于后端）
echo [3/3] 检查Python环境（可选）...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] 未检测到Python环境
    echo 如需使用后端计算功能，请安装Python 3.9+
    echo.
) else (
    echo [OK] Python环境检测通过
    echo.
)
echo ========================================
echo    启动完整版系统...
echo ========================================
echo.

echo 启动前端服务...
echo 仪表板地址: http://localhost:3000
echo.
echo 包含功能:
echo   - 仪表板: 实时3D可视化 + 参数控制
echo   - 模拟: 高级模拟控制台 + 批量计算
echo   - 历史: 模拟记录管理 + 结果分析
echo   - 设置: 系统参数配置 + 偏好设置
echo.
echo 按Ctrl+C停止服务器
echo.

start "光伏热效应模拟器-前端" cmd /k "npm run dev"

echo.
echo ========================================
echo    系统启动完成！
echo ========================================
echo.
echo 浏览器访问: http://localhost:3000
echo.
echo 首次使用建议:
echo   1. 从"仪表板"开始，查看实时数据可视化
echo   2. 点击"模拟"标签体验高级计算功能
echo   3. 查看"历史"了解模拟记录管理
echo   4. 在"设置"中配置系统参数
echo.
echo 按任意键退出此窗口 (服务将继续运行)
pause >nul

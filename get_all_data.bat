@echo off
chcp 65001 >nul
title 环境数据一键获取和Excel生成工具

echo ========================================
echo    环境数据完整管理工具
echo ========================================
echo.
echo 本工具将完成以下任务:
echo 1. 从世界银行API获取最新数据
echo 2. 生成JSON格式数据文件
echo 3. 生成标准版Excel文件
echo 4. 生成详细版Excel文件
echo.

REM 检查Python环境
echo [1/4] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未检测到Python环境
    echo 请先安装Python 3.9+
    pause
    exit /b 1
)
echo [OK] Python环境检测通过
echo.

REM 安装依赖
echo [2/4] 检查并安装依赖包...
pip install pandas openpyxl requests -q
echo [OK] 依赖包检查完成
echo.

REM 创建数据目录
if not exist "data" mkdir data
echo [OK] 数据目录已准备
echo.

REM 获取世界银行数据
echo [3/4] 获取世界银行环境数据...
python data\simple_fetch.py
if %errorlevel% neq 0 (
    echo [ERROR] 数据获取失败
    pause
    exit /b 1
)
echo [OK] 世界银行数据获取完成
echo.

REM 生成Excel文件
echo [4/4] 生成Excel格式文件...
python data\create_excel.py
if %errorlevel% neq 0 (
    echo [ERROR] Excel生成失败
    pause
    exit /b 1
)
echo [OK] Excel文件生成完成
echo.

echo ========================================
echo    数据更新完成！
echo ========================================
echo.
echo 生成的文件:
echo [JSON格式]
echo   - data\current_environmental_data.json (最新数据)
echo   - data\environmental_data_YYYYMMDD_HHMM.json (历史数据)
echo.
echo [Excel格式]
echo   - data\environmental_data_excel.xlsx (标准版，10个工作表)
echo   - data\environmental_data_detailed.xlsx (详细版，10个工作表)
echo.
echo [使用说明]
echo   - data\EXCEL_GUIDE.md (详细使用指南)
echo.

choice /C YN /M "是否立即打开Excel文件查看"
if errorlevel 2 (
    echo.
    echo 文件已保存，您可以稍后打开
    echo 使用说明: data\EXCEL_GUIDE.md
) else (
    echo.
    echo 正在打开Excel文件...
    start data\environmental_data_excel.xlsx
)

echo.
echo ========================================
echo    后续操作建议
echo ========================================
echo.
echo 1. 查看Excel文件内容
echo 2. 阅读 data\EXCEL_GUIDE.md 了解使用方法
echo 3. 定期运行本脚本更新数据 (建议每月一次)
echo 4. 集成到您的项目中使用
echo.

pause

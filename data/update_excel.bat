@echo off
chcp 65001 >nul
echo ========================================
echo    环境数据Excel更新工具
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未检测到Python环境
    echo 请先安装Python 3.9+
    pause
    exit /b 1
)

echo [INFO] 开始更新Excel环境数据文件...
echo.

REM 检查JSON数据文件
if not exist "data\current_environmental_data.json" (
    echo [WARNING] JSON数据文件不存在，先获取数据...
    python data\simple_fetch.py
    echo.
)

REM 运行Excel生成脚本
python data\create_excel.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo    Excel文件更新成功!
    echo ========================================
    echo.
    echo 生成的文件:
    echo - data\environmental_data_excel.xlsx (标准版)
    echo - data\environmental_data_detailed.xlsx (详细版)
    echo.
    echo 使用说明:
    echo - 查看 data\EXCEL_GUIDE.md 了解详细使用方法
    echo.
    echo 下次更新:
    echo - 建议每月运行此脚本一次
    echo.
    choice /C YN /M "是否立即打开Excel文件"
    if errorlevel 2 (
        echo 文件已保存，可以稍后打开
    ) else (
        echo 正在打开Excel文件...
        start data\environmental_data_excel.xlsx
        start data\environmental_data_detailed.xlsx
    )
) else (
    echo.
    echo [ERROR] Excel文件更新失败
    echo 请检查:
    echo - Python环境是否正常
    echo - 是否安装了pandas和openpyxl
    echo - JSON数据文件是否存在
)

echo.
pause

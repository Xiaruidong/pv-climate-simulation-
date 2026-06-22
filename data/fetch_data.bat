@echo off
chcp 65001 >nul
echo ========================================
echo    环境数据快速获取工具
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python环境
    echo 请先安装Python 3.9+
    pause
    exit /b 1
)

echo 正在获取环境数据...
echo.

REM 进入数据目录
if not exist "data" mkdir data
cd data

REM 运行数据获取脚本
cd ..
python data\get_real_data.py

echo.
echo ========================================
echo    数据获取完成！
echo ========================================
echo.
echo 生成的文件:
echo - data/current_environmental_data.json (最新数据)
echo - data/sample_environmental_data.json (示例数据)
echo - data/environmental_data_YYYYMMDD.json (历史数据)
echo.
echo 按任意键查看数据来源信息...
pause >nul

start "" https://www.mee.gov.cn/
start "" https://data.worldbank.org/
start "" http://www.ceads.net.cn/

echo.
echo 数据获取工具已就绪！
pause

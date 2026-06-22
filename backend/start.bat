@echo off
chcp 65001 >nul
echo Starting Backend Service
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found, please install Python 3.9+
    pause
    exit /b 1
)

cd /d "%~dp0"

echo Installing dependencies...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo Starting FastAPI server...
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

python main.py
pause

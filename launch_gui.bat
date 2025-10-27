@echo off
REM PatentCheck-Desktop GUI 启动脚本 (Windows)

cd /d "%~dp0"

echo ======================================
echo   PatentCheck-Desktop GUI 启动中...
echo ======================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    echo 请先安装 Python 3
    pause
    exit /b 1
)

REM 检查依赖
echo 🔍 检查依赖...
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  未安装 PySide6，正在安装...
    pip install PySide6 Pillow python-docx reportlab
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
)

REM 启动GUI
echo 🚀 启动应用...
echo.
python src\gui\main_window.py

echo.
echo 应用已关闭
pause

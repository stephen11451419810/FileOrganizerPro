@echo off
echo ========================================
echo File Organizer Pro - 安装脚本
echo ========================================
echo.

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo 创建虚拟环境...
python -m venv venv

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装依赖包...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo 安装完成！
echo 运行 run.bat 启动程序
echo.
pause

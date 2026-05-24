@echo off
chcp 65001 >nul
title 拖拽文件夹到此窗口整理
color 0E

echo ========================================
echo    将文件夹拖拽到此窗口即可整理
echo ========================================
echo.
echo 💡 使用说明:
echo    1. 打开文件资源管理器
echo    2. 找到要整理的文件夹
echo    3. 把文件夹拖拽到这个黑色窗口
echo    4. 按回车开始整理
echo.
echo ========================================
echo.

set /p target_dir="📁 请拖拽文件夹到此处: "

set target_dir=%target_dir:"=%

if "%target_dir%"=="" (
    echo 未检测到文件夹，请重试
    pause
    exit /b
)

echo.
echo 正在整理: %target_dir%
echo.

python src/main.py -d "%target_dir%" -m auto

echo.
echo 整理完成！
pause

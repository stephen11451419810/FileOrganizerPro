@echo off
chcp 65001 >nul
title File Organizer Pro
color 0A

echo ========================================
echo    File Organizer Pro - 智能文件整理
echo ========================================
echo.
echo 请选择启动模式:
echo [1] 图形界面模式 (推荐 - 可视化选择文件夹)
echo [2] 命令行模式 (手动输入路径)
echo [3] 拖拽模式 (直接把文件夹拖到这里)
echo [4] 预览模式 (先看看效果)
echo.

set /p choice="请输入选项 (1/2/3/4): "

if "%choice%"=="1" goto gui
if "%choice%"=="2" goto cli
if "%choice%"=="3" goto drag
if "%choice%"=="4" goto preview

:gui
echo 启动图形界面...
python src/main.py --gui
goto end

:cli
echo.
echo 请输入要整理的文件夹路径
echo 例如: D:\我的文档\下载 或 C:\Users\Administrator\Desktop
echo.
set /p target_dir="文件夹路径: "
if "%target_dir%"=="" (
    echo 路径不能为空！
    pause
    goto cli
)
echo.
echo 正在整理: %target_dir%
python src/main.py -d "%target_dir%" -m auto
goto end

:drag
echo.
echo 请把文件夹拖拽到这里，然后按回车
echo.
set /p target_dir="拖拽文件夹到此窗口: "
set target_dir=%target_dir:"=%
if "%target_dir%"=="" (
    echo 路径不能为空！
    pause
    goto drag
)
echo.
echo 正在整理: %target_dir%
python src/main.py -d "%target_dir%" -m auto
goto end

:preview
echo.
echo 请拖拽或输入要预览的文件夹路径
set /p target_dir="文件夹路径: "
set target_dir=%target_dir:"=%
python src/main.py -d "%target_dir%" -m auto --preview
goto end

:end
echo.
echo 程序运行完毕
pause

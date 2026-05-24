@echo off
echo ========================================
echo 打包为EXE文件
echo ========================================

pip install pyinstaller

pyinstaller --onefile --windowed --name "FileOrganizerPro" --icon=icon.ico src/main.py

echo 打包完成！EXE文件在 dist 目录下
pause

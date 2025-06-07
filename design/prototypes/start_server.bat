@echo off
chcp 65001 >nul
title 访客管理系统 UI 原型服务器

echo.
echo ========================================
echo   访客管理系统 UI 原型预览服务器
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo 💡 请先安装Python 3.6或更高版本
    echo 📥 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查index.html是否存在
if not exist "index.html" (
    echo ❌ 错误: 找不到 index.html 文件
    echo 💡 请确保在 design/prototypes 目录中运行此脚本
    pause
    exit /b 1
)

REM 设置默认端口
set PORT=8000

REM 如果提供了端口参数
if not "%1"=="" (
    set PORT=%1
)

echo 🚀 正在启动服务器...
echo 📍 服务地址: http://localhost:%PORT%
echo 📁 服务目录: %CD%
echo 🌐 服务器启动后将自动打开浏览器
echo ⏹️  按 Ctrl+C 停止服务器
echo.
echo ----------------------------------------

REM 启动Python HTTP服务器
python start_server.py %PORT%

pause 
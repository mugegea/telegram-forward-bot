@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 启动 Telegram 转发机器人...

REM 检查配置文件
if not exist .env (
    echo ❌ 未找到 .env 配置文件
    echo 请先复制 config.env.example 为 .env 并配置 BOT_TOKEN
    echo copy config.env.example .env
    echo notepad .env
    pause
    exit /b 1
)

REM 检查 BOT_TOKEN
findstr /C:"BOT_TOKEN=your_bot_token_here" .env >nul
if !errorlevel! equ 0 (
    echo ❌ 请先在 .env 文件中配置 BOT_TOKEN
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist venv (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 📥 安装依赖...
pip install -r requirements.txt

REM 启动机器人
echo ✅ 启动机器人...
python bot.py

pause

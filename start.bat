@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo Starting Telegram Forward Bot...

REM Check if .env file exists
if not exist .env (
    echo Creating .env file from template...
    copy config.env.example .env
    echo.
    echo Please configure BOT_TOKEN in .env file before running the bot
    echo Opening .env file for editing...
    notepad .env
    echo.
    echo After configuring BOT_TOKEN, run this script again
    pause
    exit /b 1
)

REM Check if BOT_TOKEN is configured
findstr /C:"BOT_TOKEN=your_bot_token_here" .env >nul
if !errorlevel! equ 0 (
    echo Please configure BOT_TOKEN in .env file
    echo Opening .env file for editing...
    notepad .env
    echo.
    echo After configuring BOT_TOKEN, run this script again
    pause
    exit /b 1
)

REM Check virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Starting bot...
python bot.py

pause

@echo off
echo Запуск Crypto Subscription Bot...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate (
    call venv\Scripts\activate
)

REM Check if requirements are installed
pip list | findstr aiogram >nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Run the crypto subscription bot with environment variable for local testing
set ENV=local
python crypto_subscription_bot.py

echo.
echo Бот остановлен.
pause
@echo off
echo Запуск Telegram бота с интеграцией подписки через CryptoBot...

REM Activate virtual environment if it exists
if exist venv\Scripts\activate (
    call venv\Scripts\activate
)

REM Run the crypto subscription bot
python crypto_subscription_bot.py

echo.
echo Бот остановлен.
pause
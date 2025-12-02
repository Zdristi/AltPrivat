@echo off
echo Setting up Telegram subscription bot...

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

echo.
echo Setup complete!
echo To run the bot:
echo 1. Set your environment variables (TELEGRAM_BOT_TOKEN, PAYMENT_PROVIDER_TOKEN, CHANNEL_ID)
echo 2. Run: python bot.py

pause
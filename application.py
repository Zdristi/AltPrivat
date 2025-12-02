# application.py
from crypto_subscription_bot import dp, bot, init_db
from aiogram import Bot
from config import BOT_TOKEN
import os
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Initialize database
init_db()

# Webhook configuration for Heroku
WEBHOOK_PATH = '/webhook'
PORT = int(os.getenv('PORT', 8000))
DOMAIN = os.getenv('HEROKU_APP_NAME', '')  # Heroku sets this environment variable

if DOMAIN:
    DOMAIN = f"https://{DOMAIN}.herokuapp.com"

async def on_startup(dispatcher):
    """Register webhook on startup"""
    if DOMAIN:
        webhook_url = f"{DOMAIN}{WEBHOOK_PATH}"
        await dispatcher.delete_webhook(drop_pending_updates=True)
        await dispatcher.set_webhook(webhook_url)

async def on_shutdown(dispatcher):
    """Unregister webhook on shutdown"""
    await dispatcher.delete_webhook()

app = web.Application()

# Register startup and shutdown events
app.on_startup.append(lambda app: on_startup(dp))
app.on_shutdown.append(lambda app: on_shutdown(dp))

# Register webhook handler
webhook_requests_handler = SimpleRequestHandler(
    dispatcher=dp,
    bot=bot,
)
webhook_requests_handler.register(app, path=WEBHOOK_PATH)

# Setup application
setup_application(app, dp, bot=bot)
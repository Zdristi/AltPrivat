# Configuration file for Telegram subscription bot
import os

# Bot settings
BOT_TOKEN = os.getenv('BOT_TOKEN', '8301794491:AAGSSYUKo3nbII79dv2m1Usx3qDGAjwJEfs')  # Replace with your actual bot token
PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN', '123456789:TEST:123456789')  # Replace with actual provider token (use test token for testing)
CRYPTO_BOT_TOKEN = os.getenv('CRYPTO_BOT_TOKEN', '493946:AA4MBwVazCcDBRCR1dVt3ow0MPgURw1Zxul')  # API token for CryptoBot application
CHANNEL_ID = os.getenv('CHANNEL_ID', '-1003354955162')  # Replace with your channel username or ID

# Subscription settings
SUBSCRIPTION_DAYS = int(os.getenv('SUBSCRIPTION_DAYS', '30'))  # Number of days for a standard subscription
SUBSCRIPTION_PRICE = int(os.getenv('SUBSCRIPTION_PRICE', '99'))  # Default price in RUB (not used in new pricing system)

# Database settings
DATABASE_PATH = os.getenv('DATABASE_PATH', 'users.db')

# Messages
SUBSCRIPTION_NAME = os.getenv('SUBSCRIPTION_NAME', 'Ножки Альтушек')
WELCOME_MESSAGE = os.getenv('WELCOME_MESSAGE', "Добро пожаловать! 🎉\n\nПолучите доступ к каналу '{}' на 30 дней.\nЦена: {} ₽ / {} ₴")
SUBSCRIPTION_TITLE = os.getenv('SUBSCRIPTION_TITLE', 'Подписка на канал')
SUBSCRIPTION_DESCRIPTION = os.getenv('SUBSCRIPTION_DESCRIPTION', 'Доступ к приватному каналу на {} дней')
SUCCESSFUL_PAYMENT_MESSAGE = os.getenv('SUCCESSFUL_PAYMENT_MESSAGE', "Спасибо за покупку! 🎉\n\nТеперь вы можете получить доступ к каналу '{}'.\n\nДоступ открыт на {} дней с сегодняшнего дня.\n\nОплачено: {} ₽ / {} ₴")
ALREADY_SUBSCRIBED_MESSAGE = os.getenv('ALREADY_SUBSCRIBED_MESSAGE', 'У вас уже есть активная подписка!')

# Admin settings
# To get your Telegram User ID, message @userinfobot in Telegram
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '787999243'))  # Your Telegram User ID
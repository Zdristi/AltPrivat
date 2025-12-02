#!/usr/bin/env python3
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import sqlite3
from datetime import datetime

# Добавляем директорию с проектом в путь Python
sys.path.insert(0, '/home/vasya812/mysite')

# Импортируем конфигурацию
from config import BOT_TOKEN, CHANNEL_ID, SUBSCRIPTION_NAME, SUBSCRIPTION_PRICE, SUBSCRIPTION_DAYS, WELCOME_MESSAGE, SUCCESSFUL_PAYMENT_MESSAGE, ALREADY_SUBSCRIBED_MESSAGE, ADMIN_USER_ID

# Bot configuration
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', BOT_TOKEN)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create table if it doesn't exist (original structure)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            subscription_expires DATE,
            is_subscribed BOOLEAN DEFAULT 0
        )
    ''')

    # Add new columns if they don't exist
    try:
        cursor.execute("SELECT payment_history FROM users LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE users ADD COLUMN payment_history TEXT DEFAULT ''")

    try:
        cursor.execute("SELECT referrals_count FROM users LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE users ADD COLUMN referrals_count INTEGER DEFAULT 0")

    try:
        cursor.execute("SELECT payment_date FROM users LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE users ADD COLUMN payment_date DATE")

    try:
        cursor.execute("SELECT joined_date FROM users LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE users ADD COLUMN joined_date DATE DEFAULT (datetime('now', 'localtime'))")

    conn.commit()
    conn.close()

# Check if user has active subscription
def is_user_subscribed(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT is_subscribed, subscription_expires FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        is_sub, expires = result
        conn.close()
        if is_sub and datetime.now().date() <= datetime.fromisoformat(expires).date():
            return True
    else:
        # User doesn't exist in database, add them with default values
        current_date = datetime.now().date()
        cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, subscription_expires, is_subscribed, joined_date)
            VALUES (?, NULL, 0, ?)
        """, (user_id, current_date))
        conn.commit()
        conn.close()

    return False

# Update user subscription
def update_subscription(user_id, days=30, payment_method="Unknown"):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Calculate subscription expiration date
    current_date = datetime.now().date()
    expiration_date = (current_date + timedelta(days=days)).date()

    # Get current payment history
    cursor.execute("SELECT payment_history FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    current_history = result[0] if result and result[0] else ""

    # Add new payment record to history
    new_payment_record = f"{current_date}|{days} days|{payment_method}"
    updated_history = f"{current_history};{new_payment_record}" if current_history else new_payment_record

    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, subscription_expires, is_subscribed, payment_history, payment_date)
        VALUES (?, ?, 1, ?, ?)
    """, (user_id, expiration_date, updated_history, current_date))

    conn.commit()
    conn.close()

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.types import CallbackQuery
import logging
from datetime import timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)

# Create router
router = Router()

# Start command - show tariff selection
@router.message(Command("start"))
async def start_handler(message: Message):
    # Check if user came through referral link
    args = message.text.split()
    if len(args) > 1:
        referrer_id_str = args[1]
        try:
            referrer_id = int(referrer_id_str)
            # Update referrer's referral count
            if referrer_id != message.from_user.id:  # Don't count self-referral
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()

                # Check if referrer exists in database
                cursor.execute("SELECT referrals_count FROM users WHERE user_id = ?", (referrer_id,))
                result = cursor.fetchone()

                if result:
                    # Update referral count
                    new_referral_count = result[0] + 1
                    cursor.execute("UPDATE users SET referrals_count = ? WHERE user_id = ?", (new_referral_count, referrer_id))
                    conn.commit()

                conn.close()
        except ValueError:
            # Not a valid user ID, ignore
            pass

    # Simple check if user exists in database (this will add user if not exists)
    is_user_subscribed(message.from_user.id)

    # Create inline keyboard with multiple tariff options
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🪙 Фото ножек", callback_data='show_tariff_photo_legs')],
        [InlineKeyboardButton(text="🪙 Сочные альтухи", callback_data='show_tariff_juicy_altushki')],
        [InlineKeyboardButton(text="🪙 Мини пробничек", callback_data='show_tariff_mini_sampler')]
    ])

    # Simple welcome message without video
    welcome_text = "Выберите тариф:"

    await message.answer(
        welcome_text,
        reply_markup=keyboard
    )

# Referral command
@router.message(Command("ref"))
@router.message(Command("referal"))
async def referral_command(message: Message):
    from config import BOT_TOKEN
    # Получаем username пользователя
    username = message.from_user.username
    user_id = message.from_user.id
    
    if username:
        referral_link = f"https://t.me/{username}?start={user_id}"
    else:
        referral_link = f"https://t.me/your_bot_username?start={user_id}"

    referral_message = f"""
🔗 Ваша реферальная ссылка:

`{referral_link}`

Поделитесь этой ссылкой с друзьями!
За каждого приглашённого пользователя вы получаете +1 к счёту приглашений.

Ваши приглашения: {get_referral_count(message.from_user.id)}
"""

    await message.answer(referral_message, parse_mode="Markdown")

def get_referral_count(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT referrals_count FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

# Handle tariff selection for main tariff
@router.callback_query(lambda c: c.data == 'show_tariff_main')
async def show_tariff_handler(callback_query: CallbackQuery):
    await callback_query.answer()

    # Video URL from Google Drive
    VIDEO_URL = "https://drive.google.com/uc?export=download&id=1Ig7RUISBOaAnIgzn2IuZTuBxQl_gHXZB"

    # Caption with Markdown formatting for the tariff page (changed to UAH)
    from config import SUBSCRIPTION_NAME, SUBSCRIPTION_DAYS, SUBSCRIPTION_PRICE

    caption = f"""
🎉 *{SUBSCRIPTION_NAME.upper()}* 🎉

Доступ к каналу *{SUBSCRIPTION_NAME}* на *{SUBSCRIPTION_DAYS} дней*

 Цена: *{SUBSCRIPTION_PRICE} ₴*

 🎁 Специальное предложение!
 🔥 Лучшее качество!
 💎 Эксклюзивный контент!
    """

    # Create inline keyboard with payment options and back button
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Укр карта", callback_data='payment_card')],
        [InlineKeyboardButton(text="⭐ Звезды Telegram", callback_data='payment_stars')],
        [InlineKeyboardButton(text="🪙 Crypto Bot", callback_data='payment_crypto')],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data='back_to_tariffs')]
    ])

    # Send video with caption on the tariff page
    try:
        await bot.send_video(
            chat_id=callback_query.from_user.id,
            video=VIDEO_URL,
            caption=caption,
            parse_mode='Markdown',  # Use Markdown for formatting
            reply_markup=back_keyboard
        )
    except Exception as e:
        logging.error(f"Failed to send video: {e}")
        # Fallback message if video fails
        await callback_query.message.answer(
            f"Видео недоступно, но вы можете оформить '{SUBSCRIPTION_NAME}'!\n\n"
            f"Цена: {SUBSCRIPTION_PRICE} ₴\n"
            f"Длительность: {SUBSCRIPTION_DAYS} дней",
            reply_markup=back_keyboard
        )

# Handle tariff selection for "Фото ножек"
@router.callback_query(lambda c: c.data == 'show_tariff_photo_legs')
async def show_tariff_photo_legs_handler(callback_query: CallbackQuery):
    await callback_query.answer()

    # Video URL from Google Drive
    VIDEO_URL = "https://drive.google.com/uc?export=download&id=1Ig7RUISBOaAnIgzn2IuZTuBxQl_gHXZB"

    # Caption with Markdown formatting for the tariff page (changed to UAH/RUB)
    tariff_name = "Фото ножек"
    tariff_price_uah = 50  # New price for this tariff
    tariff_price_rub = 130  # RUB equivalent

    caption = f"""
🎉 *{tariff_name.upper()}* 🎉

Доступ к каналу *{SUBSCRIPTION_NAME}* на *{SUBSCRIPTION_DAYS} дней*

 Цена: *{tariff_price_rub} ₽ / {tariff_price_uah} ₴*

 🎁 Специальное предложение!
 🔥 Красивые ножки!
 💎 Фото высокого качества!
    """

    # Create inline keyboard with payment options and back button
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Укр карта", callback_data='payment_card')],
        [InlineKeyboardButton(text="⭐ Звезды Telegram", callback_data='payment_stars')],
        [InlineKeyboardButton(text="🪙 Crypto Bot", callback_data='payment_crypto')],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data='back_to_tariffs')]
    ])

    # Send video with caption on the tariff page
    try:
        await bot.send_video(
            chat_id=callback_query.from_user.id,
            video=VIDEO_URL,
            caption=caption,
            parse_mode='Markdown',  # Use Markdown for formatting
            reply_markup=back_keyboard
        )
    except Exception as e:
        logging.error(f"Failed to send video: {e}")
        # Fallback message if video fails
        await callback_query.message.answer(
            f"Видео недоступно, но вы можете оформить '{tariff_name}'!\n\n"
            f"Цена: {tariff_price_rub} ₽ / {tariff_price_uah} ₴\n"
            f"Длительность: {SUBSCRIPTION_DAYS} дней",
            reply_markup=back_keyboard
        )

# Handle tariff selection for "Сочные альтухи"
@router.callback_query(lambda c: c.data == 'show_tariff_juicy_altushki')
async def show_tariff_juicy_altushki_handler(callback_query: CallbackQuery):
    await callback_query.answer()

    # Video URL from Google Drive
    VIDEO_URL = "https://drive.google.com/uc?export=download&id=1Ig7RUISBOaAnIgzn2IuZTuBxQl_gHXZB"

    # Caption with Markdown formatting for the tariff page (changed to UAH/RUB)
    tariff_name = "Сочные альтухи"
    tariff_price_uah = 100  # New price for this tariff
    tariff_price_rub = 260  # RUB equivalent

    caption = f"""
🎉 *{tariff_name.upper()}* 🎉

Доступ к каналу *{SUBSCRIPTION_NAME}* на *{SUBSCRIPTION_DAYS} дней*

 Цена: *{tariff_price_rub} ₽ / {tariff_price_uah} ₴*

 🎁 Сочные и сочные!
 🔥 Мокренькие!
 💎 Вкусняшки!
    """

    # Create inline keyboard with payment options and back button
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Укр карта", callback_data='payment_card')],
        [InlineKeyboardButton(text="⭐ Звезды Telegram", callback_data='payment_stars')],
        [InlineKeyboardButton(text="🪙 Crypto Bot", callback_data='payment_crypto')],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data='back_to_tariffs')]
    ])

    # Send video with caption on the tariff page
    try:
        await bot.send_video(
            chat_id=callback_query.from_user.id,
            video=VIDEO_URL,
            caption=caption,
            parse_mode='Markdown',  # Use Markdown for formatting
            reply_markup=back_keyboard
        )
    except Exception as e:
        logging.error(f"Failed to send video: {e}")
        # Fallback message if video fails
        await callback_query.message.answer(
            f"Видео недоступно, но вы можете оформить '{tariff_name}'!\n\n"
            f"Цена: {tariff_price_rub} ₽ / {tariff_price_uah} ₴\n"
            f"Длительность: {SUBSCRIPTION_DAYS} дней",
            reply_markup=back_keyboard
        )

# Handle tariff selection for "Мини пробничек"
@router.callback_query(lambda c: c.data == 'show_tariff_mini_sampler')
async def show_tariff_mini_sampler_handler(callback_query: CallbackQuery):
    await callback_query.answer()

    # Video URL from Google Drive
    VIDEO_URL = "https://drive.google.com/uc?export=download&id=1Ig7RUISBOaAnIgzn2IuZTuBxQl_gHXZB"

    # Caption with Markdown formatting for the tariff page (changed to UAH/RUB)
    tariff_name = "Мини пробничек"
    tariff_price_uah = 35  # New price for this tariff
    tariff_price_rub = 90  # RUB equivalent

    caption = f"""
🎉 *{tariff_name.upper()}* 🎉

Доступ к каналу *{SUBSCRIPTION_NAME}* на *15 дней*

 Цена: *{tariff_price_rub} ₽ / {tariff_price_uah} ₴*

 🎁 Маленький, но вкусный!
 🔥 Только для ознакомления!
 💎 Пробный период!
    """

    # Create inline keyboard with payment options and back button
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Укр карта", callback_data='payment_card')],
        [InlineKeyboardButton(text="⭐ Звезды Telegram", callback_data='payment_stars')],
        [InlineKeyboardButton(text="🪙 Crypto Bot", callback_data='payment_crypto')],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data='back_to_tariffs')]
    ])

    # Send video with caption on the tariff page
    try:
        await bot.send_video(
            chat_id=callback_query.from_user.id,
            video=VIDEO_URL,
            caption=caption,
            parse_mode='Markdown',  # Use Markdown for formatting
            reply_markup=back_keyboard
        )
    except Exception as e:
        logging.error(f"Failed to send video: {e}")
        # Fallback message if video fails
        await callback_query.message.answer(
            f"Видео недоступно, но вы можете оформить '{tariff_name}'!\n\n"
            f"Цена: {tariff_price_rub} ₽ / {tariff_price_uah} ₴\n"
            f"Длительность: 15 дней",
            reply_markup=back_keyboard
        )


# Handle back button to return to tariff selection
@router.callback_query(lambda c: c.data == 'back_to_tariffs')
async def back_to_tariffs_handler(callback_query: CallbackQuery):
    await callback_query.answer()

    # Create inline keyboard with multiple tariff options
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🪙 Фото ножек", callback_data='show_tariff_photo_legs')],
        [InlineKeyboardButton(text="🪙 Сочные альтухи", callback_data='show_tariff_juicy_altushki')],
        [InlineKeyboardButton(text="🪙 Мини пробничек", callback_data='show_tariff_mini_sampler')]
    ])

    # Try to edit text if it's a text message, otherwise send new message
    try:
        await callback_query.message.edit_text(
            "Выберите тариф:",
            reply_markup=keyboard
        )
    except Exception:
        # If message doesn't have text (e.g., it's a video), send new message
        await callback_query.message.answer(
            "Выберите тариф:",
            reply_markup=keyboard
        )
        # Delete the previous message that contained video
        try:
            await callback_query.message.delete()
        except Exception:
            pass  # If message can't be deleted, just ignore

# Handle payment card option (through operator)
@router.callback_query(lambda c: c.data == 'payment_card')
async def payment_card_handler(callback_query: CallbackQuery):
    await callback_query.answer()

    # Check if user already has active subscription
    if is_user_subscribed(callback_query.from_user.id):
        await callback_query.message.answer(ALREADY_SUBSCRIBED_MESSAGE)
        return

    # Instructions for payment via Ukrainian card through operator (with dual currency)
    default_price_uah = 50  # Average price for tariff
    default_price_rub = 130  # RUB equivalent

    instructions = f"""
    🎉 Подписка '{SUBSCRIPTION_NAME}' 🎉

    Оплата картой через оператора:

    1. Нажмите на кнопку "Оплатить картой" ниже
    2. Выберите удобный для вас способ оплаты
    3. Укажите сумму {default_price_rub} ₽ / {default_price_uah} ₴
    4. В комментарии укажите ваш Telegram ID: @{callback_query.from_user.username or callback_query.from_user.id}

    После оплаты сохраните чек и следуйте инструкциям оператора
    """

    # Add back button to payment options
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить картой", url="https://t.me/your_operator_bot")],  # Replace with actual operator link
        [InlineKeyboardButton(text="⬅️ Назад", callback_data='back_to_tariffs')]
    ])

    await callback_query.message.answer(instructions, reply_markup=back_keyboard)

# Handle payment via Telegram Stars
@router.callback_query(lambda c: c.data == 'payment_stars')
async def payment_stars_handler(callback_query: CallbackQuery):
    await callback_query.answer()

    # Check if user already has active subscription
    if is_user_subscribed(callback_query.from_user.id):
        await callback_query.message.answer(ALREADY_SUBSCRIBED_MESSAGE)
        return

    # Send subscription invoice using Telegram Stars
    from aiogram.types import LabeledPrice
    try:
        await bot.send_invoice(
            chat_id=callback_query.from_user.id,
            title=f"Подписка на канал {SUBSCRIPTION_NAME}",
            description=f"Доступ к каналу '{SUBSCRIPTION_NAME}' на {SUBSCRIPTION_DAYS} дней",
            payload="channel_subscription_stars",
            provider_token='',  # Empty token for Telegram Stars
            currency='XTR',  # Telegram Stars
            prices=[LabeledPrice(label=f'Подписка на {SUBSCRIPTION_DAYS} дней', amount=99)]
        )
    except Exception as e:
        logging.error(f"Failed to send Telegram Stars invoice: {e}")
        # Fallback message
        default_price_uah = 50  # Average price for tariff
        default_price_rub = 130  # RUB equivalent

        await callback_query.message.answer(
            f"Ошибка при создании счёта звёздами. Попробуйте оплатить через украинскую карту.\n\n"
            f"Цена: {default_price_rub} ₽ / {default_price_uah} ₴\n"
            f"Длительность: {SUBSCRIPTION_DAYS} дней"
        )

# Handle payment via CryptoBot (using payment link)
@router.callback_query(lambda c: c.data == 'payment_crypto')
async def payment_crypto_handler(callback_query: CallbackQuery):
    await callback_query.answer()

    # Check if user already has active subscription
    if is_user_subscribed(callback_query.from_user.id):
        await callback_query.message.answer(ALREADY_SUBSCRIBED_MESSAGE)
        return

    # Create inline keyboard with payment link and back button
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🪙 Купить через Crypto Bot", url="https://t.me/send?start=SBnoOjz9gFhrwxMzli")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data='back_to_tariffs')]
    ])

    # Using default crypto price - we should update this according to the tariff
    crypto_price_uah = 50  # Default price for crypto payment
    crypto_price_rub = 130  # RUB equivalent for crypto payment

    await callback_query.message.answer(
        f"Для оплаты подписки через Crypto Bot перейдите по ссылке ниже:\n\n"
        f"Доступ к каналу '{SUBSCRIPTION_NAME}' на {SUBSCRIPTION_DAYS} дней\n"
        f"Сумма: {crypto_price_rub} ₽ / {crypto_price_uah} ₴",
        reply_markup=back_keyboard
    )

# Handle successful payment via Telegram Stars
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: CallbackQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(lambda message: message.successful_payment is not None)
async def successful_payment(message: Message):
    # Update user subscription in database
    update_subscription(message.from_user.id, SUBSCRIPTION_DAYS, "Telegram Stars")

    # Send welcome message with channel link (with dual currency)
    default_price_uah = 50  # Average price for tariff
    default_price_rub = 130  # RUB equivalent

    await message.answer(
        SUCCESSFUL_PAYMENT_MESSAGE.format(SUBSCRIPTION_NAME, SUBSCRIPTION_DAYS, default_price_rub, default_price_uah)
    )

# Admin commands
@router.message(Command("broadcast"))
async def broadcast_command(message: Message):
    # Check if user is admin
    if message.from_user.id != ADMIN_USER_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    # Extract broadcast message
    if not message.text or len(message.text.split()) < 2:
        await message.answer("Использование: /broadcast <сообщение для рассылки>")
        return

    broadcast_text = ' '.join(message.text.split()[1:])

    # Get all user IDs from database (not just subscribed)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    user_ids = cursor.fetchall()
    conn.close()

    successful_sends = 0
    failed_sends = 0

    for user_id_tuple in user_ids:
        user_id = user_id_tuple[0]
        try:
            await bot.send_message(user_id, f"📢 {broadcast_text}")
            successful_sends += 1
        except Exception as e:
            # User might have blocked the bot
            failed_sends += 1

    await message.answer(f"Рассылка завершена!\n"
                        f"Отправлено: {successful_sends} пользователей\n"
                        f"Неудачно: {failed_sends} пользователей")

@router.message(Command("stats"))
async def stats_command(message: Message):
    # Check if user is admin
    if message.from_user.id != ADMIN_USER_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    # Get statistics from database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Total users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # Active subscribers
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_subscribed = 1")
    active_subscribers = cursor.fetchone()[0]

    # Total payments
    cursor.execute("SELECT COUNT(*) FROM users WHERE payment_history != ''")
    total_payments = cursor.fetchone()[0]

    # Total referrals
    cursor.execute("SELECT SUM(referrals_count) FROM users")
    total_referrals = cursor.fetchone()[0] or 0

    conn.close()

    stats_message = f"""
📊 Статистика бота:

👥 Всего пользователей: {total_users}
✅ Активных подписчиков: {active_subscribers}
💳 Всего оплат: {total_payments}
🔗 Всего рефералов: {total_referrals}
    """

    await message.answer(stats_message)

# Handle subscribe channel button
@router.callback_query(lambda c: c.data == 'subscribe_channel')
async def process_subscribe_channel(callback_query: CallbackQuery):
    await callback_query.answer()

    # Check if user already has active subscription
    if is_user_subscribed(callback_query.from_user.id):
        await callback_query.message.answer(ALREADY_SUBSCRIBED_MESSAGE)
        return

    # Instructions for subscription with payment options (dual currency)
    default_price_uah = 50  # Average price for tariff
    default_price_rub = 130  # RUB equivalent

    instructions = f"""
    🎉 Подписка '{SUBSCRIPTION_NAME}' 🎉

    Для получения доступа к каналу '{SUBSCRIPTION_NAME}' на {SUBSCRIPTION_DAYS} дней:

    Цена: {default_price_rub} ₽ / {default_price_uah} ₴

    Выберите удобный способ оплаты:
    """

    # Add back button to payment options
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Укр карта", callback_data='payment_card')],
        [InlineKeyboardButton(text="⭐ Звезды Telegram", callback_data='payment_stars')],
        [InlineKeyboardButton(text="🪙 Crypto Bot", callback_data='payment_crypto')],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data='back_to_tariffs')]
    ])

    await callback_query.message.answer(instructions, reply_markup=back_keyboard)

# Register the router
dp.include_router(router)

# Webhook configuration
WEBHOOK_PATH = '/webhook'
HOST = '0.0.0.0'
PORT = int(os.getenv('PORT', 8000))  # PythonAnywhere uses environment PORT
DOMAIN = os.getenv('DOMAIN', 'your-username.pythonanywhere.com')  # Replace with your actual domain

async def on_startup(dispatcher):
    """Register webhook on startup"""
    webhook_url = f"https://{DOMAIN}{WEBHOOK_PATH}"
    await dispatcher.delete_webhook(drop_pending_updates=True)
    await dispatcher.set_webhook(webhook_url)

async def on_shutdown(dispatcher):
    """Unregister webhook on shutdown"""
    await dispatcher.delete_webhook()

def main():
    init_db()
    
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

    return app

# Create the application instance
application = main()

if __name__ == '__main__':
    web.run_app(
        application,
        host=HOST,
        port=PORT,
    )
import os
import json
import sqlite3
from datetime import datetime, timedelta
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import logging

# Установка логирования
logging.basicConfig(level=logging.INFO)

# Конфигурация бота
BOT_TOKEN = os.getenv('BOT_TOKEN', '8301794491:AAGSSYUKo3nbII79dv2m1Usx3qDGAjwJEfs')
CHANNEL_ID = os.getenv('CHANNEL_ID', '-1003354955162')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '787999243'))
SUBSCRIPTION_NAME = os.getenv('SUBSCRIPTION_NAME', 'Ножки Альтушек')
SUBSCRIPTION_DAYS = int(os.getenv('SUBSCRIPTION_DAYS', '30'))
SUBSCRIPTION_PRICE = int(os.getenv('SUBSCRIPTION_PRICE', '99'))

# База данных
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            subscription_expires DATE,
            is_subscribed BOOLEAN DEFAULT 0,
            payment_history TEXT DEFAULT '',
            referrals_count INTEGER DEFAULT 0,
            payment_date DATE,
            joined_date DATE DEFAULT (datetime('now', 'localtime'))
        )
    ''')
    conn.commit()
    conn.close()

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
        # Пользователь не существует в базе, добавляем его
        current_date = datetime.now().date()
        cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, subscription_expires, is_subscribed, joined_date)
            VALUES (?, NULL, 0, ?)
        """, (user_id, current_date))
        conn.commit()
        conn.close()
    
    return False

def update_subscription(user_id, days=30, payment_method="Unknown"):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Рассчитываем дату окончания подписки
    current_date = datetime.now().date()
    expiration_date = (current_date + timedelta(days=days)).date()
    
    # Получаем текущую историю платежей
    cursor.execute("SELECT payment_history FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    current_history = result[0] if result and result[0] else ""
    
    # Добавляем новую запись о платеже в историю
    new_payment_record = f"{current_date}|{days} days|{payment_method}"
    updated_history = f"{current_history};{new_payment_record}" if current_history else new_payment_record
    
    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, subscription_expires, is_subscribed, payment_history, payment_date)
        VALUES (?, ?, 1, ?, ?)
    """, (user_id, expiration_date, updated_history, current_date))
    
    conn.commit()
    conn.close()

# Отправка сообщения через Telegram API
def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    
    response = requests.post(url, data=data)
    return response.json()

# Отправка инвойса (для Telegram Stars)
def send_invoice(chat_id, title, description, payload, provider_token, currency, prices):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendInvoice"
    data = {
        'chat_id': chat_id,
        'title': title,
        'description': description,
        'payload': payload,
        'provider_token': provider_token,
        'currency': currency,
        'prices': json.dumps(prices)
    }
    
    response = requests.post(url, data=data)
    return response.json()

def answer_pre_checkout_query(pre_checkout_query_id, ok=True, error_message=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerPreCheckoutQuery"
    data = {
        'pre_checkout_query_id': pre_checkout_query_id,
        'ok': ok
    }
    if error_message:
        data['error_message'] = error_message
    
    response = requests.post(url, data=data)
    return response.json()

# Обработка команд
def handle_start(user_id, text):
    # Проверяем, пришел ли пользователь по реферальной ссылке
    args = text.split()
    if len(args) > 1:
        referrer_id_str = args[1]
        try:
            referrer_id = int(referrer_id_str)
            # Обновляем количество рефералов у пригласившего
            if referrer_id != user_id:  # Не считаем самоприглашение
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                
                # Проверяем, существует ли пригласивший пользователь в базе
                cursor.execute("SELECT referrals_count FROM users WHERE user_id = ?", (referrer_id,))
                result = cursor.fetchone()
                
                if result:
                    # Обновляем количество рефералов
                    new_referral_count = result[0] + 1
                    cursor.execute("UPDATE users SET referrals_count = ? WHERE user_id = ?", (new_referral_count, referrer_id))
                    conn.commit()
                
                conn.close()
        except ValueError:
            # Это не корректный ID пользователя, игнорируем
            pass
    
    # Простая проверка, существует ли пользователь в базе (это добавит пользователя, если его нет)
    is_user_subscribed(user_id)
    
    # Создаем клавиатуру с тарифами
    keyboard = {
        'inline_keyboard': [
            [{'text': '🪙 Фото ножек', 'callback_data': 'show_tariff_photo_legs'}],
            [{'text': '🪙 Сочные альтухи', 'callback_data': 'show_tariff_juicy_altushki'}],
            [{'text': '🪙 Мини пробничек', 'callback_data': 'show_tariff_mini_sampler'}]
        ]
    }
    
    # Приветственное сообщение
    welcome_text = "Выберите тариф:"
    
    return send_message(user_id, welcome_text, keyboard)

def get_referral_count(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT referrals_count FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def handle_referral(user_id, username):
    referral_link = f"https://t.me/{username or 'username_not_set'}?start={user_id}"
    
    referral_message = f"""
🔗 Ваша реферальная ссылка:

`{referral_link}`

Поделитесь этой ссылкой с друзьями!
За каждого приглашённого пользователя вы получаете +1 к счёту приглашений.

Ваши приглашения: {get_referral_count(user_id)}
"""
    
    return send_message(user_id, referral_message)

def handle_tariff_selection(user_id, tariff_data):
    # Определяем тариф
    if tariff_data == 'show_tariff_photo_legs':
        tariff_name = "Фото ножек"
        tariff_price_uah = 50
        tariff_price_rub = 130
        tariff_days = SUBSCRIPTION_DAYS
    elif tariff_data == 'show_tariff_juicy_altushki':
        tariff_name = "Сочные альтухи"
        tariff_price_uah = 100
        tariff_price_rub = 260
        tariff_days = SUBSCRIPTION_DAYS
    elif tariff_data == 'show_tariff_mini_sampler':
        tariff_name = "Мини пробничек"
        tariff_price_uah = 35
        tariff_price_rub = 90
        tariff_days = 15  # 15 дней для пробника
    else:
        # Основной тариф
        tariff_name = SUBSCRIPTION_NAME
        tariff_price_uah = SUBSCRIPTION_PRICE
        tariff_price_rub = int(SUBSCRIPTION_PRICE * 2.6)  # Примерный пересчет в рубли
        tariff_days = SUBSCRIPTION_DAYS
    
    caption = f"""
🎉 *{tariff_name.upper()}* 🎉

Доступ к каналу *{SUBSCRIPTION_NAME}* на *{tariff_days} дней*

 Цена: *{tariff_price_rub} ₽ / {tariff_price_uah} ₴*

 🎁 Специальное предложение!
 🔥 Лучшее качество!
 💎 Эксклюзивный контент!
"""
    
    # Клавиатура с вариантами оплаты
    back_keyboard = {
        'inline_keyboard': [
            [{'text': '💳 Укр карта', 'callback_data': 'payment_card'}],
            [{'text': '⭐ Звезды Telegram', 'callback_data': 'payment_stars'}],
            [{'text': '🪙 Crypto Bot', 'callback_data': 'payment_crypto'}],
            [{'text': '⬅️ Назад', 'callback_data': 'back_to_tariffs'}]
        ]
    }
    
    return send_message(user_id, caption, back_keyboard)

def handle_payment_option(user_id, payment_option):
    # Проверяем, есть ли у пользователя активная подписка
    if is_user_subscribed(user_id):
        return send_message(user_id, "У вас уже есть активная подписка!")
    
    # Варианты оплаты
    if payment_option == 'payment_card':
        default_price_uah = 50
        default_price_rub = 130
        
        instructions = f"""
🎉 Подписка '{SUBSCRIPTION_NAME}' 🎉

Оплата картой через оператора:

1. Нажмите на кнопку "Оплатить картой" ниже
2. Выберите удобный для вас способ оплаты
3. Укажите сумму {default_price_rub} ₽ / {default_price_uah} ₴
4. В комментарии укажите ваш Telegram ID: @{user_id}

После оплаты сохраните чек и следуйте инструкциям оператора
"""
        
        back_keyboard = {
            'inline_keyboard': [
                [{'text': '💳 Оплатить картой', 'url': 'https://t.me/your_operator_bot'}],
                [{'text': '⬅️ Назад', 'callback_data': 'back_to_tariffs'}]
            ]
        }
        
        return send_message(user_id, instructions, back_keyboard)
    
    elif payment_option == 'payment_stars':
        # Отправляем инвойс для оплаты звёздами
        prices = [{'label': f'Подписка на {SUBSCRIPTION_DAYS} дней', 'amount': 99}]  # 99 звёзд
        return send_invoice(
            user_id,
            f"Подписка на канал {SUBSCRIPTION_NAME}",
            f"Доступ к каналу '{SUBSCRIPTION_NAME}' на {SUBSCRIPTION_DAYS} дней",
            "channel_subscription_stars",
            "",  # Пустой токен для звёзд
            "XTR",  # Код валюты для звёзд
            prices
        )
    
    elif payment_option == 'payment_crypto':
        crypto_price_uah = 50
        crypto_price_rub = 130
        
        back_keyboard = {
            'inline_keyboard': [
                [{'text': '🪙 Купить через Crypto Bot', 'url': 'https://t.me/send?start=SBnoOjz9gFhrwxMzli'}],
                [{'text': '⬅️ Назад', 'callback_data': 'back_to_tariffs'}]
            ]
        }
        
        return send_message(
            user_id,
            f"Для оплаты подписки через Crypto Bot перейдите по ссылке ниже:\n\n"
            f"Доступ к каналу '{SUBSCRIPTION_NAME}' на {SUBSCRIPTION_DAYS} дней\n"
            f"Сумма: {crypto_price_rub} ₽ / {crypto_price_uah} ₴",
            back_keyboard
        )

def handle_back_to_tariffs(user_id):
    keyboard = {
        'inline_keyboard': [
            [{'text': '🪙 Фото ножек', 'callback_data': 'show_tariff_photo_legs'}],
            [{'text': '🪙 Сочные альтухи', 'callback_data': 'show_tariff_juicy_altushki'}],
            [{'text': '🪙 Мини пробничек', 'callback_data': 'show_tariff_mini_sampler'}]
        ]
    }
    
    return send_message(user_id, "Выберите тариф:", keyboard)

def handle_successful_payment(user_id):
    # Обновляем подписку пользователя в базе
    update_subscription(user_id, SUBSCRIPTION_DAYS, "Telegram Stars")
    
    default_price_uah = 50
    default_price_rub = 130
    
    message = f"Спасибо за покупку! 🎉\n\nТеперь вы можете получить доступ к каналу '{SUBSCRIPTION_NAME}'.\n\nДоступ открыт на {SUBSCRIPTION_DAYS} дней с сегодняшнего дня.\n\nОплачено: {default_price_rub} ₽ / {default_price_uah} ₴"
    
    return send_message(user_id, message)

def handle_broadcast(user_id, message_text):
    # Проверяем, является ли пользователь администратором
    if user_id != ADMIN_USER_ID:
        return send_message(user_id, "У вас нет прав для выполнения этой команды.")
    
    # Извлекаем текст рассылки
    if not message_text or len(message_text.split()) < 2:
        return send_message(user_id, "Использование: /broadcast <сообщение для рассылки>")
    
    broadcast_text = ' '.join(message_text.split()[1:])
    
    # Получаем все ID пользователей из базы
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    user_ids = cursor.fetchall()
    conn.close()
    
    successful_sends = 0
    failed_sends = 0
    
    for user_id_tuple in user_ids:
        try:
            send_message(user_id_tuple[0], f"📢 {broadcast_text}")
            successful_sends += 1
        except Exception:
            # Пользователь мог заблокировать бота
            failed_sends += 1
    
    return send_message(user_id, f"Рассылка завершена!\nОтправлено: {successful_sends} пользователей\nНеудачно: {failed_sends} пользователей")

def handle_stats(user_id):
    # Проверяем, является ли пользователь администратором
    if user_id != ADMIN_USER_ID:
        return send_message(user_id, "У вас нет прав для выполнения этой команды.")
    
    # Получаем статистику из базы
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Всего пользователей
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    # Активные подписчики
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_subscribed = 1")
    active_subscribers = cursor.fetchone()[0]
    
    # Всего платежей
    cursor.execute("SELECT COUNT(*) FROM users WHERE payment_history != ''")
    total_payments = cursor.fetchone()[0]
    
    # Всего рефералов
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
    
    return send_message(user_id, stats_message)

# HTTP-сервер для обработки вебхуков
class TelegramWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            update = json.loads(post_data)
            
            # Обработка обновлений от Telegram
            if 'message' in update:
                message = update['message']
                user_id = message['from']['id']
                text = message.get('text', '')
                
                # Обработка команд
                if text.startswith('/start'):
                    handle_start(user_id, text)
                elif text.startswith('/ref') or text.startswith('/referal'):
                    handle_referral(user_id, message['from'].get('username'))
                elif text.startswith('/broadcast'):
                    handle_broadcast(user_id, text)
                elif text.startswith('/stats'):
                    handle_stats(user_id)
                else:
                    # Если это не команда, просто показать выбор тарифа
                    handle_start(user_id, '/start')
            
            elif 'callback_query' in update:
                callback_query = update['callback_query']
                user_id = callback_query['from']['id']
                callback_data = callback_query['data']
                
                if callback_data == 'show_tariff_photo_legs':
                    handle_tariff_selection(user_id, 'show_tariff_photo_legs')
                elif callback_data == 'show_tariff_juicy_altushki':
                    handle_tariff_selection(user_id, 'show_tariff_juicy_altushki')
                elif callback_data == 'show_tariff_mini_sampler':
                    handle_tariff_selection(user_id, 'show_tariff_mini_sampler')
                elif callback_data.startswith('payment_'):
                    handle_payment_option(user_id, callback_data)
                elif callback_data == 'back_to_tariffs':
                    handle_back_to_tariffs(user_id)
                
                # Отвечаем на callback
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True}).encode())
                return
            
            elif 'pre_checkout_query' in update:
                pre_checkout_query = update['pre_checkout_query']
                answer_pre_checkout_query(pre_checkout_query['id'])
            
            elif 'message' in update and 'successful_payment' in update['message']:
                user_id = update['message']['from']['id']
                handle_successful_payment(user_id)
            
            # Отвечаем на запрос
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True}).encode())
            
        except Exception as e:
            logging.error(f"Ошибка при обработке обновления: {e}")
            self.send_response(500)
            self.end_headers()

    def do_GET(self):
        # Простой эндпоинт для проверки работоспособности
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Telegram Bot is running!")

def set_webhook():
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_URL', 'your-app-name.onrender.com')}/webhook"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    data = {'url': webhook_url}
    
    response = requests.post(url, data=data)
    return response.json()

def run_server():
    init_db()
    set_webhook()

    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), TelegramWebhookHandler)
    logging.info(f"Starting server on port {port}")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
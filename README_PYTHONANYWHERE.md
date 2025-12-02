# Установка и запуск бота на PythonAnywhere

## Подготовка

1. Зарегистрируйтесь на [pythonanywhere.com](https://www.pythonanywhere.com) (если у вас еще нет аккаунта)
2. После регистрации зайдите в панель управления (Dashboard)

## Загрузка файлов

1. В панели управления перейдите в раздел **Files** (Файлы)
2. Создайте новую папку, например, `mysite`
3. Загрузите в эту папку следующие файлы:
   - `crypto_subscription_bot.py`
   - `config.py`
   - `wsgi.py`
   - `launcher.py`
   - `requirements.txt`

## Установка зависимостей

1. Перейдите в раздел **Consoles** (Консоли) и запустите Bash-консоль
2. Выполните команду для установки зависимостей:
   ```bash
   pip3.12 install -r mysite/requirements.txt
   ```

## Настройка вебхука

1. В той же консоли запустите Python:
   ```bash
   python3.12
   ```
   
2. В Python-консоли выполните:
   ```python
   from aiogram import Bot
   from config import BOT_TOKEN
   
   bot = Bot(token=BOT_TOKEN)
   
   # Установите вебхук (замените username на ваш username на PythonAnywhere)
   webhook_url = 'https://your-username.pythonanywhere.com/webhook'
   await bot.set_webhook(webhook_url)
   
   # Проверьте, что вебхук установлен
   webhook_info = await bot.get_webhook_info()
   print(webhook_info.url)
   ```

3. Выйдите из Python-консоли:
   ```python
   exit()
   ```

## Настройка переменных окружения

1. В панели управления перейдите в раздел **Files** (Файлы)
2. Найдите файл `.bashrc` в вашей домашней директории (если его нет - создайте)
3. Добавьте в этот файл переменные окружения:
   ```bash
   export BOT_TOKEN="ваш_токен_бота_из_BotFather"
   export CHANNEL_ID="id_вашего_канала"
   export ADMIN_USER_ID="ваш_user_id_в_телеграм"
   export SUBSCRIPTION_NAME="Название_вашей_подписки"
   export SUBSCRIPTION_DAYS="30"
   export SUBSCRIPTION_PRICE="99"
   ```

## Настройка веб-приложения

1. Перейдите в раздел **Web** (Веб)
2. Нажмите "Add a new web app"
3. Выберите "Manual configuration" (ручная настройка)
4. Выберите версию Python (3.12)
5. Когда появится диалог о настройке приложения, замените содержимое на:
   ```python
   import sys
   import os
   
   # Добавляем путь к нашему приложению
   path = '/home/ваш_username/mysite'
   if path not in sys.path:
       sys.path.append(path)
   
   # Загружаем переменные окружения
   from config import BOT_TOKEN, CHANNEL_ID, ADMIN_USER_ID
   os.environ['BOT_TOKEN'] = BOT_TOKEN
   os.environ['CHANNEL_ID'] = CHANNEL_ID
   os.environ['ADMIN_USER_ID'] = str(ADMIN_USER_ID)
   
   # Импортируем наше приложение
   from wsgi import application
   ```

6. В том же разделе **Web**, в настройках вашего веб-приложения:
   - Убедитесь, что путь к домашней директории указывает на `/home/ваш_username/mysite`
   - Перезапустите приложение с помощью кнопки "Reload"

## Альтернативный способ запуска через задачи (Tasks)

Если вебхук не работает, можно запустить бота в режиме long polling через раздел **Tasks**:

1. Перейдите в раздел **Tasks** (Задачи)
2. Добавьте новую задачу с командой:
   ```bash
   cd /home/ваш_username/mysite && python3.12 crypto_subscription_bot.py
   ```
3. Установите частоту выполнения "Never (run by cron)" и время выполнения

## Проверка работы бота

1. Отправьте боту команду `/start` в Telegram
2. Убедитесь, что все функции работают корректно
3. Проверьте, что база данных создается и обновляется

## Устранение неполадок

- Если вы получаете ошибки с доступом к файлам, убедитесь, что пути к базе данных и другим файлам указаны корректно
- Если бот не отвечает, проверьте, установлен ли вебхук правильно и работают ли переменные окружения
- В случае проблем с оплатой или отправкой сообщений, проверьте, что токен бота указан правильно
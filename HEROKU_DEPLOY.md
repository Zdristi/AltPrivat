# Деплой бота на Heroku

## Подготовка

1. Зарегистрируйтесь на [Heroku](https://www.heroku.com/)
2. Установите [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

## Настройка приложения

1. Откройте терминал или командную строку
2. Авторизуйтесь в Heroku:
   ```bash
   heroku login
   ```

3. Создайте новый проект:
   ```bash
   heroku create your-app-name
   ```
   (замените your-app-name на уникальное имя для вашего приложения)

## Настройка переменных окружения

Установите переменные окружения:

```bash
heroku config:set BOT_TOKEN="ваш_токен_бота"
heroku config:set CHANNEL_ID="id_вашего_канала"
heroku config:set ADMIN_USER_ID="ваш_user_id"
heroku config:set SUBSCRIPTION_NAME="Название_подписки"
heroku config:set SUBSCRIPTION_DAYS=30
heroku config:set SUBSCRIPTION_PRICE=99
```

## Деплой

1. Добавьте все файлы:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Загрузите на Heroku:
   ```bash
   git push heroku main
   ```

3. Запустите приложение:
   ```bash
   heroku ps:scale web=1
   ```

## Проверка работы

1. Проверьте логи приложения:
   ```bash
   heroku logs --tail
   ```

2. Отправьте команду /start вашему боту в Telegram

## Важно

- Heroku предоставляет бесплатный тариф, но приложение может "засыпать" при бездействии
- Бесплатные dyno на Heroku ограничены по времени работы в месяц
- База данных SQLite может не сохранять данные при перезапуске приложения
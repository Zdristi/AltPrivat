# Список файлов для деплоя на Heroku

Необходимые файлы:
1. crypto_subscription_bot.py - основной файл бота
2. config.py - файл конфигурации
3. application.py - файл приложения для Heroku
4. requirements.txt - зависимости
5. Procfile - инструкции для Heroku
6. runtime.txt - версия Python
7. HEROKU_DEPLOY.md - инструкция по деплою

Дополнительно (по желанию):
- db_manager.py - для управления базой данных
- README.md - описание проекта

# Инструкция по деплою

1. Создайте аккаунт на Heroku: https://signup.heroku.com/
2. Установите Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
3. Откройте терминал и выполните:
   heroku login
4. Перейдите в папку с проектом
5. Создайте Heroku app:
   heroku create your-app-name
6. Установите переменные окружения:
   heroku config:set BOT_TOKEN=ваш_токен_бота
   heroku config:set CHANNEL_ID=ваш_id_канала
   heroku config:set ADMIN_USER_ID=ваш_user_id
   heroku config:set SUBSCRIPTION_NAME="Название подписки"
   heroku config:set SUBSCRIPTION_DAYS=30
   heroku config:set SUBSCRIPTION_PRICE=99
7. Залейте файлы:
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
8. Запустите приложение:
   heroku ps:scale web=1
# Файлы для деплоя на Railway

## Обязательные файлы:
1. crypto_subscription_bot.py - основной файл с логикой бота
2. config.py - файл конфигурации
3. requirements.txt - зависимости Python
4. Dockerfile - инструкции для сборки контейнера
5. .railway/variables.yml - переменные окружения для Railway

## Дополнительные файлы:
6. RAILWAY_DEPLOY.md - инструкция по деплою
7. application.py - альтернативный файл запуска
8. db_manager.py - управление базой данных
9. Procfile - для совместимости с другими платформами
10. runtime.txt - версия Python
11. wsgi.py - для совместимости с PythonAnywhere

## Как деплоить:

1. Зайдите на https://railway.app
2. Нажмите "New Project"
3. Выберите "Deploy from scratch"
4. Загрузите все файлы из этой папки
5. После деплоя настройте переменные окружения:
   - BOT_TOKEN
   - CHANNEL_ID
   - ADMIN_USER_ID
   - SUBSCRIPTION_NAME
   - SUBSCRIPTION_DAYS
   - SUBSCRIPTION_PRICE

## Переменные окружения:

- BOT_TOKEN: токен вашего Telegram бота (получите у @BotFather)
- CHANNEL_ID: ID канала, к которому даете доступ
- ADMIN_USER_ID: ваш ID пользователя в Telegram
- SUBSCRIPTION_NAME: название подписки (по умолчанию "Ножки Альтушек")
- SUBSCRIPTION_DAYS: количество дней подписки (по умолчанию 30)
- SUBSCRIPTION_PRICE: цена подписки (по умолчанию 99)
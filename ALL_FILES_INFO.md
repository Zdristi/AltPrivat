# Полный набор файлов для деплоя бота

## Список файлов:
1. crypto_subscription_bot.py - основной файл с логикой бота
2. config.py - файл конфигурации
3. requirements.txt - зависимости Python
4. Dockerfile - инструкции для сборки контейнера
5. .railway/variables.yml - переменные окружения для Railway
6. application.py - файл приложения
7. db_manager.py - управление базой данных
8. Procfile - для совместимости
9. runtime.txt - версия Python
10. wsgi.py - для PythonAnywhere
11. launcher.py - дополнительный файл запуска
12. HEROKU_DEPLOY.md - инструкция по деплою на Heroku
13. RAILWAY_DEPLOY.md - инструкция по деплою на Railway
14. RAILWAY_FILES.md - файл описания файлов Railway
15. README_PYTHONANYWHERE.md - инструкция по PythonAnywhere
16. DEPLOYMENT_INSTRUCTIONS.md - общая инструкция
17. GITHUB_REPO.md - инструкция по созданию репозитория
18. UPLOAD_LIST.md - список файлов для загрузки

## Платформы для деплоя:
- Railway (рекомендуется) - https://railway.app/
- Heroku - https://heroku.com/
- PythonAnywhere - https://pythonanywhere.com/

## Переменные окружения (обязательные):
- BOT_TOKEN: токен вашего Telegram бота
- CHANNEL_ID: ID канала, к которому даете доступ
- ADMIN_USER_ID: ваш ID пользователя в Telegram

## Дополнительные переменные:
- SUBSCRIPTION_NAME: название подписки
- SUBSCRIPTION_DAYS: количество дней подписки
- SUBSCRIPTION_PRICE: цена подписки

## Примечание:
Для Railway рекомендуется использовать GitHub репозиторий для деплоя.
Создайте публичный репозиторий на GitHub и закиньте туда все файлы,
затем подключите его к Railway.

Для других платформ можно загружать файлы напрямую.
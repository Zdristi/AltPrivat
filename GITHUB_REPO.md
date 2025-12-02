# Создание репозитория на GitHub и деплой на Railway

## Создание репозитория на GitHub

1. Зайдите на [GitHub](https://github.com/)
2. Нажмите на "+" в правом верхнем углу и выберите "New repository"
3. Введите имя репозитория (например, "crypto-subscription-bot")
4. Выберите "Public" (если хотите бесплатный репозиторий)
5. Не ставьте галочку "Initialize this repository with a README"
6. Не добавляйте .gitignore или license - мы добавим файлы позже
7. Нажмите "Create repository"

## Подготовка локального репозитория и загрузка файлов

1. Установите [Git](https://git-scm.com/downloads) на ваш компьютер
2. Откройте командную строку или Git Bash
3. Перейдите в папку с проектом:
   ```bash
   cd "C:\Users\Andrey\Desktop\AltPrivat"
   ```
4. Инициализируйте репозиторий:
   ```bash
   git init
   ```
5. Добавьте удалённый репозиторий (замените URL на ваш):
   ```bash
   git remote add origin https://github.com/ваш_логин/ваш_репозиторий.git
   ```
6. Добавьте все файлы:
   ```bash
   git add .
   ```
7. Сделайте первый коммит:
   ```bash
   git commit -m "Initial commit"
   ```
8. Загрузите файлы на GitHub:
   ```bash
   git branch -M main
   git push -u origin main
   ```

## Деплой на Railway

1. Зайдите на [Railway](https://railway.app/)
2. Нажмите "New Project"
3. Выберите "Deploy from GitHub repo"
4. Выберите ваш только что созданный репозиторий
5. После деплоя настройте переменные окружения:
   - BOT_TOKEN
   - CHANNEL_ID
   - ADMIN_USER_ID
   - SUBSCRIPTION_NAME
   - SUBSCRIPTION_DAYS
   - SUBSCRIPTION_PRICE

## Альтернативный способ через CLI Railway

1. Установите [Railway CLI](https://docs.railway.app/cli/installation)
2. Войдите в аккаунт:
   ```bash
   railway login
   ```
3. Инициализируйте проект:
   ```bash
   railway init
   ```
4. Установите переменные:
   ```bash
   railway var set BOT_TOKEN="ваш_токен"
   railway var set CHANNEL_ID="id_канала"
   railway var set ADMIN_USER_ID="ваш_user_id"
   railway var set SUBSCRIPTION_NAME="Название"
   railway var set SUBSCRIPTION_DAYS=30
   railway var set SUBSCRIPTION_PRICE=99
   ```
5. Деплой:
   ```bash
   railway up
   ```

Теперь ваш бот будет работать на Railway!
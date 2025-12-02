# Инструкция по завершению загрузки файлов в GitHub

Для завершения загрузки файлов в GitHub репозиторий нужно:

1. Сгенерировать персональный токен на GitHub:
   - Зайдите на https://github.com/settings/tokens
   - Нажмите "Generate new token" → "Tokens (classic)"
   - Установите название токена (например, "my-token")
   - Выберите разрешения: минимально нужен "repo"
   - Скопируйте сгенерированный токен

2. Затем выполните команду (замените "ваш_токен" на реальный токен):
   ```bash
   cd "C:\Users\Andrey\Desktop\AltPrivat" && git push -u origin main
   ```
   
   При запросе логина и пароля:
   - Введите ваш GitHub логин
   - Вместо пароля вставьте токен

Альтернативный способ - использовать GitHub Desktop:
1. Скачайте GitHub Desktop с https://desktop.github.com/
2. Войдите в свой аккаунт
3. Добавьте локальный репозиторий (File → Add Local Repository)
4. Выберите папку C:\Users\Andrey\Desktop\AltPrivat
5. Нажмите "Publish repository"
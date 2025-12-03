@echo off
echo Installing dependencies without pydantic...

REM Сначала устанавливаем aiogram без зависимостей
pip install aiogram==3.4.1 --no-deps

REM Затем устанавливаем остальные зависимости
pip install requests==2.31.0
pip install aiohttp==3.9.1
pip install gunicorn==21.2.0

REM Убедимся, что pydantic не установлен
pip uninstall pydantic -y

echo Dependencies installed successfully.
pause
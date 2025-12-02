#!/usr/bin/env python3
"""
Файл запуска для PythonAnywhere
"""
import os
import sys
from wsgi import application

if __name__ == "__main__":
    # Запускаем приложение
    from aiohttp import web
    web.run_app(
        application,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --only-binary=all --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "crypto_subscription_bot.py"]
#!/bin/bash

echo "🚀 Запуск SYMBIOS LAW BOT..."

# Активуємо Python environment, якщо потрібно
# source venv/bin/activate

# Експорт змінних середовища з .env
export $(grep -v '^#' .env | xargs)

# Запуск Webhook бота
python3 webhook.py

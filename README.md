
# SYMBIOS LAW BOT — Інтегрований диплой

Цей проект об'єднує всі ключові функції AI-юриста:
- GPT-відповіді на листи
- OCR обробка вкладень
- Контекстуальна памʼять
- Webhook Telegram-бот
- Підготовка до fine-tune

## 🔧 Вимоги
- Python 3.10+
- Установити залежності: `pip install -r requirements.txt`
- Заповнити файл `.env` зі змінними:
  - TELEGRAM_BOT_TOKEN=
  - OPENAI_API_KEY=
  - EXCHANGE_LOGIN=
  - EXCHANGE_PASSWORD=
  - WEBHOOK_URL=

## 🚀 Запуск
```bash
bash launch_all.sh
```

## 🧠 Структура
- `webhook.py` — головний скрипт запуску
- `ocr_reply.py` — модуль OCR
- `gpt_reply.py` — відповіді GPT
- `memory_manager.py` — контекстна памʼять
- `mail_parser.py` — обробка пошти
- `train/` — підготовка до fine-tune

---

Архітектор: Andriy Podybailo  
SYMBIOS AI Core // Маска Стратега

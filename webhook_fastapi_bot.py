import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from webhook_bot_gpt_memory import generate_gpt_with_memory, memory_lookup

# --- Конфіг ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID"))

# --- Логування ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Telegram App ---
telegram_app = ApplicationBuilder().token(TOKEN).build()

# --- FastAPI ---
fastapi_app = FastAPI()

# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text("✅ SYMBIOS LAW BOT активовано (FastAPI).")

# --- Основна логіка ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return

    text = update.message.text
    logger.info(f"[📩] Вхідне: {text}")

    context_memory = memory_lookup(text)
    reply = generate_gpt_with_memory(text, context_memory)

    await update.message.reply_text(f"🧠 GPT-відповідь:\n{reply}")

# --- Хендлери ---
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Webhook endpoint ---
@fastapi_app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}

# --- Запуск (використовуй gunicorn, не через if __name__...) ---
# gunicorn webhook_fastapi_bot:fastapi_app

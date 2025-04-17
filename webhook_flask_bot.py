import os
import logging
import threading
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from webhook_bot_gpt_memory import generate_gpt_with_memory, memory_lookup

# --- Конфіг ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID"))

# --- Логування ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Flask-додаток ---
flask_app = Flask(__name__)
telegram_app = ApplicationBuilder().token(TOKEN).build()

# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text("✅ SYMBIOS LAW BOT активовано (Flask).")

# --- Обробка повідомлень ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return

    text = update.message.text
    logger.info(f"[📩] Вхідне повідомлення: {text}")

    context_memory = memory_lookup(text)
    reply = generate_gpt_with_memory(text, context_memory)

    await update.message.reply_text(f"🧠 GPT-відповідь:\n{reply}")

# --- Хендлери ---
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Webhook endpoint ---
@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return "OK"

# --- Запуск ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    # Flask окремо в потоці
    def run_flask():
        flask_app.run(host="0.0.0.0", port=port)

    threading.Thread(target=run_flask).start()

    # Telegram запускається в asyncio event loop
    asyncio.run(telegram_app.initialize())
    asyncio.run(telegram_app.start())

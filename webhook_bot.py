import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from webhook_bot_gpt import generate_gpt_response
from webhook_bot_gpt_memory import memory_lookup
from email_extractor_exchange import fetch_emails
from ocr_parser import parse_attachments

# Завантаження середовищ
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text("✅ SYMBIOS LAW BOT запущено.")

# Основна логіка
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return

    user_input = update.message.text
    logger.info(f"📨 Повідомлення: {user_input}")

    # Пошук у памʼяті (опціонально)
    context_memory = memory_lookup(user_input)

    # Генерація GPT-відповіді
    gpt_reply = generate_gpt_response(user_input, context_memory)

    # Витяг пошти (опціонально, тільки як демонстрація)
    # emails = fetch_emails()
    # parsed_attachments = parse_attachments(emails)

    await update.message.reply_text(gpt_reply)

# Запуск Webhook
def main():
    logger.info("🚀 Старт SYMBIOS LAW BOT")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    PORT = int(os.environ.get("PORT", 8080))
    app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()

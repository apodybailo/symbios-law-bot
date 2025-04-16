import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from email_extractor_exchange import fetch_emails, connect_to_exchange

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("symbios-law-webhook")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "10000"))

# Команди
async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("⛔️ Доступ заборонено.")
        return
    await update.message.reply_text("📬 Запускаю обробку пошти...")
    try:
        acc = connect_to_exchange()
        fetch_emails(acc)
        await update.message.reply_text("✅ Обробка завершена.")
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка: {str(e)}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text("🔍 Надішліть /latest або документ.")

if __name__ == "__main__":
    logger.info("🚀 SYMBIOS AI Юрист: запуск через Webhook (PTB 22.0)")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("latest", latest))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        webhook_path="/"  # ⚠️ Ключовий момент
    )

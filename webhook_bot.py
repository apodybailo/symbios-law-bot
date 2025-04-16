import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from email_extractor_exchange import fetch_emails, connect_to_exchange

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("symbios-law-webhook")

# Змінні середовища
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Наприклад: https://symbios-law-bot.onrender.com/webhook
PORT = int(os.getenv("PORT", "10000"))

# Команда /latest — запуск аналізу пошти
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
        logger.exception("Помилка під час обробки пошти")

# Відповідь на текст
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text("🔍 Для аналізу надішліть /latest або документ.")

# Запуск Webhook
if __name__ == "__main__":
    logger.info("🚀 Запуск SYMBIOS AI Юрист через Webhook (PTB 22.x)")
    logger.info(f"➡️  URL Webhook: {WEBHOOK_URL}")
    logger.info(f"➡️  PORT: {PORT}")
    logger.info(f"✅ AUTHORIZED_USER_ID: {AUTHORIZED_USER_ID}")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("latest", latest))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )

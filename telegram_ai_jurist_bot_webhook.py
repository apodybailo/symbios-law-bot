import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from email_extractor_exchange import fetch_emails, connect_to_exchange

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_jurist_webhook")

# Команда запуску аналізу пошти
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

# Обробка текстових повідомлень
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text("🔍 Для аналізу надішліть /latest або документ.")

# Запуск додатку з webhook
if __name__ == "__main__":
    logger.info("🚀 Запуск бота SYMBIOS AI Юрист (Webhook)...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("latest", latest))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        webhook_url=f"{WEBHOOK_URL}"
    )

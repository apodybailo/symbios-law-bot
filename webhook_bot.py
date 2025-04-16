import os
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from email_extractor_exchange import fetch_emails, connect_to_exchange

# Налаштування логів
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("symbios-law-webhook")

# ENV
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "10000"))

# === Хендлери ===

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"[latest] From ID {update.effective_user.id}")
    if update.effective_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("⛔️ Доступ заборонено.")
        return
    await update.message.reply_text("📬 Запускаю обробку пошти...")
    try:
        acc = connect_to_exchange()
        fetch_emails(acc)
        await update.message.reply_text("✅ Обробка завершена.")
    except Exception as e:
        logger.exception("❌ Помилка при обробці")
        await update.message.reply_text(f"❌ Помилка: {str(e)}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"[echo] {update.message.text} | ID {update.effective_user.id}")
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text("🔍 Надішліть /latest або документ.")

# === Основний запуск ===

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("latest", latest))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Aiohttp сервер
    web_app = web.Application()
    web_app.router.add_post("/webhook", app.webhook_handler)

    logger.info("🚀 SYMBIOS AI Юрист: Webhook + aiohttp live")

    await app.initialize()
    await app.start()
    await web._run_app(web_app, port=PORT)
    await app.stop()
    await app.shutdown()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

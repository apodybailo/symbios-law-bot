
import os
import logging
from telegram import Update, Document
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from ocr_parser import extract_text_from_file
from openai import OpenAI

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("symbios-law-gpt")

client = OpenAI(api_key=OPENAI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text("🤖 SYMBIOS AI GPT Юрист готовий до роботи.")

async def analyze_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return

    document = update.message.document
    if not document:
        await update.message.reply_text("❌ Надішліть документ PDF або DOCX.")
        return

    file = await document.get_file()
    file_path = await file.download_to_drive()
    text = extract_text_from_file(file_path)

    await update.message.reply_text("🧠 Аналізуємо документ GPT...")
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Аналізуй юридичний документ:
{text}"}],
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(f"📄 GPT-відповідь:
{reply[:4000]}")
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка GPT: {e}")

if __name__ == "__main__":
    logger.info("🚀 Запуск SYMBIOS GPT Webhook...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, analyze_document))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )

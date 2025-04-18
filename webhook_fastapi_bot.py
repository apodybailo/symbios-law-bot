import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from webhook_bot_gpt_memory import generate_gpt_with_memory, memory_lookup
from email_extractor_exchange import connect_to_exchange, fetch_emails
from ocr_parser import extract_text_from_file  # реалізуй логіку в ocr_parser.py

# --- Конфіг ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", 0))

# --- FastAPI App ---
fastapi_app = FastAPI()

# --- Telegram Bot ---
telegram_app = Application.builder().token(TOKEN).build()

# --- Логування ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == AUTHORIZED_USER_ID:
        await update.message.reply_text("✅ SYMBIOS LAW BOT (FastAPI) активовано.")

# --- Обробка повідомлення ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return

    text = update.message.text
    logger.info(f"[📩] Вхідне повідомлення: {text}")

    context_memory = memory_lookup(text)
    reply = generate_gpt_with_memory(text, context_memory)

    await update.message.reply_text(f"🧠 GPT-відповідь:\n{reply}")

# --- Обробка команди /emails ---
async def fetch_emails_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return

    account = connect_to_exchange()
    messages = fetch_emails(account)
    await update.message.reply_text("📥 Отримано останні листи з Exchange. Перевір журнал.")

# --- Обробка документів (OCR) ---
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return

    file = await update.message.document.get_file()
    file_path = f"/tmp/{file.file_unique_id}_{file.file_path.split('/')[-1]}"
    await file.download_to_drive(file_path)

    extracted_text = extract_text_from_file(file_path)
    context_memory = memory_lookup(extracted_text)
    reply = generate_gpt_with_memory(extracted_text, context_memory)

    await update.message.reply_text(f"📄 Оброблено документ. 🧠 GPT-відповідь:\n{reply}")

# --- Додаємо хендлери ---
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("emails", fetch_emails_command))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
telegram_app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

# --- Webhook FastAPI endpoint ---
@fastapi_app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}

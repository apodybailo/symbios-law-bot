import os
import logging
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from webhook_bot_gpt_memory import generate_gpt_with_memory, memory_lookup
from email_extractor_exchange import connect_to_exchange, fetch_emails
from ocr_parser import extract_text_from_file

# --- Конфіг ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))

# --- Логування ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("symbios-law-fastapi")

# --- Telegram app ---
telegram_app = ApplicationBuilder().token(TOKEN).build()

# --- FastAPI app ---
fastapi_app = FastAPI()

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text("✅ SYMBIOS LAW BOT активовано (FastAPI).")

# --- Обробка повідомлень ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return

    text = update.message.text
    logger.info(f"[📩] Вхідне повідомлення: {text}")

    # Памʼять
    context_memory = memory_lookup(text)
    reply = generate_gpt_with_memory(text, context_memory)

    await update.message.reply_text(f"🧠 GPT-відповідь:\n{reply}")

# --- Обробка документа (OCR) ---
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return

    file = await update.message.document.get_file()
    file_path = f"/tmp/{file.file_id}_{update.message.document.file_name}"
    await file.download_to_drive(file_path)

    text = extract_text_from_file(file_path)
    reply = generate_gpt_with_memory(text, memory_lookup(text))

    await update.message.reply_text(f"📄 OCR + GPT-відповідь:\n{reply}")

# --- Команда /mail ---
async def handle_mail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return

    account = connect_to_exchange()
    messages = fetch_emails(account, max_items=3)

    await update.message.reply_text(f"📬 Останні листи:")
    for msg in messages:
        subject = msg.subject
        sender = msg.sender.email_address if msg.sender else "Невідомо"
        await update.message.reply_text(f"{subject}\nвід {sender}")

# --- Додаємо хендлери ---
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("mail", handle_mail))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
telegram_app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

# --- FastAPI Startup ---
@fastapi_app.on_event("startup")
async def on_startup():
    await telegram_app.initialize()
    logger.info("✅ Telegram App Initialized")

# --- Вебхук ---
@fastapi_app.post("/webhook")
async def process_webhook(request: Request):
    update_data = await request.json()
    update = Update.de_json(update_data, telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return {"status": "ok"}

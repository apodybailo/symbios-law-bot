import os
import logging
import tempfile
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)
from exchangelib import Credentials, Account, Configuration, DELEGATE
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import json

# === КОНФІГ ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", 0))
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EXCHANGE_SERVER = os.getenv("EXCHANGE_SERVER", "outlook.office365.com")
MEMORY_FILE = "memory.json"

# === ІНІЦІАЛІЗАЦІЯ ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("symbios-law-fastapi")
fastapi_app = FastAPI()
telegram_app: Application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# === МОДУЛЬ: ПАМʼЯТЬ ===
def memory_lookup(query):
    if not os.path.exists(MEMORY_FILE):
        return ""
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
    return "\n".join([entry["text"] for entry in data if query.lower() in entry["text"].lower()])

def remember(text, source="telegram"):
    entry = {"text": text, "source": source}
    data = []
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
    data.append(entry)
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

# === МОДУЛЬ: GPT ===
def generate_gpt_with_memory(prompt: str, context: str) -> str:
    return f"[GPT ✨] Контекст: {context}\nВідповідь на '{prompt}' — тут буде GPT-інтеграція."

# === МОДУЛЬ: ПОШТА ===
def connect_to_exchange():
    creds = Credentials(EMAIL, EMAIL_PASSWORD)
    config = Configuration(server=EXCHANGE_SERVER, credentials=creds)
    account = Account(primary_smtp_address=EMAIL, credentials=creds, autodiscover=False, config=config, access_type=DELEGATE)
    return account

def fetch_emails(account, max_items=5):
    inbox = account.inbox
    return list(inbox.all().order_by('-datetime_received')[:max_items])

# === МОДУЛЬ: OCR ===
def parse_attachments(emails, download_dir="attachments"):
    extracted_texts = []
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    for i, email in enumerate(emails):
        for attachment in getattr(email, "attachments", []):
            filename = attachment.name.lower()
            if filename.endswith(".pdf"):
                file_path = os.path.join(download_dir, f"{i}_{filename}")
                with open(file_path, "wb") as f:
                    f.write(attachment.content)
                with tempfile.TemporaryDirectory() as temp_dir:
                    images = convert_from_path(file_path, output_folder=temp_dir)
                    text_all_pages = [pytesseract.image_to_string(img, lang="uk+eng") for img in images]
                extracted_texts.append({"file": filename, "text": "\n".join(text_all_pages)})
    return extracted_texts

# === ОБРОБНИКИ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text("✅ SYMBIOS FASTAPI BOT активований.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    text = update.message.text
    context_memory = memory_lookup(text)
    reply = generate_gpt_with_memory(text, context_memory)
    remember(text)
    await update.message.reply_text(reply)

# === ХЕНДЛЕРИ ===
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === WEBHOOK ===
@fastapi_app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}


import os
import logging
import json
from datetime import datetime
from telegram import Update, Document
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from ocr_parser import extract_text_from_file
from openai import OpenAI

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "10000"))

client = OpenAI(api_key=OPENAI_API_KEY)
MEMORY_FILE = "memory.jsonl"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("symbios-law-gpt-memory")

def remember(text, reply, source="telegram", tags=None):
    entry = {
        "date": datetime.now().isoformat(),
        "user_id": AUTHORIZED_USER_ID,
        "type": "document",
        "source": source,
        "text": text,
        "gpt_reply": reply,
        "tags": tags or []
    }
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def load_memory(limit=5, tag_filter=None):
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, encoding="utf-8") as f:
        lines = f.readlines()
    entries = [json.loads(line) for line in lines]
    if tag_filter:
        entries = [e for e in entries if tag_filter in e.get("tags", [])]
    return entries[-limit:]

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return

    doc = update.message.document
    file = await doc.get_file()
    file_path = await file.download_to_drive()
    text = extract_text_from_file(file_path)

    memory_context = load_memory(limit=3)
    mem_text = "\n\n".join([f"- {m['text'][:300]}" for m in memory_context])

    prompt = f"Контекст попередніх документів:\n{mem_text}\n\nНовий документ:\n{text}"

    await update.message.reply_text("🧠 GPT аналізує документ з урахуванням памʼяті...")

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content
        remember(text, reply)
        await update.message.reply_text(f"📄 GPT-відповідь:
{reply[:4000]}")
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка GPT: {e}")

async def context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entries = load_memory()
    output = "\n---\n".join([f"{e['date']}\n{e['gpt_reply'][:300]}" for e in entries])
    await update.message.reply_text(f"🧠 Останні GPT-взаємодії:\n{output[:4000]}")

if __name__ == "__main__":
    logger.info("🚀 SYMBIOS GPT з памʼяттю — запуск")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("context", context))
    app.add_handler(MessageHandler(filters.Document.ALL, analyze))
    app.run_webhook(listen="0.0.0.0", port=PORT, webhook_url=WEBHOOK_URL)

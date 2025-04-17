import os
import logging
from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from webhook_bot_gpt_memory import generate_gpt_with_memory, memory_lookup

# --- Конфіг ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID"))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "symbios-core")

# --- Логування ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("symbios-law-fastapi")

# --- Telegram ---
telegram_app = ApplicationBuilder().token(TOKEN).build()

# --- FastAPI ---
fastapi_app = FastAPI()

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text("✅ SYMBIOS LAW BOT активовано (FastAPI).")

# === Обробка повідомлень ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return

    text = update.message.text
    logger.info(f"[📩] Вхідне повідомлення: {text}")

    context_memory = memory_lookup(text)
    reply = generate_gpt_with_memory(text, context_memory)

    await update.message.reply_text(f"🧠 GPT-відповідь:\n{reply}")

# === Telegram Handlers ===
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === /webhook ===
@fastapi_app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
    except Exception as e:
        logger.error(f"[❌] Webhook error: {e}")
        raise HTTPException(status_code=400, detail="Invalid webhook payload")
    return {"status": "ok"}

# === / ===
@fastapi_app.get("/")
async def root():
    return {"status": "alive", "service": "symbios-law-bot", "mode": "FastAPI"}

# === /healthz ===
@fastapi_app.get("/healthz")
async def healthz():
    return {"ok": True, "uptime": "✔️ running"}

# === /info ===
@fastapi_app.get("/info")
async def info():
    return {
        "authorized_user_id": AUTHORIZED_USER_ID,
        "webhook_secret": WEBHOOK_SECRET,
        "token_loaded": bool(TOKEN),
    }

# === /test_gpt ===
@fastapi_app.get("/test_gpt")
async def test_gpt():
    test_prompt = "Що таке AI в юридичній практиці?"
    context = memory_lookup(test_prompt)
    reply = generate_gpt_with_memory(test_prompt, context)
    return {"prompt": test_prompt, "response": reply}

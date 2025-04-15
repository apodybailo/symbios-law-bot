import os
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from openai import OpenAI
from dotenv import load_dotenv
import tempfile
import docx2txt
import fitz
from PIL import Image
import pytesseract

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "Ти — досвідчений корпоративний юрист. Генеруй офіційну юридичну відповідь українською мовою, "
    "аналізуючи зміст документа або запиту. Враховуй діловий стиль і практику відповіді на службові листи."
)

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".pdf":
            doc = fitz.open(file_path)
            return "\n".join([page.get_text() for page in doc])
        elif ext == ".docx":
            return docx2txt.process(file_path)
        elif ext in [".jpg", ".jpeg", ".png"]:
            image = Image.open(file_path)
            return pytesseract.image_to_string(image)
        else:
            return f"(Непідтримуваний формат: {ext})"
    except Exception as e:
        return f"❌ Помилка обробки файлу: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вітаю! Надішліть документ (PDF, DOCX, зображення), і я сформую юридичну відповідь.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        await file.download_to_drive(tmp.name)
        extracted_text = extract_text_from_file(tmp.name)

    await update.message.reply_text("📄 Документ отримано. Генерую відповідь...")

    try:
        completion = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Ось документ:\n\n{extracted_text}"}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        response = completion.choices[0].message.content
        await update.message.reply_text(f"🧠 Відповідь:\n\n{response}")
    except Exception as e:
        await update.message.reply_text(f"❌ GPT помилка: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.run_polling()

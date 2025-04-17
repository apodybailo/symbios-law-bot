import os
import json
import logging
from datetime import datetime
from openai import OpenAI

# 🔐 Ключ API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# 📁 Файл для збереження памʼяті
MEMORY_FILE = "memory.json"

# 🔊 Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("symbios-law-memory")

# 🧠 Збереження відповіді в памʼять
def remember(query: str, reply: str, source="telegram", tags=None):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "reply": reply,
        "source": source,
        "tags": tags or []
    }

    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump([], f)

    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)

    data.append(entry)

    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

# 🔎 Пошук в памʼяті (опційно)
def memory_lookup(query: str):
    if not os.path.exists(MEMORY_FILE):
        return ""

    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)

    # Пошук останнього схожого запиту (простий фільтр)
    for item in reversed(data):
        if query.lower() in item["query"].lower():
            return item["reply"]

    return ""

# 🤖 Генерація GPT-відповіді + запис у памʼять
def generate_gpt_with_memory(user_input: str, context: str = "") -> str:
    try:
        prompt = f"Аналізуй юридичний документ:\nКонтекст: {context}\nЗапит: {user_input}"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ти юридичний аналітик. Відповідай чітко й структуровано."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )

        reply = response.choices[0].message.content.strip()
        remember(user_input, reply)
        return reply

    except Exception as e:
        logger.error(f"❌ GPT error: {e}")
        return "GPT не відповів через помилку."

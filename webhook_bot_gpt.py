import os
import logging
from openai import OpenAI

# 🔐 Ключі з .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# 🔊 Логування
logger = logging.getLogger("symbios-law-gpt")

# 🧠 Основна функція генерації відповіді
def generate_gpt_response(user_input: str, context: str = "") -> str:
    try:
        prompt = f"Аналізуй юридичний документ:\nКонтекст: {context}\nЗапит: {user_input}"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ти юридичний асистент. Відповідай чітко та лаконічно."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )

        reply = response.choices[0].message.content.strip()
        return reply

    except Exception as e:
        logger.error(f"GPT Error: {str(e)}")
        return "❌ Помилка генерації GPT-відповіді."

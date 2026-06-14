import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv

# تحميل المتغيرات من .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# إعداد OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Prompt النظام (ASQ Brain)
SYSTEM_PROMPT = """
You are ASQ AI – Senior Business Analyst.

Transform any idea into a structured product document.

Always respond in this format:

📄 Project Summary
🎯 Problem Definition
🧩 Features (MVP)
👤 User Stories
🚀 MVP Scope
⚙️ System Flow
⚠️ Risks & Assumptions
💰 Business Model
"""

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ASQ AI جاهز!\nارسل فكرتك وسأحولها إلى مشروع كامل."
    )

# معالجة الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    if not user_input:
        await update.message.reply_text("اكتب فكرة أولاً.")
        return

    try:
        await update.message.chat.send_action("typing")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )

        result = response.choices[0].message.content

        # تقسيم الرسالة إذا كانت طويلة (Telegram limit)
        for i in range(0, len(result), 3500):
            await update.message.reply_text(result[i:i+3500])

    except Exception as e:
        logging.error(str(e))
        await update.message.reply_text("حدث خطأ أثناء المعالجة، حاول مرة أخرى.")

# تشغيل البوت
def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("ASQ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

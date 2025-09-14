# bot_apps.py

import nest_asyncio
nest_asyncio.apply()  # дозволяє використовувати asyncio всередині Render

import asyncio
from flask import Flask, jsonify
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging

# ---------- Налаштування логів ----------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---------- Flask App ----------
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return jsonify({"status": "ok", "message": "Bot server is running!"})

# ---------- Telegram Bot ----------
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"  # заміни на свій токен

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Бот запущено.")

async def help_command(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Це тестовий бот. Використовуй /start")

async def run_telegram_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    await app.run_polling()

# ---------- Основний запуск ----------
def main():
    # Запускаємо Flask у окремому таску
    loop = asyncio.get_event_loop()

    # Flask через Uvicorn
    import uvicorn
    flask_task = loop.create_task(
        uvicorn.run(
            "bot_apps:flask_app",
            host="0.0.0.0",
            port=8000,
            reload=False  # на Render не треба reload=True
        )
    )

    # Telegram Bot у асинхронному таску
    bot_task = loop.create_task(run_telegram_bot())

    # Запускаємо обидва таски
    loop.run_until_complete(asyncio.gather(flask_task, bot_task))

if __name__ == "__main__":
    main()

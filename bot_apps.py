# bot_apps.py

import nest_asyncio
nest_asyncio.apply()  # дозволяє використовувати asyncio всередині Render

import asyncio
from threading import Thread
import logging
from flask import Flask, jsonify
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---------- Логи ----------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---------- Flask App ----------
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return jsonify({"status": "ok", "message": "Bot server is running!"})

def run_flask():
    # daemon=True щоб не блокувати закриття програми
    flask_app.run(host="0.0.0.0", port=8000, debug=False)

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
async def main():
    # Flask у окремому потоці
    Thread(target=run_flask, daemon=True).start()

    # Telegram бот
    await run_telegram_bot()

if __name__ == "__main__":
    asyncio.run(main())

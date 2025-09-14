# bot_apps.py

import nest_asyncio
nest_asyncio.apply()  # дозволяє використовувати asyncio всередині Render

import asyncio
import logging
from flask import Flask, jsonify
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import uvicorn
from asgiref.wsgi import WsgiToAsgi

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
    # Flask через ASGI
    flask_asgi_app = WsgiToAsgi(flask_app)
    flask_task = asyncio.create_task(
        uvicorn.run(
            flask_asgi_app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    )

    # Telegram бот
    bot_task = asyncio.create_task(run_telegram_bot())

    # Обидва таски одночасно
    await asyncio.gather(flask_task, bot_task)

if __name__ == "__main__":
    asyncio.run(main())

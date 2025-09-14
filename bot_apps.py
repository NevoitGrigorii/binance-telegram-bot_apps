import os
import logging
import asyncio
import uvicorn
from flask import Flask
from asgiref.wsgi import WsgiToAsgi
from telegram import Update, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Налаштування ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEB_APP_URL = os.environ.get("WEB_APP_URL")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Telegram бот ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    button = KeyboardButton("📈 Відкрити інтерактивний графік", web_app=WebAppInfo(url=WEB_APP_URL))
    keyboard = [[button]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привіт! Натисніть кнопку нижче, щоб відкрити інтерактивний графік криптовалют.",
        reply_markup=reply_markup
    )

if not TELEGRAM_TOKEN or not WEB_APP_URL:
    raise ValueError("TELEGRAM_TOKEN та WEB_APP_URL мають бути встановлені!")

ptb_app = Application.builder().token(TELEGRAM_TOKEN).build()
ptb_app.add_handler(CommandHandler("start", start))

# --- Flask (для фронтенду) ---
_flask_app = Flask(__name__, static_folder="frontend", static_url_path="")

@_flask_app.route("/")
def index():
    return _flask_app.send_static_file("index.html")

flask_app = WsgiToAsgi(_flask_app)

# --- Головна функція ---
async def main():
    port = int(os.environ.get("PORT", 8080))

    # запускаємо Uvicorn у бекграунді
    config = uvicorn.Config(app=flask_app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())

    # запускаємо Telegram-бота (асинхронно)
    await ptb_app.run_polling(close_loop=False)

    # якщо бот зупиниться — глушимо сервер
    server.should_exit = True
    await server_task

if __name__ == "__main__":
    asyncio.run(main())

import os
import logging
import asyncio
from flask import Flask
from telegram import Update, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes
import uvicorn

# --- Налаштування ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEB_APP_URL = os.environ.get("WEB_APP_URL")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- Функції Telegram-бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    button = KeyboardButton("📈 Відкрити інтерактивний графік", web_app=WebAppInfo(url=WEB_APP_URL))
    keyboard = [[button]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привіт! Натисніть кнопку нижче, щоб відкрити інтерактивний графік криптовалют.",
        reply_markup=reply_markup
    )


# --- Налаштування Telegram Application ---
if not TELEGRAM_TOKEN or not WEB_APP_URL:
    raise ValueError("TELEGRAM_TOKEN та WEB_APP_URL мають бути встановлені!")

ptb_app = Application.builder().token(TELEGRAM_TOKEN).build()
ptb_app.add_handler(CommandHandler("start", start))

# --- Flask частина для віддачі фронтенду ---
flask_app = Flask(__name__, static_folder='frontend', static_url_path='')


@flask_app.route('/')
def index():
    return flask_app.send_static_file('index.html')


# --- Головна функція для запуску всього разом ---
async def main():
    """Запускає веб-сервер Uvicorn та Telegram-бота разом."""
    port = int(os.environ.get('PORT', 8080))

    # Створюємо та налаштовуємо Uvicorn-сервер
    config = uvicorn.Config(
        "__main__:flask_app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)

    # Запускаємо PTB Application та Uvicorn-сервер паралельно
    await ptb_app.initialize()
    await ptb_app.start()
    await ptb_app.updater.start_polling()
    await server.serve()
    await ptb_app.updater.stop()
    await ptb_app.stop()


if __name__ == "__main__":
    # Запускаємо головну async-функцію
    asyncio.run(main())
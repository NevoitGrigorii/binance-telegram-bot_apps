import os
import logging
from flask import Flask
from telegram import Update, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes
from threading import Thread

# --- Налаштування ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEB_APP_URL = os.environ.get("WEB_APP_URL")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- Функції Telegram-бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Надсилає кнопку для запуску Web App."""
    button = KeyboardButton(
        "📈 Відкрити інтерактивний графік",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    keyboard = [[button]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привіт! Натисніть кнопку нижче, щоб відкрити інтерактивний графік криптовалют.",
        reply_markup=reply_markup
    )

def run_bot():
    """Запускає polling-режим бота."""
    if not TELEGRAM_TOKEN or not WEB_APP_URL:
        logger.error("TELEGRAM_TOKEN та WEB_APP_URL мають бути встановлені!")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    logger.info("Бот запускається в режимі polling...")
    application.run_polling()


# --- Flask частина для віддачі фронтенду ---
app = Flask(__name__, static_folder='frontend', static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

# --- ЗАПУСК БОТА ПРИ ІМПОРТІ ФАЙЛУ ---
# Цей код виконається, коли Gunicorn завантажить файл,п і запустить бота у фоновому потоці.
logger.info("Запускаємо потік для Telegram-бота...")
bot_thread = Thread(target=run_bot)
bot_thread.start()

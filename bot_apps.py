import os
import logging
from flask import Flask
from telegram import Update, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Налаштування ---
# Токен і URL беремо зі змінних середовища на сервері
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEB_APP_URL = os.environ.get("WEB_APP_URL")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Flask частина для віддачі нашого міні-сайту ---
# `static_folder` вказує, що файли (index.html, etc.) лежать у папці 'frontend'
app = Flask(__name__, static_folder='frontend', static_url_path='')


# --- Telegram частина ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Надсилає кнопку для запуску Web App."""

    # Правильно створюємо об'єкт кнопки, як того вимагає бібліотека
    button = KeyboardButton(
        "📈 Відкрити інтерактивний графік",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )

    # Створюємо клавіатуру з одного ряду, що містить нашу кнопку
    keyboard = [[button]]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)Я ---

    await update.message.reply_text(
        "Привіт! Натисніть кнопку нижче, щоб відкрити інтерактивний графік криптовалют.",
        reply_markup=reply_markup
    )


def main() -> None:
    """Основна функція запуску."""
    if not TELEGRAM_TOKEN or not WEB_APP_URL:
        logger.error("TELEGRAM_TOKEN та WEB_APP_URL мають бути встановлені як змінні середовища!")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    logger.info("Бот запускається...")
    application.run_polling()


if __name__ == "__main__":
    main()
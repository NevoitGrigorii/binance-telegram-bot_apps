import os
import logging
from flask import Flask
from telegram import Update, WebAppInfo, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Налаштування ---
# Токен будемо брати зі змінних середовища на сервері
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
# URL нашого сервісу на Render (додамо його пізніше)
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
    # Створюємо кнопку, яка відкриє наш міні-сайт
    keyboard = [
        [{"text": "📈 Відкрити інтерактивний графік", "web_app": WebAppInfo(url=WEB_APP_URL)}]
    ]
    # Створюємо клавіатуру
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

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
    # Цей блок не буде виконуватися на Render, але потрібен для локальних тестів.
    # На Render ми будемо запускати Gunicorn, який керуватиме Flask `app`.
    main()
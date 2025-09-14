import os
import logging
import nest_asyncio
import asyncio

from flask import Flask
from asgiref.wsgi import WsgiToAsgi  # Для запуску Flask через ASGI
from telegram import Update, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Налаштування ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEB_APP_URL = os.environ.get("WEB_APP_URL")
PORT = int(os.environ.get("PORT", 8080))

if not TELEGRAM_TOKEN or not WEB_APP_URL:
    raise ValueError("TELEGRAM_TOKEN та WEB_APP_URL мають бути встановлені!")

# --- Логи ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Функції Telegram-бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

# --- Налаштування Telegram Application ---
ptb_app = Application.builder().token(TELEGRAM_TOKEN).build()
ptb_app.add_handler(CommandHandler("start", start))

# --- Flask частина для фронтенду ---
_flask_app = Flask(__name__, static_folder='frontend', static_url_path='')


@_flask_app.route('/')
def index():
    return _flask_app.send_static_file('index.html')


# Wrap Flask у ASGI
flask_app = WsgiToAsgi(_flask_app)

# --- Головна функція для запуску ---
def main():
    # Дозволяємо повторне використання event loop (Render/Production середовище)
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()

    import uvicorn

    # --- Запуск Flask серверу як таск ---
    flask_task = loop.create_task(
        uvicorn.run(
            "bot_apps:flask_app",
            host="0.0.0.0",
            port=PORT,
            log_level="info",
            loop=loop,
        )
    )

    # --- Запуск Telegram бота ---
    bot_task = loop.create_task(ptb_app.run_polling(close_loop=False))

    # --- Чекаємо завершення обох тасків ---
    loop.run_until_complete(asyncio.gather(flask_task, bot_task))


if __name__ == "__main__":
    main()

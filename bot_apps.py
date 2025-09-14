from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"  # заміни на свій токен

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Бот запущено.")

async def help_command(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Це тестовий бот. Використовуй /start")

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

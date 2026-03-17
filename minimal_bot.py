#!/usr/bin/env python3
"""
Мінімальний тестовий бот - тільки echo
Без будь-яких складностей, щоб перевірити чи працює Telegram API
"""

import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Завантажуємо конфіг
load_dotenv('/home/sashok/.openclaw/workspace/insilver-v2/.env')
TOKEN = os.getenv("TELEGRAM_TOKEN")

print(f"🚀 Запускаю мінімальний бот з токеном: {TOKEN[:20]}...")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text("✅ Мінімальний бот працює!")
    print(f"📨 /start від {update.effective_user.first_name}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo всіх повідомлень"""
    text = update.message.text
    await update.message.reply_text(f"🔄 Echo: {text}")
    print(f"📨 Повідомлення від {update.effective_user.first_name}: {text}")

def main():
    """Запуск бота"""
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print("🚀 Мінімальний бот запущений...")
    app.run_polling()

if __name__ == "__main__":
    main()
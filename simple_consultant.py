#!/usr/bin/env python3
"""
Простий консультант InSilver без складностей
Тільки базові функції для розробки
"""

import os
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Завантажуємо конфіг
load_dotenv('/home/sashok/.openclaw/workspace/insilver-v2/.env')
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "189793675").split(",")]

print(f"🚀 Простий консультант з токеном: {TOKEN[:20]}...")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text(
        "🔧 Простий консультант InSilver активний!\n"
        "Я можу:\n"
        "• Відповідати на повідомлення\n"
        "• /admin - режим навчання\n"
        "• /kb - показати базу знань"
    )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Режим адміна для навчання"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Доступ заборонено")
        return
    
    await update.message.reply_text(
        "👨‍💼 АДМІН РЕЖИМ АКТИВНИЙ\n"
        "Напишіть факт для запам'ятовування:\n"
        "Приклад: Якірне плетіння мінімальна маса 35-40г"
    )

async def kb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показати базу знань"""
    try:
        with open('/home/sashok/.openclaw/workspace/insilver-v2/data/knowledge.json', 'r') as f:
            kb = json.load(f)
        
        facts = kb.get('learned', [])
        if not facts:
            await update.message.reply_text("📭 База знань порожня")
            return
        
        text = "📚 БАЗА ЗНАНЬ:\n\n"
        for i, entry in enumerate(facts[-10:], 1):  # Останні 10
            fact = entry.get('fact', entry.get('text', 'Невідомий факт'))
            text += f"{i}. {fact}\n"
        
        await update.message.reply_text(text)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка читання БЗ: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка повідомлень"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Якщо адмін - зберігаємо як факт
    if user_id in ADMIN_IDS and len(text) > 10:
        try:
            # Завантажуємо базу знань
            kb_file = '/home/sashok/.openclaw/workspace/insilver-v2/data/knowledge.json'
            try:
                with open(kb_file, 'r') as f:
                    kb = json.load(f)
            except:
                kb = {"learned": []}
            
            # Додаємо факт
            from datetime import datetime
            new_fact = {
                "fact": text,
                "category": "manual",
                "date": datetime.now().strftime("%d.%m.%Y %H:%M")
            }
            kb["learned"].append(new_fact)
            
            # Зберігаємо
            with open(kb_file, 'w') as f:
                json.dump(kb, f, ensure_ascii=False, indent=2)
            
            await update.message.reply_text(f"✅ Запам'ятав: {text}")
            return
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка збереження: {e}")
            return
    
    # Звичайна відповідь
    await update.message.reply_text(
        f"🔧 Простий консультант отримав: {text}\n"
        f"👤 Від: {update.effective_user.first_name}\n"
        "💡 Для навчання використовуйте /admin"
    )

def main():
    """Запуск бота"""
    if not TOKEN:
        print("❌ TELEGRAM_TOKEN не знайдено!")
        return
        
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("kb", kb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Простий консультант запущений...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
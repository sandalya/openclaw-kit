#!/usr/bin/env python3
"""
Telegram Hook для автоматичного логування
Інтегрується з OpenClaw message tool
"""

import sys
import os
sys.path.append('/home/sashok/.openclaw/workspace')

from telegram_logger import log_incoming, log_outgoing

def log_kit_message(text):
    """Логування повідомлення від Кіта"""
    log_outgoing("kit", text, {"tool": "message", "target": "telegram"})
    
def log_sashok_message(text):
    """Логування повідомлення від Сашка"""
    log_incoming("sashok", text, {"source": "telegram"})

# Wrapper функція для message tool
def logged_telegram_send(message_text, **kwargs):
    """
    Обгортка для відправки повідомлень з логуванням
    Використовується замість прямого message tool
    """
    # Логуємо перед відправкою
    log_kit_message(message_text)
    
    # Тут буде виклик справжнього message tool
    # (в OpenClaw environment це буде автоматично)
    print(f"SENDING TO TELEGRAM: {message_text}")
    
    return {"status": "logged_and_sent", "text": message_text}

if __name__ == "__main__":
    # Демо
    log_sashok_message("а ти можеш писати логи для тг?")
    logged_telegram_send("Відмінна ідея! Створюю систему логування...")
    
    # Показати результат
    from telegram_logger import analyze_conversation
    print("\n=== АНАЛІЗ ПЕРЕПИСКИ ===")
    print(analyze_conversation())
#!/usr/bin/env python3
"""
Telegram Conversation Logger
Логує нашу переписку для подальшого аналізу
"""

import json
from datetime import datetime
import os

LOG_FILE = "/home/sashok/.openclaw/workspace/telegram_conversation.log"

def log_message(direction, user, text, metadata=None):
    """
    Логування повідомлення
    direction: 'IN' або 'OUT'
    user: 'sashok' або 'kit'
    text: текст повідомлення
    metadata: додаткова інформація
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = {
        "timestamp": timestamp,
        "direction": direction,
        "user": user,
        "text": text.strip(),
        "metadata": metadata or {}
    }
    
    # Записуємо в readable форматі
    log_line = f"[{timestamp}] {direction}({user}): {text.strip()}"
    
    # Додаємо до файлу
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    
    # Також JSON для парсингу
    json_file = LOG_FILE.replace(".log", ".json")
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    
    data.append(log_entry)
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def log_incoming(user, text, metadata=None):
    """Логування вхідного повідомлення"""
    log_message("IN", user, text, metadata)

def log_outgoing(user, text, metadata=None):
    """Логування вихідного повідомлення"""
    log_message("OUT", user, text, metadata)

def analyze_conversation(query=None, limit=50):
    """Аналіз переписки з можливістю фільтрації"""
    json_file = LOG_FILE.replace(".log", ".json")
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return "Логи переписки не знайдені"
    
    # Фільтрація якщо потрібно
    if query:
        query_lower = query.lower()
        filtered = [msg for msg in data if query_lower in msg["text"].lower()]
    else:
        filtered = data
    
    # Останні N повідомлень
    recent = filtered[-limit:] if limit else filtered
    
    result = []
    for msg in recent:
        result.append(f"[{msg['timestamp']}] {msg['direction']}({msg['user']}): {msg['text']}")
    
    return "\n".join(result)

if __name__ == "__main__":
    # Тест
    log_incoming("sashok", "а ти можеш писати логи для тг?")
    log_outgoing("kit", "Відмінна ідея! Так, я можу створити систему логування...")
    
    print("Логи створені. Аналіз:")
    print(analyze_conversation())
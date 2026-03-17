#!/usr/bin/env python3
"""
Аналіз Telegram переписки
Пошук по ключових словах, часовим проміжкам, тощо
"""

import json
import re
from datetime import datetime
from telegram_logger import analyze_conversation

def search_conversation(query, limit=None):
    """Пошук в переписці по ключовому слову"""
    json_file = "/home/sashok/.openclaw/workspace/telegram_conversation.json"
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return "Логи переписки не знайдені"
    
    query_lower = query.lower()
    matches = []
    
    for i, msg in enumerate(data):
        if query_lower in msg["text"].lower():
            # Додаємо контекст (попереднє та наступне повідомлення)
            context = []
            if i > 0:
                prev = data[i-1]
                context.append(f"  [{prev['timestamp']}] {prev['direction']}({prev['user']}): {prev['text']}")
            
            context.append(f"▶ [{msg['timestamp']}] {msg['direction']}({msg['user']}): {msg['text']}")
            
            if i < len(data) - 1:
                next_msg = data[i+1]
                context.append(f"  [{next_msg['timestamp']}] {next_msg['direction']}({next_msg['user']}): {next_msg['text']}")
            
            matches.append("\n".join(context))
    
    result = matches[:limit] if limit else matches
    return "\n\n" + "\n\n".join(result) if result else f"Не знайдено повідомлень з '{query}'"

def find_problems():
    """Знайти повідомлення пов'язані з проблемами"""
    problems = ["помилка", "баг", "не працює", "зникаю", "обіцяю", "problem", "error"]
    
    results = []
    for problem in problems:
        matches = search_conversation(problem, limit=3)
        if "Не знайдено" not in matches:
            results.append(f"=== ПРОБЛЕМИ З '{problem.upper()}' ===")
            results.append(matches)
    
    return "\n\n".join(results) if results else "Проблем не знайдено в логах"

def conversation_stats():
    """Статистика переписки"""
    json_file = "/home/sashok/.openclaw/workspace/telegram_conversation.json"
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return "Логи переписки не знайдені"
    
    total = len(data)
    sashok_msgs = len([m for m in data if m["user"] == "sashok"])
    kit_msgs = len([m for m in data if m["user"] == "kit"])
    
    if total == 0:
        return "Немає повідомлень в логах"
    
    first_msg = data[0]["timestamp"] if data else "—"
    last_msg = data[-1]["timestamp"] if data else "—"
    
    return f"""📊 СТАТИСТИКА ПЕРЕПИСКИ:

Загалом повідомлень: {total}
• Сашко: {sashok_msgs} ({sashok_msgs/total*100:.1f}%)
• Кіт: {kit_msgs} ({kit_msgs/total*100:.1f}%)

Перше повідомлення: {first_msg}
Останнє повідомлення: {last_msg}
"""

if __name__ == "__main__":
    print(conversation_stats())
    print("\n" + "="*50)
    print(find_problems())
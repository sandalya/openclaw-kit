# TOOLS_SUMMARY.md - Quick Reference


## 🤖 InSilver Консультант  
**Модель:** GPT-4o + GPT-4o-mini (escalation)  
**Статус:** Active через systemd

## ⚡ SSH Аліаси (Основні)
```bash
startbot     # Запустити консультант
stopbot      # Зупинити консультант  
reset-bot    # Перезапустити консультант
statusbot    # Статус сервісу
logs-bot     # Показати логи
fix-dupes    # Автофікс дублікатів (~11-й раз!)
```

## 🚨 Критичні Проблеми
**Дублікати bot.py** = конфлікт токенів = консультант зникає  
**Вирішено:** Відключено Telegram в OpenClaw → 1 токен = 1 процес

## 📁 Проект
**Основний:** `~/.openclaw/workspace/insilver-v2/`  
**База знань:** `data/knowledge.json`  
**Логи:** `bot.log`

## 💡 Швидкі команди
- **Статус системи:** `systemctl status insilver-bot`
- **Активні процеси:** `ps aux | grep bot.py`  
- **Логи консультанта:** `tail -20 bot.log`

---
*Повна версія: читай `TOOLS.md` коли потрібні деталі*
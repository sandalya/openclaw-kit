# HEARTBEAT.md

## 🔍 Системні перевірки (кожна 3-4 heartbeat)

### Перевірка дублікатів процесів
```bash
# Перевірити чи є дублікати bot.py (✅ ВИРІШЕНО 22:16 - відключив Telegram в OpenClaw)
bot_count=$(ps aux | grep -c "[b]ot.py")
if [ $bot_count -gt 1 ]; then
    echo "⚠️ ЗНАЙДЕНО $bot_count копій bot.py! Конфлікт токенів можливий"
    echo "📋 Перевірити чи не увімкнувся знову Telegram в OpenClaw"
    ps aux | grep "[b]ot.py"
else
    echo "✅ bot.py процесів: $bot_count (норма після кардинального рішення)"
fi
```

### Статус основних сервісів
```bash
# Перевірити InSilver бот
systemctl is-active insilver-bot --quiet || echo "❌ insilver-bot не працює"

# Перевірити OpenClaw
pgrep -f openclaw-gateway > /dev/null || echo "❌ openclaw-gateway не працює"
```

## 🎯 Коли алертити Сашка:
- Дублікати процесів (критично для Telegram)  
- Падіння основних сервісів  
- Помилки в логах bot.py

#!/bin/bash
# auto-fix-duplicates.sh
# ТИМЧАСОВЕ РІШЕННЯ до кардинальної зміни архітектури

echo "🔍 Перевіряю дублікати bot.py..."

# Підрахунок процесів
bot_count=$(ps aux | grep -c "[b]ot.py")

if [ $bot_count -gt 1 ]; then
    echo "🚨 ЗНАЙДЕНО $bot_count копій bot.py!"
    echo "📊 Це вже ~10-й раз з цією проблемою"
    echo ""
    
    # Показати процеси
    echo "📋 Поточні процеси:"
    ps aux | grep "[b]ot.py" --color=never
    echo ""
    
    # Зупинити systemd (якщо активний)
    if systemctl is-active insilver-bot --quiet; then
        echo "🛑 Зупиняю systemd сервіс..."
        sudo systemctl stop insilver-bot
        sleep 2
    fi
    
    # Убити всі bot.py процеси
    echo "💀 Убиваю всі bot.py процеси..."
    pkill -f "bot\.py"
    sleep 3
    
    # Запустити через systemd
    echo "🚀 Запускаю через systemd..."
    sudo systemctl start insilver-bot
    sleep 2
    
    # Перевірити результат
    if systemctl is-active insilver-bot --quiet; then
        echo "✅ Успішно! InSilver бот працює через systemd"
        echo "📊 Процесів bot.py зараз: $(ps aux | grep -c '[b]ot\.py')"
    else
        echo "❌ Помилка запуску через systemd"
        exit 1
    fi
    
    echo ""
    echo "⚠️  ПОПЕРЕДЖЕННЯ: Це тимчасове рішення!"
    echo "📖 Див. CRITICAL_PATTERNS.md для кардинального рішення"
    echo "🎯 Наступний раз = lock files/docker/guardian, не патчі!"
    
else
    echo "✅ Дублікатів немає ($bot_count процес)"
fi
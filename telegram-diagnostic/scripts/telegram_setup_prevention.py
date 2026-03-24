#!/usr/bin/env python3
"""
Налаштування профілактичних заходів для Telegram ботів
"""
import os
import subprocess
import sys

def setup_lock_protection():
    """Додати lock файли до systemd сервісів"""
    
    print("🔒 Налаштування lock protection для systemd...")
    
    # Шаблон для lock файлів
    lock_template = """
# Додати до [Service] секції:
ExecStartPre=/bin/sh -c 'if [ -f /tmp/telegram_bot.lock ]; then PID=$(cat /tmp/telegram_bot.lock); if kill -0 $PID 2>/dev/null; then echo "Bot already running" && exit 1; fi; fi'
ExecStartPost=/bin/sh -c 'echo $MAINPID > /tmp/telegram_bot.lock'
ExecStopPost=/bin/sh -c 'rm -f /tmp/telegram_bot.lock'
"""
    
    print("✅ Lock template готовий для додавання до systemd сервісів")
    print(lock_template)
    
    return lock_template

def create_health_monitor():
    """Створити health check скрипт"""
    
    monitor_script = """#!/bin/bash
# Health monitor для Telegram ботів
TOKENS_FILE="/home/sashok/.config/telegram_tokens.conf"

if [ ! -f "$TOKENS_FILE" ]; then
    echo "❌ Файл токенів не знайдено: $TOKENS_FILE"
    exit 1
fi

while read -r bot_name token; do
    [ -z "$token" ] && continue
    
    echo "🔍 Перевіряю $bot_name..."
    
    # Тест API доступності
    response=$(curl -s "https://api.telegram.org/bot$token/getUpdates?timeout=1&limit=1")
    
    if echo "$response" | grep -q "terminated by other"; then
        echo "🚨 КОНФЛІКТ у $bot_name! Токен: ${token:0:10}..."
        logger "TELEGRAM_CONFLICT: $bot_name"
        
        # Опціонально - надіслати Telegram повідомлення
        # curl -s "https://api.telegram.org/bot$ALERT_TOKEN/sendMessage" \\
        #      -d "chat_id=$ADMIN_CHAT_ID" \\
        #      -d "text=🚨 Telegram conflict detected: $bot_name"
    else
        echo "✅ $bot_name працює нормально"
    fi
    
done < "$TOKENS_FILE"
"""
    
    script_path = "/home/sashok/.local/bin/telegram_health_check.sh"
    
    try:
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        with open(script_path, 'w') as f:
            f.write(monitor_script)
        
        os.chmod(script_path, 0o755)
        print(f"✅ Health monitor створено: {script_path}")
        
        # Створити конфіг файл з токенами
        config_path = "/home/sashok/.config/telegram_tokens.conf"
        config_content = """# Формат: bot_name token
insilver-v3 8627781342:AAGRpzlKRGmABft7QkTIyzZjWHk4SFqw4wI
# insilver-v2 8527798600:AAEKuieIZd6GQhiEwzX2Gu3GzI3R04fDdec
"""
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            f.write(config_content)
            
        print(f"✅ Конфіг токенів створено: {config_path}")
        
        return script_path, config_path
        
    except Exception as e:
        print(f"❌ Помилка створення health monitor: {e}")
        return None, None

def setup_cron_monitoring():
    """Додати cron job для моніторингу"""
    
    print("⏰ Налаштування cron моніторингу...")
    
    cron_entry = "*/10 * * * * /home/sashok/.local/bin/telegram_health_check.sh >> /var/log/telegram_monitor.log 2>&1"
    
    print("Додайте до crontab:")
    print(f"  {cron_entry}")
    print("\nКоманда: crontab -e")
    
    return cron_entry

def create_emergency_script():
    """Створити emergency cleanup скрипт"""
    
    emergency_script = """#!/bin/bash
# Emergency Telegram cleanup
echo "🚨 EMERGENCY TELEGRAM CLEANUP"

# Зупинити всі telegram боти
systemctl --user stop 'telegram-*' 2>/dev/null
systemctl --user stop 'insilver-*' 2>/dev/null
sudo systemctl stop 'insilver-*' 2>/dev/null

# Kill всі Python процеси з 'bot' у назві
pkill -f "python.*bot"

# Очистити lock файли  
rm -f /tmp/telegram_bot.lock /tmp/insilver*.lock

echo "✅ Cleanup завершено. Перезапустіть потрібні сервіси."
"""
    
    script_path = "/home/sashok/.local/bin/telegram_emergency_cleanup.sh"
    
    try:
        with open(script_path, 'w') as f:
            f.write(emergency_script)
        
        os.chmod(script_path, 0o755)
        print(f"🚨 Emergency cleanup створено: {script_path}")
        
        return script_path
        
    except Exception as e:
        print(f"❌ Помилка створення emergency script: {e}")
        return None

def main():
    print("🛡️  TELEGRAM PROTECTION SETUP")
    print("=" * 50)
    
    # 1. Lock protection
    setup_lock_protection()
    
    # 2. Health monitoring
    script_path, config_path = create_health_monitor()
    
    # 3. Cron monitoring
    cron_entry = setup_cron_monitoring()
    
    # 4. Emergency cleanup
    emergency_path = create_emergency_script()
    
    print("\n🎯 ПІДСУМОК:")
    print("✅ Профілактичні заходи налаштовано")
    print("✅ Health monitor готовий до використання")
    print("✅ Emergency cleanup доступний")
    print("\n💡 НАСТУПНІ КРОКИ:")
    print("1. Додайте lock protection до systemd сервісів")
    print("2. Налаштуйте cron моніторинг")
    print("3. Тестуйте health check періодично")

if __name__ == "__main__":
    main()
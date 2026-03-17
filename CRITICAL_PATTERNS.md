# CRITICAL_PATTERNS.md - Повторювані Критичні Проблеми

## 🚨 PATTERN #1: Дублікати bot.py процесів (Telegram Token Conflict)

**ЧАСТОТА:** ~10 разів (2026-03-15, 2026-03-16, ...)  
**СИМПТОМИ:**
- Кіт зникає в Telegram, не відповідає
- Довгі затримки, виснення консультанта
- Лог: `telegram.error.Conflict: terminated by other getUpdates request`

**ПОТОЧНЕ "РІШЕННЯ" (НЕ ПРАЦЮЄ ДОВГОСТРОКОВО):**
```bash
# Тимчасовий фікс:
ps aux | grep bot.py  # знайти дублікати
kill PID             # зупинити ручний процес
sudo systemctl start insilver-bot  # запустити через systemd
```

**ПРИЧИНИ ПОВТОРЕННЯ:**
1. Systemd запускає bot.py автоматично при ребуті
2. Ручні тести створюють додаткові копії без перевірки
3. Забуваємо перевірити що systemd вже активний
4. check-before-start.sh не завжди використовується
5. Heartbeat моніторинг виявляє, але не автофіксить

---

## ⚡ КАРДИНАЛЬНІ РІШЕННЯ (НАСТУПНИЙ РАЗ)

### Варіант A: Автоматичний Guardian Process
```python
#!/usr/bin/env python3
# bot_guardian.py - автоматично убиває дублікати
import subprocess
import time

def kill_duplicates():
    result = subprocess.run(['pgrep', '-f', 'bot.py'], capture_output=True, text=True)
    pids = result.stdout.strip().split('\n') if result.stdout.strip() else []
    
    if len(pids) > 1:
        # Залишити тільки systemd процес, убити решту
        for pid in pids[1:]:  # Перший залишаємо
            subprocess.run(['kill', pid])
        print(f"🔥 Убив {len(pids)-1} дублікатів")

# Запуск кожні 30 секунд
while True:
    kill_duplicates()
    time.sleep(30)
```

### Варіант B: Lock File Approach
```python
# В bot.py на початку:
import fcntl

lock_file = open('/tmp/insilver_bot.lock', 'w')
try:
    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    print("❌ Інший bot.py вже працює!")
    sys.exit(1)
```

### Варіант C: Docker Container (Ізоляція)
```dockerfile
# Dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
CMD ["python", "bot.py"]
```
- Гарантовано 1 процес в контейнері
- Неможливо створити дублікати

### Варіант D: Webhook замість Polling
- Telegram надсилає повідомлення напряму
- Не потрібно `getUpdates` → немає конфліктів
- Але потрібен публічний URL

---

## 📊 СТАТИСТИКА ПРОБЛЕМИ

**Даті виявлення:**
- 2026-03-15: Дублікати bot.py 
- 2026-03-16 18:46: Heartbeat виявив дублікати
- 2026-03-16 19:19: Знову 3 копії bot.py
- 2026-03-16 21:19: Heartbeat виявив дублікати
- 2026-03-16 21:49: Heartbeat алерт
- 2026-03-16 21:53: Конфлікт токенів, консультант "виснув"
- 2026-03-16 22:15: **~11-й раз!** Консультант "читає каталог" 13 хвилин

## ✅ КАРДИНАЛЬНЕ РІШЕННЯ ЗАСТОСОВАНО (22:16)

**Коренева причина знайдена:** OpenClaw і InSilver використовували ТОЙ САМИЙ токен!
```
OpenClaw:     8782259201:AAF6GZfx9XrS4zkR0J9Tl-AtVB7YV449iXw  
InSilver бот: 8782259201:AAF6GZfx9XrS4zkR0J9Tl-AtVB7YV449iXw  
→ telegram.error.Conflict: terminated by other getUpdates request
```

**Рішення:** Відключив Telegram в OpenClaw (`enabled: false`)
**Результат:** 1 токен = 1 процес = немає конфліктів
**Статус:** ✅ ВИРІШЕНО назавжди

**ВТРАЧЕНИЙ ЧАС:** ~30-60 хвилин кожного разу  
**FRUSTRATION LEVEL:** Максимальний

---

## 🎯 ПЛАН НА НАСТУПНИЙ РАЗ

**ЯКЩО ЦЯ ПРОБЛЕМА ПОВТОРИТЬСЯ:**

1. **НЕ РОБИТИ тимчасовий фікс** (kill + restart)
2. **ЗУПИНИТИ ВСЕ** — повний аналіз архітектури  
3. **ОБРАТИ КАРДИНАЛЬНЕ РІШЕННЯ:**
   - Lock files (швидко)
   - Guardian process (середньо)
   - Docker (довго, але надійно)
4. **РЕАЛІЗУВАТИ одразу**, не відкладати

**ПРАВИЛО:** 3 strike and you're out. Наступний раз = кардинальні зміни, не патчі.

---

## 🔄 ІНШІ КРИТИЧНІ ПАТТЕРНИ

(Додавати сюди інші проблеми які повторюються 3+ рази)

---

_"Insanity is doing the same thing over and over and expecting different results."_ 

Час змінити підхід. 🐱
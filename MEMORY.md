# MEMORY.md - Довгострокова пам'ять Кіта

## InSilver v3 - Telegram Бот для Ювелірної Майстерні

**Статус:** 🔄 Активна розробка  
**Сервер:** Raspberry Pi 5  
**Версія:** v3 (міграція з v2)
**Власник майстерні:** Влад  
**Розробник:** Сашко

---

## 🏗️ АРХІТЕКТУРА v3

### Структура проекту:
```
insilver-v3/
├── main.py                    # Точка входу, Telegram інтеграція
├── core/                      # Основна бізнес-логіка
│   ├── config.py             # Конфігурація системи
│   ├── ai.py                 # AI інтеграція (OpenAI GPT-4)
│   ├── prompt.py             # AI промпти
│   ├── catalog.py            # Каталог виробів
│   ├── order_context.py      # Контекст замовлень
│   ├── order_config.py       # Налаштування замовлень
│   ├── conversation_logger.py # Логування діалогів
│   ├── backup_system.py      # Система резервного копіювання
│   ├── log_analyzer.py       # Аналізатор логів
│   ├── health.py             # Health моніторинг
│   ├── photo.py              # Обробка фото
│   └── lock.py               # Блокування процесів
├── bot/                      # Telegram bot handlers
│   ├── client.py            # Клієнтська частина (12KB)
│   ├── admin.py             # Адмін панель (88KB) - повний інтерфейс
│   └── order.py             # Обробка замовлень (16KB)
├── data/                    # Дані
│   ├── knowledge/           # База знань
│   │   ├── training.json   # 15 записів Q&A для консультанта
│   │   └── media/          # Медіа файли знань
│   ├── orders/             # Замовлення клієнтів
│   ├── photos/site/        # Фото з сайту
│   ├── silver.json         # Базові налаштування
│   └── site_catalog.json   # Каталог сайту (1.3MB)
├── logs/                   # Логи системи
│   ├── bot.log            # Основні логи бота
│   ├── conversations.log  # Діалоги з клієнтами
│   └── training_backups/  # Бекапи навчальних даних
└── scripts/               # Допоміжні скрипти
```

### Ключові модулі:

**🤖 AI Система:**
- `ai.py` - OpenAI GPT-4 інтеграція
- `prompt.py` - Промпти консультанта
- `training.json` - 15 записів навчальних даних з v2

**📦 Замовлення:**
- `order_context.py` - Стан і контекст замовлення
- `order.py` - Telegram handlers для замовлень
- `catalog.py` - Каталог виробів і цін

**🔧 Система:**
- `health.py` - Моніторинг Pi5
- `backup_system.py` - Автобекап даних
- `conversation_logger.py` - Логи клієнтів

---

## 📋 КОМАНДИ ЩОДЕННОГО ВИКОРИСТАННЯ

### Systemd команди:
```bash
# Статус і контроль InSilver
sudo systemctl status insilver-v3
sudo systemctl restart insilver-v3
sudo systemctl stop insilver-v3
sudo systemctl start insilver-v3

# Статус і контроль OpenClaw (мене)
sudo systemctl status openclaw
sudo systemctl restart openclaw
```

### Логи та дебаг:
```bash
# Логи InSilver бота
tail -f ~/.openclaw/workspace/insilver-v3/logs/bot.log
tail -20 ~/.openclaw/workspace/insilver-v3/logs/conversations.log

# Логи OpenClaw
journalctl -u openclaw -f --no-pager
openclaw logs --follow

# Процеси
ps aux | grep main.py | grep -v grep
ps aux | grep python3
```

### Git workflow:
```bash
cd ~/.openclaw/workspace/insilver-v3
git status && git log --oneline -5
git add -A && git commit -m "feat: опис змін"
git push

# Мої зміни (workspace)
cd ~/.openclaw/workspace  
git status && git add -A && git commit -m "ai: опис"
```

### Розробка:
```bash
# Структура проекту
tree -d ~/.openclaw/workspace/insilver-v3
find ~/.openclaw/workspace/insilver-v3 -name "*.py" -type f

# Здоров'я системи
python3 ~/.openclaw/workspace/health_monitor.py
free -m && df -h
```

---

## 🔥 ТИПОВІ ПРОБЛЕМИ ТА РІШЕННЯ

### 1. **Дублікати bot процесів (вирішено 2026-03-24)**
**Проблема:** Декілька копій main.py працюють одночасно → конфлікти токенів
**Рішення:** 
```bash
ps aux | grep main.py | grep -v grep  # перевірити
sudo systemctl restart insilver-v3    # перезапуск через systemd
```
**Профілактика:** Завжди перевіряти процеси перед ручним запуском

### 2. **Telegram API conflicts (вирішено)**
**Проблема:** InSilver і OpenClaw використовували однакові токени
**Рішення:** Роздільні токени в різних .env файлах:
- InSilver: `insilver-v3/.env` → `TELEGRAM_TOKEN=8627781342:...`
- OpenClaw: `workspace/.env` → `TELEGRAM_BOT_TOKEN=8627596455:...`

### 3. **Pi5 падіння під навантаженням (2026-03-24)**
**Проблема:** ОС падала при інтенсивній роботі бота
**Рішення:** Systemd обмеження ресурсів + health monitoring
**Моніторинг:** `health_monitor.py` кожні 15 хвилин

### 4. **OpenClaw витрати ($150/рік → оптимізація)**
**Рішення:** 
- contextPruning TTL: 5min → 2h
- heartbeat optimization  
- Cost-aware tool usage

### 5. **База знань v2→v3 міграція**
**Статус:** ✅ Завершено (27 записів → 15 оптимізованих)
**Файл:** `data/knowledge/training.json`
**Формат:** `{"title": "питання", "content": [{"text": "відповідь"}]}`

---

## 🎯 ПОТОЧНИЙ СТАН ПРОЕКТУ (2026-03-24)

### ✅ ЩО ПРАЦЮЄ СТАБІЛЬНО:
1. **Telegram Bot Integration**
   - InSilver консультант: стабільний 1h 39min uptime
   - OpenClaw розробник: dual-channel (web + telegram)
   - Роздільні токени, без конфліктів

2. **Навчальна База (15 записів)**
   - Міграція v2→v3 завершена
   - Q&A для ювелірних консультацій
   - Інтеграція в AI промпт працює

3. **Systemd Services**
   - `insilver-v3.service` - стабільний
   - `openclaw.service` - стабільний  
   - Автозапуск після reboot

4. **Git Workflow**
   - 4 команди: `гіт`, `гіткіт`, `фікс`, `чкп`
   - Backup система працює
   - Розділення репозиторіїв

### 🔄 В ПРОЦЕСІ:
1. **Health Monitoring**
   - `health_monitor.py` активний
   - Alerts в `health_alerts.log`
   - CPU/RAM/Disk контроль

2. **Cost Optimization** 
   - OpenClaw витрати знижені
   - Token-aware tool usage
   - Розумний чекпоінт workflow

### 🚀 ЗАПЛАНОВАНО:
1. **AI Промпт Покращення**
   - Інтеграція всіх 15 навчальних записів
   - Оптимізація відповідей консультанта

2. **Production Stability**
   - Stress-тести Pi5
   - Auto-restart механізми
   - Backup automation

---

## 💡 ІНСАЙТИ ТА NOTES

### Сашко Preferences:
- 🇺🇦 Тільки українська мова (критично)
- 💰 Мінімум токенів завжди пріоритет
- 📁 `.env` структура незмінна ("мені зручно")
- 🎯 Готові рішення > довгі обговорення

### Архітектурні рішення:
- **Single Pi5** - розробка + продакшн
- **JSON файли** замість БД (простота)
- **Systemd** для процесів (стабільність)  
- **Git-based** backup (надійність)

### Performance Notes:
- InSilver: ~10-20 повідомлень/день від клієнтів
- OpenClaw: ~100+ tool calls/день розробки
- Pi5 ресурси: критично моніторити RAM > 85%

---

*Останнє оновлення: 2026-03-24 22:20*  
*Git HEAD: 6fa6a56 - OpenClaw cost optimization*
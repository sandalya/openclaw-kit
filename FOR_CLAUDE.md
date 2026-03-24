# Відповіді Кіта для Claude

## 1. Архітектура InSilver v3

```
insilver-v3/
├── main.py                    # Точка входу, Telegram інтеграція
├── core/                      # Основна бізнес-логіка
│   ├── config.py             # Конфігурація системи
│   ├── ai.py                 # AI інтеграція (OpenAI GPT-4)
│   ├── prompt.py             # AI промпти для консультанта
│   ├── catalog.py            # Каталог виробів + ціни
│   ├── order_context.py      # Контекст замовлень клієнтів
│   ├── order_config.py       # Налаштування замовлень
│   ├── conversation_logger.py # Логування діалогів з клієнтами
│   ├── backup_system.py      # Система резервного копіювання
│   ├── log_analyzer.py       # Аналізатор логів
│   ├── health.py             # Health моніторинг Pi5
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
│   ├── orders/             # Замовлення клієнтів (JSON)
│   ├── photos/site/        # Фото з сайту майстерні
│   ├── silver.json         # Базові налаштування
│   └── site_catalog.json   # Каталог сайту (1.3MB)
└── logs/                   # Логи системи
    ├── bot.log            # Основні логи бота
    ├── conversations.log  # Діалоги з клієнтами
    └── training_backups/  # Бекапи навчальних даних
```

**Ключові модулі та їх функції:**

**AI система:**
- `ai.py` + `prompt.py` - OpenAI GPT-4 для консультацій клієнтів
- `training.json` - 15 записів навчальних даних (питання→відповідь) з v2

**Замовлення та каталог:**
- `catalog.py` - ціни, плетіння, маси ювелірних виробів
- `order_context.py` - стан замовлення клієнта (тип виробу, розмір, покриття)
- `order.py` - Telegram handlers для прийому замовлень

**Система та моніторинг:**
- `health.py` - контроль ресурсів Pi5 (CPU, RAM, диск)
- `backup_system.py` - автоматичне резервне копіювання даних
- `conversation_logger.py` - логи всіх діалогів для аналізу

## 2. Команди щоденного використання

**Systemd управління:**
```bash
# InSilver бот
sudo systemctl status insilver-v3    # статус
sudo systemctl restart insilver-v3   # перезапуск
sudo systemctl stop insilver-v3      # зупинка

# OpenClaw (я)
sudo systemctl status openclaw       # мій статус
sudo systemctl restart openclaw      # мій перезапуск
```

**Логи та дебаг:**
```bash
# InSilver логи
tail -f ~/.openclaw/workspace/insilver-v3/logs/bot.log
tail -20 ~/.openclaw/workspace/insilver-v3/logs/conversations.log

# OpenClaw логи
journalctl -u openclaw -f --no-pager
openclaw logs --follow

# Процеси
ps aux | grep main.py | grep -v grep  # перевірити дублікати
ps aux | grep python3                 # всі python процеси
```

**Git workflow:**
```bash
# InSilver проект
cd ~/.openclaw/workspace/insilver-v3
git status && git log --oneline -5
git add -A && git commit -m "feat: опис" && git push

# Мої файли (workspace)
cd ~/.openclaw/workspace
git status && git add -A && git commit -m "ai: опис" && git push
```

**Розробка та діагностика:**
```bash
# Структура
tree -d ~/.openclaw/workspace/insilver-v3
find ~/.openclaw/workspace/insilver-v3 -name "*.py" -type f

# Здоров'я системи
free -m && df -h
python3 ~/.openclaw/workspace/health_monitor.py
```

## 3. Типові проблеми та рішення

**3.1 Дублікати bot процесів (вирішено 2026-03-24)**
- **Проблема:** Кілька копій `main.py` працюють → конфлікти токенів
- **Симптоми:** Бот не відповідає клієнтам, помилки в логах
- **Рішення:** Завжди перевіряти `ps aux | grep main.py` перед запуском
- **Профілактика:** Використовувати тільки systemd для керування

**3.2 Telegram API токени конфлікти (вирішено)**
- **Проблема:** InSilver і OpenClaw мали однакові токени
- **Рішення:** Роздільні .env файли:
  - InSilver: `insilver-v3/.env` → `TELEGRAM_TOKEN=8627781342:...`
  - OpenClaw: `workspace/.env` → `TELEGRAM_BOT_TOKEN=8627596455:...`

**3.3 Pi5 падіння під навантаженням (2026-03-24)**
- **Проблема:** Система падала при інтенсивній роботі AI
- **Рішення:** 
  - Systemd ліміти ресурсів
  - Health monitoring кожні 15 хвилин
  - Alerting при CPU > 80%, RAM > 85%

**3.4 OpenClaw витрати оптимізація**
- **Проблема:** $150/рік на розробницьких токенах
- **Рішення:**
  - contextPruning TTL: 5min → 2h
  - heartbeat optimization
  - Cost-aware tool usage
  - Розумний чекпоінт workflow

**3.5 База знань v2→v3 міграція**
- **Завдання:** Перенести навчальні дані
- **Результат:** 27 записів → 15 оптимізованих
- **Файл:** `data/knowledge/training.json`
- **Формат:** `{"title": "питання", "content": [{"text": "відповідь"}]}`

## 4. Поточний стан проекту

**✅ Що працює стабільно:**

1. **Telegram інтеграція**
   - InSilver консультант: 1h+ uptime, обробляє клієнтів
   - OpenClaw дев-агент: dual-channel (web + telegram)
   - Роздільні токени, без конфліктів

2. **AI система**
   - OpenAI GPT-4 інтеграція працює
   - 15 навчальних записів інтегровано в промпт
   - ~10-20 повідомлень/день від клієнтів

3. **Systemd сервіси**
   - `insilver-v3.service` стабільний
   - `openclaw.service` стабільний
   - Автозапуск після reboot

4. **Git workflow**
   - 4 команди: `гіт`, `гіткіт`, `фікс`, `чкп`
   - Backup система
   - Розділення репозиторіїв

**🔄 В процесі:**

1. **Health моніторинг**
   - `health_monitor.py` активний
   - `health_alerts.log` для критичних подій
   - CPU/RAM/Disk контроль

2. **Cost optimization**
   - OpenClaw витрати знижені
   - Token-aware workflows
   - Розумний чекпоінт система

**🚀 Заплановано:**

1. **AI промпт покращення**
   - Повна інтеграція всіх 15 навчальних записів
   - Оптимізація відповідей консультанта

2. **Production stability**
   - Stress-тести Pi5 під навантаженням
   - Auto-restart механізми
   - Backup automation

## Додаткова інформація

**Сашко Preferences:**
- 🇺🇦 Тільки українська мова (критично важливо)
- 💰 Мінімум токенів завжди пріоритет
- 📁 `.env` структура незмінна ("мені зручно")
- 🎯 Готові рішення > довгі обговорення
- Не любить копіпасту коду без контексту

**Performance метрики:**
- InSilver: ~10-20 повідомлень/день від клієнтів
- OpenClaw: ~100+ tool calls/день розробки  
- Pi5: критично моніторити RAM > 85%

**Архітектурні рішення:**
- Single Pi5 для розробки + продакшн
- JSON файли замість БД (простота)
- Systemd для управління процесами
- Git-based backup стратегія
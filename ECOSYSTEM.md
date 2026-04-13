# ECOSYSTEM.md — Екосистема Pi5

## Карта проектів

### InSilver (`insilver-v3/`)
- **Призначення:** Telegram-бот консультант для ювелірної майстерні Влада
- **Користувачі:** клієнти ювелірки (українці)
- **Стек:** Python 3.11, python-telegram-bot, OpenAI GPT-4
- **Точка входу:** main.py
- **AI:** core/ai.py + core/prompt.py
- **Дані:** data/knowledge/training.json (15 Q&A записів)
- **Логи:** logs/bot.log
- **Ключові файли:** bot/admin.py (88KB — обережно!), bot/client.py, core/catalog.py
- **Сервіс:** insilver-v3.service (sudo systemctl)

### Abby (`abby/`)
- **Призначення:** дизайн-асистент для Ксюші
- **Стек:** Python, python-telegram-bot, Gemini Flash Image
- **AI:** core/image_gen.py (gemini-3.1-flash-image-preview — НЕ підтримує inpainting, завжди генерує з нуля)
- **Ключові файли:** core/prompt.py (doublecheck/даблчек feature), bot/client.py (_get_reply_images)
- **Сервіс:** abby.service (sudo systemctl)
- **Логи:** logs/bot.log
- **⚠️ Ніяких "Samuel" — назва назавжди Abby**

### Sam (`sam/`)
- **Призначення:** AI/кар'єрний асистент Сашка (новини + навчання)
- **Стек:** Python, python-telegram-bot, Claude (claude-sonnet-4-20250514)
- **Архітектура:** main.py + modules/ (base, digest, catchup, curriculum, onboarding, science)
- **AI:** call_claude / call_claude_with_search
- **Persona:** Samwise UA
- **Дані:** data/, profile.json
- **Команди:** /digest /science /catchup /cur /onboarding
- **Сервіс:** sam.service (sudo systemctl)
- **Логи:** тільки journalctl (файлових логів немає)

### Garcia (`garcia/`)
- **Призначення:** пакувальний дизайн навчання для Ксюші
- **Стек:** аналогічний Sam, persona Penelope Garcia
- **Команди:** /analyze /onboarding /cur /digest
- **Особливості:** auto-digest о 9:00 для ADMIN_IDS, 840 Pinterest pins в data/pinterest_analysis.json
- **Сервіс:** garcia.service (sudo systemctl)
- **Логи:** journalctl

### Meggie (`household_agent/`)
- **Призначення:** домашній асистент
- **⚠️ Відома проблема:** SyntaxError від \n в string literals при file-patching.
  Base64 pipeline не може містити Cyrillic або \n в string literals.
- **Сервіс:** household_agent.service (sudo systemctl)
- **Логи:** logs/bot.log

### Kit (`kit/` / OpenClaw workspace)
- **Призначення:** цей агент (дев для всієї екосистеми)
- **Сервіс:** openclaw-gateway (systemctl --user)
- **Утиліти:** health_monitor.py, cost_dashboard.py, ai_tracker.py, consult.py

## Спільні патерни

При фіксі в одному боті — перевір чи потрібен аналогічний фікс в інших:

| Патерн | Де використовується |
|--------|---------------------|
| BaseModule | Sam, Garcia |
| call_claude / call_claude_with_search | Sam, Garcia |
| persona prompts | Sam (Samwise), Garcia (Penelope), Abby (дизайнер) |
| python-telegram-bot | InSilver, Abby, Sam, Garcia, Meggie |
| systemd service | Всі |
| inline keyboard buttons | Sam (/cur), InSilver |

## AI провайдери

| Бот | Провайдер | Модель | Примітки |
|-----|-----------|--------|----------|
| InSilver | OpenAI | GPT-4 | Клієнтські консультації |
| Abby | Google | Gemini Flash Image | Генерація зображень, немає inpainting |
| Sam | Anthropic | Claude Sonnet | call_claude wrapper |
| Garcia | Anthropic | Claude Sonnet | call_claude wrapper |
| Kit | Anthropic | Claude (configurable) | OpenClaw gateway |

## Інфраструктура Pi5

- Все на одному Raspberry Pi 5 (dev + prod)
- Сервіси ізольовані через systemd
- Git-based backup (кожен проект — окреме repo)
- JSON замість БД
- Health monitoring: health_monitor.py (CPU >80% alert, RAM >85% критично)

## Git репо

| Проект | Шлях | Remote |
|--------|------|--------|
| InSilver | ~/.openclaw/workspace/insilver-v3/ | sandalya/insilver-v3 |
| Abby | ~/.openclaw/workspace/abby/ | sandalya/abby-v1 |
| Kit workspace | ~/.openclaw/workspace/ | sandalya/openclaw-kit |

## Логи по ботах

| Бот | Команда |
|-----|---------|
| InSilver | `tail -f ~/.openclaw/workspace/insilver-v3/logs/bot.log` |
| Abby | `tail -f ~/.openclaw/workspace/abby/logs/bot.log` |
| Sam | `journalctl -u sam -f --no-pager` |
| Garcia | `journalctl -u garcia -f --no-pager` |
| Meggie | `tail -f ~/.openclaw/workspace/household_agent/logs/bot.log` |
| Kit | `journalctl --user -u openclaw-gateway -f --no-pager` |

## Статус всіх одразу
```bash
for s in insilver-v3 abby household_agent sam garcia; do echo "=== $s ===" && sudo systemctl is-active $s; done && echo "=== kit ===" && systemctl --user is-active openclaw-gateway
```

## Debug-пайплайн (будь-який бот)
```bash
sudo systemctl status [сервіс]
tail -20 [шлях_до_логів] | grep -E "(ERROR|CRITICAL|Exception)" || echo "Clean"
ps aux | grep main.py | grep -v grep
```

### Sam/Garcia (немає файлових логів)
```bash
journalctl -u [sam|garcia] -n 30 --no-pager
```

## Аліаси в терміналі
Схема: [агент]-[дія]. Дії: start stop rs st log live cd.
Повний список: команда `agents`.

## GitHub → raw конвертація
Коли Сашко кидає github.com/.../blob/... URL:
→ Автоматично переформатувати на raw.githubusercontent.com і витягти через fetch.

## API ключі
Ніколи не показувати в терміналі. Показувати тільки останні 4 символи.

## Перед тестом бота
Завжди нагадати Сашку запустити логи ПЕРЕД відправкою повідомлення боту.

## Граматичні підказки (українська)
- Майбутній час: напишеш (не "писатимеш")
- Дієслова руху: йди (не "ходи")
- гарний/добрий (не "хороший")

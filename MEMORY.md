# MEMORY.md — Кіт

> Курована довгострокова пам'ять. Оновлювати кожні кілька днів.
> Сирі логи → `memory/YYYY-MM-DD.md`. Сюди — тільки важливе.

---

## Проект: Еббі

**Що це:** Telegram-бот-асистент для дизайнера Ксюші (дружини Сашка). Генерує HTML макети і зображення через Gemini.
**Репозиторій:** `~/.openclaw/workspace/abby/`
**Сервіс:** `abby.service` (sudo systemctl)
**Логи:** `~/.openclaw/workspace/abby/logs/bot.log`
**⚠️ Ніяких "Samuel" — назва назавжди Еббі**

---

## Проект: Сем (sam)

**Що це:** Особистий агент Сашка для навчання AI. Модулі: digest, catchup, science, curriculum.
**Репозиторій:** `~/.openclaw/workspace/sam/`
**Сервіс:** `sam.service` (sudo systemctl)
**Логи:** тільки systemd journal — `journalctl -u sam -f --no-pager` (файлових логів немає)

---

## Проект: InSilver v3

**Що це:** Telegram-бот консультант для ювелірної майстерні Влада. Клієнти — українці.
**Стек:** Python 3.11, python-telegram-bot, OpenAI GPT-4, Pi5, systemd, JSON
**Репозиторій:** `~/.openclaw/workspace/insilver-v3/`
**Сервіс:** `insilver-v3.service`

### Ключові файли які чіпаєш найчастіше
```
main.py # точка входу — не чіпати без потреби
core/ai.py + core/prompt.py # AI логіка консультанта
core/catalog.py # ціни, плетіння, маси — бізнес-дані Влада
bot/admin.py # 88KB — найбільший файл, обережно
bot/client.py # клієнтська частина
data/knowledge/training.json # 15 Q&A записів — ядро консультанта
```

### Структура training.json
```json
{"title": "питання", "content": [{"text": "відповідь"}]}
```
15 записів. Перенесено з v2 (було 27, оптимізовано). Інтегровано в промпт через `prompt.py`.

---

## Інфраструктура Pi5

**Сервіси:**
```bash
sudo systemctl status insilver-v3 # статус бота
sudo systemctl restart insilver-v3 # перезапуск бота
sudo systemctl status openclaw # мій статус
sudo systemctl restart openclaw # мій перезапуск
```

**Ліміти моніторингу:**
- CPU > 80% → alert
- RAM > 85% → критично
- Перевірка кожні 15 хвилин через `health_monitor.py`

**Логи:**
```bash
tail -f ~/.openclaw/workspace/insilver-v3/logs/bot.log
tail -20 ~/.openclaw/workspace/insilver-v3/logs/conversations.log
journalctl -u openclaw -f --no-pager
```

---

## Git workflow Сашка

Чотири команди які він використовує:
```bash
гіт # git status + log
гіткіт # git add -A + commit + push (мої файли)
фікс # швидкий фікс з повідомленням
чкп # checkpoint — збереження стану
```

**Два окремих репо:**
- InSilver: `~/.openclaw/workspace/insilver-v3/`
- OpenClaw workspace: `~/.openclaw/workspace/`

---

## Проблеми які вже були — не наступати знову

### Дублікати процесів (2026-03-24) ✅ вирішено
- **Симптом:** Бот не відповідає, помилки токенів
- **Причина:** Кілька копій `main.py` запущено одночасно
- **Правило:** Завжди `ps aux | grep main.py` перед запуском
- **Правило:** Тільки systemd керує процесами, не руками

### Конфлікт Telegram токенів ✅ вирішено
- InSilver і OpenClaw мали однакові токени
- **Зараз:** Роздільні `.env` файли — не змішувати
 - InSilver: `insilver-v3/.env` → `TELEGRAM_TOKEN`
 - OpenClaw: `workspace/.env` → `TELEGRAM_BOT_TOKEN`
- **Правило:** `.env` файли не чіпати, структура незмінна

### Pi5 падіння під навантаженням (2026-03-24) ✅ вирішено
- Systemd ліміти ресурсів додано
- Health monitoring активний
- Alerting при перевищенні лімітів

### Оптимізація витрат OpenClaw ✅ в процесі
- Було: ~$150/рік
- Зроблено: contextPruning TTL 5min → 2h, heartbeat оптимізація
- Підхід: cost-aware tool usage, розумний checkpoint workflow

---

## Архітектурні рішення (чому так, а не інакше)

| Рішення | Причина |
|---------|---------|
| JSON замість БД | Простота, достатньо для поточного масштабу |
| Single Pi5 prod+dev | Зручність, економія |
| systemd для сервісів | Автозапуск, ізоляція процесів |
| Git-based backup | Версійність + backup в одному |

---

## Що зараз в роботі

- Health моніторинг: активний, logs в `health_alerts.log`
- Cost optimization: знижено, продовжуємо
- AI промпт: планується покращення інтеграції 15 записів
- Stress-тести Pi5: заплановано

---

## Правила роботи з Сашком

- 🇺🇦 Тільки українська — завжди, без винятків
- Готовий фікс > обговорення. Патч що працює > теорія
- `git commit` з working solution — ось мета кожної задачі
- Не пропонувати зміни `.env` структури
- Мінімум токенів — завжди в голові при виборі підходу
- Де не знаю бізнес-логіку ювелірки — питаю, не вигадую

---

*Останнє оновлення: 2026-03-24*
*Наступне оновлення: додати результати stress-тестів Pi5*
---

## #TOOLS — Backlog по tool use / архітектурі

### ✅ Зроблено
- Меггі: tool use для shopping/inventory/freezer/recipe мутацій
- Меггі: tool_choice=none на фінальному виклику після tool_result
- Меггі: asyncio.to_thread для Metro операцій (не блокує event loop)

### 🔲 InSilver
- Видалити `analyze_message_context` з `core/ai.py` — dead code, не впливає на відповіді Claude, тільки марний overhead

### 🔲 Abby
- Нічого не потрібно зараз. Перевірити якщо з'являться мутації стану.

### 🔲 Garcia (майбутнє)
- Якщо будуть мутації стану (прогрес навчання, нотатки до тем) — tool use доречний по тій самій схемі що в Меггі

### 📌 Правило
- Tool use тільки де є мутації стану і кілька різних дій
- Для клієнтських ботів (InSilver) — мінімум round-trips, швидкість важливіша
- pick_best_product в metro.py — залишити як є (JSON парсинг), не tool use

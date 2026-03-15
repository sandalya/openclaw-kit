# MEMORY.md - Довготривала пам'ять

## Проект InSilver v2 - Telegram Бот для Ювелірної Майстерні

**Власник:** Влад (Владислав)  
**Розробник:** Сашко (Олександр)  
**Сервер:** Raspberry Pi 5  
**База:** 1,028 ювелірних виробів (CATALOG.md)  
**Статус:** 🟢 Production Live (PID 3942576)

---

## 🔄 Поточне: Step 1/5 Dynamic Form Integration (2026-03-15)

**Завершено:**
- ✅ form_config.py — 7 типів виробів з динамічними кроками
- ✅ order_form_new.py, order_form_adapter.py — нові функції  
- ✅ bot.py інтегрована з safe fallback
- ✅ Всі типи тестовані локально (8, 8, 6, 5, 6, 5, 5 кроків)
- ✅ Bot live з новим кодом (PID 3942576)
- ✅ Weight-aware search (тендітні ланцюжки < 120г)
- ✅ CATALOG.md з 1,028 виробів

**Коміти:** d2470fc, abfa974, 3c95044, 24ffba9

**На наступну сесію:**
1. Тест браслета у Telegram (моніторити bot.log)
2. Обновити show_form_step() + handle_order_form_callback()
3. Розширити на інші типи
4. Видалити fallback

---

## 🏗️ Архітектура

**Папки:**
- `/home/sashok/.openclaw/workspace/` — основна
- `insilver-v2/` — бот + форма + фото
- `memory/` — щоденні записи

**Ключові файли:**
- `bot.py` — main консультант (PID 3942576)
- `form_config.py` — 7 типів + кроки (динамічна)
- `order_form_new.py` — новий API форми
- `CATALOG.md` — 1,028 виробів розкритих
- `FORM_INTEGRATION.md` — 5-step план

**Bootstrap (автоматично інектуються):**
- SOUL.md, IDENTITY.md, USER.md, AGENTS.md, TOOLS.md

---

## 📊 Типи Виробів

| Тип | Кроків | Перший | Статус |
|-----|--------|--------|--------|
| Браслет | 8 | weaving (14) | ✅ |
| Ланцюжок | 8 | weaving (14) | ✅ |
| Обручка | 6 | style (4) | ✅ |
| Хрестик | 5 | cross_type (4) | ✅ |
| Перстень | 6 | motif (4) | ✅ |
| Кулон | 5 | collection (3) | ✅ |
| Набір | 5 | set_composition | ✅ |

---

## 🎯 УТОЧНИТИ У ВЛАДА

1. Які вироби мають плетіння?
2. Які кроки для кожного типу? (застібка для кулона?)
3. Розміри для печатки/обручки/набору?

---

## 🔧 Проблеми & Рішення (2026-03-15, вечірня сесія)

**Проблема:** Кіт в Telegram відповідав як "порожній агент" без особистості

**Причини:**
1. ❌ Токен в `openclaw.json` ≠ `.env` 
2. ❌ MEMORY.md був 40KB → витіснув SOUL.md + IDENTITY.md із bootstrap контексту
3. ❌ `agent.py` + `bot.py` конфліктували на одному токені (409 error)

**Виправлення:**
- ✅ Токен синхронізований
- ✅ MEMORY.md скорочено до 3KB
- ✅ Кіт тепер в Telegram з повною особистістю
- ✅ Два окремих боти на різних токенах (Option A)

**Токени (ФІКСОВАНО):**
```
~/.openclaw/workspace/.env          → @kit_sashok_assistant_bot
~/.openclaw/workspace/insilver-v2/.env → @gamaiunchik_bot
```

**Статус Запуску:**
- OpenClaw (Kit) — systemd автоматично ✅
- bot.py (InSilver) — PID 247232, живий ✅

**Постійний запуск bot.py: ✅ НАЛАШТОВАНО**
```bash
bash ~/.openclaw/workspace/insilver-v2/setup-systemd.sh
```

Статус:
- 🟢 Active (running) — PID 251624
- 🚀 Автозапуск при ребуті: enabled
- 📋 Управління:
  ```bash
  sudo systemctl stop insilver-bot      # зупинити
  sudo systemctl restart insilver-bot   # перезапустити
  sudo systemctl status insilver-bot    # статус
  journalctl -u insilver-bot -f         # живі логи
  ```

---

## 🎭 Архітектура: 2 Боти на Різних Токенах

**Потреба:**
- `bot.py` — консультант для клієнтів InSilver (Telegram channel/bot)
- `agent.py` — агент OpenClaw для Сашка (через kit_assistant_bot)
- Паралельно, без конфліктів

**Рішення:**
```
.env:
  TELEGRAM_BOT_TOKEN = bot_token_insilver    # Для bot.py
  KIT_AGENT_BOT_TOKEN = kit_agent_token      # Для agent.py (OpenClaw)
  
openclaw.json:
  "telegram": { "token": "kit_agent_token" } # OpenClaw токен
```

**Запуск:**
```bash
# Terminal 1 (інкапсульовано)
cd insilver-v2/
python3 bot_manager.py start

# Terminal 2 (OpenClaw)
openclaw status  # Кіт готовий слухати в Telegram
```

---

## ⚙️ Команди

```bash
cd insilver-v2/
python3 bot_manager.py status      # Стан
python3 test_weight_fix.py         # Тести (4/4 PASS)
tail -f bot.log                    # Логи
```

**OpenClaw Bootstrap:** agents.defaults.workspace = ~/.openclaw/workspace  
**Максимум per файл:** 20,000 chars  
**Максимум разом:** 150,000 chars

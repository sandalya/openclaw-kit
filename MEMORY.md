# MEMORY.md — Довгострокова пам'ять Кота

> Курована. Оновлювати кожні кілька днів.
> Сирі логи → memory/YYYY-MM-DD.md. Тут — тільки патерни і уроки.

## Аналіз екосистеми (Opus, квітень 2026)
Файл: kit/memory/ecosystem_analysis_opus.md + sam/data/ecosystem_analysis_opus.md
Деталі: kit/memory/2026-04-13.md

Ключові проблеми (пріоритет):
1. InSilver — видалити мертві файли (main_broken.py, main_old_broken.py та ін.)
2. Sam base.py — дублює AgentBase. Привести до стану Garcia base.py
3. shared/config.py — моделі хардкоджені в 5+ місцях
4. Tool use — додати до Sam
5. Agentic loop — retry + валідація (почати з /digest)
6. Prompt management — промпти в .md файли
7. Тести — pytest для shared/
8. Kit health check — heartbeat від усіх ботів

Баг виправлений (2026-04-13):
- shared/agent_base.py → parse_json_response повертала [] замість dict
- Sam /digest завис через це (PARSED value=[])
- Виправлено: тепер повертає list або dict як є

---

## Проблеми які вже були — RUNBOOK

### Дублікати процесів
- Симптом: Бот не відповідає, помилки токенів
- Діагноз: ps aux | grep main.py | grep -v grep → більше 1
- Фікс: kill всі → systemctl restart
- Профілактика: завжди перевіряти перед запуском

### Конфлікт Telegram токенів
- Симптом: дивна поведінка, "не мій чат"
- Причина: однакові токени в різних .env
- Правило: .env файли не чіпати
- InSilver: TELEGRAM_TOKEN, OpenClaw: TELEGRAM_BOT_TOKEN

### Pi5 падіння під навантаженням
- Фікс: systemd ліміти ресурсів + health monitoring
- Моніторинг: health_monitor.py (CPU >80%, RAM >85%)

### Meggie SyntaxError
- Причина: \n в string literals при file-patching
- Правило: base64 pipeline без Cyrillic і \n в string literals

---

## Архітектурні рішення

| Рішення | Причина |
|---------|---------|
| JSON замість БД | Простота, достатньо для поточного масштабу |
| Single Pi5 | Зручність, економія |
| systemd | Автозапуск, ізоляція |
| Git backup | Версійність + backup |

---

## Cost уроки
- OpenClaw ~$150/рік до оптимізації
- contextPruning TTL 5min → 2h (значна економія)
- Heartbeat оптимізація: lightContext: true
- $400 загальних витрат на навчання Кота — рахуй кожен токен

---

## Tools backlog

### Зроблено
- Meggie: tool use для shopping/inventory/freezer/recipe мутацій
- Meggie: tool_choice=none на фінальному виклику після tool_result
- Meggie: asyncio.to_thread для Metro операцій

### InSilver
- Видалити analyze_message_context з core/ai.py — dead code, overhead

### Garcia (майбутнє)
- Tool use якщо з'являться мутації стану (прогрес навчання, нотатки)

### Правило
- Tool use тільки де є мутації стану і кілька різних дій
- Для клієнтських ботів (InSilver) — мінімум round-trips

*Останнє оновлення: 2026-04-13*

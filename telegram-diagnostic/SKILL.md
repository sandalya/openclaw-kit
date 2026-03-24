---
name: telegram-diagnostic
description: Діагностика та вирішення конфліктів Telegram ботів. Use when: bot shows "terminated by other getUpdates request", multiple bot processes running simultaneously, token conflicts, webhook/polling conflicts, or any Telegram bot connectivity issues. Provides systematic diagnostics, conflict resolution, and prevention strategies.
---

# Telegram Bot Diagnostic

Системна діагностика та вирішення проблем з Telegram ботами. Вирішує 95% типових проблем автоматично.

## Коли використовувати

- ❌ `telegram.error.Conflict: terminated by other getUpdates request`  
- ❌ Бот перестав відповідати без очевидних причин
- ❌ Підозри на дублікати процесів або конфлікти токенів
- ❌ Проблеми з webhook vs polling
- ❌ Токен працює в тестах, але не в production

## Швидка діагностика

Запустіть повну діагностику:

```bash
scripts/telegram_full_diagnostic.py --token "YOUR_TOKEN" --check-processes --check-webhooks
```

Або етапами:

### 1. Перевірка процесів з токеном

```bash
scripts/find_token_conflicts.py "8627596455:AAG..."
```

### 2. Тест токена

```bash
scripts/test_telegram_token.py "8627596455:AAG..."
```

### 3. Webhook діагностика

```bash
scripts/telegram_webhook_diagnostic.py "8627596455:AAG..."
```

## Типові проблеми та рішення

### Проблема 1: getUpdates конфлікт

**Симптом:** `terminated by other getUpdates request`

**Причина:** Два процеси використовують polling одночасно.

**Рішення:**
1. Знайти конфліктні процеси: `scripts/find_token_conflicts.py`
2. Зупинити зайві: `kill PID` або `systemctl stop`
3. Очистити webhook: `scripts/clear_webhooks.py` 

### Проблема 2: Phantom webhook

**Симптом:** Бот не отримує повідомлення, але токен валідний

**Причина:** Старий webhook блокує polling.

**Рішення:**
1. Перевірити webhook: `scripts/telegram_webhook_diagnostic.py`
2. Очистити: `curl -X POST "https://api.telegram.org/bot$TOKEN/deleteWebhook"`

### Проблема 3: Systemd дублікати

**Симптом:** Сервіс запущений, але процес відсутній/конфліктний

**Рішення:**
1. Повна зупинка: `systemctl stop SERVICE_NAME`
2. Очистка phantom: `scripts/cleanup_telegram_phantoms.py`
3. Перезапуск: `systemctl start SERVICE_NAME`

## Детальна діагностика

Для складних випадків див. [DIAGNOSTICS.md](references/DIAGNOSTICS.md) - повний checklist із 15 кроків.

Для webhook налаштування див. [WEBHOOK_SETUP.md](references/WEBHOOK_SETUP.md).

Для systemd інтеграції див. [SYSTEMD_BEST_PRACTICES.md](references/SYSTEMD_BEST_PRACTICES.md).

## Профілактика

1. **Один токен = один процес**: Ніколи не запускайте два процеси на одному токені
2. **Clear start strategy**: Завжди перевіряйте поточні процеси перед запуском
3. **Systemd locks**: Використовуйте lock файли в systemd сервісах
4. **Environment isolation**: Різні боти = різні .env файли

Запустіть `scripts/telegram_setup_prevention.py` для автоматичного налаштування.
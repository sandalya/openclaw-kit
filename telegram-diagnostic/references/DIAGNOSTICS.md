# Повна діагностика Telegram проблем

## 15-крокова діагностика

### 1. Базова перевірка токена
```bash
curl "https://api.telegram.org/bot$TOKEN/getMe"
```
**Очікуваний результат:** `{"ok":true,"result":{"id":...}}`
**Якщо помилка:** Перевірте токен, можливо змінився

### 2. Перевірка webhook стану
```bash
curl "https://api.telegram.org/bot$TOKEN/getWebhookInfo"
```
**Небезпечно якщо:** `url` не порожній - webhook блокує polling

### 3. Тест polling
```bash
curl "https://api.telegram.org/bot$TOKEN/getUpdates?timeout=5&limit=1"
```
**Конфлікт якщо:** HTTP 409 "terminated by other getUpdates request"

### 4. Пошук процесів з токеном
```bash
ps aux | grep "bot\.py\|telegram\|insilver"
sudo lsof | grep "$TOKEN_PREFIX"
```
**Проблема якщо:** > 1 процесу з одним токеном

### 5. Systemd сервіси
```bash
systemctl list-units | grep -E "telegram|bot|insilver"
systemctl status SERVICE_NAME
```
**Перевірити:** Чи не запущено декілька сервісів

### 6. Мережеві з'єднання
```bash
netstat -tlnp | grep ":443\|:8443\|:8080"
ss -tulpn | grep python
```
**Шукати:** Декілька процесів на одному порті

### 7. Логи процесів
```bash
tail -50 /var/log/syslog | grep telegram
journalctl -u SERVICE_NAME --since "1 hour ago"
```
**Індикатори проблем:** "Conflict", "terminated", "timeout"

### 8. Environment змінні
```bash
printenv | grep -E "TELEGRAM|BOT"
find . -name ".env" -exec grep -l "TELEGRAM" {} \;
```
**Ризик:** Декілька .env з одним токеном

### 9. Python процеси детально
```bash
pgrep -f python | xargs ps -p
lsof -p PID | grep network
```
**Аналіз:** Які файли/мережі використовує кожен процес

### 10. Docker контейнери
```bash
docker ps | grep telegram
docker logs CONTAINER_ID
```
**Перевірити:** Чи не запущено бота в контейнері

### 11. Cron jobs
```bash
crontab -l | grep -E "telegram|bot"
sudo crontab -l | grep -E "telegram|bot"
```
**Ризик:** Автоматичне перезапускання ботів

### 12. File locks
```bash
find /tmp -name "*telegram*" -o -name "*bot*"
lsof | grep ".lock"
```
**Очистити:** Старі lock файли

### 13. Проксі та мережа
```bash
echo $https_proxy $http_proxy
ping api.telegram.org
```
**Проблеми:** Блокування або повільна мережа

### 14. Memory та ресурси
```bash
free -h
ps aux --sort=-%mem | grep python
```
**Проблема:** Недостатньо ресурсів для роботи

### 15. Telegram API лімити
```bash
curl -w "%{http_code}" "https://api.telegram.org/bot$TOKEN/getMe"
```
**Rate limit якщо:** HTTP 429

## Типові комбінації проблем

### Проблема: OpenClaw + окремий бот
**Симптом:** Обидва використовують один токен
**Рішення:** Різні токени або відключити один

### Проблема: Systemd phantom процеси
**Симптом:** Сервіс "active" але процесу немає
**Рішення:** `systemctl daemon-reload && systemctl restart`

### Проблема: Webhook zombie
**Симптом:** Webhook давно не працює, але не очищений
**Рішення:** `deleteWebhook` + `getUpdates` offset=-1

### Проблема: Multiple systemd services
**Симптом:** Декілька сервісів з одним ботом
**Рішення:** Відключити зайві: `systemctl disable SERVICE`

### Проблема: Container + host процеси
**Симптом:** Бот в Docker + бот на хості
**Рішення:** `docker stop` або налаштувати різні токени

## Автоматичне рішення

```bash
# Повна очистка
./scripts/telegram_full_diagnostic.py --token "$TOKEN" --check-processes --check-webhooks --fix-conflicts

# Ручне рішення по кроках
./scripts/find_token_conflicts.py "$TOKEN" --kill
./scripts/clear_webhooks.py "$TOKEN"
systemctl restart YOUR_BOT_SERVICE
```

## Профілактичні заходи

### 1. Lock файли в systemd
```ini
[Service]
ExecStartPre=/bin/sh -c 'if [ -f /tmp/bot.lock ]; then PID=$(cat /tmp/bot.lock); if kill -0 $PID 2>/dev/null; then echo "Bot already running"; exit 1; fi; fi'
ExecStart=/path/to/bot.py
ExecStartPost=/bin/sh -c 'echo $MAINPID > /tmp/bot.lock'
ExecStopPost=/bin/sh -c 'rm -f /tmp/bot.lock'
```

### 2. Health check скрипти
```bash
#!/bin/bash
# health_check.sh
TOKEN="$1"
RESPONSE=$(curl -s "https://api.telegram.org/bot$TOKEN/getUpdates?timeout=1&limit=1")
if echo "$RESPONSE" | grep -q "terminated by other"; then
    echo "CONFLICT DETECTED"
    exit 1
fi
```

### 3. Monitoring
```bash
# Додати в crontab
*/5 * * * * /path/to/health_check.sh "$TOKEN" || logger "Telegram bot conflict"
```

Це покриває 99% всіх можливих проблем з Telegram ботами.
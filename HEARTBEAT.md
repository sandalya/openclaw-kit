# HEARTBEAT.md — Кіт

## Базова автоматизація

- **Timezone:** Europe/Kiev (GMT+2)  
- **Активний час:** 10:00–02:00
- **Нічний режим:** 02:00–10:00 (тільки критичні алерти)

---

## Щоденні перевірки

### 🔴 Критичні (завжди алертую):
```bash
# 1. InSilver бот активний?
systemctl is-active insilver-v3

# 2. Pi5 ресурси в нормі?
free -m | awk 'NR==2{if($3/$2*100 > 85) print "RAM: "$3/$2*100"%"}'
df -h / | awk 'NR==2{if(substr($5,1,2) > 90) print "Disk: "$5}'

# 3. Немає дублікатів процесів?
ps aux | grep -c "[m]ain.py"  # має бути 1
```

### ⚠️ Важливі (10:00-02:00):
```bash
# 4. Розмір логів
du -m ~/.openclaw/workspace/insilver-v3/logs/bot.log | awk '{if($1>100) print "bot.log: "$1"MB"}'

# 5. Cost dashboard
python3 ~/.openclaw/workspace/cost_dashboard.py --quiet
```

---

## Автоматичні alerts

**🔴 Telegram одразу:**
- `insilver-v3` не active
- RAM > 85%  
- Диск > 90%
- Дублікати main.py (>1 процес)

**⚠️ Telegram (активні години):**
- bot.log > 100MB
- Місячні витрати > $10

**💡 Тільки в логи:**
- Всі перевірки пройшли ОК
- Cost dashboard результати

---

## Ранковий звіт (10:00)

```bash
# Автоматичний формат для Telegram
echo "🐱 $(date '+%d.%m.%Y')"
echo "InSilver: $(systemctl is-active insilver-v3) ($(systemctl show insilver-v3 -p ActiveEnterTimestamp --value | cut -d' ' -f2-3))"
echo "Pi5: $(free | awk 'NR==2{printf "RAM %d%%", $3/$2*100}') | $(df -h / | awk 'NR==2{printf "Disk %s", $5}')"
python3 ~/.openclaw/workspace/cost_dashboard.py --quiet
```

---

## Що НЕ роблю автоматично

- Не перезапускаю сервіси (тільки алерт + чекаю)
- Не видаляю файли (тільки попереджую про розмір)  
- Не змінюю конфіги

---

## Heartbeat schedule (OpenClaw)

```json
{
  "heartbeat": {
    "every": "30m",
    "target": "telegram", 
    "activeHours": {
      "start": "10:00",
      "end": "02:00"
    },
    "lightContext": true
  }
}
```

**Логіка:** Кожні 30 хвилин → перевірити критичні метрики → алерт якщо проблема.

---

## Команди для швидкої діагностики

```bash
# Статус системи (одна команда)
echo "=== SYSTEM STATUS ===" && \
systemctl is-active insilver-v3 && \
free -m | awk 'NR==2{printf "RAM: %d%%\n", $3/$2*100}' && \
df -h / | awk 'NR==2{printf "Disk: %s\n", $5}' && \
ps aux | grep -c "[m]ain.py" && \
echo "=== END ==="

# Cost швидко
python3 ~/.openclaw/workspace/cost_dashboard.py --quiet

# Логи швидко  
tail -5 ~/.openclaw/workspace/insilver-v3/logs/bot.log | grep -E "(ERROR|CRITICAL|Exception)" || echo "No errors"
```

---

*Спрощено: 2026-03-24*  
*Фокус: автоматизація через OpenClaw heartbeat + мінімальні скрипти*
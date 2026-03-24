# DISASTER RECOVERY — Pi5 Reboot Loop

> Коли Кіт щось зламав і SSH недоступний.
> Створено після інциденту 2026-03-24.

---

## 🚨 Симптоми reboot-loop

- SSH connection refused / timeout
- Pi5 постійно перезавантажується
- Зелений LED миготить неправильно
- Система не завантажується повністю

---

## 🛡️ ПЛАН A: Фізичний доступ (якщо поруч)

### Крок 1: Аварійне відключення
```
1. Відключити Pi5 від живлення (витягти кабель)
2. Почекати 10 секунд
3. Під'єднати HDMI + клавіатуру
4. Увімкнути Pi5
```

### Крок 2: Safe boot режим
```
1. При завантаженні натиснути Shift (recovery mode)
2. Або: додати в cmdline.txt: init=/bin/bash
3. Отримати root shell без systemd
```

### Крок 3: Відкат змін
```bash
# Відключити автозапуск сервісів
sudo systemctl disable insilver-v3
sudo systemctl disable openclaw-gateway

# Відкатити останні зміни
cd ~/.openclaw/workspace/insilver-v3
git log --oneline -5
git reset --hard HEAD~1  # або до відомо стабільного коміту

# Відкатити конфіг OpenClaw
cd ~/.openclaw
cp openclaw.json.backup openclaw.json

# Перезавантажити
sudo reboot
```

---

## 🛡️ ПЛАН B: Віддалений доступ (без фізичного)

### Варіант 1: Інший комп'ютер в мережі
```
1. Телефон → hotspot Wi-Fi
2. Laptop підключити до того ж hotspot
3. nmap -sP 192.168.x.0/24  # знайти Pi5
4. SSH з laptop
```

### Варіант 2: Backup SSH ключі
```
# На Pi5 (зараз налаштувати):
sudo adduser emergency
sudo usermod -aG sudo emergency
# Додати окремі SSH ключі для emergency user
# Тестувати: ssh emergency@raspberrypi.local
```

### Варіант 3: VNC / TeamViewer
```bash
# Налаштувати на Pi5 (зараз):
sudo apt install tightvncserver
vncserver :1 -geometry 1024x768 -depth 24

# Автозапуск VNC навіть при проблемах SSH
sudo systemctl enable vncserver@1
```

---

## 🛡️ ПЛАН C: Превентивні заходи (зараз зробити!)

### 1. Автоматичний Rollback
Створити `safe_deploy.sh`:
```bash
#!/bin/bash
# Автоматично відкатити зміни якщо система не відповідає 5 хвилин

CHECKPOINT_FILE="/tmp/deploy_checkpoint"
echo "$(date): Deploy started" > $CHECKPOINT_FILE

# Задеплоїти зміни
systemctl restart insilver-v3

# Встановити таймер на 5 хвилин
(sleep 300 && if [ -f $CHECKPOINT_FILE ]; then 
    echo "Deploy failed - rolling back"
    git reset --hard HEAD~1
    systemctl restart insilver-v3
fi) &

echo "Deploy done. Run 'rm $CHECKPOINT_FILE' if all OK"
```

### 2. Health Check Endpoint
Додати до бота:
```python
@app.route('/health')
def health():
    return {"status": "ok", "timestamp": time.time()}

# Запустити на :8080
# curl http://pi5.local:8080/health
```

### 3. Systemd Recovery
```bash
# /etc/systemd/system/insilver-v3.service
[Service]
Restart=on-failure
RestartSec=30
StartLimitBurst=3
StartLimitIntervalSec=300
# Після 3 невдач за 5 хвилин - зупинити автоматично
```

### 4. Backup конфігурації (щодня)
```bash
#!/bin/bash
# backup_configs.sh
DATE=$(date +%Y%m%d)
mkdir -p ~/.openclaw/backups/$DATE

cp ~/.openclaw/openclaw.json ~/.openclaw/backups/$DATE/
cp ~/.openclaw/workspace/insilver-v3/.env ~/.openclaw/backups/$DATE/
cp /etc/systemd/system/insilver-v3.service ~/.openclaw/backups/$DATE/

# Зберегти тільки останні 7 днів
find ~/.openclaw/backups/ -mtime +7 -delete
```

---

## ⚡ Кіт: Безпечні практики

### Перед будь-якими змінами:
```bash
# 1. Створити checkpoint
git tag "before-$(date +%Y%m%d-%H%M)"

# 2. Бекап конфігів
cp openclaw.json openclaw.json.backup

# 3. Перевірити що є фізичний доступ до Pi5
echo "Сашко, ти поруч з Pi5? Щось важливе змінюватиму."
```

### Тестувати зміни:
```bash
# 1. Спочатку в test mode
systemctl stop insilver-v3
python3 main.py --test-mode  # 30 секунд, потім auto-exit

# 2. Поступовий restart
systemctl start insilver-v3
sleep 60  # чекати 1 хвилину
curl http://localhost:8080/health  # перевірити відповідь
```

### Ніколи не робити:
- Змінювати systemd конфіги без backup
- Реstarт OpenClaw + InSilver одночасно
- Git push без локального тестування
- Оновлення system packages пізно ввечері

---

## 📞 Emergency Contacts

**Якщо нічого не працює:**
1. **Перепочинок** - краще поспати і вранці з ясною головою
2. **Telegram Кіт** - якщо працює, попросити rollback команди
3. **Фізичний доступ** - keyboards + HDMI до Pi5
4. **У крайньому випадку** - переустановлення з backup SD карти

---

## 🧪 Тестування Recovery (TODO)

- [ ] Створити emergency SSH user
- [ ] Налаштувати VNC сервер
- [ ] Написати safe_deploy.sh
- [ ] Додати health endpoint до бота
- [ ] Налаштувати щоденні config backups
- [ ] Створити recovery SD карту з основними налаштуваннями

**Наступний раз коли щось пішло не так - цей план врятує нерви!**
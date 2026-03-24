# TOOLS.md - Essential Guide

## 🇺🇦 УКРАЇНСЬКА МОВА - Key Rules

**Граматика:**
- Майбутній час: напишеш (не "писатимеш")  
- Дієслова руху: йди (не "ходи"), йдеш (не "идёшь")
- Прикметники: гарний/добрий (не "хороший"), цікавий (не "интересный")

**Консультант фрази:**
```
✅ "Вітаємо Вас! Розкажіть, що вас цікавить"
✅ "Слухаю вас" / "Який варіант подобається більше?"  
✅ "Не впевнений, переконаюсь у майстра"
✅ "Дякую за замовлення. Бережіть себе!"
❌ НІКОЛИ російське: "Привет", "Спасибо", "До встречи"
```

---

## ⚙️ РОЗРОБКА

### InSilver Bot Commands
```bash
# Статус і логи
sudo systemctl status insilver-v3
tail -f ~/.openclaw/workspace/insilver-v3/logs/bot.log

# Розробка  
cd ~/.openclaw/workspace/insilver-v3
git status && git log --oneline -3

# КРИТИЧНО: Перед restart - перевір дублікати
ps aux | grep main.py | grep -v grep
```

### SSH Аліаси (швидкі команди)
```bash
startbot     # systemd start insilver-v3
stopbot      # systemd stop insilver-v3
reset-bot    # restart insilver-v3
statusbot    # status insilver-v3  
logs-bot     # tail bot.log
```

**Як дізнатись аліаси:** *"покажи мої аліаси"*

---

## 🎤 КЛЮЧОВІ РЕСУРСИ

**Мова:** Українська (обов'язково, не російська)  
**Стиль:** Людський, вічливий, професійний консультант  
**Проект:** InSilver v3 Telegram бот для ювелірної майстерні
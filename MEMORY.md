# MEMORY.md - Компактна пам'ять

## InSilver v3 - Telegram Бот для Ювелірної Майстерні

**Статус:** 🔄 Активна розробка  
**Сервер:** Raspberry Pi 5  
**Версія:** v3 (міграція з v2)

---

## 🎯 ПОТОЧНА ФАЗА: Telegram зв'язок

**ПРОБЛЕМА:** Handlers не спрацьовують - повідомлення не обробляються  
**СТАТУС:** Updates потрапляють в API, але не в handlers  
**NEXT:** Дебаг handlers/filters після оптимізації витрат  

**ВИРІШЕНО:**
- ✅ Token працює, getUpdates працює  
- ✅ Conflict errors усунені  
- ✅ 7 handlers налаштовано в Application

---

## 🔧 АРХІТЕКТУРА v3

**Структура:**
```
insilver-v3/
├── core/ - конфіг, AI, каталог, здоров'я
├── bot/ - client.py, order.py, admin.py
├── data/ - knowledge/training.json, orders/, media/
└── main.py - стабільна Telegram інтеграція
```

**Сервіс:** systemd insilver-v3

---

## 🎯 КРИТИЧНІ МОМЕНТИ

1. **Telegram Integration** - handlers debugging
2. **AI Integration** - knowledge від v2 → v3
3. **Cost Optimization** - OpenClaw витрати
4. **Production Stability** - інтеграція навчальних даних

---

## 🔄 ШВИДКІ КОМАНДИ

```bash
# Статус
sudo systemctl status insilver-v3
tail -f ~/.openclaw/workspace/insilver-v3/logs/bot.log

# Розробка
cd ~/.openclaw/workspace/insilver-v3
git status && git log --oneline -5
```
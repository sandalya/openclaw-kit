# AI Operations Tracker — Usage Guide

## 🚀 Швидкий старт

### Логування операції (робиш в кінці кожної задачі):
```python
from ai_tracker import log_operation

# Стандартне використання
log_operation("Fixed InSilver bot restart issue", ["exec", "read", "systemctl"], 
              context="Bot had duplicate processes", efficiency="high", category="debugging")

# Мінімальне  
log_operation("Updated documentation", ["write"])
```

### Перегляд логів:
```bash
python3 ai_tracker.py recent        # останні 10 операцій
python3 ai_tracker.py analyze       # швидкий efficiency аналіз
```

### Повний аналіз:
```bash
python3 analyze_ai_operations.py report        # повний звіт
python3 analyze_ai_operations.py efficiency    # patterns analysis  
python3 analyze_ai_operations.py trends        # тижневі тренди
```

## 📊 Categories

- **development** — кодинг, фічі, рефакторинг
- **debugging** — фікс багів, troubleshooting
- **monitoring** — health checks, статуси
- **analysis** — data analysis, звіти
- **documentation** — docs, comments, guides
- **infrastructure** — налаштування, deployment, системні зміни

## ⚡ Efficiency Levels

- **high** — багато результату за мало токенів/часу
- **medium** — стандартне співвідношення
- **low** — багато токенів/часу, мало результату (складні проблеми, експерименти)

## 🎯 Example Log Entry

```json
{
  "timestamp": "2026-03-28T10:18:00.123456",
  "task": "Created AI operations tracker system", 
  "tools": ["write", "exec"],
  "tool_count": 2,
  "context": "Sashko requested detailed tracking for analysis",
  "efficiency": "high",
  "category": "infrastructure",
  "notes": "New system for future optimization analysis"
}
```

## 🔮 Майбутній аналіз з Клодом

Коли накопичиться 50+ операцій:
1. `python3 analyze_ai_operations.py report > ai_report.txt`
2. Дати Клоду файл для insights
3. Оптимізувати workflow на базі patterns
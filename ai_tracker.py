#!/usr/bin/env python3
"""
AI Operations Tracker — детальний лог всіх операцій Кіта
Використання: log_operation(task, tools, context) в кінці кожної задачі
"""

import json
import time
from datetime import datetime
from pathlib import Path

TRACKER_FILE = Path.home() / ".openclaw/workspace/ai_operations.jsonl"

def log_operation(task_description, tools_used, context=None, efficiency="medium", category="general", notes=None):
    """
    Логує одну AI операцію в JSONL файл
    
    Args:
        task_description: Що робив (коротко)
        tools_used: Список використаних tools ["read", "exec", "write"]
        context: Додатковий контекст задачі
        efficiency: "low", "medium", "high" (багато результату за мало токенів)
        category: "monitoring", "development", "debugging", "analysis", "documentation"
        notes: Вільні нотатки
    """
    
    operation = {
        "timestamp": datetime.now().isoformat(),
        "task": task_description,
        "tools": tools_used,
        "tool_count": len(tools_used) if tools_used else 0,
        "context": context,
        "efficiency": efficiency,
        "category": category,
        "notes": notes,
        "session_info": {
            "model": "claude-sonnet-4-20250514",  # можна динамічно отримувати
            "session_start": time.time()  # baseline для розрахунку тривалості
        }
    }
    
    # Додаємо до JSONL файлу
    TRACKER_FILE.parent.mkdir(exist_ok=True)
    with open(TRACKER_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(operation, ensure_ascii=False) + "\n")
    
    print(f"📊 Logged: {task_description} | Tools: {len(tools_used)} | {efficiency} efficiency")

def show_recent_operations(limit=10):
    """Показує останні N операцій"""
    if not TRACKER_FILE.exists():
        print("❌ Немає логів операцій")
        return
    
    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    recent = lines[-limit:] if len(lines) > limit else lines
    
    print(f"📋 Останні {len(recent)} операцій:")
    for line in recent:
        op = json.loads(line.strip())
        timestamp = op["timestamp"][:16].replace("T", " ")  # 2026-03-28 10:17
        tools_str = ", ".join(op["tools"][:3])  # перші 3 tools
        if len(op["tools"]) > 3:
            tools_str += f" +{len(op['tools'])-3}"
        
        print(f"  {timestamp} | {op['task'][:50]:<50} | {tools_str:<20} | {op['efficiency']}")

def analyze_efficiency():
    """Швидкий аналіз efficiency patterns"""
    if not TRACKER_FILE.exists():
        print("❌ Немає даних для аналізу")
        return
    
    operations = []
    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        for line in f:
            operations.append(json.loads(line.strip()))
    
    if not operations:
        print("❌ Немає операцій")
        return
    
    # Групування по efficiency
    eff_stats = {"high": [], "medium": [], "low": []}
    for op in operations:
        eff_stats[op["efficiency"]].append(op["tool_count"])
    
    print("📈 Efficiency Analysis:")
    for level in ["high", "medium", "low"]:
        count = len(eff_stats[level])
        avg_tools = sum(eff_stats[level]) / count if count > 0 else 0
        print(f"  {level.title()}: {count} ops, avg {avg_tools:.1f} tools")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "recent":
            show_recent_operations()
        elif sys.argv[1] == "analyze":
            analyze_efficiency()
        else:
            print("Usage: python ai_tracker.py [recent|analyze]")
    else:
        print("AI Operations Tracker готовий!")
        print("Використання: python ai_tracker.py [recent|analyze]")
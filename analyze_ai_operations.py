#!/usr/bin/env python3
"""
AI Operations Analyzer — розширений аналіз для optimization insights
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path

TRACKER_FILE = Path.home() / ".openclaw/workspace/ai_operations.jsonl"

def load_operations(days_back=None):
    """Завантажує операції за останні N днів"""
    if not TRACKER_FILE.exists():
        return []
    
    operations = []
    cutoff = None
    if days_back:
        cutoff = datetime.now() - timedelta(days=days_back)
    
    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        for line in f:
            op = json.loads(line.strip())
            op_time = datetime.fromisoformat(op["timestamp"])
            
            if cutoff is None or op_time >= cutoff:
                operations.append(op)
    
    return operations

def efficiency_patterns():
    """Аналіз patterns efficiency"""
    ops = load_operations()
    
    print("🔍 EFFICIENCY PATTERNS")
    print("=" * 50)
    
    # Групування по efficiency + tool count
    eff_tools = defaultdict(list)
    for op in ops:
        eff_tools[op["efficiency"]].append(op["tool_count"])
    
    for eff in ["high", "medium", "low"]:
        tools = eff_tools[eff]
        if tools:
            avg_tools = sum(tools) / len(tools)
            print(f"{eff.upper():>6}: {len(tools):>3} ops | avg {avg_tools:.1f} tools | range {min(tools)}-{max(tools)}")
    
    print()
    
    # Top efficient tools combinations
    high_eff_tools = []
    for op in ops:
        if op["efficiency"] == "high":
            high_eff_tools.extend(op["tools"])
    
    tools_freq = Counter(high_eff_tools)
    print("🚀 Top tools in HIGH efficiency tasks:")
    for tool, count in tools_freq.most_common(5):
        print(f"   {tool}: {count} uses")

def category_breakdown():
    """Розбивка по категоріях"""
    ops = load_operations()
    
    print("\n📊 CATEGORY BREAKDOWN")
    print("=" * 50)
    
    cat_stats = defaultdict(lambda: {"count": 0, "tools": [], "efficiency": []})
    
    for op in ops:
        cat = op["category"]
        cat_stats[cat]["count"] += 1
        cat_stats[cat]["tools"].append(op["tool_count"])
        cat_stats[cat]["efficiency"].append(op["efficiency"])
    
    for cat, stats in sorted(cat_stats.items()):
        count = stats["count"]
        avg_tools = sum(stats["tools"]) / count
        high_eff = stats["efficiency"].count("high")
        eff_pct = (high_eff / count) * 100
        
        print(f"{cat:>15}: {count:>3} ops | {avg_tools:.1f} avg tools | {eff_pct:>4.0f}% high eff")

def weekly_trends():
    """Тижневі тренди"""
    ops = load_operations(days_back=7)
    
    print("\n📈 WEEKLY TRENDS (last 7 days)")
    print("=" * 50)
    
    if not ops:
        print("❌ Немає даних за тиждень")
        return
    
    # По дням
    daily = defaultdict(lambda: {"count": 0, "tools": 0})
    
    for op in ops:
        day = datetime.fromisoformat(op["timestamp"]).strftime("%Y-%m-%d")
        daily[day]["count"] += 1
        daily[day]["tools"] += op["tool_count"]
    
    print("Daily activity:")
    for day in sorted(daily.keys()):
        stats = daily[day]
        avg_tools = stats["tools"] / stats["count"] if stats["count"] > 0 else 0
        print(f"  {day}: {stats['count']:>2} ops, {avg_tools:.1f} avg tools")
    
    total_ops = len(ops)
    total_tools = sum(op["tool_count"] for op in ops)
    print(f"\nWeek total: {total_ops} ops, {total_tools} tools, {total_tools/total_ops:.1f} avg")

def generate_report():
    """Повний звіт для Клода"""
    print("🤖 AI OPERATIONS FULL REPORT")
    print("=" * 60)
    
    efficiency_patterns()
    category_breakdown() 
    weekly_trends()
    
    ops = load_operations()
    if ops:
        print(f"\n📋 Dataset: {len(ops)} operations since {ops[0]['timestamp'][:10]}")
        print("Ready for Claude analysis! 🎯")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "efficiency":
            efficiency_patterns()
        elif sys.argv[1] == "categories":
            category_breakdown()
        elif sys.argv[1] == "trends":
            weekly_trends()
        elif sys.argv[1] == "report":
            generate_report()
        else:
            print("Usage: python analyze_ai_operations.py [efficiency|categories|trends|report]")
    else:
        generate_report()
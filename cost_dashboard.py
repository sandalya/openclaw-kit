#!/usr/bin/env python3
# cost_dashboard.py — Кіт
# Показує витрати токенів за день/тиждень/місяць
# Запуск: python3 cost_dashboard.py
# Запуск тихо (для heartbeat): python3 cost_dashboard.py --quiet

import os
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
INSILVER = WORKSPACE / "insilver-v3"

# Ціни Anthropic ($/1M токенів)
PRICES = {
    "claude-sonnet": {"input": 3.0,  "output": 15.0},
    "claude-opus":   {"input": 15.0, "output": 75.0},
    "claude-haiku":  {"input": 0.25, "output": 1.25},
    "gpt-4o":        {"input": 5.0,  "output": 15.0},
    "gpt-4":         {"input": 30.0, "output": 60.0},
}

QUIET = "--quiet" in sys.argv

def color(text, code):
    if QUIET:
        return text
    return f"\033[{code}m{text}\033[0m"

def red(t):    return color(t, "31")
def yellow(t): return color(t, "33")
def green(t):  return color(t, "32")
def bold(t):   return color(t, "1")
def dim(t):    return color(t, "2")

def parse_openclaw_logs():
    """Читає логи OpenClaw і витягає використання токенів."""
    results = []
    log_path = WORKSPACE / "logs" / "openclaw.log"
    journal_cmd = "journalctl -u openclaw --no-pager -n 2000 2>/dev/null"

    lines = []

    if log_path.exists():
        try:
            lines = log_path.read_text(errors="ignore").splitlines()
        except Exception:
            pass

    if not lines:
        try:
            lines = os.popen(journal_cmd).read().splitlines()
        except Exception:
            pass

    # Шукаємо рядки з usage/tokens
    token_pattern = re.compile(
        r"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}).*?"
        r"input[_\s]tokens?[:\s]+(\d+).*?output[_\s]tokens?[:\s]+(\d+)",
        re.IGNORECASE
    )
    model_pattern = re.compile(r"(claude-sonnet|claude-opus|claude-haiku|gpt-4o|gpt-4)", re.IGNORECASE)

    for line in lines:
        m = token_pattern.search(line)
        if m:
            date_str, time_str, inp, out = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
            model_m = model_pattern.search(line)
            model = model_m.group(1).lower() if model_m else "claude-sonnet"
            results.append({
                "date": date_str,
                "time": time_str,
                "model": model,
                "input": inp,
                "output": out,
                "source": "openclaw"
            })

    return results

def parse_insilver_logs():
    """Читає bot.log InSilver і витягає виклики AI."""
    results = []
    log_path = INSILVER / "logs" / "bot.log"

    if not log_path.exists():
        return results

    try:
        lines = log_path.read_text(errors="ignore").splitlines()
    except Exception:
        return results

    # Шукаємо usage або просто підраховуємо виклики GPT-4
    token_pattern = re.compile(
        r"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}).*?"
        r"(?:usage|tokens?).*?(\d+).*?(\d+)",
        re.IGNORECASE
    )
    call_pattern = re.compile(
        r"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}).*?"
        r"(?:openai|gpt-4|completion|response)",
        re.IGNORECASE
    )

    for line in lines:
        m = token_pattern.search(line)
        if m:
            results.append({
                "date": m.group(1),
                "time": m.group(2),
                "model": "gpt-4",
                "input": int(m.group(3)),
                "output": int(m.group(4)),
                "source": "insilver"
            })
        elif call_pattern.search(line):
            # Немає точних токенів — оцінка: середній діалог ~500 input + 300 output
            m2 = call_pattern.search(line)
            results.append({
                "date": m2.group(1),
                "time": m2.group(2),
                "model": "gpt-4",
                "input": 500,
                "output": 300,
                "source": "insilver",
                "estimated": True
            })

    return results

def calc_cost(records, since_date):
    """Рахує витрати з певної дати."""
    total_input = 0
    total_output = 0
    total_cost = 0.0
    estimated = False
    by_model = {}

    for r in records:
        if r["date"] < since_date:
            continue
        model_key = None
        for k in PRICES:
            if k in r["model"]:
                model_key = k
                break
        if not model_key:
            model_key = "claude-sonnet"

        price = PRICES[model_key]
        cost = (r["input"] / 1_000_000 * price["input"] +
                r["output"] / 1_000_000 * price["output"])

        total_input += r["input"]
        total_output += r["output"]
        total_cost += cost
        if r.get("estimated"):
            estimated = True

        if model_key not in by_model:
            by_model[model_key] = {"input": 0, "output": 0, "cost": 0.0, "calls": 0}
        by_model[model_key]["input"] += r["input"]
        by_model[model_key]["output"] += r["output"]
        by_model[model_key]["cost"] += cost
        by_model[model_key]["calls"] += 1

    return total_input, total_output, total_cost, by_model, estimated

def format_cost(cost):
    if cost < 0.01:
        return green(f"${cost:.4f}")
    elif cost < 0.5:
        return green(f"${cost:.3f}")
    elif cost < 5.0:
        return yellow(f"${cost:.2f}")
    else:
        return red(f"${cost:.2f}")

def run():
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    openclaw_records = parse_openclaw_logs()
    insilver_records = parse_insilver_logs()
    all_records = openclaw_records + insilver_records

    if QUIET:
        # Короткий вивід для heartbeat
        _, _, day_cost, _, _ = calc_cost(all_records, today)
        _, _, month_cost, _, _ = calc_cost(all_records, month_ago)
        print(f"💰 Токени сьогодні: ${day_cost:.3f} | місяць: ${month_cost:.2f}")
        if month_cost > 10:
            print(f"⚠️ Місячні витрати ${month_cost:.2f} — перевір dashboard")
        return

    # Повний вивід
    print()
    print(bold("═══════════════════════════════════════"))
    print(bold("   🐱 Cost Dashboard — Кіт + InSilver  "))
    print(bold("═══════════════════════════════════════"))
    print(dim(f"   {datetime.now().strftime('%d.%m.%Y %H:%M')} | Pi5"))
    print()

    for label, since, records_set, icon in [
        ("Сьогодні",  today,      all_records, "📅"),
        ("7 днів",    week_ago,   all_records, "📆"),
        ("30 днів",   month_ago,  all_records, "🗓️ "),
    ]:
        inp, out, cost, by_model, estimated = calc_cost(records_set, since)
        est_mark = dim(" ~оцінка") if estimated else ""
        print(f"  {icon} {bold(label)}: {format_cost(cost)}{est_mark}")
        if by_model:
            for model, stats in sorted(by_model.items(), key=lambda x: -x[1]["cost"]):
                source_records = [r for r in records_set if r["date"] >= since and model in r["model"]]
                oc = sum(1 for r in source_records if r["source"] == "openclaw")
                ins = sum(1 for r in source_records if r["source"] == "insilver")
                sources = []
                if oc:  sources.append(f"кіт:{oc}")
                if ins: sources.append(f"insilver:{ins}")
                print(dim(f"     {model}: ${stats['cost']:.4f} ({', '.join(sources)})"))
        print()

    # Прогноз місяця
    _, _, week_cost, _, _ = calc_cost(all_records, week_ago)
    monthly_projection = week_cost / 7 * 30
    print(f"  📈 Прогноз місяця: {format_cost(monthly_projection)}")
    print(f"  🎯 Бюджет: {green('$12.50/міс')} ({green('$150/рік')})")

    if monthly_projection > 12.5:
        over = monthly_projection - 12.5
        print(f"  {red(f'⚠️  Перевищення прогнозу на ${over:.2f}')}")
    else:
        left = 12.5 - monthly_projection
        print(f"  {green(f'✅ Залишок бюджету ~${left:.2f}')}")

    print()

    # Якщо немає даних
    if not all_records:
        print(dim("  Логи порожні або формат не розпізнано."))
        print(dim("  Перевір шляхи до логів у скрипті."))
        print()

    print(bold("═══════════════════════════════════════"))
    print()

if __name__ == "__main__":
    run()
#!/usr/bin/env python3
"""
consult.py — openclaw-kit consultation module
Дозволяє агенту консультуватися з Claude по складних питаннях.

Використання:
 python consult.py "Твоє питання або опис проблеми"
 python consult.py "Питання" --context path/to/file.md
 python consult.py "Питання" --type bug|decision|review|stuck
 python consult.py "Питання" --status "вирішено"
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error

# ── Конфігурація ──────────────────────────────────────────────────────────────

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2000
CONSULTATIONS_LOG = Path(__file__).parent / "CONSULTATIONS.md"
API_KEY_ENV = "ANTHROPIC_API_KEY"

SYSTEM_PROMPT = """Ти — старший консультант для AI агента на імʼя openclaw.
Агент звертається до тебе коли застряє, не може прийняти рішення, або хоче перевірити своє рішення.

Твої відповіді мають бути:
- Конкретними і actionable (не теоретичними)
- Стислими (агент читає програмно — без зайвих слів)
- Структурованими: спочатку діагноз, потім рекомендація, потім конкретні кроки

Якщо питання про код — давай конкретні приклади.
Якщо питання про рішення — давай чітку рекомендацію з коротким обґрунтуванням.
Відповідай мовою запиту."""

CONSULTATION_TYPES = {
 "bug": "🐛 Баг/помилка",
 "decision": "🤔 Рішення",
 "review": "🔍 Перевірка",
 "stuck": "🔧 Застряг",
 "general": "💬 Загальне",
}

# ── Основна логіка ────────────────────────────────────────────────────────────

def get_api_key() -> str:
 key = os.environ.get(API_KEY_ENV)
 if not key:
  print(f"[consult] Помилка: змінна середовища {API_KEY_ENV} не встановлена.", file=sys.stderr)
  print(f"[consult] Встанови: export {API_KEY_ENV}=sk-ant-...", file=sys.stderr)
  sys.exit(1)
 return key


def build_message(question: str, context, consult_type: str) -> str:
 type_label = CONSULTATION_TYPES.get(consult_type, CONSULTATION_TYPES["general"])
 parts = [
  f"**Тип консультації:** {type_label}",
  f"**Питання:**\n{question}",
 ]
 if context:
  parts.append(f"**Контекст:**\n{context}")
 return "\n\n".join(parts)


def call_claude(question: str, context, consult_type: str) -> str:
 api_key = get_api_key()
 message_content = build_message(question, context, consult_type)

 payload = {
  "model": MODEL,
  "max_tokens": MAX_TOKENS,
  "system": SYSTEM_PROMPT,
  "messages": [{"role": "user", "content": message_content}],
 }

 req = urllib.request.Request(
  API_URL,
  data=json.dumps(payload).encode("utf-8"),
  headers={
   "Content-Type": "application/json",
   "x-api-key": api_key,
   "anthropic-version": "2023-06-01",
  },
  method="POST",
 )

 try:
  with urllib.request.urlopen(req, timeout=60) as resp:
   data = json.loads(resp.read().decode("utf-8"))
   return data["content"][0]["text"]
 except urllib.error.HTTPError as e:
  body = e.read().decode("utf-8")
  print(f"[consult] HTTP помилка {e.code}: {body}", file=sys.stderr)
  sys.exit(1)
 except urllib.error.URLError as e:
  print(f"[consult] Помилка зʼєднання: {e.reason}", file=sys.stderr)
  sys.exit(1)


def append_to_log(question: str, answer: str, consult_type: str, status: str) -> None:
 type_label = CONSULTATION_TYPES.get(consult_type, CONSULTATION_TYPES["general"])
 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

 entry = (
  f"\n## {timestamp} {type_label}\n"
  f"**Питання:** {question}\n\n"
  f"**Відповідь:**\n{answer}\n\n"
  f"**Статус:** {status}\n\n"
  f"---"
 )

 if not CONSULTATIONS_LOG.exists():
  CONSULTATIONS_LOG.write_text("# Consultations Log\n", encoding="utf-8")

 with CONSULTATIONS_LOG.open("a", encoding="utf-8") as f:
  f.write(entry + "\n")


def load_context_file(path: str) -> str:
 p = Path(path)
 if not p.exists():
  print(f"[consult] Файл контексту не знайдено: {path}", file=sys.stderr)
  sys.exit(1)
 return p.read_text(encoding="utf-8")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
 parser = argparse.ArgumentParser(
  description="Консультація агента openclaw з Claude",
  formatter_class=argparse.RawDescriptionHelpFormatter,
  epilog="""
Приклади:
 python consult.py "Як обробити випадок коли токен протух?"
 python consult.py "Переглянь мій план" --type review --context DEV_CHECKPOINT.md
 python consult.py "Баг у парсері" --type bug --status "вирішено"
 """,
 )
 parser.add_argument("question", help="Питання або опис проблеми")
 parser.add_argument(
  "--type", "-t",
  choices=list(CONSULTATION_TYPES.keys()),
  default="general",
  help="Тип консультації (default: general)",
 )
 parser.add_argument(
  "--context", "-c",
  metavar="FILE",
  help="Шлях до файлу з додатковим контекстом (напр. DEV_CHECKPOINT.md)",
 )
 parser.add_argument(
  "--status", "-s",
  default="очікує",
  help="Статус для логу (default: 'очікує')",
 )
 parser.add_argument(
  "--no-log",
  action="store_true",
  help="Не записувати в CONSULTATIONS.md",
 )

 args = parser.parse_args()

 context = load_context_file(args.context) if args.context else None

 print(f"[consult] Відправляю запит до Claude ({MODEL})...", file=sys.stderr)
 answer = call_claude(args.question, context, args.type)

 # Виводимо відповідь у stdout — агент може її читати програмно
 print(answer)

 if not args.no_log:
  append_to_log(args.question, answer, args.type, args.status)
  print(f"\n[consult] Записано в {CONSULTATIONS_LOG}", file=sys.stderr)


if __name__ == "__main__":
 main()
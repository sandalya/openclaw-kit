#!/usr/bin/env python3
"""Auto-checkpoint tracker для розумної системи"""
import os
import time
import json
from pathlib import Path

TRACKER_FILE = Path.home() / '.openclaw' / 'workspace' / '.checkpoint_tracker.json'

def load_tracker():
    if TRACKER_FILE.exists():
        try:
            return json.loads(TRACKER_FILE.read_text())
        except:
            pass
    return {
        'tool_calls': 0,
        'last_checkpoint': time.time(),
        'session_start': time.time()
    }

def save_tracker(data):
    TRACKER_FILE.write_text(json.dumps(data, indent=2))

def should_auto_checkpoint():
    """Чи час для авто-чекпоінту?"""
    data = load_tracker()
    now = time.time()
    
    # 50 tool calls OR 45 minutes
    time_limit = 45 * 60  # 45 minutes
    
    return (
        data['tool_calls'] >= 50 or 
        (now - data['last_checkpoint']) >= time_limit
    )

def increment_tool_calls():
    """Додати tool call"""
    data = load_tracker()
    data['tool_calls'] += 1
    save_tracker(data)

def reset_checkpoint():
    """Скинути після чекпоінту"""  
    data = load_tracker()
    data['tool_calls'] = 0
    data['last_checkpoint'] = time.time()
    save_tracker(data)


def run_chkp(project, description, next_step, context='', context_update=''):
    """Виконати чекпоінт: SESSION.md + git + опційно CONTEXT.md"""
    import subprocess
    from datetime import datetime

    workspace = Path.home() / '.openclaw' / 'workspace'

    # 1. Запускаємо chkp.sh
    chkp_sh = workspace / 'kit' / 'chkp.sh'
    args = [str(chkp_sh), project, description, next_step]
    if context:
        args.append(context)
    subprocess.run(['bash'] + args)

    # 2. Якщо є оновлення контексту — append в CONTEXT.md
    if context_update:
        context_file = workspace / project / 'CONTEXT.md'
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        block = f"\n## {date_str}\n{context_update}\n"
        with open(context_file, 'a', encoding='utf-8') as f:
            f.write(block)
        print(f"\n✅ CONTEXT.md оновлено: {context_file}")

    # 3. Скидаємо лічильник
    reset_checkpoint()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'check':
            print('true' if should_auto_checkpoint() else 'false')
        elif sys.argv[1] == 'increment':
            increment_tool_calls()
        elif sys.argv[1] == 'reset':
            reset_checkpoint()
        elif sys.argv[1] == 'chkp':
            if len(sys.argv) < 5:
                print("Usage: checkpoint_tracker.py chkp <project> <description> <next_step> [context] [context_update]")
                sys.exit(1)
            run_chkp(
                project=sys.argv[2],
                description=sys.argv[3],
                next_step=sys.argv[4],
                context=sys.argv[5] if len(sys.argv) > 5 else '',
                context_update=sys.argv[6] if len(sys.argv) > 6 else ''
            )
        elif sys.argv[1] == 'status':
            data = load_tracker()
            print(f"Tool calls: {data['tool_calls']}/50")
            elapsed = (time.time() - data['last_checkpoint']) / 60
            print(f"Time since last: {elapsed:.1f}/45 minutes")

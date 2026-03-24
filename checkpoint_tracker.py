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

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'check':
            print('true' if should_auto_checkpoint() else 'false')
        elif sys.argv[1] == 'increment':
            increment_tool_calls()
        elif sys.argv[1] == 'reset':
            reset_checkpoint()
        elif sys.argv[1] == 'status':
            data = load_tracker()
            print(f"Tool calls: {data['tool_calls']}/50")
            elapsed = (time.time() - data['last_checkpoint']) / 60
            print(f"Time since last: {elapsed:.1f}/45 minutes")

#!/usr/bin/env python3
"""
Знайти всі процеси що використовують конкретний Telegram токен
"""
import os
import sys
import subprocess
import argparse
import re

def find_token_processes(token):
    """Знайти всі процеси що містять токен або схожі patterns"""
    
    # Безпечно обрізаємо токен для пошуку
    bot_id = token.split(':')[0]  # Частина до двокрапки
    token_prefix = token[:20]     # Перші 20 символів
    
    print(f"🔍 Шукаємо процеси з токеном bot{bot_id}...")
    
    processes = []
    
    try:
        # 1. Пошук через ps aux
        ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        for line in ps_result.stdout.split('\n'):
            line_lower = line.lower()
            if any([
                bot_id in line,
                token_prefix in line,
                'bot.py' in line_lower,
                'telegram' in line_lower and ('bot' in line_lower or 'python' in line_lower),
                'insilver' in line_lower
            ]):
                if 'grep' not in line and line.strip():
                    processes.append(line.strip())
        
        # 2. Пошук через pgrep для конкретних patterns
        patterns = ['python.*bot', 'telegram', 'insilver']
        for pattern in patterns:
            try:
                pgrep_result = subprocess.run(['pgrep', '-f', pattern], 
                                            capture_output=True, text=True)
                if pgrep_result.stdout:
                    pids = pgrep_result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            # Отримати детальну інформацію про процес
                            ps_detail = subprocess.run(['ps', '-p', pid, '-o', 'pid,user,command'], 
                                                     capture_output=True, text=True)
                            if ps_detail.returncode == 0:
                                detail_lines = ps_detail.stdout.strip().split('\n')[1:]  # Skip header
                                for detail in detail_lines:
                                    if detail.strip() and detail not in [p.split()[1:] for p in processes]:
                                        processes.append(detail.strip())
            except:
                pass
        
        # 3. Перевірити systemd сервіси
        systemctl_result = subprocess.run(['systemctl', 'list-units', '--type=service', '--state=running'], 
                                        capture_output=True, text=True)
        
        relevant_services = []
        for line in systemctl_result.stdout.split('\n'):
            if any(keyword in line.lower() for keyword in ['telegram', 'insilver', 'bot']):
                relevant_services.append(line.strip())
        
        # Вивести результати
        print(f"\n📊 РЕЗУЛЬТАТИ ПОШУКУ:")
        print("="*60)
        
        if processes:
            print(f"\n✅ Знайдено {len(processes)} процесів:")
            for i, proc in enumerate(processes, 1):
                parts = proc.split()
                if len(parts) >= 2:
                    print(f"{i}. PID: {parts[1]} | User: {parts[0]} | Command: {' '.join(parts[10:])}")
                else:
                    print(f"{i}. {proc}")
                    
            if len(processes) > 1:
                print(f"\n⚠️  УВАГА: Знайдено {len(processes)} процесів!")
                print("   Це може бути причиною 'terminated by other getUpdates request'")
                print("\n🔧 ДЛЯ ВИРІШЕННЯ:")
                print("   1. Визначте який процес потрібен")
                print("   2. Зупиніть зайві: sudo kill PID")
                print("   3. Або зупиніть сервіс: sudo systemctl stop SERVICE_NAME")
        else:
            print("❌ Не знайдено процесів з цим токеном")
            print("   Можливо бот не запущений або використовує інший токен")
        
        if relevant_services:
            print(f"\n🔧 SYSTEMD СЕРВІСИ ({len(relevant_services)}):")
            for service in relevant_services:
                print(f"   {service}")
        
        return len(processes)
        
    except Exception as e:
        print(f"❌ Помилка пошуку: {e}")
        return -1

def kill_conflicts(token, exclude_pid=None):
    """Автоматично зупинити конфліктні процеси"""
    print("\n🚨 РЕЖИМ AUTO-KILL (НЕБЕЗПЕЧНО!)")
    
    # Знайти процеси
    bot_id = token.split(':')[0]
    
    try:
        ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        target_pids = []
        for line in ps_result.stdout.split('\n'):
            if (bot_id in line or 'bot.py' in line.lower()) and 'grep' not in line:
                parts = line.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    if exclude_pid and pid != exclude_pid:
                        target_pids.append((pid, ' '.join(parts[10:])))
        
        if target_pids:
            print(f"🎯 Знайдено {len(target_pids)} процесів для зупинки:")
            for pid, cmd in target_pids:
                print(f"   PID {pid}: {cmd}")
            
            confirm = input("\n⚠️  Підтвердіть зупинку (yes/no): ")
            if confirm.lower() == 'yes':
                for pid, cmd in target_pids:
                    try:
                        subprocess.run(['kill', pid], check=True)
                        print(f"✅ Зупинено PID {pid}")
                    except subprocess.CalledProcessError:
                        print(f"❌ Не вдалося зупинити PID {pid}")
            else:
                print("❌ Відмінено користувачем")
        else:
            print("✅ Конфліктних процесів не знайдено")
            
    except Exception as e:
        print(f"❌ Помилка auto-kill: {e}")

def main():
    parser = argparse.ArgumentParser(description='Find Telegram token conflicts')
    parser.add_argument('token', help='Telegram bot token to search for')
    parser.add_argument('--kill', action='store_true', help='Auto-kill conflicting processes (DANGEROUS)')
    parser.add_argument('--exclude-pid', help='PID to exclude from kill (keep running)')
    
    args = parser.parse_args()
    
    if not args.token or len(args.token) < 20:
        print("❌ Некоректний токен")
        return 1
    
    process_count = find_token_processes(args.token)
    
    if args.kill and process_count > 1:
        kill_conflicts(args.token, args.exclude_pid)
    
    return 0 if process_count <= 1 else 1

if __name__ == "__main__":
    exit(main())
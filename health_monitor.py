#!/usr/bin/env python3
"""Health monitor для InSilver bot + Pi system"""
import os
import subprocess
import sys
from datetime import datetime
import requests
import psutil

def check_bot_service():
    """Перевірити systemd статус"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'insilver-v3'], 
                               capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip()
    except:
        return False, "error"

def check_system_resources():
    """Перевірити системні ресурси"""
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu,
            'memory_percent': memory.percent,
            'memory_available_mb': memory.available / 1024 / 1024,
            'disk_percent': disk.percent
        }
    except:
        return None

def send_alert(message):
    """Надіслати alert (поки що в лог)"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    alert = f"[{timestamp}] 🚨 ALERT: {message}"
    
    # Логувати alert
    with open('/home/sashok/.openclaw/workspace/health_alerts.log', 'a') as f:
        f.write(alert + '\n')
    
    # Вивести в stdout для systemd journal
    print(alert)
    
    # TODO: Додати Telegram/email notification

def main():
    """Головна перевірка"""
    issues = []
    
    # Перевірка бота
    bot_ok, bot_status = check_bot_service()
    if not bot_ok:
        issues.append(f"InSilver bot не працює: {bot_status}")
    
    # Перевірка ресурсів
    resources = check_system_resources()
    if resources:
        if resources['cpu_percent'] > 80:
            issues.append(f"Високий CPU: {resources['cpu_percent']:.1f}%")
        
        if resources['memory_percent'] > 85:
            issues.append(f"Мало RAM: {resources['memory_percent']:.1f}% використано")
        
        if resources['disk_percent'] > 90:
            issues.append(f"Мало місця: {resources['disk_percent']:.1f}% диск")
    
    # Відправити alerts
    for issue in issues:
        send_alert(issue)
    
    # Success log
    if not issues:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] ✅ Health check OK")
    
    return len(issues) == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

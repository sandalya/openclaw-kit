#!/usr/bin/env python3
"""
Повна діагностика Telegram бота
Автоматично знаходить і звітує про всі типові проблеми
"""
import os
import sys
import json
import subprocess
import requests
import argparse
import re
from pathlib import Path

class TelegramDiagnostic:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.issues = []
        self.warnings = []
        self.suggestions = []
        
    def log_issue(self, issue):
        self.issues.append(f"❌ {issue}")
        print(f"❌ {issue}")
        
    def log_warning(self, warning):
        self.warnings.append(f"⚠️ {warning}")
        print(f"⚠️ {warning}")
        
    def log_suggestion(self, suggestion):
        self.suggestions.append(f"💡 {suggestion}")
        print(f"💡 {suggestion}")
        
    def log_ok(self, message):
        print(f"✅ {message}")

    def test_token_validity(self):
        """Перевірити чи токен валідний"""
        print("\n=== ПЕРЕВІРКА ТОКЕНА ===")
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if response.status_code == 200:
                bot_info = response.json()['result']
                self.log_ok(f"Токен валідний. Бот: {bot_info['first_name']} (@{bot_info.get('username', 'N/A')})")
                return True
            else:
                self.log_issue(f"Токен невалідний: {response.status_code}")
                return False
        except Exception as e:
            self.log_issue(f"Помилка з'єднання з Telegram API: {e}")
            return False

    def check_webhook_status(self):
        """Перевірити webhook стан"""
        print("\n=== ПЕРЕВІРКА WEBHOOK ===")
        try:
            response = requests.get(f"{self.base_url}/getWebhookInfo", timeout=10)
            if response.status_code == 200:
                webhook_info = response.json()['result']
                if webhook_info.get('url'):
                    self.log_warning(f"Webhook налаштований: {webhook_info['url']}")
                    self.log_warning("Webhook блокує polling! Це може бути причиною конфлікту")
                    self.log_suggestion("Очистіть webhook: curl -X POST \"https://api.telegram.org/bot$TOKEN/deleteWebhook\"")
                    return 'webhook'
                else:
                    self.log_ok("Webhook відсутній - polling може працювати")
                    return 'polling'
            else:
                self.log_warning("Не вдалося перевірити webhook статус")
                return 'unknown'
        except Exception as e:
            self.log_warning(f"Помилка перевірки webhook: {e}")
            return 'unknown'

    def find_processes_with_token(self):
        """Знайти всі процеси що використовують токен"""
        print("\n=== ПОШУК ПРОЦЕСІВ З ТОКЕНОМ ===")
        token_part = self.token[:20]  # Перші 20 символів для безпеки
        
        try:
            # Пошук в процесах
            ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            processes_with_token = []
            
            for line in ps_result.stdout.split('\n'):
                if token_part in line or 'bot.py' in line or 'telegram' in line.lower():
                    if 'grep' not in line and line.strip():
                        processes_with_token.append(line.strip())
            
            if len(processes_with_token) > 1:
                self.log_issue(f"Знайдено {len(processes_with_token)} процесів що можуть використовувати токен:")
                for proc in processes_with_token:
                    print(f"  {proc}")
                self.log_suggestion("Зупиніть зайві процеси: kill PID або systemctl stop")
                return processes_with_token
            elif len(processes_with_token) == 1:
                self.log_ok(f"Знайдено 1 процес: {processes_with_token[0]}")
                return processes_with_token
            else:
                self.log_warning("Не знайдено активних процесів з токеном")
                return []
                
        except Exception as e:
            self.log_warning(f"Помилка пошуку процесів: {e}")
            return []

    def check_systemd_services(self):
        """Перевірити systemd сервіси"""
        print("\n=== ПЕРЕВІРКА SYSTEMD СЕРВІСІВ ===")
        try:
            # Шукаємо сервіси зі словом 'telegram' або 'insilver' або 'bot'
            systemctl_result = subprocess.run(['systemctl', 'list-units', '--type=service'], 
                                            capture_output=True, text=True)
            
            relevant_services = []
            for line in systemctl_result.stdout.split('\n'):
                if any(keyword in line.lower() for keyword in ['telegram', 'insilver', 'bot']):
                    relevant_services.append(line.strip())
            
            if relevant_services:
                self.log_ok(f"Знайдено {len(relevant_services)} сервісів:")
                for service in relevant_services:
                    print(f"  {service}")
            else:
                self.log_ok("Не знайдено відповідних systemd сервісів")
                
            return relevant_services
            
        except Exception as e:
            self.log_warning(f"Помилка перевірки systemd: {e}")
            return []

    def check_port_conflicts(self):
        """Перевірити конфлікти портів"""
        print("\n=== ПЕРЕВІРКА ПОРТІВ ===")
        common_ports = [8080, 8443, 443, 80]
        
        for port in common_ports:
            try:
                netstat_result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
                if f":{port} " in netstat_result.stdout:
                    processes = [line for line in netstat_result.stdout.split('\n') 
                               if f":{port} " in line]
                    if processes:
                        self.log_warning(f"Порт {port} зайнятий: {processes[0]}")
                        
            except Exception:
                pass  # netstat може бути відсутній

    def check_env_files(self):
        """Перевірити .env файли на дублікати"""
        print("\n=== ПЕРЕВІРКА .ENV ФАЙЛІВ ===")
        env_files = []
        
        # Шукаємо .env файли в поточній директорії та підпапках
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file == '.env':
                    env_files.append(os.path.join(root, file))
        
        if len(env_files) > 1:
            self.log_warning(f"Знайдено {len(env_files)} .env файлів:")
            for env_file in env_files:
                print(f"  {env_file}")
            self.log_suggestion("Перевірте чи не використовується один токен в декількох місцях")
        elif len(env_files) == 1:
            self.log_ok(f"Знайдено 1 .env файл: {env_files[0]}")
        else:
            self.log_warning("Не знайдено .env файлів")

    def test_polling(self):
        """Спробувати зробити test polling запит"""
        print("\n=== ТЕСТ POLLING ===")
        try:
            response = requests.get(f"{self.base_url}/getUpdates", 
                                  params={'timeout': 5, 'limit': 1}, 
                                  timeout=10)
            if response.status_code == 200:
                self.log_ok("Polling працює - токен може отримувати повідомлення")
                return True
            elif response.status_code == 409:  # Conflict
                self.log_issue("КОНФЛІКТ! Інший процес використовує getUpdates")
                self.log_suggestion("Знайдіть і зупиніть конфліктний процес")
                return False
            else:
                self.log_warning(f"Unexpected polling response: {response.status_code}")
                return False
        except Exception as e:
            self.log_warning(f"Помилка тесту polling: {e}")
            return False

    def generate_summary(self):
        """Створити підсумок діагностики"""
        print("\n" + "="*50)
        print("🔍 ПІДСУМОК ДІАГНОСТИКИ")
        print("="*50)
        
        if self.issues:
            print("\n❌ КРИТИЧНІ ПРОБЛЕМИ:")
            for issue in self.issues:
                print(f"  {issue}")
                
        if self.warnings:
            print("\n⚠️ ПОПЕРЕДЖЕННЯ:")
            for warning in self.warnings:
                print(f"  {warning}")
                
        if self.suggestions:
            print("\n💡 РЕКОМЕНДАЦІЇ:")
            for suggestion in self.suggestions:
                print(f"  {suggestion}")
                
        if not self.issues and not self.warnings:
            print("\n✅ Проблем не виявлено! Бот повинен працювати нормально.")
        
        print("\n" + "="*50)

def main():
    parser = argparse.ArgumentParser(description='Telegram Bot Full Diagnostic')
    parser.add_argument('--token', required=True, help='Telegram bot token')
    parser.add_argument('--check-processes', action='store_true', help='Check for process conflicts')
    parser.add_argument('--check-webhooks', action='store_true', help='Check webhook status')
    parser.add_argument('--fix-conflicts', action='store_true', help='Try to auto-fix conflicts')
    
    args = parser.parse_args()
    
    print("🐱 TELEGRAM BOT DIAGNOSTIC TOOL")
    print("=" * 50)
    
    diagnostic = TelegramDiagnostic(args.token)
    
    # Базова перевірка токена
    if not diagnostic.test_token_validity():
        print("\n❌ Токен невалідний - решта перевірок неможлива")
        return 1
    
    # Основні перевірки
    diagnostic.check_webhook_status()
    
    if args.check_processes:
        diagnostic.find_processes_with_token()
        diagnostic.check_systemd_services()
        diagnostic.check_env_files()
        diagnostic.check_port_conflicts()
    
    if args.check_webhooks:
        diagnostic.test_polling()
    
    diagnostic.generate_summary()
    
    # Повертаємо код помилки якщо є критичні проблеми
    return 1 if diagnostic.issues else 0

if __name__ == "__main__":
    exit(main())
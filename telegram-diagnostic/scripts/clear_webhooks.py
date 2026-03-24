#!/usr/bin/env python3
"""
Очистити webhook для Telegram бота
"""
import requests
import sys
import argparse

def clear_webhook(token):
    """Очистити webhook для бота"""
    
    base_url = f"https://api.telegram.org/bot{token}"
    
    print("🔍 Перевіряємо поточний webhook...")
    
    # Перевірити поточний webhook
    try:
        response = requests.get(f"{base_url}/getWebhookInfo", timeout=10)
        if response.status_code == 200:
            webhook_info = response.json()['result']
            
            if webhook_info.get('url'):
                print(f"⚠️  Знайдено webhook: {webhook_info['url']}")
                print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
                
                if webhook_info.get('last_error_message'):
                    print(f"   Остання помилка: {webhook_info['last_error_message']}")
                
                # Очистити webhook
                print("\n🧹 Очищаємо webhook...")
                clear_response = requests.post(f"{base_url}/deleteWebhook", timeout=10)
                
                if clear_response.status_code == 200:
                    result = clear_response.json()
                    if result.get('ok'):
                        print("✅ Webhook успішно очищено!")
                        print("🔄 Тепер бот може використовувати polling")
                        
                        # Додатково - очистити pending updates
                        print("\n🧹 Очищаємо pending updates...")
                        updates_response = requests.get(f"{base_url}/getUpdates", 
                                                       params={'offset': -1}, 
                                                       timeout=10)
                        if updates_response.status_code == 200:
                            print("✅ Pending updates очищено")
                        else:
                            print("⚠️  Не вдалося очистити pending updates")
                        
                        return True
                    else:
                        print(f"❌ Помилка очищення: {result.get('description', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ HTTP помилка: {clear_response.status_code}")
                    return False
            else:
                print("✅ Webhook відсутній - очищення не потрібно")
                return True
        else:
            print(f"❌ Не вдалося перевірити webhook: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def set_webhook(token, url):
    """Встановити webhook (опціонально)"""
    
    base_url = f"https://api.telegram.org/bot{token}"
    
    print(f"🔗 Встановлюємо webhook: {url}")
    
    try:
        response = requests.post(f"{base_url}/setWebhook", 
                               json={'url': url}, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook успішно встановлено!")
                return True
            else:
                print(f"❌ Помилка встановлення: {result.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP помилка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def test_token(token):
    """Швидкий тест токена"""
    base_url = f"https://api.telegram.org/bot{token}"
    
    try:
        response = requests.get(f"{base_url}/getMe", timeout=10)
        if response.status_code == 200:
            bot_info = response.json()['result']
            print(f"✅ Токен валідний. Бот: {bot_info['first_name']} (@{bot_info.get('username', 'N/A')})")
            return True
        else:
            print(f"❌ Токен невалідний: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Помилка перевірки токена: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Telegram Webhook Management')
    parser.add_argument('token', help='Telegram bot token')
    parser.add_argument('--set-webhook', help='Set webhook URL instead of clearing')
    parser.add_argument('--test-only', action='store_true', help='Only test token validity')
    
    args = parser.parse_args()
    
    if not args.token or len(args.token) < 30:
        print("❌ Некоректний токен")
        return 1
    
    print("🤖 TELEGRAM WEBHOOK MANAGER")
    print("=" * 50)
    
    # Спочатку тест токена
    if not test_token(args.token):
        return 1
    
    if args.test_only:
        return 0
    
    if args.set_webhook:
        success = set_webhook(args.token, args.set_webhook)
    else:
        success = clear_webhook(args.token)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
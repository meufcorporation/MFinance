#!/usr/bin/env python3
"""
Тест аутентифікації Keycloak для MFinance
"""

import requests
import json

# Keycloak configuration
KEYCLOAK_URL = "http://localhost:8080"
REALM_NAME = "mfinance"
CLIENT_ID = "mfinance-web"
CLIENT_SECRET = "mfinance-secret-key-2024"
TEST_USER = "test@mfinance.com"
TEST_PASSWORD = "test123"

def test_keycloak_auth():
    """Тестування аутентифікації через Keycloak"""
    print("🔐 Тестування аутентифікації Keycloak...")
    
    # 1. Отримати токен
    token_url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username": TEST_USER,
        "password": TEST_PASSWORD
    }
    
    print(f"📡 Запит до: {token_url}")
    print(f"👤 Користувач: {TEST_USER}")
    
    try:
        response = requests.post(token_url, data=data)
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Токен отримано успішно!")
            print(f"🔑 Access Token: {token_data.get('access_token', '')[:50]}...")
            print(f"⏰ Expires In: {token_data.get('expires_in', 'N/A')} секунд")
            
            # 2. Отримати інформацію про користувача
            userinfo_url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/userinfo"
            headers = {'Authorization': f'Bearer {token_data["access_token"]}'}
            
            userinfo_response = requests.get(userinfo_url, headers=headers)
            print(f"👤 User Info статус: {userinfo_response.status_code}")
            
            if userinfo_response.status_code == 200:
                user_info = userinfo_response.json()
                print("✅ Інформація про користувача отримана!")
                print(f"📧 Email: {user_info.get('email', 'N/A')}")
                print(f"👤 Name: {user_info.get('name', 'N/A')}")
                print(f"🆔 Sub: {user_info.get('sub', 'N/A')}")
            else:
                print(f"❌ Помилка отримання user info: {userinfo_response.text}")
                
        else:
            print(f"❌ Помилка аутентифікації: {response.text}")
            
    except Exception as e:
        print(f"❌ Помилка: {e}")

def test_frontend_auth():
    """Тестування аутентифікації через frontend"""
    print("\n🌐 Тестування frontend аутентифікації...")
    
    # Тест credentials аутентифікації
    print("🔐 Тестування credentials аутентифікації...")
    
    try:
        # Перевірити сторінку входу
        login_response = requests.get("http://localhost:3000/login")
        print(f"📄 Сторінка входу: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Сторінка входу доступна")
        else:
            print("❌ Сторінка входу недоступна")
            
    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    print("🚀 Починаю тестування аутентифікації MFinance...")
    print("="*60)
    
    test_keycloak_auth()
    test_frontend_auth()
    
    print("="*60)
    print("✅ Тестування завершено!")

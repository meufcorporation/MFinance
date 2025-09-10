#!/usr/bin/env python3
"""
Перевірка користувача в Keycloak
"""

import requests
import json

# Keycloak configuration
KEYCLOAK_URL = "http://localhost:8080"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"
REALM_NAME = "mfinance"

def get_admin_token():
    """Отримати admin token"""
    token_url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "grant_type": "password",
        "client_id": "admin-cli"
    }
    
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Помилка отримання admin token: {response.status_code}")
        print(response.text)
        return None

def check_users(admin_token):
    """Перевірити користувачів в realm"""
    headers = {'Authorization': f'Bearer {admin_token}'}
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        users = response.json()
        print(f"👥 Знайдено {len(users)} користувачів:")
        for user in users:
            print(f"  - {user.get('username', 'N/A')} ({user.get('email', 'N/A')}) - {user.get('enabled', False)}")
        return users
    else:
        print(f"❌ Помилка отримання користувачів: {response.status_code}")
        print(response.text)
        return []

def create_test_user(admin_token):
    """Створити тестового користувача"""
    headers = {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }
    
    user_data = {
        "username": "test@mfinance.com",
        "email": "test@mfinance.com",
        "firstName": "Test",
        "lastName": "User",
        "enabled": True,
        "emailVerified": True,
        "credentials": [{
            "type": "password",
            "value": "test123",
            "temporary": False
        }]
    }
    
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users"
    response = requests.post(url, json=user_data, headers=headers)
    
    if response.status_code == 201:
        print("✅ Тестовий користувач створено")
        return True
    elif response.status_code == 409:
        print("⚠️ Користувач вже існує")
        return True
    else:
        print(f"❌ Помилка створення користувача: {response.status_code}")
        print(response.text)
        return False

def reset_user_password(admin_token, user_id):
    """Скинути пароль користувача"""
    headers = {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }
    
    password_data = {
        "type": "password",
        "value": "test123",
        "temporary": False
    }
    
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{user_id}/reset-password"
    response = requests.put(url, json=password_data, headers=headers)
    
    if response.status_code == 204:
        print("✅ Пароль користувача скинуто")
        return True
    else:
        print(f"❌ Помилка скидання пароля: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    print("🔍 Перевірка користувачів Keycloak...")
    print("="*50)
    
    # Отримати admin token
    admin_token = get_admin_token()
    if not admin_token:
        exit(1)
    
    print("✅ Admin token отримано")
    
    # Перевірити користувачів
    users = check_users(admin_token)
    
    # Знайти тестового користувача
    test_user = None
    for user in users:
        if user.get('email') == 'test@mfinance.com':
            test_user = user
            break
    
    if test_user:
        print(f"👤 Тестовий користувач знайдено: {test_user['username']}")
        print(f"📧 Email: {test_user.get('email')}")
        print(f"✅ Enabled: {test_user.get('enabled')}")
        
        # Скинути пароль
        if reset_user_password(admin_token, test_user['id']):
            print("✅ Пароль скинуто на 'test123'")
    else:
        print("❌ Тестовий користувач не знайдено, створюю...")
        create_test_user(admin_token)
    
    print("="*50)
    print("✅ Перевірка завершена!")

#!/usr/bin/env python3
"""
Keycloak Setup Script for MFinance
Автоматично налаштовує realm, клієнтів та користувачів для MFinance
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Keycloak configuration
KEYCLOAK_URL = "http://localhost:8080"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"
REALM_NAME = "mfinance"
CLIENT_ID = "mfinance-web"
CLIENT_SECRET = "mfinance-secret-key-2024"

class KeycloakSetup:
    def __init__(self):
        self.base_url = KEYCLOAK_URL
        self.admin_token = None
        self.realm_url = f"{self.base_url}/admin/realms"
        
    def get_admin_token(self) -> str:
        """Отримати admin token для Keycloak"""
        print("🔐 Отримую admin token...")
        
        token_url = f"{self.base_url}/realms/master/protocol/openid-connect/token"
        data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD,
            "grant_type": "password",
            "client_id": "admin-cli"
        }
        
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.admin_token = token_data["access_token"]
            print("✅ Admin token отримано")
            return self.admin_token
        else:
            print(f"❌ Помилка отримання token: {response.status_code}")
            print(response.text)
            sys.exit(1)
    
    def create_realm(self) -> bool:
        """Створити realm для MFinance"""
        print(f"🏗️ Створюю realm '{REALM_NAME}'...")
        
        realm_config = {
            "realm": REALM_NAME,
            "displayName": "MFinance",
            "displayNameHtml": "<div class=\"kc-logo-text\"><span>MFinance</span></div>",
            "enabled": True,
            "sslRequired": "external",
            "registrationAllowed": True,
            "registrationEmailAsUsername": True,
            "rememberMe": True,
            "verifyEmail": True,
            "loginWithEmailAllowed": True,
            "duplicateEmailsAllowed": False,
            "resetPasswordAllowed": True,
            "editUsernameAllowed": False,
            "bruteForceProtected": True,
            "permanentLockout": False,
            "maxFailureWaitSeconds": 900,
            "minimumQuickLoginWaitSeconds": 60,
            "waitIncrementSeconds": 60,
            "quickLoginCheckMilliSeconds": 1000,
            "maxDeltaTimeSeconds": 43200,
            "failureFactor": 30,
            "defaultSignatureAlgorithm": "RS256",
            "revokeRefreshToken": False,
            "refreshTokenMaxReuse": 0,
            "accessTokenLifespan": 300,
            "accessTokenLifespanForImplicitFlow": 900,
            "ssoSessionIdleTimeout": 1800,
            "ssoSessionMaxLifespan": 36000,
            "ssoSessionIdleTimeoutRememberMe": 0,
            "ssoSessionMaxLifespanRememberMe": 0,
            "offlineSessionIdleTimeout": 2592000,
            "offlineSessionMaxLifespanEnabled": False,
            "offlineSessionMaxLifespan": 5184000,
            "clientSessionIdleTimeout": 0,
            "clientSessionMaxLifespan": 0,
            "clientOfflineSessionIdleTimeout": 0,
            "clientOfflineSessionMaxLifespan": 0,
            "accessCodeLifespan": 60,
            "accessCodeLifespanUserAction": 300,
            "accessCodeLifespanLogin": 1800,
            "actionTokenGeneratedByAdminLifespan": 43200,
            "actionTokenGeneratedByUserLifespan": 300,
            "oauth2DeviceCodeLifespan": 600,
            "oauth2DevicePollingInterval": 5,
            "internationalizationEnabled": True,
            "supportedLocales": ["en", "uk"],
            "defaultLocale": "uk",
            "passwordPolicy": "hashIterations(27500)",
            "otpPolicyType": "totp",
            "otpPolicyAlgorithm": "HmacSHA1",
            "otpPolicyInitialCounter": 0,
            "otpPolicyDigits": 6,
            "otpPolicyLookAheadWindow": 1,
            "otpPolicyPeriod": 30,
            "otpSupportedApplications": ["FreeOTP", "Google Authenticator"],
            "webAuthnPolicyRpEntityName": "MFinance",
            "webAuthnPolicySignatureAlgorithms": ["ES256"],
            "webAuthnPolicyRpId": "",
            "webAuthnPolicyAttestationConveyancePreference": "not specified",
            "webAuthnPolicyAuthenticatorAttachment": "not specified",
            "webAuthnPolicyRequireResidentKey": "not specified",
            "webAuthnPolicyUserVerificationRequirement": "not specified",
            "webAuthnPolicyCreateTimeout": 0,
            "webAuthnPolicyAvoidSameAuthenticator": False,
            "webAuthnPolicyAcceptableAaguids": [],
            "webAuthnPolicyPasswordlessRpEntityName": "MFinance",
            "webAuthnPolicyPasswordlessSignatureAlgorithms": ["ES256"],
            "webAuthnPolicyPasswordlessRpId": "",
            "webAuthnPolicyPasswordlessAttestationConveyancePreference": "not specified",
            "webAuthnPolicyPasswordlessAuthenticatorAttachment": "not specified",
            "webAuthnPolicyPasswordlessRequireResidentKey": "not specified",
            "webAuthnPolicyPasswordlessUserVerificationRequirement": "not specified",
            "webAuthnPolicyPasswordlessCreateTimeout": 0,
            "webAuthnPolicyPasswordlessAvoidSameAuthenticator": False,
            "webAuthnPolicyPasswordlessAcceptableAaguids": [],
            "browserSecurityHeaders": {
                "contentSecurityPolicyReportOnly": "",
                "xContentTypeOptions": "nosniff",
                "xRobotsTag": "none",
                "xFrameOptions": "SAMEORIGIN",
                "contentSecurityPolicy": "frame-src 'self'; frame-ancestors 'self'; object-src 'none';",
                "xXSSProtection": "1; mode=block",
                "strictTransportSecurity": "max-age=31536000; includeSubDomains"
            },
            "smtpServer": {},
            "loginTheme": "keycloak",
            "accountTheme": "keycloak",
            "adminTheme": "keycloak",
            "emailTheme": "keycloak",
            "eventsEnabled": False,
            "eventsListeners": ["jboss-logging"],
            "enabledEventTypes": [],
            "adminEventsEnabled": False,
            "adminEventsDetailsEnabled": False,
            "attributes": {
                "frontendUrl": "http://localhost:3000",
                "adminUrl": "http://localhost:3000"
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
        
        # Перевірити чи realm вже існує
        check_response = requests.get(f"{self.realm_url}/{REALM_NAME}", headers=headers)
        if check_response.status_code == 200:
            print(f"✅ Realm '{REALM_NAME}' вже існує")
            return True
        
        # Створити realm
        response = requests.post(self.realm_url, json=realm_config, headers=headers)
        if response.status_code == 201:
            print(f"✅ Realm '{REALM_NAME}' створено")
            return True
        else:
            print(f"❌ Помилка створення realm: {response.status_code}")
            print(response.text)
            return False
    
    def create_client(self) -> bool:
        """Створити клієнт для MFinance Web"""
        print(f"🔧 Створюю клієнт '{CLIENT_ID}'...")
        
        headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
        
        # Перевірити чи клієнт вже існує
        clients_response = requests.get(
            f"{self.realm_url}/{REALM_NAME}/clients?clientId={CLIENT_ID}",
            headers=headers
        )
        
        if clients_response.status_code == 200:
            clients = clients_response.json()
            if clients:
                print(f"✅ Клієнт '{CLIENT_ID}' вже існує")
                return True
        
        client_config = {
            "clientId": CLIENT_ID,
            "name": "MFinance Web Application",
            "description": "MFinance Web Cabinet Application",
            "enabled": True,
            "clientAuthenticatorType": "client-secret",
            "secret": CLIENT_SECRET,
            "redirectUris": [
                "http://localhost:3000/api/auth/callback/keycloak",
                "http://localhost:3000/*"
            ],
            "webOrigins": [
                "http://localhost:3000",
                "http://localhost:3000/*"
            ],
            "protocol": "openid-connect",
            "publicClient": False,
            "serviceAccountsEnabled": True,
            "authorizationServicesEnabled": False,
            "standardFlowEnabled": True,
            "implicitFlowEnabled": False,
            "directAccessGrantsEnabled": True,
            "frontchannelLogout": True,
            "attributes": {
                "saml.assertion.signature": "false",
                "saml.force.post.binding": "false",
                "saml.multivalued.roles": "false",
                "saml.encrypt": "false",
                "saml.server.signature": "false",
                "saml.server.signature.keyinfo.ext": "false",
                "exclude.session.state.from.auth.response": "false",
                "saml_force_name_id_format": "false",
                "saml.client.signature": "false",
                "tls.client.certificate.bound.access.tokens": "false",
                "saml.authnstatement": "false",
                "display.on.consent.screen": "false",
                "saml.onetimeuse.condition": "false"
            },
            "authenticationFlowBindingOverrides": {},
            "fullScopeAllowed": True,
            "nodeReRegistrationTimeout": -1,
            "defaultClientScopes": [
                "web-origins",
                "role_list",
                "profile",
                "roles",
                "email"
            ],
            "optionalClientScopes": [
                "address",
                "phone",
                "offline_access",
                "microprofile-jwt"
            ]
        }
        
        response = requests.post(
            f"{self.realm_url}/{REALM_NAME}/clients",
            json=client_config,
            headers=headers
        )
        
        if response.status_code == 201:
            print(f"✅ Клієнт '{CLIENT_ID}' створено")
            return True
        else:
            print(f"❌ Помилка створення клієнта: {response.status_code}")
            print(response.text)
            return False
    
    def create_roles(self) -> bool:
        """Створити ролі для MFinance"""
        print("👥 Створюю ролі...")
        
        roles = [
            {"name": "user", "description": "Звичайний користувач"},
            {"name": "admin", "description": "Адміністратор системи"},
            {"name": "accountant", "description": "Бухгалтер"},
            {"name": "fop", "description": "Фізична особа-підприємець"}
        ]
        
        headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
        
        for role in roles:
            response = requests.post(
                f"{self.realm_url}/{REALM_NAME}/roles",
                json=role,
                headers=headers
            )
            
            if response.status_code == 201:
                print(f"✅ Роль '{role['name']}' створено")
            else:
                print(f"❌ Помилка створення ролі '{role['name']}': {response.status_code}")
        
        return True
    
    def create_test_user(self) -> bool:
        """Створити тестового користувача"""
        print("👤 Створюю тестового користувача...")
        
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
        
        headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
        
        # Створити користувача
        response = requests.post(
            f"{self.realm_url}/{REALM_NAME}/users",
            json=user_data,
            headers=headers
        )
        
        if response.status_code == 201:
            print("✅ Тестовий користувач створено")
            
            # Отримати ID користувача
            users_response = requests.get(
                f"{self.realm_url}/{REALM_NAME}/users?username=test@mfinance.com",
                headers=headers
            )
            
            if users_response.status_code == 200:
                users = users_response.json()
                if users:
                    user_id = users[0]["id"]
                    
                    # Призначити ролі
                    role_data = {"name": "user"}
                    role_response = requests.post(
                        f"{self.realm_url}/{REALM_NAME}/users/{user_id}/role-mappings/realm",
                        json=[role_data],
                        headers=headers
                    )
                    
                    if role_response.status_code == 204:
                        print("✅ Роль 'user' призначено тестовому користувачу")
                    
                    return True
        else:
            print(f"❌ Помилка створення користувача: {response.status_code}")
            print(response.text)
            return False
    
    def setup_complete(self):
        """Вивести інформацію про завершення налаштування"""
        print("\n" + "="*60)
        print("🎉 KEYCLOAK НАЛАШТУВАННЯ ЗАВЕРШЕНО!")
        print("="*60)
        print(f"🌐 Keycloak Admin Console: {self.base_url}/admin")
        print(f"🔑 Realm: {REALM_NAME}")
        print(f"📱 Client ID: {CLIENT_ID}")
        print(f"🔐 Client Secret: {CLIENT_SECRET}")
        print(f"👤 Test User: test@mfinance.com / test123")
        print("\n📋 Наступні кроки:")
        print("1. Перевірте налаштування в Keycloak Admin Console")
        print("2. Налаштуйте Django для роботи з Keycloak")
        print("3. Налаштуйте NextAuth.js з Keycloak провайдером")
        print("="*60)

def main():
    print("🚀 Починаю налаштування Keycloak для MFinance...")
    
    setup = KeycloakSetup()
    
    # Отримати admin token
    setup.get_admin_token()
    
    # Створити realm
    if not setup.create_realm():
        print("❌ Не вдалося створити realm")
        sys.exit(1)
    
    # Зачекати трохи для ініціалізації realm
    time.sleep(2)
    
    # Створити клієнт
    if not setup.create_client():
        print("❌ Не вдалося створити клієнт")
        sys.exit(1)
    
    # Створити ролі
    setup.create_roles()
    
    # Створити тестового користувача
    setup.create_test_user()
    
    # Вивести інформацію про завершення
    setup.setup_complete()

if __name__ == "__main__":
    main()

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import login, logout
from django.utils import timezone
from django.conf import settings
import requests
import jwt
from datetime import datetime, timedelta

from .models import User, UserProfile, Role, UserRole, UserSession, AuditLog, KeycloakConfig
from .serializers import (
    UserSerializer, UserCreateSerializer, LoginSerializer, 
    RoleSerializer, UserRoleSerializer, UserSessionSerializer,
    AuditLogSerializer, ChangePasswordSerializer, KeycloakTokenSerializer
)


class KeycloakAuthMixin:
    """Mixin для роботи з Keycloak"""
    
    def get_keycloak_config(self):
        """Отримати конфігурацію Keycloak"""
        try:
            return KeycloakConfig.objects.filter(is_active=True).first()
        except:
            return None
    
    def get_keycloak_user_info(self, access_token):
        """Отримати інформацію про користувача з Keycloak"""
        config = self.get_keycloak_config()
        if not config:
            return None
        
        url = f"{config.server_url}/realms/{config.realm_name}/protocol/openid-connect/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error getting user info from Keycloak: {e}")
        
        return None
    
    def create_or_update_user_from_keycloak(self, user_info, access_token):
        """Створити або оновити користувача з даних Keycloak"""
        keycloak_id = user_info.get('sub')
        email = user_info.get('email')
        username = user_info.get('preferred_username', email)
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')
        
        # Створити або оновити користувача
        user, created = User.objects.get_or_create(
            keycloak_id=keycloak_id,
            defaults={
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_verified': True,
                'is_active': True
            }
        )
        
        if not created:
            # Оновити існуючого користувача
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.is_verified = True
            user.save()
        
        # Створити або оновити профіль
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        # Створити сесію
        session_key = f"keycloak_{keycloak_id}_{int(timezone.now().timestamp())}"
        expires_at = timezone.now() + timedelta(hours=1)
        
        UserSession.objects.create(
            user=user,
            session_key=session_key,
            access_token=access_token,
            expires_at=expires_at
        )
        
        return user, created


class KeycloakLoginView(KeycloakAuthMixin, APIView):
    """Вхід через Keycloak"""
    
    def post(self, request):
        """Обробити токен від Keycloak"""
        serializer = KeycloakTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = serializer.validated_data['access_token']
        
        # Отримати інформацію про користувача з Keycloak
        user_info = self.get_keycloak_user_info(access_token)
        if not user_info:
            return Response(
                {'error': 'Не вдалося отримати інформацію про користувача'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Створити або оновити користувача
        user, created = self.create_or_update_user_from_keycloak(user_info, access_token)
        
        # Логувати вхід
        AuditLog.objects.create(
            user=user,
            action='login',
            resource_type='user',
            resource_id=str(user.id),
            description=f'Вхід через Keycloak',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Авторизувати користувача в Django
        login(request, user)
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Успішний вхід через Keycloak',
            'created': created
        })
    
    def get_client_ip(self, request):
        """Отримати IP адресу клієнта"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileView(APIView):
    """Профіль користувача"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Отримати профіль поточного користувача"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Оновити профіль користувача"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Вихід з системи"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Вихід користувача"""
        # Логувати вихід
        AuditLog.objects.create(
            user=request.user,
            action='logout',
            resource_type='user',
            resource_id=str(request.user.id),
            description='Вихід з системи',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Деактивувати сесії
        UserSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
        
        # Вихід з Django
        logout(request)
        
        return Response({'message': 'Успішний вихід з системи'})
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile, Role, UserRole, UserSession, AuditLog


class UserProfileSerializer(serializers.ModelSerializer):
    """Серіалізатор для профілю користувача"""
    
    class Meta:
        model = UserProfile
        fields = [
            'company_name', 'position', 'bio', 'website', 
            'address', 'date_of_birth'
        ]


class UserSerializer(serializers.ModelSerializer):
    """Серіалізатор для користувача"""
    profile = UserProfileSerializer(read_only=True)
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'avatar', 'timezone', 'language', 'is_verified',
            'is_active', 'date_joined', 'last_login', 'profile', 'roles'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_roles(self, obj):
        """Отримати ролі користувача"""
        return [role.role.name for role in obj.user_roles.filter(is_active=True)]


class UserCreateSerializer(serializers.ModelSerializer):
    """Серіалізатор для створення користувача"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        """Валідація паролів"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Паролі не співпадають")
        return attrs
    
    def create(self, validated_data):
        """Створити користувача"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Серіалізатор для входу в систему"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        """Валідація даних входу"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Невірні облікові дані')
            if not user.is_active:
                raise serializers.ValidationError('Обліковий запис деактивовано')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Необхідно вказати email та пароль')
        
        return attrs


class RoleSerializer(serializers.ModelSerializer):
    """Серіалізатор для ролей"""
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions', 'is_active']


class UserRoleSerializer(serializers.ModelSerializer):
    """Серіалізатор для ролей користувача"""
    role = RoleSerializer(read_only=True)
    role_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserRole
        fields = ['id', 'role', 'role_id', 'assigned_at', 'is_active']


class UserSessionSerializer(serializers.ModelSerializer):
    """Серіалізатор для сесій користувача"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'user', 'session_key', 'expires_at', 
            'created_at', 'last_activity', 'ip_address', 'is_active'
        ]
        read_only_fields = ['id', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """Серіалізатор для логів аудиту"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'action', 'resource_type', 'resource_id',
            'description', 'ip_address', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ChangePasswordSerializer(serializers.Serializer):
    """Серіалізатор для зміни пароля"""
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        """Валідація паролів"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Нові паролі не співпадають")
        return attrs
    
    def validate_old_password(self, value):
        """Валідація старого пароля"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Невірний старий пароль")
        return value


class KeycloakTokenSerializer(serializers.Serializer):
    """Серіалізатор для токенів Keycloak"""
    access_token = serializers.CharField()
    refresh_token = serializers.CharField(required=False)
    expires_in = serializers.IntegerField()
    token_type = serializers.CharField(default='Bearer')
    
    def validate(self, attrs):
        """Валідація токенів"""
        if not attrs.get('access_token'):
            raise serializers.ValidationError("Access token обов'язковий")
        return attrs

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone as django_timezone


class User(AbstractUser):
    """
    Розширена модель користувача з додатковими полями для MFinance
    """
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    timezone = models.CharField(max_length=50, default='Europe/Kiev')
    language = models.CharField(max_length=10, default='uk')
    is_verified = models.BooleanField(default=False)
    keycloak_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    # Перевизначити related_name для уникнення конфліктів
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='auth_system_user_set',
        related_query_name='auth_system_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='auth_system_user_set',
        related_query_name='auth_system_user',
    )
    
    class Meta:
        db_table = 'auth_system_user'
        verbose_name = 'Користувач'
        verbose_name_plural = 'Користувачі'


class UserProfile(models.Model):
    """
    Додатковий профіль користувача
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company_name = models.CharField(max_length=200, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'auth_user_profile'
        verbose_name = 'Профіль користувача'
        verbose_name_plural = 'Профілі користувачів'


class Role(models.Model):
    """
    Ролі користувачів в системі
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    permissions = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=django_timezone.now)
    
    class Meta:
        db_table = 'auth_role'
        verbose_name = 'Роль'
        verbose_name_plural = 'Ролі'
    
    def __str__(self):
        return self.name


class UserRole(models.Model):
    """
    Зв'язок користувачів з ролями
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    assigned_at = models.DateTimeField(default=django_timezone.now)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_roles')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'auth_user_role'
        unique_together = ['user', 'role']
        verbose_name = 'Роль користувача'
        verbose_name_plural = 'Ролі користувачів'
    
    def __str__(self):
        return f"{self.user.email} - {self.role.name}"


class UserSession(models.Model):
    """
    Сесії користувачів для відстеження активності
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=100, unique=True)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=django_timezone.now)
    last_activity = models.DateTimeField(default=django_timezone.now)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'auth_user_session'
        verbose_name = 'Сесія користувача'
        verbose_name_plural = 'Сесії користувачів'
    
    def __str__(self):
        return f"{self.user.email} - {self.session_key}"


class AuditLog(models.Model):
    """
    Лог аудиту для відстеження дій користувачів
    """
    ACTION_CHOICES = [
        ('login', 'Вхід в систему'),
        ('logout', 'Вихід з системи'),
        ('create', 'Створення'),
        ('update', 'Оновлення'),
        ('delete', 'Видалення'),
        ('view', 'Перегляд'),
        ('export', 'Експорт'),
        ('import', 'Імпорт'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=django_timezone.now)
    
    class Meta:
        db_table = 'auth_audit_log'
        verbose_name = 'Запис аудиту'
        verbose_name_plural = 'Записи аудиту'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email if self.user else 'System'} - {self.action} - {self.resource_type}"


class KeycloakConfig(models.Model):
    """
    Конфігурація Keycloak для різних середовищ
    """
    name = models.CharField(max_length=100, unique=True)
    server_url = models.URLField()
    realm_name = models.CharField(max_length=100)
    client_id = models.CharField(max_length=100)
    client_secret = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_keycloak_config'
        verbose_name = 'Конфігурація Keycloak'
        verbose_name_plural = 'Конфігурації Keycloak'
    
    def __str__(self):
        return f"{self.name} - {self.realm_name}"
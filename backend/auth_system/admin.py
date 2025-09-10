from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, Role, UserRole, UserSession, AuditLog, KeycloakConfig


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Адміністративний інтерфейс для користувачів"""
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['is_verified', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональна інформація', {'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')}),
        ('Налаштування', {'fields': ('timezone', 'language', 'is_verified')}),
        ('Keycloak', {'fields': ('keycloak_id',)}),
        ('Права доступу', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важливі дати', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Адміністративний інтерфейс для профілів користувачів"""
    list_display = ['user', 'company_name', 'position', 'website']
    list_filter = ['company_name']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'company_name']
    raw_id_fields = ['user']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Адміністративний інтерфейс для ролей"""
    list_display = ['name', 'description', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Адміністративний інтерфейс для ролей користувачів"""
    list_display = ['user', 'role', 'assigned_at', 'assigned_by', 'is_active']
    list_filter = ['role', 'is_active', 'assigned_at']
    search_fields = ['user__email', 'role__name', 'assigned_by__email']
    raw_id_fields = ['user', 'assigned_by']
    ordering = ['-assigned_at']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Адміністративний інтерфейс для сесій користувачів"""
    list_display = ['user', 'session_key', 'expires_at', 'created_at', 'last_activity', 'is_active']
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['user__email', 'session_key', 'ip_address']
    raw_id_fields = ['user']
    ordering = ['-created_at']
    
    readonly_fields = ['session_key', 'access_token', 'created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Адміністративний інтерфейс для логів аудиту"""
    list_display = ['user', 'action', 'resource_type', 'description', 'ip_address', 'created_at']
    list_filter = ['action', 'resource_type', 'created_at']
    search_fields = ['user__email', 'description', 'ip_address']
    raw_id_fields = ['user']
    ordering = ['-created_at']
    
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        """Заборонити створення записів аудиту через адмінку"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Заборонити редагування записів аудиту"""
        return False


@admin.register(KeycloakConfig)
class KeycloakConfigAdmin(admin.ModelAdmin):
    """Адміністративний інтерфейс для конфігурації Keycloak"""
    list_display = ['name', 'server_url', 'realm_name', 'client_id', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'server_url', 'realm_name', 'client_id']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('name', 'is_active')}),
        ('Keycloak налаштування', {'fields': ('server_url', 'realm_name', 'client_id', 'client_secret')}),
        ('Метадані', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at']
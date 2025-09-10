from django.contrib import admin
from django.utils.html import format_html
from .models import (
    PaymentProvider, PaymentMethod, Payment, PaymentSchedule,
    PaymentWebhook, PaymentLog, PaymentTemplate
)


@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'name']
    search_fields = ['name', 'display_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'method_type', 'provider', 'is_default', 
        'is_active', 'auto_pay_enabled', 'created_at'
    ]
    list_filter = ['method_type', 'is_active', 'is_default', 'auto_pay_enabled', 'provider']
    search_fields = ['user__email', 'card_holder', 'iban']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'amount', 'currency', 'status', 
        'payment_type', 'provider', 'created_at'
    ]
    list_filter = ['status', 'payment_type', 'currency', 'provider', 'created_at']
    search_fields = ['user__email', 'description', 'external_payment_id']
    readonly_fields = ['created_at', 'updated_at', 'processed_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('user', 'fop_profile', 'tax_obligation', 'amount', 'currency')
        }),
        ('Платіжна інформація', {
            'fields': ('payment_method', 'provider', 'payment_type', 'description')
        }),
        ('Статус', {
            'fields': ('status', 'created_at', 'updated_at', 'processed_at')
        }),
        ('Зовнішні ID', {
            'fields': ('external_payment_id', 'external_transaction_id'),
            'classes': ('collapse',)
        }),
        ('Додаткова інформація', {
            'fields': ('metadata', 'error_message'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'provider', 'payment_method')


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'frequency', 'is_active', 
        'next_payment_date', 'last_payment_date'
    ]
    list_filter = ['frequency', 'is_active', 'payment_type']
    search_fields = ['name', 'user__email', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'provider', 'event_type', 'is_processed', 
        'created_at', 'processed_at'
    ]
    list_filter = ['provider', 'event_type', 'is_processed', 'created_at']
    search_fields = ['event_type', 'payload']
    readonly_fields = ['created_at', 'processed_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('provider', 'payment')


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'level', 'message', 'created_at']
    list_filter = ['level', 'created_at']
    search_fields = ['message', 'payment__id']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment')


@admin.register(PaymentTemplate)
class PaymentTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'payment_type', 'amount', 
        'is_active', 'is_public', 'created_at'
    ]
    list_filter = ['payment_type', 'is_active', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
from django.contrib import admin
from .models import Bank, BankAccount, BankToken, BankTransaction, BankWebhook, BankSyncLog


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'bank_type', 'is_active', 'is_sandbox', 'created_at']
    list_filter = ['bank_type', 'is_active', 'is_sandbox']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'bank', 'account_number', 'currency', 'balance', 'is_active', 'last_sync']
    list_filter = ['bank', 'currency', 'is_active', 'account_type']
    search_fields = ['user__username', 'account_number', 'bank__name']
    ordering = ['-created_at']


@admin.register(BankToken)
class BankTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'bank', 'token_type', 'expires_at', 'is_active', 'created_at']
    list_filter = ['bank', 'token_type', 'is_active']
    search_fields = ['user__username', 'bank__name']
    ordering = ['-created_at']


@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ['bank_account', 'external_id', 'amount', 'currency', 'transaction_type', 'transaction_date', 'is_processed']
    list_filter = ['transaction_type', 'currency', 'is_processed', 'is_categorized', 'transaction_date']
    search_fields = ['external_id', 'description', 'merchant', 'bank_account__account_number']
    ordering = ['-transaction_date']


@admin.register(BankWebhook)
class BankWebhookAdmin(admin.ModelAdmin):
    list_display = ['bank', 'webhook_type', 'is_processed', 'created_at']
    list_filter = ['bank', 'webhook_type', 'is_processed']
    search_fields = ['bank__name']
    ordering = ['-created_at']


@admin.register(BankSyncLog)
class BankSyncLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'bank', 'sync_type', 'status', 'transactions_imported', 'started_at']
    list_filter = ['bank', 'sync_type', 'status']
    search_fields = ['user__username', 'bank__name']
    ordering = ['-started_at']

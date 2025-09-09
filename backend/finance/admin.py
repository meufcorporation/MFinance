from django.contrib import admin
from .models import Account, Category, Transaction, Budget, Rule, ImportJob

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'bank_name', 'account_type', 'balance', 'currency', 'user', 'is_active']
    list_filter = ['account_type', 'currency', 'is_active', 'created_at']
    search_fields = ['name', 'bank_name', 'account_number']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'parent', 'user', 'is_active']
    list_filter = ['category_type', 'is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'transaction_type', 'account', 'category', 'date', 'user']
    list_filter = ['transaction_type', 'date', 'account', 'category']
    search_fields = ['description', 'merchant', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'period', 'category', 'user', 'is_active']
    list_filter = ['period', 'is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'category', 'priority', 'is_active', 'user']
    list_filter = ['rule_type', 'is_active', 'priority']
    search_fields = ['name', 'condition']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = ['filename', 'status', 'total_rows', 'processed_rows', 'user', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['filename']
    readonly_fields = ['created_at', 'updated_at']

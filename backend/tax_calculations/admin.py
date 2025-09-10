from django.contrib import admin
from .models import TaxRate, TaxCalculation, TaxPayment, TaxRule, TaxExemption


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ['tax_type', 'fop_group', 'rate_percent', 'min_amount', 'max_amount', 'valid_from', 'is_active']
    list_filter = ['tax_type', 'fop_group', 'is_active']
    search_fields = ['tax_type', 'fop_group']
    ordering = ['tax_type', 'fop_group', '-valid_from']


@admin.register(TaxCalculation)
class TaxCalculationAdmin(admin.ModelAdmin):
    list_display = ['fop_profile', 'calculation_type', 'year', 'month', 'quarter', 'total_tax_amount', 'status', 'created_at']
    list_filter = ['calculation_type', 'year', 'status']
    search_fields = ['fop_profile__first_name', 'fop_profile__last_name']
    ordering = ['-year', '-month', '-quarter']


@admin.register(TaxPayment)
class TaxPaymentAdmin(admin.ModelAdmin):
    list_display = ['tax_calculation', 'payment_type', 'amount', 'due_date', 'status', 'created_at']
    list_filter = ['payment_type', 'status', 'due_date']
    search_fields = ['payment_reference', 'bank_transaction_id']
    ordering = ['-due_date']


@admin.register(TaxRule)
class TaxRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'fop_group', 'priority', 'is_active', 'created_at']
    list_filter = ['rule_type', 'fop_group', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['-priority', 'name']


@admin.register(TaxExemption)
class TaxExemptionAdmin(admin.ModelAdmin):
    list_display = ['fop_profile', 'exemption_type', 'exemption_percent', 'valid_from', 'is_active', 'created_at']
    list_filter = ['exemption_type', 'is_active']
    search_fields = ['fop_profile__first_name', 'fop_profile__last_name']
    ordering = ['-valid_from']

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ReportTemplate, Report, ReportData, DigitalSignature, 
    ReportSubmission
)


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'format', 'version', 'is_active', 'is_public', 'created_by', 'created_at']
    list_filter = ['report_type', 'format', 'is_active', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'created_by__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'description', 'report_type', 'format', 'version')
        }),
        ('Шаблон', {
            'fields': ('template_content', 'template_file'),
            'classes': ('collapse',)
        }),
        ('Налаштування', {
            'fields': ('is_active', 'is_public', 'created_by')
        }),
        ('Метадані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'report_type', 'status', 'created_at', 'generated_at']
    list_filter = ['status', 'report_type', 'format', 'created_at', 'generated_at']
    search_fields = ['name', 'description', 'user__email', 'fop_profile__name']
    readonly_fields = ['created_at', 'generated_at', 'signed_at', 'submitted_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('user', 'fop_profile', 'tax_period', 'template', 'name', 'description')
        }),
        ('Деталі звіту', {
            'fields': ('report_type', 'format', 'status')
        }),
        ('Файли', {
            'fields': ('generated_file', 'signed_file'),
            'classes': ('collapse',)
        }),
        ('Дати', {
            'fields': ('created_at', 'generated_at', 'signed_at', 'submitted_at'),
            'classes': ('collapse',)
        }),
        ('Додаткова інформація', {
            'fields': ('metadata', 'error_message'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'fop_profile', 'tax_period', 'template')


@admin.register(ReportData)
class ReportDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'report', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['report__name', 'report__user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('report')


@admin.register(DigitalSignature)
class DigitalSignatureAdmin(admin.ModelAdmin):
    list_display = ['id', 'report', 'signature_type', 'signer_name', 'is_valid', 'signed_at']
    list_filter = ['signature_type', 'is_valid', 'signed_at']
    search_fields = ['report__name', 'signer_name', 'signer_identifier']
    readonly_fields = ['signed_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('report')


@admin.register(ReportSubmission)
class ReportSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'report', 'submission_id', 'status', 'submitted_at', 'response_at']
    list_filter = ['status', 'submitted_at', 'response_at']
    search_fields = ['report__name', 'submission_id', 'submission_url']
    readonly_fields = ['submitted_at', 'response_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('report')
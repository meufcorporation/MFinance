from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ReportTemplate, Report, ReportData, DigitalSignature, 
    ReportSubmission
)
from fop.models import FOPProfile, TaxPeriod

User = get_user_model()


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Серіалізатор для шаблонів звітів"""
    created_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'description', 'report_type', 'format',
            'template_content', 'template_file', 'is_active', 'is_public',
            'version', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ReportDataSerializer(serializers.ModelSerializer):
    """Серіалізатор для даних звітів"""
    
    class Meta:
        model = ReportData
        fields = ['id', 'data', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DigitalSignatureSerializer(serializers.ModelSerializer):
    """Серіалізатор для цифрових підписів"""
    
    class Meta:
        model = DigitalSignature
        fields = [
            'id', 'signature_type', 'signer_name', 'signer_identifier',
            'certificate_serial', 'signature_file', 'certificate_file',
            'signed_at', 'is_valid', 'validation_message'
        ]
        read_only_fields = ['id', 'signed_at']


class ReportSubmissionSerializer(serializers.ModelSerializer):
    """Серіалізатор для подачі звітів"""
    
    class Meta:
        model = ReportSubmission
        fields = [
            'id', 'submission_id', 'submission_url', 'status',
            'submitted_at', 'response_at', 'response_data', 'error_message'
        ]
        read_only_fields = ['id', 'submitted_at', 'response_at']


class ReportSerializer(serializers.ModelSerializer):
    """Серіалізатор для звітів"""
    user = serializers.StringRelatedField(read_only=True)
    fop_profile = serializers.StringRelatedField(read_only=True)
    tax_period = serializers.StringRelatedField(read_only=True)
    template = ReportTemplateSerializer(read_only=True)
    data = ReportDataSerializer(many=True, read_only=True)
    signatures = DigitalSignatureSerializer(many=True, read_only=True)
    submissions = ReportSubmissionSerializer(many=True, read_only=True)
    
    # ID для створення
    fop_profile_id = serializers.IntegerField(write_only=True)
    tax_period_id = serializers.IntegerField(write_only=True)
    template_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'user', 'fop_profile', 'fop_profile_id', 'tax_period',
            'tax_period_id', 'template', 'template_id', 'name', 'description',
            'report_type', 'format', 'status', 'created_at', 'generated_at',
            'signed_at', 'submitted_at', 'generated_file', 'signed_file',
            'metadata', 'error_message', 'data', 'signatures', 'submissions'
        ]
        read_only_fields = [
            'id', 'user', 'generated_at', 'signed_at', 'submitted_at',
            'generated_file', 'signed_file', 'metadata', 'error_message'
        ]
    
    def create(self, validated_data):
        """Створити звіт з автоматичним призначенням користувача"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReportCreateSerializer(serializers.Serializer):
    """Серіалізатор для створення звіту"""
    template_id = serializers.IntegerField()
    fop_profile_id = serializers.IntegerField()
    tax_period_id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    data = serializers.JSONField(required=False, default=dict)
    
    def validate(self, attrs):
        """Валідація створення звіту"""
        template_id = attrs.get('template_id')
        fop_profile_id = attrs.get('fop_profile_id')
        tax_period_id = attrs.get('tax_period_id')
        
        # Перевірити існування шаблону
        try:
            template = ReportTemplate.objects.get(id=template_id)
            if not template.is_active:
                raise serializers.ValidationError("Шаблон не активний")
        except ReportTemplate.DoesNotExist:
            raise serializers.ValidationError("Шаблон не знайдено")
        
        # Перевірити існування профілю ФОП
        try:
            FOPProfile.objects.get(id=fop_profile_id)
        except FOPProfile.DoesNotExist:
            raise serializers.ValidationError("Профіль ФОП не знайдено")
        
        # Перевірити існування податкового періоду
        try:
            TaxPeriod.objects.get(id=tax_period_id)
        except TaxPeriod.DoesNotExist:
            raise serializers.ValidationError("Податковий період не знайдено")
        
        return attrs


class ReportGenerateSerializer(serializers.Serializer):
    """Серіалізатор для генерації звіту"""
    report_id = serializers.IntegerField()
    data = serializers.JSONField(required=False, default=dict)
    format = serializers.ChoiceField(choices=['xml', 'pdf', 'excel'], required=False)
    
    def validate(self, attrs):
        """Валідація генерації звіту"""
        report_id = attrs.get('report_id')
        
        try:
            report = Report.objects.get(id=report_id)
            if report.status not in ['draft', 'error']:
                raise serializers.ValidationError(
                    f"Неможливо згенерувати звіт зі статусом {report.status}"
                )
        except Report.DoesNotExist:
            raise serializers.ValidationError("Звіт не знайдено")
        
        return attrs


class ReportSignSerializer(serializers.Serializer):
    """Серіалізатор для підпису звіту"""
    report_id = serializers.IntegerField()
    signature_type = serializers.ChoiceField(choices=DigitalSignature.SIGNATURE_TYPE_CHOICES)
    signer_name = serializers.CharField(max_length=200)
    signer_identifier = serializers.CharField(max_length=100)
    certificate_serial = serializers.CharField(max_length=100, required=False)
    signature_file = serializers.FileField()
    certificate_file = serializers.FileField(required=False)
    
    def validate(self, attrs):
        """Валідація підпису звіту"""
        report_id = attrs.get('report_id')
        
        try:
            report = Report.objects.get(id=report_id)
            if report.status != 'ready':
                raise serializers.ValidationError(
                    "Звіт повинен бути готовий для підпису"
                )
        except Report.DoesNotExist:
            raise serializers.ValidationError("Звіт не знайдено")
        
        return attrs


class ReportSubmitSerializer(serializers.Serializer):
    """Серіалізатор для подачі звіту"""
    report_id = serializers.IntegerField()
    submission_url = serializers.URLField(required=False)
    
    def validate(self, attrs):
        """Валідація подачі звіту"""
        report_id = attrs.get('report_id')
        
        try:
            report = Report.objects.get(id=report_id)
            if report.status not in ['ready', 'signed']:
                raise serializers.ValidationError(
                    "Звіт повинен бути готовий або підписаний для подачі"
                )
        except Report.DoesNotExist:
            raise serializers.ValidationError("Звіт не знайдено")
        
        return attrs


class ReportTemplateCreateSerializer(serializers.Serializer):
    """Серіалізатор для створення шаблону звіту"""
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    report_type = serializers.ChoiceField(choices=ReportTemplate.REPORT_TYPE_CHOICES)
    format = serializers.ChoiceField(choices=ReportTemplate.FORMAT_CHOICES, default='xml')
    template_content = serializers.CharField()
    template_file = serializers.FileField(required=False)
    is_public = serializers.BooleanField(default=False)
    version = serializers.CharField(max_length=20, default='1.0')
    
    def create(self, validated_data):
        """Створити шаблон з автоматичним призначенням користувача"""
        validated_data['created_by'] = self.context['request'].user
        return ReportTemplate.objects.create(**validated_data)

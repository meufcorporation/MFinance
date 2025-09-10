from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    PaymentProvider, PaymentMethod, Payment, PaymentSchedule,
    PaymentWebhook, PaymentLog, PaymentTemplate
)
from fop.models import FOPProfile, TaxObligation
from bank_integration.models import BankAccount

User = get_user_model()


class PaymentProviderSerializer(serializers.ModelSerializer):
    """Серіалізатор для провайдерів платежів"""
    
    class Meta:
        model = PaymentProvider
        fields = [
            'id', 'name', 'display_name', 'is_active', 'api_url',
            'webhook_url', 'settings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Серіалізатор для способів оплати"""
    provider = PaymentProviderSerializer(read_only=True)
    provider_id = serializers.IntegerField(write_only=True)
    bank_account = serializers.StringRelatedField(read_only=True)
    bank_account_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'method_type', 'provider', 'provider_id', 'bank_account',
            'bank_account_id', 'card_holder', 'iban', 'is_default',
            'is_active', 'auto_pay_enabled', 'max_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Валідація способу оплати"""
        method_type = attrs.get('method_type')
        
        if method_type == 'card' and not attrs.get('card_holder'):
            raise serializers.ValidationError("Для картки необхідно вказати власника")
        
        if method_type == 'iban' and not attrs.get('iban'):
            raise serializers.ValidationError("Для IBAN необхідно вказати номер рахунку")
        
        return attrs


class PaymentSerializer(serializers.ModelSerializer):
    """Серіалізатор для платежів"""
    user = serializers.StringRelatedField(read_only=True)
    fop_profile = serializers.StringRelatedField(read_only=True)
    tax_obligation = serializers.StringRelatedField(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)
    provider = PaymentProviderSerializer(read_only=True)
    
    # ID для створення
    fop_profile_id = serializers.IntegerField(write_only=True)
    tax_obligation_id = serializers.IntegerField(write_only=True, required=False)
    payment_method_id = serializers.IntegerField(write_only=True)
    provider_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'fop_profile', 'fop_profile_id', 'tax_obligation',
            'tax_obligation_id', 'payment_method', 'payment_method_id',
            'provider', 'provider_id', 'amount', 'currency', 'payment_type',
            'description', 'status', 'created_at', 'updated_at', 'processed_at',
            'external_payment_id', 'external_transaction_id', 'metadata',
            'error_message'
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'updated_at', 'processed_at',
            'external_payment_id', 'external_transaction_id', 'metadata',
            'error_message'
        ]
    
    def create(self, validated_data):
        """Створити платіж з автоматичним призначенням користувача"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PaymentScheduleSerializer(serializers.ModelSerializer):
    """Серіалізатор для розкладу платежів"""
    user = serializers.StringRelatedField(read_only=True)
    fop_profile = serializers.StringRelatedField(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)
    
    # ID для створення
    fop_profile_id = serializers.IntegerField(write_only=True)
    payment_method_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = PaymentSchedule
        fields = [
            'id', 'user', 'fop_profile', 'fop_profile_id', 'payment_method',
            'payment_method_id', 'name', 'description', 'frequency',
            'cron_expression', 'amount', 'payment_type', 'is_active',
            'next_payment_date', 'last_payment_date', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'next_payment_date', 'last_payment_date',
            'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        """Створити розклад з автоматичним призначенням користувача"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PaymentWebhookSerializer(serializers.ModelSerializer):
    """Серіалізатор для webhook'ів"""
    provider = PaymentProviderSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = PaymentWebhook
        fields = [
            'id', 'provider', 'payment', 'event_type', 'payload',
            'signature', 'is_processed', 'processed_at', 'error_message',
            'created_at'
        ]
        read_only_fields = [
            'id', 'is_processed', 'processed_at', 'error_message', 'created_at'
        ]


class PaymentLogSerializer(serializers.ModelSerializer):
    """Серіалізатор для логів платежів"""
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = PaymentLog
        fields = [
            'id', 'payment', 'level', 'message', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentTemplateSerializer(serializers.ModelSerializer):
    """Серіалізатор для шаблонів платежів"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = PaymentTemplate
        fields = [
            'id', 'user', 'name', 'description', 'amount', 'payment_type',
            'description_template', 'is_active', 'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Створити шаблон з автоматичним призначенням користувача"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PaymentCreateSerializer(serializers.Serializer):
    """Серіалізатор для створення платежу з шаблону"""
    template_id = serializers.IntegerField(required=False)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_method_id = serializers.IntegerField()
    description = serializers.CharField(max_length=500, required=False)
    fop_profile_id = serializers.IntegerField()
    tax_obligation_id = serializers.IntegerField(required=False)
    
    def validate(self, attrs):
        """Валідація створення платежу"""
        if not attrs.get('template_id') and not attrs.get('description'):
            raise serializers.ValidationError(
                "Необхідно вказати або template_id, або description"
            )
        return attrs


class PaymentStatusUpdateSerializer(serializers.Serializer):
    """Серіалізатор для оновлення статусу платежу"""
    status = serializers.ChoiceField(choices=Payment.STATUS_CHOICES)
    external_payment_id = serializers.CharField(max_length=100, required=False)
    external_transaction_id = serializers.CharField(max_length=100, required=False)
    metadata = serializers.JSONField(required=False)
    error_message = serializers.CharField(required=False)


class PaymentMethodCreateSerializer(serializers.Serializer):
    """Серіалізатор для створення способу оплати"""
    method_type = serializers.ChoiceField(choices=PaymentMethod.METHOD_CHOICES)
    provider_id = serializers.IntegerField()
    bank_account_id = serializers.IntegerField(required=False)
    card_number = serializers.CharField(max_length=20, required=False)
    card_holder = serializers.CharField(max_length=100, required=False)
    iban = serializers.CharField(max_length=34, required=False)
    is_default = serializers.BooleanField(default=False)
    auto_pay_enabled = serializers.BooleanField(default=False)
    max_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    
    def validate(self, attrs):
        """Валідація способу оплати"""
        method_type = attrs.get('method_type')
        
        if method_type == 'card':
            if not attrs.get('card_number') or not attrs.get('card_holder'):
                raise serializers.ValidationError(
                    "Для картки необхідно вказати номер та власника"
                )
        
        if method_type == 'iban':
            if not attrs.get('iban'):
                raise serializers.ValidationError(
                    "Для IBAN необхідно вказати номер рахунку"
                )
        
        return attrs

from rest_framework import serializers
from .models import FOPProfile, TaxPeriod, FOPSettings, TaxObligation


class FOPProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FOPProfile
        fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'tax_number',
            'registration_date', 'tax_group', 'tax_system', 'bank_name',
            'bank_code', 'account_number', 'phone', 'email', 'address',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaxPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxPeriod
        fields = [
            'id', 'period_type', 'year', 'month', 'quarter',
            'declaration_deadline', 'payment_deadline', 'declaration_submitted',
            'payment_made', 'tax_amount', 'paid_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FOPSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FOPSettings
        fields = [
            'id', 'notification_channels', 'notify_before_deadline',
            'notify_weekly', 'notify_monthly', 'auto_calculate_tax',
            'include_vat', 'export_format', 'include_receipts',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaxObligationSerializer(serializers.ModelSerializer):
    remaining_amount = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = TaxObligation
        fields = [
            'id', 'obligation_type', 'calculated_amount', 'paid_amount',
            'payment_deadline', 'status', 'calculation_data',
            'payment_reference', 'remaining_amount', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FOPProfileDetailSerializer(serializers.ModelSerializer):
    tax_periods = TaxPeriodSerializer(many=True, read_only=True)
    settings = FOPSettingsSerializer(read_only=True)
    
    class Meta:
        model = FOPProfile
        fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'tax_number',
            'registration_date', 'tax_group', 'tax_system', 'bank_name',
            'bank_code', 'account_number', 'phone', 'email', 'address',
            'is_active', 'tax_periods', 'settings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

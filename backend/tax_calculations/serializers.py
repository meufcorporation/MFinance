from rest_framework import serializers
from .models import TaxRate, TaxCalculation, TaxPayment, TaxRule, TaxExemption


class TaxRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRate
        fields = [
            'id', 'tax_type', 'fop_group', 'rate_percent', 'min_amount',
            'max_amount', 'valid_from', 'valid_to', 'is_active', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaxCalculationSerializer(serializers.ModelSerializer):
    fop_profile_name = serializers.CharField(source='fop_profile.get_full_name', read_only=True)
    fop_tax_group = serializers.CharField(source='fop_profile.tax_group', read_only=True)
    
    class Meta:
        model = TaxCalculation
        fields = [
            'id', 'fop_profile', 'fop_profile_name', 'fop_tax_group',
            'calculation_type', 'year', 'month', 'quarter', 'total_income',
            'total_expenses', 'taxable_income', 'single_tax_amount', 'esv_amount',
            'vat_amount', 'income_tax_amount', 'total_tax_amount', 'status',
            'calculation_data', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaxPaymentSerializer(serializers.ModelSerializer):
    tax_calculation_period = serializers.CharField(source='tax_calculation.get_period_display', read_only=True)
    
    class Meta:
        model = TaxPayment
        fields = [
            'id', 'tax_calculation', 'tax_calculation_period', 'payment_type',
            'amount', 'paid_amount', 'due_date', 'paid_date', 'status',
            'payment_reference', 'bank_transaction_id', 'payment_data',
            'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaxRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRule
        fields = [
            'id', 'name', 'rule_type', 'fop_group', 'condition', 'action',
            'priority', 'is_active', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaxExemptionSerializer(serializers.ModelSerializer):
    fop_profile_name = serializers.CharField(source='fop_profile.get_full_name', read_only=True)
    
    class Meta:
        model = TaxExemption
        fields = [
            'id', 'fop_profile', 'fop_profile_name', 'exemption_type',
            'valid_from', 'valid_to', 'exemption_percent', 'max_amount',
            'is_active', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaxCalculationRequestSerializer(serializers.Serializer):
    """Serializer for tax calculation requests"""
    fop_profile = serializers.PrimaryKeyRelatedField(queryset=None)  # Will be set in view
    calculation_type = serializers.ChoiceField(choices=TaxCalculation.CALCULATION_TYPES)
    year = serializers.IntegerField()
    month = serializers.IntegerField(required=False, allow_null=True)
    quarter = serializers.IntegerField(required=False, allow_null=True)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    
    def validate(self, data):
        calculation_type = data.get('calculation_type')
        month = data.get('month')
        quarter = data.get('quarter')
        
        if calculation_type == 'monthly' and not month:
            raise serializers.ValidationError("Month is required for monthly calculation")
        
        if calculation_type == 'quarterly' and not quarter:
            raise serializers.ValidationError("Quarter is required for quarterly calculation")
        
        if calculation_type == 'yearly' and (month or quarter):
            raise serializers.ValidationError("Month and quarter should not be specified for yearly calculation")
        
        return data


class TaxPaymentRequestSerializer(serializers.Serializer):
    """Serializer for tax payment requests"""
    tax_calculation = serializers.PrimaryKeyRelatedField(queryset=TaxCalculation.objects.all())
    payment_type = serializers.ChoiceField(choices=TaxPayment.PAYMENT_TYPES)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    payment_method = serializers.CharField(max_length=50, default='bank_transfer')
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value


class TaxDeadlineSerializer(serializers.Serializer):
    """Serializer for tax deadlines"""
    type = serializers.CharField()
    period = serializers.CharField()
    deadline = serializers.DateField()
    description = serializers.CharField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    status = serializers.CharField()
    is_overdue = serializers.BooleanField()


class TaxSummarySerializer(serializers.Serializer):
    """Serializer for tax summary"""
    year = serializers.IntegerField()
    total_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    taxable_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_tax_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_paid_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    remaining_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    calculations_count = serializers.IntegerField()
    payments_count = serializers.IntegerField()

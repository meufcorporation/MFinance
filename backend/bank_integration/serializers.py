from rest_framework import serializers
from .models import Bank, BankAccount, BankToken, BankTransaction, BankWebhook, BankSyncLog


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = [
            'id', 'name', 'code', 'bank_type', 'api_base_url', 'auth_url', 'token_url',
            'webhook_url', 'client_id', 'is_active', 'is_sandbox', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BankAccountSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source='bank.name', read_only=True)
    bank_type = serializers.CharField(source='bank.bank_type', read_only=True)
    
    class Meta:
        model = BankAccount
        fields = [
            'id', 'bank', 'bank_name', 'bank_type', 'account_id', 'account_number',
            'account_type', 'currency', 'balance', 'credit_limit', 'is_active',
            'last_sync', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BankTokenSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source='bank.name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = BankToken
        fields = [
            'id', 'bank', 'bank_name', 'token_type', 'expires_at', 'is_active',
            'is_expired', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BankTransactionSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source='bank_account.bank.name', read_only=True)
    account_number = serializers.CharField(source='bank_account.account_number', read_only=True)
    
    class Meta:
        model = BankTransaction
        fields = [
            'id', 'bank_account', 'bank_name', 'account_number', 'external_id',
            'amount', 'currency', 'transaction_type', 'description', 'merchant',
            'mcc_code', 'transaction_date', 'processed_date', 'is_processed',
            'is_categorized', 'internal_transaction', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BankWebhookSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source='bank.name', read_only=True)
    
    class Meta:
        model = BankWebhook
        fields = [
            'id', 'bank', 'bank_name', 'webhook_type', 'payload', 'signature',
            'is_processed', 'processed_at', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BankSyncLogSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source='bank.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = BankSyncLog
        fields = [
            'id', 'user', 'user_username', 'bank', 'bank_name', 'sync_type',
            'status', 'transactions_imported', 'transactions_updated', 'errors_count',
            'started_at', 'finished_at', 'duration', 'details', 'error_message',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BankConnectionSerializer(serializers.Serializer):
    """Serializer for bank connection flow"""
    bank = serializers.PrimaryKeyRelatedField(queryset=Bank.objects.filter(is_active=True))
    authorization_code = serializers.CharField(max_length=500)
    state = serializers.CharField(max_length=100, required=False)
    
    def validate_bank(self, value):
        if not value.is_active:
            raise serializers.ValidationError("Bank is not active")
        return value


class BankSyncSerializer(serializers.Serializer):
    """Serializer for manual bank sync"""
    bank_account = serializers.PrimaryKeyRelatedField(queryset=BankAccount.objects.filter(is_active=True))
    sync_type = serializers.ChoiceField(choices=BankSyncLog.SYNC_TYPES)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    
    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError("Start date must be before end date")
        return data

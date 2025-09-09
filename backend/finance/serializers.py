from rest_framework import serializers
from .models import Account, Category, Transaction, Budget, Rule, ImportJob


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'name', 'account_type', 'bank_name', 'account_number', 
                 'balance', 'currency', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'category_type', 'parent', 'color', 'icon', 
                 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'account_name', 'category', 'category_name',
                 'amount', 'transaction_type', 'description', 'merchant', 'date',
                 'to_account', 'external_id', 'tags', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    spent_amount = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Budget
        fields = ['id', 'name', 'category', 'category_name', 'amount', 'period',
                 'start_date', 'end_date', 'is_active', 'spent_amount', 
                 'remaining_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_spent_amount(self, obj):
        # Розрахунок витраченої суми за період
        from django.db.models import Sum
        from django.utils import timezone
        
        transactions = Transaction.objects.filter(
            user=obj.user,
            category=obj.category,
            transaction_type='expense',
            date__gte=obj.start_date,
            date__lte=obj.end_date
        )
        spent = transactions.aggregate(total=Sum('amount'))['total'] or 0
        return spent
    
    def get_remaining_amount(self, obj):
        spent = self.get_spent_amount(obj)
        return obj.amount - spent


class RuleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Rule
        fields = ['id', 'name', 'rule_type', 'condition', 'category', 'category_name',
                 'priority', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ImportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportJob
        fields = ['id', 'filename', 'status', 'total_rows', 'processed_rows',
                 'error_message', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransactionFilterSerializer(serializers.Serializer):
    """Серіалізатор для фільтрації транзакцій"""
    account = serializers.IntegerField(required=False)
    category = serializers.IntegerField(required=False)
    transaction_type = serializers.ChoiceField(choices=Transaction.TRANSACTION_TYPES, required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    search = serializers.CharField(required=False)
    min_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)

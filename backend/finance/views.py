from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Account, Category, Transaction, Budget, Rule, ImportJob
from .serializers import (
    AccountSerializer, CategorySerializer, TransactionSerializer, 
    BudgetSerializer, RuleSerializer, ImportJobSerializer, TransactionFilterSerializer
)
from .tasks import process_csv_import


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.none()  # Will be overridden by get_queryset
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'bank_name', 'account_number']
    filterset_fields = ['account_type', 'currency', 'is_active']
    ordering_fields = ['created_at', 'balance', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def balance_history(self, request, pk=None):
        """Історія змін балансу рахунку"""
        account = self.get_object()
        # Тут можна додати логіку для отримання історії балансу
        return Response({'message': 'Balance history endpoint'})
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Підсумок по всіх рахунках"""
        accounts = self.get_queryset()
        total_balance = accounts.aggregate(total=Sum('balance'))['total'] or 0
        
        by_type = {}
        for account_type, _ in Account.ACCOUNT_TYPES:
            balance = accounts.filter(account_type=account_type).aggregate(
                total=Sum('balance'))['total'] or 0
            by_type[account_type] = balance
        
        return Response({
            'total_balance': total_balance,
            'by_type': by_type,
            'accounts_count': accounts.count()
        })


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.none()  # Will be overridden by get_queryset
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    filterset_fields = ['category_type', 'is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['category_type', 'name']
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Дерево категорій з підкатегоріями"""
        categories = self.get_queryset().filter(parent=None)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.none()  # Will be overridden by get_queryset
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'merchant', 'notes']
    filterset_fields = ['account', 'category', 'transaction_type']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'filter':
            return TransactionFilterSerializer
        return TransactionSerializer
    
    @action(detail=False, methods=['post'])
    def filter(self, request):
        """Розширена фільтрація транзакцій"""
        serializer = TransactionFilterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset()
        filters = serializer.validated_data
        
        if filters.get('account'):
            queryset = queryset.filter(account=filters['account'])
        if filters.get('category'):
            queryset = queryset.filter(category=filters['category'])
        if filters.get('transaction_type'):
            queryset = queryset.filter(transaction_type=filters['transaction_type'])
        if filters.get('start_date'):
            queryset = queryset.filter(date__gte=filters['start_date'])
        if filters.get('end_date'):
            queryset = queryset.filter(date__lte=filters['end_date'])
        if filters.get('search'):
            search = filters['search']
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(merchant__icontains=search) |
                Q(notes__icontains=search)
            )
        if filters.get('min_amount'):
            queryset = queryset.filter(amount__gte=filters['min_amount'])
        if filters.get('max_amount'):
            queryset = queryset.filter(amount__lte=filters['max_amount'])
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Підсумок транзакцій за період"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date:
            start_date = timezone.now().replace(day=1)
        else:
            start_date = datetime.fromisoformat(start_date)
        
        if not end_date:
            end_date = timezone.now()
        else:
            end_date = datetime.fromisoformat(end_date)
        
        queryset = self.get_queryset().filter(date__gte=start_date, date__lte=end_date)
        
        income = queryset.filter(transaction_type='income').aggregate(
            total=Sum('amount'))['total'] or 0
        expense = queryset.filter(transaction_type='expense').aggregate(
            total=Sum('amount'))['total'] or 0
        
        by_category = {}
        for category in Category.objects.filter(user=request.user):
            amount = queryset.filter(category=category).aggregate(
                total=Sum('amount'))['total'] or 0
            if amount > 0:
                by_category[category.name] = amount
        
        return Response({
            'period': {'start': start_date, 'end': end_date},
            'income': income,
            'expense': expense,
            'balance': income - expense,
            'by_category': by_category,
            'transactions_count': queryset.count()
        })
    
    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        """Імпорт транзакцій з CSV файлу"""
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        import_job = ImportJob.objects.create(
            user=request.user,
            filename=file.name,
            status='pending'
        )
        
        # Запускаємо Celery task
        process_csv_import.delay(import_job.id, file.read().decode('utf-8'))
        
        return Response({
            'message': 'Import started',
            'job_id': import_job.id
        }, status=status.HTTP_202_ACCEPTED)


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.none()  # Will be overridden by get_queryset
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    filterset_fields = ['period', 'is_active', 'category']
    ordering_fields = ['created_at', 'amount', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Поточні активні бюджети"""
        now = timezone.now().date()
        budgets = self.get_queryset().filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )
        serializer = self.get_serializer(budgets, many=True)
        return Response(serializer.data)


class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.none()  # Will be overridden by get_queryset
    serializer_class = RuleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'condition']
    filterset_fields = ['rule_type', 'is_active']
    ordering_fields = ['priority', 'name', 'created_at']
    ordering = ['-priority', 'name']
    
    def get_queryset(self):
        return Rule.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ImportJobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ImportJob.objects.none()  # Will be overridden by get_queryset
    serializer_class = ImportJobSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return ImportJob.objects.filter(user=self.request.user)
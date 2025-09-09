from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Bank, BankAccount, BankToken, BankTransaction, BankWebhook, BankSyncLog
from .serializers import (
    BankSerializer, BankAccountSerializer, BankTokenSerializer,
    BankTransactionSerializer, BankWebhookSerializer, BankSyncLogSerializer,
    BankConnectionSerializer, BankSyncSerializer
)


class BankFilter(filters.FilterSet):
    bank_type = filters.ChoiceFilter(choices=Bank.BANK_TYPES)
    is_active = filters.BooleanFilter()
    is_sandbox = filters.BooleanFilter()
    
    class Meta:
        model = Bank
        fields = ['bank_type', 'is_active', 'is_sandbox']


class BankViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for banks (read-only)"""
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = BankFilter
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class BankAccountFilter(filters.FilterSet):
    bank = filters.ModelChoiceFilter(queryset=Bank.objects.all())
    currency = filters.CharFilter(lookup_expr='iexact')
    is_active = filters.BooleanFilter()
    
    class Meta:
        model = BankAccount
        fields = ['bank', 'currency', 'is_active']


class BankAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for user's bank accounts"""
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = BankAccountFilter
    search_fields = ['account_number', 'bank__name']
    ordering_fields = ['created_at', 'last_sync', 'balance']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Manual sync for bank account"""
        account = self.get_object()
        serializer = BankSyncSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create sync log
            sync_log = BankSyncLog.objects.create(
                user=request.user,
                bank=account.bank,
                sync_type=serializer.validated_data.get('sync_type', 'manual'),
                status='started'
            )
            
            # TODO: Implement actual sync logic
            # This would call the bank API and import transactions
            
            sync_log.status = 'success'
            sync_log.finished_at = timezone.now()
            sync_log.save()
            
            return Response({'message': 'Sync completed successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get transactions for this account"""
        account = self.get_object()
        transactions = BankTransaction.objects.filter(bank_account=account)
        
        # Apply filters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        transaction_type = request.query_params.get('transaction_type')
        
        if start_date:
            transactions = transactions.filter(transaction_date__date__gte=start_date)
        if end_date:
            transactions = transactions.filter(transaction_date__date__lte=end_date)
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
        
        serializer = BankTransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class BankTransactionFilter(filters.FilterSet):
    bank_account = filters.ModelChoiceFilter(queryset=BankAccount.objects.all())
    transaction_type = filters.ChoiceFilter(choices=BankTransaction.TRANSACTION_TYPES)
    currency = filters.CharFilter(lookup_expr='iexact')
    is_processed = filters.BooleanFilter()
    is_categorized = filters.BooleanFilter()
    date_from = filters.DateFilter(field_name='transaction_date', lookup_expr='date__gte')
    date_to = filters.DateFilter(field_name='transaction_date', lookup_expr='date__lte')
    
    class Meta:
        model = BankTransaction
        fields = ['bank_account', 'transaction_type', 'currency', 'is_processed', 'is_categorized']


class BankTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for bank transactions (read-only)"""
    serializer_class = BankTransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = BankTransactionFilter
    search_fields = ['description', 'merchant', 'external_id']
    ordering_fields = ['transaction_date', 'amount', 'created_at']
    ordering = ['-transaction_date']
    
    def get_queryset(self):
        return BankTransaction.objects.filter(
            bank_account__user=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def categorize(self, request, pk=None):
        """Categorize transaction"""
        transaction = self.get_object()
        category_id = request.data.get('category_id')
        
        if not category_id:
            return Response(
                {'error': 'category_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Implement categorization logic
        # This would create an internal transaction and link it
        
        transaction.is_categorized = True
        transaction.save()
        
        return Response({'message': 'Transaction categorized successfully'})
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get transaction summary"""
        queryset = self.get_queryset()
        
        # Calculate summary statistics
        total_income = queryset.filter(transaction_type='income').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        total_expense = queryset.filter(transaction_type='expense').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        total_transfer = queryset.filter(transaction_type='transfer').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'total_transfer': total_transfer,
            'net_amount': total_income - total_expense,
            'total_transactions': queryset.count()
        })


class BankTokenViewSet(viewsets.ModelViewSet):
    """ViewSet for bank tokens"""
    serializer_class = BankTokenSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return BankToken.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """Refresh bank token"""
        token = self.get_object()
        
        # TODO: Implement token refresh logic
        # This would call the bank API to refresh the token
        
        return Response({'message': 'Token refreshed successfully'})


class BankWebhookViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for bank webhooks (read-only)"""
    serializer_class = BankWebhookSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['bank', 'webhook_type', 'is_processed']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return BankWebhook.objects.filter(bank__is_active=True)
    
    @action(detail=False, methods=['post'])
    def receive(self, request):
        """Receive webhook from bank"""
        bank_id = request.data.get('bank_id')
        webhook_type = request.data.get('type')
        payload = request.data.get('payload', {})
        signature = request.headers.get('X-Signature', '')
        
        try:
            bank = Bank.objects.get(id=bank_id, is_active=True)
        except Bank.DoesNotExist:
            return Response(
                {'error': 'Bank not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create webhook record
        webhook = BankWebhook.objects.create(
            bank=bank,
            webhook_type=webhook_type,
            payload=payload,
            signature=signature
        )
        
        # TODO: Process webhook asynchronously
        # This would trigger a Celery task to process the webhook
        
        return Response({'message': 'Webhook received successfully'})


class BankSyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for bank sync logs (read-only)"""
    serializer_class = BankSyncLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['bank', 'sync_type', 'status']
    ordering = ['-started_at']
    
    def get_queryset(self):
        return BankSyncLog.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get sync statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_syncs': queryset.count(),
            'successful_syncs': queryset.filter(status='success').count(),
            'failed_syncs': queryset.filter(status='failed').count(),
            'total_transactions_imported': queryset.aggregate(
                total=models.Sum('transactions_imported')
            )['total'] or 0,
            'total_errors': queryset.aggregate(
                total=models.Sum('errors_count')
            )['total'] or 0
        }
        
        return Response(stats)
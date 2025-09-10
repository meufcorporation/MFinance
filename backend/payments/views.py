from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q, Sum, Count
from datetime import datetime, timedelta

from .models import (
    PaymentProvider, PaymentMethod, Payment, PaymentSchedule,
    PaymentWebhook, PaymentLog, PaymentTemplate
)
from .serializers import (
    PaymentProviderSerializer, PaymentMethodSerializer, PaymentSerializer,
    PaymentScheduleSerializer, PaymentWebhookSerializer, PaymentLogSerializer,
    PaymentTemplateSerializer, PaymentCreateSerializer, PaymentStatusUpdateSerializer,
    PaymentMethodCreateSerializer
)
from .tasks import process_payment, schedule_payment


class PaymentProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для провайдерів платежів"""
    queryset = PaymentProvider.objects.filter(is_active=True)
    serializer_class = PaymentProviderSerializer
    permission_classes = [permissions.IsAuthenticated]


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """ViewSet для способів оплати"""
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['method_type', 'is_active', 'auto_pay_enabled']
    search_fields = ['card_holder', 'iban']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фільтрація по користувачу"""
        return PaymentMethod.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Створити спосіб оплати для поточного користувача"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Встановити як основний спосіб оплати"""
        payment_method = self.get_object()
        
        # Скинути всі інші способи оплати користувача
        PaymentMethod.objects.filter(user=request.user).update(is_default=False)
        
        # Встановити поточний як основний
        payment_method.is_default = True
        payment_method.save()
        
        return Response({'message': 'Спосіб оплати встановлено як основний'})
    
    @action(detail=True, methods=['post'])
    def toggle_auto_pay(self, request, pk=None):
        """Увімкнути/вимкнути автоматичну оплату"""
        payment_method = self.get_object()
        payment_method.auto_pay_enabled = not payment_method.auto_pay_enabled
        payment_method.save()
        
        status_text = 'увімкнено' if payment_method.auto_pay_enabled else 'вимкнено'
        return Response({
            'message': f'Автоматичну оплату {status_text}',
            'auto_pay_enabled': payment_method.auto_pay_enabled
        })


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для платежів"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'payment_type', 'currency']
    search_fields = ['description', 'external_payment_id']
    ordering_fields = ['created_at', 'amount', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фільтрація по користувачу"""
        return Payment.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Створити платіж для поточного користувача"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_from_template(self, request):
        """Створити платіж з шаблону"""
        serializer = PaymentCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Логіка створення платежу з шаблону
            template_id = serializer.validated_data.get('template_id')
            if template_id:
                try:
                    template = PaymentTemplate.objects.get(
                        id=template_id,
                        user=request.user
                    )
                    description = template.description_template
                except PaymentTemplate.DoesNotExist:
                    return Response(
                        {'error': 'Шаблон не знайдено'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                description = serializer.validated_data.get('description', '')
            
            # Створити платіж
            payment_data = {
                'user': request.user,
                'fop_profile_id': serializer.validated_data['fop_profile_id'],
                'tax_obligation_id': serializer.validated_data.get('tax_obligation_id'),
                'payment_method_id': serializer.validated_data['payment_method_id'],
                'amount': serializer.validated_data['amount'],
                'description': description,
                'payment_type': 'tax'
            }
            
            payment = Payment.objects.create(**payment_data)
            
            # Запустити обробку платежу
            process_payment.delay(payment.id)
            
            return Response(
                PaymentSerializer(payment).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Повторити платіж"""
        payment = self.get_object()
        
        if payment.status not in ['failed', 'cancelled']:
            return Response(
                {'error': 'Можна повторити тільки невдалі або скасовані платежі'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Скинути статус та запустити обробку
        payment.status = 'pending'
        payment.error_message = None
        payment.save()
        
        process_payment.delay(payment.id)
        
        return Response({'message': 'Платіж поставлено в чергу на обробку'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Скасувати платіж"""
        payment = self.get_object()
        
        if payment.status not in ['pending', 'processing']:
            return Response(
                {'error': 'Можна скасувати тільки очікуючі або обробляючі платежі'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = 'cancelled'
        payment.save()
        
        return Response({'message': 'Платіж скасовано'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика платежів"""
        user_payments = self.get_queryset()
        
        # Загальна статистика
        total_payments = user_payments.count()
        total_amount = user_payments.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Статистика по статусах
        status_stats = user_payments.values('status').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        
        # Статистика по типах
        type_stats = user_payments.values('payment_type').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        
        # Статистика за останній місяць
        last_month = timezone.now() - timedelta(days=30)
        monthly_stats = user_payments.filter(
            created_at__gte=last_month
        ).aggregate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        
        return Response({
            'total_payments': total_payments,
            'total_amount': float(total_amount),
            'status_breakdown': list(status_stats),
            'type_breakdown': list(type_stats),
            'monthly_stats': monthly_stats
        })


class PaymentScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet для розкладу платежів"""
    queryset = PaymentSchedule.objects.all()
    serializer_class = PaymentScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['frequency', 'is_active', 'payment_type']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'next_payment_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фільтрація по користувачу"""
        return PaymentSchedule.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Створити розклад для поточного користувача"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Увімкнути/вимкнути розклад"""
        schedule = self.get_object()
        schedule.is_active = not schedule.is_active
        schedule.save()
        
        status_text = 'увімкнено' if schedule.is_active else 'вимкнено'
        return Response({
            'message': f'Розклад {status_text}',
            'is_active': schedule.is_active
        })
    
    @action(detail=True, methods=['post'])
    def execute_now(self, request, pk=None):
        """Виконати платіж зараз"""
        schedule = self.get_object()
        
        if not schedule.is_active:
            return Response(
                {'error': 'Розклад не активний'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Запустити платіж
        schedule_payment.delay(schedule.id)
        
        return Response({'message': 'Платіж поставлено в чергу на виконання'})


class PaymentTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet для шаблонів платежів"""
    queryset = PaymentTemplate.objects.all()
    serializer_class = PaymentTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['payment_type', 'is_active', 'is_public']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фільтрація по користувачу та публічним шаблонам"""
        return PaymentTemplate.objects.filter(
            Q(user=self.request.user) | Q(is_public=True)
        )
    
    def perform_create(self, serializer):
        """Створити шаблон для поточного користувача"""
        serializer.save(user=self.request.user)


class PaymentWebhookViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для webhook'ів (тільки для адміністраторів)"""
    queryset = PaymentWebhook.objects.all()
    serializer_class = PaymentWebhookSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['provider', 'event_type', 'is_processed']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class PaymentLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для логів платежів"""
    queryset = PaymentLog.objects.all()
    serializer_class = PaymentLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['level', 'payment']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фільтрація по користувачу"""
        return PaymentLog.objects.filter(payment__user=self.request.user)
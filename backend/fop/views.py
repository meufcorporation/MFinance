from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from datetime import datetime, timedelta

from .models import FOPProfile, TaxPeriod, FOPSettings, TaxObligation
from .serializers import (
    FOPProfileSerializer, TaxPeriodSerializer, FOPSettingsSerializer,
    TaxObligationSerializer, FOPProfileDetailSerializer
)


class FOPProfileViewSet(viewsets.ModelViewSet):
    queryset = FOPProfile.objects.none()
    serializer_class = FOPProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'tax_number']
    filterset_fields = ['tax_group', 'tax_system', 'is_active']
    ordering_fields = ['created_at', 'last_name', 'first_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return FOPProfile.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FOPProfileDetailSerializer
        return FOPProfileSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def tax_deadlines(self, request, pk=None):
        """Дедлайни податків для ФОП"""
        fop_profile = self.get_object()
        now = timezone.now().date()
        
        # Отримуємо наступні дедлайни
        upcoming_deadlines = TaxPeriod.objects.filter(
            fop_profile=fop_profile,
            payment_deadline__gte=now
        ).order_by('payment_deadline')[:5]
        
        # Отримуємо прострочені
        overdue_deadlines = TaxPeriod.objects.filter(
            fop_profile=fop_profile,
            payment_deadline__lt=now,
            payment_made=False
        ).order_by('payment_deadline')
        
        serializer = TaxPeriodSerializer(upcoming_deadlines, many=True)
        overdue_serializer = TaxPeriodSerializer(overdue_deadlines, many=True)
        
        return Response({
            'upcoming': serializer.data,
            'overdue': overdue_serializer.data,
            'total_upcoming': upcoming_deadlines.count(),
            'total_overdue': overdue_deadlines.count()
        })
    
    @action(detail=True, methods=['post'])
    def create_tax_period(self, request, pk=None):
        """Створити податковий період"""
        fop_profile = self.get_object()
        serializer = TaxPeriodSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(fop_profile=fop_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaxPeriodViewSet(viewsets.ModelViewSet):
    queryset = TaxPeriod.objects.none()
    serializer_class = TaxPeriodSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['period_type', 'year', 'month', 'quarter', 'declaration_submitted', 'payment_made']
    ordering_fields = ['year', 'month', 'quarter', 'payment_deadline']
    ordering = ['-year', '-month', '-quarter']
    
    def get_queryset(self):
        return TaxPeriod.objects.filter(fop_profile__user=self.request.user)
    
    def perform_create(self, serializer):
        fop_profile = FOPProfile.objects.get(user=self.request.user)
        serializer.save(fop_profile=fop_profile)
    
    @action(detail=False, methods=['get'])
    def current_periods(self, request):
        """Поточні податкові періоди"""
        now = timezone.now().date()
        current_year = now.year
        current_month = now.month
        
        periods = self.get_queryset().filter(
            year=current_year,
            month=current_month
        )
        
        serializer = self.get_serializer(periods, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming_deadlines(self, request):
        """Наближуючі дедлайни"""
        now = timezone.now().date()
        next_30_days = now + timedelta(days=30)
        
        periods = self.get_queryset().filter(
            payment_deadline__gte=now,
            payment_deadline__lte=next_30_days,
            payment_made=False
        ).order_by('payment_deadline')
        
        serializer = self.get_serializer(periods, many=True)
        return Response(serializer.data)


class FOPSettingsViewSet(viewsets.ModelViewSet):
    queryset = FOPSettings.objects.none()
    serializer_class = FOPSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FOPSettings.objects.filter(fop_profile__user=self.request.user)
    
    def perform_create(self, serializer):
        fop_profile = FOPProfile.objects.get(user=self.request.user)
        serializer.save(fop_profile=fop_profile)


class TaxObligationViewSet(viewsets.ModelViewSet):
    queryset = TaxObligation.objects.none()
    serializer_class = TaxObligationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['obligation_type', 'status', 'tax_period']
    ordering_fields = ['payment_deadline', 'calculated_amount', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return TaxObligation.objects.filter(fop_profile__user=self.request.user)
    
    def perform_create(self, serializer):
        fop_profile = FOPProfile.objects.get(user=self.request.user)
        serializer.save(fop_profile=fop_profile)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Прострочені зобов'язання"""
        now = timezone.now().date()
        overdue = self.get_queryset().filter(
            payment_deadline__lt=now,
            status__in=['pending', 'calculated']
        ).order_by('payment_deadline')
        
        serializer = self.get_serializer(overdue, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Позначити як сплачене"""
        obligation = self.get_object()
        paid_amount = request.data.get('paid_amount', obligation.calculated_amount)
        
        obligation.paid_amount = paid_amount
        obligation.status = 'paid'
        obligation.payment_reference = request.data.get('payment_reference', '')
        obligation.save()
        
        serializer = self.get_serializer(obligation)
        return Response(serializer.data)
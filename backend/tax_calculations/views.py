from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.db import models
from .models import TaxRate, TaxCalculation, TaxPayment, TaxRule, TaxExemption
from .serializers import (
    TaxRateSerializer, TaxCalculationSerializer, TaxPaymentSerializer,
    TaxRuleSerializer, TaxExemptionSerializer, TaxCalculationRequestSerializer,
    TaxPaymentRequestSerializer, TaxDeadlineSerializer, TaxSummarySerializer
)
from .services import TaxCalculationService


class TaxRateFilter(filters.FilterSet):
    tax_type = filters.ChoiceFilter(choices=TaxRate.TAX_TYPES)
    fop_group = filters.ChoiceFilter(choices=TaxRate.FOP_GROUPS)
    is_active = filters.BooleanFilter()
    
    class Meta:
        model = TaxRate
        fields = ['tax_type', 'fop_group', 'is_active']


class TaxRateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for tax rates (read-only)"""
    queryset = TaxRate.objects.all()
    serializer_class = TaxRateSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TaxRateFilter
    ordering_fields = ['tax_type', 'fop_group', 'valid_from']
    ordering = ['tax_type', 'fop_group', '-valid_from']


class TaxCalculationFilter(filters.FilterSet):
    fop_profile = filters.ModelChoiceFilter(queryset=None)
    calculation_type = filters.ChoiceFilter(choices=TaxCalculation.CALCULATION_TYPES)
    year = filters.NumberFilter()
    month = filters.NumberFilter()
    quarter = filters.NumberFilter()
    status = filters.ChoiceFilter(choices=TaxCalculation.STATUS_CHOICES)
    
    class Meta:
        model = TaxCalculation
        fields = ['fop_profile', 'calculation_type', 'year', 'month', 'quarter', 'status']


class TaxCalculationViewSet(viewsets.ModelViewSet):
    """ViewSet for tax calculations"""
    serializer_class = TaxCalculationSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TaxCalculationFilter
    ordering_fields = ['year', 'month', 'quarter', 'created_at']
    ordering = ['-year', '-month', '-quarter']
    
    def get_queryset(self):
        return TaxCalculation.objects.filter(
            fop_profile__user=self.request.user
        )
    
    def perform_create(self, serializer):
        from fop.models import FOPProfile
        try:
            fop_profile = FOPProfile.objects.get(user=self.request.user)
            serializer.save(fop_profile=fop_profile)
        except FOPProfile.DoesNotExist:
            raise serializers.ValidationError("FOP profile not found")
    
    @action(detail=True, methods=['post'])
    def calculate(self, request, pk=None):
        """Calculate taxes for this calculation"""
        calculation = self.get_object()
        
        if calculation.status != 'draft':
            return Response(
                {'error': 'Only draft calculations can be calculated'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = TaxCalculationService()
        try:
            updated_calculation = service.calculate_taxes(calculation)
            serializer = self.get_serializer(updated_calculation)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class TaxPaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for tax payments"""
    serializer_class = TaxPaymentSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['due_date', 'amount', 'created_at']
    ordering = ['-due_date']
    
    def get_queryset(self):
        return TaxPayment.objects.filter(
            tax_calculation__fop_profile__user=self.request.user
        )


class TaxRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for tax rules"""
    queryset = TaxRule.objects.all()
    serializer_class = TaxRuleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['rule_type', 'fop_group', 'is_active']
    ordering_fields = ['priority', 'name']
    ordering = ['-priority', 'name']


class TaxExemptionViewSet(viewsets.ModelViewSet):
    """ViewSet for tax exemptions"""
    serializer_class = TaxExemptionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['exemption_type', 'is_active']
    ordering_fields = ['valid_from', 'exemption_percent']
    ordering = ['-valid_from']
    
    def get_queryset(self):
        return TaxExemption.objects.filter(
            fop_profile__user=self.request.user
        )
    
    def perform_create(self, serializer):
        from fop.models import FOPProfile
        try:
            fop_profile = FOPProfile.objects.get(user=self.request.user)
            serializer.save(fop_profile=fop_profile)
        except FOPProfile.DoesNotExist:
            raise serializers.ValidationError("FOP profile not found")
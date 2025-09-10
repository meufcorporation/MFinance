from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta

from .models import (
    ReportTemplate, Report, ReportData, DigitalSignature, 
    ReportSubmission
)
from .serializers import (
    ReportTemplateSerializer, ReportSerializer, ReportDataSerializer,
    DigitalSignatureSerializer, ReportSubmissionSerializer,
    ReportCreateSerializer, ReportGenerateSerializer, ReportSignSerializer,
    ReportSubmitSerializer, ReportTemplateCreateSerializer
)
from .tasks import generate_report, sign_report, submit_report


class ReportTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet для шаблонів звітів"""
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['report_type', 'format', 'is_active', 'is_public']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name', 'version']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фільтрація по користувачу та публічним шаблонам"""
        return ReportTemplate.objects.filter(
            Q(created_by=self.request.user) | Q(is_public=True)
        )
    
    def perform_create(self, serializer):
        """Створити шаблон для поточного користувача"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def create_report(self, request, pk=None):
        """Створити звіт з шаблону"""
        template = self.get_object()
        serializer = ReportCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Створити звіт
            report_data = serializer.validated_data
            report_data['template'] = template
            report_data['user'] = request.user
            report_data['report_type'] = template.report_type
            report_data['format'] = template.format
            
            report = Report.objects.create(**report_data)
            
            # Створити дані звіту
            if 'data' in report_data:
                ReportData.objects.create(
                    report=report,
                    data=report_data['data']
                )
            
            return Response(
                ReportSerializer(report).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet для звітів"""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'report_type', 'format']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'generated_at', 'signed_at', 'submitted_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фільтрація по користувачу"""
        return Report.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Створити звіт для поточного користувача"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Згенерувати звіт"""
        report = self.get_object()
        serializer = ReportGenerateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Оновити дані звіту якщо надано
            if 'data' in serializer.validated_data:
                report_data, created = ReportData.objects.get_or_create(
                    report=report,
                    defaults={'data': serializer.validated_data['data']}
                )
                if not created:
                    report_data.data = serializer.validated_data['data']
                    report_data.save()
            
            # Оновити формат якщо надано
            if 'format' in serializer.validated_data:
                report.format = serializer.validated_data['format']
                report.save()
            
            # Запустити генерацію
            generate_report.delay(report.id)
            
            return Response({'message': 'Генерація звіту запущена'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        """Підписати звіт"""
        report = self.get_object()
        serializer = ReportSignSerializer(data=request.data)
        
        if serializer.is_valid():
            # Створити підпис
            signature_data = serializer.validated_data
            signature_data['report'] = report
            
            signature = DigitalSignature.objects.create(**signature_data)
            
            # Запустити підпис
            sign_report.delay(report.id, signature.id)
            
            return Response({'message': 'Підпис звіту запущено'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Подати звіт до ДПС"""
        report = self.get_object()
        serializer = ReportSubmitSerializer(data=request.data)
        
        if serializer.is_valid():
            # Створити запис про подачу
            submission_data = serializer.validated_data
            submission_data['report'] = report
            submission_data['submission_id'] = f"SUBMIT-{report.id}-{int(timezone.now().timestamp())}"
            
            submission = ReportSubmission.objects.create(**submission_data)
            
            # Запустити подачу
            submit_report.delay(report.id, submission.id)
            
            return Response({'message': 'Подача звіту запущена'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Завантажити звіт"""
        report = self.get_object()
        
        if report.generated_file:
            from django.http import FileResponse
            return FileResponse(
                report.generated_file,
                as_attachment=True,
                filename=f"{report.name}.{report.format}"
            )
        
        return Response(
            {'error': 'Файл звіту не знайдено'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=True, methods=['get'])
    def download_signed(self, request, pk=None):
        """Завантажити підписаний звіт"""
        report = self.get_object()
        
        if report.signed_file:
            from django.http import FileResponse
            return FileResponse(
                report.signed_file,
                as_attachment=True,
                filename=f"{report.name}_signed.{report.format}"
            )
        
        return Response(
            {'error': 'Підписаний файл звіту не знайдено'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика звітів"""
        user_reports = self.get_queryset()
        
        # Загальна статистика
        total_reports = user_reports.count()
        
        # Статистика по статусах
        status_stats = user_reports.values('status').annotate(
            count=Count('id')
        )
        
        # Статистика по типах
        type_stats = user_reports.values('report_type').annotate(
            count=Count('id')
        )
        
        # Статистика за останній місяць
        last_month = timezone.now() - timedelta(days=30)
        monthly_stats = user_reports.filter(
            created_at__gte=last_month
        ).count()
        
        return Response({
            'total_reports': total_reports,
            'status_breakdown': list(status_stats),
            'type_breakdown': list(type_stats),
            'monthly_reports': monthly_stats
        })


class ReportDataViewSet(viewsets.ModelViewSet):
    """ViewSet для даних звітів"""
    queryset = ReportData.objects.all()
    serializer_class = ReportDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['report']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фільтрація по користувачу"""
        return ReportData.objects.filter(report__user=self.request.user)


class DigitalSignatureViewSet(viewsets.ModelViewSet):
    """ViewSet для цифрових підписів"""
    queryset = DigitalSignature.objects.all()
    serializer_class = DigitalSignatureSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['signature_type', 'is_valid', 'report']
    ordering_fields = ['signed_at']
    ordering = ['-signed_at']
    
    def get_queryset(self):
        """Фільтрація по користувачу"""
        return DigitalSignature.objects.filter(report__user=self.request.user)


class ReportSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для подачі звітів"""
    queryset = ReportSubmission.objects.all()
    serializer_class = ReportSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'report']
    ordering_fields = ['submitted_at', 'response_at']
    ordering = ['-submitted_at']
    
    def get_queryset(self):
        """Фільтрація по користувачу"""
        return ReportSubmission.objects.filter(report__user=self.request.user)
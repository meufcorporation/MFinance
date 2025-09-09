from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta

from .models import NotificationTemplate, Notification, NotificationPreference, NotificationLog
from .serializers import (
    NotificationTemplateSerializer, NotificationSerializer,
    NotificationPreferenceSerializer, NotificationLogSerializer,
    NotificationCreateSerializer, NotificationStatsSerializer
)


class NotificationTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NotificationTemplate.objects.filter(is_active=True)
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'template_type']
    filterset_fields = ['template_type', 'channel']
    ordering_fields = ['name', 'template_type', 'created_at']
    ordering = ['template_type', 'name']


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.none()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'body']
    filterset_fields = ['status', 'channel', 'priority', 'template']
    ordering_fields = ['created_at', 'scheduled_at', 'sent_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Кількість непрочитаних нотифікацій"""
        count = self.get_queryset().filter(status='pending').count()
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Останні нотифікації"""
        recent = self.get_queryset().order_by('-created_at')[:10]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика нотифікацій"""
        queryset = self.get_queryset()
        
        stats = queryset.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            sent=Count('id', filter=Q(status='sent')),
            failed=Count('id', filter=Q(status='failed')),
            delivered=Count('id', filter=Q(status='delivered'))
        )
        
        # Розраховуємо успішність
        total_sent = stats['sent'] + stats['delivered']
        success_rate = (stats['delivered'] / total_sent * 100) if total_sent > 0 else 0
        
        stats['success_rate'] = round(success_rate, 2)
        
        serializer = NotificationStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Позначити як прочитане"""
        notification = self.get_object()
        notification.status = 'delivered'
        notification.delivered_at = timezone.now()
        notification.save()
        
        # Логуємо дію
        NotificationLog.objects.create(
            notification=notification,
            action='marked_read',
            details={'marked_by': request.user.id}
        )
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Повторити відправку"""
        notification = self.get_object()
        
        if notification.status not in ['failed', 'pending']:
            return Response(
                {'error': 'Можна повторити тільки невдалі або очікуючі нотифікації'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notification.status = 'pending'
        notification.retry_count += 1
        notification.error_message = ''
        notification.save()
        
        # Логуємо дію
        NotificationLog.objects.create(
            notification=notification,
            action='retry',
            details={'retry_count': notification.retry_count}
        )
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = NotificationPreference.objects.none()
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_preferences(self, request):
        """Мої налаштування нотифікацій"""
        try:
            preferences = self.get_queryset().get()
            serializer = self.get_serializer(preferences)
            return Response(serializer.data)
        except NotificationPreference.DoesNotExist:
            # Створюємо налаштування за замовчуванням
            preferences = NotificationPreference.objects.create(user=request.user)
            serializer = self.get_serializer(preferences)
            return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_preferences(self, request):
        """Оновити налаштування нотифікацій"""
        try:
            preferences = self.get_queryset().get()
            serializer = self.get_serializer(preferences, data=request.data, partial=True)
        except NotificationPreference.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NotificationLog.objects.none()
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'action']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return NotificationLog.objects.filter(notification__user=self.request.user)
from rest_framework import serializers
from .models import NotificationTemplate, Notification, NotificationPreference, NotificationLog


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'template_type', 'channel', 'subject_template',
            'body_template', 'is_active', 'variables', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'template', 'template_name', 'user_name', 'subject',
            'body', 'channel', 'priority', 'status', 'context_data', 'external_id',
            'scheduled_at', 'sent_at', 'delivered_at', 'error_message',
            'retry_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'email_enabled', 'sms_enabled', 'push_enabled', 'telegram_enabled',
            'quiet_hours_start', 'quiet_hours_end', 'timezone', 'tax_deadline_enabled',
            'payment_reminder_enabled', 'report_enabled', 'system_alert_enabled',
            'daily_digest', 'weekly_digest', 'monthly_digest', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = ['id', 'notification', 'action', 'details', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationCreateSerializer(serializers.Serializer):
    """Серіалізатор для створення нотифікації"""
    template_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    context_data = serializers.JSONField(default=dict)
    priority = serializers.ChoiceField(choices=Notification.PRIORITY_CHOICES, default='normal')
    scheduled_at = serializers.DateTimeField(required=False)
    
    def create(self, validated_data):
        template = NotificationTemplate.objects.get(id=validated_data['template_id'])
        user = User.objects.get(id=validated_data['user_id'])
        
        # Рендеримо шаблон
        subject = template.subject_template.format(**validated_data['context_data'])
        body = template.body_template.format(**validated_data['context_data'])
        
        notification = Notification.objects.create(
            user=user,
            template=template,
            subject=subject,
            body=body,
            channel=template.channel,
            priority=validated_data['priority'],
            context_data=validated_data['context_data'],
            scheduled_at=validated_data.get('scheduled_at', timezone.now())
        )
        
        return notification


class NotificationStatsSerializer(serializers.Serializer):
    """Статистика нотифікацій"""
    total = serializers.IntegerField()
    pending = serializers.IntegerField()
    sent = serializers.IntegerField()
    failed = serializers.IntegerField()
    delivered = serializers.IntegerField()
    success_rate = serializers.FloatField()

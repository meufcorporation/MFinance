from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class NotificationTemplate(models.Model):
    """Шаблони нотифікацій"""
    TEMPLATE_TYPES = [
        ('tax_deadline', 'Дедлайн податку'),
        ('payment_reminder', 'Нагадування про платіж'),
        ('monthly_report', 'Місячний звіт'),
        ('weekly_report', 'Тижневий звіт'),
        ('system_alert', 'Системне сповіщення'),
    ]
    
    CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
        ('telegram', 'Telegram'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Назва шаблону')
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, verbose_name='Тип шаблону')
    channel = models.CharField(max_length=20, choices=CHANNELS, verbose_name='Канал')
    
    # Шаблони
    subject_template = models.CharField(max_length=200, verbose_name='Шаблон теми')
    body_template = models.TextField(verbose_name='Шаблон тіла')
    
    # Налаштування
    is_active = models.BooleanField(default=True, verbose_name='Активний')
    variables = models.JSONField(default=list, verbose_name='Змінні шаблону')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Шаблон нотифікації'
        verbose_name_plural = 'Шаблони нотифікацій'
        ordering = ['template_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_channel_display()})"


class Notification(models.Model):
    """Нотифікації"""
    STATUS_CHOICES = [
        ('pending', 'Очікує'),
        ('sent', 'Відправлено'),
        ('failed', 'Помилка'),
        ('delivered', 'Доставлено'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Низький'),
        ('normal', 'Звичайний'),
        ('high', 'Високий'),
        ('urgent', 'Терміновий'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, related_name='notifications')
    
    # Контент
    subject = models.CharField(max_length=200, verbose_name='Тема')
    body = models.TextField(verbose_name='Тіло')
    
    # Метадані
    channel = models.CharField(max_length=20, verbose_name='Канал')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name='Пріоритет')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    
    # Контекст
    context_data = models.JSONField(default=dict, verbose_name='Контекстні дані')
    external_id = models.CharField(max_length=100, blank=True, verbose_name='Зовнішній ID')
    
    # Час
    scheduled_at = models.DateTimeField(default=timezone.now, verbose_name='Заплановано на')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Відправлено о')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='Доставлено о')
    
    # Помилки
    error_message = models.TextField(blank=True, verbose_name='Повідомлення про помилку')
    retry_count = models.IntegerField(default=0, verbose_name='Кількість спроб')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Нотифікація'
        verbose_name_plural = 'Нотифікації'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['scheduled_at', 'status']),
            models.Index(fields=['template', 'status']),
        ]
    
    def __str__(self):
        return f"{self.subject} - {self.user.username} ({self.status})"


class NotificationPreference(models.Model):
    """Налаштування нотифікацій користувача"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Канали
    email_enabled = models.BooleanField(default=True, verbose_name='Email увімкнено')
    sms_enabled = models.BooleanField(default=False, verbose_name='SMS увімкнено')
    push_enabled = models.BooleanField(default=True, verbose_name='Push увімкнено')
    telegram_enabled = models.BooleanField(default=False, verbose_name='Telegram увімкнено')
    
    # Налаштування часу
    quiet_hours_start = models.TimeField(null=True, blank=True, verbose_name='Початок тихих годин')
    quiet_hours_end = models.TimeField(null=True, blank=True, verbose_name='Кінець тихих годин')
    timezone = models.CharField(max_length=50, default='Europe/Kiev', verbose_name='Часовий пояс')
    
    # Налаштування типів
    tax_deadline_enabled = models.BooleanField(default=True, verbose_name='Дедлайни податків')
    payment_reminder_enabled = models.BooleanField(default=True, verbose_name='Нагадування про платежі')
    report_enabled = models.BooleanField(default=True, verbose_name='Звіти')
    system_alert_enabled = models.BooleanField(default=True, verbose_name='Системні сповіщення')
    
    # Частота
    daily_digest = models.BooleanField(default=False, verbose_name='Щоденний дайджест')
    weekly_digest = models.BooleanField(default=True, verbose_name='Тижневий дайджест')
    monthly_digest = models.BooleanField(default=True, verbose_name='Місячний дайджест')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Налаштування нотифікацій'
        verbose_name_plural = 'Налаштування нотифікацій'
    
    def __str__(self):
        return f"Налаштування {self.user.username}"


class NotificationLog(models.Model):
    """Лог нотифікацій для аудиту"""
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=50, verbose_name='Дія')
    details = models.JSONField(default=dict, verbose_name='Деталі')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Лог нотифікації'
        verbose_name_plural = 'Логи нотифікацій'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification.subject} - {self.action}"
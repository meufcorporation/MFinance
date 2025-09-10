from django.db import models
from django.utils import timezone as django_timezone
from django.contrib.auth import get_user_model
from fop.models import FOPProfile, TaxObligation
from bank_integration.models import BankAccount

User = get_user_model()


class PaymentProvider(models.Model):
    """
    Провайдери платіжних систем (Mono, Privat, Open Banking)
    """
    PROVIDER_CHOICES = [
        ('mono', 'Mono Bank'),
        ('privat', 'PrivatBank'),
        ('open_banking', 'Open Banking'),
        ('manual', 'Ручна сплата'),
    ]
    
    name = models.CharField(max_length=50, choices=PROVIDER_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    api_url = models.URLField(blank=True, null=True)
    webhook_url = models.URLField(blank=True, null=True)
    credentials = models.JSONField(default=dict, blank=True)  # API ключі, токени
    settings = models.JSONField(default=dict, blank=True)  # Налаштування провайдера
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments_provider'
        verbose_name = 'Провайдер платежів'
        verbose_name_plural = 'Провайдери платежів'
    
    def __str__(self):
        return self.display_name


class PaymentMethod(models.Model):
    """
    Способи оплати (карта, IBAN, готівка)
    """
    METHOD_CHOICES = [
        ('card', 'Банківська карта'),
        ('iban', 'IBAN переказ'),
        ('cash', 'Готівка'),
        ('crypto', 'Криптовалюта'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=20, choices=METHOD_CHOICES)
    provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE, related_name='payment_methods')
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, blank=True, null=True)
    
    # Дані для оплати
    card_number = models.CharField(max_length=20, blank=True, null=True)  # Зашифрований
    card_holder = models.CharField(max_length=100, blank=True, null=True)
    iban = models.CharField(max_length=34, blank=True, null=True)
    
    # Налаштування
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    auto_pay_enabled = models.BooleanField(default=False)  # Автоматична сплата
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments_method'
        verbose_name = 'Спосіб оплати'
        verbose_name_plural = 'Способи оплати'
        unique_together = ['user', 'method_type', 'provider']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_method_type_display()}"


class Payment(models.Model):
    """
    Платежі (податки, штрафи, інші зобов'язання)
    """
    STATUS_CHOICES = [
        ('pending', 'Очікує'),
        ('processing', 'Обробляється'),
        ('completed', 'Завершено'),
        ('failed', 'Помилка'),
        ('cancelled', 'Скасовано'),
        ('refunded', 'Повернено'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('tax', 'Податок'),
        ('fine', 'Штраф'),
        ('fee', 'Збір'),
        ('other', 'Інше'),
    ]
    
    # Основна інформація
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    fop_profile = models.ForeignKey(FOPProfile, on_delete=models.CASCADE, related_name='payments')
    tax_obligation = models.ForeignKey(TaxObligation, on_delete=models.CASCADE, related_name='payments', blank=True, null=True)
    
    # Платіжна інформація
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name='payments')
    provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE, related_name='payments')
    
    # Деталі платежу
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='UAH')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='tax')
    description = models.TextField()
    
    # Статус та дати
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    # Зовнішні ID
    external_payment_id = models.CharField(max_length=100, blank=True, null=True)  # ID від провайдера
    external_transaction_id = models.CharField(max_length=100, blank=True, null=True)  # ID транзакції
    
    # Додаткова інформація
    metadata = models.JSONField(default=dict, blank=True)  # Додаткові дані від провайдера
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'payments_payment'
        verbose_name = 'Платіж'
        verbose_name_plural = 'Платежі'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Платіж {self.id} - {self.amount} {self.currency} ({self.status})"


class PaymentSchedule(models.Model):
    """
    Розклад автоматичних платежів
    """
    FREQUENCY_CHOICES = [
        ('monthly', 'Щомісячно'),
        ('quarterly', 'Щоквартально'),
        ('yearly', 'Щорічно'),
        ('custom', 'Користувацький'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_schedules')
    fop_profile = models.ForeignKey(FOPProfile, on_delete=models.CASCADE, related_name='payment_schedules')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name='payment_schedules')
    
    # Налаштування розкладу
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    cron_expression = models.CharField(max_length=100, blank=True, null=True)  # Для custom
    
    # Параметри платежу
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    payment_type = models.CharField(max_length=20, choices=Payment.PAYMENT_TYPE_CHOICES, default='tax')
    
    # Статус
    is_active = models.BooleanField(default=True)
    next_payment_date = models.DateTimeField(blank=True, null=True)
    last_payment_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments_schedule'
        verbose_name = 'Розклад платежів'
        verbose_name_plural = 'Розклади платежів'
    
    def __str__(self):
        return f"{self.name} - {self.frequency}"


class PaymentWebhook(models.Model):
    """
    Webhook'и від платіжних провайдерів
    """
    provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE, related_name='webhooks')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='webhooks', blank=True, null=True)
    
    # Webhook дані
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    signature = models.CharField(max_length=500, blank=True, null=True)
    
    # Статус обробки
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    
    class Meta:
        db_table = 'payments_webhook'
        verbose_name = 'Webhook платежу'
        verbose_name_plural = 'Webhook\'и платежів'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Webhook {self.id} - {self.event_type}"


class PaymentLog(models.Model):
    """
    Логи платіжних операцій
    """
    LOG_LEVEL_CHOICES = [
        ('info', 'Інформація'),
        ('warning', 'Попередження'),
        ('error', 'Помилка'),
        ('debug', 'Відладка'),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(max_length=20, choices=LOG_LEVEL_CHOICES, default='info')
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    
    class Meta:
        db_table = 'payments_log'
        verbose_name = 'Лог платежу'
        verbose_name_plural = 'Логи платежів'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Log {self.id} - {self.level}"


class PaymentTemplate(models.Model):
    """
    Шаблони платежів для швидкого створення
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_templates')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Параметри шаблону
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    payment_type = models.CharField(max_length=20, choices=Payment.PAYMENT_TYPE_CHOICES, default='tax')
    description_template = models.TextField()
    
    # Налаштування
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)  # Публічний шаблон
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments_template'
        verbose_name = 'Шаблон платежу'
        verbose_name_plural = 'Шаблони платежів'
    
    def __str__(self):
        return self.name
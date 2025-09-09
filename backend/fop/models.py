from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class FOPProfile(models.Model):
    """Профіль ФОП"""
    TAX_GROUPS = [
        ('1', '1 група - до 300 тис. грн'),
        ('2', '2 група - до 1.5 млн грн'),
        ('3', '3 група - до 7 млн грн'),
    ]
    
    TAX_SYSTEMS = [
        ('single', 'Єдиний податок'),
        ('general', 'Загальна система'),
        ('simplified', 'Спрощена система'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fop_profile')
    first_name = models.CharField(max_length=100, verbose_name='Ім\'я')
    last_name = models.CharField(max_length=100, verbose_name='Прізвище')
    middle_name = models.CharField(max_length=100, blank=True, verbose_name='По батькові')
    tax_number = models.CharField(max_length=10, unique=True, verbose_name='ІПН')
    registration_date = models.DateField(verbose_name='Дата реєстрації')
    tax_group = models.CharField(max_length=1, choices=TAX_GROUPS, verbose_name='Податкова група')
    tax_system = models.CharField(max_length=20, choices=TAX_SYSTEMS, verbose_name='Система оподаткування')
    
    # Банківські реквізити
    bank_name = models.CharField(max_length=100, verbose_name='Назва банку')
    bank_code = models.CharField(max_length=10, verbose_name='МФО')
    account_number = models.CharField(max_length=29, verbose_name='Номер рахунку')
    
    # Контактна інформація
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    address = models.TextField(blank=True, verbose_name='Адреса')
    
    # Налаштування
    is_active = models.BooleanField(default=True, verbose_name='Активний')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Профіль ФОП'
        verbose_name_plural = 'Профілі ФОП'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name} (ІПН: {self.tax_number})"


class TaxPeriod(models.Model):
    """Податкові періоди"""
    PERIOD_TYPES = [
        ('monthly', 'Місячний'),
        ('quarterly', 'Квартальний'),
        ('yearly', 'Річний'),
    ]
    
    fop_profile = models.ForeignKey(FOPProfile, on_delete=models.CASCADE, related_name='tax_periods')
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPES, verbose_name='Тип періоду')
    year = models.IntegerField(verbose_name='Рік')
    month = models.IntegerField(null=True, blank=True, verbose_name='Місяць')
    quarter = models.IntegerField(null=True, blank=True, verbose_name='Квартал')
    
    # Дедлайни
    declaration_deadline = models.DateField(verbose_name='Дедлайн подачі декларації')
    payment_deadline = models.DateField(verbose_name='Дедлайн сплати')
    
    # Статуси
    declaration_submitted = models.BooleanField(default=False, verbose_name='Декларація подана')
    payment_made = models.BooleanField(default=False, verbose_name='Сплачено')
    
    # Суми
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Сума податку')
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Сплачена сума')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Податковий період'
        verbose_name_plural = 'Податкові періоди'
        ordering = ['-year', '-month', '-quarter']
        unique_together = ['fop_profile', 'period_type', 'year', 'month', 'quarter']
    
    def __str__(self):
        if self.period_type == 'monthly':
            return f"{self.year}-{self.month:02d}"
        elif self.period_type == 'quarterly':
            return f"{self.year} Q{self.quarter}"
        else:
            return str(self.year)


class FOPSettings(models.Model):
    """Налаштування ФОП"""
    NOTIFICATION_CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
        ('telegram', 'Telegram'),
    ]
    
    fop_profile = models.OneToOneField(FOPProfile, on_delete=models.CASCADE, related_name='settings')
    
    # Налаштування нотифікацій
    notification_channels = models.JSONField(default=list, verbose_name='Канали нотифікацій')
    notify_before_deadline = models.IntegerField(default=7, verbose_name='Сповіщати за днів до дедлайну')
    notify_weekly = models.BooleanField(default=True, verbose_name='Тижневі звіти')
    notify_monthly = models.BooleanField(default=True, verbose_name='Місячні звіти')
    
    # Налаштування розрахунків
    auto_calculate_tax = models.BooleanField(default=True, verbose_name='Автоматичний розрахунок податку')
    include_vat = models.BooleanField(default=False, verbose_name='Включати ПДВ')
    
    # Налаштування експорту
    export_format = models.CharField(max_length=10, default='excel', verbose_name='Формат експорту')
    include_receipts = models.BooleanField(default=True, verbose_name='Включати квитанції')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Налаштування ФОП'
        verbose_name_plural = 'Налаштування ФОП'
    
    def __str__(self):
        return f"Налаштування {self.fop_profile}"


class TaxObligation(models.Model):
    """Податкові зобов'язання"""
    OBLIGATION_TYPES = [
        ('single_tax', 'Єдиний податок'),
        ('esv', 'ЄСВ'),
        ('vat', 'ПДВ'),
        ('income_tax', 'Податок на доходи'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Очікує'),
        ('calculated', 'Розраховано'),
        ('paid', 'Сплачено'),
        ('overdue', 'Прострочено'),
    ]
    
    fop_profile = models.ForeignKey(FOPProfile, on_delete=models.CASCADE, related_name='tax_obligations')
    tax_period = models.ForeignKey(TaxPeriod, on_delete=models.CASCADE, related_name='obligations')
    obligation_type = models.CharField(max_length=20, choices=OBLIGATION_TYPES, verbose_name='Тип зобов\'язання')
    
    # Суми
    calculated_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Розрахована сума')
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Сплачена сума')
    
    # Дедлайни
    payment_deadline = models.DateField(verbose_name='Дедлайн сплати')
    
    # Статус
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    
    # Метадані
    calculation_data = models.JSONField(default=dict, verbose_name='Дані для розрахунку')
    payment_reference = models.CharField(max_length=100, blank=True, verbose_name='Референс платежу')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Податкове зобов\'язання'
        verbose_name_plural = 'Податкові зобов\'язання'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_obligation_type_display()} - {self.tax_period} ({self.status})"
    
    @property
    def remaining_amount(self):
        return self.calculated_amount - self.paid_amount
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.payment_deadline < timezone.now().date() and self.status != 'paid'
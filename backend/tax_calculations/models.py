from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class TaxRate(models.Model):
    """Податкові ставки"""
    TAX_TYPES = [
        ('single_tax', 'Єдиний податок'),
        ('esv', 'ЄСВ'),
        ('vat', 'ПДВ'),
        ('income_tax', 'Податок на доходи'),
    ]
    
    FOP_GROUPS = [
        ('1', '1 група'),
        ('2', '2 група'),
        ('3', '3 група'),
    ]
    
    tax_type = models.CharField(max_length=20, choices=TAX_TYPES, verbose_name='Тип податку')
    fop_group = models.CharField(max_length=1, choices=FOP_GROUPS, verbose_name='Група ФОП')
    
    # Ставки
    rate_percent = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Ставка (%)')
    min_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Мінімальна сума')
    max_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='Максимальна сума')
    
    # Період дії
    valid_from = models.DateField(verbose_name='Діє з')
    valid_to = models.DateField(null=True, blank=True, verbose_name='Діє до')
    
    # Додаткові параметри
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    description = models.TextField(blank=True, verbose_name='Опис')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Податкова ставка'
        verbose_name_plural = 'Податкові ставки'
        ordering = ['tax_type', 'fop_group', 'valid_from']
        unique_together = ['tax_type', 'fop_group', 'valid_from']
    
    def __str__(self):
        return f"{self.get_tax_type_display()} - {self.get_fop_group_display()} ({self.rate_percent}%)"


class TaxCalculation(models.Model):
    """Розрахунки податків"""
    CALCULATION_TYPES = [
        ('monthly', 'Місячний'),
        ('quarterly', 'Квартальний'),
        ('yearly', 'Річний'),
        ('manual', 'Ручний'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Чернетка'),
        ('calculated', 'Розраховано'),
        ('approved', 'Затверджено'),
        ('paid', 'Сплачено'),
    ]
    
    fop_profile = models.ForeignKey('fop.FOPProfile', on_delete=models.CASCADE, related_name='tax_calculations')
    calculation_type = models.CharField(max_length=20, choices=CALCULATION_TYPES, verbose_name='Тип розрахунку')
    
    # Період
    year = models.IntegerField(verbose_name='Рік')
    month = models.IntegerField(null=True, blank=True, verbose_name='Місяць')
    quarter = models.IntegerField(null=True, blank=True, verbose_name='Квартал')
    
    # Доходи та витрати
    total_income = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Загальний дохід')
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Загальні витрати')
    taxable_income = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Оподатковуваний дохід')
    
    # Розраховані податки
    single_tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Єдиний податок')
    esv_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='ЄСВ')
    vat_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='ПДВ')
    income_tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Податок на доходи')
    
    # Загальна сума
    total_tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Загальна сума податків')
    
    # Статус
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    
    # Метадані
    calculation_data = models.JSONField(default=dict, verbose_name='Дані розрахунку')
    notes = models.TextField(blank=True, verbose_name='Примітки')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Розрахунок податків'
        verbose_name_plural = 'Розрахунки податків'
        ordering = ['-year', '-month', '-quarter']
        unique_together = ['fop_profile', 'calculation_type', 'year', 'month', 'quarter']
    
    def __str__(self):
        period = f"{self.year}"
        if self.month:
            period = f"{self.year}-{self.month:02d}"
        elif self.quarter:
            period = f"{self.year} Q{self.quarter}"
        return f"{self.fop_profile} - {period} ({self.get_status_display()})"
    
    def calculate_taxes(self):
        """Розрахувати податки"""
        from .services import TaxCalculationService
        
        service = TaxCalculationService()
        return service.calculate_taxes(self)


class TaxPayment(models.Model):
    """Платежі податків"""
    PAYMENT_TYPES = [
        ('single_tax', 'Єдиний податок'),
        ('esv', 'ЄСВ'),
        ('vat', 'ПДВ'),
        ('income_tax', 'Податок на доходи'),
        ('penalty', 'Штраф'),
        ('fine', 'Пеня'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Очікує'),
        ('processing', 'Обробляється'),
        ('completed', 'Завершено'),
        ('failed', 'Помилка'),
        ('cancelled', 'Скасовано'),
    ]
    
    tax_calculation = models.ForeignKey(TaxCalculation, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, verbose_name='Тип платежу')
    
    # Суми
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Сума')
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Сплачена сума')
    
    # Дедлайни
    due_date = models.DateField(verbose_name='Термін сплати')
    paid_date = models.DateField(null=True, blank=True, verbose_name='Дата сплати')
    
    # Статус
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending', verbose_name='Статус')
    
    # Платіжні дані
    payment_reference = models.CharField(max_length=100, blank=True, verbose_name='Референс платежу')
    bank_transaction_id = models.CharField(max_length=100, blank=True, verbose_name='ID банківської транзакції')
    
    # Метадані
    payment_data = models.JSONField(default=dict, verbose_name='Дані платежу')
    error_message = models.TextField(blank=True, verbose_name='Повідомлення про помилку')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Платіж податку'
        verbose_name_plural = 'Платежі податків'
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.amount} UAH ({self.get_status_display()})"
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.status != 'completed'
    
    @property
    def remaining_amount(self):
        return self.amount - self.paid_amount


class TaxRule(models.Model):
    """Правила розрахунку податків"""
    RULE_TYPES = [
        ('income_threshold', 'Поріг доходу'),
        ('expense_category', 'Категорія витрат'),
        ('vat_exemption', 'ПДВ пільга'),
        ('esv_exemption', 'ЄСВ пільга'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Назва правила')
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES, verbose_name='Тип правила')
    fop_group = models.CharField(max_length=1, choices=TaxRate.FOP_GROUPS, verbose_name='Група ФОП')
    
    # Умови
    condition = models.JSONField(verbose_name='Умова')
    action = models.JSONField(verbose_name='Дія')
    
    # Пріоритет
    priority = models.IntegerField(default=0, verbose_name='Пріоритет')
    
    # Статус
    is_active = models.BooleanField(default=True, verbose_name='Активне')
    description = models.TextField(blank=True, verbose_name='Опис')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Правило розрахунку податків'
        verbose_name_plural = 'Правила розрахунку податків'
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"


class TaxExemption(models.Model):
    """Податкові пільги"""
    EXEMPTION_TYPES = [
        ('vat', 'ПДВ'),
        ('esv', 'ЄСВ'),
        ('single_tax', 'Єдиний податок'),
    ]
    
    fop_profile = models.ForeignKey('fop.FOPProfile', on_delete=models.CASCADE, related_name='tax_exemptions')
    exemption_type = models.CharField(max_length=20, choices=EXEMPTION_TYPES, verbose_name='Тип пільги')
    
    # Період дії
    valid_from = models.DateField(verbose_name='Діє з')
    valid_to = models.DateField(null=True, blank=True, verbose_name='Діє до')
    
    # Параметри
    exemption_percent = models.DecimalField(max_digits=5, decimal_places=2, default=100, verbose_name='Відсоток пільги')
    max_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='Максимальна сума')
    
    # Статус
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    description = models.TextField(blank=True, verbose_name='Опис')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Податкова пільга'
        verbose_name_plural = 'Податкові пільги'
        ordering = ['-valid_from']
    
    def __str__(self):
        return f"{self.fop_profile} - {self.get_exemption_type_display()} ({self.exemption_percent}%)"
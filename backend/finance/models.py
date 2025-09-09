from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Account(models.Model):
    """Банківські рахунки користувачів"""
    ACCOUNT_TYPES = [
        ('checking', 'Розрахунковий'),
        ('savings', 'Депозитний'),
        ('credit', 'Кредитний'),
        ('investment', 'Інвестиційний'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100, verbose_name='Назва рахунку')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, verbose_name='Тип рахунку')
    bank_name = models.CharField(max_length=100, verbose_name='Назва банку')
    account_number = models.CharField(max_length=50, blank=True, verbose_name='Номер рахунку')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Баланс')
    currency = models.CharField(max_length=3, default='UAH', verbose_name='Валюта')
    is_active = models.BooleanField(default=True, verbose_name='Активний')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Рахунок'
        verbose_name_plural = 'Рахунки'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.bank_name})"


class Category(models.Model):
    """Категорії транзакцій"""
    CATEGORY_TYPES = [
        ('income', 'Дохід'),
        ('expense', 'Витрата'),
        ('transfer', 'Переказ'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100, verbose_name='Назва категорії')
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, verbose_name='Тип категорії')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    color = models.CharField(max_length=7, default='#3B82F6', verbose_name='Колір')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Іконка')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['category_type', 'name']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return self.name


class Transaction(models.Model):
    """Транзакції"""
    TRANSACTION_TYPES = [
        ('income', 'Дохід'),
        ('expense', 'Витрата'),
        ('transfer', 'Переказ'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Сума')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name='Тип транзакції')
    description = models.TextField(verbose_name='Опис')
    merchant = models.CharField(max_length=200, blank=True, verbose_name='Мерчант')
    date = models.DateTimeField(verbose_name='Дата')
    
    # Для переказів
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, related_name='incoming_transfers')
    
    # Метадані
    external_id = models.CharField(max_length=100, blank=True, verbose_name='Зовнішній ID')
    tags = models.JSONField(default=list, blank=True, verbose_name='Теги')
    notes = models.TextField(blank=True, verbose_name='Нотатки')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Транзакція'
        verbose_name_plural = 'Транзакції'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['account', 'date']),
            models.Index(fields=['category', 'date']),
        ]
    
    def __str__(self):
        return f"{self.description} - {self.amount} {self.account.currency}"


class Budget(models.Model):
    """Бюджети"""
    BUDGET_PERIODS = [
        ('monthly', 'Щомісячний'),
        ('weekly', 'Тижневий'),
        ('yearly', 'Річний'),
        ('custom', 'Користувацький'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    name = models.CharField(max_length=100, verbose_name='Назва бюджету')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Сума')
    period = models.CharField(max_length=20, choices=BUDGET_PERIODS, verbose_name='Період')
    start_date = models.DateField(verbose_name='Дата початку')
    end_date = models.DateField(verbose_name='Дата закінчення')
    is_active = models.BooleanField(default=True, verbose_name='Активний')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Бюджет'
        verbose_name_plural = 'Бюджети'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.amount} {self.period}"


class Rule(models.Model):
    """Правила автоматичної категоризації"""
    RULE_TYPES = [
        ('description', 'За описом'),
        ('merchant', 'За мерчантом'),
        ('amount', 'За сумою'),
        ('account', 'За рахунком'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rules')
    name = models.CharField(max_length=100, verbose_name='Назва правила')
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES, verbose_name='Тип правила')
    condition = models.CharField(max_length=500, verbose_name='Умова')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='rules')
    priority = models.IntegerField(default=0, verbose_name='Пріоритет')
    is_active = models.BooleanField(default=True, verbose_name='Активне')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Правило'
        verbose_name_plural = 'Правила'
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.name} -> {self.category.name}"


class ImportJob(models.Model):
    """Завдання імпорту CSV"""
    STATUS_CHOICES = [
        ('pending', 'Очікує'),
        ('processing', 'Обробляється'),
        ('completed', 'Завершено'),
        ('failed', 'Помилка'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='import_jobs')
    filename = models.CharField(max_length=255, verbose_name='Назва файлу')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    total_rows = models.IntegerField(default=0, verbose_name='Всього рядків')
    processed_rows = models.IntegerField(default=0, verbose_name='Оброблено рядків')
    error_message = models.TextField(blank=True, verbose_name='Повідомлення про помилку')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Завдання імпорту'
        verbose_name_plural = 'Завдання імпорту'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.filename} - {self.status}"
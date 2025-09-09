from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Bank(models.Model):
    """Банки для інтеграції"""
    BANK_TYPES = [
        ('mono', 'Монобанк'),
        ('privat', 'ПриватБанк'),
        ('oschad', 'Ощадбанк'),
        ('raiffeisen', 'Райффайзен Банк'),
        ('ukrsib', 'УкрСиббанк'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Назва банку')
    code = models.CharField(max_length=10, unique=True, verbose_name='Код банку')
    bank_type = models.CharField(max_length=20, choices=BANK_TYPES, verbose_name='Тип банку')
    
    # API налаштування
    api_base_url = models.URLField(verbose_name='Базовий URL API')
    auth_url = models.URLField(verbose_name='URL авторизації')
    token_url = models.URLField(verbose_name='URL отримання токену')
    webhook_url = models.URLField(blank=True, verbose_name='URL webhook')
    
    # Налаштування OAuth
    client_id = models.CharField(max_length=255, verbose_name='Client ID')
    client_secret = models.CharField(max_length=255, verbose_name='Client Secret')
    redirect_uri = models.URLField(verbose_name='Redirect URI')
    scope = models.TextField(default='read', verbose_name='Scope')
    
    # Статус
    is_active = models.BooleanField(default=True, verbose_name='Активний')
    is_sandbox = models.BooleanField(default=True, verbose_name='Sandbox режим')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Банк'
        verbose_name_plural = 'Банки'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({'Sandbox' if self.is_sandbox else 'Production'})"


class BankAccount(models.Model):
    """Банківські рахунки користувачів"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='accounts')
    
    # Дані рахунку
    account_id = models.CharField(max_length=100, verbose_name='ID рахунку в банку')
    account_number = models.CharField(max_length=29, verbose_name='Номер рахунку')
    account_type = models.CharField(max_length=20, verbose_name='Тип рахунку')
    currency = models.CharField(max_length=3, default='UAH', verbose_name='Валюта')
    
    # Баланс
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Баланс')
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Кредитний ліміт')
    
    # Статус
    is_active = models.BooleanField(default=True, verbose_name='Активний')
    last_sync = models.DateTimeField(null=True, blank=True, verbose_name='Остання синхронізація')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Банківський рахунок'
        verbose_name_plural = 'Банківські рахунки'
        unique_together = ['user', 'bank', 'account_id']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.bank.name} ({self.account_number})"


class BankToken(models.Model):
    """Токени доступу до банківських API"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_tokens')
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='tokens')
    
    # Токени
    access_token = models.TextField(verbose_name='Access Token')
    refresh_token = models.TextField(blank=True, verbose_name='Refresh Token')
    token_type = models.CharField(max_length=20, default='Bearer', verbose_name='Тип токену')
    
    # Час життя
    expires_at = models.DateTimeField(verbose_name='Термін дії')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Статус
    is_active = models.BooleanField(default=True, verbose_name='Активний')
    
    class Meta:
        verbose_name = 'Банківський токен'
        verbose_name_plural = 'Банківські токени'
        unique_together = ['user', 'bank']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.bank.name} Token"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at


class BankTransaction(models.Model):
    """Транзакції з банківських API"""
    TRANSACTION_TYPES = [
        ('income', 'Дохід'),
        ('expense', 'Витрата'),
        ('transfer', 'Переказ'),
    ]
    
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='bank_transactions')
    external_id = models.CharField(max_length=100, verbose_name='ID в банку')
    
    # Дані транзакції
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Сума')
    currency = models.CharField(max_length=3, default='UAH', verbose_name='Валюта')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name='Тип транзакції')
    
    # Опис
    description = models.TextField(verbose_name='Опис')
    merchant = models.CharField(max_length=255, blank=True, verbose_name='Мерчант')
    mcc_code = models.CharField(max_length=4, blank=True, verbose_name='MCC код')
    
    # Дати
    transaction_date = models.DateTimeField(verbose_name='Дата транзакції')
    processed_date = models.DateTimeField(verbose_name='Дата обробки')
    
    # Статус
    is_processed = models.BooleanField(default=False, verbose_name='Оброблено')
    is_categorized = models.BooleanField(default=False, verbose_name='Категоризовано')
    
    # Зв'язок з внутрішньою транзакцією
    internal_transaction = models.ForeignKey(
        'finance.Transaction', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='bank_transaction'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Банківська транзакція'
        verbose_name_plural = 'Банківські транзакції'
        unique_together = ['bank_account', 'external_id']
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['bank_account', 'transaction_date']),
            models.Index(fields=['external_id']),
            models.Index(fields=['is_processed']),
        ]
    
    def __str__(self):
        return f"{self.bank_account.bank.name} - {self.amount} {self.currency} ({self.transaction_date})"


class BankWebhook(models.Model):
    """Webhook події від банків"""
    WEBHOOK_TYPES = [
        ('transaction', 'Нова транзакція'),
        ('balance', 'Зміна балансу'),
        ('account', 'Зміна рахунку'),
        ('error', 'Помилка'),
    ]
    
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='webhooks')
    webhook_type = models.CharField(max_length=20, choices=WEBHOOK_TYPES, verbose_name='Тип webhook')
    
    # Дані
    payload = models.JSONField(verbose_name='Дані webhook')
    signature = models.CharField(max_length=255, blank=True, verbose_name='Підпис')
    
    # Статус обробки
    is_processed = models.BooleanField(default=False, verbose_name='Оброблено')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='Оброблено о')
    error_message = models.TextField(blank=True, verbose_name='Повідомлення про помилку')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Банківський webhook'
        verbose_name_plural = 'Банківські webhooks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.bank.name} - {self.get_webhook_type_display()} ({self.created_at})"


class BankSyncLog(models.Model):
    """Лог синхронізації з банками"""
    SYNC_TYPES = [
        ('manual', 'Ручна'),
        ('scheduled', 'За розкладом'),
        ('webhook', 'Webhook'),
    ]
    
    STATUS_CHOICES = [
        ('started', 'Розпочато'),
        ('success', 'Успішно'),
        ('failed', 'Помилка'),
        ('partial', 'Частково'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_sync_logs')
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='sync_logs')
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES, verbose_name='Тип синхронізації')
    
    # Результати
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='Статус')
    transactions_imported = models.IntegerField(default=0, verbose_name='Імпортовано транзакцій')
    transactions_updated = models.IntegerField(default=0, verbose_name='Оновлено транзакцій')
    errors_count = models.IntegerField(default=0, verbose_name='Кількість помилок')
    
    # Час
    started_at = models.DateTimeField(verbose_name='Розпочато о')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='Завершено о')
    duration = models.DurationField(null=True, blank=True, verbose_name='Тривалість')
    
    # Деталі
    details = models.JSONField(default=dict, verbose_name='Деталі')
    error_message = models.TextField(blank=True, verbose_name='Повідомлення про помилку')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Лог синхронізації банку'
        verbose_name_plural = 'Логи синхронізації банків'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.bank.name} ({self.status})"
from django.db import models
from django.utils import timezone as django_timezone
from django.contrib.auth import get_user_model
from fop.models import FOPProfile, TaxPeriod, TaxObligation

User = get_user_model()


class ReportTemplate(models.Model):
    """
    Шаблони звітів для різних типів податкової звітності
    """
    REPORT_TYPE_CHOICES = [
        ('single_tax', 'Єдиний податок (ЄП)'),
        ('social_contribution', 'Єдиний соціальний внесок (ЄСВ)'),
        ('vat', 'Податок на додану вартість (ПДВ)'),
        ('income_tax', 'Податок на доходи фізичних осіб'),
        ('custom', 'Користувацький звіт'),
    ]
    
    FORMAT_CHOICES = [
        ('xml', 'XML'),
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Назва шаблону")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES, verbose_name="Тип звіту")
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='xml', verbose_name="Формат")
    
    # Шаблон звіту
    template_content = models.TextField(verbose_name="Вміст шаблону")
    template_file = models.FileField(upload_to='report_templates/', blank=True, null=True, verbose_name="Файл шаблону")
    
    # Налаштування
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    is_public = models.BooleanField(default=False, verbose_name="Публічний")
    version = models.CharField(max_length=20, default='1.0', verbose_name="Версія")
    
    # Метадані
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_report_templates', verbose_name="Створено")
    created_at = models.DateTimeField(default=django_timezone.now, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")
    
    class Meta:
        db_table = 'reports_template'
        verbose_name = 'Шаблон звіту'
        verbose_name_plural = 'Шаблони звітів'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class Report(models.Model):
    """
    Згенеровані звіти
    """
    STATUS_CHOICES = [
        ('draft', 'Чернетка'),
        ('generating', 'Генерується'),
        ('ready', 'Готовий'),
        ('signed', 'Підписано'),
        ('submitted', 'Подано'),
        ('rejected', 'Відхилено'),
        ('error', 'Помилка'),
    ]
    
    # Основна інформація
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', verbose_name="Користувач")
    fop_profile = models.ForeignKey(FOPProfile, on_delete=models.CASCADE, related_name='reports', verbose_name="Профіль ФОП")
    tax_period = models.ForeignKey(TaxPeriod, on_delete=models.CASCADE, related_name='reports', verbose_name="Податковий період")
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='reports', verbose_name="Шаблон")
    
    # Деталі звіту
    name = models.CharField(max_length=200, verbose_name="Назва звіту")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")
    report_type = models.CharField(max_length=50, verbose_name="Тип звіту")
    format = models.CharField(max_length=10, verbose_name="Формат")
    
    # Статус та дати
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    created_at = models.DateTimeField(default=django_timezone.now, verbose_name="Створено")
    generated_at = models.DateTimeField(blank=True, null=True, verbose_name="Згенеровано")
    signed_at = models.DateTimeField(blank=True, null=True, verbose_name="Підписано")
    submitted_at = models.DateTimeField(blank=True, null=True, verbose_name="Подано")
    
    # Файли
    generated_file = models.FileField(upload_to='reports/generated/', blank=True, null=True, verbose_name="Згенерований файл")
    signed_file = models.FileField(upload_to='reports/signed/', blank=True, null=True, verbose_name="Підписаний файл")
    
    # Метадані
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Метадані")
    error_message = models.TextField(blank=True, null=True, verbose_name="Повідомлення про помилку")
    
    class Meta:
        db_table = 'reports_report'
        verbose_name = 'Звіт'
        verbose_name_plural = 'Звіти'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"


class ReportData(models.Model):
    """
    Дані для генерації звітів
    """
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='data', verbose_name="Звіт")
    
    # Дані звіту
    data = models.JSONField(verbose_name="Дані звіту")
    
    # Метадані
    created_at = models.DateTimeField(default=django_timezone.now, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")
    
    class Meta:
        db_table = 'reports_data'
        verbose_name = 'Дані звіту'
        verbose_name_plural = 'Дані звітів'
    
    def __str__(self):
        return f"Дані для звіту {self.report.id}"


class DigitalSignature(models.Model):
    """
    Цифрові підписи для звітів
    """
    SIGNATURE_TYPE_CHOICES = [
        ('kep', 'Кваліфікований електронний підпис (КЕП)'),
        ('diia', 'Дія.Підпис'),
        ('bank_id', 'BankID'),
        ('other', 'Інший'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='signatures', verbose_name="Звіт")
    
    # Інформація про підпис
    signature_type = models.CharField(max_length=20, choices=SIGNATURE_TYPE_CHOICES, verbose_name="Тип підпису")
    signer_name = models.CharField(max_length=200, verbose_name="Ім'я підписанта")
    signer_identifier = models.CharField(max_length=100, verbose_name="Ідентифікатор підписанта")
    certificate_serial = models.CharField(max_length=100, blank=True, null=True, verbose_name="Серійний номер сертифікату")
    
    # Файли підпису
    signature_file = models.FileField(upload_to='reports/signatures/', verbose_name="Файл підпису")
    certificate_file = models.FileField(upload_to='reports/certificates/', blank=True, null=True, verbose_name="Файл сертифікату")
    
    # Метадані
    signed_at = models.DateTimeField(default=django_timezone.now, verbose_name="Підписано")
    is_valid = models.BooleanField(default=True, verbose_name="Валідний")
    validation_message = models.TextField(blank=True, null=True, verbose_name="Повідомлення валідації")
    
    class Meta:
        db_table = 'reports_signature'
        verbose_name = 'Цифровий підпис'
        verbose_name_plural = 'Цифрові підписи'
        ordering = ['-signed_at']
    
    def __str__(self):
        return f"Підпис {self.signature_type} для звіту {self.report.id}"


class ReportSubmission(models.Model):
    """
    Подача звітів до ДПС
    """
    STATUS_CHOICES = [
        ('pending', 'Очікує'),
        ('submitted', 'Подано'),
        ('accepted', 'Прийнято'),
        ('rejected', 'Відхилено'),
        ('error', 'Помилка'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='submissions', verbose_name="Звіт")
    
    # Інформація про подачу
    submission_id = models.CharField(max_length=100, unique=True, verbose_name="ID подачі")
    submission_url = models.URLField(blank=True, null=True, verbose_name="URL подачі")
    
    # Статус та дати
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    submitted_at = models.DateTimeField(blank=True, null=True, verbose_name="Подано")
    response_at = models.DateTimeField(blank=True, null=True, verbose_name="Відповідь отримано")
    
    # Відповідь від ДПС
    response_data = models.JSONField(default=dict, blank=True, verbose_name="Дані відповіді")
    error_message = models.TextField(blank=True, null=True, verbose_name="Повідомлення про помилку")
    
    class Meta:
        db_table = 'reports_submission'
        verbose_name = 'Подача звіту'
        verbose_name_plural = 'Подачі звітів'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Подача звіту {self.report.id} - {self.get_status_display()}"
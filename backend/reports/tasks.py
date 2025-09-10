from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.template.loader import render_to_string
from django.conf import settings
import logging
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import zipfile
import tempfile

from .models import Report, ReportTemplate, ReportData, DigitalSignature, ReportSubmission

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_report(self, report_id):
    """
    Згенерувати звіт
    """
    try:
        report = Report.objects.get(id=report_id)
        
        # Логування початку генерації
        logger.info(f"Початок генерації звіту {report_id}")
        
        # Оновити статус
        report.status = 'generating'
        report.save()
        
        # Отримати дані звіту
        try:
            report_data = ReportData.objects.get(report=report)
            data = report_data.data
        except ReportData.DoesNotExist:
            data = {}
        
        # Генерувати звіт залежно від формату
        if report.format == 'xml':
            file_path = generate_xml_report(report, data)
        elif report.format == 'pdf':
            file_path = generate_pdf_report(report, data)
        elif report.format == 'excel':
            file_path = generate_excel_report(report, data)
        elif report.format == 'json':
            file_path = generate_json_report(report, data)
        else:
            raise ValueError(f'Невідомий формат: {report.format}')
        
        # Зберегти файл
        with open(file_path, 'rb') as f:
            report.generated_file.save(
                f"{report.name}.{report.format}",
                f,
                save=True
            )
        
        # Оновити статус
        report.status = 'ready'
        report.generated_at = timezone.now()
        report.save()
        
        # Очистити тимчасовий файл
        os.unlink(file_path)
        
        logger.info(f"Звіт {report_id} успішно згенеровано")
        
        return {'success': True, 'file_path': report.generated_file.path}
        
    except Report.DoesNotExist:
        logger.error(f'Звіт {report_id} не знайдено')
        return {'success': False, 'error': 'Звіт не знайдено'}
    except Exception as exc:
        logger.error(f'Помилка генерації звіту {report_id}: {exc}')
        
        # Оновити статус звіту
        try:
            report = Report.objects.get(id=report_id)
            report.status = 'error'
            report.error_message = str(exc)
            report.save()
        except:
            pass
        
        # Повторити задачу
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


def generate_xml_report(report, data):
    """
    Згенерувати XML звіт
    """
    template = report.template
    
    # Створити XML структуру
    root = ET.Element("Report")
    root.set("id", str(report.id))
    root.set("type", report.report_type)
    root.set("format", report.format)
    root.set("created_at", report.created_at.isoformat())
    
    # Додати метадані
    metadata = ET.SubElement(root, "Metadata")
    ET.SubElement(metadata, "Name").text = report.name
    ET.SubElement(metadata, "Description").text = report.description or ""
    ET.SubElement(metadata, "FOPProfile").text = str(report.fop_profile.id)
    ET.SubElement(metadata, "TaxPeriod").text = str(report.tax_period.id)
    
    # Додати дані звіту
    data_element = ET.SubElement(root, "Data")
    for key, value in data.items():
        item = ET.SubElement(data_element, "Item")
        item.set("key", key)
        item.text = str(value)
    
    # Зберегти XML
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False)
    tree = ET.ElementTree(root)
    tree.write(temp_file.name, encoding='utf-8', xml_declaration=True)
    temp_file.close()
    
    return temp_file.name


def generate_pdf_report(report, data):
    """
    Згенерувати PDF звіт
    """
    # Тут можна використовувати ReportLab або інші PDF бібліотеки
    # Для простоти створюємо текстовий файл
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False)
    
    content = f"""
ЗВІТ: {report.name}
Тип: {report.report_type}
Формат: {report.format}
Дата створення: {report.created_at}
Профіль ФОП: {report.fop_profile.id}
Податковий період: {report.tax_period.id}

Дані звіту:
{json.dumps(data, indent=2, ensure_ascii=False)}
"""
    
    temp_file.write(content)
    temp_file.close()
    
    return temp_file.name


def generate_excel_report(report, data):
    """
    Згенерувати Excel звіт
    """
    # Тут можна використовувати openpyxl або xlsxwriter
    # Для простоти створюємо CSV файл
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False)
    
    # Заголовки
    temp_file.write("Параметр,Значення\n")
    
    # Основна інформація
    temp_file.write(f"Назва звіту,{report.name}\n")
    temp_file.write(f"Тип звіту,{report.report_type}\n")
    temp_file.write(f"Формат,{report.format}\n")
    temp_file.write(f"Дата створення,{report.created_at}\n")
    temp_file.write(f"Профіль ФОП,{report.fop_profile.id}\n")
    temp_file.write(f"Податковий період,{report.tax_period.id}\n")
    
    # Дані звіту
    for key, value in data.items():
        temp_file.write(f"{key},{value}\n")
    
    temp_file.close()
    
    return temp_file.name


def generate_json_report(report, data):
    """
    Згенерувати JSON звіт
    """
    report_data = {
        'id': report.id,
        'name': report.name,
        'description': report.description,
        'report_type': report.report_type,
        'format': report.format,
        'created_at': report.created_at.isoformat(),
        'fop_profile_id': report.fop_profile.id,
        'tax_period_id': report.tax_period.id,
        'data': data
    }
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(report_data, temp_file, indent=2, ensure_ascii=False)
    temp_file.close()
    
    return temp_file.name


@shared_task(bind=True, max_retries=3)
def sign_report(self, report_id, signature_id):
    """
    Підписати звіт
    """
    try:
        report = Report.objects.get(id=report_id)
        signature = DigitalSignature.objects.get(id=signature_id)
        
        logger.info(f"Початок підпису звіту {report_id}")
        
        if report.status != 'ready':
            raise ValueError(f"Звіт повинен бути готовий для підпису. Поточний статус: {report.status}")
        
        # Тут має бути логіка підпису залежно від типу підпису
        if signature.signature_type == 'kep':
            result = sign_with_kep(report, signature)
        elif signature.signature_type == 'diia':
            result = sign_with_diia(report, signature)
        elif signature.signature_type == 'bank_id':
            result = sign_with_bank_id(report, signature)
        else:
            result = sign_with_other(report, signature)
        
        if result['success']:
            # Оновити статус звіту
            report.status = 'signed'
            report.signed_at = timezone.now()
            report.signed_file = result['signed_file']
            report.save()
            
            # Оновити підпис
            signature.is_valid = True
            signature.validation_message = "Підпис успішно створено"
            signature.save()
            
            logger.info(f"Звіт {report_id} успішно підписано")
        else:
            signature.is_valid = False
            signature.validation_message = result.get('error', 'Невідома помилка')
            signature.save()
            
            raise ValueError(result.get('error', 'Помилка підпису'))
        
        return result
        
    except Report.DoesNotExist:
        logger.error(f'Звіт {report_id} не знайдено')
        return {'success': False, 'error': 'Звіт не знайдено'}
    except DigitalSignature.DoesNotExist:
        logger.error(f'Підпис {signature_id} не знайдено')
        return {'success': False, 'error': 'Підпис не знайдено'}
    except Exception as exc:
        logger.error(f'Помилка підпису звіту {report_id}: {exc}')
        
        # Оновити статус підпису
        try:
            signature = DigitalSignature.objects.get(id=signature_id)
            signature.is_valid = False
            signature.validation_message = str(exc)
            signature.save()
        except:
            pass
        
        # Повторити задачу
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


def sign_with_kep(report, signature):
    """
    Підписати звіт КЕП
    """
    # Тут має бути інтеграція з КЕП SDK
    # Для демонстрації створюємо простий підпис
    return {
        'success': True,
        'signed_file': report.generated_file,  # В реальності це буде підписаний файл
        'message': 'Підпис КЕП створено'
    }


def sign_with_diia(report, signature):
    """
    Підписати звіт Дія.Підпис
    """
    # Тут має бути інтеграція з Дія.Підпис API
    return {
        'success': True,
        'signed_file': report.generated_file,
        'message': 'Підпис Дія.Підпис створено'
    }


def sign_with_bank_id(report, signature):
    """
    Підписати звіт BankID
    """
    # Тут має бути інтеграція з BankID
    return {
        'success': True,
        'signed_file': report.generated_file,
        'message': 'Підпис BankID створено'
    }


def sign_with_other(report, signature):
    """
    Підписати звіт іншим способом
    """
    return {
        'success': True,
        'signed_file': report.generated_file,
        'message': 'Підпис створено'
    }


@shared_task(bind=True, max_retries=3)
def submit_report(self, report_id, submission_id):
    """
    Подати звіт до ДПС
    """
    try:
        report = Report.objects.get(id=report_id)
        submission = ReportSubmission.objects.get(id=submission_id)
        
        logger.info(f"Початок подачі звіту {report_id}")
        
        if report.status not in ['ready', 'signed']:
            raise ValueError(f"Звіт повинен бути готовий або підписаний для подачі. Поточний статус: {report.status}")
        
        # Оновити статус подачі
        submission.status = 'submitted'
        submission.submitted_at = timezone.now()
        submission.save()
        
        # Тут має бути інтеграція з ДПС API
        result = submit_to_dps(report, submission)
        
        if result['success']:
            # Оновити статус звіту
            report.status = 'submitted'
            report.submitted_at = timezone.now()
            report.save()
            
            # Оновити подачу
            submission.status = 'accepted'
            submission.response_at = timezone.now()
            submission.response_data = result.get('response_data', {})
            submission.save()
            
            logger.info(f"Звіт {report_id} успішно подано")
        else:
            submission.status = 'error'
            submission.error_message = result.get('error', 'Невідома помилка')
            submission.save()
            
            raise ValueError(result.get('error', 'Помилка подачі'))
        
        return result
        
    except Report.DoesNotExist:
        logger.error(f'Звіт {report_id} не знайдено')
        return {'success': False, 'error': 'Звіт не знайдено'}
    except ReportSubmission.DoesNotExist:
        logger.error(f'Подача {submission_id} не знайдено')
        return {'success': False, 'error': 'Подача не знайдено'}
    except Exception as exc:
        logger.error(f'Помилка подачі звіту {report_id}: {exc}')
        
        # Оновити статус подачі
        try:
            submission = ReportSubmission.objects.get(id=submission_id)
            submission.status = 'error'
            submission.error_message = str(exc)
            submission.save()
        except:
            pass
        
        # Повторити задачу
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


def submit_to_dps(report, submission):
    """
    Подати звіт до ДПС
    """
    # Тут має бути інтеграція з ДПС API
    # Для демонстрації повертаємо успішний результат
    return {
        'success': True,
        'submission_id': submission.submission_id,
        'response_data': {
            'status': 'accepted',
            'message': 'Звіт успішно прийнято',
            'reference_number': f"REF-{report.id}-{int(timezone.now().timestamp())}"
        }
    }


@shared_task
def cleanup_old_reports():
    """
    Очистити старі звіти та файли
    """
    try:
        from datetime import timedelta
        
        # Видалити звіти старіше 1 року
        old_date = timezone.now() - timedelta(days=365)
        old_reports = Report.objects.filter(created_at__lt=old_date)
        
        deleted_count = 0
        for report in old_reports:
            # Видалити файли
            if report.generated_file:
                try:
                    report.generated_file.delete()
                except:
                    pass
            
            if report.signed_file:
                try:
                    report.signed_file.delete()
                except:
                    pass
            
            # Видалити звіт
            report.delete()
            deleted_count += 1
        
        logger.info(f"Очищено {deleted_count} старих звітів")
        
    except Exception as e:
        logger.error(f'Помилка очищення звітів: {e}')

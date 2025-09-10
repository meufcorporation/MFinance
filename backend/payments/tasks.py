from celery import shared_task
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import logging
import requests
import json

from .models import Payment, PaymentSchedule, PaymentLog, PaymentProvider
from fop.models import TaxObligation

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_payment(self, payment_id):
    """
    Обробити платіж через платіжний провайдер
    """
    try:
        payment = Payment.objects.get(id=payment_id)
        
        # Логування початку обробки
        PaymentLog.objects.create(
            payment=payment,
            level='info',
            message=f'Початок обробки платежу через {payment.provider.name}',
            metadata={'task_id': self.request.id}
        )
        
        # Оновити статус
        payment.status = 'processing'
        payment.save()
        
        # Отримати провайдера
        provider = payment.provider
        
        if provider.name == 'mono':
            result = process_mono_payment(payment)
        elif provider.name == 'privat':
            result = process_privat_payment(payment)
        elif provider.name == 'open_banking':
            result = process_open_banking_payment(payment)
        elif provider.name == 'manual':
            result = process_manual_payment(payment)
        else:
            raise ValueError(f'Невідомий провайдер: {provider.name}')
        
        if result['success']:
            payment.status = 'completed'
            payment.processed_at = timezone.now()
            payment.external_payment_id = result.get('payment_id')
            payment.external_transaction_id = result.get('transaction_id')
            payment.metadata = result.get('metadata', {})
            payment.error_message = None
            
            PaymentLog.objects.create(
                payment=payment,
                level='info',
                message='Платіж успішно оброблено',
                metadata=result
            )
        else:
            payment.status = 'failed'
            payment.error_message = result.get('error', 'Невідома помилка')
            
            PaymentLog.objects.create(
                payment=payment,
                level='error',
                message=f'Помилка обробки платежу: {result.get("error")}',
                metadata=result
            )
        
        payment.save()
        
        return result
        
    except Payment.DoesNotExist:
        logger.error(f'Платіж {payment_id} не знайдено')
        return {'success': False, 'error': 'Платіж не знайдено'}
    except Exception as exc:
        logger.error(f'Помилка обробки платежу {payment_id}: {exc}')
        
        # Логування помилки
        try:
            payment = Payment.objects.get(id=payment_id)
            PaymentLog.objects.create(
                payment=payment,
                level='error',
                message=f'Критична помилка: {str(exc)}',
                metadata={'task_id': self.request.id, 'retry_count': self.request.retries}
            )
        except:
            pass
        
        # Повторити задачу
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


def process_mono_payment(payment):
    """
    Обробити платіж через Mono Bank API
    """
    try:
        provider = payment.provider
        credentials = provider.credentials
        
        # URL для створення платежу в Mono
        api_url = f"{provider.api_url}/api/merchant/invoice/create"
        
        headers = {
            'X-Token': credentials.get('api_token'),
            'Content-Type': 'application/json'
        }
        
        data = {
            'amount': int(payment.amount * 100),  # Конвертувати в копійки
            'ccy': payment.currency,
            'merchantPaymInfo': {
                'reference': f"TAX-{payment.id}",
                'destination': payment.description,
                'basketOrder': [{
                    'name': payment.description,
                    'qty': 1,
                    'sum': int(payment.amount * 100)
                }]
            },
            'redirectUrl': f"https://mfinance.com/payments/{payment.id}/status",
            'webHookUrl': f"https://mfinance.com/api/payments/webhook/mono"
        }
        
        response = requests.post(api_url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'payment_id': result.get('invoiceId'),
                'transaction_id': result.get('invoiceId'),
                'metadata': result
            }
        else:
            return {
                'success': False,
                'error': f'Mono API error: {response.status_code} - {response.text}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Mono payment error: {str(e)}'
        }


def process_privat_payment(payment):
    """
    Обробити платіж через PrivatBank API
    """
    try:
        provider = payment.provider
        credentials = provider.credentials
        
        # URL для створення платежу в PrivatBank
        api_url = f"{provider.api_url}/api/checkout/create"
        
        headers = {
            'Authorization': f"Bearer {credentials.get('access_token')}",
            'Content-Type': 'application/json'
        }
        
        data = {
            'amount': payment.amount,
            'currency': payment.currency,
            'description': payment.description,
            'order_id': f"TAX-{payment.id}",
            'return_url': f"https://mfinance.com/payments/{payment.id}/status",
            'notify_url': f"https://mfinance.com/api/payments/webhook/privat"
        }
        
        response = requests.post(api_url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'payment_id': result.get('order_id'),
                'transaction_id': result.get('transaction_id'),
                'metadata': result
            }
        else:
            return {
                'success': False,
                'error': f'PrivatBank API error: {response.status_code} - {response.text}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'PrivatBank payment error: {str(e)}'
        }


def process_open_banking_payment(payment):
    """
    Обробити платіж через Open Banking API
    """
    try:
        provider = payment.provider
        credentials = provider.credentials
        
        # URL для створення платежу через Open Banking
        api_url = f"{provider.api_url}/api/v1/payments"
        
        headers = {
            'Authorization': f"Bearer {credentials.get('access_token')}",
            'Content-Type': 'application/json',
            'X-Request-ID': f"TAX-{payment.id}-{int(timezone.now().timestamp())}"
        }
        
        data = {
            'amount': {
                'amount': str(payment.amount),
                'currency': payment.currency
            },
            'description': payment.description,
            'reference': f"TAX-{payment.id}",
            'redirect_uri': f"https://mfinance.com/payments/{payment.id}/status",
            'webhook_uri': f"https://mfinance.com/api/payments/webhook/open-banking"
        }
        
        response = requests.post(api_url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 201:
            result = response.json()
            return {
                'success': True,
                'payment_id': result.get('payment_id'),
                'transaction_id': result.get('id'),
                'metadata': result
            }
        else:
            return {
                'success': False,
                'error': f'Open Banking API error: {response.status_code} - {response.text}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Open Banking payment error: {str(e)}'
        }


def process_manual_payment(payment):
    """
    Обробити ручний платіж (тільки створення запису)
    """
    return {
        'success': True,
        'payment_id': f"MANUAL-{payment.id}",
        'transaction_id': f"MANUAL-{payment.id}",
        'metadata': {
            'type': 'manual',
            'status': 'pending_manual_confirmation'
        }
    }


@shared_task
def schedule_payment(schedule_id):
    """
    Виконати платіж за розкладом
    """
    try:
        schedule = PaymentSchedule.objects.get(id=schedule_id)
        
        if not schedule.is_active:
            logger.info(f'Розклад {schedule_id} не активний')
            return
        
        # Створити платіж
        payment_data = {
            'user': schedule.user,
            'fop_profile': schedule.fop_profile,
            'payment_method': schedule.payment_method,
            'provider': schedule.payment_method.provider,
            'amount': schedule.amount or 0,
            'description': f"Автоматичний платіж: {schedule.name}",
            'payment_type': schedule.payment_type
        }
        
        with transaction.atomic():
            payment = Payment.objects.create(**payment_data)
            
            # Оновити розклад
            schedule.last_payment_date = timezone.now()
            schedule.next_payment_date = calculate_next_payment_date(schedule)
            schedule.save()
            
            # Запустити обробку платежу
            process_payment.delay(payment.id)
        
        logger.info(f'Платіж {payment.id} створено за розкладом {schedule_id}')
        
    except PaymentSchedule.DoesNotExist:
        logger.error(f'Розклад {schedule_id} не знайдено')
    except Exception as e:
        logger.error(f'Помилка виконання розкладу {schedule_id}: {e}')


def calculate_next_payment_date(schedule):
    """
    Розрахувати наступну дату платежу
    """
    now = timezone.now()
    
    if schedule.frequency == 'monthly':
        return now + timedelta(days=30)
    elif schedule.frequency == 'quarterly':
        return now + timedelta(days=90)
    elif schedule.frequency == 'yearly':
        return now + timedelta(days=365)
    else:
        # Для custom частоти використовуємо cron_expression
        # Тут можна додати логіку для парсингу cron
        return now + timedelta(days=30)


@shared_task
def process_webhook(webhook_id):
    """
    Обробити webhook від платіжного провайдера
    """
    try:
        webhook = PaymentWebhook.objects.get(id=webhook_id)
        
        # Логіка обробки webhook залежно від провайдера
        if webhook.provider.name == 'mono':
            result = process_mono_webhook(webhook)
        elif webhook.provider.name == 'privat':
            result = process_privat_webhook(webhook)
        elif webhook.provider.name == 'open_banking':
            result = process_open_banking_webhook(webhook)
        else:
            result = {'success': False, 'error': 'Невідомий провайдер'}
        
        if result['success']:
            webhook.is_processed = True
            webhook.processed_at = timezone.now()
        else:
            webhook.error_message = result.get('error')
        
        webhook.save()
        
        return result
        
    except PaymentWebhook.DoesNotExist:
        logger.error(f'Webhook {webhook_id} не знайдено')
        return {'success': False, 'error': 'Webhook не знайдено'}
    except Exception as e:
        logger.error(f'Помилка обробки webhook {webhook_id}: {e}')
        return {'success': False, 'error': str(e)}


def process_mono_webhook(webhook):
    """Обробити webhook від Mono Bank"""
    # Логіка обробки webhook від Mono
    return {'success': True}


def process_privat_webhook(webhook):
    """Обробити webhook від PrivatBank"""
    # Логіка обробки webhook від PrivatBank
    return {'success': True}


def process_open_banking_webhook(webhook):
    """Обробити webhook від Open Banking"""
    # Логіка обробки webhook від Open Banking
    return {'success': True}


@shared_task
def cleanup_old_payments():
    """
    Очистити старі платежі та логи
    """
    try:
        # Видалити логи старіше 90 днів
        old_date = timezone.now() - timedelta(days=90)
        deleted_logs = PaymentLog.objects.filter(created_at__lt=old_date).delete()
        
        # Видалити webhook'и старіше 30 днів
        webhook_date = timezone.now() - timedelta(days=30)
        deleted_webhooks = PaymentWebhook.objects.filter(created_at__lt=webhook_date).delete()
        
        logger.info(f'Очищено {deleted_logs[0]} логів та {deleted_webhooks[0]} webhook\'ів')
        
    except Exception as e:
        logger.error(f'Помилка очищення: {e}')

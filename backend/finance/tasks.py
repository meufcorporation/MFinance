from celery import shared_task
from django.db import transaction
from django.contrib.auth.models import User
import csv
import io
from decimal import Decimal
from datetime import datetime

from .models import ImportJob, Transaction, Account, Category


@shared_task(bind=True)
def process_csv_import(self, job_id, csv_content):
    """Обробка CSV файлу з транзакціями"""
    try:
        import_job = ImportJob.objects.get(id=job_id)
        import_job.status = 'processing'
        import_job.save()
        
        # Парсинг CSV
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        total_rows = 0
        processed_rows = 0
        errors = []
        
        with transaction.atomic():
            for row_num, row in enumerate(reader, 1):
                total_rows += 1
                
                try:
                    # Оновлюємо прогрес
                    if row_num % 100 == 0:
                        import_job.processed_rows = processed_rows
                        import_job.save()
                        self.update_state(
                            state='PROGRESS',
                            meta={'current': processed_rows, 'total': total_rows}
                        )
                    
                    # Валідація та створення транзакції
                    transaction_data = _parse_transaction_row(row, import_job.user)
                    if transaction_data:
                        Transaction.objects.create(**transaction_data)
                        processed_rows += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    continue
        
        # Оновлюємо статус завдання
        import_job.total_rows = total_rows
        import_job.processed_rows = processed_rows
        import_job.status = 'completed'
        if errors:
            import_job.error_message = f"Processed {processed_rows}/{total_rows} rows. Errors: {'; '.join(errors[:10])}"
        import_job.save()
        
        return {
            'status': 'completed',
            'total_rows': total_rows,
            'processed_rows': processed_rows,
            'errors': len(errors)
        }
        
    except Exception as e:
        import_job = ImportJob.objects.get(id=job_id)
        import_job.status = 'failed'
        import_job.error_message = str(e)
        import_job.save()
        
        return {
            'status': 'failed',
            'error': str(e)
        }


def _parse_transaction_row(row, user):
    """Парсинг рядка CSV в дані транзакції"""
    # Очікувані колонки: date, description, amount, account, category, type
    required_fields = ['date', 'description', 'amount']
    
    # Перевіряємо наявність обов'язкових полів
    for field in required_fields:
        if field not in row or not row[field]:
            return None
    
    # Парсинг дати
    try:
        date_str = row['date'].strip()
        # Спробуємо різні формати дати
        for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
            try:
                date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f"Unable to parse date: {date_str}")
    except Exception:
        return None
    
    # Парсинг суми
    try:
        amount_str = row['amount'].replace(',', '.').replace(' ', '')
        amount = Decimal(amount_str)
        if amount <= 0:
            return None
    except Exception:
        return None
    
    # Отримуємо або створюємо рахунок
    account_name = row.get('account', 'Default Account')
    account, _ = Account.objects.get_or_create(
        user=user,
        name=account_name,
        defaults={
            'account_type': 'checking',
            'bank_name': 'Unknown',
            'currency': 'UAH'
        }
    )
    
    # Отримуємо або створюємо категорію
    category = None
    if row.get('category'):
        category_name = row['category'].strip()
        category, _ = Category.objects.get_or_create(
            user=user,
            name=category_name,
            defaults={
                'category_type': 'expense',
                'color': '#3B82F6'
            }
        )
    
    # Визначаємо тип транзакції
    transaction_type = row.get('type', 'expense').lower()
    if transaction_type not in ['income', 'expense', 'transfer']:
        transaction_type = 'expense'
    
    return {
        'user': user,
        'account': account,
        'category': category,
        'amount': amount,
        'transaction_type': transaction_type,
        'description': row['description'].strip(),
        'merchant': row.get('merchant', '').strip(),
        'date': date,
        'external_id': row.get('external_id', ''),
        'notes': row.get('notes', '').strip()
    }


@shared_task
def apply_categorization_rules(user_id):
    """Застосування правил автоматичної категоризації"""
    try:
        user = User.objects.get(id=user_id)
        rules = Rule.objects.filter(user=user, is_active=True).order_by('-priority')
        uncategorized_transactions = Transaction.objects.filter(
            user=user, 
            category__isnull=True
        )
        
        updated_count = 0
        for transaction in uncategorized_transactions:
            for rule in rules:
                if _apply_rule(transaction, rule):
                    updated_count += 1
                    break
        
        return {
            'status': 'completed',
            'updated_transactions': updated_count
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }


def _apply_rule(transaction, rule):
    """Застосування правила до транзакції"""
    try:
        condition = rule.condition.lower()
        
        if rule.rule_type == 'description':
            return condition in transaction.description.lower()
        elif rule.rule_type == 'merchant':
            return condition in transaction.merchant.lower()
        elif rule.rule_type == 'amount':
            # Парсинг умови суми (наприклад: ">100", "<50", "=200")
            if condition.startswith('>'):
                return transaction.amount > Decimal(condition[1:])
            elif condition.startswith('<'):
                return transaction.amount < Decimal(condition[1:])
            elif condition.startswith('='):
                return transaction.amount == Decimal(condition[1:])
        elif rule.rule_type == 'account':
            return condition in transaction.account.name.lower()
        
        return False
    except Exception:
        return False


@shared_task
def calculate_budget_progress(user_id):
    """Розрахунок прогресу бюджетів"""
    try:
        user = User.objects.get(id=user_id)
        from .models import Budget
        from django.db.models import Sum
        from django.utils import timezone
        
        budgets = Budget.objects.filter(user=user, is_active=True)
        updated_budgets = 0
        
        for budget in budgets:
            # Розраховуємо витрати за період бюджету
            spent = Transaction.objects.filter(
                user=user,
                category=budget.category,
                transaction_type='expense',
                date__gte=budget.start_date,
                date__lte=budget.end_date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Оновлюємо бюджет (якщо потрібно зберігати прогрес)
            updated_budgets += 1
        
        return {
            'status': 'completed',
            'updated_budgets': updated_budgets
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }

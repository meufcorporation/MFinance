from decimal import Decimal
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict


class AnalyticsService:
    """Сервіс для аналітики фінансів"""
    
    def __init__(self, user):
        self.user = user
    
    def get_dashboard_data(self, period_days=30):
        """Отримати дані для дашборду"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        # Отримуємо транзакції за період
        from finance.models import Transaction, Account
        
        transactions = Transaction.objects.filter(
            account__user=self.user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Розраховуємо основні показники
        total_income = transactions.filter(transaction_type='income').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        total_expense = transactions.filter(transaction_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        # Баланс рахунків
        accounts = Account.objects.filter(user=self.user, is_active=True)
        total_balance = sum(account.balance for account in accounts)
        
        # Топ категорії витрат
        top_expense_categories = self._get_top_categories(transactions, 'expense')
        
        # Топ категорії доходів
        top_income_categories = self._get_top_categories(transactions, 'income')
        
        # Тренди
        daily_trends = self._get_daily_trends(transactions, start_date, end_date)
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'net_income': total_income - total_expense,
            'total_balance': total_balance,
            'top_expense_categories': top_expense_categories,
            'top_income_categories': top_income_categories,
            'daily_trends': daily_trends,
            'period_days': period_days
        }
    
    def get_category_analysis(self, period_days=30):
        """Аналіз по категоріях"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        from finance.models import Transaction, Category
        
        transactions = Transaction.objects.filter(
            account__user=self.user,
            date__gte=start_date,
            date__lte=end_date
        ).select_related('category')
        
        # Групуємо по категоріях
        category_data = defaultdict(lambda: {'income': Decimal('0'), 'expense': Decimal('0'), 'count': 0})
        
        for transaction in transactions:
            category_name = transaction.category.name if transaction.category else 'Без категорії'
            
            if transaction.transaction_type == 'income':
                category_data[category_name]['income'] += transaction.amount
            else:
                category_data[category_name]['expense'] += abs(transaction.amount)
            
            category_data[category_name]['count'] += 1
        
        # Сортуємо по загальній сумі
        sorted_categories = sorted(
            category_data.items(),
            key=lambda x: x[1]['income'] + x[1]['expense'],
            reverse=True
        )
        
        return {
            'categories': [
                {
                    'name': name,
                    'income': data['income'],
                    'expense': data['expense'],
                    'net': data['income'] - data['expense'],
                    'count': data['count']
                }
                for name, data in sorted_categories
            ],
            'period_days': period_days
        }
    
    def get_monthly_comparison(self, months=12):
        """Порівняння по місяцях"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=months * 30)
        
        from finance.models import Transaction
        
        transactions = Transaction.objects.filter(
            account__user=self.user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Групуємо по місяцях
        monthly_data = defaultdict(lambda: {'income': Decimal('0'), 'expense': Decimal('0'), 'count': 0})
        
        for transaction in transactions:
            month_key = transaction.date.strftime('%Y-%m')
            
            if transaction.transaction_type == 'income':
                monthly_data[month_key]['income'] += transaction.amount
            else:
                monthly_data[month_key]['expense'] += abs(transaction.amount)
            
            monthly_data[month_key]['count'] += 1
        
        # Сортуємо по даті
        sorted_months = sorted(monthly_data.items())
        
        return {
            'months': [
                {
                    'month': month,
                    'income': data['income'],
                    'expense': data['expense'],
                    'net': data['income'] - data['expense'],
                    'count': data['count']
                }
                for month, data in sorted_months
            ],
            'months_count': months
        }
    
    def get_budget_analysis(self):
        """Аналіз бюджетів"""
        from finance.models import Budget
        
        budgets = Budget.objects.filter(user=self.user, is_active=True)
        
        budget_data = []
        for budget in budgets:
            # Розраховуємо витрати за поточний період
            spent = self._calculate_budget_spent(budget)
            remaining = budget.amount - spent
            percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0
            
            budget_data.append({
                'id': budget.id,
                'name': budget.name,
                'category': budget.category.name if budget.category else 'Без категорії',
                'amount': budget.amount,
                'spent': spent,
                'remaining': remaining,
                'percentage': percentage,
                'status': self._get_budget_status(percentage)
            })
        
        return {
            'budgets': budget_data,
            'total_budget': sum(budget.amount for budget in budgets),
            'total_spent': sum(data['spent'] for data in budget_data)
        }
    
    def get_tax_analysis(self):
        """Аналіз податків"""
        from fop.models import FOPProfile, TaxPeriod
        
        try:
            fop_profile = FOPProfile.objects.get(user=self.user)
        except FOPProfile.DoesNotExist:
            return {'error': 'ФОП профіль не знайдено'}
        
        # Отримуємо податкові періоди за поточний рік
        current_year = timezone.now().year
        tax_periods = TaxPeriod.objects.filter(
            fop_profile=fop_profile,
            year=current_year
        ).order_by('month', 'quarter')
        
        periods_data = []
        total_tax = Decimal('0')
        total_paid = Decimal('0')
        
        for period in tax_periods:
            periods_data.append({
                'period': f"{period.year}-{period.month:02d}" if period.month else f"{period.year} Q{period.quarter}",
                'tax_amount': period.tax_amount,
                'paid_amount': period.paid_amount,
                'remaining': period.tax_amount - period.paid_amount,
                'status': 'paid' if period.payment_made else 'pending'
            })
            
            total_tax += period.tax_amount
            total_paid += period.paid_amount
        
        return {
            'fop_profile': {
                'name': f"{fop_profile.last_name} {fop_profile.first_name}",
                'tax_group': fop_profile.get_tax_group_display(),
                'tax_system': fop_profile.get_tax_system_display()
            },
            'periods': periods_data,
            'total_tax': total_tax,
            'total_paid': total_paid,
            'remaining': total_tax - total_paid,
            'year': current_year
        }
    
    def get_merchant_analysis(self, period_days=30):
        """Аналіз по мерчантах"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        from finance.models import Transaction
        
        transactions = Transaction.objects.filter(
            account__user=self.user,
            date__gte=start_date,
            date__lte=end_date,
            merchant__isnull=False
        ).exclude(merchant='')
        
        # Групуємо по мерчантах
        merchant_data = defaultdict(lambda: {'amount': Decimal('0'), 'count': 0, 'last_transaction': None})
        
        for transaction in transactions:
            merchant = transaction.merchant
            merchant_data[merchant]['amount'] += abs(transaction.amount)
            merchant_data[merchant]['count'] += 1
            
            if (merchant_data[merchant]['last_transaction'] is None or 
                transaction.date > merchant_data[merchant]['last_transaction']):
                merchant_data[merchant]['last_transaction'] = transaction.date
        
        # Сортуємо по сумі
        sorted_merchants = sorted(
            merchant_data.items(),
            key=lambda x: x[1]['amount'],
            reverse=True
        )
        
        return {
            'merchants': [
                {
                    'name': merchant,
                    'amount': data['amount'],
                    'count': data['count'],
                    'avg_amount': data['amount'] / data['count'] if data['count'] > 0 else 0,
                    'last_transaction': data['last_transaction']
                }
                for merchant, data in sorted_merchants
            ],
            'period_days': period_days
        }
    
    def _get_top_categories(self, transactions, transaction_type, limit=5):
        """Отримати топ категорії"""
        from finance.models import Category
        
        filtered_transactions = transactions.filter(transaction_type=transaction_type)
        
        category_totals = defaultdict(Decimal)
        for transaction in filtered_transactions:
            category_name = transaction.category.name if transaction.category else 'Без категорії'
            amount = transaction.amount if transaction_type == 'income' else abs(transaction.amount)
            category_totals[category_name] += amount
        
        return [
            {'name': name, 'amount': amount}
            for name, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:limit]
        ]
    
    def _get_daily_trends(self, transactions, start_date, end_date):
        """Отримати денні тренди"""
        daily_data = defaultdict(lambda: {'income': Decimal('0'), 'expense': Decimal('0')})
        
        for transaction in transactions:
            date_key = transaction.date.strftime('%Y-%m-%d')
            
            if transaction.transaction_type == 'income':
                daily_data[date_key]['income'] += transaction.amount
            else:
                daily_data[date_key]['expense'] += abs(transaction.amount)
        
        # Заповнюємо пропуски нулями
        trends = []
        current_date = start_date
        while current_date <= end_date:
            date_key = current_date.strftime('%Y-%m-%d')
            data = daily_data.get(date_key, {'income': Decimal('0'), 'expense': Decimal('0')})
            
            trends.append({
                'date': date_key,
                'income': data['income'],
                'expense': data['expense'],
                'net': data['income'] - data['expense']
            })
            
            current_date += timedelta(days=1)
        
        return trends
    
    def _calculate_budget_spent(self, budget):
        """Розрахувати витрати по бюджету"""
        from finance.models import Transaction
        
        # Визначаємо період бюджету
        if budget.period == 'monthly':
            start_date = timezone.now().date().replace(day=1)
            end_date = timezone.now().date()
        elif budget.period == 'yearly':
            start_date = timezone.now().date().replace(month=1, day=1)
            end_date = timezone.now().date()
        else:  # quarterly
            quarter = (timezone.now().month - 1) // 3 + 1
            start_month = (quarter - 1) * 3 + 1
            start_date = timezone.now().date().replace(month=start_month, day=1)
            end_date = timezone.now().date()
        
        # Розраховуємо витрати
        transactions = Transaction.objects.filter(
            account__user=self.user,
            transaction_type='expense',
            date__gte=start_date,
            date__lte=end_date
        )
        
        if budget.category:
            transactions = transactions.filter(category=budget.category)
        
        return sum(abs(t.amount) for t in transactions)
    
    def _get_budget_status(self, percentage):
        """Отримати статус бюджету"""
        if percentage >= 100:
            return 'exceeded'
        elif percentage >= 90:
            return 'warning'
        elif percentage >= 75:
            return 'caution'
        else:
            return 'good'

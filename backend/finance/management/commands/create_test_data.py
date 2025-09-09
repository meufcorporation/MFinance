from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime, timedelta
import random

from finance.models import Account, Category, Transaction, Budget, Rule


class Command(BaseCommand):
    help = 'Create test data for MFinance application'

    def handle(self, *args, **options):
        # Створюємо тестового користувача
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created test user: testuser'))

        # Створюємо рахунки
        accounts_data = [
            {'name': 'Основной рахунок', 'bank_name': 'ПриватБанк', 'account_type': 'checking', 'balance': 15000.00},
            {'name': 'Депозит', 'bank_name': 'Монобанк', 'account_type': 'savings', 'balance': 50000.00},
            {'name': 'Кредитна карта', 'bank_name': 'Ощадбанк', 'account_type': 'credit', 'balance': -5000.00},
        ]
        
        accounts = []
        for acc_data in accounts_data:
            account, created = Account.objects.get_or_create(
                user=user,
                name=acc_data['name'],
                defaults={
                    'bank_name': acc_data['bank_name'],
                    'account_type': acc_data['account_type'],
                    'balance': acc_data['balance'],
                    'currency': 'UAH'
                }
            )
            accounts.append(account)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created account: {account.name}'))

        # Створюємо категорії
        categories_data = [
            # Доходи
            {'name': 'Зарплата', 'category_type': 'income', 'color': '#10B981'},
            {'name': 'Фріланс', 'category_type': 'income', 'color': '#3B82F6'},
            {'name': 'Інвестиції', 'category_type': 'income', 'color': '#8B5CF6'},
            # Витрати
            {'name': 'Продукти', 'category_type': 'expense', 'color': '#F59E0B'},
            {'name': 'Транспорт', 'category_type': 'expense', 'color': '#EF4444'},
            {'name': 'Розваги', 'category_type': 'expense', 'color': '#EC4899'},
            {'name': 'Одяг', 'category_type': 'expense', 'color': '#06B6D4'},
            {'name': 'Медицина', 'category_type': 'expense', 'color': '#84CC16'},
            {'name': 'Комунальні', 'category_type': 'expense', 'color': '#F97316'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                user=user,
                name=cat_data['name'],
                defaults={
                    'category_type': cat_data['category_type'],
                    'color': cat_data['color']
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        # Створюємо транзакції
        income_categories = [c for c in categories if c.category_type == 'income']
        expense_categories = [c for c in categories if c.category_type == 'expense']
        
        # Транзакції доходів
        income_transactions = [
            {'description': 'Зарплата за вересень', 'amount': 25000.00, 'merchant': 'IT Company'},
            {'description': 'Проект веб-сайту', 'amount': 15000.00, 'merchant': 'Freelance Client'},
            {'description': 'Дивіденди', 'amount': 2000.00, 'merchant': 'Investment Fund'},
        ]
        
        for trans_data in income_transactions:
            Transaction.objects.get_or_create(
                user=user,
                account=accounts[0],  # Основной рахунок
                description=trans_data['description'],
                amount=trans_data['amount'],
                defaults={
                    'transaction_type': 'income',
                    'merchant': trans_data['merchant'],
                    'category': random.choice(income_categories),
                    'date': datetime.now() - timedelta(days=random.randint(1, 30))
                }
            )

        # Транзакції витрат
        expense_transactions = [
            {'description': 'Продукти в супермаркеті', 'amount': 1200.00, 'merchant': 'АТБ'},
            {'description': 'Бензин', 'amount': 800.00, 'merchant': 'WOG'},
            {'description': 'Кіно', 'amount': 300.00, 'merchant': 'Multiplex'},
            {'description': 'Одяг', 'amount': 2500.00, 'merchant': 'Zara'},
            {'description': 'Ліки', 'amount': 450.00, 'merchant': 'Аптека'},
            {'description': 'Електрика', 'amount': 1200.00, 'merchant': 'Київенерго'},
            {'description': 'Кава', 'amount': 150.00, 'merchant': 'Starbucks'},
            {'description': 'Таксі', 'amount': 200.00, 'merchant': 'Uber'},
        ]
        
        for trans_data in expense_transactions:
            Transaction.objects.get_or_create(
                user=user,
                account=accounts[0],  # Основной рахунок
                description=trans_data['description'],
                amount=trans_data['amount'],
                defaults={
                    'transaction_type': 'expense',
                    'merchant': trans_data['merchant'],
                    'category': random.choice(expense_categories),
                    'date': datetime.now() - timedelta(days=random.randint(1, 30))
                }
            )

        # Створюємо бюджети
        budget_data = [
            {'name': 'Бюджет на продукти', 'amount': 5000.00, 'period': 'monthly', 'category': 'Продукти'},
            {'name': 'Бюджет на розваги', 'amount': 2000.00, 'period': 'monthly', 'category': 'Розваги'},
            {'name': 'Бюджет на транспорт', 'amount': 3000.00, 'period': 'monthly', 'category': 'Транспорт'},
        ]
        
        for budget_info in budget_data:
            category = Category.objects.get(user=user, name=budget_info['category'])
            Budget.objects.get_or_create(
                user=user,
                name=budget_info['name'],
                defaults={
                    'category': category,
                    'amount': budget_info['amount'],
                    'period': budget_info['period'],
                    'start_date': datetime.now().date().replace(day=1),
                    'end_date': (datetime.now().date().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                }
            )

        # Створюємо правила категоризації
        rules_data = [
            {'name': 'Автомобільні витрати', 'rule_type': 'merchant', 'condition': 'WOG', 'category': 'Транспорт'},
            {'name': 'Продукти', 'rule_type': 'merchant', 'condition': 'АТБ', 'category': 'Продукти'},
            {'name': 'Розваги', 'rule_type': 'merchant', 'condition': 'Multiplex', 'category': 'Розваги'},
        ]
        
        for rule_info in rules_data:
            category = Category.objects.get(user=user, name=rule_info['category'])
            Rule.objects.get_or_create(
                user=user,
                name=rule_info['name'],
                defaults={
                    'rule_type': rule_info['rule_type'],
                    'condition': rule_info['condition'],
                    'category': category,
                    'priority': 1
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully created test data!'))
        self.stdout.write(f'User: testuser (password: testpass123)')
        self.stdout.write(f'Accounts: {len(accounts)}')
        self.stdout.write(f'Categories: {len(categories)}')
        self.stdout.write(f'Transactions: {Transaction.objects.filter(user=user).count()}')
        self.stdout.write(f'Budgets: {Budget.objects.filter(user=user).count()}')
        self.stdout.write(f'Rules: {Rule.objects.filter(user=user).count()}')

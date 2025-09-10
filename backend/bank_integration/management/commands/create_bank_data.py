from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bank_integration.models import Bank, BankAccount, BankToken, BankTransaction
from fop.models import FOPProfile
from decimal import Decimal
from datetime import datetime, timedelta, date
import random


class Command(BaseCommand):
    help = 'Create test data for bank integration'

    def handle(self, *args, **options):
        self.stdout.write('Creating bank integration test data...')
        
        # Create banks
        banks_data = [
            {
                'name': 'Монобанк',
                'code': 'mono',
                'bank_type': 'mono',
                'api_base_url': 'https://api.monobank.ua',
                'auth_url': 'https://api.monobank.ua/auth',
                'token_url': 'https://api.monobank.ua/token',
                'client_id': 'test_mono_client',
                'client_secret': 'test_mono_secret',
                'redirect_uri': 'http://localhost:3000/auth/callback/mono',
                'is_sandbox': True
            },
            {
                'name': 'ПриватБанк',
                'code': 'privat',
                'bank_type': 'privat',
                'api_base_url': 'https://api.privatbank.ua',
                'auth_url': 'https://api.privatbank.ua/auth',
                'token_url': 'https://api.privatbank.ua/token',
                'client_id': 'test_privat_client',
                'client_secret': 'test_privat_secret',
                'redirect_uri': 'http://localhost:3000/auth/callback/privat',
                'is_sandbox': True
            },
            {
                'name': 'Ощадбанк',
                'code': 'oschad',
                'bank_type': 'oschad',
                'api_base_url': 'https://api.oschadbank.ua',
                'auth_url': 'https://api.oschadbank.ua/auth',
                'token_url': 'https://api.oschadbank.ua/token',
                'client_id': 'test_oschad_client',
                'client_secret': 'test_oschad_secret',
                'redirect_uri': 'http://localhost:3000/auth/callback/oschad',
                'is_sandbox': True
            }
        ]
        
        banks = []
        for bank_data in banks_data:
            bank, created = Bank.objects.get_or_create(
                code=bank_data['code'],
                defaults=bank_data
            )
            banks.append(bank)
            if created:
                self.stdout.write(f'Created bank: {bank.name}')
        
        # Get or create test user
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
            self.stdout.write('Created test user: testuser')
        
        # Create FOP profile for test user
        fop_profile, created = FOPProfile.objects.get_or_create(
            user=user,
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'middle_name': 'Testovich',
                'tax_number': '1234567890',
                'registration_date': date(2024, 1, 1),
                'tax_group': '3',
                'tax_system': 'single_tax'
            }
        )
        if created:
            self.stdout.write('Created FOP profile for test user')
        
        # Create bank accounts for test user
        account_types = ['current', 'savings', 'credit']
        currencies = ['UAH', 'USD', 'EUR']
        
        for i, bank in enumerate(banks):
            for j in range(2):  # 2 accounts per bank
                account, created = BankAccount.objects.get_or_create(
                    user=user,
                    bank=bank,
                    account_id=f'{bank.code}_{j+1}',
                    defaults={
                        'account_number': f'{bank.code.upper()}{random.randint(1000000000, 9999999999)}',
                        'account_type': random.choice(account_types),
                        'currency': random.choice(currencies),
                        'balance': Decimal(random.uniform(1000, 50000)).quantize(Decimal('0.01')),
                        'credit_limit': Decimal(random.uniform(0, 10000)).quantize(Decimal('0.01')) if random.choice([True, False]) else Decimal('0'),
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(f'Created bank account: {account.account_number}')
        
        # Create bank tokens
        for bank in banks:
            token, created = BankToken.objects.get_or_create(
                user=user,
                bank=bank,
                defaults={
                    'access_token': f'test_access_token_{bank.code}_{random.randint(1000, 9999)}',
                    'refresh_token': f'test_refresh_token_{bank.code}_{random.randint(1000, 9999)}',
                    'token_type': 'Bearer',
                    'expires_at': datetime.now() + timedelta(days=30),
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created bank token for: {bank.name}')
        
        # Create bank transactions
        accounts = BankAccount.objects.filter(user=user)
        transaction_types = ['income', 'expense', 'transfer']
        merchants = [
            'АТБ', 'Сільпо', 'Нова Пошта', 'Uber', 'Bolt', 'Rozetka',
            'Comfy', 'Епіцентр', 'Метро', 'Велика Кишеня', 'Фора'
        ]
        
        for account in accounts:
            # Create 20-50 transactions per account
            num_transactions = random.randint(20, 50)
            
            for i in range(num_transactions):
                transaction_date = datetime.now() - timedelta(days=random.randint(1, 90))
                transaction_type = random.choice(transaction_types)
                amount = Decimal(random.uniform(10, 5000)).quantize(Decimal('0.01'))
                
                if transaction_type == 'expense':
                    amount = -amount
                
                transaction, created = BankTransaction.objects.get_or_create(
                    bank_account=account,
                    external_id=f'{account.bank.code}_{random.randint(100000, 999999)}_{i}',
                    defaults={
                        'amount': amount,
                        'currency': account.currency,
                        'transaction_type': transaction_type,
                        'description': f'Transaction {i+1} for {account.bank.name}',
                        'merchant': random.choice(merchants) if transaction_type == 'expense' else '',
                        'mcc_code': str(random.randint(1000, 9999)),
                        'transaction_date': transaction_date,
                        'processed_date': transaction_date + timedelta(minutes=random.randint(1, 60)),
                        'is_processed': random.choice([True, False]),
                        'is_categorized': random.choice([True, False])
                    }
                )
                if created and i % 10 == 0:  # Log every 10th transaction
                    self.stdout.write(f'Created transaction: {transaction.external_id}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created bank integration test data!')
        )

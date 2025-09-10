from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tax_calculations.models import TaxRate, TaxCalculation, TaxPayment, TaxRule, TaxExemption
from fop.models import FOPProfile
from decimal import Decimal
from datetime import datetime, timedelta, date
import random


class Command(BaseCommand):
    help = 'Create test data for tax calculations'

    def handle(self, *args, **options):
        self.stdout.write('Creating tax calculations test data...')
        
        # Create tax rates
        tax_rates_data = [
            # Single Tax rates
            {
                'tax_type': 'single_tax',
                'fop_group': '1',
                'rate_percent': Decimal('0'),
                'min_amount': Decimal('1000'),
                'valid_from': date(2024, 1, 1),
                'description': 'Єдиний податок 1 група (фіксована сума)'
            },
            {
                'tax_type': 'single_tax',
                'fop_group': '2',
                'rate_percent': Decimal('4'),
                'min_amount': Decimal('0'),
                'valid_from': date(2024, 1, 1),
                'description': 'Єдиний податок 2 група (4% від доходу)'
            },
            {
                'tax_type': 'single_tax',
                'fop_group': '3',
                'rate_percent': Decimal('5'),
                'min_amount': Decimal('0'),
                'valid_from': date(2024, 1, 1),
                'description': 'Єдиний податок 3 група (5% від доходу)'
            },
            # ESV rates
            {
                'tax_type': 'esv',
                'fop_group': '1',
                'rate_percent': Decimal('22'),
                'min_amount': Decimal('8000'),
                'valid_from': date(2024, 1, 1),
                'description': 'ЄСВ 1 група (22% від мінімальної заробітної плати)'
            },
            {
                'tax_type': 'esv',
                'fop_group': '2',
                'rate_percent': Decimal('22'),
                'min_amount': Decimal('8000'),
                'valid_from': date(2024, 1, 1),
                'description': 'ЄСВ 2 група (22% від мінімальної заробітної плати)'
            },
            {
                'tax_type': 'esv',
                'fop_group': '3',
                'rate_percent': Decimal('22'),
                'min_amount': Decimal('8000'),
                'valid_from': date(2024, 1, 1),
                'description': 'ЄСВ 3 група (22% від мінімальної заробітної плати)'
            },
            # VAT rates
            {
                'tax_type': 'vat',
                'fop_group': '1',
                'rate_percent': Decimal('0'),
                'min_amount': Decimal('1000000'),
                'valid_from': date(2024, 1, 1),
                'description': 'ПДВ 1 група (звільнення до 1 млн грн)'
            },
            {
                'tax_type': 'vat',
                'fop_group': '2',
                'rate_percent': Decimal('20'),
                'min_amount': Decimal('1000000'),
                'valid_from': date(2024, 1, 1),
                'description': 'ПДВ 2 група (20% після 1 млн грн)'
            },
            {
                'tax_type': 'vat',
                'fop_group': '3',
                'rate_percent': Decimal('20'),
                'min_amount': Decimal('1000000'),
                'valid_from': date(2024, 1, 1),
                'description': 'ПДВ 3 група (20% після 1 млн грн)'
            }
        ]
        
        for rate_data in tax_rates_data:
            rate, created = TaxRate.objects.get_or_create(
                tax_type=rate_data['tax_type'],
                fop_group=rate_data['fop_group'],
                valid_from=rate_data['valid_from'],
                defaults=rate_data
            )
            if created:
                self.stdout.write(f'Created tax rate: {rate.get_tax_type_display()} - {rate.get_fop_group_display()}')
        
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
                'tax_group': '3',
                'tax_system': 'single_tax'
            }
        )
        if created:
            self.stdout.write('Created FOP profile for test user')
        
        # Create tax calculations for current year
        current_year = datetime.now().year
        
        for month in range(1, 13):
            # Generate random income and expenses
            total_income = Decimal(random.uniform(50000, 200000)).quantize(Decimal('0.01'))
            total_expenses = Decimal(random.uniform(10000, 80000)).quantize(Decimal('0.01'))
            taxable_income = total_income - total_expenses
            
            # Calculate taxes based on FOP group
            if fop_profile.tax_group == '1':
                single_tax_amount = Decimal('1000')  # Fixed amount
            elif fop_profile.tax_group == '2':
                single_tax_amount = total_income * Decimal('0.04')
            else:  # group 3
                single_tax_amount = total_income * Decimal('0.05')
            
            # ESV calculation
            esv_base = max(Decimal('8000'), total_income)  # Min salary or actual income
            esv_amount = esv_base * Decimal('0.22')
            
            # VAT calculation (only if income > 1M)
            vat_amount = Decimal('0')
            if total_income > Decimal('1000000'):
                vat_amount = taxable_income * Decimal('0.20')
            
            total_tax_amount = single_tax_amount + esv_amount + vat_amount
            
            calculation, created = TaxCalculation.objects.get_or_create(
                fop_profile=fop_profile,
                calculation_type='monthly',
                year=current_year,
                month=month,
                defaults={
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'taxable_income': taxable_income,
                    'single_tax_amount': single_tax_amount,
                    'esv_amount': esv_amount,
                    'vat_amount': vat_amount,
                    'income_tax_amount': Decimal('0'),
                    'total_tax_amount': total_tax_amount,
                    'status': 'calculated'
                }
            )
            if created:
                self.stdout.write(f'Created tax calculation for {current_year}-{month:02d}')
        
        # Create quarterly calculations
        for quarter in range(1, 5):
            # Sum up monthly calculations for the quarter
            start_month = (quarter - 1) * 3 + 1
            end_month = quarter * 3
            
            monthly_calculations = TaxCalculation.objects.filter(
                fop_profile=fop_profile,
                year=current_year,
                month__gte=start_month,
                month__lte=end_month
            )
            
            total_income = sum(calc.total_income for calc in monthly_calculations)
            total_expenses = sum(calc.total_expenses for calc in monthly_calculations)
            total_tax_amount = sum(calc.total_tax_amount for calc in monthly_calculations)
            
            calculation, created = TaxCalculation.objects.get_or_create(
                fop_profile=fop_profile,
                calculation_type='quarterly',
                year=current_year,
                quarter=quarter,
                defaults={
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'taxable_income': total_income - total_expenses,
                    'single_tax_amount': sum(calc.single_tax_amount for calc in monthly_calculations),
                    'esv_amount': sum(calc.esv_amount for calc in monthly_calculations),
                    'vat_amount': sum(calc.vat_amount for calc in monthly_calculations),
                    'income_tax_amount': Decimal('0'),
                    'total_tax_amount': total_tax_amount,
                    'status': 'calculated'
                }
            )
            if created:
                self.stdout.write(f'Created quarterly calculation for Q{quarter} {current_year}')
        
        # Create tax payments
        calculations = TaxCalculation.objects.filter(fop_profile=fop_profile, year=current_year)
        
        for calculation in calculations:
            # Create single tax payment
            if calculation.month:
                if calculation.month == 12:
                    due_date = date(current_year + 1, 1, 20)
                else:
                    due_date = date(current_year, calculation.month + 1, 20)
            else:
                due_date = date(current_year + 1, 1, 20)
            
            payment, created = TaxPayment.objects.get_or_create(
                tax_calculation=calculation,
                payment_type='single_tax',
                defaults={
                    'amount': calculation.single_tax_amount,
                    'due_date': due_date,
                    'status': 'pending' if due_date > date.today() else 'completed',
                    'paid_amount': calculation.single_tax_amount if due_date < date.today() else Decimal('0'),
                    'paid_date': due_date - timedelta(days=random.randint(1, 10)) if due_date < date.today() else None
                }
            )
            if created:
                self.stdout.write(f'Created single tax payment for {calculation.year}-{calculation.month or calculation.quarter}')
            
            # Create ESV payment
            esv_payment, created = TaxPayment.objects.get_or_create(
                tax_calculation=calculation,
                payment_type='esv',
                defaults={
                    'amount': calculation.esv_amount,
                    'due_date': due_date,
                    'status': 'pending' if due_date > date.today() else 'completed',
                    'paid_amount': calculation.esv_amount if due_date < date.today() else Decimal('0'),
                    'paid_date': due_date - timedelta(days=random.randint(1, 10)) if due_date < date.today() else None
                }
            )
            if created:
                self.stdout.write(f'Created ESV payment for {calculation.year}-{calculation.month or calculation.quarter}')
            
            # Create VAT payment if applicable
            if calculation.vat_amount > 0:
                vat_payment, created = TaxPayment.objects.get_or_create(
                    tax_calculation=calculation,
                    payment_type='vat',
                    defaults={
                        'amount': calculation.vat_amount,
                        'due_date': due_date,
                        'status': 'pending' if due_date > date.today() else 'completed',
                        'paid_amount': calculation.vat_amount if due_date < date.today() else Decimal('0'),
                        'paid_date': due_date - timedelta(days=random.randint(1, 10)) if due_date < date.today() else None
                    }
                )
                if created:
                    self.stdout.write(f'Created VAT payment for {calculation.year}-{calculation.month or calculation.quarter}')
        
        # Create tax rules
        rules_data = [
            {
                'name': 'Поріг доходу для ПДВ',
                'rule_type': 'income_threshold',
                'fop_group': '1',
                'condition': {'threshold': 1000000, 'field': 'total_income'},
                'action': {'type': 'enable_vat', 'rate': 20},
                'priority': 1,
                'description': 'Включити ПДВ при доході понад 1 млн грн'
            },
            {
                'name': 'Пільга для молодого підприємця',
                'rule_type': 'esv_exemption',
                'fop_group': '1',
                'condition': {'age_limit': 35, 'registration_date': '2024-01-01'},
                'action': {'type': 'exempt_esv', 'period_months': 12},
                'priority': 2,
                'description': 'Звільнення від ЄСВ для молодих підприємців'
            }
        ]
        
        for rule_data in rules_data:
            rule, created = TaxRule.objects.get_or_create(
                name=rule_data['name'],
                defaults=rule_data
            )
            if created:
                self.stdout.write(f'Created tax rule: {rule.name}')
        
        # Create tax exemptions
        exemptions_data = [
            {
                'exemption_type': 'esv',
                'valid_from': date(2024, 1, 1),
                'valid_to': date(2024, 12, 31),
                'exemption_percent': Decimal('100'),
                'description': 'Звільнення від ЄСВ на 2024 рік'
            },
            {
                'exemption_type': 'vat',
                'valid_from': date(2024, 1, 1),
                'valid_to': date(2024, 6, 30),
                'exemption_percent': Decimal('50'),
                'description': '50% пільга по ПДВ на перше півріччя'
            }
        ]
        
        for exemption_data in exemptions_data:
            exemption, created = TaxExemption.objects.get_or_create(
                fop_profile=fop_profile,
                exemption_type=exemption_data['exemption_type'],
                valid_from=exemption_data['valid_from'],
                defaults=exemption_data
            )
            if created:
                self.stdout.write(f'Created tax exemption: {exemption.get_exemption_type_display()}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created tax calculations test data!')
        )
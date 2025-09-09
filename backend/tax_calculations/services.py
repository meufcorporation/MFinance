from decimal import Decimal
from django.utils import timezone
from .models import TaxRate, TaxCalculation, TaxRule, TaxExemption


class TaxCalculationService:
    """Сервіс для розрахунку податків"""
    
    def __init__(self):
        self.current_date = timezone.now().date()
    
    def calculate_taxes(self, calculation: TaxCalculation):
        """Розрахувати всі податки для розрахунку"""
        fop_profile = calculation.fop_profile
        
        # Отримуємо актуальні ставки
        rates = self._get_tax_rates(fop_profile.tax_group, calculation.year, calculation.month)
        
        # Розраховуємо кожен тип податку
        calculation.single_tax_amount = self._calculate_single_tax(
            calculation, rates.get('single_tax')
        )
        
        calculation.esv_amount = self._calculate_esv(
            calculation, rates.get('esv')
        )
        
        calculation.vat_amount = self._calculate_vat(
            calculation, rates.get('vat')
        )
        
        calculation.income_tax_amount = self._calculate_income_tax(
            calculation, rates.get('income_tax')
        )
        
        # Загальна сума
        calculation.total_tax_amount = (
            calculation.single_tax_amount +
            calculation.esv_amount +
            calculation.vat_amount +
            calculation.income_tax_amount
        )
        
        calculation.status = 'calculated'
        calculation.save()
        
        return calculation
    
    def _get_tax_rates(self, fop_group: str, year: int, month: int = None):
        """Отримати актуальні ставки податків"""
        rates = {}
        
        for tax_type in ['single_tax', 'esv', 'vat', 'income_tax']:
            rate = TaxRate.objects.filter(
                tax_type=tax_type,
                fop_group=fop_group,
                valid_from__lte=self.current_date,
                is_active=True
            ).order_by('-valid_from').first()
            
            if rate:
                rates[tax_type] = rate
        
        return rates
    
    def _calculate_single_tax(self, calculation: TaxCalculation, rate: TaxRate = None):
        """Розрахувати єдиний податок"""
        if not rate:
            return Decimal('0')
        
        # Для 1 групи - фіксована сума
        if calculation.fop_profile.tax_group == '1':
            return rate.min_amount
        
        # Для 2-3 груп - відсоток від доходу
        if calculation.fop_profile.tax_group in ['2', '3']:
            return calculation.total_income * (rate.rate_percent / 100)
        
        return Decimal('0')
    
    def _calculate_esv(self, calculation: TaxCalculation, rate: TaxRate = None):
        """Розрахувати ЄСВ"""
        if not rate:
            return Decimal('0')
        
        # ЄСВ розраховується від мінімальної заробітної плати
        # або від фактичного доходу, якщо він більший
        min_salary = rate.min_amount  # Мінімальна заробітна плата
        esv_base = max(min_salary, calculation.total_income)
        
        return esv_base * (rate.rate_percent / 100)
    
    def _calculate_vat(self, calculation: TaxCalculation, rate: TaxRate = None):
        """Розрахувати ПДВ"""
        if not rate:
            return Decimal('0')
        
        # ПДВ розраховується тільки якщо дохід перевищує поріг
        if calculation.total_income < rate.min_amount:
            return Decimal('0')
        
        # ПДВ = (дохід - витрати) * ставка ПДВ
        vat_base = calculation.total_income - calculation.total_expenses
        return vat_base * (rate.rate_percent / 100)
    
    def _calculate_income_tax(self, calculation: TaxCalculation, rate: TaxRate = None):
        """Розрахувати податок на доходи"""
        if not rate:
            return Decimal('0')
        
        # Податок на доходи розраховується від оподатковуваного доходу
        return calculation.taxable_income * (rate.rate_percent / 100)
    
    def apply_tax_rules(self, calculation: TaxCalculation):
        """Застосувати правила розрахунку податків"""
        rules = TaxRule.objects.filter(
            fop_group=calculation.fop_profile.tax_group,
            is_active=True
        ).order_by('-priority')
        
        for rule in rules:
            if self._evaluate_rule_condition(rule, calculation):
                self._apply_rule_action(rule, calculation)
    
    def _evaluate_rule_condition(self, rule: TaxRule, calculation: TaxCalculation) -> bool:
        """Перевірити умову правила"""
        condition = rule.condition
        
        if rule.rule_type == 'income_threshold':
            threshold = Decimal(condition.get('threshold', 0))
            return calculation.total_income >= threshold
        
        elif rule.rule_type == 'expense_category':
            category = condition.get('category')
            # Тут буде логіка перевірки категорій витрат
            return True
        
        return False
    
    def _apply_rule_action(self, rule: TaxRule, calculation: TaxCalculation):
        """Застосувати дію правила"""
        action = rule.action
        
        if action.get('type') == 'adjust_rate':
            # Змінити ставку податку
            pass
        elif action.get('type') == 'exempt_amount':
            # Звільнити від податку
            pass
    
    def get_tax_exemptions(self, fop_profile, tax_type: str):
        """Отримати податкові пільги"""
        return TaxExemption.objects.filter(
            fop_profile=fop_profile,
            exemption_type=tax_type,
            valid_from__lte=self.current_date,
            is_active=True
        ).order_by('-valid_from')
    
    def calculate_monthly_tax(self, fop_profile, year: int, month: int):
        """Розрахувати податки за місяць"""
        # Отримуємо доходи та витрати за місяць
        from finance.models import Transaction
        
        transactions = Transaction.objects.filter(
            account__user=fop_profile.user,
            date__year=year,
            date__month=month
        )
        
        total_income = sum(
            t.amount for t in transactions 
            if t.transaction_type == 'income'
        )
        
        total_expenses = sum(
            abs(t.amount) for t in transactions 
            if t.transaction_type == 'expense'
        )
        
        # Створюємо розрахунок
        calculation = TaxCalculation.objects.create(
            fop_profile=fop_profile,
            calculation_type='monthly',
            year=year,
            month=month,
            total_income=total_income,
            total_expenses=total_expenses,
            taxable_income=total_income - total_expenses
        )
        
        # Розраховуємо податки
        return self.calculate_taxes(calculation)
    
    def calculate_quarterly_tax(self, fop_profile, year: int, quarter: int):
        """Розрахувати податки за квартал"""
        # Отримуємо доходи та витрати за квартал
        from finance.models import Transaction
        
        start_month = (quarter - 1) * 3 + 1
        end_month = quarter * 3
        
        transactions = Transaction.objects.filter(
            account__user=fop_profile.user,
            date__year=year,
            date__month__gte=start_month,
            date__month__lte=end_month
        )
        
        total_income = sum(
            t.amount for t in transactions 
            if t.transaction_type == 'income'
        )
        
        total_expenses = sum(
            abs(t.amount) for t in transactions 
            if t.transaction_type == 'expense'
        )
        
        # Створюємо розрахунок
        calculation = TaxCalculation.objects.create(
            fop_profile=fop_profile,
            calculation_type='quarterly',
            year=year,
            quarter=quarter,
            total_income=total_income,
            total_expenses=total_expenses,
            taxable_income=total_income - total_expenses
        )
        
        # Розраховуємо податки
        return self.calculate_taxes(calculation)
    
    def get_tax_deadlines(self, fop_profile, year: int):
        """Отримати дедлайни податків на рік"""
        deadlines = []
        
        # Місячні дедлайни
        for month in range(1, 13):
            deadlines.append({
                'type': 'monthly',
                'month': month,
                'year': year,
                'deadline': self._get_monthly_deadline(year, month),
                'description': f'Єдиний податок за {month:02d}.{year}'
            })
        
        # Квартальні дедлайни
        for quarter in range(1, 5):
            deadlines.append({
                'type': 'quarterly',
                'quarter': quarter,
                'year': year,
                'deadline': self._get_quarterly_deadline(year, quarter),
                'description': f'Квартальний звіт Q{quarter} {year}'
            })
        
        return deadlines
    
    def _get_monthly_deadline(self, year: int, month: int):
        """Отримати дедлайн за місяць"""
        # Дедлайн - 20 число наступного місяця
        if month == 12:
            return f"{year + 1}-01-20"
        else:
            return f"{year}-{month + 1:02d}-20"
    
    def _get_quarterly_deadline(self, year: int, quarter: int):
        """Отримати дедлайн за квартал"""
        # Дедлайн - 20 число місяця, що наступає за кварталом
        if quarter == 1:
            return f"{year}-04-20"
        elif quarter == 2:
            return f"{year}-07-20"
        elif quarter == 3:
            return f"{year}-10-20"
        else:  # quarter == 4
            return f"{year + 1}-01-20"

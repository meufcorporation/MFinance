"""
Unit tests for finance module.
"""

import pytest
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from finance.models import Account, Transaction, Category, Budget, BudgetRule
from auth_system.models import User

User = get_user_model()


@pytest.mark.unit
@pytest.mark.finance
class TestAccountModel(TestCase):
    """Test Account model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_account_creation(self):
        """Test account creation."""
        account = Account.objects.create(
            user=self.user,
            name='Test Account',
            account_type='checking',
            balance=Decimal('1000.00'),
            currency='UAH'
        )
        self.assertEqual(account.user, self.user)
        self.assertEqual(account.name, 'Test Account')
        self.assertEqual(account.account_type, 'checking')
        self.assertEqual(account.balance, Decimal('1000.00'))
        self.assertEqual(account.currency, 'UAH')
    
    def test_account_str_representation(self):
        """Test account string representation."""
        account = Account.objects.create(
            user=self.user,
            name='Test Account',
            account_type='checking',
            balance=Decimal('1000.00'),
            currency='UAH'
        )
        self.assertEqual(str(account), 'Test Account (UAH)')
    
    def test_account_balance_update(self):
        """Test account balance update."""
        account = Account.objects.create(
            user=self.user,
            name='Test Account',
            account_type='checking',
            balance=Decimal('1000.00'),
            currency='UAH'
        )
        account.balance = Decimal('1500.00')
        account.save()
        self.assertEqual(account.balance, Decimal('1500.00'))


@pytest.mark.unit
@pytest.mark.finance
class TestCategoryModel(TestCase):
    """Test Category model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_category_creation(self):
        """Test category creation."""
        category = Category.objects.create(
            user=self.user,
            name='Test Category',
            category_type='expense',
            color='#FF0000'
        )
        self.assertEqual(category.user, self.user)
        self.assertEqual(category.name, 'Test Category')
        self.assertEqual(category.category_type, 'expense')
        self.assertEqual(category.color, '#FF0000')
    
    def test_category_str_representation(self):
        """Test category string representation."""
        category = Category.objects.create(
            user=self.user,
            name='Test Category',
            category_type='expense',
            color='#FF0000'
        )
        self.assertEqual(str(category), 'Test Category (expense)')


@pytest.mark.unit
@pytest.mark.finance
class TestTransactionModel(TestCase):
    """Test Transaction model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Test Account',
            account_type='checking',
            balance=Decimal('1000.00'),
            currency='UAH'
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Test Category',
            category_type='expense',
            color='#FF0000'
        )
    
    def test_transaction_creation(self):
        """Test transaction creation."""
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.category,
            amount=Decimal('100.00'),
            description='Test Transaction',
            transaction_type='expense',
            currency='UAH'
        )
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.account, self.account)
        self.assertEqual(transaction.category, self.category)
        self.assertEqual(transaction.amount, Decimal('100.00'))
        self.assertEqual(transaction.description, 'Test Transaction')
        self.assertEqual(transaction.transaction_type, 'expense')
        self.assertEqual(transaction.currency, 'UAH')
    
    def test_transaction_str_representation(self):
        """Test transaction string representation."""
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.category,
            amount=Decimal('100.00'),
            description='Test Transaction',
            transaction_type='expense',
            currency='UAH'
        )
        self.assertEqual(str(transaction), 'Test Transaction - 100.00 UAH')


@pytest.mark.unit
@pytest.mark.finance
class TestBudgetModel(TestCase):
    """Test Budget model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Test Category',
            category_type='expense',
            color='#FF0000'
        )
    
    def test_budget_creation(self):
        """Test budget creation."""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('500.00'),
            period='monthly',
            currency='UAH'
        )
        self.assertEqual(budget.user, self.user)
        self.assertEqual(budget.category, self.category)
        self.assertEqual(budget.amount, Decimal('500.00'))
        self.assertEqual(budget.period, 'monthly')
        self.assertEqual(budget.currency, 'UAH')
    
    def test_budget_str_representation(self):
        """Test budget string representation."""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('500.00'),
            period='monthly',
            currency='UAH'
        )
        self.assertEqual(str(budget), 'Test Category - 500.00 UAH (monthly)')


@pytest.mark.unit
@pytest.mark.finance
class TestBudgetRuleModel(TestCase):
    """Test BudgetRule model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Test Category',
            category_type='expense',
            color='#FF0000'
        )
        self.budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('500.00'),
            period='monthly',
            currency='UAH'
        )
    
    def test_budget_rule_creation(self):
        """Test budget rule creation."""
        rule = BudgetRule.objects.create(
            budget=self.budget,
            rule_type='percentage',
            threshold=Decimal('80.00'),
            action='notify'
        )
        self.assertEqual(rule.budget, self.budget)
        self.assertEqual(rule.rule_type, 'percentage')
        self.assertEqual(rule.threshold, Decimal('80.00'))
        self.assertEqual(rule.action, 'notify')
    
    def test_budget_rule_str_representation(self):
        """Test budget rule string representation."""
        rule = BudgetRule.objects.create(
            budget=self.budget,
            rule_type='percentage',
            threshold=Decimal('80.00'),
            action='notify'
        )
        self.assertEqual(str(rule), 'Test Category - 80.00% (notify)')


@pytest.mark.integration
@pytest.mark.finance
class TestFinanceAPI(APITestCase):
    """Test finance API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Test Account',
            account_type='checking',
            balance=Decimal('1000.00'),
            currency='UAH'
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Test Category',
            category_type='expense',
            color='#FF0000'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_account_list(self):
        """Test account list endpoint."""
        url = reverse('finance:account-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Account')
    
    def test_account_create(self):
        """Test account creation endpoint."""
        url = reverse('finance:account-list')
        data = {
            'name': 'New Account',
            'account_type': 'savings',
            'balance': '2000.00',
            'currency': 'UAH'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Account.objects.filter(name='New Account').exists())
    
    def test_transaction_list(self):
        """Test transaction list endpoint."""
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.category,
            amount=Decimal('100.00'),
            description='Test Transaction',
            transaction_type='expense',
            currency='UAH'
        )
        url = reverse('finance:transaction-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_transaction_create(self):
        """Test transaction creation endpoint."""
        url = reverse('finance:transaction-list')
        data = {
            'account': self.account.id,
            'category': self.category.id,
            'amount': '150.00',
            'description': 'New Transaction',
            'transaction_type': 'expense',
            'currency': 'UAH'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Transaction.objects.filter(description='New Transaction').exists())
    
    def test_category_list(self):
        """Test category list endpoint."""
        url = reverse('finance:category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Category')
    
    def test_budget_list(self):
        """Test budget list endpoint."""
        Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('500.00'),
            period='monthly',
            currency='UAH'
        )
        url = reverse('finance:budget-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

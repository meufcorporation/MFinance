"""
Pytest configuration and fixtures for MFinance tests.
"""

import os
import django
from django.conf import settings

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mfinance.test_settings')
django.setup()

import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from faker import Faker

from auth_system.models import User, Role, UserProfile
from fop.models import FOPProfile, TaxPeriod
from finance.models import Account, Transaction, Category, Budget
from payments.models import PaymentProvider, PaymentMethod, Payment
from reports.models import ReportTemplate, Report

fake = Faker()
User = get_user_model()


@pytest.fixture
def api_client():
    """API client for testing."""
    return APIClient()


@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user():
    """Create an admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Authenticated API client."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def fop_profile(user):
    """Create a test FOP profile."""
    return FOPProfile.objects.create(
        user=user,
        name='Test FOP',
        fop_code='1234567890',
        fop_group='1',
        tax_address='Test Address',
        iban='UA123456789012345678901234567'
    )


@pytest.fixture
def tax_period():
    """Create a test tax period."""
    return TaxPeriod.objects.create(
        name='2024 Q1',
        start_date='2024-01-01',
        end_date='2024-03-31',
        period_type='quarterly'
    )


@pytest.fixture
def account(user):
    """Create a test account."""
    return Account.objects.create(
        user=user,
        name='Test Account',
        account_type='checking',
        balance=1000.00,
        currency='UAH'
    )


@pytest.fixture
def category(user):
    """Create a test category."""
    return Category.objects.create(
        user=user,
        name='Test Category',
        category_type='expense',
        color='#FF0000'
    )


@pytest.fixture
def transaction(user, account, category):
    """Create a test transaction."""
    return Transaction.objects.create(
        user=user,
        account=account,
        category=category,
        amount=100.00,
        description='Test Transaction',
        transaction_type='expense',
        currency='UAH'
    )


@pytest.fixture
def budget(user, category):
    """Create a test budget."""
    return Budget.objects.create(
        user=user,
        category=category,
        amount=500.00,
        period='monthly',
        currency='UAH'
    )


@pytest.fixture
def payment_provider():
    """Create a test payment provider."""
    return PaymentProvider.objects.create(
        name='test_provider',
        display_name='Test Provider',
        is_active=True,
        api_url='http://test.example.com',
        credentials={'api_key': 'test_key'},
        settings={'timeout': 30}
    )


@pytest.fixture
def payment_method(user, payment_provider):
    """Create a test payment method."""
    return PaymentMethod.objects.create(
        user=user,
        method_type='card',
        provider=payment_provider,
        card_holder='Test User',
        is_default=True,
        is_active=True
    )


@pytest.fixture
def payment(user, fop_profile, payment_method, payment_provider):
    """Create a test payment."""
    return Payment.objects.create(
        user=user,
        fop_profile=fop_profile,
        payment_method=payment_method,
        provider=payment_provider,
        amount=100.00,
        currency='UAH',
        payment_type='tax',
        description='Test Payment'
    )


@pytest.fixture
def report_template():
    """Create a test report template."""
    return ReportTemplate.objects.create(
        name='Test Template',
        description='Test template description',
        report_type='single_tax',
        format='xml',
        template_content='<test>Template content</test>',
        is_active=True,
        is_public=True
    )


@pytest.fixture
def report(user, fop_profile, tax_period, report_template):
    """Create a test report."""
    return Report.objects.create(
        user=user,
        fop_profile=fop_profile,
        tax_period=tax_period,
        template=report_template,
        name='Test Report',
        description='Test report description',
        report_type='single_tax',
        format='xml'
    )


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        'username': fake.user_name(),
        'email': fake.email(),
        'password': 'testpass123',
        'first_name': fake.first_name(),
        'last_name': fake.last_name()
    }


@pytest.fixture
def sample_fop_data():
    """Sample FOP profile data for testing."""
    return {
        'name': fake.company(),
        'fop_code': fake.numerify('##########'),
        'fop_group': '1',
        'tax_address': fake.address(),
        'iban': fake.iban()
    }


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing."""
    return {
        'amount': fake.pydecimal(left_digits=4, right_digits=2, positive=True),
        'description': fake.sentence(),
        'transaction_type': fake.random_element(['income', 'expense']),
        'currency': 'UAH'
    }


@pytest.fixture
def sample_payment_data():
    """Sample payment data for testing."""
    return {
        'amount': fake.pydecimal(left_digits=4, right_digits=2, positive=True),
        'currency': 'UAH',
        'payment_type': 'tax',
        'description': fake.sentence()
    }


@pytest.fixture
def sample_report_data():
    """Sample report data for testing."""
    return {
        'name': fake.sentence(nb_words=3),
        'description': fake.sentence(),
        'report_type': 'single_tax',
        'format': 'xml'
    }


# Pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as authentication related"
    )
    config.addinivalue_line(
        "markers", "finance: mark test as finance module test"
    )
    config.addinivalue_line(
        "markers", "fop: mark test as FOP module test"
    )
    config.addinivalue_line(
        "markers", "payments: mark test as payments module test"
    )
    config.addinivalue_line(
        "markers", "reports: mark test as reports module test"
    )

"""
Unit tests for payments module.
"""

import pytest
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from payments.models import PaymentProvider, PaymentMethod, Payment, PaymentSchedule, PaymentTemplate
from auth_system.models import User
from fop.models import FOPProfile

User = get_user_model()


@pytest.mark.unit
@pytest.mark.payments
class TestPaymentProviderModel(TestCase):
    """Test PaymentProvider model."""
    
    def test_payment_provider_creation(self):
        """Test payment provider creation."""
        provider = PaymentProvider.objects.create(
            name='test_provider',
            display_name='Test Provider',
            is_active=True,
            api_url='http://test.example.com',
            credentials={'api_key': 'test_key'},
            settings={'timeout': 30}
        )
        self.assertEqual(provider.name, 'test_provider')
        self.assertEqual(provider.display_name, 'Test Provider')
        self.assertTrue(provider.is_active)
        self.assertEqual(provider.api_url, 'http://test.example.com')
        self.assertEqual(provider.credentials, {'api_key': 'test_key'})
        self.assertEqual(provider.settings, {'timeout': 30})
    
    def test_payment_provider_str_representation(self):
        """Test payment provider string representation."""
        provider = PaymentProvider.objects.create(
            name='test_provider',
            display_name='Test Provider',
            is_active=True
        )
        self.assertEqual(str(provider), 'Test Provider')


@pytest.mark.unit
@pytest.mark.payments
class TestPaymentMethodModel(TestCase):
    """Test PaymentMethod model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.provider = PaymentProvider.objects.create(
            name='test_provider',
            display_name='Test Provider',
            is_active=True
        )
    
    def test_payment_method_creation(self):
        """Test payment method creation."""
        method = PaymentMethod.objects.create(
            user=self.user,
            method_type='card',
            provider=self.provider,
            card_holder='Test User',
            is_default=True,
            is_active=True
        )
        self.assertEqual(method.user, self.user)
        self.assertEqual(method.method_type, 'card')
        self.assertEqual(method.provider, self.provider)
        self.assertEqual(method.card_holder, 'Test User')
        self.assertTrue(method.is_default)
        self.assertTrue(method.is_active)
    
    def test_payment_method_str_representation(self):
        """Test payment method string representation."""
        method = PaymentMethod.objects.create(
            user=self.user,
            method_type='card',
            provider=self.provider,
            card_holder='Test User'
        )
        self.assertEqual(str(method), 'test@example.com - Банківська карта')


@pytest.mark.unit
@pytest.mark.payments
class TestPaymentModel(TestCase):
    """Test Payment model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.fop_profile = FOPProfile.objects.create(
            user=self.user,
            name='Test FOP',
            fop_code='1234567890',
            fop_group='1',
            tax_address='Test Address',
            iban='UA123456789012345678901234567'
        )
        self.provider = PaymentProvider.objects.create(
            name='test_provider',
            display_name='Test Provider',
            is_active=True
        )
        self.method = PaymentMethod.objects.create(
            user=self.user,
            method_type='card',
            provider=self.provider,
            card_holder='Test User'
        )
    
    def test_payment_creation(self):
        """Test payment creation."""
        payment = Payment.objects.create(
            user=self.user,
            fop_profile=self.fop_profile,
            payment_method=self.method,
            provider=self.provider,
            amount=Decimal('100.00'),
            currency='UAH',
            payment_type='tax',
            description='Test Payment'
        )
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.fop_profile, self.fop_profile)
        self.assertEqual(payment.payment_method, self.method)
        self.assertEqual(payment.provider, self.provider)
        self.assertEqual(payment.amount, Decimal('100.00'))
        self.assertEqual(payment.currency, 'UAH')
        self.assertEqual(payment.payment_type, 'tax')
        self.assertEqual(payment.description, 'Test Payment')
        self.assertEqual(payment.status, 'pending')
    
    def test_payment_str_representation(self):
        """Test payment string representation."""
        payment = Payment.objects.create(
            user=self.user,
            fop_profile=self.fop_profile,
            payment_method=self.method,
            provider=self.provider,
            amount=Decimal('100.00'),
            currency='UAH',
            payment_type='tax',
            description='Test Payment'
        )
        self.assertEqual(str(payment), f'Платіж {payment.id} - 100.00 UAH (pending)')


@pytest.mark.unit
@pytest.mark.payments
class TestPaymentScheduleModel(TestCase):
    """Test PaymentSchedule model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.fop_profile = FOPProfile.objects.create(
            user=self.user,
            name='Test FOP',
            fop_code='1234567890',
            fop_group='1',
            tax_address='Test Address',
            iban='UA123456789012345678901234567'
        )
        self.provider = PaymentProvider.objects.create(
            name='test_provider',
            display_name='Test Provider',
            is_active=True
        )
        self.method = PaymentMethod.objects.create(
            user=self.user,
            method_type='card',
            provider=self.provider,
            card_holder='Test User'
        )
    
    def test_payment_schedule_creation(self):
        """Test payment schedule creation."""
        schedule = PaymentSchedule.objects.create(
            user=self.user,
            fop_profile=self.fop_profile,
            payment_method=self.method,
            name='Test Schedule',
            description='Test schedule description',
            frequency='monthly',
            amount=Decimal('500.00'),
            payment_type='tax',
            is_active=True
        )
        self.assertEqual(schedule.user, self.user)
        self.assertEqual(schedule.fop_profile, self.fop_profile)
        self.assertEqual(schedule.payment_method, self.method)
        self.assertEqual(schedule.name, 'Test Schedule')
        self.assertEqual(schedule.frequency, 'monthly')
        self.assertEqual(schedule.amount, Decimal('500.00'))
        self.assertTrue(schedule.is_active)
    
    def test_payment_schedule_str_representation(self):
        """Test payment schedule string representation."""
        schedule = PaymentSchedule.objects.create(
            user=self.user,
            fop_profile=self.fop_profile,
            payment_method=self.method,
            name='Test Schedule',
            frequency='monthly'
        )
        self.assertEqual(str(schedule), 'Test Schedule - monthly')


@pytest.mark.unit
@pytest.mark.payments
class TestPaymentTemplateModel(TestCase):
    """Test PaymentTemplate model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_payment_template_creation(self):
        """Test payment template creation."""
        template = PaymentTemplate.objects.create(
            user=self.user,
            name='Test Template',
            description='Test template description',
            amount=Decimal('100.00'),
            payment_type='tax',
            description_template='Payment for {{amount}}',
            is_active=True,
            is_public=False
        )
        self.assertEqual(template.user, self.user)
        self.assertEqual(template.name, 'Test Template')
        self.assertEqual(template.amount, Decimal('100.00'))
        self.assertEqual(template.payment_type, 'tax')
        self.assertTrue(template.is_active)
        self.assertFalse(template.is_public)
    
    def test_payment_template_str_representation(self):
        """Test payment template string representation."""
        template = PaymentTemplate.objects.create(
            user=self.user,
            name='Test Template',
            description='Test template description'
        )
        self.assertEqual(str(template), 'Test Template')


@pytest.mark.integration
@pytest.mark.payments
class TestPaymentsAPI(APITestCase):
    """Test payments API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.fop_profile = FOPProfile.objects.create(
            user=self.user,
            name='Test FOP',
            fop_code='1234567890',
            fop_group='1',
            tax_address='Test Address',
            iban='UA123456789012345678901234567'
        )
        self.provider = PaymentProvider.objects.create(
            name='test_provider',
            display_name='Test Provider',
            is_active=True
        )
        self.method = PaymentMethod.objects.create(
            user=self.user,
            method_type='card',
            provider=self.provider,
            card_holder='Test User'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_payment_method_list(self):
        """Test payment method list endpoint."""
        url = reverse('payments:paymentmethod-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['method_type'], 'card')
    
    def test_payment_method_create(self):
        """Test payment method creation endpoint."""
        url = reverse('payments:paymentmethod-list')
        data = {
            'method_type': 'iban',
            'provider_id': self.provider.id,
            'iban': 'UA123456789012345678901234567',
            'is_default': False,
            'auto_pay_enabled': False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PaymentMethod.objects.filter(iban='UA123456789012345678901234567').exists())
    
    def test_payment_list(self):
        """Test payment list endpoint."""
        Payment.objects.create(
            user=self.user,
            fop_profile=self.fop_profile,
            payment_method=self.method,
            provider=self.provider,
            amount=Decimal('100.00'),
            currency='UAH',
            payment_type='tax',
            description='Test Payment'
        )
        url = reverse('payments:payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_payment_create(self):
        """Test payment creation endpoint."""
        url = reverse('payments:payment-list')
        data = {
            'fop_profile_id': self.fop_profile.id,
            'payment_method_id': self.method.id,
            'provider_id': self.provider.id,
            'amount': '150.00',
            'currency': 'UAH',
            'payment_type': 'tax',
            'description': 'New Payment'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Payment.objects.filter(description='New Payment').exists())
    
    def test_payment_schedule_list(self):
        """Test payment schedule list endpoint."""
        PaymentSchedule.objects.create(
            user=self.user,
            fop_profile=self.fop_profile,
            payment_method=self.method,
            name='Test Schedule',
            frequency='monthly',
            amount=Decimal('500.00'),
            payment_type='tax'
        )
        url = reverse('payments:paymentschedule-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_payment_template_list(self):
        """Test payment template list endpoint."""
        PaymentTemplate.objects.create(
            user=self.user,
            name='Test Template',
            description='Test template description',
            amount=Decimal('100.00'),
            payment_type='tax'
        )
        url = reverse('payments:paymenttemplate-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

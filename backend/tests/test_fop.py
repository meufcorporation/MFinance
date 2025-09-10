"""
Unit tests for FOP module.
"""

import pytest
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from fop.models import FOPProfile, TaxPeriod, TaxObligation, TaxPayment
from auth_system.models import User

User = get_user_model()


@pytest.mark.unit
@pytest.mark.fop
class TestFOPProfileModel(TestCase):
    """Test FOPProfile model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_fop_profile_creation(self):
        """Test FOP profile creation."""
        profile = FOPProfile.objects.create(
            user=self.user,
            name='Test FOP',
            fop_code='1234567890',
            fop_group='1',
            tax_address='Test Address',
            iban='UA123456789012345678901234567'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.name, 'Test FOP')
        self.assertEqual(profile.fop_code, '1234567890')
        self.assertEqual(profile.fop_group, '1')
        self.assertEqual(profile.tax_address, 'Test Address')
        self.assertEqual(profile.iban, 'UA123456789012345678901234567')
        self.assertTrue(profile.is_active)
    
    def test_fop_profile_str_representation(self):
        """Test FOP profile string representation."""
        profile = FOPProfile.objects.create(
            user=self.user,
            name='Test FOP',
            fop_code='1234567890',
            fop_group='1',
            tax_address='Test Address',
            iban='UA123456789012345678901234567'
        )
        self.assertEqual(str(profile), 'Test FOP (1234567890)')


@pytest.mark.unit
@pytest.mark.fop
class TestTaxPeriodModel(TestCase):
    """Test TaxPeriod model."""
    
    def test_tax_period_creation(self):
        """Test tax period creation."""
        period = TaxPeriod.objects.create(
            name='2024 Q1',
            start_date='2024-01-01',
            end_date='2024-03-31',
            period_type='quarterly'
        )
        self.assertEqual(period.name, '2024 Q1')
        self.assertEqual(period.start_date, '2024-01-01')
        self.assertEqual(period.end_date, '2024-03-31')
        self.assertEqual(period.period_type, 'quarterly')
    
    def test_tax_period_str_representation(self):
        """Test tax period string representation."""
        period = TaxPeriod.objects.create(
            name='2024 Q1',
            start_date='2024-01-01',
            end_date='2024-03-31',
            period_type='quarterly'
        )
        self.assertEqual(str(period), '2024 Q1 (quarterly)')


@pytest.mark.unit
@pytest.mark.fop
class TestTaxObligationModel(TestCase):
    """Test TaxObligation model."""
    
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
        self.tax_period = TaxPeriod.objects.create(
            name='2024 Q1',
            start_date='2024-01-01',
            end_date='2024-03-31',
            period_type='quarterly'
        )
    
    def test_tax_obligation_creation(self):
        """Test tax obligation creation."""
        obligation = TaxObligation.objects.create(
            fop_profile=self.fop_profile,
            tax_period=self.tax_period,
            tax_type='single_tax',
            amount=Decimal('1000.00'),
            due_date='2024-04-30',
            status='pending'
        )
        self.assertEqual(obligation.fop_profile, self.fop_profile)
        self.assertEqual(obligation.tax_period, self.tax_period)
        self.assertEqual(obligation.tax_type, 'single_tax')
        self.assertEqual(obligation.amount, Decimal('1000.00'))
        self.assertEqual(obligation.due_date, '2024-04-30')
        self.assertEqual(obligation.status, 'pending')
    
    def test_tax_obligation_str_representation(self):
        """Test tax obligation string representation."""
        obligation = TaxObligation.objects.create(
            fop_profile=self.fop_profile,
            tax_period=self.tax_period,
            tax_type='single_tax',
            amount=Decimal('1000.00'),
            due_date='2024-04-30',
            status='pending'
        )
        self.assertEqual(str(obligation), 'Test FOP - single_tax - 1000.00 UAH')


@pytest.mark.unit
@pytest.mark.fop
class TestTaxPaymentModel(TestCase):
    """Test TaxPayment model."""
    
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
        self.tax_period = TaxPeriod.objects.create(
            name='2024 Q1',
            start_date='2024-01-01',
            end_date='2024-03-31',
            period_type='quarterly'
        )
        self.obligation = TaxObligation.objects.create(
            fop_profile=self.fop_profile,
            tax_period=self.tax_period,
            tax_type='single_tax',
            amount=Decimal('1000.00'),
            due_date='2024-04-30',
            status='pending'
        )
    
    def test_tax_payment_creation(self):
        """Test tax payment creation."""
        payment = TaxPayment.objects.create(
            fop_profile=self.fop_profile,
            tax_obligation=self.obligation,
            amount=Decimal('1000.00'),
            payment_date='2024-04-15',
            status='completed'
        )
        self.assertEqual(payment.fop_profile, self.fop_profile)
        self.assertEqual(payment.tax_obligation, self.obligation)
        self.assertEqual(payment.amount, Decimal('1000.00'))
        self.assertEqual(payment.payment_date, '2024-04-15')
        self.assertEqual(payment.status, 'completed')
    
    def test_tax_payment_str_representation(self):
        """Test tax payment string representation."""
        payment = TaxPayment.objects.create(
            fop_profile=self.fop_profile,
            tax_obligation=self.obligation,
            amount=Decimal('1000.00'),
            payment_date='2024-04-15',
            status='completed'
        )
        self.assertEqual(str(payment), f'Платіж {payment.id} - 1000.00 UAH (completed)')


@pytest.mark.integration
@pytest.mark.fop
class TestFOPAPI(APITestCase):
    """Test FOP API endpoints."""
    
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
        self.client.force_authenticate(user=self.user)
    
    def test_fop_profile_list(self):
        """Test FOP profile list endpoint."""
        url = reverse('fop:fopprofile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test FOP')
    
    def test_fop_profile_create(self):
        """Test FOP profile creation endpoint."""
        url = reverse('fop:fopprofile-list')
        data = {
            'name': 'New FOP',
            'fop_code': '0987654321',
            'fop_group': '2',
            'tax_address': 'New Address',
            'iban': 'UA098765432109876543210987654321'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FOPProfile.objects.filter(name='New FOP').exists())
    
    def test_tax_period_list(self):
        """Test tax period list endpoint."""
        TaxPeriod.objects.create(
            name='2024 Q1',
            start_date='2024-01-01',
            end_date='2024-03-31',
            period_type='quarterly'
        )
        url = reverse('fop:taxperiod-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_tax_obligation_list(self):
        """Test tax obligation list endpoint."""
        tax_period = TaxPeriod.objects.create(
            name='2024 Q1',
            start_date='2024-01-01',
            end_date='2024-03-31',
            period_type='quarterly'
        )
        TaxObligation.objects.create(
            fop_profile=self.fop_profile,
            tax_period=tax_period,
            tax_type='single_tax',
            amount=Decimal('1000.00'),
            due_date='2024-04-30',
            status='pending'
        )
        url = reverse('fop:taxobligation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

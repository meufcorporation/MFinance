"""
Simple tests for MFinance project.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.unit
class TestBasicFunctionality(TestCase):
    """Test basic functionality."""
    
    def test_user_creation(self):
        """Test user creation."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(str(user), 'testuser')
    
    def test_superuser_creation(self):
        """Test superuser creation."""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


@pytest.mark.unit
class TestDjangoSetup(TestCase):
    """Test Django setup."""
    
    def test_django_is_configured(self):
        """Test that Django is properly configured."""
        from django.conf import settings
        self.assertTrue(settings.configured)
        self.assertEqual(settings.DATABASES['default']['ENGINE'], 'django.db.backends.sqlite3')
    
    def test_test_database_creation(self):
        """Test that test database is created."""
        from django.db import connection
        self.assertTrue(hasattr(connection.creation, 'create_test_db'))


@pytest.mark.unit
class TestModelsImport(TestCase):
    """Test that models can be imported."""
    
    def test_auth_models_import(self):
        """Test auth models import."""
        from auth_system.models import User, Role, UserProfile, UserSession, AuditLog
        self.assertTrue(True)
    
    def test_finance_models_import(self):
        """Test finance models import."""
        from finance.models import Account, Transaction, Category, Budget
        self.assertTrue(True)
    
    def test_fop_models_import(self):
        """Test FOP models import."""
        from fop.models import FOPProfile, TaxPeriod, TaxObligation
        self.assertTrue(True)
    
    def test_payments_models_import(self):
        """Test payments models import."""
        from payments.models import PaymentProvider, PaymentMethod, Payment, PaymentSchedule, PaymentTemplate
        self.assertTrue(True)
    
    def test_reports_models_import(self):
        """Test reports models import."""
        from reports.models import ReportTemplate, Report, ReportData, DigitalSignature, ReportSubmission
        self.assertTrue(True)


@pytest.mark.unit
class TestSerializersImport(TestCase):
    """Test that serializers can be imported."""
    
    def test_finance_serializers_import(self):
        """Test finance serializers import."""
        from finance.serializers import AccountSerializer, TransactionSerializer, CategorySerializer, BudgetSerializer
        self.assertTrue(True)
    
    def test_fop_serializers_import(self):
        """Test FOP serializers import."""
        from fop.serializers import FOPProfileSerializer, TaxPeriodSerializer, TaxObligationSerializer
        self.assertTrue(True)
    
    def test_payments_serializers_import(self):
        """Test payments serializers import."""
        from payments.serializers import PaymentProviderSerializer, PaymentMethodSerializer, PaymentSerializer
        self.assertTrue(True)
    
    def test_reports_serializers_import(self):
        """Test reports serializers import."""
        from reports.serializers import ReportTemplateSerializer, ReportSerializer, ReportDataSerializer
        self.assertTrue(True)


@pytest.mark.unit
class TestViewsImport(TestCase):
    """Test that views can be imported."""
    
    def test_finance_views_import(self):
        """Test finance views import."""
        from finance.views import AccountViewSet, TransactionViewSet, CategoryViewSet, BudgetViewSet
        self.assertTrue(True)
    
    def test_fop_views_import(self):
        """Test FOP views import."""
        from fop.views import FOPProfileViewSet, TaxPeriodViewSet, TaxObligationViewSet
        self.assertTrue(True)
    
    def test_payments_views_import(self):
        """Test payments views import."""
        from payments.views import PaymentProviderViewSet, PaymentMethodViewSet, PaymentViewSet
        self.assertTrue(True)
    
    def test_reports_views_import(self):
        """Test reports views import."""
        from reports.views import ReportTemplateViewSet, ReportViewSet, ReportDataViewSet
        self.assertTrue(True)


@pytest.mark.unit
class TestURLsImport(TestCase):
    """Test that URLs can be imported."""
    
    def test_main_urls_import(self):
        """Test main URLs import."""
        from mfinance.urls import urlpatterns
        self.assertTrue(len(urlpatterns) > 0)
    
    def test_finance_urls_import(self):
        """Test finance URLs import."""
        from finance.urls import urlpatterns
        self.assertTrue(len(urlpatterns) > 0)
    
    def test_fop_urls_import(self):
        """Test FOP URLs import."""
        from fop.urls import urlpatterns
        self.assertTrue(len(urlpatterns) > 0)
    
    def test_payments_urls_import(self):
        """Test payments URLs import."""
        from payments.urls import urlpatterns
        self.assertTrue(len(urlpatterns) > 0)
    
    def test_reports_urls_import(self):
        """Test reports URLs import."""
        from reports.urls import urlpatterns
        self.assertTrue(len(urlpatterns) > 0)

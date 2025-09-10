"""
Unit tests for reports module.
"""

import pytest
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from reports.models import ReportTemplate, Report, ReportData, DigitalSignature, ReportSubmission
from auth_system.models import User
from fop.models import FOPProfile, TaxPeriod

User = get_user_model()


@pytest.mark.unit
@pytest.mark.reports
class TestReportTemplateModel(TestCase):
    """Test ReportTemplate model."""
    
    def test_report_template_creation(self):
        """Test report template creation."""
        template = ReportTemplate.objects.create(
            name='Test Template',
            description='Test template description',
            report_type='single_tax',
            format='xml',
            template_content='<test>Template content</test>',
            is_active=True,
            is_public=True
        )
        self.assertEqual(template.name, 'Test Template')
        self.assertEqual(template.description, 'Test template description')
        self.assertEqual(template.report_type, 'single_tax')
        self.assertEqual(template.format, 'xml')
        self.assertEqual(template.template_content, '<test>Template content</test>')
        self.assertTrue(template.is_active)
        self.assertTrue(template.is_public)
    
    def test_report_template_str_representation(self):
        """Test report template string representation."""
        template = ReportTemplate.objects.create(
            name='Test Template',
            description='Test template description',
            report_type='single_tax',
            format='xml'
        )
        self.assertEqual(str(template), 'Test Template (single_tax)')


@pytest.mark.unit
@pytest.mark.reports
class TestReportModel(TestCase):
    """Test Report model."""
    
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
        self.template = ReportTemplate.objects.create(
            name='Test Template',
            description='Test template description',
            report_type='single_tax',
            format='xml',
            template_content='<test>Template content</test>',
            is_active=True,
            is_public=True
        )
    
    def test_report_creation(self):
        """Test report creation."""
        report = Report.objects.create(
            user=self.user,
            fop_profile=self.fop_profile,
            tax_period=self.tax_period,
            template=self.template,
            name='Test Report',
            description='Test report description',
            report_type='single_tax',
            format='xml'
        )
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.fop_profile, self.fop_profile)
        self.assertEqual(report.tax_period, self.tax_period)
        self.assertEqual(report.template, self.template)
        self.assertEqual(report.name, 'Test Report')
        self.assertEqual(report.description, 'Test report description')
        self.assertEqual(report.report_type, 'single_tax')
        self.assertEqual(report.format, 'xml')
        self.assertEqual(report.status, 'draft')
    
    def test_report_str_representation(self):
        """Test report string representation."""
        report = Report.objects.create(
            user=self.user,
            fop_profile=self.fop_profile,
            tax_period=self.tax_period,
            template=self.template,
            name='Test Report',
            description='Test report description',
            report_type='single_tax',
            format='xml'
        )
        self.assertEqual(str(report), 'Test Report (draft)')


@pytest.mark.unit
@pytest.mark.reports
class TestReportDataModel(TestCase):
    """Test ReportData model."""
    
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
        self.template = ReportTemplate.objects.create(
            name='Test Template',
            description='Test template description',
            report_type='single_tax',
            format='xml',
            template_content='<test>Template content</test>',
            is_active=True,
            is_public=True
        )
        self.report = Report.objects.create(
            user=self.user,
            fop_profile=self.fop_profile,
            tax_period=self.tax_period,
            template=self.template,
            name='Test Report',
            description='Test report description',
            report_type='single_tax',
            format='xml'
        )
    
    def test_report_data_creation(self):
        """Test report data creation."""
        data = ReportData.objects.create(
            report=self.report,
            data_type='income',
            field_name='total_income',
            field_value='1000.00',
            field_type='decimal'
        )
        self.assertEqual(data.report, self.report)
        self.assertEqual(data.data_type, 'income')
        self.assertEqual(data.field_name, 'total_income')
        self.assertEqual(data.field_value, '1000.00')
        self.assertEqual(data.field_type, 'decimal')
    
    def test_report_data_str_representation(self):
        """Test report data string representation."""
        data = ReportData.objects.create(
            report=self.report,
            data_type='income',
            field_name='total_income',
            field_value='1000.00',
            field_type='decimal'
        )
        self.assertEqual(str(data), 'Test Report - total_income: 1000.00')


@pytest.mark.unit
@pytest.mark.reports
class TestDigitalSignatureModel(TestCase):
    """Test DigitalSignature model."""
    
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
        self.template = ReportTemplate.objects.create(
            name='Test Template',
            description='Test template description',
            report_type='single_tax',
            format='xml',
            template_content='<test>Template content</test>',
            is_active=True,
            is_public=True
        )
        self.report = Report.objects.create(
            user=self.user,
            fop_profile=self.fop_profile,
            tax_period=self.tax_period,
            template=self.template,
            name='Test Report',
            description='Test report description',
            report_type='single_tax',
            format='xml'
        )
    
    def test_digital_signature_creation(self):
        """Test digital signature creation."""
        signature = DigitalSignature.objects.create(
            report=self.report,
            signature_type='kep',
            certificate_serial='1234567890',
            signature_data='signature_data_here',
            is_valid=True
        )
        self.assertEqual(signature.report, self.report)
        self.assertEqual(signature.signature_type, 'kep')
        self.assertEqual(signature.certificate_serial, '1234567890')
        self.assertEqual(signature.signature_data, 'signature_data_here')
        self.assertTrue(signature.is_valid)
    
    def test_digital_signature_str_representation(self):
        """Test digital signature string representation."""
        signature = DigitalSignature.objects.create(
            report=self.report,
            signature_type='kep',
            certificate_serial='1234567890',
            signature_data='signature_data_here',
            is_valid=True
        )
        self.assertEqual(str(signature), f'Test Report - KEP (1234567890)')


@pytest.mark.unit
@pytest.mark.reports
class TestReportSubmissionModel(TestCase):
    """Test ReportSubmission model."""
    
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
        self.template = ReportTemplate.objects.create(
            name='Test Template',
            description='Test template description',
            report_type='single_tax',
            format='xml',
            template_content='<test>Template content</test>',
            is_active=True,
            is_public=True
        )
        self.report = Report.objects.create(
            user=self.user,
            fop_profile=self.fop_profile,
            tax_period=self.tax_period,
            template=self.template,
            name='Test Report',
            description='Test report description',
            report_type='single_tax',
            format='xml'
        )
    
    def test_report_submission_creation(self):
        """Test report submission creation."""
        submission = ReportSubmission.objects.create(
            report=self.report,
            submission_type='electronic',
            submission_id='SUB123456',
            status='submitted',
            response_data={'status': 'accepted'}
        )
        self.assertEqual(submission.report, self.report)
        self.assertEqual(submission.submission_type, 'electronic')
        self.assertEqual(submission.submission_id, 'SUB123456')
        self.assertEqual(submission.status, 'submitted')
        self.assertEqual(submission.response_data, {'status': 'accepted'})
    
    def test_report_submission_str_representation(self):
        """Test report submission string representation."""
        submission = ReportSubmission.objects.create(
            report=self.report,
            submission_type='electronic',
            submission_id='SUB123456',
            status='submitted'
        )
        self.assertEqual(str(submission), f'Test Report - SUB123456 (submitted)')


@pytest.mark.integration
@pytest.mark.reports
class TestReportsAPI(APITestCase):
    """Test reports API endpoints."""
    
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
        self.template = ReportTemplate.objects.create(
            name='Test Template',
            description='Test template description',
            report_type='single_tax',
            format='xml',
            template_content='<test>Template content</test>',
            is_active=True,
            is_public=True
        )
        self.client.force_authenticate(user=self.user)
    
    def test_report_template_list(self):
        """Test report template list endpoint."""
        url = reverse('reports:reporttemplate-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Template')
    
    def test_report_list(self):
        """Test report list endpoint."""
        Report.objects.create(
            user=self.user,
            fop_profile=self.fop_profile,
            tax_period=self.tax_period,
            template=self.template,
            name='Test Report',
            description='Test report description',
            report_type='single_tax',
            format='xml'
        )
        url = reverse('reports:report-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_report_create(self):
        """Test report creation endpoint."""
        url = reverse('reports:report-list')
        data = {
            'fop_profile_id': self.fop_profile.id,
            'tax_period_id': self.tax_period.id,
            'template_id': self.template.id,
            'name': 'New Report',
            'description': 'New report description',
            'report_type': 'single_tax',
            'format': 'xml'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Report.objects.filter(name='New Report').exists())
    
    def test_report_generate(self):
        """Test report generation endpoint."""
        report = Report.objects.create(
            user=self.user,
            fop_profile=self.fop_profile,
            tax_period=self.tax_period,
            template=self.template,
            name='Test Report',
            description='Test report description',
            report_type='single_tax',
            format='xml'
        )
        url = reverse('reports:report-generate', kwargs={'pk': report.id})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_report_download(self):
        """Test report download endpoint."""
        report = Report.objects.create(
            user=self.user,
            fop_profile=self.fop_profile,
            tax_period=self.tax_period,
            template=self.template,
            name='Test Report',
            description='Test report description',
            report_type='single_tax',
            format='xml',
            status='ready'
        )
        url = reverse('reports:report-download', kwargs={'pk': report.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

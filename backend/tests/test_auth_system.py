"""
Unit tests for auth_system module.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_system.models import User, Role, UserProfile, UserSession, AuditLog

User = get_user_model()


@pytest.mark.unit
@pytest.mark.auth
class TestUserModel(TestCase):
    """Test User model."""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_user_creation(self):
        """Test user creation."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_superuser_creation(self):
        """Test superuser creation."""
        user = User.objects.create_superuser(**self.user_data)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'test@example.com')
    
    def test_user_required_fields(self):
        """Test user required fields."""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username='test',
                email='',
                password='testpass123'
            )


@pytest.mark.unit
@pytest.mark.auth
class TestRoleModel(TestCase):
    """Test Role model."""
    
    def test_role_creation(self):
        """Test role creation."""
        role = Role.objects.create(
            name='test_role',
            description='Test role description',
            permissions=['auth.add_user', 'auth.change_user']
        )
        self.assertEqual(role.name, 'test_role')
        self.assertEqual(role.description, 'Test role description')
        self.assertEqual(role.permissions, ['auth.add_user', 'auth.change_user'])
    
    def test_role_str_representation(self):
        """Test role string representation."""
        role = Role.objects.create(
            name='test_role',
            description='Test role description'
        )
        self.assertEqual(str(role), 'test_role')


@pytest.mark.unit
@pytest.mark.auth
class TestUserProfileModel(TestCase):
    """Test UserProfile model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        """Test user profile creation."""
        profile = UserProfile.objects.create(
            user=self.user,
            phone='+380123456789',
            timezone='Europe/Kiev',
            language='uk'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.phone, '+380123456789')
        self.assertEqual(profile.timezone, 'Europe/Kiev')
        self.assertEqual(profile.language, 'uk')
    
    def test_user_profile_str_representation(self):
        """Test user profile string representation."""
        profile = UserProfile.objects.create(
            user=self.user,
            phone='+380123456789'
        )
        self.assertEqual(str(profile), 'test@example.com Profile')


@pytest.mark.unit
@pytest.mark.auth
class TestUserSessionModel(TestCase):
    """Test UserSession model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_session_creation(self):
        """Test user session creation."""
        session = UserSession.objects.create(
            user=self.user,
            session_key='test_session_key',
            ip_address='192.168.1.1',
            user_agent='Test Browser'
        )
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.session_key, 'test_session_key')
        self.assertEqual(session.ip_address, '192.168.1.1')
        self.assertEqual(session.user_agent, 'Test Browser')
        self.assertTrue(session.is_active)


@pytest.mark.unit
@pytest.mark.auth
class TestAuditLogModel(TestCase):
    """Test AuditLog model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_audit_log_creation(self):
        """Test audit log creation."""
        log = AuditLog.objects.create(
            user=self.user,
            action='LOGIN',
            resource_type='User',
            resource_id=str(self.user.id),
            details={'ip': '192.168.1.1'}
        )
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'LOGIN')
        self.assertEqual(log.resource_type, 'User')
        self.assertEqual(log.resource_id, str(self.user.id))
        self.assertEqual(log.details, {'ip': '192.168.1.1'})


@pytest.mark.integration
@pytest.mark.auth
class TestAuthAPI(APITestCase):
    """Test authentication API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.login_url = reverse('auth_system:login')
        self.register_url = reverse('auth_system:register')
        self.profile_url = reverse('auth_system:profile')
    
    def test_user_registration(self):
        """Test user registration."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
    
    def test_user_login(self):
        """Test user login."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_user_profile_access(self):
        """Test user profile access."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_user_profile_update(self):
        """Test user profile update."""
        self.client.force_authenticate(user=self.user)
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')

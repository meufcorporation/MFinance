"""
Test settings for MFinance project.
"""

from .settings import *
import os

# Use in-memory database for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Disable Celery for tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable Redis for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Disable logging for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}

# Test-specific settings
SECRET_KEY = 'test-secret-key'
DEBUG = False
ALLOWED_HOSTS = ['testserver']

# Disable external services
KEYCLOAK_OP_AUTHORIZATION_ENDPOINT = 'http://testserver/auth'
KEYCLOAK_OP_TOKEN_ENDPOINT = 'http://testserver/token'
KEYCLOAK_OP_USER_ENDPOINT = 'http://testserver/userinfo'
KEYCLOAK_OP_JWKS_ENDPOINT = 'http://testserver/jwks'
KEYCLOAK_OP_LOGOUT_ENDPOINT = 'http://testserver/logout'

# Media files for tests
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')
MEDIA_URL = '/test_media/'

# Static files for tests
STATIC_ROOT = os.path.join(BASE_DIR, 'test_static')

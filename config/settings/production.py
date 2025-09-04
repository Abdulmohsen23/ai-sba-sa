import os
import dj_database_url
from .base import *

# Security
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-key-change-in-production')
ALLOWED_HOSTS = ['*']  # Railway handles domain security

# Database
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.parse(DATABASE_URL)
else:
    # Fallback to SQLite for development
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

# Static and Media Files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security Settings (enable after HTTPS is confirmed)
if not DEBUG:
    SECURE_SSL_REDIRECT = False  # Railway handles SSL
    SESSION_COOKIE_SECURE = False  # Enable after confirming HTTPS works
    CSRF_COOKIE_SECURE = False  # Enable after confirming HTTPS works
    
# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'program_ideation': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'askme': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Cache (optional - add Redis later if needed)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
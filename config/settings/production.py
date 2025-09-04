import os
import dj_database_url
from .base import *

# Railway automatically sets DEBUG=False for production
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Railway provides RAILWAY_ENVIRONMENT variable
RAILWAY_ENVIRONMENT = os.environ.get('RAILWAY_ENVIRONMENT')

# Use Railway's provided secret key or fallback
SECRET_KEY = os.environ.get('SECRET_KEY', os.environ.get('RAILWAY_SECRET_KEY', 'fallback-secret-key'))

# Railway automatically provides domains
ALLOWED_HOSTS = ['*']  # Railway handles this securely

# Database - Railway provides DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.parse(DATABASE_URL)

# Static files configuration for Railway
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Disable S3 storage for now - use local storage on Railway
# DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings - only enable if HTTPS is properly configured
if RAILWAY_ENVIRONMENT == 'production':
    # SECURE_SSL_REDIRECT = True
    # SESSION_COOKIE_SECURE = True
    # CSRF_COOKIE_SECURE = True
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True
    pass

# Logging configuration for Railway
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
            'level': 'INFO',
        },
    },
}
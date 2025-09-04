#!/usr/bin/env python
"""
Script to create superuser in production.
"""
import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create superuser if it doesn't exist
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='Mohsen',                    # Change this to your preferred username
        email='Abdull.11@outlook.com',     # Change this to your email
        password='Moh*123321'   # Change this to a strong password
    )
    print("Superuser created successfully!")
else:
    print("Superuser already exists.")
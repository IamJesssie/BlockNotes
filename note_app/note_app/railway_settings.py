"""
Railway-specific Django settings
This file extends the main settings.py for Railway deployment
"""

import os
from pathlib import Path
from decouple import config

# Import all settings from main settings.py
from .settings import *

# Override settings for Railway deployment
SECRET_KEY = config('SECRET_KEY', default='django-insecure-railway-deployment-key')
DEBUG = config('DEBUG', default=False, cast=bool)

# Railway provides specific hosts
ALLOWED_HOSTS = ['*']  # Allow all Railway subdomains

# Database configuration for Railway
if 'DATABASE_URL' in os.environ:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }

# Static files configuration for Railway
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise for serving static files
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add Whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
"""Django settings for django-seo-audit test suite."""

import os

# Build paths inside the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in tests secret!
SECRET_KEY = "test-secret-key-for-django-seo-audit-do-not-use-in-production"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django_seo_audit",
    "tests.example_app",
]

MIDDLEWARE = []

ROOT_URLCONF = None

TEMPLATES = []

# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
# https://docs.djangoproject.com/en/stable/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Test settings
# Disable migrations for faster tests
# Comment out if you need to test migrations
# MIGRATION_MODULES = {
#     app: None
#     for app in INSTALLED_APPS
#     if app not in ["django.contrib.contenttypes", "django.contrib.auth"]
# }

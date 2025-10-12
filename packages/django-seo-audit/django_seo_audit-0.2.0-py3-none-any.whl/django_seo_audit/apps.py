"""Django app configuration for django-seo-audit."""

from django.apps import AppConfig


class DjangoSeoAuditConfig(AppConfig):
    """AppConfig for django-seo-audit package."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_seo_audit"
    verbose_name = "Django SEO Audit"

"""AppConfig for example_app."""

from django.apps import AppConfig


class ExampleAppConfig(AppConfig):
    """Configuration for the example app used in testing."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "tests.example_app"
    verbose_name = "Example App"

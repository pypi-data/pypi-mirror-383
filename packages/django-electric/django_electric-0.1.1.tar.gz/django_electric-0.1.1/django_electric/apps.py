"""Django app configuration for django-electric."""

from django.apps import AppConfig
from django.conf import settings


class DjangoElectricConfig(AppConfig):
    """Configuration for the Django Electric app."""

    name = "django_electric"
    verbose_name = "Django Electric"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        """
        Called when Django starts.
        Register signals and validate settings.
        """
        # Import signal handlers
        from . import signals  # noqa: F401

        # Validate Electric SQL settings
        self._validate_settings()

    def _validate_settings(self) -> None:
        """Validate that required Electric SQL settings are present."""
        required_settings = ["ELECTRIC_SERVICE_URL"]

        for setting in required_settings:
            if not hasattr(settings, setting):
                raise ImproperlyConfigured(
                    f"'{setting}' must be defined in Django settings to use django-electric"
                )


from django.core.exceptions import ImproperlyConfigured

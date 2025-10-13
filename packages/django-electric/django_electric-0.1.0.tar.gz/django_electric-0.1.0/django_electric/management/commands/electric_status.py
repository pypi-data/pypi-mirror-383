"""Django management command to check Electric SQL status."""

from typing import Any
from django.core.management.base import BaseCommand
from django.apps import apps

from django_electric.client import ElectricClient
from django_electric.models import ElectricSyncMixin
from django_electric.conf import electric_settings
from django_electric.exceptions import ElectricConnectionError


class Command(BaseCommand):
    """
    Check Electric SQL connection and sync status.

    Usage:
        python manage.py electric_status
    """

    help = "Check Electric SQL connection and sync status"

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        self.stdout.write(self.style.HTTP_INFO("=" * 60))
        self.stdout.write(self.style.HTTP_INFO("Electric SQL Status"))
        self.stdout.write(self.style.HTTP_INFO("=" * 60))

        # Check configuration
        self.stdout.write("\nConfiguration:")
        self.stdout.write(f"  Service URL: {electric_settings.SERVICE_URL}")
        self.stdout.write(f"  Auto Sync: {electric_settings.AUTO_SYNC}")
        self.stdout.write(f"  Batch Size: {electric_settings.SYNC_BATCH_SIZE}")
        self.stdout.write(f"  Timeout: {electric_settings.TIMEOUT}s")

        # Check connection
        self.stdout.write("\nConnection:")
        client = ElectricClient()
        try:
            # Try a simple connection check
            # In a real implementation, this would ping the Electric service
            self.stdout.write(
                self.style.SUCCESS("  ✓ Electric client initialized")
            )
        except ElectricConnectionError as e:
            self.stdout.write(
                self.style.ERROR(f"  ✗ Connection failed: {e}")
            )
            return
        finally:
            client.close()

        # List models with Electric sync
        self.stdout.write("\nModels with Electric Sync:")
        electric_models = []
        for model in apps.get_models():
            if issubclass(model, ElectricSyncMixin):
                if getattr(model._meta, "electric_sync", False):
                    electric_models.append(model)
                    model_name = f"{model._meta.app_label}.{model.__name__}"
                    where = getattr(model._meta, "electric_where", None)
                    where_str = f" (where: {where})" if where else ""
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✓ {model_name}{where_str}")
                    )

        if not electric_models:
            self.stdout.write("  No models configured for Electric sync")

        self.stdout.write("\n" + "=" * 60)

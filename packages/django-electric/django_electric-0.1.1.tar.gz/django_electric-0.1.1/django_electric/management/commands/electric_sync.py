"""Django management command to sync models with Electric SQL."""

from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from django.apps import apps

from django_electric.sync import SyncManager
from django_electric.models import ElectricSyncMixin


class Command(BaseCommand):
    """
    Sync Django models with Electric SQL.

    Usage:
        python manage.py electric_sync
        python manage.py electric_sync --model myapp.MyModel
        python manage.py electric_sync --model myapp.MyModel --where "active = true"
        python manage.py electric_sync --all --force
    """

    help = "Sync Django models with Electric SQL"

    def add_arguments(self, parser: CommandParser) -> None:
        """Add command arguments."""
        parser.add_argument(
            "--model",
            type=str,
            help="Specific model to sync (format: app_label.ModelName)",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Sync all models with ElectricSyncMixin",
        )
        parser.add_argument(
            "--where",
            type=str,
            help="SQL WHERE clause for filtering",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force sync even if recently synced",
        )
        parser.add_argument(
            "--pull",
            action="store_true",
            help="Pull data from Electric to local database",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        model_name = options.get("model")
        sync_all = options.get("all")
        where = options.get("where")
        force = options.get("force", False)
        pull = options.get("pull", False)

        if not model_name and not sync_all:
            self.stdout.write(
                self.style.ERROR("Please specify --model or --all")
            )
            return

        models_to_sync = []

        if sync_all:
            # Find all models with ElectricSyncMixin
            for model in apps.get_models():
                if issubclass(model, ElectricSyncMixin):
                    # Check if electric_sync is enabled in Meta
                    if getattr(model._meta, "electric_sync", False):
                        models_to_sync.append(model)

            self.stdout.write(
                self.style.SUCCESS(f"Found {len(models_to_sync)} models to sync")
            )

        elif model_name:
            # Parse app_label.ModelName
            try:
                app_label, model_class_name = model_name.split(".")
                model = apps.get_model(app_label, model_class_name)

                if not issubclass(model, ElectricSyncMixin):
                    self.stdout.write(
                        self.style.ERROR(
                            f"{model_name} does not use ElectricSyncMixin"
                        )
                    )
                    return

                models_to_sync.append(model)

            except ValueError:
                self.stdout.write(
                    self.style.ERROR(
                        "Invalid model format. Use: app_label.ModelName"
                    )
                )
                return
            except LookupError:
                self.stdout.write(
                    self.style.ERROR(f"Model {model_name} not found")
                )
                return

        # Sync each model
        for model in models_to_sync:
            self.sync_model(model, where=where, force=force, pull=pull)

    def sync_model(
        self,
        model: Any,
        where: str = None,
        force: bool = False,
        pull: bool = False,
    ) -> None:
        """
        Sync a specific model.

        Args:
            model: Django model class
            where: SQL WHERE clause
            force: Force sync
            pull: Pull data to local database
        """
        model_name = f"{model._meta.app_label}.{model.__name__}"

        try:
            self.stdout.write(f"Syncing {model_name}...")

            if pull:
                # Pull data from Electric
                stats = model.electric_pull(where=where)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ {model_name}: "
                        f"created={stats['created']}, "
                        f"updated={stats['updated']}, "
                        f"errors={stats['errors']}"
                    )
                )
            else:
                # Just sync the shape
                result = model.electric_sync(where=where, force=force)
                shape_id = result.get("shape_id", "unknown")
                cached = " (cached)" if result.get("cached") else ""
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ {model_name}: shape_id={shape_id}{cached}"
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ✗ {model_name}: {str(e)}")
            )

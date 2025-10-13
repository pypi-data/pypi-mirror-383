"""Custom Django model managers for Electric SQL."""

from typing import Optional, Any
from django.db import models
from django.db.models import QuerySet

from .sync import SyncManager


class ElectricQuerySet(QuerySet):
    """
    Custom QuerySet with Electric sync capabilities.

    Example:
        >>> User.objects.electric_sync(where="is_active = true")
    """

    def electric_sync(self, where: Optional[str] = None, force: bool = False) -> Any:
        """
        Sync this queryset with Electric SQL.

        Args:
            where: Additional WHERE clause
            force: Force sync even if recently synced

        Returns:
            Sync result
        """
        # Use the model's sync method
        if hasattr(self.model, "electric_sync"):
            return self.model.electric_sync(where=where, force=force)
        raise NotImplementedError(
            f"{self.model.__name__} must use ElectricSyncMixin for sync operations"
        )

    def electric_pull(
        self,
        where: Optional[str] = None,
        update_existing: bool = True,
    ) -> Any:
        """
        Pull data from Electric SQL for this queryset.

        Args:
            where: Additional WHERE clause
            update_existing: Update existing records

        Returns:
            Sync statistics
        """
        if hasattr(self.model, "electric_pull"):
            return self.model.electric_pull(where=where, update_existing=update_existing)
        raise NotImplementedError(
            f"{self.model.__name__} must use ElectricSyncMixin for sync operations"
        )


class ElectricManager(models.Manager):
    """
    Custom model manager with Electric SQL sync capabilities.

    Use this as the manager for models that use Electric sync.

    Example:
        >>> class User(ElectricSyncMixin, models.Model):
        ...     username = models.CharField(max_length=100)
        ...     objects = ElectricManager()
        ...
        >>> User.objects.electric_sync()
    """

    def get_queryset(self) -> ElectricQuerySet:
        """Return custom queryset with Electric methods."""
        return ElectricQuerySet(self.model, using=self._db)

    def electric_sync(self, where: Optional[str] = None, force: bool = False) -> Any:
        """
        Sync all objects with Electric SQL.

        Args:
            where: SQL WHERE clause for filtering
            force: Force sync even if recently synced

        Returns:
            Sync result
        """
        return self.get_queryset().electric_sync(where=where, force=force)

    def electric_pull(
        self,
        where: Optional[str] = None,
        update_existing: bool = True,
    ) -> Any:
        """
        Pull data from Electric SQL to local database.

        Args:
            where: SQL WHERE clause for filtering
            update_existing: Update existing records

        Returns:
            Sync statistics
        """
        return self.get_queryset().electric_pull(where=where, update_existing=update_existing)

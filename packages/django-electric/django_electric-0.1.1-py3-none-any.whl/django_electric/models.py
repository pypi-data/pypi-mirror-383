"""Django model mixins for Electric SQL integration."""

from typing import Optional, Dict, Any, List
from django.db import models

from .sync import SyncManager, SyncShape


class ElectricSyncMixin:
    """
    Mixin for Django models to add Electric SQL sync capabilities.

    Add this mixin to your models to enable automatic syncing with Electric.

    Example:
        >>> class User(ElectricSyncMixin, models.Model):
        ...     username = models.CharField(max_length=100)
        ...     email = models.EmailField()
        ...
        ...     class Meta:
        ...         electric_sync = True
        ...         electric_where = "is_active = true"

    Class Attributes:
        electric_sync (bool): Enable sync for this model
        electric_where (str): Default WHERE clause for syncing
        electric_columns (list): Columns to sync (defaults to all)
        electric_include (dict): Related models to include
    """

    # Class-level sync manager (shared across all instances)
    _electric_manager: Optional[SyncManager] = None

    @classmethod
    def get_electric_manager(cls) -> SyncManager:
        """Get or create the Electric sync manager for this model."""
        if cls._electric_manager is None:
            cls._electric_manager = SyncManager()
        return cls._electric_manager

    @classmethod
    def get_electric_shape(
        cls,
        where: Optional[str] = None,
        columns: Optional[List[str]] = None,
        include: Optional[Dict[str, Any]] = None,
    ) -> SyncShape:
        """
        Get Electric sync shape for this model.

        Args:
            where: SQL WHERE clause (uses Meta.electric_where if not provided)
            columns: Columns to sync (uses Meta.electric_columns if not provided)
            include: Related models (uses Meta.electric_include if not provided)

        Returns:
            SyncShape instance
        """
        # Get defaults from Meta
        meta_where = getattr(cls._meta, "electric_where", None)
        meta_columns = getattr(cls._meta, "electric_columns", None)
        meta_include = getattr(cls._meta, "electric_include", None)

        # Override with provided values
        where = where or meta_where
        columns = columns or meta_columns
        include = include or meta_include

        manager = cls.get_electric_manager()
        return manager.create_shape_for_model(
            cls,
            where=where,
            columns=columns,
            include=include,
        )

    @classmethod
    def electric_sync(
        cls,
        where: Optional[str] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Sync this model with Electric SQL.

        Args:
            where: SQL WHERE clause for filtering
            force: Force sync even if recently synced

        Returns:
            Sync result

        Example:
            >>> User.electric_sync(where="is_active = true")
        """
        shape = cls.get_electric_shape(where=where)
        manager = cls.get_electric_manager()
        return manager.sync(shape, force=force)

    @classmethod
    def electric_pull(
        cls,
        where: Optional[str] = None,
        batch_size: Optional[int] = None,
        update_existing: bool = True,
    ) -> Dict[str, int]:
        """
        Pull data from Electric SQL to local database.

        Args:
            where: SQL WHERE clause for filtering
            batch_size: Batch size for operations
            update_existing: Update existing records

        Returns:
            Dictionary with stats (created, updated, skipped)

        Example:
            >>> stats = User.electric_pull(where="is_active = true")
            >>> print(f"Created {stats['created']} users")
        """
        shape = cls.get_electric_shape(where=where)
        manager = cls.get_electric_manager()

        # Ensure shape is synced
        if not shape.shape_id:
            manager.sync(shape)

        return manager.sync_to_model(
            shape,
            cls,
            batch_size=batch_size,
            update_existing=update_existing,
        )

    @classmethod
    def electric_get_data(
        cls,
        where: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get synced data from Electric SQL.

        Args:
            where: SQL WHERE clause for filtering
            offset: Pagination offset
            limit: Number of records

        Returns:
            List of records

        Example:
            >>> users = User.electric_get_data(limit=50)
        """
        shape = cls.get_electric_shape(where=where)
        manager = cls.get_electric_manager()

        # Ensure shape is synced
        if not shape.shape_id:
            manager.sync(shape)

        return manager.get_shape_data(shape, offset=offset, limit=limit)

"""Sync management for Electric SQL."""

import logging
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass
from datetime import datetime

from django.db import models
from django.core.cache import cache

from .client import ElectricClient
from .conf import electric_settings
from .exceptions import ElectricSyncError, ShapeNotFoundError

logger = logging.getLogger(__name__)


@dataclass
class SyncShape:
    """
    Represents a sync shape configuration.

    Attributes:
        table: Table name
        where: SQL WHERE clause
        columns: List of columns to sync
        include: Related tables to include
        shape_id: ID assigned by Electric service
        last_synced: Last sync timestamp
    """

    table: str
    where: Optional[str] = None
    columns: Optional[List[str]] = None
    include: Optional[Dict[str, Any]] = None
    shape_id: Optional[str] = None
    last_synced: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        shape_dict: Dict[str, Any] = {"table": self.table}

        if self.where:
            shape_dict["where"] = self.where
        if self.columns:
            shape_dict["columns"] = self.columns
        if self.include:
            shape_dict["include"] = self.include

        return shape_dict


class SyncManager:
    """
    Manages sync operations between Django models and Electric SQL.

    This manager handles:
    - Creating and managing shapes
    - Syncing data between local and remote
    - Caching sync metadata
    - Batch operations

    Example:
        >>> manager = SyncManager()
        >>> shape = manager.create_shape_for_model(MyModel, where="active = true")
        >>> manager.sync(shape)
        >>> data = manager.get_shape_data(shape)
    """

    def __init__(self, client: Optional[ElectricClient] = None):
        """
        Initialize sync manager.

        Args:
            client: Electric client instance (creates default if not provided)
        """
        self.client = client or ElectricClient()
        self._shapes: Dict[str, SyncShape] = {}

    def create_shape_for_model(
        self,
        model: Type[models.Model],
        where: Optional[str] = None,
        columns: Optional[List[str]] = None,
        include: Optional[Dict[str, Any]] = None,
    ) -> SyncShape:
        """
        Create a sync shape for a Django model.

        Args:
            model: Django model class
            where: SQL WHERE clause for filtering
            columns: Specific columns to sync (defaults to all)
            include: Related models to include

        Returns:
            SyncShape instance

        Example:
            >>> shape = manager.create_shape_for_model(
            ...     User,
            ...     where="is_active = true",
            ...     columns=["id", "username", "email"]
            ... )
        """
        table_name = model._meta.db_table

        if columns is None:
            # Get all field names from model
            columns = [field.column for field in model._meta.fields]

        shape = SyncShape(
            table=table_name,
            where=where,
            columns=columns,
            include=include,
        )

        return shape

    def sync(self, shape: SyncShape, force: bool = False) -> Dict[str, Any]:
        """
        Sync a shape with Electric service.

        Args:
            shape: SyncShape to sync
            force: Force sync even if recently synced

        Returns:
            Sync result from Electric service

        Raises:
            ElectricSyncError: If sync fails
        """
        cache_key = f"electric_shape_{shape.table}_{hash(shape.where or '')}"

        # Check cache unless forcing
        if not force:
            cached_shape_id = cache.get(cache_key)
            if cached_shape_id:
                shape.shape_id = cached_shape_id
                logger.debug(f"Using cached shape ID: {cached_shape_id}")
                return {"shape_id": cached_shape_id, "cached": True}

        try:
            logger.info(f"Syncing shape for table '{shape.table}'")
            result = self.client.sync_shape(shape.to_dict())

            shape.shape_id = result.get("shape_id")
            shape.last_synced = datetime.now()

            # Cache the shape ID
            if shape.shape_id:
                cache.set(cache_key, shape.shape_id, timeout=3600)  # 1 hour
                self._shapes[shape.shape_id] = shape

            logger.info(f"Shape synced successfully: {shape.shape_id}")
            return result

        except Exception as e:
            logger.error(f"Failed to sync shape: {e}")
            raise ElectricSyncError(f"Sync failed for table '{shape.table}': {e}")

    def get_shape_data(
        self,
        shape: SyncShape,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get data for a synced shape.

        Args:
            shape: SyncShape to fetch data for
            offset: Pagination offset
            limit: Number of records to fetch

        Returns:
            List of records

        Raises:
            ShapeNotFoundError: If shape hasn't been synced
        """
        if not shape.shape_id:
            raise ShapeNotFoundError(
                f"Shape for table '{shape.table}' has not been synced yet. "
                "Call sync() first."
            )

        try:
            result = self.client.get_shape_data(shape.shape_id, offset=offset, limit=limit)
            return result.get("data", [])

        except Exception as e:
            logger.error(f"Failed to fetch shape data: {e}")
            raise ElectricSyncError(f"Failed to fetch data: {e}")

    def sync_to_model(
        self,
        shape: SyncShape,
        model: Type[models.Model],
        batch_size: Optional[int] = None,
        update_existing: bool = True,
    ) -> Dict[str, int]:
        """
        Sync Electric data to Django model.

        Args:
            shape: SyncShape to sync from
            model: Django model to sync to
            batch_size: Batch size for bulk operations
            update_existing: Update existing records or skip

        Returns:
            Dictionary with stats (created, updated, skipped)

        Example:
            >>> stats = manager.sync_to_model(shape, User)
            >>> print(f"Created: {stats['created']}, Updated: {stats['updated']}")
        """
        if not shape.shape_id:
            # Sync the shape first
            self.sync(shape)

        batch_size = batch_size or electric_settings.SYNC_BATCH_SIZE
        stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}

        try:
            offset = 0
            while True:
                data = self.get_shape_data(shape, offset=offset, limit=batch_size)

                if not data:
                    break

                for record in data:
                    try:
                        pk_field = model._meta.pk.name
                        pk_value = record.get(pk_field)

                        if pk_value and update_existing:
                            obj, created = model.objects.update_or_create(
                                **{pk_field: pk_value},
                                defaults=record,
                            )
                            if created:
                                stats["created"] += 1
                            else:
                                stats["updated"] += 1
                        else:
                            model.objects.create(**record)
                            stats["created"] += 1

                    except Exception as e:
                        logger.error(f"Error syncing record: {e}")
                        stats["errors"] += 1

                offset += batch_size

            logger.info(f"Sync completed: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Sync to model failed: {e}")
            raise ElectricSyncError(f"Failed to sync to model: {e}")

    def get_shape_by_id(self, shape_id: str) -> Optional[SyncShape]:
        """Get a shape by its ID."""
        return self._shapes.get(shape_id)

    def clear_cache(self, table: Optional[str] = None) -> None:
        """
        Clear cached shape information.

        Args:
            table: Specific table to clear (clears all if None)
        """
        if table:
            cache_pattern = f"electric_shape_{table}_*"
            logger.info(f"Clearing cache for table: {table}")
            # Django cache doesn't support pattern deletion by default
            # Implementation depends on cache backend
        else:
            self._shapes.clear()
            logger.info("Cleared all shape cache")

    def close(self) -> None:
        """Close the Electric client connection."""
        self.client.close()

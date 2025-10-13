"""Exceptions for django-electric."""


class ElectricError(Exception):
    """Base exception for all Electric-related errors."""

    pass


class ElectricConnectionError(ElectricError):
    """Raised when connection to Electric service fails."""

    pass


class ElectricSyncError(ElectricError):
    """Raised when sync operation fails."""

    pass


class ElectricConfigurationError(ElectricError):
    """Raised when Electric is misconfigured."""

    pass


class ShapeNotFoundError(ElectricError):
    """Raised when a shape is not found."""

    pass

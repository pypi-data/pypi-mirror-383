"""Configuration utilities for django-electric."""

from typing import Any, Dict, Optional
from django.conf import settings


class ElectricSettings:
    """
    Settings for Django Electric.

    Reads configuration from Django settings with sensible defaults.
    """

    @property
    def SERVICE_URL(self) -> str:
        """Electric service URL."""
        return getattr(settings, "ELECTRIC_SERVICE_URL", "")

    @property
    def DATABASE_URL(self) -> Optional[str]:
        """Database connection URL for Electric."""
        return getattr(settings, "ELECTRIC_DATABASE_URL", None)

    @property
    def AUTH_TOKEN(self) -> Optional[str]:
        """Authentication token for Electric service."""
        return getattr(settings, "ELECTRIC_AUTH_TOKEN", None)

    @property
    def RECONNECT_INTERVAL(self) -> int:
        """Reconnection interval in milliseconds."""
        return getattr(settings, "ELECTRIC_RECONNECT_INTERVAL", 5000)

    @property
    def TIMEOUT(self) -> int:
        """Request timeout in seconds."""
        return getattr(settings, "ELECTRIC_TIMEOUT", 30)

    @property
    def DEBUG(self) -> bool:
        """Enable debug mode."""
        return getattr(settings, "ELECTRIC_DEBUG", settings.DEBUG)

    @property
    def AUTO_SYNC(self) -> bool:
        """Automatically start syncing when models are accessed."""
        return getattr(settings, "ELECTRIC_AUTO_SYNC", True)

    @property
    def SYNC_BATCH_SIZE(self) -> int:
        """Batch size for sync operations."""
        return getattr(settings, "ELECTRIC_SYNC_BATCH_SIZE", 100)

    @property
    def MIDDLEWARE_ENABLED(self) -> bool:
        """Enable Electric middleware."""
        return getattr(settings, "ELECTRIC_MIDDLEWARE_ENABLED", False)

    def get_client_config(self) -> Dict[str, Any]:
        """Get configuration dict for Electric client."""
        config: Dict[str, Any] = {
            "url": self.SERVICE_URL,
            "timeout": self.TIMEOUT,
            "reconnect_interval": self.RECONNECT_INTERVAL,
            "debug": self.DEBUG,
        }

        if self.DATABASE_URL:
            config["database_url"] = self.DATABASE_URL

        if self.AUTH_TOKEN:
            config["auth_token"] = self.AUTH_TOKEN

        return config


electric_settings = ElectricSettings()

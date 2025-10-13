"""Middleware for Electric SQL integration."""

import logging
from typing import Callable
from django.http import HttpRequest, HttpResponse

from .conf import electric_settings

logger = logging.getLogger(__name__)


class ElectricSyncMiddleware:
    """
    Middleware to handle Electric SQL sync operations per request.

    This middleware can:
    - Track sync status in request context
    - Handle sync errors gracefully
    - Add sync metadata to responses

    Add to MIDDLEWARE in settings.py:
        MIDDLEWARE = [
            ...
            'django_electric.middleware.ElectricSyncMiddleware',
            ...
        ]
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        """Initialize middleware."""
        self.get_response = get_response
        self.enabled = electric_settings.MIDDLEWARE_ENABLED

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request."""
        if not self.enabled:
            return self.get_response(request)

        # Add Electric context to request
        request.electric_sync_enabled = True

        # Process request
        response = self.get_response(request)

        # Add sync metadata to response headers (optional)
        if hasattr(request, "electric_sync_count"):
            response["X-Electric-Syncs"] = str(request.electric_sync_count)

        return response

    def process_exception(
        self, request: HttpRequest, exception: Exception
    ) -> None:
        """Handle exceptions during request processing."""
        # Log Electric-related exceptions
        from .exceptions import ElectricError

        if isinstance(exception, ElectricError):
            logger.error(f"Electric sync error in request: {exception}")


class ElectricReadOnlyMiddleware:
    """
    Middleware to prevent writes when syncing from Electric.

    Use this middleware to ensure data integrity during sync operations.

    Add to MIDDLEWARE in settings.py:
        MIDDLEWARE = [
            ...
            'django_electric.middleware.ElectricReadOnlyMiddleware',
            ...
        ]
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        """Initialize middleware."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request."""
        # Check if request is during sync
        if getattr(request, "electric_syncing", False):
            # Mark request as read-only
            request.electric_read_only = True

        return self.get_response(request)

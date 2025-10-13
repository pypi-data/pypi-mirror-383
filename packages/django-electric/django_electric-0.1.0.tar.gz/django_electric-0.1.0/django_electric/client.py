"""Electric SQL client wrapper for Django."""

import logging
from typing import Any, Dict, List, Optional, Callable
from urllib.parse import urljoin
import asyncio
import json

import requests
import websockets

from .conf import electric_settings
from .exceptions import ElectricConnectionError, ElectricSyncError

logger = logging.getLogger(__name__)


class ElectricClient:
    """
    Client for interacting with Electric SQL sync service.

    This client handles:
    - Connection management to Electric service
    - Shape-based sync operations
    - WebSocket connections for real-time updates
    - Authentication and error handling

    Example:
        >>> client = ElectricClient()
        >>> shape = client.create_shape(table="users", where="active = true")
        >>> client.sync_shape(shape)
    """

    def __init__(
        self,
        url: Optional[str] = None,
        auth_token: Optional[str] = None,
        timeout: Optional[int] = None,
        debug: bool = False,
    ):
        """
        Initialize Electric client.

        Args:
            url: Electric service URL (defaults to settings)
            auth_token: Authentication token (defaults to settings)
            timeout: Request timeout in seconds (defaults to settings)
            debug: Enable debug logging (defaults to settings)
        """
        self.url = url or electric_settings.SERVICE_URL
        self.auth_token = auth_token or electric_settings.AUTH_TOKEN
        self.timeout = timeout or electric_settings.TIMEOUT
        self.debug = debug or electric_settings.DEBUG

        self._session: Optional[requests.Session] = None
        self._ws_connection: Optional[websockets.WebSocketClientProtocol] = None
        self._subscriptions: Dict[str, Callable] = {}

        if self.debug:
            logger.setLevel(logging.DEBUG)

    @property
    def session(self) -> requests.Session:
        """Get or create HTTP session."""
        if self._session is None:
            self._session = requests.Session()
            if self.auth_token:
                self._session.headers["Authorization"] = f"Bearer {self.auth_token}"
            self._session.headers["Content-Type"] = "application/json"
        return self._session

    def create_shape(
        self,
        table: str,
        where: Optional[str] = None,
        columns: Optional[List[str]] = None,
        include: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a sync shape definition.

        Args:
            table: Table name to sync
            where: SQL WHERE clause for filtering
            columns: List of columns to include
            include: Related tables to include

        Returns:
            Shape definition dictionary

        Example:
            >>> shape = client.create_shape(
            ...     table="posts",
            ...     where="published = true",
            ...     columns=["id", "title", "content"],
            ...     include={"author": {"columns": ["name", "email"]}}
            ... )
        """
        shape: Dict[str, Any] = {"table": table}

        if where:
            shape["where"] = where
        if columns:
            shape["columns"] = columns
        if include:
            shape["include"] = include

        return shape

    def sync_shape(self, shape: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync a shape from Electric service.

        Args:
            shape: Shape definition from create_shape()

        Returns:
            Sync result containing data and metadata

        Raises:
            ElectricConnectionError: If connection fails
            ElectricSyncError: If sync operation fails
        """
        endpoint = urljoin(self.url, "/v1/shape")

        try:
            logger.debug(f"Syncing shape: {shape}")
            response = self.session.post(
                endpoint,
                json=shape,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.ConnectionError as e:
            raise ElectricConnectionError(f"Failed to connect to Electric service: {e}")
        except requests.exceptions.Timeout as e:
            raise ElectricConnectionError(f"Request timed out: {e}")
        except requests.exceptions.HTTPError as e:
            raise ElectricSyncError(f"Sync failed: {e}")
        except Exception as e:
            raise ElectricSyncError(f"Unexpected error during sync: {e}")

    def get_shape_data(self, shape_id: str, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        Get data for a synced shape.

        Args:
            shape_id: ID of the synced shape
            offset: Pagination offset
            limit: Number of records to fetch

        Returns:
            Shape data and pagination info
        """
        endpoint = urljoin(self.url, f"/v1/shape/{shape_id}")
        params = {"offset": offset, "limit": limit}

        try:
            response = self.session.get(endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            raise ElectricSyncError(f"Failed to fetch shape data: {e}")

    async def subscribe_to_shape(
        self,
        shape_id: str,
        callback: Callable[[Dict[str, Any]], None],
    ) -> None:
        """
        Subscribe to real-time updates for a shape via WebSocket.

        Args:
            shape_id: ID of the synced shape
            callback: Function to call with updates

        Example:
            >>> def on_update(data):
            ...     print(f"Received update: {data}")
            >>> await client.subscribe_to_shape("shape-123", on_update)
        """
        ws_url = self.url.replace("http://", "ws://").replace("https://", "wss://")
        ws_endpoint = urljoin(ws_url, f"/v1/shape/{shape_id}/stream")

        try:
            async with websockets.connect(ws_endpoint) as websocket:
                self._ws_connection = websocket
                self._subscriptions[shape_id] = callback

                logger.info(f"Subscribed to shape {shape_id}")

                async for message in websocket:
                    try:
                        data = json.loads(message)
                        callback(data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse WebSocket message: {e}")
                    except Exception as e:
                        logger.error(f"Error in callback: {e}")

        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            raise ElectricConnectionError(f"Failed to subscribe: {e}")

    def unsubscribe(self, shape_id: str) -> None:
        """Unsubscribe from shape updates."""
        if shape_id in self._subscriptions:
            del self._subscriptions[shape_id]
            logger.info(f"Unsubscribed from shape {shape_id}")

    def close(self) -> None:
        """Close all connections."""
        if self._session:
            self._session.close()
            self._session = None

        if self._ws_connection:
            asyncio.create_task(self._ws_connection.close())
            self._ws_connection = None

        self._subscriptions.clear()
        logger.info("Electric client closed")

    def __enter__(self) -> "ElectricClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

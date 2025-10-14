"""Base client for Stack Exchange API operations."""

import asyncio
import os
from typing import Any, Dict, Optional

import httpx

from stack_overflow_mcp_light.logging_config import get_logger

logger = get_logger(__name__)


class StackExchangeConnection:
    """Singleton connection manager for Stack Exchange API client."""

    _instance: Optional["StackExchangeConnection"] = None
    _initialized: bool = False

    def __new__(cls) -> "StackExchangeConnection":
        """Ensure only one connection instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the connection only once."""
        if not StackExchangeConnection._initialized:
            self._client: Optional[httpx.AsyncClient] = None
            self._api_key: Optional[str] = None
            self._base_url = "https://api.stackexchange.com/2.3"
            self._site = "stackoverflow"
            self._setup_client()
            StackExchangeConnection._initialized = True

    def _setup_client(self) -> None:
        """Setup Stack Exchange API client."""
        try:
            self._api_key = os.getenv("STACK_EXCHANGE_API_KEY")

            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "User-Agent": "Stack Overflow MCP Server/1.0.0",
            }

            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=headers,
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            )

            if self._api_key:
                logger.info("Stack Exchange API client initialized with API key")
            else:
                logger.info(
                    "Stack Exchange API client initialized without API key (rate limited)"
                )

        except Exception as e:
            logger.error(f"Failed to initialize Stack Exchange client: {e}")
            raise

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client."""
        if self._client is None:
            raise RuntimeError("HTTP client not initialized")
        return self._client

    @property
    def api_key(self) -> Optional[str]:
        """Get the API key."""
        return self._api_key

    @property
    def site(self) -> str:
        """Get the site parameter."""
        return self._site

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()


class BaseStackExchangeClient:
    """Base client that uses shared connection for Stack Exchange API operations."""

    def __init__(self) -> None:
        """Initialize the base client with shared connection."""
        self._connection = StackExchangeConnection()
        self._rate_limit_delay = 0.1  # Base delay between requests

    async def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the Stack Exchange API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            API response data

        Raises:
            httpx.HTTPStatusError: For HTTP errors
            ValueError: For API-specific errors
        """
        if params is None:
            params = {}

        # Add required site parameter
        params["site"] = self._connection.site

        # Add API key if available
        if self._connection.api_key:
            params["key"] = self._connection.api_key

        try:
            # Add rate limiting delay
            await asyncio.sleep(self._rate_limit_delay)

            response = await self._connection.client.get(endpoint, params=params)
            response.raise_for_status()

            # httpx automatically handles gzip decompression, so we can use .json() directly
            data = response.json()

            # Check for API errors in response
            if "error_id" in data:
                error_msg = data.get("error_message", "Unknown API error")
                logger.error(f"Stack Exchange API error: {error_msg}")
                raise ValueError(f"API Error: {error_msg}")

            # Check for rate limit information
            if "quota_remaining" in data:
                quota = data["quota_remaining"]
                if quota < 100:
                    logger.warning(f"API quota low: {quota} requests remaining")

            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for {endpoint}: {e.response.status_code}")
            # Handle specific HTTP errors
            if e.response.status_code == 429:
                logger.error("Rate limit exceeded")
                raise ValueError(
                    "Rate limit exceeded. Please wait before making more requests."
                )
            elif e.response.status_code == 400:
                logger.error(f"Bad request: {e.response.text}")
                raise ValueError("Invalid request parameters")
            else:
                raise ValueError(
                    f"HTTP error {e.response.status_code}: {e.response.text}"
                )

        except Exception as e:
            logger.error(f"Unexpected error making request to {endpoint}: {e}")
            raise ValueError(f"Request failed: {str(e)}")

    async def _paginated_request(
        self, endpoint: str, params: Dict[str, Any], page: int = 1, page_size: int = 30
    ) -> Dict[str, Any]:
        """
        Make a paginated request to the API.

        Args:
            endpoint: API endpoint path
            params: Base query parameters
            page: Page number
            page_size: Items per page

        Returns:
            API response data with pagination info
        """
        paginated_params = {**params, "page": page, "pagesize": page_size}

        return await self._make_request(endpoint, paginated_params)

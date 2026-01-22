"""Cached HTTP client with retry logic for external API calls."""

import httpx
import asyncio
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from hashlib import md5
import structlog

from swiss_ai_mcp_commons.serialization import JsonSerializableMixin

logger = structlog.get_logger(__name__)


class CachedHttpClient(JsonSerializableMixin):
    """HTTP client with caching and retry logic for API calls."""

    def __init__(
        self,
        base_url: str = "",
        cache_ttl_seconds: int = 120,
        max_retries: int = 3,
        timeout_seconds: int = 30,
    ):
        """Initialize cached HTTP client.

        Args:
            base_url: Base URL for all requests
            cache_ttl_seconds: Cache time-to-live in seconds
            max_retries: Maximum number of retry attempts
            timeout_seconds: Request timeout in seconds
        """
        self.base_url = base_url
        self.cache_ttl_seconds = cache_ttl_seconds
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    def _get_cache_key(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key from URL and params."""
        key_parts = [url]
        if params:
            # Sort params for consistent cache keys
            sorted_params = sorted(params.items())
            key_parts.append(str(sorted_params))

        combined = "".join(key_parts)
        return md5(combined.encode()).hexdigest()

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid."""
        if cache_key not in self._cache:
            return False

        _, timestamp = self._cache[cache_key]
        age = datetime.now() - timestamp
        return age.total_seconds() < self.cache_ttl_seconds

    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Get value from cache if valid."""
        if self._is_cache_valid(cache_key):
            value, _ = self._cache[cache_key]
            logger.info("cache_hit", cache_key=cache_key[:8])
            return value
        return None

    def _set_cache(self, cache_key: str, value: Any) -> None:
        """Store value in cache."""
        self._cache[cache_key] = (value, datetime.now())
        logger.info("cache_set", cache_key=cache_key[:8])

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Make GET request with optional caching and retries.

        Args:
            url: Request URL (relative to base_url)
            params: Query parameters
            use_cache: Whether to use cache for this request
            **kwargs: Additional arguments for httpx.get()

        Returns:
            Response JSON as dictionary

        Raises:
            httpx.HTTPError: If request fails after retries
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        cache_key = self._get_cache_key(url, params) if use_cache else None

        # Check cache first
        if cache_key and use_cache:
            cached = self._get_cached(cache_key)
            if cached is not None:
                return cached

        # Retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(
                    "http_request",
                    method="GET",
                    url=url,
                    attempt=attempt + 1,
                    max_retries=self.max_retries
                )

                response = await self._client.get(url, params=params, **kwargs)
                response.raise_for_status()

                data = response.json()

                # Cache successful response
                if cache_key and use_cache:
                    self._set_cache(cache_key, data)

                logger.info("http_success", method="GET", url=url, status=response.status_code)
                return data

            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code >= 500:  # Server error, retry
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(
                            "http_server_error",
                            status=e.response.status_code,
                            attempt=attempt + 1,
                            retry_after=wait_time
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error("http_max_retries", method="GET", url=url, status=e.response.status_code)
                else:  # Client error, don't retry
                    logger.error("http_client_error", method="GET", url=url, status=e.response.status_code)
                    raise

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(
                        "http_connection_error",
                        error=str(e),
                        attempt=attempt + 1,
                        retry_after=wait_time
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("http_connection_failed", method="GET", url=url, error=str(e))

        # All retries exhausted
        if last_error:
            raise last_error
        raise RuntimeError("HTTP request failed after all retries")

    async def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make POST request with retry logic.

        Args:
            url: Request URL (relative to base_url)
            json: JSON body data
            **kwargs: Additional arguments for httpx.post()

        Returns:
            Response JSON as dictionary

        Raises:
            httpx.HTTPError: If request fails after retries
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(
                    "http_request",
                    method="POST",
                    url=url,
                    attempt=attempt + 1,
                    max_retries=self.max_retries
                )

                response = await self._client.post(url, json=json, **kwargs)
                response.raise_for_status()

                logger.info("http_success", method="POST", url=url, status=response.status_code)
                return response.json()

            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code >= 500 and attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(
                        "http_server_error",
                        status=e.response.status_code,
                        attempt=attempt + 1,
                        retry_after=wait_time
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("http_error", method="POST", url=url, status=e.response.status_code)
                    raise

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(
                        "http_connection_error",
                        error=str(e),
                        attempt=attempt + 1,
                        retry_after=wait_time
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("http_connection_failed", method="POST", url=url, error=str(e))

        if last_error:
            raise last_error
        raise RuntimeError("HTTP request failed after all retries")

    def clear_cache(self) -> None:
        """Clear all cached responses."""
        cache_size = len(self._cache)
        self._cache.clear()
        logger.info("cache_cleared", items=cache_size)

    def __str__(self) -> str:
        """String representation of HTTP client."""
        cache_size = len(self._cache)
        return f"CachedHttpClient(base_url={self.base_url}, cache_entries={cache_size})"

    def __repr__(self) -> str:
        """Repr representation of HTTP client."""
        return (
            f"CachedHttpClient("
            f"base_url={self.base_url!r}, "
            f"cache_ttl={self.cache_ttl_seconds}s, "
            f"max_retries={self.max_retries}, "
            f"timeout={self.timeout_seconds}s"
            f")"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert client state to dictionary for JSON serialization."""
        return {
            "base_url": self.base_url,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "cache_size": len(self._cache),
        }

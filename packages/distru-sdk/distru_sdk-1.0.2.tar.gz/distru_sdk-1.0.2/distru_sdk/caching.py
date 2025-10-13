"""Caching layer for Distru SDK.

Provides configurable caching for API responses to reduce network calls.
"""

import hashlib
import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for no expiry)
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete key from cache.

        Args:
            key: Cache key
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass


class InMemoryCache(CacheBackend):
    """Simple in-memory cache implementation.

    This cache stores data in a Python dictionary and is not thread-safe.
    For production use with multiple threads, consider using a thread-safe
    implementation or external cache like Redis.

    Example:
        >>> cache = InMemoryCache(default_ttl=300)
        >>> cache.set("key", {"data": "value"})
        >>> cache.get("key")
        {'data': 'value'}
    """

    def __init__(self, default_ttl: Optional[int] = None, max_size: int = 1000) -> None:
        """Initialize in-memory cache.

        Args:
            default_ttl: Default time-to-live in seconds (None for no expiry)
            max_size: Maximum number of items to store (oldest items evicted first)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._access_order: list = []

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Check if expired
        if entry["expires_at"] is not None and time.time() > entry["expires_at"]:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            return None

        # Update access order for LRU
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        # Evict oldest item if at max size
        if len(self._cache) >= self._max_size and key not in self._cache:
            if self._access_order:
                oldest_key = self._access_order.pop(0)
                if oldest_key in self._cache:
                    del self._cache[oldest_key]

        ttl = ttl if ttl is not None else self._default_ttl
        expires_at = time.time() + ttl if ttl is not None else None

        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
        }

        # Update access order
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

    def delete(self, key: str) -> None:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_order:
            self._access_order.remove(key)

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_order.clear()


class ResponseCache:
    """HTTP response caching for API clients.

    Automatically caches GET requests based on URL and parameters.

    Example:
        >>> cache = ResponseCache(backend=InMemoryCache(default_ttl=300))
        >>> cache.get("GET", "/products", {"page": 1})
        None
        >>> cache.set("GET", "/products", {"page": 1}, {"data": [...]})
        >>> cache.get("GET", "/products", {"page": 1})
        {'data': [...]}
    """

    def __init__(
        self,
        backend: Optional[CacheBackend] = None,
        cache_methods: tuple = ("GET",),
    ) -> None:
        """Initialize response cache.

        Args:
            backend: Cache backend to use (defaults to InMemoryCache)
            cache_methods: HTTP methods to cache (default: GET only)
        """
        self.backend = backend or InMemoryCache(default_ttl=300)
        self.cache_methods = cache_methods

    def _make_key(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create cache key from request parameters.

        Args:
            method: HTTP method
            path: Request path
            params: Query parameters

        Returns:
            Cache key string
        """
        # Sort params for consistent keys
        params_str = json.dumps(params or {}, sort_keys=True)
        key_data = f"{method}:{path}:{params_str}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def should_cache(self, method: str) -> bool:
        """Check if method should be cached.

        Args:
            method: HTTP method

        Returns:
            True if method should be cached
        """
        return method.upper() in self.cache_methods

    def get(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """Get cached response.

        Args:
            method: HTTP method
            path: Request path
            params: Query parameters

        Returns:
            Cached response data or None
        """
        if not self.should_cache(method):
            return None

        key = self._make_key(method, path, params)
        return self.backend.get(key)

    def set(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]],
        response_data: Any,
        ttl: Optional[int] = None,
    ) -> None:
        """Set cached response.

        Args:
            method: HTTP method
            path: Request path
            params: Query parameters
            response_data: Response data to cache
            ttl: Time to live in seconds
        """
        if not self.should_cache(method):
            return

        key = self._make_key(method, path, params)
        self.backend.set(key, response_data, ttl)

    def clear(self) -> None:
        """Clear all cached responses."""
        self.backend.clear()

    def invalidate_path(self, path: str) -> None:
        """Invalidate all cached responses for a path.

        Note: This is a simplified implementation. For production use,
        consider using a backend that supports pattern-based deletion.

        Args:
            path: Path to invalidate
        """
        # For in-memory cache, we'd need to track keys by path
        # This is a simplified version that just clears everything
        # A production implementation would be more sophisticated
        self.clear()

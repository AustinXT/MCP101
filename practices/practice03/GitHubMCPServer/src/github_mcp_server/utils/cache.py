"""Simple optional in-memory cache utilities.

This module provides a lightweight, process-local cache with TTL support.
It's optional: tools may choose to use it, but the server works fine without it.
"""

import time
from typing import Any, Optional


class CacheEntry:
    """Internal cache entry holding value and expiry timestamp."""

    __slots__ = ("value", "expires_at")

    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.expires_at = time.time() + max(0, ttl_seconds)

    def is_expired(self) -> bool:
        return time.time() >= self.expires_at


_CACHE: dict[str, CacheEntry] = {}


def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache if present and not expired."""
    entry = _CACHE.get(key)
    if not entry:
        return None
    if entry.is_expired():
        # Remove expired entry
        _CACHE.pop(key, None)
        return None
    return entry.value


def cache_set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    """Set a value in cache with TTL (default 5 minutes)."""
    _CACHE[key] = CacheEntry(value, ttl_seconds)


def cache_clear(prefix: Optional[str] = None) -> int:
    """Clear cache entries.

    If prefix is provided, clears keys starting with the prefix.
    Returns the number of entries removed.
    """
    if not _CACHE:
        return 0
    if prefix is None:
        removed = len(_CACHE)
        _CACHE.clear()
        return removed

    keys = [k for k in _CACHE.keys() if k.startswith(prefix)]
    for k in keys:
        _CACHE.pop(k, None)
    return len(keys)
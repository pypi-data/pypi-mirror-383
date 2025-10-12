"""
Utility functions for caching and retry logic.

Implements TTL caching with stale-while-revalidate support.
"""

import asyncio
import time
from typing import Any, Dict, Optional

from .types import CacheOptions, Resolver


class TTL:
    """Pre-defined TTL constants for convenience (in seconds)."""

    short = 30  # 30 seconds
    minute = 60  # 1 minute
    minutes5 = 5 * 60  # 5 minutes
    minutes15 = 15 * 60  # 15 minutes
    hour = 60 * 60  # 1 hour
    hours6 = 6 * 60 * 60  # 6 hours
    day = 24 * 60 * 60  # 24 hours


class CachedResolver:
    """
    Wrapper that caches resolver results with TTL and stale-while-revalidate support.

    This implements the same caching strategy as the TypeScript version:
    - Age < TTL: Return cached data (fresh)
    - TTL ≤ Age ≤ max_age: Stale-while-revalidate or force refresh
    - Age > max_age: Always force refresh
    """

    def __init__(self, resolver: Resolver, options: CacheOptions):
        self._resolver = resolver
        self._options = options
        self.name = f"cached({resolver.name})"
        self.metadata: Dict[str, Any] = {}

        # Cache state
        self._cache: Optional[Dict[str, Any]] = None
        self._refresh_task: Optional[asyncio.Task] = None

    async def load(self) -> Dict[str, str]:
        """Load with caching logic."""
        now = time.time()

        # Convert to seconds (supports timedelta)
        ttl_seconds = self._options.get_ttl_seconds()
        max_age_seconds = self._options.get_max_age_seconds()

        # If no cache or cache is expired beyond maxAge, force refresh
        if self._cache is None or (now - self._cache["timestamp"]) > max_age_seconds:
            data = await self._resolver.load()
            data_dict = dict(data)  # Convert Mapping to dict
            self._cache = {"data": data_dict, "timestamp": now}
            self.metadata = {"cached": False}
            return data_dict

        # If cache is within TTL, return cached data (fresh)
        age = now - self._cache["timestamp"]
        if age < ttl_seconds:
            self.metadata = {"cached": True}
            cached_data: dict[str, str] = self._cache["data"]
            return cached_data

        # Cache is stale (between TTL and maxAge)
        # If stale-while-revalidate is enabled, serve stale data while refreshing in background
        if self._options.stale_while_revalidate:
            # Trigger a refresh if one isn't already running, but always serve stale data.
            if self._refresh_task is None or self._refresh_task.done():
                async def background_refresh() -> None:
                    try:
                        data = await self._resolver.load()
                        if self._cache is not None:
                            self._cache["data"] = data
                            self._cache["timestamp"] = time.time()
                    except Exception:
                        # Keep serving stale data if refresh fails.
                        pass
                    finally:
                        self._refresh_task = None

                self._refresh_task = asyncio.create_task(background_refresh())

            self.metadata = {
                "cached": True,
                "stale": True,
                "refresh_in_flight": self._refresh_task is not None
            }
            stale_data: dict[str, str] = self._cache["data"]
            return stale_data

        # Cache is stale and no stale-while-revalidate, force refresh
        data = await self._resolver.load()
        data_dict = dict(data)  # Convert Mapping to dict
        self._cache = {"data": data_dict, "timestamp": now}
        self.metadata = {"cached": False}
        return data_dict


def cached(
    resolver: Resolver,
    options: Optional[CacheOptions] = None
) -> CachedResolver:
    """
    Wrap a resolver with TTL caching.

    Args:
        resolver: The resolver to cache
        options: Cache configuration options

    Returns:
        Cached resolver wrapper

    Example:
        >>> from python_env_resolver import cached, TTL
        >>>
        >>> resolver = cached(
        ...     your_custom_resolver,
        ...     CacheOptions(ttl=TTL.minutes5, stale_while_revalidate=True)
        ... )
    """
    if options is None:
        options = CacheOptions()

    return CachedResolver(resolver, options)



"""Fixtures for cache testing."""

import os
from collections.abc import AsyncGenerator, Generator
from unittest.mock import patch

import pytest
import pytest_asyncio
from ab_core.cache.caches import Cache
from ab_core.cache.caches.base import CacheAsyncSession, CacheSession
from ab_core.cache.session_context import cache_session_async_cm, cache_session_sync_cm
from ab_core.dependency import Load


@pytest.fixture
def tmp_cache_sync() -> Generator[Cache, None, None]:
    """Yield a temporary in-memory cache instance for testing."""
    with patch.dict(
        os.environ,
        {
            "CACHE_TYPE": "INMEMORY",
        },
        clear=False,
    ):
        cache: Cache = Load(Cache)
        yield cache


@pytest_asyncio.fixture
async def tmp_cache_async() -> AsyncGenerator[Cache, None]:
    """Yield a temporary in-memory cache instance for testing."""
    with patch.dict(
        os.environ,
        {
            "CACHE_TYPE": "INMEMORY",
        },
        clear=False,
    ):
        cache: Cache = Load(Cache)
        yield cache


@pytest.fixture
def tmp_cache_sync_session(tmp_cache_sync: Cache) -> Generator[CacheSession, None, None]:
    """Yield a synchronous cache session for testing."""
    with cache_session_sync_cm(tmp_cache_sync) as session:
        yield session


@pytest_asyncio.fixture
async def tmp_cache_async_session(
    tmp_cache_async: Cache,
) -> AsyncGenerator[CacheAsyncSession, None]:
    """Yield an asynchronous cache session for testing."""
    async with cache_session_async_cm(tmp_cache_async) as session:
        yield session

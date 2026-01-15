"""Redis connection management."""

from collections.abc import AsyncGenerator
from typing import cast

import redis.asyncio as aioredis

from app.config import get_settings

settings = get_settings()

redis_client = cast(
    aioredis.Redis,
    aioredis.from_url(  # type: ignore[no-untyped-call]
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    ),
)


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """Dependency that provides a Redis client."""
    try:
        yield redis_client
    finally:
        pass  # Connection pooling handles cleanup

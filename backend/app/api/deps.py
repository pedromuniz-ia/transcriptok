"""API dependencies for dependency injection."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.core.database import get_db
from app.core.redis import get_redis
from app.config import get_settings

settings = get_settings()

# Type aliases for cleaner dependency injection
DbSession = Annotated[AsyncSession, Depends(get_db)]
RedisClient = Annotated[aioredis.Redis, Depends(get_redis)]


async def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    # Check for forwarded IP (behind proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


ClientIP = Annotated[str, Depends(get_client_ip)]


class RateLimiter:
    """Rate limiting dependency."""

    def __init__(self, key_prefix: str, limit: int, window_seconds: int = 3600):
        self.key_prefix = key_prefix
        self.limit = limit
        self.window_seconds = window_seconds

    async def __call__(
        self,
        request: Request,
        redis: RedisClient,
        client_ip: ClientIP,
    ) -> None:
        """Check rate limit for the client."""
        key = f"rate_limit:{self.key_prefix}:{client_ip}"

        # Get current count
        current = await redis.get(key)
        if current is None:
            # First request in window
            await redis.setex(key, self.window_seconds, 1)
        elif int(current) >= self.limit:
            # Rate limit exceeded
            ttl = await redis.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": self.limit,
                    "window_seconds": self.window_seconds,
                    "retry_after": ttl,
                },
            )
        else:
            # Increment counter
            await redis.incr(key)


# Pre-configured rate limiters
download_rate_limit = RateLimiter("download", limit=5, window_seconds=3600)
transcript_rate_limit = RateLimiter("transcript", limit=10, window_seconds=3600)
ai_tool_rate_limit = RateLimiter("ai_tool", limit=20, window_seconds=3600)

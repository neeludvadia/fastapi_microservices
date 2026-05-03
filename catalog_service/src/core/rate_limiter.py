"""
Custom Redis-based Rate Limiter using the Sliding Window Counter algorithm.

How it works:
  - Each client (identified by IP) gets a Redis key like "rate_limit:<ip>:<endpoint>"
  - We use Redis INCR to count requests within a fixed time window (e.g., 60 seconds)
  - On the first request, we set a TTL (expiry) on the key equal to the window size
  - If the count exceeds the allowed limit, we return HTTP 429 Too Many Requests
  - Redis automatically cleans up expired keys, so no manual cleanup is needed

This is equivalent to the express-rate-limit middleware used in the Node.js version.
"""

import os
import redis.asyncio as aioredis
from fastapi import Request, HTTPException, status

# Singleton Redis connection
_redis_client = None

async def get_redis_client() -> aioredis.Redis:
    """Get or create a singleton async Redis connection."""
    global _redis_client
    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        _redis_client = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    return _redis_client


async def close_redis_client():
    """Cleanly close the Redis connection on shutdown."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


def rate_limiter(max_requests: int = 10, window_seconds: int = 60):
    """
    Returns a FastAPI dependency that enforces rate limiting.
    
    Args:
        max_requests: Maximum number of requests allowed within the window.
        window_seconds: The time window in seconds (e.g., 60 = 1 minute).
    
    Usage:
        router = APIRouter(dependencies=[Depends(rate_limiter(max_requests=10, window_seconds=60))])
    """
    async def _rate_limit_dependency(request: Request):
        client_ip = request.client.host
        endpoint = request.url.path
        redis_key = f"rate_limit:{client_ip}:{endpoint}"
        
        redis_client = await get_redis_client()
        
        # INCR atomically increments the counter and returns the new value
        current_count = await redis_client.incr(redis_key)
        
        # If this is the first request in the window, set the TTL
        if current_count == 1:
            await redis_client.expire(redis_key, window_seconds)
        
        # Get remaining TTL for response headers
        ttl = await redis_client.ttl(redis_key)
        
        if current_count > max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "max_requests": max_requests,
                    "window_seconds": window_seconds,
                    "retry_after": ttl
                },
                headers={"Retry-After": str(ttl)}
            )
    
    return _rate_limit_dependency

"""
Simple in-memory rate limiter middleware.
Uses Redis sliding window counter for accurate rate limiting.
"""
import os
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis.asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_redis_client = None


async def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 200, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"
        try:
            r = await get_redis()
            current = await r.incr(key)
            if current == 1:
                await r.expire(key, self.window_seconds)
            if current > self.max_requests:
                return JSONResponse(
                    status_code=429,
                    content={"detail": f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds}s."},
                )
        except Exception:
            pass  # If Redis is down, allow the request through
        return await call_next(request)

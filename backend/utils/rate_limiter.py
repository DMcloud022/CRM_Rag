from fastapi import HTTPException
from functools import wraps
import time
import asyncio

def rate_limit(max_requests: int, interval: int = 60):
    def decorator(func):
        requests = []
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()
            requests.append(now)
            requests[:] = [r for r in requests if now - r < interval]
            if len(requests) > max_requests:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
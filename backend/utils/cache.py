from functools import wraps
import time

def cache(expire: int):
    def decorator(func):
        cache_dict = {}
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in cache_dict:
                result, timestamp = cache_dict[key]
                if time.time() - timestamp < expire:
                    return result
            result = await func(*args, **kwargs)
            cache_dict[key] = (result, time.time())
            return result
        return wrapper
    return decorator
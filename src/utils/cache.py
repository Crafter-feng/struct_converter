import functools
from typing import Callable, Any, Dict, TypeVar
from loguru import logger

logger = logger.bind(name="Cache")

T = TypeVar('T')

def cached(key_func: Callable[..., str]) -> Callable:
    """缓存装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache: Dict[str, T] = {}
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            key = key_func(*args, **kwargs)
            if key not in cache:
                cache[key] = func(*args, **kwargs)
                logger.debug(f"Cache miss for {func.__name__}[{key}]")
            else:
                logger.debug(f"Cache hit for {func.__name__}[{key}]")
            return cache[key]
        return wrapper
    return decorator 
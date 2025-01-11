from functools import wraps
from time import time
from typing import Any, Callable, TypeVar
from loguru import logger

T = TypeVar('T')

def log_execution(name: str = None):
    """记录函数执行的装饰器
    
    Args:
        name: 日志名称，默认使用函数名
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        log_name = name or func.__name__
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            start_time = time()
            try:
                result = func(*args, **kwargs)
                end_time = time()
                logger.debug(
                    f"{log_name} completed in {end_time - start_time:.3f}s"
                )
                return result
            except Exception as e:
                logger.error(f"{log_name} failed: {e}")
                raise
        return wrapper
    return decorator

def cache_result(cache_key_fn: Callable[..., str]):
    """缓存函数结果的装饰器
    
    Args:
        cache_key_fn: 生成缓存键的函数
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache = {}
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            key = cache_key_fn(*args, **kwargs)
            if key not in cache:
                logger.debug(f"Cache miss for {func.__name__}[{key}]")
                cache[key] = func(*args, **kwargs)
            else:
                logger.debug(f"Cache hit for {func.__name__}[{key}]")
            return cache[key]
        return wrapper
    return decorator 
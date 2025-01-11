import logging
import functools
import time
from typing import Any, Callable, TypeVar

T = TypeVar('T')

def log_execution(logger: logging.Logger) -> Callable:
    """记录函数执行的装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                logger.debug(
                    f"{func.__name__} completed in {end_time - start_time:.3f}s"
                )
                return result
            except Exception as e:
                logger.error(f"{func.__name__} failed: {e}")
                raise
        return wrapper
    return decorator 
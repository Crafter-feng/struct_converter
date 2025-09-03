import functools
import time
from typing import Callable, Any
from loguru import logger

__all__ = ['logger']


def log_execution(func: Callable) -> Callable:
    """记录函数执行日志的装饰器"""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
    return wrapper 

logger.add("logs/debug.log", level="ERROR", mode='w')
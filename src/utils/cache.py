import threading
from typing import Any, Callable, Dict, TypeVar
from functools import wraps

T = TypeVar('T')

class ThreadSafeCache:
    """线程安全的缓存"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._lock = threading.Lock()
        
    def get(self, key: str) -> Any:
        """获取缓存值"""
        with self._lock:
            return self._cache.get(key)
            
    def set(self, key: str, value: Any) -> None:
        """设置缓存值"""
        with self._lock:
            self._cache[key] = value
            
    def clear(self) -> None:
        """清除缓存"""
        with self._lock:
            self._cache.clear()

def cached(cache_key_fn: Callable[..., str]) -> Callable:
    """缓存装饰器
    
    Args:
        cache_key_fn: 生成缓存键的函数
    """
    cache = ThreadSafeCache()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            key = cache_key_fn(*args, **kwargs)
            result = cache.get(key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(key, result)
            return result
        return wrapper
    return decorator 
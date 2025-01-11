import time
import functools
from typing import Callable, Any
from utils.logger_config import setup_logger
from contextlib import contextmanager
import inspect

logger = setup_logger('Profiler')

class Profiler:
    """性能分析器"""
    
    def __init__(self):
        self.stats = {}
        
    def profile(self, func: Callable) -> Callable:
        """性能分析装饰器"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                duration = end_time - start_time
                
                func_name = func.__name__
                if func_name not in self.stats:
                    self.stats[func_name] = {
                        'calls': 0,
                        'total_time': 0,
                        'min_time': float('inf'),
                        'max_time': 0
                    }
                    
                stats = self.stats[func_name]
                stats['calls'] += 1
                stats['total_time'] += duration
                stats['min_time'] = min(stats['min_time'], duration)
                stats['max_time'] = max(stats['max_time'], duration)
                
        return wrapper
        
    def print_stats(self) -> None:
        """打印性能统计信息"""
        logger.info("Performance Statistics:")
        for func_name, stats in self.stats.items():
            avg_time = stats['total_time'] / stats['calls']
            logger.info(f"{func_name}:")
            logger.info(f"  Calls: {stats['calls']}")
            logger.info(f"  Total Time: {stats['total_time']:.6f}s")
            logger.info(f"  Average Time: {avg_time:.6f}s")
            logger.info(f"  Min Time: {stats['min_time']:.6f}s")
            logger.info(f"  Max Time: {stats['max_time']:.6f}s") 
        
    @contextmanager
    def profile_if(self, enabled: bool):
        """条件性能分析上下文管理器"""
        if not enabled:
            yield
            return
            
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            func_name = 'unknown'
            for frame in inspect.stack()[1:]:
                if frame.function != 'profile_if':
                    func_name = frame.function
                    break
                    
            if func_name not in self.stats:
                self.stats[func_name] = {
                    'calls': 0,
                    'total_time': 0,
                    'min_time': float('inf'),
                    'max_time': 0
                }
                
            stats = self.stats[func_name]
            stats['calls'] += 1
            stats['total_time'] += duration
            stats['min_time'] = min(stats['min_time'], duration)
            stats['max_time'] = max(stats['max_time'], duration) 
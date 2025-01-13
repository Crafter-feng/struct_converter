import time
import functools
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
from loguru import logger

logger = logger.bind(name="Profiler")

class Profiler:
    """性能分析器"""
    
    def __init__(self):
        self.logger = logger
        self.stats: Dict[str, Dict[str, float]] = {}
        self.start_time: Optional[float] = None
        self.enabled: bool = True
        
    def start(self) -> None:
        """开始性能分析"""
        self.start_time = time.time()
        self.stats.clear()
        
    def stop(self) -> Dict[str, Dict[str, float]]:
        """停止性能分析并返回统计信息"""
        if self.start_time is None:
            raise RuntimeError("Profiler not started")
            
        total_time = time.time() - self.start_time
        self.stats['total'] = {
            'duration': total_time,
            'calls': 1
        }
        return self.stats
        
    def profile(self, func: Callable) -> Callable:
        """性能分析装饰器"""
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not self.enabled:
                return func(*args, **kwargs)
                
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start
                name = func.__qualname__
                
                if name not in self.stats:
                    self.stats[name] = {
                        'duration': 0.0,
                        'calls': 0,
                        'min_time': float('inf'),
                        'max_time': 0.0
                    }
                    
                stats = self.stats[name]
                stats['duration'] += duration
                stats['calls'] += 1
                stats['min_time'] = min(stats['min_time'], duration)
                stats['max_time'] = max(stats['max_time'], duration)
                
        return wrapper
        
    @contextmanager
    def profile_block(self, name: str):
        """性能分析代码块"""
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            if name not in self.stats:
                self.stats[name] = {
                    'duration': 0.0,
                    'calls': 0
                }
            self.stats[name]['duration'] += duration
            self.stats[name]['calls'] += 1
            
    def print_stats(self) -> None:
        """打印性能统计信息"""
        if not self.stats:
            self.logger.warning("No profiling data available")
            return
            
        self.logger.info("Performance Statistics:")
        for name, data in self.stats.items():
            if name == 'total':
                continue
                
            calls = data['calls']
            total = data['duration']
            avg = total / calls if calls else 0
            
            self.logger.info(f"\n{name}:")
            self.logger.info(f"  Calls: {calls}")
            self.logger.info(f"  Total Time: {total:.6f}s")
            self.logger.info(f"  Average Time: {avg:.6f}s")
            
            if 'min_time' in data:
                self.logger.info(f"  Min Time: {data['min_time']:.6f}s")
                self.logger.info(f"  Max Time: {data['max_time']:.6f}s") 
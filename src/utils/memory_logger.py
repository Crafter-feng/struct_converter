import os
import psutil
import threading
from typing import Dict, Any
from datetime import datetime
from loguru import logger

logger = logger.bind(name="MemoryLogger")

class MemoryLogger:
    """内存使用监控器"""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.enabled = False
        self.process = psutil.Process(os.getpid())
        self.stats: Dict[str, Any] = {}
        self._monitor_thread = None
        self.logger = logger
        
    def start(self) -> None:
        """开始监控内存使用"""
        if self.enabled:
            return
            
        self.enabled = True
        self.stats.clear()
        self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self._monitor_thread.start()
        self.logger.info("Memory monitoring started")
        
    def stop(self) -> Dict[str, Any]:
        """停止监控并返回统计信息"""
        if not self.enabled:
            return self.stats
            
        self.enabled = False
        if self._monitor_thread:
            self._monitor_thread.join()
            self._monitor_thread = None
            
        self.logger.info("Memory monitoring stopped")
        return self.stats
        
    def _monitor(self) -> None:
        """监控线程的主循环"""
        start_time = datetime.now()
        peak_memory = 0
        
        while self.enabled:
            try:
                memory_info = self.process.memory_info()
                current_memory = memory_info.rss / 1024 / 1024  # MB
                peak_memory = max(peak_memory, current_memory)
                
                self.stats.update({
                    'current_memory_mb': current_memory,
                    'peak_memory_mb': peak_memory,
                    'virtual_memory_mb': memory_info.vms / 1024 / 1024,
                    'duration': (datetime.now() - start_time).total_seconds()
                })
                
                if current_memory > peak_memory * 0.9:  # 内存使用接近峰值
                    self.logger.warning(
                        f"High memory usage: {current_memory:.2f}MB "
                        f"(Peak: {peak_memory:.2f}MB)"
                    )
                    
            except Exception as e:
                self.logger.error(f"Memory monitoring error: {e}")
                
            threading.Event().wait(self.interval)
            
    def print_stats(self) -> None:
        """打印内存统计信息"""
        if not self.stats:
            self.logger.warning("No memory statistics available")
            return
            
        self.logger.info("\nMemory Statistics:")
        self.logger.info(f"Current Memory: {self.stats['current_memory_mb']:.2f}MB")
        self.logger.info(f"Peak Memory: {self.stats['peak_memory_mb']:.2f}MB")
        self.logger.info(f"Virtual Memory: {self.stats['virtual_memory_mb']:.2f}MB")
        self.logger.info(f"Duration: {self.stats['duration']:.2f}s") 
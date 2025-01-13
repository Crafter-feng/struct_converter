from typing import Dict, Any, Optional
import yaml
from pathlib import Path
from loguru import logger
from .base_config import BaseConfig

logger = logger.bind(name="LoggingConfig")

class LoggingConfig(BaseConfig):
    """日志配置"""
    
    def __init__(self, config_file: Optional[str] = None):
        super().__init__(config_file)
        self.log_level: str = "INFO"
        self.log_file: Optional[str] = None
        self.format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name: <15} | {message}"
        self.rotation: str = "1 day"
        self.retention: str = "7 days"
        self.compression: str = "zip"
        self.backtrace: bool = True
        self.diagnose: bool = True
        self.enqueue: bool = True
        self.logger = logger
        
    def _validate_config(self) -> None:
        """验证日志配置"""
        if 'log_level' in self.config_data:
            level = self.config_data['log_level'].upper()
            if level not in {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}:
                raise ValueError(f"Invalid log level: {level}")
                
    def _process_config(self) -> None:
        """处理日志配置"""
        self.log_level = self.config_data.get('log_level', self.log_level).upper()
        self.log_file = self.config_data.get('log_file', self.log_file)
        self.format = self.config_data.get('format', self.format)
        self.rotation = self.config_data.get('rotation', self.rotation)
        self.retention = self.config_data.get('retention', self.retention)
        self.compression = self.config_data.get('compression', self.compression)
        self.backtrace = self.config_data.get('backtrace', self.backtrace)
        self.diagnose = self.config_data.get('diagnose', self.diagnose)
        self.enqueue = self.config_data.get('enqueue', self.enqueue) 
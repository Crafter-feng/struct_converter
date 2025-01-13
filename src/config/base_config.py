from typing import Dict, Any, Optional
import yaml
from pathlib import Path
from loguru import logger

logger = logger.bind(name="Config")

class BaseConfig:
    """配置基类"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logger
        self.config_data = {}
        if config_file:
            self.load(config_file)
            
    def load(self, config_file: str) -> None:
        """从YAML文件加载配置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f) or {}
            self._validate_config()
            self._process_config()
        except Exception as e:
            logger.error(f"Failed to load config from {config_file}: {e}")
            raise
            
    def save(self, config_file: str) -> None:
        """保存配置到YAML文件"""
        try:
            config_path = Path(config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.to_dict(), f, allow_unicode=True)
        except Exception as e:
            logger.error(f"Failed to save config to {config_file}: {e}")
            raise
            
    def _validate_config(self) -> None:
        """验证配置有效性"""
        pass
        
    def _process_config(self) -> None:
        """处理配置数据"""
        pass
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.config_data.copy() 
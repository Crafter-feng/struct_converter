from typing import Dict, Any, Type, TypeVar
from pathlib import Path
import yaml
from .base_config import BaseConfig

T = TypeVar('T', bound=BaseConfig)

class ConfigLoader:
    """配置加载器"""
    
    @staticmethod
    def load(config_class: Type[T], file_path: str) -> T:
        """加载配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return config_class(data)
        except Exception as e:
            raise ValueError(f"Failed to load config from {file_path}: {e}")
            
    @staticmethod
    def load_all(config_dir: str) -> Dict[str, BaseConfig]:
        """加载目录下的所有配置"""
        configs = {}
        config_path = Path(config_dir)
        
        if not config_path.exists():
            return configs
            
        for yaml_file in config_path.glob('*.yaml'):
            name = yaml_file.stem
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                configs[name] = BaseConfig(data)
            except Exception as e:
                logger.warning(f"Failed to load config {yaml_file}: {e}")
                
        return configs 
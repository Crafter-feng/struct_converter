from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
from .exceptions import ValidationError
from utils.logger_config import get_logger
from .encryption_config import EncryptionConfig

logger = get_logger("Config")

@dataclass
class GeneratorConfig:
    """代码生成器配置"""
    
    # 输出目录
    output_dir: str = "generated"
    
    # 加密配置
    encryption: Optional[EncryptionConfig] = None
    
    # 是否生成序列化代码
    enable_serialization: bool = True
    
    # 是否生成版本控制
    enable_version_control: bool = True
    
    # 是否生成文档注释
    enable_doc_comments: bool = True
    
    # 是否生成类型检查
    enable_type_checking: bool = True
    
    # 是否生成调试信息
    enable_debug_info: bool = False
    
    # 是否生成性能分析代码
    enable_profiling: bool = False
    
    # 字节序设置 ('native', 'little', 'big')
    byte_order: str = 'native'
    
    # 指针大小 (4 或 8)
    pointer_size: int = 8
    
    # 默认对齐方式
    default_alignment: int = 4
    
    # 是否启用字段加密
    enable_field_encryption: bool = False
    
    # 字段加密盐值
    field_encryption_salt: str = "struct_converter"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneratorConfig':
        """从字典创建配置"""
        try:
            return cls(**data)
        except Exception as e:
            raise ValidationError(f"Invalid config data: {e}")
            
    @classmethod
    def load(cls, config_file: str) -> 'GeneratorConfig':
        """从文件加载配置"""
        with open(config_file) as f:
            data = json.load(f)
            
        # 处理加密配置
        if "encryption" in data:
            data["encryption"] = EncryptionConfig.from_dict(data["encryption"])
            
        return cls(**data)
            
    def save(self, config_file: str) -> None:
        """保存配置到文件"""
        data = self.__dict__.copy()
        
        # 处理加密配置
        if self.encryption:
            data["encryption"] = self.encryption.__dict__
            
        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2) 
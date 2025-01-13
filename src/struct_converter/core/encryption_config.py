from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
import json
from pathlib import Path

@dataclass
class EncryptionConfig:
    """加密配置"""
    
    # 是否启用加密
    enable: bool = False
    
    # 加密盐值
    salt: str = "struct_converter"
    
    # 是否加密所有字段
    encrypt_all: bool = False
    
    # 需要加密的字段列表 (struct_name -> [field_names])
    encrypted_fields: Dict[str, List[str]] = None
    
    # 不需要加密的字段列表
    excluded_fields: Optional[Dict[str, List[str]]] = None
    
    # 是否在注释中保留原始名称
    keep_original_names: bool = True
    
    # 是否生成字段映射文件
    generate_map_file: bool = True
    
    # 加密密钥
    encryption_key: Optional[str] = None
    
    # 加密方法
    encryption_method: Optional[str] = None
    
    # 字段前缀
    field_prefix: Optional[str] = None
    
    # 字段后缀
    field_suffix: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EncryptionConfig':
        return cls(**data)
        
    @classmethod
    def load(cls, config_file: Path) -> 'EncryptionConfig':
        """从文件加载配置"""
        if not config_file.exists():
            return cls()
            
        with open(config_file) as f:
            data = json.load(f)
        return cls.from_dict(data)
        
    def save(self, config_file: Path) -> None:
        """保存配置到文件"""
        with open(config_file, 'w') as f:
            json.dump(self.__dict__, f, indent=2)
            
    def should_encrypt_field(self, struct_name: str, field_name: str) -> bool:
        """判断是否需要加密字段"""
        if not self.enable:
            return False
            
        # 检查排除列表
        if self.excluded_fields and struct_name in self.excluded_fields:
            if field_name in self.excluded_fields[struct_name]:
                return False
                
        # 检查加密列表
        if self.encrypt_all:
            return True
            
        if self.encrypted_fields and struct_name in self.encrypted_fields:
            return field_name in self.encrypted_fields[struct_name]
            
        return False 
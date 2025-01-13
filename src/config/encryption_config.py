from typing import Dict, Any, List, Optional
from .base_config import BaseConfig

class EncryptionConfig(BaseConfig):
    """字段加密配置"""
    
    def __init__(self, config_file: Optional[str] = None):
        super().__init__(config_file)
        self.enable: bool = False
        self.salt: str = "default_salt"
        self.encrypt_all: bool = False
        self.encrypted_fields: Dict[str, List[str]] = {}
        self.excluded_fields: Dict[str, List[str]] = {}
        
    def _validate_config(self) -> None:
        """验证加密配置"""
        if self.config_data.get('enable', False):
            if 'salt' not in self.config_data:
                raise ValueError("Missing encryption salt")
                
    def _process_config(self) -> None:
        """处理加密配置"""
        self.enable = self.config_data.get('enable', False)
        self.salt = self.config_data.get('salt', 'default_salt')
        self.encrypt_all = self.config_data.get('encrypt_all', False)
        self.encrypted_fields = self.config_data.get('encrypted_fields', {})
        self.excluded_fields = self.config_data.get('excluded_fields', {})
        
    def should_encrypt_field(self, struct_name: str, field_name: str) -> bool:
        """检查字段是否需要加密"""
        if not self.enable:
            return False
            
        if struct_name in self.excluded_fields:
            if field_name in self.excluded_fields[struct_name]:
                return False
                
        if self.encrypt_all:
            return True
            
        return (struct_name in self.encrypted_fields and 
                field_name in self.encrypted_fields[struct_name]) 
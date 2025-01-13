import re
from typing import Optional, Dict, Set
from loguru import logger
from .exceptions import ValidationError

logger = logger.bind(name="FieldValidator")

class FieldValidator:
    """字段验证器"""
    
    def __init__(self):
        self.logger = logger
        self.name_pattern = re.compile(r'^[A-Z][A-Z0-9]{3}$')
        self.used_names: Set[str] = set()
        self.struct_prefixes: Dict[str, str] = {}
        
    def validate_field_name(self, field_name: str, struct_name: str) -> None:
        """验证字段名称"""
        if not field_name:
            raise ValidationError(f"Empty field name in struct {struct_name}")
            
        if field_name.startswith('_'):
            raise ValidationError(
                f"Field name '{field_name}' in struct '{struct_name}' "
                "cannot start with underscore"
            )
            
        if not field_name.isidentifier():
            raise ValidationError(
                f"Invalid field name '{field_name}' in struct '{struct_name}'"
            )
            
    def validate_encrypted_name(self, name: str, struct_name: str) -> None:
        """验证加密后的字段名"""
        if not self.name_pattern.match(name):
            raise ValidationError(
                f"Invalid encrypted name '{name}' for struct '{struct_name}'"
            )
            
        if name in self.used_names:
            raise ValidationError(
                f"Duplicate encrypted name '{name}' in struct '{struct_name}'"
            )
            
        self.used_names.add(name)
        
    def validate_struct_prefix(self, prefix: str, struct_name: str) -> None:
        """验证结构体前缀"""
        if len(prefix) != 2 or not prefix.isalpha() or not prefix.isupper():
            raise ValidationError(
                f"Invalid struct prefix '{prefix}' for struct '{struct_name}'. "
                "Prefix must be 2 uppercase letters."
            )
            
        if prefix in self.struct_prefixes.values():
            existing = next(k for k, v in self.struct_prefixes.items() if v == prefix)
            raise ValidationError(
                f"Prefix '{prefix}' for struct '{struct_name}' conflicts with "
                f"existing struct '{existing}'"
            )
            
        self.struct_prefixes[struct_name] = prefix
        
    def reset(self) -> None:
        """重置验证器状态"""
        self.used_names.clear()
        self.struct_prefixes.clear() 
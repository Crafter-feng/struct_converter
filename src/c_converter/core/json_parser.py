import json
from typing import Dict, Any, Optional
from .field_encryptor import FieldEncryptor

class JsonParser:
    """JSON解析器，支持加密字段"""
    
    def __init__(self, encryptor: Optional[FieldEncryptor] = None):
        self.encryptor = encryptor
        self._name_cache: Dict[str, Dict[str, str]] = {}  # struct_name -> {encrypted: original}
        
    def _build_name_cache(self, struct_name: str) -> None:
        """构建字段名缓存"""
        if struct_name not in self._name_cache and self.encryptor:
            self._name_cache[struct_name] = {
                encrypted: original
                for encrypted, original in self.encryptor.field_comments.get(struct_name, {}).items()
            }
            
    def parse_json(self, json_str: str, struct_name: str, is_encrypted: bool = False) -> Dict[str, Any]:
        """解析JSON字符串
        
        Args:
            json_str: JSON字符串
            struct_name: 结构体名称
            is_encrypted: JSON中的字段名是否已加密
        """
        try:
            data = json.loads(json_str)
            if not isinstance(data, dict):
                raise ValueError("JSON must be an object")
                
            if is_encrypted and self.encryptor:
                self._build_name_cache(struct_name)
                name_map = self._name_cache.get(struct_name, {})
                
                # 使用字典推导式优化性能
                return {
                    name_map.get(k, k): v
                    for k, v in data.items()
                }
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
            
    def generate_json(self, data: Dict[str, Any], struct_name: str, encrypt: bool = False) -> str:
        """生成JSON字符串
        
        Args:
            data: 数据字典
            struct_name: 结构体名称
            encrypt: 是否加密字段名
        """
        if encrypt and self.encryptor:
            self._build_name_cache(struct_name)
            encrypted_fields = self.encryptor.encrypted_fields.get(struct_name, {})
            
            # 使用字典推导式优化性能
            data = {
                encrypted_fields.get(k, k): v
                for k, v in data.items()
            }
            
        return json.dumps(data, indent=2, ensure_ascii=False) 
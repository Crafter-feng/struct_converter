from typing import Set, Dict

class FieldValidator:
    """字段名验证器"""
    
    def __init__(self):
        self.used_names: Set[str] = set()
        self.struct_prefixes: Dict[str, str] = {}
        
    def validate_encrypted_name(self, encrypted_name: str) -> bool:
        """验证加密名称格式"""
        if len(encrypted_name) != 4:
            return False
            
        # 前两位应该是大写字母
        if not encrypted_name[:2].isalpha() or not encrypted_name[:2].isupper():
            return False
            
        # 后两位应该是base32字符（大写字母和数字2-7）
        valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567')
        if not all(c in valid_chars for c in encrypted_name[2:]):
            return False
            
        return True
        
    def check_name_conflict(self, encrypted_name: str) -> bool:
        """检查名称冲突"""
        if encrypted_name in self.used_names:
            return True
        self.used_names.add(encrypted_name)
        return False
        
    def validate_struct_prefix(self, struct_name: str, prefix: str) -> bool:
        """验证结构体前缀"""
        if prefix in self.struct_prefixes.values():
            return False
        self.struct_prefixes[struct_name] = prefix
        return True 
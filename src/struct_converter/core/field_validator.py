import re
import threading
from typing import Set, Dict

class FieldValidator:
    """字段名验证器"""
    
    def __init__(self):
        self.used_names: Set[str] = set()
        self.struct_prefixes: Dict[str, str] = {}
        self._lock = threading.Lock()  # 用于线程安全
        
    def validate_encrypted_name(self, name: str) -> bool:
        """验证加密名称格式
        
        规则:
        1. 长度必须是4字节
        2. 前两位必须是大写字母
        3. 后两位必须是base32字符（大写字母和数字2-7）
        """
        try:
            if not isinstance(name, str):
                return False
                
            if len(name) != 4:
                return False
                
            # 前两位必须是大写字母
            if not name[:2].isalpha() or not name[:2].isupper():
                return False
                
            # 后两位必须是base32字符
            valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567')
            if not all(c in valid_chars for c in name[2:]):
                return False
                
            return True
            
        except Exception:
            return False
            
    def check_name_conflict(self, encrypted_name: str) -> bool:
        """检查名称冲突
        
        返回:
            bool: True表示有冲突，False表示无冲突
        """
        with self._lock:
            if encrypted_name in self.used_names:
                return True
            self.used_names.add(encrypted_name)
            return False
            
    def validate_struct_prefix(self, struct_name: str, prefix: str) -> bool:
        """验证结构体前缀
        
        规则:
        1. 前缀必须是2个大写字母
        2. 不同结构体不能使用相同前缀
        """
        try:
            if not isinstance(prefix, str):
                return False
                
            # 检查前缀格式
            if len(prefix) != 2:
                return False
                
            if not prefix.isalpha() or not prefix.isupper():
                return False
                
            # 检查前缀冲突
            with self._lock:
                if prefix in self.struct_prefixes.values():
                    return False
                self.struct_prefixes[struct_name] = prefix
                return True
                
        except Exception:
            return False
            
    def reset(self) -> None:
        """重置验证器状态"""
        with self._lock:
            self.used_names.clear()
            self.struct_prefixes.clear() 
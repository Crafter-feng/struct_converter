from typing import Dict, Any, Optional, List
from loguru import logger

class TypeManager:
    """C语言类型管理器"""
    
    def __init__(self):
        self.logger = logger.bind(component="TypeManager")
        self.type_map: Dict[str, str] = {
            # 基本类型映射
            'char': 'int8_t',
            'unsigned char': 'uint8_t',
            'short': 'int16_t',
            'unsigned short': 'uint16_t',
            'int': 'int32_t',
            'unsigned int': 'uint32_t',
            'long': 'int32_t',
            'unsigned long': 'uint32_t',
            'long long': 'int64_t',
            'unsigned long long': 'uint64_t',
            'float': 'float',
            'double': 'double',
            'void': 'void',
            'bool': 'bool',
        }
        self.type_sizes: Dict[str, int] = {
            'int8_t': 1,
            'uint8_t': 1,
            'int16_t': 2,
            'uint16_t': 2,
            'int32_t': 4,
            'uint32_t': 4,
            'int64_t': 8,
            'uint64_t': 8,
            'float': 4,
            'double': 8,
            'bool': 1,
            'void': 0,
        }
        
    def resolve_type(self, type_info: Dict[str, Any]) -> str:
        """解析C类型"""
        base_type = type_info.get('base_type', '')
        if not base_type:
            return 'void'
            
        # 处理指针
        ptr_count = type_info.get('pointer_level', 0)
        if ptr_count > 0:
            return f"{'*' * ptr_count}{self.type_map.get(base_type, base_type)}"
            
        # 处理数组
        array_dims = type_info.get('array_dims', [])
        if array_dims:
            dims = ''.join(f'[{d}]' for d in array_dims)
            return f"{self.type_map.get(base_type, base_type)}{dims}"
            
        return self.type_map.get(base_type, base_type)
        
    def get_type_size(self, type_name: str) -> int:
        """获取类型大小"""
        return self.type_sizes.get(type_name, 4)  # 默认4字节
        
    def register_type(self, name: str, size: int) -> None:
        """注册新类型"""
        self.type_sizes[name] = size
        
    def is_integer_type(self, type_name: str) -> bool:
        """检查是否是整数类型"""
        return type_name in {
            'int8_t', 'uint8_t',
            'int16_t', 'uint16_t',
            'int32_t', 'uint32_t',
            'int64_t', 'uint64_t'
        } 
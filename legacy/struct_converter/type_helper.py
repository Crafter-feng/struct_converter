from typing import Optional
from c_parser.type_manager import TypeManager
from utils.logger_config import setup_logger

logger = setup_logger('TypeHelper')

class TypeHelper:
    """类型处理辅助工具"""
    
    def __init__(self, type_manager: TypeManager):
        self.type_manager = type_manager
        self.printf_formats = {
            'char': '"%c"',
            'char*': '"%s"',
            'int': '"%d"',
            'unsigned int': '"%u"',
            'long': '"%ld"',
            'unsigned long': '"%lu"',
            'float': '"%f"',
            'double': '"%lf"',
            'bool': '"%s"',
            'void*': '"%p"',
            # 添加更多类型的格式化字符串
        }
        
    def get_printf_format(self, type_name: str) -> str:
        """获取类型的printf格式化字符串"""
        real_type = self.type_manager.get_real_type(type_name)
        return self.printf_formats.get(real_type, '"%p"')  # 默认使用指针格式
        
    def get_default_value(self, type_name: str) -> str:
        """获取类型的默认值"""
        real_type = self.type_manager.get_real_type(type_name)
        
        if real_type in ['char*', 'void*'] or '*' in type_name:
            return "NULL"
        elif real_type in ['int', 'long', 'char']:
            return "0"
        elif real_type in ['float', 'double']:
            return "0.0"
        elif real_type == 'bool':
            return "false"
        else:
            return "{0}"  # 结构体类型默认值
            
    def is_pointer_type(self, type_name: str) -> bool:
        """检查是否为指针类型"""
        return '*' in type_name or self.type_manager.is_pointer_type(type_name)
        
    def get_array_dimensions(self, field: dict) -> Optional[list]:
        """获取数组维度"""
        return field.get('array_size')
        
    def is_basic_type(self, type_name: str) -> bool:
        """检查是否为基本类型"""
        real_type = self.type_manager.get_real_type(type_name)
        return real_type in self.printf_formats 
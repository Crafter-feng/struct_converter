from typing import Dict, Any, List, Optional
from utils.logger import logger 
from .type_manager import TypeManager



class DataManager:
    """数据管理器，管理解析后的C语言数据结构"""
    
    def __init__(self, type_manager: TypeManager = None):
        self.type_manager = type_manager or TypeManager()
        self.variables = {
            'variables': [],    # 基本类型变量
            'struct_vars': [],  # 结构体变量
            'pointer_vars': [], # 指针变量
            'array_vars': [],   # 数组变量
        }
        
    def add_variable(self, var_info: Dict[str, Any]) -> None:
        """添加变量定义"""
        if var_info.get('is_pointer'):
            self.variables['pointer_vars'].append(var_info)
        elif var_info.get('array_size'):
            self.variables['array_vars'].append(var_info)
        elif self.type_manager.is_struct_type(var_info['type']):
            self.variables['struct_vars'].append(var_info)
        else:
            self.variables['variables'].append(var_info)
            
    def get_type_info(self) -> Dict[str, Any]:
        """获取类型信息"""
        return {
            'global': self.type_manager.export_global_type_info(),
            'current': self.type_manager.export_current_type_info()
        }
        
    def get_variables(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取变量信息"""
        return self.variables
        
    def get_all_data(self) -> Dict[str, Any]:
        """获取所有数据"""
        return {
            'structs': self.type_manager.find_types_by_kind('struct', scope='current'),
            'unions': self.type_manager.find_types_by_kind('union', scope='current'),
            'enums': self.type_manager.find_types_by_kind('enum', scope='current'),
            'typedefs': self.type_manager.find_types_by_kind('typedef', scope='current'),
            'variables': self.variables,
        }
        
    def clear(self) -> None:
        """清空所有数据"""
        self.variables = {
            'variables': [],
            'struct_vars': [],
            'pointer_vars': [],
            'array_vars': [],
        }
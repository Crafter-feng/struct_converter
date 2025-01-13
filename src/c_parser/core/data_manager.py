from typing import Dict, Any, List, Optional
from utils.logger import logger 
from .type_manager import TypeManager



class DataManager:
    """数据管理器，管理解析后的C语言数据结构"""
    
    def __init__(self):
        self.type_manager = TypeManager()
        self.variables = {
            'variables': [],    # 基本类型变量
            'struct_vars': [],  # 结构体变量
            'pointer_vars': [], # 指针变量
            'array_vars': [],   # 数组变量
        }
        self.structs = {}      # 结构体定义
        self.unions = {}       # 联合体定义
        self.enums = {}        # 枚举定义
        self.typedefs = {}     # 类型定义
        self.defines = {}      # 宏定义
        self.includes = []     # 包含文件
        
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
            
    def add_struct(self, name: str, struct_info: Dict[str, Any]) -> None:
        """添加结构体定义"""
        self.structs[name] = struct_info
        self.type_manager.add_struct_type(name, struct_info)
        
    def add_union(self, name: str, union_info: Dict[str, Any]) -> None:
        """添加联合体定义"""
        self.unions[name] = union_info
        self.type_manager.add_union_type(name, union_info)
        
    def add_enum(self, name: str, enum_info: Dict[str, Any]) -> None:
        """添加枚举定义"""
        self.enums[name] = enum_info
        self.type_manager.add_enum_type(name, enum_info)
        
    def add_typedef(self, name: str, type_info: Dict[str, Any]) -> None:
        """添加类型定义"""
        self.typedefs[name] = type_info
        self.type_manager.add_typedef(name, type_info)
        
    def add_define(self, name: str, value: Any) -> None:
        """添加宏定义"""
        self.defines[name] = value
        self.type_manager.add_macro_definition(name, value)
        
    def add_include(self, include_path: str) -> None:
        """添加包含文件"""
        if include_path not in self.includes:
            self.includes.append(include_path)
            
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
            'types': self.get_type_info(),
            'variables': self.variables,
            'structs': self.structs,
            'unions': self.unions,
            'enums': self.enums,
            'typedefs': self.typedefs,
            'defines': self.defines,
            'includes': self.includes
        }
        
    def clear(self) -> None:
        """清空所有数据"""
        self.variables = {
            'variables': [],
            'struct_vars': [],
            'pointer_vars': [],
            'array_vars': [],
        }
        self.structs.clear()
        self.unions.clear()
        self.enums.clear()
        self.typedefs.clear()
        self.defines.clear()
        self.includes.clear()
        self.type_manager.clear() 
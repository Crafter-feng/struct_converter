from typing import Dict, Any, Set, Optional
from utils.logger import logger 
import json



class TypeManager:
    """C语言类型管理器"""
    
    # 基本类型集合
    BASIC_TYPES = {
        # 整型
        'char', 'short', 'int', 'long', 'long long',
        'unsigned char', 'unsigned short', 'unsigned int', 'unsigned long', 'unsigned long long',
        'int8_t', 'int16_t', 'int32_t', 'int64_t',
        'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t',
        # 浮点型
        'float', 'double', 'long double',
        # 其他基本类型
        'bool', 'size_t', 'void', 'signed'
    }
    
    # 类型别名映射
    TYPE_ALIASES = {
        'u8': 'uint8_t',
        'u16': 'uint16_t',
        'u32': 'uint32_t',
        'u64': 'uint64_t',
        'i8': 'int8_t',
        'i16': 'int16_t',
        'i32': 'int32_t',
        'i64': 'int64_t',
        'f32': 'float',
        'f64': 'double'
    }
    
    # 基本打印格式映射
    PRINTF_FORMATS = {
        'char': '"%c"',
        'short': '%d',
        'int': '%d',
        'long': '%ld',
        'long long': '%lld',
        'unsigned char': '%u',
        'unsigned short': '%u',
        'unsigned int': '%u',
        'unsigned long': '%lu',
        'unsigned long long': '%llu',
        'int8_t': '%d',
        'int16_t': '%d',
        'int32_t': '%d',
        'int64_t': '%ld',
        'uint8_t': '%u',
        'uint16_t': '%u',
        'uint32_t': '%u',
        'uint64_t': '%lu',
        'float': '%.6f',
        'double': '%.6lf',
        'long double': '%.6Lf',
        'bool': '%s',
        'size_t': '%zu',
    }
    
    def __init__(self, type_info: Optional[Dict[str, Any]] = None):
        """初始化类型管理器"""
        # 全局类型信息
        self._global_typedef_types = {}
        self._global_struct_types = set()
        self._global_union_types = set()
        self._global_pointer_types = set()
        self._global_struct_info = {}
        self._global_union_info = {}
        self._global_enum_types = set()
        self._global_enum_info = {}
        self._global_macro_definitions = {}
        
        # 当前文件的类型信息
        self._current_typedef_types = {}
        self._current_struct_types = set()
        self._current_union_types = set()
        self._current_pointer_types = set()
        self._current_struct_info = {}
        self._current_union_info = {}
        self._current_enum_types = set()
        self._current_enum_info = {}
        self._current_macro_definitions = {}
        
        # 初始化全局类型信息
        if type_info:
            self._global_typedef_types.update(type_info.get('typedef_types', {}))
            self._global_struct_types.update(type_info.get('struct_types', set()))
            self._global_struct_info.update(type_info.get('struct_info', {}))
            self._global_union_types.update(type_info.get('union_types', set()))
            self._global_union_info.update(type_info.get('union_info', {}))
            self._global_enum_types.update(type_info.get('enum_types', set()))
            self._global_enum_info.update(type_info.get('enum_info', {}))
            self._global_pointer_types.update(type_info.get('pointer_types', set()))
            self._global_macro_definitions.update(type_info.get('macro_definitions', {}))

        # 更新类型别名映射
        if type_info and 'typedef_types' in type_info:
            self.TYPE_ALIASES.update(type_info['typedef_types'])

    def add_struct_type(self, type_name: str, type_info: Dict[str, Any], is_typedef: bool = False):
        """添加结构体类型到当前文件"""
        self._current_struct_types.add(type_name)
        self._current_struct_info[type_name] = type_info
        if is_typedef:
            self._current_typedef_types[type_name] = type_name

    def add_union_type(self, type_name: str, type_info: Dict[str, Any], is_typedef: bool = False):
        """添加联合体类型到当前文件"""
        self._current_union_types.add(type_name)
        self._current_union_info[type_name] = type_info
        if is_typedef:
            self._current_typedef_types[type_name] = type_name

    def add_enum_type(self, type_name: str, type_info: Dict[str, Any], is_typedef: bool = False):
        """添加枚举类型到当前文件"""
        self._current_enum_types.add(type_name)
        self._current_enum_info[type_name] = type_info
        if is_typedef:
            self._current_typedef_types[type_name] = type_name

    def add_pointer_type(self, alias: str, is_typedef: bool = False):
        """添加指针类型到当前文件"""
        self._current_pointer_types.add(alias)
        if is_typedef:
            self._current_typedef_types[alias] = alias

    def add_typedef_type(self, alias: str, target: str):
        """添加类型别名到当前文件"""
        self._current_typedef_types[alias] = target

    def add_macro_definition(self, macro_name: str, macro_value: str):
        """添加宏定义到当前文件"""
        self._current_macro_definitions[macro_name] = macro_value

    def export_type_info(self):
        """导出所有类型信息（合并全局和当前文件）"""
        # 合并类型定义
        typedef_types = self._global_typedef_types.copy()
        typedef_types.update(self._current_typedef_types)
        
        # 合并结构体信息
        struct_types = self._global_struct_types.union(self._current_struct_types)
        struct_info = self._global_struct_info.copy()
        struct_info.update(self._current_struct_info)
        
        # 合并联合体信息
        union_types = self._global_union_types.union(self._current_union_types)
        union_info = self._global_union_info.copy()
        union_info.update(self._current_union_info)
        
        # 合并枚举信息
        enum_types = self._global_enum_types.union(self._current_enum_types)
        enum_info = self._global_enum_info.copy()
        enum_info.update(self._current_enum_info)
        
        # 合并指针类型
        pointer_types = self._global_pointer_types.union(self._current_pointer_types)
        
        # 合并宏定义
        macro_definitions = self._global_macro_definitions.copy()
        macro_definitions.update(self._current_macro_definitions)
        
        return {
            'typedef_types': typedef_types,
            'struct_types': list(struct_types),
            'struct_info': struct_info,   
            'union_types': list(union_types),
            'union_info': union_info,
            'enum_types': list(enum_types),
            'enum_info': enum_info,
            'pointer_types': list(pointer_types),
            'macro_definitions': macro_definitions
        }
    
    def update_type_info(self, type_info: Dict[str, Any], to_global: bool = False):
        """更新类型信息
        
        Args:
            type_info: 要更新的类型信息
            to_global: 是否更新到全局类型信息
        """
        self.merge_type_info(type_info, to_global)
        
        # 如果更新到全局，同时更新类型别名映射
        if to_global and 'typedef_types' in type_info:
            self.TYPE_ALIASES.update(type_info['typedef_types'])

    def reset_type_info(self):
        """重置所有类型信息（包括全局和当前文件）"""
        # 重置全局类型信息
        self._global_typedef_types = {}
        self._global_struct_types = set()
        self._global_struct_info = {}
        self._global_union_types = set()
        self._global_union_info = {}
        self._global_enum_types = set()
        self._global_enum_info = {}
        self._global_pointer_types = set()
        self._global_macro_definitions = {}
        
        # 重置当前文件类型信息
        self.reset_current_type_info()

    def get_struct_info(self, struct_name: str = None) -> Dict[str, Any]:
        """获取结构体信息"""
        if struct_name:
            # 优先查找当前文件
            if struct_name in self._current_struct_info:
                return self._current_struct_info[struct_name]
            # 然后查找全局定义
            return self._global_struct_info.get(struct_name, {})
        else:
            # 合并全局和当前文件的信息
            merged_info = self._global_struct_info.copy()
            merged_info.update(self._current_struct_info)
            return merged_info
    
    def get_union_info(self, union_name: str = None) -> Dict[str, Any]:
        """获取联合体信息"""
        if union_name:
            # 优先查找当前文件
            if union_name in self._current_union_info:
                return self._current_union_info[union_name]
            # 然后查找全局定义
            return self._global_union_info.get(union_name, {})
        else:
            # 合并全局和当前文件的信息
            merged_info = self._global_union_info.copy()
            merged_info.update(self._current_union_info)
            return merged_info
    
    def get_enum_info(self, enum_name: str = None) -> Dict[str, Any]:
        """获取枚举信息"""
        if enum_name:
            # 优先查找当前文件
            if enum_name in self._current_enum_info:
                return self._current_enum_info[enum_name]
            # 然后查找全局定义
            return self._global_enum_info.get(enum_name, {})
        else:
            # 合并全局和当前文件的信息
            merged_info = self._global_enum_info.copy()
            merged_info.update(self._current_enum_info)
            return merged_info
    
    def get_macro_definition(self, macro_name: str = None) -> str:
        """获取宏定义"""
        if macro_name:
            # 优先查找当前文件
            if macro_name in self._current_macro_definitions:
                return self._current_macro_definitions[macro_name]
            # 然后查找全局定义
            return self._global_macro_definitions.get(macro_name, macro_name)
        else:
            # 合并全局和当前文件的信息
            merged_info = self._global_macro_definitions.copy()
            merged_info.update(self._current_macro_definitions)
            return merged_info
    
    def is_basic_type(self, type_name: str) -> bool:
        """检查是否是基本类型"""
        # 检查是否是其他已知类型
        if (type_name in self._global_struct_types or type_name in self._current_struct_types or
            type_name in self._global_union_types or type_name in self._current_union_types or
            type_name in self._global_enum_types or type_name in self._current_enum_types or
            type_name in self._global_pointer_types or type_name in self._current_pointer_types):
            return False
            
        # 检查是否是基本类型或其别名
        if type_name in self.BASIC_TYPES:
            return True
            
        # 检查是否是类型别名，并递归检查其实际类型
        real_type = self.get_real_type(type_name)
        if real_type != type_name:
            return self.is_basic_type(real_type)
            
        return False
        
    def is_struct_type(self, type_name: str) -> bool:
        """检查是否是结构体类型"""
        if type_name.startswith('struct '):
            return True
        
        # 清理类型名称，移除struct前缀
        clean_name = self._clean_type_name(type_name)
        
        # 检查当前文件和全局的结构体类型集合
        if clean_name in self._current_struct_types or clean_name in self._global_struct_types:
            return True
        
        # 检查类型别名
        real_type = self.get_real_type(clean_name)
        # 只在实际类型不同且不是自身引用时继续检查
        if real_type != clean_name and real_type != type_name:
            return self.is_struct_type(real_type)
        
        return False
        
    def is_union_type(self, type_name: str) -> bool:
        """检查是否是联合体类型"""
        if type_name.startswith('union '):
            return True
        
        # 清理类型名称，移除union前缀
        clean_name = self._clean_type_name(type_name)
        
        # 检查当前文件和全局的联合体类型集合
        if clean_name in self._current_union_types or clean_name in self._global_union_types:
            return True
        
        # 检查类型别名
        real_type = self.get_real_type(clean_name)
        # 只在实际类型不同且不是自身引用时继续检查
        if real_type != clean_name and real_type != type_name:
            return self.is_union_type(real_type)
        
        return False
        
    def is_enum_type(self, type_name: str) -> bool:
        """检查是否是枚举类型"""
        if type_name.startswith('enum '):
            return True
        
        # 清理类型名称
        clean_name = self._clean_type_name(type_name)
        
        # 检查当前文件和全局的枚举类型集合
        if clean_name in self._current_enum_types or clean_name in self._global_enum_types:
            return True
        
        # 检查类型别名
        real_type = self.get_real_type(clean_name)
        if real_type != clean_name:
            return self.is_enum_type(real_type)
        
        return False
        
    def is_pointer_type(self, type_name: str) -> bool:
        """检查是否是指针类型"""
        # 检查直接指针语法
        if '*' in type_name:
            return True
            
        # 清理类型名称
        clean_name = self._clean_type_name(type_name)
        
        # 检查当前文件和全局的指针类型集合
        if clean_name in self._current_pointer_types or clean_name in self._global_pointer_types:
            return True
            
        # 检查类型别名
        real_type = self.get_real_type(clean_name)
        if real_type != clean_name:
            return self.is_pointer_type(real_type)
            
        return False
        
    def get_real_type(self, type_name: str, visited: Set[str] = None) -> str:
        """获取类型的实际类型（解析别名）"""
        if visited is None:
            visited = set()
        
        # 防止循环引用
        if type_name in visited:
            logger.warning(f"Detected circular type reference: {type_name}")
            return type_name
        visited.add(type_name)
        
        # 检查内置类型别名
        if type_name in self.BASIC_TYPES:
            return type_name
        
        if type_name in self.TYPE_ALIASES:
            return self.TYPE_ALIASES[type_name]
        
        # 优先检查当前文件的类型别名
        if type_name in self._current_typedef_types:
            base_type = self._current_typedef_types[type_name]
            if base_type != type_name:  # 避免自引用
                return self.get_real_type(base_type, visited)
            
        # 然后检查全局类型别名
        if type_name in self._global_typedef_types:
            base_type = self._global_typedef_types[type_name]
            if base_type != type_name:  # 避免自引用
                return self.get_real_type(base_type, visited)
            
        return type_name
    
    def _clean_type_name(self, type_name: str) -> str:
        """清理类型名称，移除前缀和修饰符
        
        Args:
            type_name: 原始类型名称
            
        Returns:
            str: 清理后的类型名称
        """
        # 移除 struct/union/enum 前缀和指针符号
        clean_name = type_name.replace('struct ', '').replace('union ', '').replace('enum ', '').rstrip('*')
        return clean_name.strip()
    
    def get_printf_format(self, type_name: str) -> str:
        """获取类型的printf格式化字符串
        
        Args:
            type_name: 类型名称
            
        Returns:
            printf格式化字符串
        """
        clean_name = self._clean_type_name(type_name)
        
        # 检查是否为指针类型
        if self.is_pointer_type(type_name):
            return '"0x%p"'
        
        # 检查是否为枚举类型
        if self.is_enum_type(clean_name):
            return '%d'
        
        # 先尝试获取实际类型（解析别名）
        real_type = self.get_real_type(clean_name)
        
        # 获取基本类型的格式化字符串
        if real_type in self.PRINTF_FORMATS:
            return self.PRINTF_FORMATS[real_type]
        
        # 默认使用十六进制格式
        return '"0x%x"'

    def resolve_type(self, type_name: str, base_info: Optional[Dict] = None) -> Dict[str, Any]:
        """解析类型名称，返回完整的类型信息"""
        logger.debug(f"\nResolving type: {type_name}")
        if base_info:
            logger.debug(f"Base info: {json.dumps(base_info, indent=2)}")
        
        # 创建基础类型信息
        type_info = {
            'type': type_name,
            'base_type': type_name,
            'resolved_type': None,
            'is_pointer': False,
            'pointer_level': 0,
            'array_size': None,
            'bit_field': None,
            'nested_fields': None,
            'info': None,
            'original_type': type_name,  # 保存原始类型名
            'is_typedef': False,         # 是否是typedef类型
            'is_anonymous': False        # 是否是匿名类型
        }
        
        # 合并基础信息
        if base_info:
            type_info.update(base_info)
        
        # 处理指针类型
        base_type = type_name
        pointer_level = type_info.get('pointer_level', 0)
        
        # 处理类型名中的指针
        while base_type.endswith('*'):
            base_type = base_type[:-1].strip()
            pointer_level += 1
        
        # 解析类型
        resolved_type = self.get_real_type(base_type)
        
        # 如果解析后的类型也是指针
        while resolved_type.endswith('*'):
            resolved_type = resolved_type[:-1].strip()
            pointer_level += 1
        
        # 检查是否是指针类型定义
        if self.is_pointer_type(resolved_type):
            pointer_level += 1
            resolved_type = resolved_type.rstrip('*')
        
        # 获取基础类型的信息
        type_info.update({
            'is_basic': self.is_basic_type(resolved_type),
            'is_struct': self.is_struct_type(resolved_type) or bool(type_info.get('nested_fields')),
            'is_union': self.is_union_type(resolved_type),
            'is_enum': self.is_enum_type(resolved_type),
            'is_pointer': pointer_level > 0,
            'pointer_level': pointer_level,
            'base_type': resolved_type,
            'resolved_type': f"{resolved_type}{'*' * pointer_level}"
        })
        
        # 获取详细类型信息
        if type_info['is_struct'] and not type_info.get('nested_fields'):
            type_info['info'] = self.get_struct_info(resolved_type)
        elif type_info['is_union']:
            type_info['info'] = self.get_union_info(resolved_type)
        elif type_info['is_enum']:
            type_info['info'] = self.get_enum_info(resolved_type)
        
        logger.debug(f"Final resolved type info: {json.dumps(type_info, indent=2)}")
        return type_info

    def export_global_type_info(self):
        """导出全局类型信息"""
        return {
            'typedef_types': self._global_typedef_types,
            'struct_types': list(self._global_struct_types),
            'struct_info': self._global_struct_info,   
            'union_types': list(self._global_union_types),
            'union_info': self._global_union_info,
            'enum_types': list(self._global_enum_types),
            'enum_info': self._global_enum_info,
            'pointer_types': list(self._global_pointer_types),
            'macro_definitions': self._global_macro_definitions
        }

    def export_current_type_info(self):
        """导出当前文件的类型信息"""
        return {
            'typedef_types': self._current_typedef_types,
            'struct_types': list(self._current_struct_types),
            'struct_info': self._current_struct_info,   
            'union_types': list(self._current_union_types),
            'union_info': self._current_union_info,
            'enum_types': list(self._current_enum_types),
            'enum_info': self._current_enum_info,
            'pointer_types': list(self._current_pointer_types),
            'macro_definitions': self._current_macro_definitions
        }

    def reset_current_type_info(self):
        """重置当前文件的类型信息"""
        self._current_typedef_types = {}
        self._current_struct_types = set()
        self._current_struct_info = {}
        self._current_union_types = set()
        self._current_union_info = {}
        self._current_enum_types = set()
        self._current_enum_info = {}
        self._current_pointer_types = set()
        self._current_macro_definitions = {}

    def is_typedef_type(self, type_name: str) -> bool:
        """检查是否是typedef类型"""
        clean_name = self._clean_type_name(type_name)
        return (clean_name in self._current_typedef_types or 
                clean_name in self._global_typedef_types)

    def is_anonymous_type(self, type_name: str) -> bool:
        """检查是否是匿名类型"""
        return not type_name or type_name.startswith('anonymous_')

    def merge_type_info(self, other_type_info: Dict[str, Any], to_global: bool = False):
        """合并其他类型信息
        
        Args:
            other_type_info: 要合并的类型信息
            to_global: 是否合并到全局类型信息
        """
        target = self._global_typedef_types if to_global else self._current_typedef_types
        target.update(other_type_info.get('typedef_types', {}))
        
        target = self._global_struct_types if to_global else self._current_struct_types
        target.update(other_type_info.get('struct_types', set()))
        
        target = self._global_struct_info if to_global else self._current_struct_info
        target.update(other_type_info.get('struct_info', {}))
        
        target = self._global_union_types if to_global else self._current_union_types
        target.update(other_type_info.get('union_types', set()))
        
        target = self._global_union_info if to_global else self._current_union_info
        target.update(other_type_info.get('union_info', {}))
        
        target = self._global_enum_types if to_global else self._current_enum_types
        target.update(other_type_info.get('enum_types', set()))
        
        target = self._global_enum_info if to_global else self._current_enum_info
        target.update(other_type_info.get('enum_info', {}))
        
        target = self._global_pointer_types if to_global else self._current_pointer_types
        pointer_types = other_type_info.get('pointer_types', set())
        if isinstance(pointer_types, list):
            target.update(set(pointer_types))
        else:
            target.update(pointer_types)
        
        target = self._global_macro_definitions if to_global else self._current_macro_definitions
        target.update(other_type_info.get('macro_definitions', {}))

    def get_type_category(self, type_name: str) -> str:
        """获取类型的分类
        
        Args:
            type_name: 类型名称
            
        Returns:
            str: 类型分类（'basic', 'struct', 'union', 'enum', 'pointer', 'typedef', 'unknown'）
        """
        if self.is_basic_type(type_name):
            return 'basic'
        elif self.is_struct_type(type_name):
            return 'struct'
        elif self.is_union_type(type_name):
            return 'union'
        elif self.is_enum_type(type_name):
            return 'enum'
        elif self.is_pointer_type(type_name):
            return 'pointer'
        elif self.is_typedef_type(type_name):
            return 'typedef'
        else:
            return 'unknown'

    def is_composite_type(self, type_name: str) -> bool:
        """检查是否是复合类型（结构体或联合体）"""
        return self.is_struct_type(type_name) or self.is_union_type(type_name)
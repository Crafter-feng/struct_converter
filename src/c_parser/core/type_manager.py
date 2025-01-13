from typing import Dict, Any, Optional, List, Set, Tuple, Union
import json
from loguru import logger


class TypeManager:
    """C语言类型管理器"""
    
    # 基本类型集合，添加更多详细信息
    BASIC_TYPES = {
        # 整型
        'char': {'size': 1, 'signed': True, 'alignment': 1},
        'short': {'size': 2, 'signed': True, 'alignment': 2},
        'int': {'size': 4, 'signed': True, 'alignment': 4},
        'long': {'size': 8, 'signed': True, 'alignment': 8},
        'long long': {'size': 8, 'signed': True, 'alignment': 8},
        'unsigned char': {'size': 1, 'signed': False, 'alignment': 1},
        'unsigned short': {'size': 2, 'signed': False, 'alignment': 2},
        'unsigned int': {'size': 4, 'signed': False, 'alignment': 4},
        'unsigned long': {'size': 8, 'signed': False, 'alignment': 8},
        'unsigned long long': {'size': 8, 'signed': False, 'alignment': 8},
        'int8_t': {'size': 1, 'signed': True, 'alignment': 1},
        'int16_t': {'size': 2, 'signed': True, 'alignment': 2},
        'int32_t': {'size': 4, 'signed': True, 'alignment': 4},
        'int64_t': {'size': 8, 'signed': True, 'alignment': 8},
        'uint8_t': {'size': 1, 'signed': False, 'alignment': 1},
        'uint16_t': {'size': 2, 'signed': False, 'alignment': 2},
        'uint32_t': {'size': 4, 'signed': False, 'alignment': 4},
        'uint64_t': {'size': 8, 'signed': False, 'alignment': 8},
        # 浮点型
        'float': {'size': 4, 'signed': True, 'alignment': 4},
        'double': {'size': 8, 'signed': True, 'alignment': 8},
        'long double': {'size': 16, 'signed': True, 'alignment': 16},
        # 其他基本类型
        'bool': {'size': 1, 'signed': False, 'alignment': 1},
        'size_t': {'size': 8, 'signed': False, 'alignment': 8},
        'void': {'size': 0, 'signed': False, 'alignment': 1},
        'signed': {'size': 4, 'signed': True, 'alignment': 4}
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
        
        # 添加新的类型管理相关属性
        self.type_info = {}  # 存储所有类型的完整信息
        self.type_details = {}  # 存储类型的详细信息
        self.type_comments = {}  # 存储类型的注释
        self.type_locations = {}  # 存储类型的位置信息
        self.type_status = {}  # 存储类型的状态
        self.type_scopes = {}  # 存储类型的作用域
        self.type_qualifiers = {}  # 存储类型的限定符
        self.type_attributes = {}  # 存储类型的属性
        self.type_metadata = {}  # 存储类型的元数据
        self.field_offsets = {}  # 存储结构体字段的偏移量
        
        # 初始化全局类型信息
        if type_info:
            self._load_type_info(type_info)
        
        # 更新类型别名映射
        if type_info and 'typedef_types' in type_info:
            self.TYPE_ALIASES.update(type_info['typedef_types'])

    @property
    def basic_types(self):
        """获取基本类型集合"""
        return self.BASIC_TYPES

    @property
    def struct_types(self):
        """获取所有结构体类型"""
        return self._global_struct_types.union(self._current_struct_types)

    @property
    def union_types(self):
        """获取所有联合体类型"""
        return self._global_union_types.union(self._current_union_types)

    @property
    def enum_types(self):
        """获取所有枚举类型"""
        return self._global_enum_types.union(self._current_enum_types)

    @property
    def typedef_types(self):
        """获取所有类型别名"""
        typedef_types = self._global_typedef_types.copy()
        typedef_types.update(self._current_typedef_types)
        return typedef_types

    def _load_type_info(self, type_info: Dict[str, Any]) -> None:
        """加载类型信息"""
        try:
            # 加载原有的类型信息
            self._global_typedef_types.update(type_info.get('typedef_types', {}))
            
            # 处理结构体类型
            struct_types = type_info.get('struct_types', {})
            if isinstance(struct_types, dict):
                self._global_struct_types.update(struct_types.keys())
                self._global_struct_info.update(struct_types)  # 直接使用 struct_types 作为 struct_info
            else:
                self._global_struct_types.update(struct_types)
            self._global_struct_info.update(type_info.get('struct_info', {}))
            
            # 处理联合体类型
            union_types = type_info.get('union_types', {})
            if isinstance(union_types, dict):
                self._global_union_types.update(union_types.keys())
                self._global_union_info.update(union_types)  # 直接使用 union_types 作为 union_info
            else:
                self._global_union_types.update(union_types)
            self._global_union_info.update(type_info.get('union_info', {}))
            
            # 处理枚举类型
            enum_types = type_info.get('enum_types', {})
            if isinstance(enum_types, dict):
                self._global_enum_types.update(enum_types.keys())
                self._global_enum_info.update(enum_types)  # 直接使用 enum_types 作为 enum_info
            else:
                self._global_enum_types.update(enum_types)
            self._global_enum_info.update(type_info.get('enum_info', {}))
            
            # 其他类型信息
            self._global_pointer_types.update(type_info.get('pointer_types', set()))
            self._global_macro_definitions.update(type_info.get('macro_definitions', {}))

            # 加载新增的类型信息
            if 'type_info' in type_info:
                self.type_info.update(type_info['type_info'])
            if 'type_details' in type_info:
                self.type_details.update(type_info['type_details'])
            if 'type_comments' in type_info:
                self.type_comments.update(type_info['type_comments'])
            if 'type_locations' in type_info:
                self.type_locations.update(type_info['type_locations'])

        except Exception as e:
            logger.error(f"Failed to load type info: {e}")
            raise

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

    def add_enum_type(self, name: str, values: Dict[str, Any]) -> None:
        """添加枚举类型
        
        Args:
            name: 枚举类型名称
            values: 枚举值字典
        """
        enum_info = {
            'kind': 'enum',
            'name': name,
            'values': values,
            'size': 4,  # 默认枚举大小为4字节
            'alignment': 4  # 默认对齐为4字节
        }
        
        # 更新类型信息
        self._current_enum_types.add(name)
        self._current_enum_info[name] = enum_info
        self.type_info[name] = enum_info
        
        # 更新枚举值到宏定义
        for enum_name, value in values.items():
            if isinstance(value, (int, float)):
                self._current_macro_definitions[enum_name] = value

    def add_pointer_type(self, alias: str, is_typedef: bool = False):
        """添加指针类型到当前文件"""
        self._current_pointer_types.add(alias)
        if is_typedef:
            self._current_typedef_types[alias] = alias

    def add_typedef_type(self, alias: str, target: str):
        """添加类型别名到当前文件"""
        self._current_typedef_types[alias] = target

    def add_macro_definition(self, name: str, value: Any) -> None:
        """添加宏定义
        
        Args:
            name: 宏名称
            value: 宏值
        """
        self._current_macro_definitions[name] = value

    def export_type_info(self):
        """导出所有类型信息（合并全局和当前文件）"""
        # 合并类型定义
        typedef_types = self._global_typedef_types.copy()
        typedef_types.update(self._current_typedef_types)
        
        # 合并结构体信息
        struct_types = {}
        struct_info = self._global_struct_info.copy()
        struct_info.update(self._current_struct_info)
        for name in self._global_struct_types.union(self._current_struct_types):
            if name in struct_info:
                struct_types[name] = struct_info[name]
        
        # 合并联合体信息
        union_types = {}
        union_info = self._global_union_info.copy()
        union_info.update(self._current_union_info)
        for name in self._global_union_types.union(self._current_union_types):
            if name in union_info:
                union_types[name] = union_info[name]
        
        # 合并枚举信息
        enum_types = {}
        enum_info = self._global_enum_info.copy()
        enum_info.update(self._current_enum_info)
        for name in self._global_enum_types.union(self._current_enum_types):
            if name in enum_info:
                enum_types[name] = enum_info[name]
        
        # 合并指针类型
        pointer_types = list(self._global_pointer_types.union(self._current_pointer_types))
        
        # 合并宏定义
        macro_definitions = self._global_macro_definitions.copy()
        macro_definitions.update(self._current_macro_definitions)
        
        return {
            'typedef_types': typedef_types,
            'struct_types': struct_types,
            'struct_info': struct_info,   
            'union_types': union_types,
            'union_info': union_info,
            'enum_types': enum_types,
            'enum_info': enum_info,
            'pointer_types': pointer_types,
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
        """判断是否为基本类型"""
        # 清理类型名称
        clean_name = self._clean_type_name(type_name)
        
        # 检查是否是其他已知类型
        if (clean_name in self._global_struct_types or clean_name in self._current_struct_types or
            clean_name in self._global_union_types or clean_name in self._current_union_types or
            clean_name in self._global_enum_types or clean_name in self._current_enum_types or
            clean_name in self._global_pointer_types or clean_name in self._current_pointer_types or
            clean_name in self._global_typedef_types or clean_name in self._current_typedef_types):  # 添加 typedef 检查
            return False
            
        # 检查是否是基本类型
        if clean_name in self.BASIC_TYPES:
            return True
            
        # 检查是否是类型别名，并递归检查其实际类型
        if clean_name in self.TYPE_ALIASES:  # 修改这里，不再递归检查类型别名
            return False
            
        return False
        
    def is_struct_type(self, type_name: str) -> bool:
        """判断是否为结构体类型"""
        # 处理 'struct X' 形式
        if type_name.startswith('struct '):
            return True
        
        # 清理类型名称
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
        """判断是否为联合体类型"""
        # 处理 'union X' 形式
        if type_name.startswith('union '):
            return True
        
        # 清理类型名称
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
        """判断是否为枚举类型"""
        # 处理 'enum X' 形式
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
        """判断是否为指针类型"""
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
        
        # 如果输入是字典，提取 base_type
        if isinstance(type_name, dict):
            type_name = type_name.get('base_type', '')
        
        # 防止循环引用
        if type_name in visited:
            logger.warning(f"Detected circular type reference: {type_name}")
            return type_name
        visited.add(type_name)
        
        # 检查内置类型别名
        if type_name in self.BASIC_TYPES:
            return type_name
        
        if type_name in self.TYPE_ALIASES:
            alias_type = self.TYPE_ALIASES[type_name]
            if isinstance(alias_type, dict):
                alias_type = alias_type.get('base_type', '')
            return self.get_real_type(alias_type, visited)
        
        # 优先检查当前文件的类型别名
        if type_name in self._current_typedef_types:
            base_type = self._current_typedef_types[type_name]
            if isinstance(base_type, dict):
                base_type = base_type.get('base_type', '')
            if base_type != type_name:  # 避免自引用
                return self.get_real_type(base_type, visited)
            
        # 然后检查全局类型别名
        if type_name in self._global_typedef_types:
            base_type = self._global_typedef_types[type_name]
            if isinstance(base_type, dict):
                base_type = base_type.get('base_type', '')
            if base_type != type_name:  # 避免自引用
                return self.get_real_type(base_type, visited)
            
        return type_name
    
    def _clean_type_name(self, type_name: str) -> str:
        """清理类型名称，移除前缀和修饰符"""
        if isinstance(type_name, dict):
            type_name = type_name.get('base_type', '')
        
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

    def export_global_type_info(self) -> Dict[str, Any]:
        """导出全局类型信息
        
        Returns:
            包含所有全局类型信息的字典
        """
        return {
            'typedef_types': self._global_typedef_types,
            'struct_types': list(self._global_struct_types),
            'struct_info': self._global_struct_info,   
            'union_types': list(self._global_union_types),
            'union_info': self._global_union_info,
            'enum_types': list(self._global_enum_types),
            'enum_info': self._global_enum_info,
            'pointer_types': list(self._global_pointer_types),
            'macro_definitions': self._global_macro_definitions,
            'type_info': self.type_info,  # 添加新的类型信息
            'type_details': self.type_details,
            'type_comments': self.type_comments,
            'type_locations': self.type_locations
        }

    def export_current_type_info(self) -> Dict[str, Any]:
        """导出当前文件的类型信息
        
        Returns:
            包含当前文件所有类型信息的字典
        """
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

    def reset_current_type_info(self) -> None:
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

    def merge_type_info(self, other_type_info: Dict[str, Any], to_global: bool = False) -> None:
        """合并其他类型信息
        
        Args:
            other_type_info: 要合并的类型信息
            to_global: 是否合并到全局类型信息
        """
        try:
            # 选择目标存储
            typedef_types = self._global_typedef_types if to_global else self._current_typedef_types
            struct_types = self._global_struct_types if to_global else self._current_struct_types
            struct_info = self._global_struct_info if to_global else self._current_struct_info
            union_types = self._global_union_types if to_global else self._current_union_types
            union_info = self._global_union_info if to_global else self._current_union_info
            enum_types = self._global_enum_types if to_global else self._current_enum_types
            enum_info = self._global_enum_info if to_global else self._current_enum_info
            pointer_types = self._global_pointer_types if to_global else self._current_pointer_types
            macro_definitions = self._global_macro_definitions if to_global else self._current_macro_definitions

            # 合并基本类型信息
            typedef_types.update(other_type_info.get('typedef_types', {}))
            struct_types.update(other_type_info.get('struct_types', set()))
            struct_info.update(other_type_info.get('struct_info', {}))
            union_types.update(other_type_info.get('union_types', set()))
            union_info.update(other_type_info.get('union_info', {}))
            enum_types.update(other_type_info.get('enum_types', set()))
            enum_info.update(other_type_info.get('enum_info', {}))
            
            # 处理指针类型
            pointer_types_data = other_type_info.get('pointer_types', set())
            if isinstance(pointer_types_data, list):
                pointer_types.update(set(pointer_types_data))
            else:
                pointer_types.update(pointer_types_data)
            
            macro_definitions.update(other_type_info.get('macro_definitions', {}))

            # 合并扩展的类型信息
            if to_global:
                if 'type_info' in other_type_info:
                    self.type_info.update(other_type_info['type_info'])
                if 'type_details' in other_type_info:
                    self.type_details.update(other_type_info['type_details'])
                if 'type_comments' in other_type_info:
                    self.type_comments.update(other_type_info['type_comments'])
                if 'type_locations' in other_type_info:
                    self.type_locations.update(other_type_info['type_locations'])

        except Exception as e:
            logger.error(f"Failed to merge type info: {e}")
            raise

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
    
    def parse_type_string(self, type_str: str) -> Dict[str, Any]:
        """解析类型字符串
        
        Args:
            type_str: 类型字符串
            
        Returns:
            包含类型信息的字典
        """
        result = {
            'base_type': '',
            'is_const': False,
            'is_volatile': False,
            'pointer_level': 0,
            'qualifiers': [],
            'array_dims': [],
            'storage_class': None,
            'is_restrict': False
        }
        
        # 移除多余空格
        type_str = ' '.join(type_str.split())
        
        # 处理存储类型
        storage_classes = ['static', 'extern', 'auto', 'register']
        for storage in storage_classes:
            if storage in type_str.split():
                result['storage_class'] = storage
                type_str = type_str.replace(storage, '').strip()
        
        # 处理限定符
        if 'const' in type_str:
            result['is_const'] = True
            result['qualifiers'].append('const')
            type_str = type_str.replace('const', '').strip()
            
        if 'volatile' in type_str:
            result['is_volatile'] = True
            result['qualifiers'].append('volatile')
            type_str = type_str.replace('volatile', '').strip()
            
        if 'restrict' in type_str:
            result['is_restrict'] = True
            result['qualifiers'].append('restrict')
            type_str = type_str.replace('restrict', '').strip()
            
        # 处理数组维度
        while '[' in type_str and ']' in type_str:
            start = type_str.find('[')
            end = type_str.find(']')
            if start > 0 and end > start:
                dim = type_str[start+1:end]
                if dim.isdigit():
                    result['array_dims'].append(int(dim))
                type_str = type_str[:start] + type_str[end+1:]
        
        # 计算指针级别
        result['pointer_level'] = type_str.count('*')
        type_str = type_str.replace('*', '').strip()
        
        # 设置基本类型
        result['base_type'] = type_str.strip()
        
        return result

    def get_type_details(self, type_name: str) -> Dict[str, Any]:
        """获取类型的详细信息
        
        Args:
            type_name: 类型名称
            
        Returns:
            包含类型详细信息的字典
        """
        if type_name in self.type_info:
            type_info = self.type_info[type_name]
            details = type_info.get('details', {})
            
            # 确保返回所有必要的字段
            return {
                'details': details,
                'location': type_info.get('location', {}),
                'comment': type_info.get('comment', ''),
                'attributes': details.get('attributes', {}),
                'visibility': details.get('visibility', 'public'),
                'storage_class': details.get('storage_class', ''),
                'packed': details.get('packed', False),
                'kind': type_info.get('kind', ''),
                'name': type_info.get('name', type_name),
                'fields': type_info.get('fields', [])
            }
        return {} 

    def get_type_location(self, type_name: str) -> Dict[str, Any]:
        """获取类型的位置信息
        
        Args:
            type_name: 类型名称
            
        Returns:
            包含位置信息的字典，包括文件、行号和列号
        """
        if type_name in self.type_info:
            return self.type_info[type_name].get('location', {})
        return {}

    def get_type_comment(self, type_name: str) -> str:
        """获取类型的注释信息
        
        Args:
            type_name: 类型名称
            
        Returns:
            类型的注释字符串，如果没有注释则返回空字符串
        """
        if type_name in self.type_info:
            return self.type_info[type_name].get('comment', '')
        return ''

    def is_compatible_types(self, type1: str, type2: str) -> bool:
        """检查两个类型是否兼容
        
        Args:
            type1: 第一个类型名称
            type2: 第二个类型名称
        
        Returns:
            如果类型兼容返回True，否则返回False
        """
        # 清理类型名称中的空格和*
        type1 = type1.replace(' ', '')
        type2 = type2.replace(' ', '')
        
        # 获取实际类型
        real_type1 = self.get_real_type(type1)
        real_type2 = self.get_real_type(type2)
        
        # 处理指针类型
        if '*' in type1 or '*' in type2:
            # void* 可以与任何指针类型兼容
            if 'void*' in (type1, type2):
                return '*' in type1 and '*' in type2
            # 检查指针级别是否相同
            if type1.count('*') != type2.count('*'):
                return False
            # 去掉指针后比较基本类型
            base1 = real_type1.rstrip('*')
            base2 = real_type2.rstrip('*')
            return base1 == base2 or 'void' in (base1, base2)
            
        # 处理基本类型
        if real_type1 in self.BASIC_TYPES and real_type2 in self.BASIC_TYPES:
            type1_info = self.BASIC_TYPES[real_type1]
            type2_info = self.BASIC_TYPES[real_type2]
            return (type1_info['size'] == type2_info['size'] and 
                   type1_info.get('signed') == type2_info.get('signed'))
                   
        # 其他情况，类型必须完全相同
        return real_type1 == real_type2

    def get_enum_value(self, enum_name: str, value_name: str) -> Optional[Any]:
        """获取枚举值
        
        Args:
            enum_name: 枚举类型名称
            value_name: 枚举值名称
            
        Returns:
            枚举值，如果不存在返回None
        """
        # 优先查找当前文件
        if enum_name in self._current_enum_info:
            values = self._current_enum_info[enum_name].get('values', {})
            if value_name in values:
                return values[value_name]
        
        # 然后查找全局定义
        if enum_name in self._global_enum_info:
            values = self._global_enum_info[enum_name].get('values', {})
            return values.get(value_name)
        
        return None

    def get_enum_values(self, enum_name: str) -> Dict[str, Any]:
        """获取枚举类型的所有值
        
        Args:
            enum_name: 枚举类型名称
            
        Returns:
            包含所有枚举值的字典
        """
        # 优先查找当前文件
        if enum_name in self._current_enum_info:
            return self._current_enum_info[enum_name].get('values', {})
        
        # 然后查找全局定义
        if enum_name in self._global_enum_info:
            return self._global_enum_info[enum_name].get('values', {})
        
        return {}

    def has_macro(self, name: str) -> bool:
        """检查宏是否存在
        
        Args:
            name: 宏名称
        
        Returns:
            如果宏存在返回True，否则返回False
        """
        return (name in self._current_macro_definitions or 
                name in self._global_macro_definitions)

    def register_type(self, name: str, info: Dict[str, Any]) -> None:
        """注册类型信息
        
        Args:
            name: 类型名称
            info: 类型信息字典
        """
        # 直接存储完整的类型信息
        self.type_info[name] = info.copy()
        
        # 根据类型分类存储
        kind = info.get('kind', '')
        if kind == 'struct':
            self._current_struct_types.add(name)
            self._current_struct_info[name] = info.copy()
        elif kind == 'union':
            self._current_union_types.add(name)
            self._current_union_info[name] = info.copy()
        elif kind == 'enum':
            self._current_enum_types.add(name)
            self._current_enum_info[name] = info.copy()
        elif kind == 'typedef':
            self._current_typedef_types[name] = info.copy()
            if info.get('base_type', '').endswith('*'):
                self._current_pointer_types.add(name)

    def get_type_size(self, type_name: str) -> int:
        """获取类型的大小（字节数）
        
        Args:
            type_name: 类型名称
            
        Returns:
            类型大小（字节数）
        """
        # 清理类型名称
        clean_name = self._clean_type_name(type_name)
        
        # 处理指针类型
        if self.is_pointer_type(type_name):
            return 8  # 64位系统上指针大小为8字节
        
        # 获取实际类型
        real_type = self.get_real_type(clean_name)
        
        # 处理基本类型
        if real_type in self.BASIC_TYPES:
            return self.BASIC_TYPES[real_type]['size']
        
        # 处理结构体类型
        if self.is_struct_type(real_type):
            struct_info = self.get_struct_info(real_type)
            return struct_info.get('size', 0)
        
        # 处理联合体类型
        if self.is_union_type(real_type):
            union_info = self.get_union_info(real_type)
            return union_info.get('size', 0)
        
        # 处理枚举类型
        if self.is_enum_type(real_type):
            return 4  # 枚举类型默认大小为4字节
        
        return 0

    def get_type_alignment(self, type_name: str) -> int:
        """获取类型的对齐要求（字节数）
        
        Args:
            type_name: 类型名称
            
        Returns:
            类型对齐要求（字节数）
        """
        # 清理类型名称
        clean_name = self._clean_type_name(type_name)
        
        # 处理指针类型
        if self.is_pointer_type(type_name):
            return 8  # 64位系统上指针对齐为8字节
        
        # 获取实际类型
        real_type = self.get_real_type(clean_name)
        
        # 处理基本类型
        if real_type in self.BASIC_TYPES:
            return self.BASIC_TYPES[real_type]['alignment']
        
        # 处理结构体类型
        if self.is_struct_type(real_type):
            struct_info = self.get_struct_info(real_type)
            return struct_info.get('alignment', 0)
        
        # 处理联合体类型
        if self.is_union_type(real_type):
            union_info = self.get_union_info(real_type)
            return union_info.get('alignment', 0)
        
        # 处理枚举类型
        if self.is_enum_type(real_type):
            return 4  # 枚举类型默认对齐为4字节
        
        return 0

    def calculate_field_offset(self, type_name: str, field_name: str) -> int:
        """计算结构体字段的偏移量
        
        Args:
            type_name: 结构体类型名称
            field_name: 字段名称
            
        Returns:
            字段偏移量（字节数）
        """
        if not self.is_struct_type(type_name):
            return 0
        
        struct_info = self.get_struct_info(type_name)
        fields = struct_info.get('fields', [])
        
        current_offset = 0
        max_alignment = 1
        
        for field in fields:
            if not isinstance(field, dict):
                continue
            
            field_type = field.get('type', '')
            field_alignment = self.get_type_alignment(field_type)
            
            # 更新最大对齐要求
            max_alignment = max(max_alignment, field_alignment)
            
            # 计算当前字段的对齐后偏移量
            current_offset = (current_offset + field_alignment - 1) & ~(field_alignment - 1)
            
            # 如果找到目标字段，返回其偏移量
            if field.get('name') == field_name:
                return current_offset
            
            # 更新偏移量
            current_offset += self.get_type_size(field_type)
        
        return 0

    def get_field_info(self, type_name: str, field_name: str) -> Dict[str, Any]:
        """获取结构体或联合体字段的信息
        
        Args:
            type_name: 类型名称
            field_name: 字段名称
            
        Returns:
            字段信息字典
        """
        if self.is_struct_type(type_name):
            info = self.get_struct_info(type_name)
        elif self.is_union_type(type_name):
            info = self.get_union_info(type_name)
        else:
            return {}
        
        fields = info.get('fields', [])
        for field in fields:
            if isinstance(field, dict) and field.get('name') == field_name:
                field_info = field.copy()
                if self.is_struct_type(type_name):
                    field_info['offset'] = self.calculate_field_offset(type_name, field_name)
                else:
                    field_info['offset'] = 0  # 联合体所有字段偏移量都是0
                return field_info
        
        return {}

    def validate_type_info(self, type_info: Dict[str, Any]) -> bool:
        """验证类型信息是否有效
        
        Args:
            type_info: 要验证的类型信息
            
        Returns:
            如果类型信息有效返回True，否则返回False
        """
        try:
            # 检查必要字段
            required_fields = ['kind', 'name']
            if not all(field in type_info for field in required_fields):
                logger.warning(f"Missing required fields in type info: {required_fields}")
                return False
            
            kind = type_info.get('kind')
            
            # 验证结构体类型
            if kind == 'struct':
                if 'fields' not in type_info:
                    logger.warning("Missing fields in struct type info")
                    return False
                for field in type_info['fields']:
                    if not isinstance(field, dict) or 'name' not in field or 'type' not in field:
                        logger.warning(f"Invalid field in struct: {field}")
                        return False
                    
            # 验证联合体类型
            elif kind == 'union':
                if 'fields' not in type_info:
                    logger.warning("Missing fields in union type info")
                    return False
                for field in type_info['fields']:
                    if not isinstance(field, dict) or 'name' not in field or 'type' not in field:
                        logger.warning(f"Invalid field in union: {field}")
                        return False
                    
            # 验证枚举类型
            elif kind == 'enum':
                if 'values' not in type_info:
                    logger.warning("Missing values in enum type info")
                    return False
                if not isinstance(type_info['values'], dict):
                    logger.warning("Enum values must be a dictionary")
                    return False
                
            # 验证typedef类型
            elif kind == 'typedef':
                if 'base_type' not in type_info:
                    logger.warning("Missing base_type in typedef info")
                    return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating type info: {e}")
            return False

    def get_type_dependencies(self, type_name: str) -> Set[str]:
        """获取类型的所有依赖类型
        
        Args:
            type_name: 类型名称
            
        Returns:
            依赖类型名称的集合
        """
        dependencies = set()
        visited = {type_name}  # 防止循环依赖
        
        def collect_dependencies(current_type: str):
            # 获取实际类型
            real_type = self.get_real_type(current_type)
            
            # 如果是基本类型，不需要继续查找依赖
            if self.is_basic_type(real_type):
                return
            
            # 处理结构体类型
            if self.is_struct_type(real_type):
                struct_info = self.get_struct_info(real_type)
                for field in struct_info.get('fields', []):
                    if isinstance(field, dict):
                        field_type = field.get('type', '')
                        if field_type and field_type not in visited:
                            visited.add(field_type)
                            dependencies.add(field_type)
                            collect_dependencies(field_type)
                            
            # 处理联合体类型
            elif self.is_union_type(real_type):
                union_info = self.get_union_info(real_type)
                for field in union_info.get('fields', []):
                    if isinstance(field, dict):
                        field_type = field.get('type', '')
                        if field_type and field_type not in visited:
                            visited.add(field_type)
                            dependencies.add(field_type)
                            collect_dependencies(field_type)
                            
            # 处理typedef类型
            elif self.is_typedef_type(real_type):
                base_type = self._current_typedef_types.get(real_type) or self._global_typedef_types.get(real_type)
                if base_type and base_type not in visited:
                    visited.add(base_type)
                    dependencies.add(base_type)
                    collect_dependencies(base_type)
        
        collect_dependencies(type_name)
        return dependencies

    def get_type_hierarchy(self, type_name: str) -> Dict[str, Any]:
        """获取类型的层次结构
        
        Args:
            type_name: 类型名称
            
        Returns:
            包含类型层次结构的字典
        """
        visited = set()
        
        def build_hierarchy(current_type: str) -> Dict[str, Any]:
            if current_type in visited:
                return {'name': current_type, 'type': 'circular_reference'}
            
            visited.add(current_type)
            hierarchy = {'name': current_type}
            
            # 获取实际类型
            real_type = self.get_real_type(current_type)
            
            # 确定类型种类
            if self.is_basic_type(real_type):
                hierarchy['type'] = 'basic'
                if real_type in self.BASIC_TYPES:
                    hierarchy['info'] = self.BASIC_TYPES[real_type]
            elif self.is_struct_type(real_type):
                hierarchy['type'] = 'struct'
                hierarchy['fields'] = []
                struct_info = self.get_struct_info(real_type)
                for field in struct_info.get('fields', []):
                    if isinstance(field, dict):
                        field_type = field.get('type', '')
                        if field_type:
                            field_hierarchy = build_hierarchy(field_type)
                            field_hierarchy['field_name'] = field.get('name', '')
                            field_hierarchy['offset'] = self.calculate_field_offset(real_type, field.get('name', ''))
                            hierarchy['fields'].append(field_hierarchy)
            elif self.is_union_type(real_type):
                hierarchy['type'] = 'union'
                hierarchy['fields'] = []
                union_info = self.get_union_info(real_type)
                for field in union_info.get('fields', []):
                    if isinstance(field, dict):
                        field_type = field.get('type', '')
                        if field_type:
                            field_hierarchy = build_hierarchy(field_type)
                            field_hierarchy['field_name'] = field.get('name', '')
                            hierarchy['fields'].append(field_hierarchy)
            elif self.is_enum_type(real_type):
                hierarchy['type'] = 'enum'
                hierarchy['values'] = self.get_enum_values(real_type)
            elif self.is_pointer_type(real_type):
                hierarchy['type'] = 'pointer'
                base_type = real_type.rstrip('*')
                if base_type:
                    hierarchy['base_type'] = build_hierarchy(base_type)
            elif self.is_typedef_type(real_type):
                hierarchy['type'] = 'typedef'
                base_type = self._current_typedef_types.get(real_type) or self._global_typedef_types.get(real_type)
                if base_type:
                    hierarchy['base_type'] = build_hierarchy(base_type)
                
            visited.remove(current_type)
            return hierarchy
        
        return build_hierarchy(type_name)

    def get_type_size_info(self, type_name: str) -> Dict[str, Any]:
        """获取类型的大小相关信息
        
        Args:
            type_name: 类型名称
            
        Returns:
            包含类型大小信息的字典
        """
        return {
            'size': self.get_type_size(type_name),
            'alignment': self.get_type_alignment(type_name),
            'is_packed': self.is_packed_type(type_name)
        }

    def is_packed_type(self, type_name: str) -> bool:
        """检查类型是否是紧凑布局
        
        Args:
            type_name: 类型名称
            
        Returns:
            如果类型是紧凑布局返回True，否则返回False
        """
        type_info = self.get_type_details(type_name)
        return type_info.get('packed', False)

    def get_type_attributes(self, type_name: str) -> Dict[str, Any]:
        """获取类型的属性信息
        
        Args:
            type_name: 类型名称
            
        Returns:
            包含类型属性的字典
        """
        type_info = self.get_type_details(type_name)
        return type_info.get('attributes', {})

    def get_type_metadata(self, type_name: str) -> Dict[str, Any]:
        """获取类型的元数据
        
        Args:
            type_name: 类型名称
            
        Returns:
            包含类型元数据的字典
        """
        return {
            'category': self.get_type_category(type_name),
            'size_info': self.get_type_size_info(type_name),
            'attributes': self.get_type_attributes(type_name),
            'location': self.get_type_location(type_name),
            'comment': self.get_type_comment(type_name),
            'dependencies': list(self.get_type_dependencies(type_name))
        }

    def get_type_status(self, type_name: str) -> Dict[str, Any]:
        """获取类型的状态信息
        
        Args:
            type_name: 类型名称
            
        Returns:
            包含类型状态的字典
        """
        return {
            'is_complete': self.is_type_complete(type_name),
            'is_forward_declared': self.is_forward_declared(type_name),
            'is_defined': self.is_type_defined(type_name),
            'scope': self.get_type_scope(type_name)
        }

    def is_type_complete(self, type_name: str) -> bool:
        """检查类型是否完整定义
        
        Args:
            type_name: 类型名称
            
        Returns:
            如果类型完整定义返回True，否则返回False
        """
        if self.is_basic_type(type_name):
            return True
        
        type_info = self.get_type_details(type_name)
        if not type_info:
            return False
        
        # 检查结构体和联合体是否有字段定义
        if self.is_struct_type(type_name) or self.is_union_type(type_name):
            return bool(type_info.get('fields'))
        
        # 检查枚举是否有值定义
        if self.is_enum_type(type_name):
            return bool(type_info.get('values'))
        
        return True

    def is_forward_declared(self, type_name: str) -> bool:
        """检查类型是否是前向声明
        
        Args:
            type_name: 类型名称
            
        Returns:
            如果类型是前向声明返回True，否则返回False
        """
        if self.is_basic_type(type_name):
            return False
        
        type_info = self.get_type_details(type_name)
        return bool(type_info) and not self.is_type_complete(type_name)

    def is_type_defined(self, type_name: str) -> bool:
        """检查类型是否已定义
        
        Args:
            type_name: 类型名称
            
        Returns:
            如果类型已定义返回True，否则返回False
        """
        return (type_name in self.type_info or 
                type_name in self.BASIC_TYPES or 
                type_name in self.TYPE_ALIASES)

    def get_type_scope(self, type_name: str) -> str:
        """获取类型的作用域
        
        Args:
            type_name: 类型名称
            
        Returns:
            类型的作用域('global', 'file', 'unknown')
        """
        clean_name = self._clean_type_name(type_name)
        
        if (clean_name in self._global_typedef_types or
            clean_name in self._global_struct_types or
            clean_name in self._global_union_types or
            clean_name in self._global_enum_types):
            return 'global'
        
        if (clean_name in self._current_typedef_types or
            clean_name in self._current_struct_types or
            clean_name in self._current_union_types or
            clean_name in self._current_enum_types):
            return 'file'
        
        if clean_name in self.BASIC_TYPES or clean_name in self.TYPE_ALIASES:
            return 'global'
        
        return 'unknown'

    def get_type_summary(self, type_name: str) -> Dict[str, Any]:
        """获取类型的完整摘要信息
        
        Args:
            type_name: 类型名称
            
        Returns:
            包含类型完整信息的字典
        """
        return {
            'name': type_name,
            'category': self.get_type_category(type_name),
            'real_type': self.get_real_type(type_name),
            'size_info': self.get_type_size_info(type_name),
            'status': self.get_type_status(type_name),
            'metadata': self.get_type_metadata(type_name),
            'hierarchy': self.get_type_hierarchy(type_name),
            'dependencies': list(self.get_type_dependencies(type_name)),
            'details': self.get_type_details(type_name)
        }

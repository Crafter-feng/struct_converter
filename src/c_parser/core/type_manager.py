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
        # 统一类型存储
        self._global_types = []  # 全局类型列表
        self._global_pointer_types = set()
        self._global_macro_definitions = {}

        self._current_types = []  # 当前文件类型列表
        self._current_pointer_types = set()
        self._current_macro_definitions = {}
        
        # 初始化全局类型信息
        if type_info:
            self._load_type_info(type_info)
        
        # 更新类型别名映射
        if type_info and 'typedef_types' in type_info:
            for typedef in type_info['typedef_types']:
                if isinstance(typedef, dict) and 'name' in typedef and 'base_type' in typedef:
                    self.TYPE_ALIASES[typedef['name']] = typedef['base_type']
        elif type_info and 'types' in type_info:
            for type_def in type_info['types']:
                if isinstance(type_def, dict) and type_def.get('kind') == 'typedef' and 'name' in type_def and 'base_type' in type_def:
                    self.TYPE_ALIASES[type_def['name']] = type_def['base_type']

    @property
    def basic_types(self):
        """获取基本类型集合"""
        return self.BASIC_TYPES

    @property
    def struct_types(self):
        """获取所有结构体类型"""
        return [t for t in self._global_types + self._current_types if t.get('kind') == 'struct']

    @property
    def union_types(self):
        """获取所有联合体类型"""
        return [t for t in self._global_types + self._current_types if t.get('kind') == 'union']

    @property
    def enum_types(self):
        """获取所有枚举类型"""
        return [t for t in self._global_types + self._current_types if t.get('kind') == 'enum']

    @property
    def typedef_types(self):
        """获取所有类型别名"""
        return [t for t in self._global_types + self._current_types if t.get('kind') == 'typedef']

    def _load_type_info(self, type_info: Dict[str, Any]) -> None:
        """加载类型信息"""
        try:
            # 直接加载类型列表
            if 'types' in type_info:
                self._global_types.extend(type_info['types'])
            else:
                # 兼容旧格式，将不同种类的类型合并到统一列表
                if 'typedef_types' in type_info:
                    for typedef in type_info['typedef_types']:
                        if isinstance(typedef, dict):
                            typedef['kind'] = 'typedef'
                            self._global_types.append(typedef)
                
                if 'struct_types' in type_info:
                    for struct in type_info['struct_types']:
                        if isinstance(struct, dict):
                            struct['kind'] = 'struct'
                            self._global_types.append(struct)
                
                if 'union_types' in type_info:
                    for union in type_info['union_types']:
                        if isinstance(union, dict):
                            union['kind'] = 'union'
                            self._global_types.append(union)
                
                if 'enum_types' in type_info:
                    for enum in type_info['enum_types']:
                        if isinstance(enum, dict):
                            enum['kind'] = 'enum'
                            self._global_types.append(enum)
            
            # 处理指针类型和宏定义
            self._global_pointer_types.update(type_info.get('pointer_types', set()))
            self._global_macro_definitions.update(type_info.get('macro_definitions', {}))

        except Exception as e:
            logger.error(f"Failed to load type info: {e}")
            raise

    def add_macro_definition(self, name: str, value: Any) -> None:
        """添加宏定义
        
        Args:
            name: 宏名称
            value: 宏值
        """
        self._current_macro_definitions[name] = value

    def export_types(self, scope: str = 'all'):
        """导出所有类型信息
        
        Args:
            scope: 导出范围，可选值为 'all'/'global'/'current'
            
        Returns:
            包含类型信息的字典
        """
        # 根据参数选择要导出的类型
        if scope == 'current':
            all_types = self._current_types
            pointer_types = list(self._current_pointer_types)
            macro_definitions = self._current_macro_definitions.copy()
        elif scope == 'global':
            all_types = self._global_types
            pointer_types = list(self._global_pointer_types)
            macro_definitions = self._global_macro_definitions.copy()
        elif scope == 'all':
            # 合并全局和当前文件的类型
            all_types = self._global_types + self._current_types
            # 合并指针类型
            pointer_types = list(self._global_pointer_types.union(self._current_pointer_types))
            # 合并宏定义
            macro_definitions = self._global_macro_definitions.copy()
            macro_definitions.update(self._current_macro_definitions)
        else:
            logger.warning(f"Invalid scope '{scope}', using 'all' instead")
            return self.export_types(scope='all')
        
        return {
            'types': all_types,
            'pointer_types': pointer_types,
            'macro_definitions': macro_definitions
        }

    def export_type_info(self, scope: str = 'all'):
        """导出所有类型信息（按类型分类）
        
        Args:
            scope: 导出范围，可选值为 'all'/'global'/'current'
            
        Returns:
            包含分类后类型信息的字典
        """
        # 根据参数选择要导出的类型
        if scope == 'current':
            export_types = self._current_types
            pointer_types = list(self._current_pointer_types)
            macro_definitions = self._current_macro_definitions.copy()
        elif scope == 'global':
            export_types = self._global_types
            pointer_types = list(self._global_pointer_types)
            macro_definitions = self._global_macro_definitions.copy()
        elif scope == 'all':
            # 合并全局和当前文件的类型
            export_types = self._global_types + self._current_types
            # 合并指针类型
            pointer_types = list(self._global_pointer_types.union(self._current_pointer_types))
            # 合并宏定义
            macro_definitions = self._global_macro_definitions.copy()
            macro_definitions.update(self._current_macro_definitions)
        else:
            logger.warning(f"Invalid scope '{scope}', using 'all' instead")
            return self.export_type_info(scope='all')
        
        # 按类型分类
        typedef_types = [t for t in export_types if t.get('kind') == 'typedef']
        struct_types = [t for t in export_types if t.get('kind') == 'struct']
        union_types = [t for t in export_types if t.get('kind') == 'union']
        enum_types = [t for t in export_types if t.get('kind') == 'enum']
        
        return {
            'typedef_types': typedef_types,
            'struct_types': struct_types,
            'union_types': union_types,
            'enum_types': enum_types,
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
            for typedef in type_info['typedef_types']:
                if isinstance(typedef, dict) and 'name' in typedef and 'base_type' in typedef:
                    self.TYPE_ALIASES[typedef['name']] = typedef['base_type']

    def reset_type_info(self):
        """重置所有类型信息（包括全局和当前文件）"""
        # 重置统一存储
        self._global_types = []
        self._current_types = []
        self._global_pointer_types = set()
        self._global_macro_definitions = {}
        self._current_pointer_types = set()
        self._current_macro_definitions = {}

    def get_struct_info(self, struct_name: str = None) -> Dict[str, Any]:
        """获取结构体信息"""
        if struct_name:
            # 使用JSONPath查询
            query = f"$[?(@.kind=='struct' && @.name=='{struct_name}')]"
            results = self.find_types_by_jsonpath(query)
            return results[0] if results else {}
        else:
            # 返回所有结构体
            return self.find_types_by_jsonpath("$[?(@.kind=='struct')]")
    
    def get_union_info(self, union_name: str = None) -> Dict[str, Any]:
        """获取联合体信息"""
        if union_name:
            # 使用JSONPath查询
            query = f"$[?(@.kind=='union' && @.name=='{union_name}')]"
            results = self.find_types_by_jsonpath(query)
            return results[0] if results else {}
        else:
            # 返回所有联合体
            return self.find_types_by_jsonpath("$[?(@.kind=='union')]")
    
    def get_enum_info(self, enum_name: str = None) -> Dict[str, Any]:
        """获取枚举信息"""
        if enum_name:
            # 使用JSONPath查询
            query = f"$[?(@.kind=='enum' && @.name=='{enum_name}')]"
            results = self.find_types_by_jsonpath(query)
            return results[0] if results else {}
        else:
            # 合并全局和当前文件的信息
            enums = self.find_types_by_jsonpath("$[?(@.kind=='enum')]")
            merged_values = {}
            for enum in enums:
                if isinstance(enum, dict):
                    name = enum.get('name')
                    if name:
                        merged_values[name] = enum.get('values', {})
            return merged_values
         
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
        
        # 先检查是否是基本类型
        if clean_name in self.BASIC_TYPES:
            return True
        
        # 检查类型别名，并递归检查其实际类型
        real_type = self.get_real_type(clean_name)
        if real_type != clean_name:
            return self.is_basic_type(real_type)
            
        return False
        
    def is_struct_type(self, type_name: str) -> bool:
        """判断是否为结构体类型"""
        # 处理 'struct X' 形式
        if type_name.startswith('struct '):
            return True
        
        # 清理类型名称
        clean_name = self._clean_type_name(type_name)
        
        # 使用新的统一存储方式查找
        if any(t.get('kind') == 'struct' and t.get('name') == clean_name 
               for t in self._current_types + self._global_types):
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
        
        # 使用新的统一存储方式查找
        if any(t.get('kind') == 'union' and t.get('name') == clean_name 
               for t in self._current_types + self._global_types):
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
        
        # 使用新的统一存储方式查找
        if any(t.get('kind') == 'enum' and t.get('name') == clean_name 
               for t in self._current_types + self._global_types):
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
        
        # 使用新的统一存储方式查找
        # 优先检查当前文件的类型别名
        for typedef in self._current_types:
            if typedef.get('kind') == 'typedef' and typedef.get('name') == type_name:
                base_type = typedef.get('base_type', '')
                if base_type != type_name:  # 避免自引用
                    return self.get_real_type(base_type, visited)
        
        # 然后检查全局类型别名
        for typedef in self._global_types:
            if typedef.get('kind') == 'typedef' and typedef.get('name') == type_name:
                base_type = typedef.get('base_type', '')
                if base_type != type_name:  # 避免自引用
                    return self.get_real_type(base_type, visited)
            
        return type_name
    
    def _clean_type_name(self, type_name: str) -> str:
        """清理类型名称，移除前缀和修饰符"""
        logger.debug(f"Cleaning type name: {type_name}")
        
        if isinstance(type_name, dict):
            type_name = type_name.get('base_type', '')
            logger.debug(f"Extracted base_type from dict: {type_name}")
        
        # 移除 struct/union/enum 前缀和指针符号
        clean_name = type_name.replace('struct ', '').replace('union ', '').replace('enum ', '')
        logger.debug(f"After removing prefixes: {clean_name}")
        
        # 不要移除指针符号，因为它们在类型兼容性检查中很重要
        # clean_name = clean_name.rstrip('*')
        
        result = clean_name.strip()
        logger.debug(f"Final cleaned name: {result}")
        return result
    
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
        """导出全局类型信息"""
        return {
            'types': self._global_types,
            'pointer_types': list(self._global_pointer_types),
            'macro_definitions': self._global_macro_definitions
        }

    def export_current_type_info(self) -> Dict[str, Any]:
        """导出当前文件的类型信息"""
        return {
            'types': self._current_types,
            'pointer_types': list(self._current_pointer_types),
            'macro_definitions': self._current_macro_definitions
        }

    def reset_current_type_info(self) -> None:
        """重置当前文件的类型信息"""
        # 重置统一存储
        self._current_types = []
        self._current_pointer_types = set()
        self._current_macro_definitions = {}

    def is_typedef_type(self, type_name: str) -> bool:
        """检查是否是typedef类型"""
        clean_name = self._clean_type_name(type_name)
        
        # 使用新的统一存储方式查找
        return any(t.get('kind') == 'typedef' and t.get('name') == clean_name 
                  for t in self._current_types + self._global_types)

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
            target_types = self._global_types if to_global else self._current_types
            target_pointer_types = self._global_pointer_types if to_global else self._current_pointer_types
            target_macro_definitions = self._global_macro_definitions if to_global else self._current_macro_definitions
            
            # 处理统一格式的类型列表
            for type_info in other_type_info.get('types', {}):
                if isinstance(type_info, dict) and 'kind' in type_info and 'name' in type_info:
                    # 检查是否已存在同名类型
                    existing_type = next((t for t in target_types if t.get('name') == type_info['name']), None)
                    if existing_type:
                        # 更新现有类型
                        existing_type.update(type_info)
                    else:
                        # 添加新类型
                        target_types.append(type_info)
            
            # 处理指针类型
            pointer_types_data = other_type_info.get('pointer_types', set())
            if isinstance(pointer_types_data, list):
                target_pointer_types.update(set(pointer_types_data))
            else:
                target_pointer_types.update(pointer_types_data)
            
            # 合并宏定义
            target_macro_definitions.update(other_type_info.get('macro_definitions', {}))

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
        """检查两个类型是否兼容"""
        logger.debug(f"\n=== Checking type compatibility ===")
        logger.debug(f"Type1: {type1}")
        logger.debug(f"Type2: {type2}")
        
        # 清理类型名称
        type1 = self._clean_type_name(type1)
        type2 = self._clean_type_name(type2)
        logger.debug(f"Cleaned types - Type1: {type1}, Type2: {type2}")
        
        # 处理指针类型
        if '*' in type1 or '*' in type2:
            logger.debug("Processing pointer types")
            
            # 检查是否都是指针类型
            if '*' not in type1 or '*' not in type2:
                logger.debug("One type is not pointer - incompatible")
                return False
            
            # 获取指针级别
            ptr_level1 = type1.count('*')
            ptr_level2 = type2.count('*')
            logger.debug(f"Pointer levels - Type1: {ptr_level1}, Type2: {ptr_level2}")
            
            if ptr_level1 != ptr_level2:
                logger.debug("Different pointer levels - incompatible")
                return False
            
            # 获取基本类型（去掉所有指针）
            base1 = type1.rstrip('*')
            base2 = type2.rstrip('*')
            logger.debug(f"Base types - Type1: {base1}, Type2: {base2}")
            
            # 获取实际类型（解析类型别名）
            real_base1 = self.get_real_type(base1)
            real_base2 = self.get_real_type(base2)
            logger.debug(f"Real base types - Type1: {real_base1}, Type2: {real_base2}")
            
            # void* 可以与任何指针类型兼容
            # 注意：这里需要检查原始类型和解析后的类型
            if ('void' in (base1, base2) or 
                'void' in (real_base1, real_base2)):
                logger.debug("void* compatibility check passed")
                return True
            
            # 检查基本类型是否兼容
            if real_base1 in self.BASIC_TYPES and real_base2 in self.BASIC_TYPES:
                logger.debug("Checking basic type compatibility")
                type1_info = self.BASIC_TYPES[real_base1]
                type2_info = self.BASIC_TYPES[real_base2]
                result = (type1_info['size'] == type2_info['size'] and 
                         type1_info.get('signed') == type2_info.get('signed'))
                logger.debug(f"Basic type compatibility result: {result}")
                return result
            
            # 其他情况，类型必须完全相同
            result = real_base1 == real_base2
            logger.debug(f"Type equality check result: {result}")
            return result
        
        # 非指针类型的处理
        logger.debug("Processing non-pointer types")
        real_type1 = self.get_real_type(type1)
        real_type2 = self.get_real_type(type2)
        logger.debug(f"Real types - Type1: {real_type1}, Type2: {real_type2}")
        
        # 处理基本类型
        if real_type1 in self.BASIC_TYPES and real_type2 in self.BASIC_TYPES:
            logger.debug("Checking basic type compatibility")
            type1_info = self.BASIC_TYPES[real_type1]
            type2_info = self.BASIC_TYPES[real_type2]
            result = (type1_info['size'] == type2_info['size'] and 
                     type1_info.get('signed') == type2_info.get('signed'))
            logger.debug(f"Basic type compatibility result: {result}")
            return result
        
        # 其他情况，类型必须完全相同
        result = real_type1 == real_type2
        logger.debug(f"Final type equality check result: {result}")
        return result

    def get_enum_values(self, enum_name: str = None) -> Dict[str, Any]:
        """获取枚举值信息"""
        if enum_name:
            # 使用简单查询
            query = f"$[?(@.kind=='enum')]"
            enums = self.find_types_by_jsonpath(query)
            # 手动过滤
            filtered = [e for e in enums if e.get('name') == enum_name]
            if filtered and 'values' in filtered[0]:
                return {enum_name: filtered[0]['values']}
            return {}
        else:
            # 使用简单查询
            query = f"$[?(@.kind=='enum')]"
            enums = self.find_types_by_jsonpath(query)
            # 手动过滤有效的枚举
            merged_values = {}
            for enum in enums:
                if isinstance(enum, dict) and 'name' in enum and enum['name'] and 'values' in enum:
                    merged_values[enum['name']] = enum['values']
            return merged_values

    def get_enum_value(self, enum_name: str, value_name: str) -> Optional[Any]:
        """获取枚举值"""
        # 使用简单查询
        query = f"$[?(@.kind=='enum')]"
        enums = self.find_types_by_jsonpath(query)
        # 手动过滤
        for enum in enums:
            if enum.get('name') == enum_name and 'values' in enum and value_name in enum['values']:
                return enum['values'][value_name]
        return None

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
        # 确保类型信息包含名称
        if 'name' not in info:
            info['name'] = name
            
        # 添加到统一存储
        self._current_types.append(info)
        
        # 处理指针类型
        kind = info.get('kind', '')
        if kind == 'typedef' and info.get('type', '').endswith('*'):
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
        # 首先确定类型种类
        if self.is_struct_type(type_name):
            kind = 'struct'
        elif self.is_union_type(type_name):
            kind = 'union'
        else:
            return {}
        
        # 清理类型名称
        clean_name = self._clean_type_name(type_name)
        
        # 简化查询，避免复杂嵌套
        query = "$[?(@.kind=='" + kind + "' && @.name=='" + clean_name + "')]"
        results = self.find_types_by_jsonpath(query)
        
        if results and 'fields' in results[0]:
            # 手动查找字段
            for field in results[0]['fields']:
                if isinstance(field, dict) and field.get('name') == field_name:
                    field_info = field.copy()
                    if kind == 'struct':
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
            
            # 查找类型信息
            type_info = self.find_type_by_name(real_type)
            if not type_info:
                return
                
            # 处理结构体和联合体类型
            if type_info.get('kind') in ('struct', 'union'):
                for field in type_info.get('fields', []):
                    if isinstance(field, dict):
                        field_type = field.get('type', '')
                        if field_type and field_type not in visited:
                            visited.add(field_type)
                            dependencies.add(field_type)
                            collect_dependencies(field_type)
                            
            # 处理typedef类型
            elif type_info.get('kind') == 'typedef':
                base_type = type_info.get('base_type', '')
                if base_type and base_type not in visited:
                    visited.add(base_type)
                    dependencies.add(base_type)
                    collect_dependencies(base_type)
        
        collect_dependencies(type_name)
        return dependencies

    def get_type_hierarchy(self, type_name: str) -> Dict[str, Any]:
        """获取类型的层次结构"""
        visited = set()
        
        def build_hierarchy(current_type: str) -> Dict[str, Any]:
            if current_type in visited:
                return {'name': current_type, 'type': 'circular_reference'}
            
            visited.add(current_type)
            hierarchy = {'name': current_type}
            
            # 处理指针类型
            if self.is_pointer_type(current_type):
                hierarchy['type'] = 'pointer'
                base_type = current_type.rstrip('*')
                if base_type and base_type not in visited:
                    hierarchy['base_type'] = build_hierarchy(base_type)
                return hierarchy
            
            # 获取实际类型
            real_type = self.get_real_type(current_type)
            
            # 查找类型信息
            type_info = self.find_type_by_name(real_type)
            
            # 确定类型种类
            if self.is_basic_type(real_type):
                hierarchy['type'] = 'basic'
            elif type_info:
                kind = type_info.get('kind', '')
                hierarchy['type'] = kind
                
                if kind in ('struct', 'union'):
                    hierarchy['fields'] = []
                    for field in type_info.get('fields', []):
                        if isinstance(field, dict):
                            field_type = field.get('type', '')
                            if field_type and field_type not in visited:
                                field_hierarchy = build_hierarchy(field_type)
                                field_hierarchy['field_name'] = field.get('name', '')
                                hierarchy['fields'].append(field_hierarchy)
                elif kind == 'typedef':
                    base_type = type_info.get('base_type', '')
                    if base_type and base_type not in visited:
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
        """获取类型的属性信息"""
        # 获取类型信息
        type_info = None
        if self.is_struct_type(type_name):
            type_info = self.get_struct_info(type_name)
        elif self.is_union_type(type_name):
            type_info = self.get_union_info(type_name)
        elif type_name in self.type_info:
            type_info = self.type_info[type_name]
        
        if not type_info:
            return {}
        
        # 合并所有属性
        attributes = {}
        # 从 attributes 字段获取
        attributes.update(type_info.get('attributes', {}))
        # 从 details 字段获取
        details = type_info.get('details', {})
        if details:
            attributes.update({
                'packed': details.get('packed', False),
                'alignment': details.get('alignment'),
                'visibility': details.get('visibility')
            })
        # 从类型信息直接获取
        if 'packed' in type_info:
            attributes['packed'] = type_info['packed']
        
        return attributes

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
        clean_name = self._clean_type_name(type_name)
        
        return (any(t.get('name') == clean_name for t in self._global_types) or
                any(t.get('name') == clean_name for t in self._current_types) or
                clean_name in self.BASIC_TYPES or 
                clean_name in self.TYPE_ALIASES)

    def get_type_scope(self, type_name: str) -> str:
        """获取类型的作用域
        
        Args:
            type_name: 类型名称
            
        Returns:
            类型的作用域('global', 'file', 'unknown')
        """
        clean_name = self._clean_type_name(type_name)
        
        # 检查全局作用域
        if any(t.get('name') == clean_name for t in self._global_types):
            return 'global'
        
        # 检查文件作用域
        if any(t.get('name') == clean_name for t in self._current_types):
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
        # 查找类型信息
        type_info = self.find_type_by_name(type_name)
        
        # 如果是基本类型
        if self.is_basic_type(type_name):
            real_type = self.get_real_type(type_name)
            basic_info = self.BASIC_TYPES.get(real_type, {})
            return {
                'name': type_name,
                'kind': 'basic',
                'real_type': real_type,
                'size': basic_info.get('size', 0),
                'alignment': basic_info.get('alignment', 0),
                'signed': basic_info.get('signed', False),
                'status': {
                    'is_complete': True,
                    'is_defined': True,
                    'scope': 'global'
                }
            }
        
        # 如果找到类型信息
        if type_info:
            return {
                'name': type_name,
                'kind': type_info.get('kind', 'unknown'),
                'real_type': self.get_real_type(type_name),
                'size': self.get_type_size(type_name),
                'alignment': self.get_type_alignment(type_name),
                'status': self.get_type_status(type_name),
                'fields': type_info.get('fields', []),
                'values': type_info.get('values', {}),
                'attributes': type_info.get('attributes', {}),
                'comment': type_info.get('comment', ''),
                'location': type_info.get('location', {})
            }
        
        # 如果未找到类型信息
        return {
            'name': type_name,
            'kind': 'unknown',
            'real_type': self.get_real_type(type_name),
            'status': {
                'is_complete': False,
                'is_defined': False,
                'scope': 'unknown'
            }
        }

    def find_types_by_jsonpath(self, query: str, scope: str = 'all') -> List[Dict[str, Any]]:
        """使用jsonpath查询类型
        
        Args:
            query: jsonpath查询表达式
            scope: 查询范围，'all'/'global'/'current'
            
        Returns:
            匹配的类型列表
        """
        try:
            import jsonpath_ng.ext as jsonpath
            
            # 准备数据源
            if scope == 'current':
                data_source = self._current_types
            elif scope == 'global':
                data_source = self._global_types
            elif scope == 'all':
                data_source = self._global_types + self._current_types
            else:
                logger.warning(f"Invalid scope '{scope}', using 'all' instead")
                data_source = self._global_types + self._current_types
            
            # 处理复杂查询 - 分解为简单查询
            if '&&' in query:
                # 分解为单独的条件
                conditions = query.split('&&')
                base_query = conditions[0].strip()
                if base_query.endswith('[?'):
                    base_query = base_query + '(@)]'
                elif not base_query.endswith(')]'):
                    base_query = base_query + ')]'
                
                # 执行基础查询
                jsonpath_expr = jsonpath.parse(base_query)
                results = [match.value for match in jsonpath_expr.find(data_source)]
                
                # 手动应用其他条件
                for condition in conditions[1:]:
                    condition = condition.strip()
                    if condition.startswith('('):
                        condition = condition[1:]
                    if condition.endswith(')]'):
                        condition = condition[:-2]
                    
                    # 解析条件
                    if '==' in condition:
                        key, value = condition.split('==')
                        key = key.strip()
                        value = value.strip().strip("'")
                        
                        # 处理嵌套属性
                        if '.' in key:
                            parts = key.split('.')
                            results = [r for r in results if self._check_nested_attribute(r, parts, value)]
                        else:
                            key = key.replace('@.', '')
                            results = [r for r in results if key in r and r[key] == value]
                    elif '!=' in condition:
                        key, value = condition.split('!=')
                        key = key.strip()
                        value = value.strip()
                        
                        if value == 'null':
                            # 检查属性存在且不为None
                            key = key.replace('@.', '')
                            results = [r for r in results if key in r and r[key] is not None]
                        else:
                            value = value.strip("'")
                            # 处理嵌套属性
                            if '.' in key:
                                parts = key.split('.')
                                results = [r for r in results if not self._check_nested_attribute(r, parts, value)]
                            else:
                                key = key.replace('@.', '')
                                results = [r for r in results if key in r and r[key] != value]
                
                return results
            else:
                # 简单查询直接执行
                jsonpath_expr = jsonpath.parse(query)
                return [match.value for match in jsonpath_expr.find(data_source)]
            
        except ImportError:
            logger.error("jsonpath_ng module not found. Please install it with: pip install jsonpath-ng")
            return []
        except Exception as e:
            logger.error(f"Error in find_types_by_jsonpath with query '{query}': {e}")
            # 尝试使用更简单的方法
            return self._fallback_find(query, scope)

    def _check_nested_attribute(self, obj: Dict, attr_path: List[str], value: Any) -> bool:
        """检查嵌套属性是否匹配指定值"""
        current = obj
        for part in attr_path:
            part = part.replace('@.', '')
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False
        return current == value

    def _fallback_find(self, query: str, scope: str) -> List[Dict[str, Any]]:
        """当JSONPath查询失败时的备用查找方法"""
        logger.info(f"Using fallback find for query: {query}")
        
        # 获取数据源
        if scope == 'current':
            data_source = self._current_types
        elif scope == 'global':
            data_source = self._global_types
        else:
            data_source = self._global_types + self._current_types
        
        # 解析简单查询
        if query.startswith("$[?(@.kind==") and query.endswith(")]"):
            # 修复语法错误：正确提取kind值
            kind_part = query.split("==")[1]
            if "'" in kind_part:
                kind = kind_part.split("'")[1]
            else:
                kind = kind_part.strip(")]")
            return [t for t in data_source if t.get('kind') == kind]
        
        # 默认返回所有类型
        return data_source

    def find_type_by_name(self, name: str, kind: str = None) -> Optional[Dict[str, Any]]:
        """查找指定名称和类型的类型定义
        
        Args:
            name: 类型名称
            kind: 类型种类，可以是'typedef'/'struct'/'union'/'enum'，如果为None则查找任何类型
            
        Returns:
            找到的类型信息，如果未找到则返回None
        """
        clean_name = self._clean_type_name(name)
        
        # 构建JSONPath查询
        if kind:
            query = f"$[?(@.name=='{clean_name}' && @.kind=='{kind}')]"
        else:
            query = f"$[?(@.name=='{clean_name}')]"
        
        # 优先查找当前文件
        results = self.find_types_by_jsonpath(query, scope='current')
        if results:
            return results[0]
        
        # 然后查找全局定义
        results = self.find_types_by_jsonpath(query, scope='global')
        if results:
            return results[0]
        
        return None

    # 添加新的便捷查询方法
    def find_types_by_kind(self, kind: str, scope: str = 'all') -> List[Dict[str, Any]]:
        """查找指定类型的所有类型定义
        
        Args:
            kind: 类型种类，可以是'typedef'/'struct'/'union'/'enum'
            scope: 查询范围，'all'/'global'/'current'
            
        Returns:
            匹配的类型列表
        """
        query = f"$[?(@.kind=='{kind}')]"
        return self.find_types_by_jsonpath(query, scope=scope)

    def find_types_by_attribute(self, attribute_name: str, attribute_value: Any = None, scope: str = 'all') -> List[Dict[str, Any]]:
        """查找具有指定属性的所有类型定义
        
        Args:
            attribute_name: 属性名称
            attribute_value: 属性值，如果为None则只检查属性是否存在
            scope: 查询范围，'all'/'global'/'current'
            
        Returns:
            匹配的类型列表
        """
        if attribute_value is None:
            query = f"$[?(@.attributes && @.attributes.{attribute_name})]"
        else:
            # 处理不同类型的属性值
            if isinstance(attribute_value, str):
                query = f"$[?(@.attributes && @.attributes.{attribute_name}=='{attribute_value}')]"
            elif isinstance(attribute_value, bool):
                value_str = 'true' if attribute_value else 'false'
                query = f"$[?(@.attributes && @.attributes.{attribute_name}=={value_str})]"
            else:
                query = f"$[?(@.attributes && @.attributes.{attribute_name}=={attribute_value})]"
        
        return self.find_types_by_jsonpath(query, scope=scope)

    def find_types_by_field(self, field_name: str, field_type: str = None, scope: str = 'all') -> List[Dict[str, Any]]:
        """查找包含指定字段的所有结构体或联合体
        
        Args:
            field_name: 字段名称
            field_type: 字段类型，如果为None则只检查字段名称
            scope: 查询范围，'all'/'global'/'current'
            
        Returns:
            匹配的类型列表
        """
        # 修复查询语法，使用更简单的表达式避免复杂嵌套
        if field_type:
            # 由于JSONPath的复杂性，这里分两步进行查询
            query = "$[?(@.kind=='struct' || @.kind=='union')]"
            results = self.find_types_by_jsonpath(query, scope=scope)
            # 手动过滤结果
            return [t for t in results if 'fields' in t and 
                    any(f.get('name') == field_name and f.get('type') == field_type 
                        for f in t['fields'] if isinstance(f, dict))]
        else:
            query = "$[?(@.kind=='struct' || @.kind=='union')]"
            results = self.find_types_by_jsonpath(query, scope=scope)
            # 手动过滤结果
            return [t for t in results if 'fields' in t and 
                    any(f.get('name') == field_name for f in t['fields'] if isinstance(f, dict))]

    def find_types_by_size(self, size: int, scope: str = 'all') -> List[Dict[str, Any]]:
        """查找指定大小的所有类型
        
        Args:
            size: 类型大小（字节数）
            scope: 查询范围，'all'/'global'/'current'
            
        Returns:
            匹配的类型列表
        """
        query = f"$[?(@.size=={size})]"
        results = self.find_types_by_jsonpath(query, scope=scope)
        
        # 检查基本类型
        if scope == 'all' or scope == 'global':
            for type_name, type_info in self.BASIC_TYPES.items():
                if type_info.get('size') == size:
                    results.append({
                        'kind': 'basic',
                        'name': type_name,
                        'size': size,
                        'alignment': type_info.get('alignment'),
                        'signed': type_info.get('signed')
                    })
        
        return results

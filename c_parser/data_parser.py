import json
from typing import Any, Dict, Optional
from utils.logger_config import setup_logger
from utils import TreeSitterUtil
from utils import ExpressionParser
from .type_parser import CTypeParser

logger = setup_logger('DataParser')

class CDataParser:
    """C语言数据解析器，负责解析C源文件中的变量定义和初始化数据"""
    
    def __init__(self, type_info):
        """初始化数据解析器"""
        logger.info("Initializing CDataParser")
        self.ts_util = TreeSitterUtil()

        self.type_resolver = None        
        # 初始化类型解析器
        self.type_parser = CTypeParser()
        
        self.global_types = type_info

        # 当前文件的类型定义
        self.current_types = {
            'typedef_types': {},
            'struct_types': set(),
            'union_types': set(),
            'pointer_types': {},
            'struct_info': {},
            'union_info': {},
            'enum_types': {},
            'macro_definitions': {}
        }
    
    def _print_type_definitions(self):
        """打印所有可用的类型定义"""
        logger.info("\n=== Available Type Definitions ===")
        
        # 打印结构体定义
        if self.type_info.get('struct_info'):
            logger.info("\nStruct Definitions:")
            for struct_name, struct_info in self.type_info['struct_info'].items():
                logger.info(f"struct {struct_name} {{")
                for field in struct_info.get('fields', []):
                    type_str = field.get('type', 'unknown')
                    if field.get('is_pointer'):
                        type_str += '*'
                    name = field.get('name', 'unnamed')
                    array_size = field.get('array_size')
                    if array_size:
                        if isinstance(array_size, list):
                            dims = ']['.join(str(dim) for dim in array_size)
                            name += f"[{dims}]"
                        else:
                            name += f"[{array_size}]"
                    logger.info(f"    {type_str} {name};")
                logger.info("};")
        
        # 打印联合体定义
        if self.type_info.get('union_info'):
            logger.info("\nUnion Definitions:")
            for union_name, union_info in self.type_info['union_info'].items():
                logger.info(f"union {union_name} {{")
                for field in union_info.get('fields', []):
                    type_str = field.get('type', 'unknown')
                    if field.get('is_pointer'):
                        type_str += '*'
                    name = field.get('name', 'unnamed')
                    array_size = field.get('array_size')
                    if array_size:
                        if isinstance(array_size, list):
                            dims = ']['.join(str(dim) for dim in array_size)
                            name += f"[{dims}]"
                        else:
                            name += f"[{array_size}]"
                    logger.info(f"    {type_str} {name};")
                logger.info("};")
        
        # 打印类型定义
        if self.type_info.get('typedef_types'):
            logger.info("\nTypedef Definitions:")
            for typedef_name, typedef_type in self.type_info['typedef_types'].items():
                logger.info(f"typedef {typedef_type} {typedef_name};")
        
        # 打印枚举定义
        if self.type_info.get('enum_types'):
            logger.info("\nEnum Definitions:")
            for enum_name, enum_values in self.type_info['enum_types'].items():
                logger.info(f"enum {enum_name} {{")
                for name, value in enum_values.items():
                    logger.info(f"    {name} = {value},")
                logger.info("};")
        
        logger.info("\n=== End of Type Definitions ===\n")
    
    def parse_global_variables(self, source_file):
        """解析C源文件中的全局变量定义和初始化数据
        
        此函数会解析C源文件中的全局变量定义，包括:
        - 基本类型变量
        - 结构体变量
        - 数组变量
        - 指针变量
        
        Args:
            source_file (str): C源文件路径
            
        Returns:
            dict: 解析结果，包含以下内容：
                {
                    'types': {
                        'struct_info': dict,    # 结构体类型信息
                        'typedef_types': dict,  # 类型定义信息
                        'enum_types': dict,     # 枚举类型信息
                        'macro_definitions': dict # 宏定义信息
                    },
                    'variables': {
                        'variables': list,      # 基本类型变量列表
                        'struct_vars': list,    # 结构体变量列表
                        'pointer_vars': list,   # 指针变量列表
                        'array_vars': list      # 数组变量列表
                    }
                }
        
        Raises:
            ValueError: 当遇到未定义的类型时抛出异常
        """
        logger.info(f"Parsing global variables from file: {source_file}")
        
        # 使用TreeSitterUtil解析文件
        tree = self.ts_util.parse_file(source_file)
        
        # 第一步：解析当前文件的类型定义
        logger.info("Step 1: Parsing type definitions")
        self._parse_current_file_types(tree)
        
        # 第二步：解析变量定义
        logger.info("Step 2: Parsing variable definitions")
        variable_definitions = {}
        self._collect_variable_definitions(tree.root_node, variable_definitions)
        
        # 第三步：对变量进行分类
        logger.info("Step 3: Categorizing variables")
        var_info = self._categorize_variables(variable_definitions)
        
        # 返回解析结果
        result = {
            'types': {
                'struct_info': self.current_types['struct_info'],
                'typedef_types': self.current_types['typedef_types'],
                'enum_types': self.current_types['enum_types'],
                'macro_definitions': self.current_types['macro_definitions']
            },
            'variables': var_info
        }
        
        logger.info("Parsing completed successfully")
        return result
    
    def _parse_current_file_types(self, tree):
        """解析当前文件中的类型定义"""
        # 使用CTypeParser解析当前文件的类型定义
        type_info = self.type_parser.parse_declarations(tree=tree)
        
        # 更新当前文件的类型信息
        self.current_types.update(type_info)

        all_types = {
            'typedef_types': self.current_types['typedef_types'],
            'struct_types': self.current_types['struct_types'],
            'union_types': self.current_types['union_types'],
            'pointer_types': self.current_types['pointer_types'],
            'struct_info': self.current_types['struct_info'],
            'union_info': self.current_types['union_info'],
            'enum_types': self.current_types['enum_types'],
            'macro_definitions': self.current_types['macro_definitions']
        }

        for k,v in self.global_types.items():
            if k in all_types:
                all_types.update({k:v})
            else:
                all_types[k] = v

        # 同时更新全局类型信息
        self.type_resolver = TypeResolver(all_types)

        # 创建值解析器
        self.value_parser = ValueParser(self.type_resolver)
    
    def _collect_variable_definitions(self, node, variable_definitions):
        """收集所有变量定义"""
        if node.type == 'declaration':
            var_data = self._process_declaration(node)
            if var_data and var_data.get('name'):
                variable_definitions[var_data['name']] = var_data
                logger.debug(f"Collected variable definition: {var_data['name']}")
        
        for child in node.children:
            self._collect_variable_definitions(child, variable_definitions)
    
    def _process_declaration(self, node):
        """处理变量声明节点"""
        # 首先检查是否是全局变量或 extern 声明
        if not self._is_global_declaration(node) or self._is_extern_declaration(node):
            logger.debug("Skipping non-global or extern declaration")
            return None
            
        # 提取类型信息
        type_info = self._extract_type_info(node)
        type_name = type_info['type']
        original_type = type_info['original_type']
        
        # 初始化变量数据
        var_data = {
            "name": None,
            "type": type_name,
            "original_type": original_type,
            "array_size": None,
            "is_pointer": False,
            "pointer_level": 0
        }
        
        # 提取声明器信息（变量名、数组、指针等）
        declarator = self._extract_declaration_before_equals(node)
        if declarator:
            declarator_info = self._extract_declarator_info(declarator)
            logger.debug(f"Declarator info: {json.dumps(declarator_info, indent=2)}")
            var_data.update(declarator_info)
            
            # 如果是指针，更新类型名和原始类型
            if var_data['is_pointer']:
                var_data['type'] = f"{type_name}{'*' * var_data['pointer_level']}"
                var_data['original_type'] = f"{original_type}{'*' * var_data['pointer_level']}"
        
        logger.debug(f"Variable data before type resolution: {json.dumps(var_data, indent=2)}")
        
        # 提取初始化器
        initializer = self._extract_declaration_after_equals(node)
        if initializer:
            # 如果是动态数组，先解析数组大小
            if var_data.get('array_size') and isinstance(var_data['array_size'], list):
                if 'dynamic' in var_data['array_size']:
                    logger.debug(f"Found dynamic array: {var_data['name']}")
                    logger.debug(f"Original array size: {var_data['array_size']}")
                    var_data['array_size'] = self._solve_dynamic_array_size(initializer, var_data['array_size'])
                    logger.debug(f"Solved array size: {var_data['array_size']}")
            
            try:
                value = self._process_initializer(
                    initializer=initializer,
                    var_data=var_data.copy()
                )
                if value is not None:
                    var_data['value'] = value
            except Exception as e:
                logger.error(f"Error parsing initializer: {str(e)}")
                logger.error(f"Initializer text: {initializer.text.decode('utf8')}")
        
        # 过滤掉 None 值
        filtered_data = {k: v for k, v in var_data.items() if v is not None}
        logger.debug(f"处理后的变量声明: {json.dumps(filtered_data, indent=2)}")
        return filtered_data
    
    def _extract_type_info(self, node):
        """提取类型信息
        
        Args:
            node: 声明节点
            
        Returns:
            dict: 包含 type 和 original_type 的字典
        """
        logger.debug(f"Extracting type info from: {node.text.decode('utf8')}")
        
        type_parts = []
        original_type = None
        
        for child in node.children:
            if child.type in ['primitive_type', 'sized_type_specifier', 'type_identifier']:
                type_text = child.text.decode('utf8')
                type_parts.append(type_text)
                logger.debug(f"Found type part: {type_text}")
                
                # 记录原始类型
                if not original_type:
                    # 使用 TypeResolver 解析类型，但不处理指针
                    resolved_type = self.type_resolver.resolve_type(type_text, {'is_pointer': False})
                    original_type = resolved_type['resolved_type']
                    if not original_type:
                        logger.error(f"Unknown type: {type_text}")
                        original_type = type_text
            
            elif child.type == 'struct_specifier':
                type_parts.append('struct')
                for struct_child in child.children:
                    if struct_child.type == 'type_identifier':
                        struct_type = struct_child.text.decode('utf8')
                        type_parts.append(struct_type)
                        if not original_type:
                            original_type = f"struct {struct_type}"
            
            elif child.type == 'union_specifier':
                type_parts.append('union')
                for union_child in child.children:
                    if union_child.type == 'type_identifier':
                        union_type = union_child.text.decode('utf8')
                        type_parts.append(union_type)
                        if not original_type:
                            original_type = f"union {union_type}"
        
        type_str = ' '.join(type_parts)
        logger.debug(f"Extracted type: {type_str}")
        logger.debug(f"Original type: {original_type}")
        
        # 如果是指针类型，在这里不处理指针，让 TypeResolver 处理
        return {
            "type": type_str,
            "original_type": original_type
        }
    
    def _categorize_variables(self, variable_definitions):
        """将变量分类到相应的列表中"""
        var_info = {
            'variables': [],  # 基本类型变量
            'struct_vars': [], # 结构体变量
            'pointer_vars': [], # 指针变量
            'array_vars': [],  # 数组变量
        }
        
        for var in variable_definitions.values():
            logger.debug(f"\nCategorizing variable: {var.get('name')}")
            logger.debug(f"Variable data: {json.dumps(var, indent=2)}")
            
            # 首先检查是否是指针
            if var.get('is_pointer'):
                logger.debug(f"Categorized as pointer variable: {var.get('name')}")
                var_info['pointer_vars'].append(var)
                continue
            
            # 然后检查是否是数组
            if var.get('array_size'):
                logger.debug(f"Categorized as array variable: {var.get('name')}")
                var_info['array_vars'].append(var)
                continue
            
            # 使用 TypeResolver 解析基础类型
            type_info = self.type_resolver.resolve_type(var['type'])
            logger.debug(f"Resolved type info: {json.dumps(type_info, indent=2)}")
            
            # 根据基础类型进行分类
            if type_info['is_struct'] or type_info.get('target_is_struct'):
                logger.debug(f"Categorized as struct variable: {var.get('name')}")
                var_info['struct_vars'].append(var)
            else:
                logger.debug(f"Categorized as basic variable: {var.get('name')}")
                var_info['variables'].append(var)
        
        return var_info
    
    def _is_extern_declaration(self, node):
        """检查是否是 extern 声明
        
        Args:
            node: 声明节点
            
        Returns:
            bool: 是否是 extern 声明
        """
        for child in node.children:
            if child.type == 'storage_class_specifier':
                storage_type = child.text.decode('utf8')
                if storage_type == 'extern':
                    logger.debug("Found extern declaration")
                    return True
        return False
    
    def _is_global_declaration(self, node):
        """检查是否是全局变量声明
        
        Args:
            node: 声明节点
            
        Returns:
            bool: 是否是全局变量声明
        """
        # 检查是否在函数内部
        current = node
        while current:
            if current.type in ['function_definition', 'compound_statement']:
                logger.debug("Found local variable in function or block")
                return False
            elif current.type in ['struct_specifier', 'union_specifier', 'enum_specifier']:
                logger.debug("Found declaration in struct/union/enum")
                return False
            current = current.parent
        
        # 检查存储类型说明符
        for child in node.children:
            if child.type == 'storage_class_specifier':
                storage_type = child.text.decode('utf8')
                if storage_type in ['auto', 'register']:
                    logger.debug(f"Found {storage_type} storage class specifier")
                    return False
        
        return True
    
    def _extract_declaration_before_equals(self, node):
        """提取等号之前的声明部分"""
        for child in node.children:
            if child.type == 'init_declarator':
                declarator = child.child_by_field_name('declarator')
                if declarator:
                    return declarator
            elif child.type == 'identifier':
                return child
        return None
    
    def _extract_declaration_after_equals(self, node):
        """提取等号之后的初始化器部分"""
        logger.debug(f"Extracting initializer from: {node.text.decode('utf8')}")
        
        for child in node.children:
            if child.type == 'init_declarator':
                for init_child in child.children:
                    if init_child.type in ['string_literal', 'initializer', 
                                         'initializer_list', 'array_initializer']:
                        logger.debug(f"Found initializer: {init_child.text.decode('utf8')}")
                        return init_child
                    elif init_child.type == 'compound_statement':
                        for stmt_child in init_child.children:
                            if stmt_child.type in ['initializer_list', 'array_initializer']:
                                logger.debug(f"Found initializer in compound statement: {stmt_child.text.decode('utf8')}")
                                return stmt_child
        
        logger.debug("No initializer found")
        return None
    
    def _extract_declarator_info(self, declarator):
        """提取声明器信息（变量名、数组、指针等）"""
        logger.debug(f"Extracting declarator info from: {declarator.text.decode('utf8')}")
        
        info = {
            "name": None,
            "array_size": None,
            "is_pointer": False,
            "pointer_level": 0
        }
        
        if declarator.type == 'pointer_declarator':
            info['is_pointer'] = True
            current = declarator
            pointer_level = 0
            
            # 计算指针级别
            while current and current.type == 'pointer_declarator':
                pointer_level += 1
                for child in current.children:
                    if child.type == 'pointer_declarator':
                        current = child
                        break
                    elif child.type == 'identifier':
                        info['name'] = child.text.decode('utf8')
                        current = None
                        break
            
            info['pointer_level'] = pointer_level
            logger.debug(f"Found pointer: {info['name']} (level: {pointer_level})")
            
            # 如果还没找到名称，继续搜索
            if not info['name']:
                for child in declarator.children:
                    if child.type == 'identifier':
                        info['name'] = child.text.decode('utf8')
                        break
        
        elif declarator.type == 'array_declarator':
            array_size, name = self._parse_array_dimensions(declarator)
            info['array_size'] = array_size
            info['name'] = name
            logger.debug(f"Found array: {name}[{array_size}]")
        
        elif declarator.type == 'identifier':
            info['name'] = declarator.text.decode('utf8')
            logger.debug(f"Found identifier: {info['name']}")
        
        return {k: v for k, v in info.items() if v is not None}
    
    def _process_initializer(self, initializer, var_data=None):
        """处理初始化器节点"""
        if not initializer:
            return None

        # 解析值
        try:
            return self.value_parser.parse(initializer, var_data)
        except Exception as e:
            logger.error(f"Error parsing initializer: {str(e)}")
            logger.error(f"Initializer text: {initializer.text.decode('utf8')}")
            return None
    
    def _parse_array_dimensions(self, declarator):
        """解析数组维度
        
        Args:
            declarator: 数组声明器节点
            
        Returns:
            tuple: (array_sizes, name)
                - array_sizes: 数组各维度的大小列表
                - name: 变量名
        """
        array_sizes = []
        name = None
        current = declarator
        
        # 首先尝试获取最内层的标识符（变量名）
        def find_identifier(node):
            if node.type in ['identifier', 'field_identifier']:
                return node.text.decode('utf8')
            for child in node.children:
                if child.type in ['identifier', 'field_identifier']:
                    return child.text.decode('utf8')
                elif child.type == 'array_declarator':
                    result = find_identifier(child)
                    if result:
                        return result
            return None
        
        # 先尝试获取变量名
        name = find_identifier(declarator)
        logger.debug(f"Found array name: {name}")
        
        while current and current.type == 'array_declarator':
            size_found = False
            next_declarator = None
            
            for child in current.children:
                if child.type == '[':
                    continue
                elif child.type == ']':
                    continue
                elif child.type == 'array_declarator':
                    next_declarator = child
                    continue
                elif child.type in ['identifier', 'field_identifier']:
                    continue  # 已经在前面处理过变量名
                
                if child.type == 'number_literal':
                    # 固定大小
                    size = int(child.text.decode('utf8'))
                    array_sizes.append(size)
                    size_found = True
                    logger.debug(f"Found fixed size {size}")
                elif child.type == 'identifier' and child.text.decode('utf8') != name:
                    # 变量大小
                    size_var = child.text.decode('utf8')
                    array_sizes.append(f"var({size_var})")
                    size_found = True
                    logger.debug(f"Found variable size {size_var}")
            
            if not size_found:
                array_sizes.append("dynamic")
                logger.debug("Found dynamic size []")
            
            current = next_declarator
        
        array_sizes.reverse()  # 反转数组维度以匹配声明顺序
        logger.debug(f"Array declaration analysis: sizes: {array_sizes}, name: {name}")
        return array_sizes, name
    
    def _solve_dynamic_array_size(self, initializer, array_sizes):
        """解析动态数组的实际大小
        
        Args:
            initializer: 初始化器节点
            array_sizes: 原始数组维度列表，可能包含'dynamic'
            
        Returns:
            list: 解析后的数组维度列表
        """
        logger.debug(f"Solving dynamic array size: {array_sizes}")
        logger.debug(f"Initializer type: {initializer.type}")
        
        # 创建新的数组维度列表
        solved_sizes = array_sizes.copy()
        
        # 只处理包含'dynamic'的情况
        if 'dynamic' not in solved_sizes:
            return solved_sizes
        
        # 处理字符串字面量
        if initializer.type == 'string_literal':
            text = initializer.text.decode('utf8').strip('"\'')
            # 字符串长度加1（为了包含null终止符）
            size = len(bytes(text, "utf-8").decode("unicode_escape")) + 1
            # 替换第一个'dynamic'
            dynamic_index = solved_sizes.index('dynamic')
            solved_sizes[dynamic_index] = size
            logger.debug(f"Solved string array size: {solved_sizes}")
            return solved_sizes
        
        # 处理初始化列表
        if initializer.type == 'initializer_list':
            def count_elements(node, depth=0):
                """递归计算初始化列表中的元素数量"""
                if depth >= len(array_sizes):
                    return 1
                
                if node.type != 'initializer_list':
                    return 1
                
                elements = [child for child in node.children 
                          if child.type not in ['comment', ',', '{', '}', '[', ']']]
                
                if depth == array_sizes.index('dynamic'):
                    return len(elements)
                
                counts = [count_elements(elem, depth + 1) for elem in elements]
                return max(counts) if counts else 0
            
            # 计算动态维度的大小
            dynamic_index = solved_sizes.index('dynamic')
            size = count_elements(initializer, 0)
            solved_sizes[dynamic_index] = size
            logger.debug(f"Solved array size from initializer list: {solved_sizes}")
            return solved_sizes
        
        # 如果无法确定大小，保持dynamic
        logger.warning(f"Could not solve dynamic array size for initializer type: {initializer.type}")
        return solved_sizes


class TypeResolver:
    """类型解析器，负责解析和匹配所有C语言类型"""
    
    def __init__(self, type_info: Dict):
        """初始化类型解析器
        
        Args:
            type_info: 包含所有类型定义的字典
        """
        # 检查基本类型
        self.basic_types = set([
            'int', 'char', 'float', 'double', 'void', 'long', 'short',
            'unsigned int', 'unsigned char', 'unsigned long', 'unsigned short',
            'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t',
            'int8_t', 'int16_t', 'int32_t', 'int64_t',
            'bool', 'size_t'
        ])
        self.typedef_types = type_info.get('typedef_types', {})
        self.struct_types = set(type_info.get('struct_types', []))
        self.union_types = set(type_info.get('union_types', []))
        self.pointer_types = type_info.get('pointer_types', {})
        self.struct_info = type_info.get('struct_info', {})
        self.union_info = type_info.get('union_info', {})
        self.enum_types = type_info.get('enum_types', {})
        self.macro_definitions = type_info.get('macro_definitions', {})
    
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
            'is_typedef': False,
            'is_struct': False,
            'is_union': False,
            'is_enum': False,
            'is_basic': False
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
        
        # 处理 typedef 类型
        resolved_type = self._resolve_typedef_chain(base_type)
        
        # 如果 typedef 解析后的类型也是指针
        while resolved_type.endswith('*'):
            resolved_type = resolved_type[:-1].strip()
            pointer_level += 1
        
        # 获取基础类型的信息
        base_type_info = self._get_type_info(resolved_type)
        
        # 如果是指针类型
        if pointer_level > 0:
            type_info.update({
                'is_pointer': True,
                'pointer_level': pointer_level,
                'base_type': resolved_type,  # 使用解析后的基础类型
                'resolved_type': f"{resolved_type}{'*' * pointer_level}",  # 包含指针标记
                'target_type': base_type_info,
                'target_info': base_type_info.get('info'),
                # 重置类型标记
                'is_struct': False,
                'is_union': False,
                'is_enum': False,
                'is_basic': False
            })
            
            # 记录目标类型的性质
            if base_type_info['is_struct']:
                type_info['target_is_struct'] = True
            elif base_type_info['is_union']:
                type_info['target_is_union'] = True
        else:
            # 非指针类型，直接使用基础类型信息
            type_info.update(base_type_info)
            type_info['resolved_type'] = resolved_type
        
        logger.debug(f"Final resolved type info: {json.dumps(type_info, indent=2)}")
        return type_info
    
    def _resolve_typedef_chain(self, type_name: str) -> str:
        """解析 typedef 链，返回最终的基础类型
        
        Args:
            type_name: 类型名称
            
        Returns:
            解析后的实际类型名称
        """
        visited = set()
        current_type = type_name
        
        while current_type in self.typedef_types and current_type not in visited:
            visited.add(current_type)
            current_type = self.typedef_types[current_type]
            
            # 处理指针类型
            if current_type.endswith('*'):
                return current_type
        
        return current_type
    
    def _get_type_info(self, type_name: str) -> Dict[str, Any]:
        """获取类型的详细定义信息"""
        info = {
            'is_typedef': False,
            'is_struct': False,
            'is_union': False,
            'is_enum': False,
            'is_basic': False,
            'info': None
        }
        
        # 移除可能的前缀空格
        type_name = type_name.strip()
        
        # 检查是否是匿名结构体（type_name 为 'struct'）
        if type_name == 'struct':
            info['is_struct'] = True
            return info
            
        # 检查是否是匿名联合体（type_name 为 'union'）
        if type_name == 'union':
            info['is_union'] = True
            return info
        
        # 检查是否是结构体类型
        if type_name.startswith('struct '):
            info['is_struct'] = True
            struct_name = type_name.replace('struct ', '')
            # 尝试多种可能的名称形式
            possible_names = [
                type_name,  # 完整名称 (struct xxx)
                struct_name,  # 不带前缀
                f"struct {struct_name}"  # 标准形式
            ]
            for name in possible_names:
                if name in self.struct_info:
                    info['info'] = self.struct_info[name]
                    break
            
        # 检查是否是联合体类型
        elif type_name.startswith('union '):
            info['is_union'] = True
            union_name = type_name.replace('union ', '')
            # 尝试多种可能的名称形式
            possible_names = [
                type_name,  # 完整名称 (union xxx)
                union_name,  # 不带前缀
                f"union {union_name}"  # 标准形式
            ]
            for name in possible_names:
                if name in self.union_info:
                    info['info'] = self.union_info[name]
                    break
            
        # 检查是否是不带前缀的类型
        elif type_name in self.struct_types:
            info['is_struct'] = True
            if type_name in self.struct_info:
                info['info'] = self.struct_info[type_name]
            elif f"struct {type_name}" in self.struct_info:
                info['info'] = self.struct_info[f"struct {type_name}"]
                
        elif type_name in self.union_types:
            info['is_union'] = True
            if type_name in self.union_info:
                info['info'] = self.union_info[type_name]
            elif f"union {type_name}" in self.union_info:
                info['info'] = self.union_info[f"union {type_name}"]
        
        # 检查是否是枚举类型
        elif type_name in self.enum_types:
            info['is_enum'] = True
            info['info'] = self.enum_types[type_name]
        
        # 如果都不是，则认为是基本类型
        else:
            info['is_basic'] = True
        
        if (info['is_struct'] or info['is_union']) and not info['info']:
            logger.debug(f"Type info not found for {type_name}")
            logger.debug(f"Available struct types: {list(self.struct_info.keys())}")
            logger.debug(f"Available union types: {list(self.union_info.keys())}")
        
        return info
    
    
class ValueParser:
    """C语言值解析器，负责解析各种类型的初始化值"""
    
    def __init__(self, type_resolver):
        """初始化值解析器
        
        Args:
            type_resolver: TypeResolver实例，用于类型解析
        """
        self.type_resolver = type_resolver
    
    def parse(self, node, var_data):
        """解析值"""
        if not node:
            return None
            
        logger.debug(f"\nParsing value:")
        logger.debug(f"Type info: {json.dumps(var_data, indent=2)}")
        logger.debug(f"Node type: {node.type}")
        logger.debug(f"Node text: {node.text.decode('utf8')}")
        
        # 使用 TypeResolver 解析完整的类型信息
        type_info = self.type_resolver.resolve_type(var_data['type'], var_data)
        
        # 根据类型选择解析方法
        if type_info['is_pointer']:
            return self._parse_pointer(node)
        elif type_info['array_size']:
            return self._parse_array(node, type_info)
        elif type_info['bit_field'] is not None:
            return self._parse_bit_field(node, type_info)
        elif type_info['is_struct']:
            return self._parse_struct(node, type_info)
        elif type_info['is_union']:
            return self._parse_union(node, type_info)
        elif type_info['is_enum']:
            return self._parse_enum(node, type_info)
        else:
            return self._parse_basic_type(node, type_info['resolved_type'])
    
    def _parse_basic_type(self, node, type_name):
        """解析基本类型值"""
        logger.debug(f"\nParsing basic type {type_name}:")
        logger.debug(f"Node type: {node.type}")
        logger.debug(f"Node text: {node.text.decode('utf8')}")
        
        # 处理字符串字面量
        if node.type == 'string_literal':
            text = node.text.decode('utf8').strip('"\'')
            result = bytes(text, "utf-8").decode("unicode_escape")
            logger.debug(f"Parsed string literal: {result}")
            return result
            
        # 处理复合字面量
        elif node.type == 'compound_literal':
            return node.text.decode('utf8')
            
        # 处理初始化列表
        elif node.type == 'initializer_list':
            return node.text.decode('utf8')
            
        # 处理表达式
        text = node.text.decode('utf8')
        try:
            # 处理sizeof表达式
            if 'sizeof' in text:
                return text  # 保持原始表达式
                
            # 处理数组初始化器
            if text.startswith('{') and text.endswith('}'):
                return text  # 保持原始表达式
                
            # 使用 ExpressionParser 解析表达式
            value, result = ExpressionParser.parse(
                text,
                self.type_resolver.enum_types,
                self.type_resolver.macro_definitions
            )
            logger.debug(f"Parsed expression: {value} {result}")
            return value
        except Exception as e:
            logger.debug(f"Failed to parse expression '{text}': {str(e)}")
            return text  # 返回原始文本
    
    def _parse_array(self, node, type_info):
        """解析数组值"""
        # 使用 TypeResolver 获取元素类型信息
        element_type_info = self.type_resolver.resolve_type(
            type_info['base_type'],
            {'array_size': type_info['array_size'][1:] if len(type_info['array_size']) > 1 else None}
        )
        
        # 获取数组元素
        elements = self._get_elements(node)
        result = []
        
        for element in elements:
            value = self.parse(element, element_type_info)
            result.append(value)
            
        return result
    
    def _parse_struct(self, node, type_info):
        """解析结构体值"""
        struct_info = type_info.get('info')
        if not struct_info:
            # 检查是否是匿名结构体
            if type_info.get('nested_fields'):
                logger.debug("Found anonymous struct with nested fields")
                return self._parse_anonymous_struct(node, type_info)
            logger.error(f"Struct info not found for {type_info['type']}")
            return {}
            
        # 获取初始化值列表
        elements = self._get_elements(node)
        if not elements and node.type == 'initializer_list':
            logger.error(f"Empty initializer list for struct {type_info['type']}")
            return {}
            
        result = {}
        
        # 按照结构体定义解析每个字段
        for i, field in enumerate(struct_info['fields']):
            field_name = field['name']
            field_type_info = self.type_resolver.resolve_type(field['type'], field)
            
            if i < len(elements):
                try:
                    value = self.parse(elements[i], field_type_info)
                    result[field_name] = value
                except Exception as e:
                    logger.error(f"Error parsing struct field {field_name}: {str(e)}")
                    logger.error(f"Field type: {field_type_info}")
                    logger.error(f"Field value node: {elements[i].text.decode('utf8')}")
                    result[field_name] = None if field_type_info['is_pointer'] else 0
            else:
                logger.warning(f"Missing initializer for struct field {field_name}")
                result[field_name] = None if field_type_info['is_pointer'] else 0
                
        return result
    
    def _parse_anonymous_struct(self, node, type_info):
        """解析匿名结构体值
        
        Args:
            node: 语法树节点
            type_info: 类型信息，包含 nested_fields
            
        Returns:
            dict: 解析后的结构体值
        """
        logger.debug("Parsing anonymous struct")
        logger.debug(f"Nested fields: {json.dumps(type_info['nested_fields'], indent=2)}")
        
        # 获取初始化值列表
        elements = self._get_elements(node)
        if not elements and node.type == 'initializer_list':
            logger.error("Empty initializer list for anonymous struct")
            return {}
            
        result = {}
        fields = type_info['nested_fields']
        
        # 按照字段定义解析每个字段
        for i, field in enumerate(fields):
            field_name = field['name']
            field_type_info = self.type_resolver.resolve_type(field['type'], field)
            
            if i < len(elements):
                try:
                    value = self.parse(elements[i], field_type_info)
                    result[field_name] = value
                except Exception as e:
                    logger.error(f"Error parsing anonymous struct field {field_name}: {str(e)}")
                    logger.error(f"Field type: {field_type_info}")
                    logger.error(f"Field value node: {elements[i].text.decode('utf8')}")
                    result[field_name] = None if field_type_info['is_pointer'] else 0
            else:
                logger.warning(f"Missing initializer for anonymous struct field {field_name}")
                result[field_name] = None if field_type_info['is_pointer'] else 0
                
        return result
    
    def _parse_union(self, node, type_info):
        """解析联合体值"""
        union_info = type_info.get('info')
        if not union_info:
            logger.error(f"Union info not found for {type_info['type']}")
            logger.error(f"Type info: {json.dumps(type_info, indent=2)}")
            return {}
            
        # 获取初始化值
        if node.type != 'initializer_list':
            # 单个值初始化，使用第一个字段
            if union_info['fields']:
                first_field = union_info['fields'][0]
                field_type_info = self.type_resolver.resolve_type(first_field['type'], first_field)
                try:
                    return {first_field['name']: self.parse(node, field_type_info)}
                except Exception as e:
                    logger.error(f"Error parsing union field {first_field['name']}: {str(e)}")
                    logger.error(f"Field type: {field_type_info}")
                    logger.error(f"Field value node: {node.text.decode('utf8')}")
                    return {first_field['name']: None if field_type_info['is_pointer'] else 0}
            return {}
            
        # 处理指定字段初始化
        for child in node.children:
            if child.type == 'initializer_pair':
                field_name = child.children[0].text.decode('utf8')[1:]  # 去掉前面的点
                
                # 查找实际的值节点
                current = child.children[1]
                while current and current.type not in ['number_literal', 'string_literal', 'initializer_list']:
                    current = current.next_sibling
                    
                if not current:
                    logger.error(f"Could not find value node for field {field_name}")
                    continue
                    
                for field in union_info['fields']:
                    if field['name'] == field_name:
                        field_type_info = self.type_resolver.resolve_type(field['type'], field)
                        try:
                            value = self.parse(current, field_type_info)
                            return {field_name: value}
                        except Exception as e:
                            logger.error(f"Error parsing designated union field {field_name}: {str(e)}")
                            logger.error(f"Field type: {field_type_info}")
                            logger.error(f"Field value node: {current.text.decode('utf8')}")
                            return {field_name: None if field_type_info['is_pointer'] else 0}
                logger.error(f"Field {field_name} not found in union {type_info['type']}")
                
        # 如果没有找到指定的字段，使用第一个字段
        if union_info['fields']:
            first_field = union_info['fields'][0]
            field_type_info = self.type_resolver.resolve_type(first_field['type'], first_field)
            try:
                elements = self._get_elements(node)
                if elements:
                    return {first_field['name']: self.parse(elements[0], field_type_info)}
            except Exception as e:
                logger.error(f"Error parsing first union field: {str(e)}")
                
        return {}

    def _get_elements(self, node):
        """获取初始化列表中的元素
        
        Args:
            node: 语法树节点
            
        Returns:
            list: 元素节点列表
        """
        if not node or node.type != 'initializer_list':
            return [node] if node else []
            
        return [
            child for child in node.children
            if child.type not in ['comment', ',', '{', '}', '[', ']']
        ]
    
    def _parse_pointer(self, node):
        """解析指针值
        
        Args:
            node: 语法树节点
            
        Returns:
            str: 指针值的字符串表示
        """
        if node.type == 'null':
            return None
        return node.text.decode('utf8')
    
    def _parse_bit_field(self, node, type_info):
        """解析位域值
        
        Args:
            node: 语法树节点
            type_info: 类型信息
            
        Returns:
            int: 位域值
        """
        value = self._parse_basic_type(node, type_info['type'])
        if isinstance(value, (int, float)):
            max_value = (1 << type_info['bit_field']) - 1
            return int(value) & max_value
        return value
    
    def _parse_enum(self, node, type_info):
        """解析枚举值
        
        Args:
            node: 语法树节点
            type_info: 类型信息
            
        Returns:
            str/int: 枚举值
        """
        text = node.text.decode('utf8')
        
        # 如果是枚举常量名
        if text in self.type_resolver.enum_types.get(type_info['type'], {}):
            return text
            
        # 如果是数值
        try:
            value = int(text)
            # 检查是否是有效的枚举值
            for name, enum_value in self.type_resolver.enum_types.get(type_info['type'], {}).items():
                if enum_value == value:
                    return name
            return value
        except ValueError:
            return text

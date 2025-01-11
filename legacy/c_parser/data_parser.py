import json
from typing import Any, Dict, Optional
from utils.logger_config import setup_logger
from utils import TreeSitterUtil
from utils import ExpressionParser
from .type_parser import CTypeParser
from .type_manager import TypeManager

logger = setup_logger('DataParser')

class CDataParser:
    """C语言数据解析器，负责解析C源文件中的变量定义和初始化数据"""
    
    def __init__(self, type_info):
        """初始化数据解析器"""
        logger.info("=== Initializing CDataParser ===")
        self.ts_util = TreeSitterUtil()
        
        # 初始化类型管理器
        logger.info("Initializing TypeManager...")
        self.type_manager = TypeManager(type_info)
        
        # 初始化解析器
        logger.info("Initializing parsers...")
        self.type_parser = CTypeParser()
        self.value_parser = ValueParser(self.type_manager)
        
        # 输出类型统计信息
        type_info = self.type_manager.export_type_info()
        logger.info("\nLoaded type definitions:")
        logger.info(f"- Typedefs:   {len(type_info['typedef_types'])} items")
        logger.info(f"- Structs:    {len(type_info['struct_types'])} items")
        logger.info(f"- Unions:     {len(type_info['union_types'])} items")
        logger.info(f"- Enums:      {len(type_info['enum_types'])} items")
        logger.info(f"- Pointers:   {len(type_info['pointer_types'])} items")
        logger.info("=== Initialization Complete ===\n")
    
    def _parse_current_file_types(self, tree):
        """解析当前文件中的类型定义"""
        logger.info("解析当前文件的类型定义")
        
        # 使用CTypeParser解析当前文件的类型定义
        current_types = self.type_parser.parse_declarations(tree=tree)
        
        # 更新类型管理器
        self.type_manager.update_type_info(current_types)
        
        # 重新创建值解析器
        self.value_parser = ValueParser(self.type_manager)
        
        logger.debug("当前文件类型解析完成:")
        debug_info = self.type_manager.export_type_info()
        logger.debug(f"- 类型定义(typedef): {len(debug_info['typedef_types'])} 个")
        logger.debug(f"- 结构体(struct): {len(debug_info['struct_types'])} 个")
        logger.debug(f"- 联合体(union): {len(debug_info['union_types'])} 个")
        logger.debug(f"- 枚举(enum): {len(debug_info['enum_types'])} 个")
        logger.debug(f"- 指针类型: {len(debug_info['pointer_types'])} 个")
    
    def _print_type_definitions(self):
        """打印所有可用的类型定义"""
        logger.info("\n=== Available Type Definitions ===")
        
        type_info = self.type_manager.export_type_info()
        
        # 打印结构体定义
        struct_info = self.type_manager.get_struct_info()
        if struct_info:
            logger.info("\nStruct Definitions:")
            for struct_name, info in struct_info.items():
                logger.info(f"struct {struct_name} {{")
                for field in info.get('fields', []):
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
        union_info = self.type_manager.get_union_info()
        if union_info:
            logger.info("\nUnion Definitions:")
            for union_name, info in union_info.items():
                logger.info(f"union {union_name} {{")
                for field in info.get('fields', []):
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
        typedef_types = type_info.get('typedef_types')
        if typedef_types:
            logger.info("\nTypedef Definitions:")
            for typedef_name, typedef_type in typedef_types.items():
                logger.info(f"typedef {typedef_type} {typedef_name};")
        
        # 打印枚举定义
        enum_types = self.type_manager.get_enum_info()
        if enum_types:
            logger.info("\nEnum Definitions:")
            for enum_name, enum_values in enum_types.items():
                logger.info(f"enum {enum_name} {{")
                for name, value in enum_values.items():
                    logger.info(f"    {name} = {value},")
                logger.info("};")
        
        logger.info("\n=== End of Type Definitions ===\n")
    
    def _categorize_variables(self, variable_definitions):
        """将变量分类到相应的列表中"""
        var_info = {
            'variables': [],   # 基本类型变量
            'struct_vars': [], # 结构体变量
            'pointer_vars': [], # 指针变量
            'array_vars': [],  # 数组变量
        }
        
        for var in variable_definitions.values():
            logger.debug(f"\nCategorizing variable: {var.get('name')}")
            logger.debug(f"Variable data: {json.dumps(var, indent=2)}")
            
            # 首先检查是否是指针
            if var.get('is_pointer') or self.type_manager.is_pointer_type(var['type']):
                logger.debug(f"Categorized as pointer variable: {var.get('name')}")
                var_info['pointer_vars'].append(var)
                continue
            
            # 然后检查是否是数组
            if var.get('array_size'):
                logger.debug(f"Categorized as array variable: {var.get('name')}")
                var_info['array_vars'].append(var)
                continue
            
            # 检查是否是结构体类型
            if self.type_manager.is_struct_type(var['type']):
                logger.debug(f"Categorized as struct variable: {var.get('name')}")
                var_info['struct_vars'].append(var)
            else:
                logger.debug(f"Categorized as basic variable: {var.get('name')}")
                var_info['variables'].append(var)
        
        return var_info
    
    def parse_global_variables(self, source_file):
        """解析C源文件中的全局变量定义和初始化数据"""
        logger.info(f"\n=== Parsing Global Variables: {source_file} ===")
        
        # 使用TreeSitterUtil解析文件
        logger.info("Step 1: Parsing source file...")
        tree = self.ts_util.parse_file(source_file)
        
        # 解析类型定义
        logger.info("\nStep 2: Parsing type definitions...")
        self._parse_current_file_types(tree)
        
        # 解析变量定义
        logger.info("\nStep 3: Parsing variable definitions...")
        variable_definitions = {}
        self._collect_variable_definitions(tree.root_node, variable_definitions)
        logger.info(f"Found {len(variable_definitions)} variable definitions")
        
        # 对变量进行分类
        logger.info("\nStep 4: Categorizing variables...")
        var_info = self._categorize_variables(variable_definitions)
        
        # 输出统计信息
        logger.info("\nParsing results:")
        logger.info(f"- Basic variables:    {len(var_info['variables'])} items")
        logger.info(f"- Struct variables:   {len(var_info['struct_vars'])} items")
        logger.info(f"- Pointer variables:  {len(var_info['pointer_vars'])} items")
        logger.info(f"- Array variables:    {len(var_info['array_vars'])} items")
        
        # 获取全局类型信息
        global_types = self.type_manager.export_global_type_info()
        
        # 获取当前文件的类型信息
        current_types = self.type_manager.export_current_type_info()
        
        # 返回解析结果
        result = {
            'types': {
                'global': {
                    'struct_info': global_types['struct_info'],
                    'typedef_types': global_types['typedef_types'],
                    'enum_types': global_types['enum_types'],
                    'macro_definitions': global_types['macro_definitions']
                },
                'current': {
                    'struct_info': current_types['struct_info'],
                    'typedef_types': current_types['typedef_types'],
                    'enum_types': current_types['enum_types'],
                    'macro_definitions': current_types['macro_definitions']
                }
            },
            'variables': var_info
        }
        
        logger.info("=== Parsing Complete ===\n")
        return result
    
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
        """提取类型信息"""
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
                    # 使用 TypeManager 解析类型
                    if self.type_manager.is_basic_type(type_text):
                        original_type = type_text
                    else:
                        original_type = self.type_manager.get_real_type(type_text)
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
        
        return {
            "type": type_str,
            "original_type": original_type
        }
    
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

        try:
            # 使用 TypeManager 获取类型信息
            type_info = self.type_manager.resolve_type(var_data['type'])
            var_data['type_info'] = type_info
            
            # 解析值
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
        """解析动态数组的实际大小"""
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
        
        logger.warning(f"Could not solve dynamic array size for initializer type: {initializer.type}")
        return solved_sizes


class ValueParser:
    """C语言值解析器，负责解析各种类型的初始化值"""
    
    def __init__(self, type_manager: TypeManager):
        """初始化值解析器
        
        Args:
            type_manager: TypeManager实例，用于类型管理
        """
        self.type_manager = type_manager
    
    def parse(self, node, var_data):
        """解析值"""
        if not node:
            return None
            
        logger.debug("\n=== Parsing Value ===")
        logger.debug(f"Type: {var_data.get('type')}")
        logger.debug(f"Node type: {node.type}")
        logger.debug(f"Node text: {node.text.decode('utf8')}")
        
        # 使用 TypeManager 解析完整的类型信息
        type_info = self.type_manager.resolve_type(var_data['type'], var_data)
        
        # 根据类型选择解析方法
        result = None
        try:
            if type_info['is_pointer'] or node.type == 'pointer_expression':
                result = self._parse_pointer(node)
                logger.debug(f"Parsed pointer value: {result}")
            elif type_info['array_size']:
                result = self._parse_array(node, type_info)
                logger.debug(f"Parsed array value: {result}")
            elif type_info['bit_field'] is not None:
                result = self._parse_bit_field(node, type_info)
                logger.debug(f"Parsed bit field value: {result}")
            elif type_info['is_struct']:
                result = self._parse_struct(node, type_info)
                logger.debug(f"Parsed struct value: {result}")
            elif type_info['is_union']:
                result = self._parse_union(node, type_info)
                logger.debug(f"Parsed union value: {result}")
            elif type_info['is_enum']:
                result = self._parse_enum(node, type_info)
                logger.debug(f"Parsed enum value: {result}")
            else:
                result = self._parse_basic_type(node, type_info['resolved_type'])
                logger.debug(f"Parsed basic type value: {result}")
        except Exception as e:
            logger.error(f"Error parsing value: {str(e)}")
            logger.error(f"Node text: {node.text.decode('utf8')}")
            raise
            
        logger.debug("=== Parsing Complete ===\n")
        return result
    
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
                self.type_manager.get_enum_info(),
                self.type_manager.get_macro_definition()
            )
            logger.debug(f"Parsed expression: {value} {result}")
            return value
        except Exception as e:
            logger.debug(f"Failed to parse expression '{text}': {str(e)}")
            return text  # 返回原始文本
    
    def _parse_array(self, node, type_info):
        """解析数组值"""
        # 使用 TypeManager 获取元素类型信息
        element_type = type_info['base_type']
        element_type_info = self.type_manager.resolve_type(
            element_type,
            {'array_size': type_info['array_size'][1:] if len(type_info['array_size']) > 1 else None}
        )
        
        # 获取数组元素
        elements = self._get_elements(node)
        result = []
        
        for element in elements:
            try:
                value = self.parse(element, element_type_info)
                result.append(value)
            except Exception as e:
                logger.error(f"Error parsing array element: {str(e)}")
                result.append(None if element_type_info['is_pointer'] else 0)
                
        return result
    
    def _parse_struct(self, node, type_info):
        """解析结构体值"""
        # 检查是否是匿名结构体
        if type_info.get('nested_fields'):
            logger.debug("Found anonymous struct with nested fields")
            return self._parse_anonymous_struct(node, type_info)
        
        struct_info = type_info.get('info')
        if not struct_info:
            logger.error(f"Struct info not found for {type_info['type']}")
            return {}
        
        # 获取初始化值列表
        elements = self._get_elements(node)
        if not elements:
            logger.error(f"Empty initializer list for struct {type_info['type']}")
            return {}
        
        result = {}
        fields = struct_info.get('fields', [])
        
        # 按照结构体定义解析每个字段
        for i, field in enumerate(fields):
            field_name = field['name']
            # 创建完整的字段类型信息
            field_type_info = {
                'type': field['type'],
                'array_size': field.get('array_size'),
                'bit_field': field.get('bit_field'),
                'nested_fields': field.get('nested_fields'),
                'is_anonymous': field.get('is_anonymous', False)
            }
            
            # 解析字段类型
            field_type_info = self.type_manager.resolve_type(field['type'], field_type_info)
            
            if i < len(elements):
                try:
                    value = self.parse(elements[i], field_type_info)
                    result[field_name] = value
                except Exception as e:
                    logger.error(f"Error parsing struct field {field_name}: {str(e)}")
                    result[field_name] = None if field_type_info['is_pointer'] else 0
            else:
                logger.warning(f"Missing initializer for struct field {field_name}")
                result[field_name] = None if field_type_info['is_pointer'] else 0
        
        return result
    
    def _parse_anonymous_struct(self, node, type_info):
        """解析匿名结构体值"""
        logger.debug("Parsing anonymous struct")
        logger.debug(f"Nested fields: {json.dumps(type_info['nested_fields'], indent=2)}")
        
        # 获取初始化值列表
        elements = self._get_elements(node)
        if not elements:
            logger.error("Empty initializer list for anonymous struct")
            return {}
        
        result = {}
        fields = type_info['nested_fields']
        
        # 按照字段定义解析每个字段
        for i, field in enumerate(fields):
            field_name = field['name']
            # 创建完整的字段类型信息
            field_type_info = {
                'type': field['type'],
                'array_size': field.get('array_size'),
                'bit_field': field.get('bit_field'),
                'nested_fields': field.get('nested_fields'),
                'is_anonymous': field.get('is_anonymous', False)
            }
            
            # 解析字段类型
            field_type_info = self.type_manager.resolve_type(field['type'], field_type_info)
            
            if i < len(elements):
                try:
                    element = elements[i]
                    value = self.parse(element, field_type_info)
                    result[field_name] = value
                except Exception as e:
                    logger.error(f"Error parsing anonymous struct field {field_name}: {str(e)}")
                    logger.error(f"Field type info: {json.dumps(field_type_info, indent=2)}")
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
            return {}
        
        logger.debug("\n=== Parsing Union Value ===")
        logger.debug(f"Union type: {type_info['type']}")
        logger.debug(f"Node type: {node.type}")
        logger.debug(f"Node text: {node.text.decode('utf8')}")
        
        # 处理指定初始化器（使用 .field = value 语法）
        if node.type == 'initializer_list':
            # 遍历所有子节点
            for child in node.children:
                # 查找 initializer_pair
                if child.type == 'initializer_pair':
                    field_name = None
                    field_value = None
                    
                    # 从 initializer_pair 中获取字段名和值
                    for pair_child in child.children:
                        if pair_child.type == 'field_designator':
                            # 获取字段名（去掉前面的点）
                            field_name = pair_child.text.decode('utf8').lstrip('.')
                            logger.debug(f"Found field designator: {field_name}")
                        elif pair_child.type not in ['comment', ',', '{', '}', '[', ']', '.', '=']:
                            field_value = pair_child
                            logger.debug(f"Found field value: {field_value.text.decode('utf8')}")
                    
                    if field_name and field_value:
                        # 查找对应的字段定义
                        for field in union_info['fields']:
                            if field['name'] == field_name:
                                logger.debug(f"Processing union field: {field_name}")
                                # 创建字段类型信息
                                field_type_info = {
                                    'type': field['type'],
                                    'array_size': field.get('array_size'),
                                    'bit_field': field.get('bit_field'),
                                    'nested_fields': field.get('nested_fields'),
                                    'is_anonymous': field.get('is_anonymous', False)
                                }
                                
                                # 解析字段类型
                                field_type_info = self.type_manager.resolve_type(field['type'], field_type_info)
                                logger.debug(f"Field type info: {json.dumps(field_type_info, indent=2)}")
                                
                                try:
                                    value = self.parse(field_value, field_type_info)
                                    logger.debug(f"Successfully parsed union field {field_name}: {value}")
                                    return {field_name: value}
                                except Exception as e:
                                    logger.error(f"Error parsing union field {field_name}: {str(e)}")
                                    return {field_name: None if field_type_info['is_pointer'] else 0}
        
        # 如果没有指定字段名，使用第一个字段
        elements = self._get_elements(node)
        if elements and union_info['fields']:
            first_field = union_info['fields'][0]
            logger.debug(f"Using first field: {first_field['name']}")
            
            field_type_info = {
                'type': first_field['type'],
                'array_size': first_field.get('array_size'),
                'bit_field': first_field.get('bit_field'),
                'nested_fields': first_field.get('nested_fields'),
                'is_anonymous': first_field.get('is_anonymous', False)
            }
            
            # 解析字段类型
            field_type_info = self.type_manager.resolve_type(first_field['type'], field_type_info)
            logger.debug(f"First field type info: {json.dumps(field_type_info, indent=2)}")
            
            try:
                value = self.parse(elements[0], field_type_info)
                logger.debug(f"Successfully parsed first field: {value}")
                return {first_field['name']: value}
            except Exception as e:
                logger.error(f"Error parsing union field: {str(e)}")
                return {first_field['name']: None if field_type_info['is_pointer'] else 0}
        
        logger.debug("=== Union Parsing Complete ===\n")
        return {}

    def _parse_pointer(self, node):
        """解析指针值"""
        if not node:
            return None
        
        if node.type == 'null':
            return None
        
        # 处理取地址操作
        if node.type == 'pointer_expression':
            # 获取操作符和操作数
            operator = None
            operand = None
            for child in node.children:
                if child.type == '&':
                    operator = '&'
                elif child.type not in ['&', '*']:
                    operand = child
            
            if operator == '&' and operand:
                # 返回取地址表达式
                return node.text.decode('utf8')
        
        # 处理其他指针值
        return node.text.decode('utf8')

    def _parse_bit_field(self, node, type_info):
        """解析位域值"""
        value = self._parse_basic_type(node, type_info['type'])
        if isinstance(value, (int, float)):
            max_value = (1 << type_info['bit_field']) - 1
            return int(value) & max_value
        return value

    def _parse_enum(self, node, type_info):
        """解析枚举值"""
        text = node.text.decode('utf8')
        enum_values = self.type_manager.get_enum_info(type_info['type'])
        
        # 如果是枚举常量名
        if text in enum_values:
            return text
            
        # 如果是数值
        try:
            value = int(text)
            # 检查是否是有效的枚举值
            for name, enum_value in enum_values.items():
                if enum_value == value:
                    return name
            return value
        except ValueError:
            return text

    def _get_elements(self, node):
        """获取初始化列表中的元素"""
        if not node:
            return []
            
        if node.type == 'initializer_list':
            elements = []
            for child in node.children:
                if child.type not in ['comment', ',', '{', '}', '[', ']']:
                    if child.type == 'initializer_list':
                        # 递归处理嵌套的初始化列表
                        elements.append(child)
                    elif child.type == 'initializer_pair':
                        # 处理指定初始化器
                        value_node = None
                        for pair_child in child.children:
                            if pair_child.type not in ['.', '=']:
                                value_node = pair_child
                                break
                        if value_node:
                            elements.append(value_node)
                    else:
                        elements.append(child)
            return elements
        else:
            return [node]

import json
from logger_config import setup_logger
from type_parser import CTypeParser
from utils import TreeSitterUtil
from utils import ExpressionParser

logger = setup_logger('DataParser')

class CDataParser:
    """C语言数据解析器，负责解析C源文件中的变量定义和初始化数据"""
    
    def __init__(self, type_info):
        """初始化数据解析器"""
        logger.info("Initializing CDataParser")
        self.ts_util = TreeSitterUtil()
        self.type_info = type_info
        
        # 从type_info初始化类型信息
        if type_info:
            self.typedef_types = type_info.get('typedef_types', {})
            self.struct_types = set(type_info.get('struct_types', []))
            self.union_types = set(type_info.get('union_types', []))
            self.pointer_types = type_info.get('pointer_types', {})
            self.struct_info = type_info.get('struct_info', {})
            self.union_info = type_info.get('union_info', {})
            self.enum_types = type_info.get('enum_types', {})
            self.macro_definitions = type_info.get('macro_definitions', {})
            
            # 打印加载的类型信息
            logger.debug("Loaded type definitions:")
            logger.debug(f"Typedefs: {json.dumps(self.typedef_types, indent=2)}")
            logger.debug(f"Structs: {json.dumps(list(self.struct_types), indent=2)}")
            logger.debug(f"Unions: {json.dumps(list(self.union_types), indent=2)}")
        
        self._print_type_definitions()
        
        # 初始化类型解析器
        self.type_parser = CTypeParser()
        
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
                logger.info(f"\nstruct {struct_name} {{")
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
                logger.info(f"\nunion {union_name} {{")
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
                logger.info(f"\nenum {enum_name} {{")
                for name, value in enum_values.items():
                    logger.info(f"    {name} = {value},")
                logger.info("};")
        
        logger.info("\n=== End of Type Definitions ===\n")
    
    def parse_source(self, source_file):
        """解析C源文件中的变量定义和初始化数据
        
        Args:
            source_file: C源文件路径
            
        Returns:
            dict: 解析结果，包含类型定义和变量信息
        """
        logger.info(f"Parsing source file: {source_file}")
        
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
        type_info = self.type_parser.parse_declarations(tree)
        
        # 更新当前文件的类型信息
        self.current_types.update(type_info)
        # 同时更新全局类型信息
        self.typedef_types.update(type_info['typedef_types'])
        self.struct_types.update(type_info['struct_types'])
        self.pointer_types.update(type_info['pointer_types'])
        self.struct_info.update(type_info['struct_info'])
        self.enum_types.update(type_info['enum_types'])
        self.macro_definitions.update(type_info['macro_definitions'])
    
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
        """处理声明节点，解析C变量声明"""
        logger.debug(f"处理声明节点: {node.text.decode('utf8')}")
        
        # 跳过 extern 声明
        if self._is_extern_declaration(node):
            logger.debug("跳过 extern 声明")
            return None
        
        # 检查是否是全局变量
        if not self._is_global_declaration(node):
            logger.debug("跳过局部变量声明")
            return None
        
        # 提取类型信息
        type_info = self._extract_type_info(node)
        
        # 检查类型是否存在
        if not type_info or not type_info.get('type'):
            logger.error(f"无法识别的类型: {node.text.decode('utf8')}")
            raise ValueError(f"Unknown type in declaration: {node.text.decode('utf8')}")
        
        # 检查类型是否在已知类型列表中
        type_name = type_info['type']
        original_type = type_info.get('original_type')
        
        # 检查基本类型
        basic_types = set([
            'int', 'char', 'float', 'double', 'void', 'long', 'short',
            'unsigned int', 'unsigned char', 'unsigned long', 'unsigned short',
            'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t',
            'int8_t', 'int16_t', 'int32_t', 'int64_t',
            'bool', 'size_t',
            # 添加自定义的类型别名
            'u8', 'u16', 'u32', 'u64',
            'i8', 'i16', 'i32', 'i64',
            'f32', 'f64'
        ])
        
        is_valid_type = (
            type_name in basic_types or
            type_name in self.typedef_types or
            type_name.startswith('struct ') and type_name.split(' ')[1] in self.struct_info or
            type_name.startswith('union ') and type_name.split(' ')[1] in self.union_info or
            original_type in basic_types or
            original_type in self.typedef_types or
            original_type and original_type.startswith('struct ') and original_type.split(' ')[1] in self.struct_info or
            original_type and original_type.startswith('union ') and original_type.split(' ')[1] in self.union_info
        )
        
        if not is_valid_type:
            logger.error(f"未定义的类型: {type_name}")
            logger.error(f"Original type: {original_type}")
            logger.error(f"Available types:")
            logger.error(f"Typedefs: {list(self.typedef_types.keys())}")
            logger.error(f"Structs: {list(self.struct_info.keys())}")
            logger.error(f"Unions: {list(self.union_info.keys())}")
            raise ValueError(f"Undefined type in declaration: {type_name}")
        
        # 初始化变量数据
        var_data = {
            "name": None,
            "type": type_name,
            "original_type": original_type,
            "array_size": None,
            "is_pointer": False,
            "pointer_level": None,
        }
        
        # 获取原始类型的完整信息
        original_type = var_data['original_type']
        logger.debug(f"Original type: {original_type}")        
        # 提取声明器信息（变量名、数组、指针等）
        declarator = self._extract_declaration_before_equals(node)
        if declarator:
            var_data.update(self._extract_declarator_info(declarator))
        
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
            
            logger.debug(f"Processing initializer for {var_data['name']}")
            logger.debug(f"Type: {var_data['original_type']}")
            logger.debug(f"Array size: {var_data['array_size']}")

            # 检查类型是否已定义并获取类型信息
            type_info = None
            
            # 规范化类型名称
            def normalize_type(type_name):
                """规范化类型名称，处理 struct/union 前缀"""
                if type_name.startswith('struct ') or type_name.startswith('union '):
                    return type_name
                
                # 先检查是否是联合体类型
                if type_name in self.union_types:
                    return f"union {type_name}"
                # 再检查是否是结构体类型
                if type_name in self.struct_types:
                    return f"struct {type_name}"
                
                # 如果是 typedef，检查其基础类型
                if type_name in self.typedef_types:
                    base_type = self.typedef_types[type_name]
                    if base_type.startswith('struct ') or base_type.startswith('union '):
                        return base_type
                    if base_type in self.union_types:
                        return f"union {base_type}"
                    if base_type in self.struct_types:
                        return f"struct {base_type}"
                
                return type_name
            
            normalized_type = normalize_type(original_type)
            logger.debug(f"Normalized type: {normalized_type}")
            
            # 按优先级检查类型
            if normalized_type.startswith('union '):
                union_type = normalized_type.split(' ')[1]
                if union_type in self.union_info:
                    type_info = {
                        'type': 'union',
                        'info': self.union_info[union_type]
                    }
                    logger.debug(f"Found union type: {union_type}")
                    logger.debug(f"Union info: {json.dumps(self.union_info[union_type], indent=2)}")
            elif normalized_type.startswith('struct '):
                struct_type = normalized_type.split(' ')[1]
                if struct_type in self.struct_info:
                    type_info = {
                        'type': 'struct',
                        'info': self.struct_info[struct_type]
                    }
                    logger.debug(f"Found struct type: {struct_type}")
                    logger.debug(f"Struct info: {json.dumps(self.struct_info[struct_type], indent=2)}")
            elif original_type in self.typedef_types:
                base_type = self.typedef_types[original_type]
                # 递归检查 typedef 的基础类型
                base_type_info = None
                normalized_base = normalize_type(base_type)
                if normalized_base.startswith('struct '):
                    struct_type = normalized_base.split(' ')[1]
                    if struct_type in self.struct_info:
                        base_type_info = {
                            'type': 'struct',
                            'info': self.struct_info[struct_type]
                        }
                type_info = {
                    'type': 'typedef',
                    'base_type': base_type,
                    'base_type_info': base_type_info
                }
                logger.debug(f"Found typedef: {original_type} -> {base_type}")
            elif original_type in self.enum_types:
                type_info = {
                    'type': 'enum',
                    'info': self.enum_types[original_type]
                }
                logger.debug(f"Found enum type: {original_type}")
            
            if type_info:
                logger.debug(f"Type info found for {original_type}:")
                logger.debug(json.dumps(type_info, indent=2))
            else:
                logger.debug(f"No type info found for {original_type}")
            
            # 解析初始化值
            value = self._process_initializer(
                initializer=initializer,
                original_type=original_type,
                array_size=var_data['array_size'],
                type_info=type_info
            )
            
            if value is not None:
                var_data['value'] = value
        
        # 过滤掉 None 值
        filtered_data = {k: v for k, v in var_data.items() if v is not None}
        logger.debug(f"处理后的变量声明: {json.dumps(filtered_data, indent=2)}")
        return filtered_data
    
    def _categorize_variables(self, variable_definitions):
        """将变量分类到相应的列表中"""
        var_info = {
            'variables': [],  # 基本类型变量
            'struct_vars': [], # 结构体变量
            'pointer_vars': [], # 指针变量
            'array_vars': [],  # 数组变量
        }
        
        for var in variable_definitions.values():
            # 首先检查是否是指针
            if var.get('is_pointer'):
                var_info['pointer_vars'].append(var)
            # 然后检查是否是数组
            elif var.get('array_size') is not None:
                var_info['array_vars'].append(var)
            # 再检查是否是结构体
            elif var.get('original_type', '').startswith('struct '):
                var_info['struct_vars'].append(var)
            # 最后是基本类型
            else:
                var_info['variables'].append(var)
        
        return var_info
    
    def _is_extern_declaration(self, node):
        """检查是否是 extern 声明"""
        for child in node.children:
            if child.type == 'storage_class_specifier':
                storage_type = child.text.decode('utf8')
                if storage_type == 'extern':
                    logger.debug("Found extern declaration")
                    return True
        return False
    
    def _is_global_declaration(self, node):
        """检查是否是全局变量声明"""
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
    
    def _extract_type_info(self, node):
        """提取类型信息
        
        Args:
            node: 语法树节点
            
        Returns:
            tuple: (type_name, is_pointer, array_size)
        """
        logger.debug(f"Extracting type info from: {node.text.decode('utf8')}")
        
        # 先打印当前正在解析的节点的完整内容
        logger.debug(f"Node content: {node.text.decode('utf8')}")
        logger.debug(f"Node type: {node.type}")
        
        type_parts = []
        original_type = None
        
        for child in node.children:
            if child.type in ['primitive_type', 'sized_type_specifier', 'type_identifier']:
                type_text = child.text.decode('utf8')
                type_parts.append(type_text)
                logger.debug(f"Found type part: {type_text}")
                
                # 记录原始类型
                if not original_type:
                    if type_text in self.typedef_types:
                        original_type = self.typedef_types[type_text]
                    elif type_text in self.struct_types:
                        original_type = f"struct {type_text}"
                    else:
                        original_type = type_text
            
            elif child.type == 'struct_specifier':
                type_parts.append('struct')
                for struct_child in child.children:
                    if struct_child.type == 'type_identifier':
                        struct_type = struct_child.text.decode('utf8')
                        type_parts.append(struct_type)
                        if not original_type:
                            original_type = f"struct {struct_type}"
        
        type_str = ' '.join(type_parts)
        logger.debug(f"Extracted type: {type_str}")
        logger.debug(f"Original type: {original_type}")
        
        return {
            "type": type_str,
            "original_type": original_type
        }
    
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
            "pointer_level": None
        }
        
        if declarator.type == 'array_declarator':
            array_size, name = self._parse_array_dimensions(declarator)
            info['array_size'] = array_size
            info['name'] = name
            logger.debug(f"Found array: {name}[{array_size}]")
        
        elif declarator.type == 'pointer_declarator':
            info['is_pointer'] = True
            pointer_level = 0
            current = declarator
            
            while current and current.type == 'pointer_declarator':
                pointer_level += 1
                for child in current.children:
                    if child.type != 'pointer_declarator':
                        current = None
                        break
                    current = child
            
            info['pointer_level'] = pointer_level
            
            for child in declarator.children:
                if child.type == 'identifier':
                    info['name'] = child.text.decode('utf8')
                    break
            
            logger.debug(f"Found pointer: {info['name']} (level: {pointer_level})")
        
        elif declarator.type == 'identifier':
            info['name'] = declarator.text.decode('utf8')
            logger.debug(f"Found identifier: {info['name']}")
        
        return {k: v for k, v in info.items() if v is not None}
    
    def _process_initializer(self, initializer, original_type, array_size=None, type_info=None):
        """处理初始化器节点
        
        Args:
            initializer: 初始化器节点
            original_type: 原始类型名
            array_size: 数组维度（可选）
            type_info: 类型信息（可选）
        """
        def get_elements(node):
            """获取初始化列表中的元素"""
            if not node or node.type != 'initializer_list':
                return []
            return [child for child in node.children 
                    if child.type not in ['comment', ',', '{', '}', '[', ']']]

        def parse_number(node):
            """解析数字字面量"""
            if not node:
                return 0
            
            text = node.text.decode('utf8')
            try:
                return ExpressionParser.parse_number(text)
            except ValueError:
                # 如果不是直接的数字，尝试计算表达式
                expr = ExpressionParser.replace_variables(
                    text,
                    self.enum_types,
                    self.macro_definitions
                )
                return ExpressionParser.evaluate_expression(expr)

        def parse_basic_type(node, type_name):
            """解析基本类型值"""
            if not node:
                return 0
                
            # 处理字符串字面量
            if node.type == 'string_literal':
                text = node.text.decode('utf8').strip('"\'')
                return bytes(text, "utf-8").decode("unicode_escape")
            
            # 处理数字字面量或表达式
            if node.type in ['number_literal', 'binary_expression', 'identifier']:
                text = node.text.decode('utf8')
                expr_type = ExpressionParser.identify_expression_type(text)
                
                if expr_type == 'number':
                    return ExpressionParser.parse_number(text)
                elif expr_type == 'expression':
                    # 替换变量并计算表达式
                    expr = ExpressionParser.replace_variables(
                        text,
                        self.enum_types,
                        self.macro_definitions
                    )
                    return ExpressionParser.evaluate_expression(expr)
            
            # 处理初始化列表
            if node.type == 'initializer_list':
                elements = get_elements(node)
                if len(elements) == 1:
                    return parse_basic_type(elements[0], type_name)
                return [parse_basic_type(e, type_name) for e in elements]
            
            # 处理标识符（可能是指针或其他引用）
            if node.type == 'identifier':
                text = node.text.decode('utf8')
                if text == 'NULL':
                    return None
                return text
                
            # 处理取地址操作符
            if node.type == 'unary_expression' and '&' in node.text.decode('utf8'):
                elements = [child for child in node.children if child.type != '&']
                if elements:
                    return '&' + elements[0].text.decode('utf8')
                    
            return node.text.decode('utf8')

        def parse_struct_field(node, field_info):
            """解析结构体字段"""
            if not node or not field_info:
                return None if field_info.get('is_pointer') else 0

            field_type = field_info['type']
            
            # 处理指针字段
            if field_info.get('is_pointer'):
                if node.type == 'identifier' and node.text.decode('utf8') == 'NULL':
                    return None
                return node.text.decode('utf8')
            
            # 处理字符数组字段的字符串初始化
            if field_type == 'char' and field_info.get('array_size') and node.type == 'string_literal':
                text = node.text.decode('utf8').strip('"\'')
                return bytes(text, "utf-8").decode("unicode_escape")
            
            # 处理数组字段
            if field_info.get('array_size'):
                return parse_array_value(node, field_type, field_info['array_size'])
            
            # 处理匿名结构体字段
            if field_type == 'struct' and field_info.get('nested_fields'):
                if node.type == 'initializer_list':
                    result = {}
                    elements = get_elements(node)
                    nested_fields = field_info['nested_fields']
                    
                    for i, nested_field in enumerate(nested_fields):
                        if i < len(elements):
                            result[nested_field['name']] = parse_struct_field(elements[i], nested_field)
                        else:
                            result[nested_field['name']] = None if nested_field.get('is_pointer') else 0
                    
                    return result
            
            # 处理命名结构体字段
            if field_type.startswith('struct '):
                nested_type_info = get_type_info(field_type)
                if nested_type_info:
                    return parse_struct_value(node, nested_type_info['info'])
            
            # 处理基本类型字段
            return parse_basic_type(node, field_type)

        def parse_struct_value(node, struct_info):
            """解析结构体值"""
            if not node or not struct_info:
                return None

            result = {}
            elements = get_elements(node)
            fields = struct_info.get('fields', [])

            for i, field in enumerate(fields):
                if i < len(elements):
                    result[field['name']] = parse_struct_field(elements[i], field)
                else:
                    # 使用适当的默认值
                    result[field['name']] = None if field.get('is_pointer') else 0

            return result

        def parse_array_value(node, element_type, dimensions):
            """解析数组值
            
            Args:
                node: 初始化器节点
                element_type: 数组元素类型
                dimensions: 数组维度列表
            """
            if not node or not dimensions:
                return []
            
            # 特殊处理字符数组的字符串初始化
            if element_type == 'char' and node.type == 'string_literal':
                text = node.text.decode('utf8').strip('"\'')
                # 直接返回解码后的字符串，不转换为字符数组
                return bytes(text, "utf-8").decode("unicode_escape")
            
            # 处理初始化列表
            if node.type == 'initializer_list':
                elements = get_elements(node)
                result = []
                
                # 获取元素的类型信息
                element_type_info = get_type_info(element_type)
                
                # 处理每个初始化元素
                for element in elements:
                    if element_type_info:
                        # 结构体数组
                        if len(dimensions) > 1:
                            sub_array = parse_array_value(element, element_type, dimensions[1:])
                            result.append(sub_array)
                        else:
                            struct_value = parse_struct_value(element, element_type_info['info'])
                            result.append(struct_value)
                    else:
                        # 基本类型数组
                        if len(dimensions) > 1:
                            sub_array = parse_array_value(element, element_type, dimensions[1:])
                            result.append(sub_array)
                        else:
                            value = parse_basic_type(element, element_type)
                            result.append(value)
                
                return result
            
            # 处理单个值初始化
            if node.type in ['number_literal', 'identifier']:
                value = parse_basic_type(node, element_type)
                return [value]
            
            # 如果没有初始化值，返回空数组
            return []

        try:
            # 根据类型和维度选择解析方式
            if array_size:
                # 数组类型
                return parse_array_value(initializer, original_type, array_size)
            elif type_info and type_info['type'] == 'struct':
                # 结构体类型
                return parse_struct_value(initializer, type_info['info'])
            elif type_info and type_info['type'] == 'union':
                # 联合体类型
                elements = get_elements(initializer)
                if elements:
                    first_field = type_info['info'].get('fields', [])[0]
                    return {first_field['name']: parse_basic_type(elements[0], first_field['type'])}
            else:
                # 基本类型
                return parse_basic_type(initializer, original_type)
            
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
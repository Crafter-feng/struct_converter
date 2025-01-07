from logger_config import setup_logger
from utils import ExpressionParser, TreeSitterUtil
import json

logger = setup_logger('TypeParser')

class CTypeParser:
    """C语言声明解析器，负责解析类型定义、枚举和宏定义
    
    主要功能：
    1. 解析类型定义（typedef）
    2. 解析结构体（struct）和联合体（union）定义
    3. 解析枚举（enum）定义
    4. 解析宏（macro）定义
    5. 处理类型别名和基本类型
    
    用法示例：
    ```python
    parser = CTypeParser()
    declarations = parser.parse_declarations("source.c")
    
    # 访问解析结果
    typedefs = declarations['typedef_types']
    structs = declarations['struct_info']
    enums = declarations['enum_types']
    macros = declarations['macro_definitions']
    ```
    """

    # 定义基本类型集合
    BASIC_TYPES = {
        # 标准整型
        'char', 'short', 'int', 'long',
        'unsigned char', 'unsigned short', 'unsigned int', 'unsigned long',
        'signed char', 'signed short', 'signed int', 'signed long',
        
        # 固定宽度整型
            'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t',
            'int8_t', 'int16_t', 'int32_t', 'int64_t',
        
        # 浮点类型
        'float', 'double', 'long double',
        
        # 其他基本类型
        'void', 'bool', 'size_t'
    }
    
    # 定义类型别名映射
    TYPE_ALIASES = {
        # 无符号整型别名
        'u8': 'uint8_t',
        'u16': 'uint16_t',
        'u32': 'uint32_t',
        'u64': 'uint64_t',
        
        # 浮点类型别名
        'f32': 'float',
        'f64': 'double'
    }

    def __init__(self):
        """初始化类型解析器"""
        logger.info("Initializing CTypeParser")
        
        # 使用TreeSitterUtil
        self.ts_util = TreeSitterUtil()
        
        # 初始化类型映射
        self.c_type_mapping = self._init_type_mapping()
        
        # 初始化类型收集器
        self.reset_collectors()
        
    def _init_type_mapping(self):
        """初始化C类型映射"""
        # 基本类型映射（类型到自身的映射）
        type_mapping = {t: t for t in self.BASIC_TYPES}
        
        # 添加类型别名映射
        type_mapping.update(self.TYPE_ALIASES)
        
        return type_mapping
    
    def reset_collectors(self):
        """重置所有类型收集器"""
        self.typedef_types = {}
        self.struct_types = set()
        self.pointer_types = {}
        self.struct_info = {}
        self.enum_types = {}
        self.macro_definitions = {}
        self.union_types = set()
        self.union_info = {}
    
    def is_basic_type(self, type_name):
        """检查是否是基本类型
        
        Args:
            type_name: 类型名称
            
        Returns:
            bool: 是否是基本类型
        """
        return (
            type_name in self.BASIC_TYPES or
            type_name in self.TYPE_ALIASES
        )
    
    def parse_declarations(self, file_path):
        """解析C语言声明，包括类型定义、枚举和宏定义
        
        Args:
            file_path: 源文件路径
            
        Returns:
            dict: 解析结果，包含以下内容：
                - typedef_types: 类型定义映射
                - struct_types: 结构体类型列表
                - union_types: 联合体类型列表
                - pointer_types: 指针类型映射
                - struct_info: 结构体详细信息
                - union_info: 联合体详细信息
                - enum_types: 枚举类型定义
                - macro_definitions: 宏定义
        """
        logger.info(f"Parsing declarations from: {file_path}")
        
        # 使用TreeSitterUtil解析文件
        tree = self.ts_util.parse_file(file_path)
        
        # 重置收集器
        self.reset_collectors()
        
        # 从根节点开始遍历解析
        self._parse_tree(tree.root_node)
        
        # 过滤掉基本类型
        self.union_info = {k: v for k, v in self.union_info.items() 
                          if not self.is_basic_type(k)}
        
        return {
            'typedef_types': self.typedef_types,
            'struct_types': list(self.struct_types),
            'union_types': list(self.union_types),
            'pointer_types': self.pointer_types,
            'struct_info': self.struct_info,
            'union_info': self.union_info,
            'enum_types': self.enum_types,
            'macro_definitions': self.macro_definitions
        }
    
    def _parse_tree(self, node):
        """递归解析语法树节点"""
        if node.type == 'struct_specifier':
            # 只处理顶层结构体定义，不处理匿名结构体
            if not (node.parent and node.parent.type == 'field_declaration'):
                struct_info = self._parse_struct_definition(node)
                if struct_info:
                    struct_name, fields = struct_info
                    if struct_name:
                        # 从 struct_name 中提取基本名称
                        base_name = struct_name.replace('struct ', '')
                        # 只有非指针类型才添加到 struct_info 和 struct_types
                        if '*' not in base_name:
                            self.struct_info[struct_name] = {
                                'name': struct_name,
                                'fields': fields or []
                            }
                            self.struct_types.add(base_name)
                            logger.debug(f"Added struct type: {base_name}")
        
        # 根据节点类型进行相应的处理
        if node.type == 'type_definition':
            # 处理类型定义
            typedef_info = self._parse_typedef_declaration(node)
            if typedef_info and typedef_info['name']:
                self.typedef_types[typedef_info['name']] = typedef_info['type']
                # 只有非指针的结构体类型才添加到 struct_types
                if typedef_info.get('is_struct') and not typedef_info.get('is_pointer'):
                    base_name = typedef_info['type'].replace('struct ', '')
                    if '*' not in base_name:  # 再次确认不是指针类型
                        self.struct_types.add(base_name)
                        logger.debug(f"Added struct type from typedef: {base_name}")
                # 只有非指针的联合体类型才添加到 union_types
                elif typedef_info.get('is_union') and not typedef_info.get('is_pointer'):
                    base_name = typedef_info['type'].replace('union ', '')
                    if '*' not in base_name:  # 再次确认不是指针类型
                        self.union_types.add(base_name)
                        logger.debug(f"Added union type from typedef: {base_name}")
        
        elif node.type == 'union_specifier':
            # 处理联合体定义
            union_info = self._parse_union_definition(node)
            if union_info:
                union_name, fields = union_info
                if union_name and fields is not None:
                    self.union_info[union_name] = {
                        'name': union_name,
                        'fields': fields
                    }
                    self.union_types.add(union_name)
        
        elif node.type == 'enum_specifier':
            # 处理枚举定义
            enum_info = self._parse_enum_definition(node)
            if enum_info:
                enum_name, enum_values = enum_info
                if enum_name and enum_values:
                    self.enum_types[enum_name] = enum_values
        
        elif node.type == 'preproc_def':
            # 处理宏定义
            macro_info = self._parse_macro_definition(node)
            if macro_info:
                macro_name, macro_value = macro_info
                if macro_name and macro_value is not None:
                    self.macro_definitions[macro_name] = macro_value
                else:
                    logger.warning(f"Invalid macro definition: {macro_name} = {macro_value}")
        
        # 递归处理子节点
        for child in node.children:
            self._parse_tree(child)
    
    def _update_type_mapping(self, typedef_info):
        """更新类型映射，处理枚举、结构体和联合体的前缀
        
        Args:
            typedef_info: 包含类型定义信息的字典
        """
        typedef_name = typedef_info['name']
        base_type = typedef_info['type']
        
        # 检查是否是枚举类型
        if typedef_info['is_enum']:
            # 为枚举类型添加 'enum' 前缀
            if not base_type.startswith('enum '):
                typedef_info['type'] = f"enum {base_type}"
                logger.debug(f"Added enum prefix for {typedef_name}: {typedef_info['type']}")
        
        # 检查是否是结构体类型（不带前缀的）
        elif typedef_info['is_struct'] and not base_type.startswith('struct '):
            # 为结构体类型添加 'struct' 前缀
            typedef_info['type'] = f"struct {base_type}"
            logger.debug(f"Added struct prefix for {typedef_name}: {typedef_info['type']}")
        
        # 检查是否是联合体类型（不带前缀的）
        elif typedef_info['is_union'] and not base_type.startswith('union '):
            # 为联合体类型添加 'union' 前缀
            typedef_info['type'] = f"union {base_type}"
            logger.debug(f"Added union prefix for {typedef_name}: {typedef_info['type']}")
        
        # 更新类型映射
        self.typedef_types[typedef_name] = typedef_info['type']
        
        # 只有非指针的结构体类型才添加到 struct_types
        if typedef_info['is_struct'] and not typedef_info['is_pointer']:
            base_name = typedef_info['type'].replace('struct ', '')
            if '*' not in base_name:  # 再次确认不是指针类型
                self.struct_types.add(base_name)
                logger.debug(f"Added struct type: {base_name}")
        
        # 只有非指针的联合体类型才添加到 union_types
        elif typedef_info['is_union'] and not typedef_info['is_pointer']:
            base_name = typedef_info['type'].replace('union ', '')
            if '*' not in base_name:  # 再次确认不是指针类型
                self.union_types.add(base_name)
                logger.debug(f"Added union type: {base_name}")
        
        # 如果是指针类型，记录到 pointer_types
        if typedef_info['is_pointer']:
            base_type = typedef_info['type'].rstrip('*')
            self.pointer_types[typedef_info['name']] = base_type
            logger.debug(f"Added pointer type: {typedef_info['name']} -> {base_type}")

    def _parse_typedef_declaration(self, node):
        """解析typedef声明"""
        logger.info("\n=== Parsing Typedef Declaration ===")
        logger.debug(f"Node text: {node.text.decode('utf8')}")
        
        # 收集所有类型定义
        typedef_infos = []
        
        # 1. 获取基础类型信息
        base_type = None
        is_struct = False
        is_union = False
        is_enum = False
        
        # 2. 遍历节点获取类型信息
        for child in node.children:
            # 处理基本类型
            if child.type in ['primitive_type', 'sized_type_specifier', 'type_identifier']:
                if not base_type:  # 只取第一个类型标识符作为基类型
                    base_type = child.text.decode('utf8')
                    logger.debug(f"Found base type: {base_type}")
            
            # 处理结构体
            elif child.type == 'struct_specifier':
                is_struct = True
                # 获取结构体名称
                for struct_child in child.children:
                    if struct_child.type == 'type_identifier':
                        struct_name = struct_child.text.decode('utf8')
                        base_type = f"struct {struct_name}"
                        logger.debug(f"Found struct type: {base_type}")
                        break
            
            # 处理联合体
            elif child.type == 'union_specifier':
                is_union = True
                # 获取联合体名称
                union_name = None
                for child in node.children:
                    if child.type == 'type_identifier':
                        union_name = child.text.decode('utf8')
                        logger.info(f"Found union name: {union_name}")
                        break
            
            # 处理枚举类型
            elif child.type == 'enum_specifier':
                is_enum = True
                # 获取枚举名称
                for enum_child in child.children:
                    if enum_child.type == 'type_identifier':
                        enum_name = enum_child.text.decode('utf8')
                        logger.info(f"Found enum name: {enum_name}")
                        break
        
        # 3. 处理声明器列表
        declarators = []
        last_identifier = None
        
        for child in node.children:
            # 处理普通类型别名
            if child.type == 'type_identifier':
                # 保存最后一个标识符
                last_identifier = child
                if child.next_sibling is None:
                    declarators.append((child, False))
                    logger.debug(f"Found type alias: {child.text.decode('utf8')}")
            
            # 处理指针类型
            elif child.type == 'pointer_declarator':
                # 获取指针层级和标识符
                current = child
                pointer_count = 0
                identifier = None
                
                while current:
                    if current.type == 'pointer_declarator':
                        pointer_count += 1
                        # 查找标识符或下一个指针声明器
                        for ptr_child in current.children:
                            if ptr_child.type == 'type_identifier':
                                identifier = ptr_child
                                break
                            elif ptr_child.type == 'pointer_declarator':
                                current = ptr_child
                                break
                        if identifier:
                            break
                        if not current.children:
                            break
                    else:
                        # 检查非指针声明器中的标识符
                        for ptr_child in current.children:
                            if ptr_child.type == 'type_identifier':
                                identifier = ptr_child
                                break
                        break
                
                if identifier:
                    declarators.append((identifier, pointer_count))
                    logger.debug(f"Found pointer type: {identifier.text.decode('utf8')} with {pointer_count} levels")
            
            # 处理普通声明器
            elif child.type == 'declarator':
                for decl_child in child.children:
                    if decl_child.type == 'type_identifier':
                        declarators.append((decl_child, False))
                        logger.debug(f"Found declarator: {decl_child.text.decode('utf8')}")
        
        # 如果没有找到声明器但有最后的标识符，将其添加为声明器
        if not declarators and last_identifier:
            declarators.append((last_identifier, False))
            logger.debug(f"Added last identifier as declarator: {last_identifier.text.decode('utf8')}")
        
        # 4. 为每个声明器创建类型信息
        for declarator, pointer_info in declarators:
            typedef_name = declarator.text.decode('utf8')
            typedef_info = {
                'name': typedef_name,
                'type': base_type,
                'is_struct': is_struct,
                'is_union': is_union,
                'is_enum': is_enum,
                'is_pointer': bool(pointer_info)
            }
            
            # 处理指针类型
            if pointer_info:
                if isinstance(pointer_info, int):
                    typedef_info['type'] = f"{base_type}{'*' * pointer_info}"
                    self.pointer_types[typedef_name] = base_type
            
            # 更新类型映射
            self._update_type_mapping(typedef_info)
            
            typedef_infos.append(typedef_info)
            logger.info(f"Added typedef: {json.dumps(typedef_info, indent=2)}")
        
        return typedef_infos[0] if typedef_infos else None
    
    def _parse_struct_definition(self, node):
        """解析结构体定义"""
        logger.info("\n=== Parsing Struct Definition ===")
        logger.debug(f"Node text: {node.text.decode('utf8')}")
        
        struct_name = None
        fields = []
        
        # 1. 获取结构体名称
        for child in node.children:
            if child.type == 'type_identifier':
                base_name = child.text.decode('utf8')
                struct_name = f"struct {base_name}"  # 只添加一次 struct 前缀
                logger.info(f"Found struct name: {struct_name}")
                break
        
        # 2. 检查是否是 typedef 中的结构体
        if not struct_name and node.parent and node.parent.type == 'type_definition':
            for sibling in node.parent.children:
                if sibling.type == 'type_identifier' and sibling != node:
                    base_name = sibling.text.decode('utf8')
                    struct_name = f"struct {base_name}"
                    logger.info(f"Found typedef struct name: {struct_name}")
                    break
        
        # 3. 检查是否是匿名结构体
        if not struct_name:
            anon_name = f"anonymous_struct_{id(node)}"
            struct_name = f"struct {anon_name}"
            logger.info(f"Generated name for anonymous struct: {struct_name}")
        
        # 4. 检查字段列表
        for child in node.children:
            if child.type == 'field_declaration_list':
                logger.debug("Processing field declaration list")
                for field_node in child.children:
                    if field_node.type == 'field_declaration':
                        field_info = self._parse_field(field_node)
                        if field_info and field_info['name']:  # 确保字段有名称
                            fields.append(field_info)
                            logger.info(f"Added field: {json.dumps(field_info, indent=2)}")
        
        logger.info(f"Completed parsing struct {struct_name}")
        logger.debug(f"Fields: {json.dumps(fields, indent=2)}")
        
        return struct_name, fields
    
    def _parse_union_definition(self, node):
        """解析联合体定义
        
        Args:
            node: 联合体定义节点 (union_specifier)
            
        Returns:
            tuple: (union_name, fields)
                - union_name: 联合体名称
                - fields: 字段列表
        """
        logger.info("\n=== Parsing Union Definition ===")
        logger.debug(f"Node type: {node.type}")
        logger.debug(f"Node text: {node.text.decode('utf8')}")
        
        # 1. 获取联合体名称
        union_name = None
        for child in node.children:
            if child.type == 'type_identifier':
                union_name = child.text.decode('utf8')
                logger.info(f"Found union name: {union_name}")
                break
        
        # 处理匿名联合体
        if not union_name:
            if node.parent and node.parent.type == 'type_definition':
                # 在typedef中查找名称
                for sibling in node.parent.children:
                    if sibling.type == 'type_identifier' and sibling != node:
                        union_name = sibling.text.decode('utf8')
                        logger.info(f"Found typedef name for anonymous union: {union_name}")
                        break
            else:
                # 生成唯一的匿名联合体名称
                union_name = f"anonymous_union_{id(node)}"
                logger.info(f"Generated name for anonymous union: {union_name}")
        
        # 2. 检查是否是前向声明
        has_field_list = False
        for child in node.children:
            if child.type == 'field_declaration_list':
                has_field_list = True
                break
        
        if not has_field_list:
            logger.info(f"Found forward declaration for union: {union_name}")
            return union_name, []
        
        # 3. 解析字段列表
        fields = []
        for child in node.children:
            if child.type == 'field_declaration_list':
                logger.debug("Processing field declaration list")
                # 遍历字段声明列表中的所有节点
                for field_node in child.children:
                    if field_node.type == 'field_declaration':
                        logger.debug(f"Processing field: {field_node.text.decode('utf8')}")
                        field_info = self._parse_field(field_node)
                        if field_info:
                            fields.append(field_info)
                            logger.info(f"Added field: {json.dumps(field_info, indent=2)}")
        
        # 4. 记录结果
        logger.info(f"Completed parsing union {union_name}")
        logger.info(f"Total fields: {len(fields)}")
        logger.debug(f"Full union info: {json.dumps({'name': union_name, 'fields': fields}, indent=2)}")
        
        return union_name, fields

    def _parse_enum_definition(self, node):
        """解析枚举定义
        
        Args:
            node: 枚举说明符节点
            
        Returns:
            tuple: (enum_name, enum_values)
                - enum_name: 枚举类型名称
                - enum_values: 枚举值字典，key为枚举名，value为对应的值
        """
        enum_name = None
        enum_values = {}
        current_value = 0
        
        # 获取枚举名称
        for child in node.children:
            if child.type == 'type_identifier':
                enum_name = child.text.decode('utf8')
                break
        
        # 如果没有找到名称，可能是匿名枚举
        if not enum_name and node.parent and node.parent.type == 'type_definition':
            for sibling in node.parent.children:
                if sibling.type == 'type_identifier' and sibling != node:
                    enum_name = sibling.text.decode('utf8')
                    break
        
        # 获取枚举值列表
        for child in node.children:
            if child.type == 'enumerator_list':
                for enumerator in child.children:
                    if enumerator.type == 'enumerator':
                        name = None
                        value = None
                        has_explicit_value = False
                        is_parsed_value = False
                        
                        # 获取枚举器名称和值
                        for enum_child in enumerator.children:
                            if enum_child.type == 'identifier':
                                name = enum_child.text.decode('utf8')
                            # 扩展表达式类型的处理
                            elif enum_child.type in [
                                'number_literal', 'hex_literal', 'octal_literal',
                                'decimal_literal', 'binary_expression', 'identifier',
                                'preproc_arg', 'unary_expression'
                            ]:
                                has_explicit_value = True
                                try:
                                    text = enum_child.text.decode('utf8').strip()
                                    # 处理括号表达式
                                    if text.startswith('(') and text.endswith(')'):
                                        text = text[1:-1].strip()
                                    
                                    # 将当前已解析的当前枚举和全局枚举一起传入
                                    if enum_values:
                                        self.enum_types[enum_name] = enum_values

                                    
                                    # 使用 ExpressionParser 处理值
                                    value, value_type = ExpressionParser.parse(
                                    text,
                                    self.enum_types,
                                    self.macro_definitions
                                )
                                    
                                    # 解析不出来的结果保持原样
                                    if value_type == 'number' and isinstance(value, (int, float)):
                                        is_parsed_value = True
                                        logger.debug(f"Parsed enum value: {name} = {value}")
                                    else:
                                        logger.error(f"Invalid enum value (non-numeric): {text}")
                                        value = text
                                except Exception as e:
                                    logger.error(f"Error parsing enum value: {text}, error: {e}")
                                    value = text
                        
                        if name:
                            if has_explicit_value:
                                # 使用显式指定的值
                                enum_values[name] = value
                                if is_parsed_value:
                                    current_value = value + 1
                            else:
                                # 使用当前值并递增
                                if isinstance(value, (int, float)):
                                    enum_values[name] = current_value
                                    current_value += 1
                                else:
                                    enum_values[name] = None
        
                            logger.debug(f"Parsed enum value: {name} = {enum_values[name]}")
        
        if enum_name:
            logger.info(f"Parsed enum {enum_name} with values: {enum_values}")
        
        return enum_name, enum_values

    def _parse_macro_definition(self, node):
        """解析宏定义"""
        macro_name = None
        macro_value = None
        
        # 获取宏名称和值
        for child in node.children:
            if child.type == 'identifier':
                if not macro_name:
                    macro_name = child.text.decode('utf8')
            elif child.type in [
                'preproc_arg', 'number_literal', 'binary_expression',
                'hex_literal', 'octal_literal', 'decimal_literal',
                'string_literal', 'char_literal'
            ]:
                text = child.text.decode('utf8').strip()
                
                # 处理括号表达式
                if text.startswith('(') and text.endswith(')'):
                    text = text[1:-1].strip()
                
                # 使用 ExpressionParser 处理值
                value, value_type = ExpressionParser.parse(
                    text,
                    self.enum_types,
                    self.macro_definitions
                )
                
                # 根据类型设置值
                if value_type == 'number':
                    macro_value = value
                elif value_type == 'string':
                    # 保持字符串字面量的引号
                    macro_value = text if text.startswith(("'", '"')) else f'"{text}"'
                else:
                    # 如果是表达式，尝试计算结果
                    try:
                        result = ExpressionParser.evaluate_expression(text)
                        if isinstance(result, (int, float)):
                            macro_value = result
                        else:
                            macro_value = text
                    except:
                        macro_value = text
        
        return macro_name, macro_value

    def _parse_field(self, node):
        """解析结构体字段"""
        field_info = {
            'name': None,
            'type': None,
            'array_size': None,
            'original_type': None,
            'pointer_type': None,
            'bit_field': None,
            'nested_fields': None
        }
        
        # 1. 获取字段名称
        for child in node.children:
            if child.type == 'field_identifier':
                field_info['name'] = child.text.decode('utf8')
                break
        
        # 2. 处理类型
        for child in node.children:
            if child.type in ['primitive_type', 'sized_type_specifier', 'type_identifier']:
                type_name = child.text.decode('utf8')
                field_info['type'] = type_name
                field_info['original_type'] = type_name
            elif child.type == 'struct_specifier':
                # 处理结构体类型
                struct_name = None
                nested_fields = []
                
                # 检查是否有名称（命名结构体引用）
                for struct_child in child.children:
                    if struct_child.type == 'type_identifier':
                        base_name = struct_child.text.decode('utf8')
                        struct_name = f"struct {base_name}"
                        field_info['type'] = struct_name
                        field_info['original_type'] = struct_name
                        break
                    
                # 检查是否有字段列表（匿名结构体）
                for struct_child in child.children:
                    if struct_child.type == 'field_declaration_list':
                        # 解析嵌套字段
                        for field_node in struct_child.children:
                            if field_node.type == 'field_declaration':
                                nested_field = self._parse_field(field_node)
                                if nested_field and nested_field['name']:
                                    nested_fields.append(nested_field)
                        
                        # 设置匿名结构体字段
                        if nested_fields:
                            field_info['nested_fields'] = nested_fields
                            field_info['type'] = 'struct'
                            field_info['original_type'] = 'struct'
                        break
        
        # 3. 处理指针
        current = None
        for child in node.children:
            if child.type == 'pointer_declarator':
                current = child
                pointer_count = 0
                
                # 计算指针层级
                while current:
                    if current.type == 'pointer_declarator':
                        pointer_count += 1
                        # 查找下一个指针声明器
                        next_ptr = None
                        for ptr_child in current.children:
                            if ptr_child.type == 'pointer_declarator':
                                next_ptr = ptr_child
                                break
                        current = next_ptr
                    else:
                        break
            
                # 设置指针类型
                if pointer_count > 0:
                    base_type = field_info['type']
                    # 设置最后一级指针类型
                    field_info['pointer_type'] = f"{base_type}{'*' * (pointer_count - 1)}"
                    # 设置完整类型
                    field_info['type'] = f"{base_type}{'*' * pointer_count}"
                
                # 检查指针声明器中的字段名
                for ptr_child in child.children:
                    if ptr_child.type == 'field_identifier':
                        field_info['name'] = ptr_child.text.decode('utf8')
                        break
        
        # 4. 处理数组
        for child in node.children:
            if child.type == 'array_declarator':
                array_sizes, array_name = self._parse_array_dimensions(child)
                if array_sizes:
                    field_info['array_size'] = array_sizes
                if array_name:
                    field_info['name'] = array_name
        
        return field_info
    
    def _parse_array_dimensions(self, declarator):
        """解析数组维度"""
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
                
                if child.type in [
                    'number_literal',
                    'hex_literal',
                    'octal_literal',
                    'decimal_literal',
                    'binary_expression',
                    'identifier',
                    'preproc_arg'
                ]:
                    # 固定大小，传入枚举和宏定义
                    value, _ = ExpressionParser.parse(
                        child.text.decode('utf8'),
                        self.enum_types,
                        self.macro_definitions
                    )
                    if isinstance(value, (int, float)):
                        array_sizes.append(int(value))
                        size_found = True
                        logger.debug(f"Found fixed size {value}")
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

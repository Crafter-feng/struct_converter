from utils.logger_config import setup_logger
from utils import ExpressionParser, TreeSitterUtil
import json
from .type_manager import TypeManager

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
    def __init__(self):
        """初始化类型解析器"""
        logger.info("Initializing CTypeParser")
        self.ts_util = TreeSitterUtil()
        self.type_manager = TypeManager()

    def parse_declarations(self, file_path=None, tree=None):
        """解析C语言声明"""
        logger.info(f"开始解析文件: {file_path}")
        
        if not tree:
            logger.info("使用 TreeSitterUtil 解析文件")
            tree = self.ts_util.parse_file(file_path)

        if not tree:
            logger.error(f"文件解析失败: {file_path}")
            return None
        
        logger.info("开始遍历语法树")
        self._parse_tree(tree.root_node)
        
        # 输出解析结果统计
        type_info = self.type_manager.export_type_info()
        logger.info("解析完成，统计信息:")
        logger.info(f"- 类型定义(typedef): {len(type_info['typedef_types'])} 个")
        logger.info(f"- 结构体(struct): {len(type_info['struct_types'])} 个")
        logger.info(f"- 联合体(union): {len(type_info['union_types'])} 个")
        logger.info(f"- 枚举(enum): {len(type_info['enum_types'])} 个")
        logger.info(f"- 指针类型: {len(type_info['pointer_types'])} 个")
        
        return type_info
    
    def _parse_tree(self, node):
        """递归解析语法树节点"""
        logger.debug(f"解析节点: {node.type}")
        
        if node.type == 'struct_specifier':
            if not (node.parent and node.parent.type == 'field_declaration'):
                logger.info("发现结构体定义")
                struct_info = self._parse_struct_definition(node)
                if struct_info:
                    struct_name, fields = struct_info
                    if struct_name:
                        base_name = struct_name.replace('struct ', '')
                        if '*' not in base_name:
                            struct_type_info = {
                                'name': struct_name,
                                'fields': fields or []
                            }
                            self.type_manager.add_struct_type(base_name, struct_type_info)
                            logger.info(f"添加结构体类型: {base_name} (字段数: {len(fields)})")

        elif node.type == 'type_definition':
            logger.info("发现类型定义")
            typedef_info = self._parse_typedef_declaration(node)
            if typedef_info and typedef_info['name']:
                logger.info(f"处理类型定义: {typedef_info['name']} -> {typedef_info['type']}")
                
                # 更新类型别名
                self.type_manager.add_typedef_type(typedef_info['name'], typedef_info['type'])
                
                # 处理结构体类型定义
                if typedef_info.get('is_struct') and not typedef_info.get('is_pointer'):
                    base_name = typedef_info['type'].replace('struct ', '')
                    if '*' not in base_name:
                        struct_type_info = {
                            'name': f"struct {base_name}",
                            'fields': []
                        }
                        self.type_manager.add_struct_type(base_name, struct_type_info, is_typedef=True)
                        logger.info(f"添加结构体类型定义: {base_name}")
                
                # 处理联合体类型定义
                elif typedef_info.get('is_union') and not typedef_info.get('is_pointer'):
                    base_name = typedef_info['type'].replace('union ', '')
                    if '*' not in base_name:
                        union_type_info = {
                            'name': f"union {base_name}",
                            'fields': []
                        }
                        self.type_manager.add_union_type(base_name, union_type_info, is_typedef=True)
                        logger.info(f"添加联合体类型定义: {base_name}")
                
                # 处理指针类型
                if typedef_info.get('is_pointer'):
                    self.type_manager.add_pointer_type(typedef_info['name'], is_typedef=True)
                    logger.info(f"添加指针类型: {typedef_info['name']}")

        elif node.type == 'union_specifier':
            union_info = self._parse_union_definition(node)
            if union_info:
                union_name, fields = union_info
                if union_name and fields is not None:
                    union_type_info = {
                        'name': union_name,
                        'fields': fields
                    }
                    self.type_manager.add_union_type(union_name, union_type_info)
                    logger.debug(f"Added union type: {union_name}")

        elif node.type == 'enum_specifier':
            enum_info = self._parse_enum_definition(node)
            if enum_info:
                enum_name, enum_values = enum_info
                if enum_name and enum_values:
                    self.type_manager.add_enum_type(enum_name, enum_values)
                    logger.debug(f"Added enum type: {enum_name}")

        elif node.type == 'preproc_def':
            macro_info = self._parse_macro_definition(node)
            if macro_info:
                macro_name, macro_value = macro_info
                if macro_name and macro_value is not None:
                    self.type_manager.add_macro_definition(macro_name, macro_value)
                    logger.debug(f"Added macro: {macro_name}")

        # 递归处理子节点
        for child in node.children:
            self._parse_tree(child)

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
                        break
            
            # 处理联合体
            elif child.type == 'union_specifier':
                is_union = True
                # 获取联合体名称
                for union_child in child.children:
                    if union_child.type == 'type_identifier':
                        union_name = union_child.text.decode('utf8')
                        base_type = f"union {union_name}"
                        break
            
            # 处理枚举类型
            elif child.type == 'enum_specifier':
                is_enum = True
                # 获取枚举名称
                for enum_child in child.children:
                    if enum_child.type == 'type_identifier':
                        enum_name = enum_child.text.decode('utf8')
                        base_type = f"enum {enum_name}"
                        break
        
        # 3. 处理声明器列表
        declarators = []
        last_identifier = None
        
        for child in node.children:
            # 处理普通类型别名
            if child.type == 'type_identifier':
                last_identifier = child
                if child.next_sibling is None:
                    declarators.append((child, False))
            
            # 处理指针类型
            elif child.type == 'pointer_declarator':
                current = child
                pointer_count = 0
                identifier = None
                
                while current:
                    if current.type == 'pointer_declarator':
                        pointer_count += 1
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
                        for ptr_child in current.children:
                            if ptr_child.type == 'type_identifier':
                                identifier = ptr_child
                                break
                        break
                
                if identifier:
                    declarators.append((identifier, pointer_count))
            
            # 处理普通声明器
            elif child.type == 'declarator':
                for decl_child in child.children:
                    if decl_child.type == 'type_identifier':
                        declarators.append((decl_child, False))
        
        # 如果没有找到声明器但有最后的标识符，将其添加为声明器
        if not declarators and last_identifier:
            declarators.append((last_identifier, False))
        
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
                struct_name = f"struct {base_name}"
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
                        if field_info and field_info['name']:
                            fields.append(field_info)
                            logger.info(f"Added field: {json.dumps(field_info, indent=2)}")
        
        return struct_name, fields

    def _parse_union_definition(self, node):
        """解析联合体定义"""
        logger.info("\n=== Parsing Union Definition ===")
        logger.debug(f"Node text: {node.text.decode('utf8')}")
        
        union_name = None
        fields = []
        
        # 1. 获取联合体名称
        for child in node.children:
            if child.type == 'type_identifier':
                union_name = child.text.decode('utf8')
                logger.info(f"Found union name: {union_name}")
                break
        
        # 处理匿名联合体
        if not union_name:
            if node.parent and node.parent.type == 'type_definition':
                for sibling in node.parent.children:
                    if sibling.type == 'type_identifier' and sibling != node:
                        union_name = sibling.text.decode('utf8')
                        logger.info(f"Found typedef name for anonymous union: {union_name}")
                        break
            else:
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
        for child in node.children:
            if child.type == 'field_declaration_list':
                logger.debug("Processing field declaration list")
                for field_node in child.children:
                    if field_node.type == 'field_declaration':
                        field_info = self._parse_field(field_node)
                        if field_info:
                            fields.append(field_info)
                            logger.info(f"Added field: {json.dumps(field_info, indent=2)}")
        
        return union_name, fields

    def _parse_enum_definition(self, node):
        """解析枚举定义"""
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
                            elif enum_child.type in [
                                'number_literal', 'hex_literal', 'octal_literal',
                                'decimal_literal', 'binary_expression', 'identifier',
                                'preproc_arg', 'unary_expression'
                            ]:
                                has_explicit_value = True
                                try:
                                    text = enum_child.text.decode('utf8').strip()
                                    if text.startswith('(') and text.endswith(')'):
                                        text = text[1:-1].strip()
                                    
                                    value, value_type = ExpressionParser.parse(
                                        text,
                                        self.type_manager.get_enum_info(),
                                        self.type_manager.get_macro_definition()
                                    )
                                    
                                    if value_type == 'number' and isinstance(value, (int, float)):
                                        is_parsed_value = True
                                        current_value = value
                                    else:
                                        value = text
                                except Exception as e:
                                    logger.error(f"Error parsing enum value: {text}, error: {e}")
                                    value = text
                        
                        if name:
                            if has_explicit_value:
                                enum_values[name] = value
                                if is_parsed_value:
                                    current_value = value + 1
                            else:
                                enum_values[name] = current_value
                                current_value += 1
        
        return enum_name, enum_values

    def _parse_macro_definition(self, node):
        """解析宏定义"""
        macro_name = None
        macro_value = None
        
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
                
                if text.startswith('(') and text.endswith(')'):
                    text = text[1:-1].strip()
                
                value, value_type = ExpressionParser.parse(
                    text,
                    self.type_manager.get_enum_info(),
                    self.type_manager.get_macro_definition()
                )
                
                if value_type == 'number':
                    macro_value = value
                elif value_type == 'string':
                    macro_value = text if text.startswith(("'", '"')) else f'"{text}"'
                else:
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
        """解析结构体/联合体字段"""
        try:
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
                    struct_name = None
                    nested_fields = []
                    
                    for struct_child in child.children:
                        if struct_child.type == 'type_identifier':
                            base_name = struct_child.text.decode('utf8')
                            struct_name = f"struct {base_name}"
                            field_info['type'] = struct_name
                            field_info['original_type'] = struct_name
                            break
                        
                    for struct_child in child.children:
                        if struct_child.type == 'field_declaration_list':
                            for field_node in struct_child.children:
                                if field_node.type == 'field_declaration':
                                    nested_field = self._parse_field(field_node)
                                    if nested_field and nested_field['name']:
                                        nested_fields.append(nested_field)
                            
                            if nested_fields:
                                field_info['nested_fields'] = nested_fields
                                field_info['type'] = 'struct'
                                field_info['original_type'] = 'struct'
                            break
            
            # 3. 处理指针
            for child in node.children:
                if child.type == 'pointer_declarator':
                    current = child
                    pointer_count = 0
                    
                    while current:
                        if current.type == 'pointer_declarator':
                            pointer_count += 1
                            next_ptr = None
                            for ptr_child in current.children:
                                if ptr_child.type == 'pointer_declarator':
                                    next_ptr = ptr_child
                                    break
                            current = next_ptr
                        else:
                            break
                    
                    if pointer_count > 0:
                        base_type = field_info['type']
                        field_info['pointer_type'] = f"{base_type}{'*' * (pointer_count - 1)}"
                        field_info['type'] = f"{base_type}{'*' * pointer_count}"
                    
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
            
            # 5. 处理位域
            for child in node.children:
                if child.type == 'bitfield_clause':
                    for bitfield_child in child.children:
                        if bitfield_child.type == ':':
                            continue
                        elif bitfield_child.type in [
                            'number_literal', 'hex_literal', 'octal_literal',
                            'decimal_literal', 'binary_expression', 'identifier',
                            'preproc_arg', 'unary_expression'
                        ]:
                            try:
                                text = bitfield_child.text.decode('utf8').strip()
                                if text.startswith('(') and text.endswith(')'):
                                    text = text[1:-1].strip()
                                
                                value, value_type = ExpressionParser.parse(
                                    text,
                                    self.type_manager.get_enum_info(),
                                    self.type_manager.get_macro_definition()
                                )
                                
                                if value_type == 'number' and isinstance(value, int):
                                    field_info['bit_field'] = value
                                else:
                                    field_info['bit_field'] = text
                            except Exception as e:
                                logger.error(f"Error parsing bit_field value: {text}, error: {e}")
                                field_info['bit_field'] = text
            
            logger.debug(f"解析字段: {field_info['name']} (类型: {field_info['type']})")
            if field_info['array_size']:
                logger.debug(f"- 数组大小: {field_info['array_size']}")
            if field_info['bit_field']:
                logger.debug(f"- 位域大小: {field_info['bit_field']}")
            if field_info['nested_fields']:
                logger.debug(f"- 嵌套字段数: {len(field_info['nested_fields'])}")
            
            return field_info
            
        except Exception as e:
            logger.error(f"字段解析错误: {str(e)}")
            return None

    def _parse_array_dimensions(self, declarator):
        """解析数组维度"""
        array_sizes = []
        name = None
        current = declarator
        
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
        
        name = find_identifier(declarator)
        logger.debug(f"Found array name: {name}")
        
        while current and current.type == 'array_declarator':
            size_found = False
            next_declarator = None
            
            for child in current.children:
                if child.type == '[' or child.type == ']':
                    continue
                elif child.type == 'array_declarator':
                    next_declarator = child
                    continue
                elif child.type in ['identifier', 'field_identifier']:
                    continue
                
                if child.type in [
                    'number_literal', 'hex_literal', 'octal_literal',
                    'decimal_literal', 'binary_expression', 'identifier',
                    'preproc_arg'
                ]:
                    value, _ = ExpressionParser.parse(
                        child.text.decode('utf8'),
                        self.type_manager.get_enum_info(),
                        self.type_manager.get_macro_definition()
                    )
                    if isinstance(value, (int, float)):
                        array_sizes.append(int(value))
                        size_found = True
                elif child.type == 'identifier' and child.text.decode('utf8') != name:
                    size_var = child.text.decode('utf8')
                    array_sizes.append(f"var({size_var})")
                    size_found = True
            
            if not size_found:
                array_sizes.append("dynamic")
            
            current = next_declarator
        
        array_sizes.reverse()
        return array_sizes, name

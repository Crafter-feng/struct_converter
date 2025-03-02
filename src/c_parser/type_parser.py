import hashlib
from typing import Dict, Any, Optional, List, Tuple, Union
from pathlib import Path
import json
from tree_sitter import Node
from utils.logger import logger 
from .core.type_manager import TypeManager
from .core.expression_parser import ExpressionParser
from .core.tree_sitter_utils import TreeSitterUtils
import re

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
        # 创建命名日志器
        self.logger = logger.bind(name="TypeParser")
        self.logger.info("=== Initializing CTypeParser ===")
        
        # 初始化组件
        self.ts_util = TreeSitterUtils()
        self.type_manager = TypeManager()
        
        # 配置
        self.pointer_size = 8  # 默认64位系统
        
        self.logger.info("Type parser initialized successfully")

    def parse_declarations(self, source: Union[str, Path], tree=None) -> Dict[str, Any]:
        """解析C语言声明"""
        try:
            self.logger.info(f"开始解析文件: {source}")
            
            # 读取源文件
            if isinstance(source, Path):
                try:
                    self.current_file = str(source)
                    text = source.read_text(encoding='utf-8')
                    self.logger.debug(f"成功读取文件: {source}")
                except Exception as e:
                    self.logger.error(f"读取文件失败: {source}, 错误: {e}")
                    return None
                    
                # 解析包含的头文件
                includes = self._parse_includes(text)
                self.logger.debug(f"发现包含文件: {includes}")
                
                for include in includes:
                    try:
                        include_path = source.parent / include
                        if include_path.exists():
                            self.logger.info(f"解析包含文件: {include}")
                            self.current_file = str(include_path)
                            self.parse_declarations(include_path)
                        else:
                            self.logger.warning(f"包含文件不存在: {include}")
                    except Exception as e:
                        self.logger.warning(f"解析包含文件失败: {include}, 错误: {e}")
            else:
                text = source
                self.current_file = "input_source"
                
            # 解析为AST
            if not tree:
                self.logger.info("使用 TreeSitterUtil 解析文件")
                try:
                    tree = self.ts_util.parse_file(text if isinstance(source, str) else str(source))
                    if tree:
                        self.logger.debug("语法树解析成功")
                    else:
                        self.logger.error("语法树解析失败")
                except Exception as e:
                    self.logger.error(f"语法树解析出错: {e}")
                    return None

            if not tree:
                self.logger.error(f"文件解析失败: {source}")
                return None
            
            self.logger.info("开始遍历语法树")
            try:
                self._parse_tree(tree)
                self.logger.debug("语法树遍历完成")
            except Exception as e:
                self.logger.error(f"语法树遍历出错: {e}")
                return None
            
            # 输出解析结果统计
            try:
                type_info = self.type_manager.export_type_info()
                self.logger.info("=== Parsing completed ===")
                self.logger.debug(f"解析结果: {json.dumps(type_info, indent=2)}")

                self.logger.info("解析完成，统计信息:")
                self.logger.info(f"- 类型定义(typedef): {len(type_info['typedef_types'])} 个")
                self.logger.info(f"- 结构体(struct): {len(type_info['struct_types'])} 个")
                self.logger.info(f"- 联合体(union): {len(type_info['union_types'])} 个")
                self.logger.info(f"- 枚举(enum): {len(type_info['enum_types'])} 个")
                self.logger.info(f"- 指针类型: {len(type_info['pointer_types'])} 个")
                self.logger.info(f"- 宏定义: {len(type_info['macro_definitions'])} 个")

                return type_info
                
            except Exception as e:
                self.logger.exception(f"导出类型信息失败: {e}")
                return None
                
        except Exception as e:
            self.logger.exception(f"解析过程发生错误: {e}")
            return None
    
    def _parse_tree(self, node):
        """递归解析语法树节点"""
        self.logger.debug(f"解析节点: {node.type}")
        if node.type == 'struct_specifier':
            self._parse_struct_definition(node)
        elif node.type == 'type_definition':
            self._parse_typedef_declaration(node)
        elif node.type == 'union_specifier':
            self._parse_union_definition(node)
        elif node.type == 'enum_specifier':
            self._parse_enum_definition(node)
        elif node.type == 'preproc_def':
            self._parse_macro_definition(node)
        elif node.type == 'translation_unit' or node.type == 'preproc_ifdef':
            # 递归处理子节点
            for child in node.children:
                self._parse_tree(child)
        elif node.type == 'preproc_if':
            # 递归处理子节点
            for child in node.children:
                self._parse_tree(child)
        elif node.type == 'preproc_else':
            # 递归处理子节点
            for child in node.children:
                self._parse_tree(child)
        else:
            self.logger.debug(f"Skipping node: {node.type} (text: {node.text.decode('utf8')})")


    def _parse_typedef_declaration(self, node):
        """解析typedef声明"""
        self.logger.info("\n=== Parsing Typedef Declaration ===")
        self.logger.debug(f"Node text: {node.text.decode('utf8')}")
        
        # 收集所有类型定义
        typedef_infos = []
        
        # 1. 获取基础类型信息
        base_type = None
        real_type = None

        declarators = []
        
        # 添加类型限定符信息
        type_qualifiers = {
            'is_const': False,
            'is_volatile': False,
            'is_restrict': False,
            'storage_class': None
        }
        
        # 2. 遍历节点获取类型信息
        for child in node.children:
            # 处理类型限定符
            if child.type == 'type_qualifier':
                qualifier = child.text.decode('utf8')
                if qualifier == 'const':
                    type_qualifiers['is_const'] = True
                elif qualifier == 'volatile':
                    type_qualifiers['is_volatile'] = True
                elif qualifier == 'restrict':
                    type_qualifiers['is_restrict'] = True
            
            # 处理存储类型
            elif child.type == 'storage_class_specifier':
                type_qualifiers['storage_class'] = child.text.decode('utf8')
            
            # 处理基本类型
            elif child.type in ['primitive_type', 'sized_type_specifier']:
                if not base_type:  # 只取第一个类型标识符作为基类型
                    real_type = 'base'
                    base_type = child.text.decode('utf8')
                    self.logger.debug(f"Found base type: {base_type}")
            
            # 处理结构体
            elif child.type == 'struct_specifier':
                real_type = 'struct'
                base_type, _ = self._parse_struct_definition(child)
            
            # 处理联合体
            elif child.type == 'union_specifier':
                real_type = 'union'
                # 获取联合体名称
                base_type, _ = self._parse_union_definition(child)
            
            # 处理枚举类型
            elif child.type == 'enum_specifier':
                real_type = 'enum'
                # 获取枚举名称
                base_type, _ = self._parse_enum_definition(child)                
            
            # 添加函数指针处理
            elif child.type == 'function_declarator':
                function_info = self._parse_function_pointer(child)
                if function_info:
                    base_type = function_info['return_type']
                    real_type = 'function_pointer'
                    
                    # 更新类型限定符
                    type_qualifiers.update(function_info['qualifiers'])
                    
                    # 构建函数指针类型字符串
                    param_types = []
                    for param in function_info['parameters']:
                        param_type = param['type']
                        if param['is_pointer']:
                            param_type += '*' * param['pointer_level']
                        param_types.append(param_type)
                    
                    if function_info['is_variadic']:
                        param_types.append('...')
                    
                    base_type = f"{base_type} (*) ({', '.join(param_types)})"
                    self.logger.debug(f"Found function pointer type: {base_type}")
            elif child.type == 'type_identifier':
                declarators.append((child, False))
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
        
        # 4. 为每个声明器创建类型信息
        for declarator, pointer_info in declarators:
            typedef_name = declarator.text.decode('utf8')
            typedef_info = {
                'kind': 'typedef',
                'name': typedef_name,
                'type': base_type,
                'base_type': base_type,
                'real_type': real_type,
                'function_info': function_info if 'function_info' in locals() else None,
                'qualifiers': type_qualifiers
            }
            
            # 处理指针类型
            if pointer_info:
                if isinstance(pointer_info, int):
                    typedef_info['type'] = f"{base_type}{'*' * pointer_info}"
            
            typedef_infos.append(typedef_info)
            self.logger.info(f"Added typedef: {json.dumps(typedef_info, indent=2)}")
        
            # 更新类型别名
            self._add_type_with_logging(typedef_name, typedef_info)
                
        return typedef_infos if typedef_infos else None

    def _parse_struct_definition(self, node):
        """解析结构体定义
        
        Args:
            node: 结构体定义节点
            
        Returns:
            (struct_name, fields): 结构体名称和字段列表
        """
        self.logger.info("\n=== Parsing Struct Definition ===")
        self.logger.debug(f"Node text: {node.text.decode('utf8')}")
        
        struct_name = None
        fields = []
        
        try:
            # 1. 获取结构体名称
            for child in node.children:
                if child.type == 'type_identifier':
                    base_name = child.text.decode('utf8')
                    # 检查是否已经包含 "struct" 前缀
                    if not base_name.startswith('struct '):
                        struct_name = f"struct {base_name}"
                    else:
                        struct_name = base_name
                    self.logger.info(f"Found struct name: {struct_name}")
                    break

            if not struct_name:
                start_point = node.start_point
                name_hash = hashlib.md5(node.text).hexdigest()[:6]
                struct_name = f"__anon_struct_{start_point[0]}_{start_point[1]}_{name_hash}"
                self.logger.debug(f"生成匿名结构体: {struct_name}")

            # 2. 解析字段列表
            for child in node.children:
                if child.type == 'field_declaration_list':
                    for field_node in child.children:
                        if field_node.type == 'field_declaration':
                            field_info = self._parse_field(field_node)
                            if field_info:
                                fields.append(field_info)
                                self.logger.debug(f"Added field: {field_info['name']}, type: {field_info.get('type')}")
            
            # 3. 检查字段有效性
            if fields:
                self.logger.info(f"解析到 {len(fields)} 个字段")
                for field in fields:
                    if field.get('bit_field') is not None:
                        self.logger.debug(f"字段 {field['name']} 是位域，大小: {field['bit_field']}")
                    if field.get('array_size'):
                        self.logger.debug(f"字段 {field['name']} 是数组，维度: {field['array_size']}")
                    if field.get('nested_fields'):
                        self.logger.debug(f"字段 {field['name']} 包含 {len(field['nested_fields'])} 个嵌套字段")
            else:
                self.logger.warning("未找到任何字段")
            
            # 获取属性和元数据
            attributes = {}
            comment = None

            
            # 尝试获取注释
            try:
                comment_node = node.prev_sibling
                if comment_node and comment_node.type == 'comment':
                    comment = comment_node.text.decode('utf8').strip('/* \n\t')
            except Exception as e:
                self.logger.warning(f"Failed to get comment: {e}")

            # 计算大小和对齐
            size_info = self._calc_struct_layout(fields)

            # 添加结构体类型并打印信息
            type_info = {
                'kind': 'struct',
                'name': struct_name,
                'fields': fields,
                'size': size_info['size'],
                'alignment': size_info['alignment'],
                'location': self._get_node_location(node),
                'attributes': attributes,
                'comment': comment
            }
            
            self._add_type_with_logging(struct_name, type_info)

            return struct_name, fields
            
        except Exception as e:
            self.logger.exception(f"结构体解析错误: {str(e)}")
            return None, None

    def _parse_union_definition(self, node):
        """解析联合体定义
        
        Args:
            node: 联合体定义节点
            
        Returns:
            (union_name, fields): 联合体名称和字段列表
        """
        self.logger.info("\n=== Parsing Union Definition ===")
        self.logger.debug(f"Node text: {node.text.decode('utf8')}")
        
        union_name = None
        fields = []
        
        try:
            # 1. 获取联合体名称
            for child in node.children:
                if child.type == 'type_identifier':
                    base_name = child.text.decode('utf8')
                    union_name = f"union {base_name}"
                    self.logger.info(f"Found union name: {union_name}")
                    break

            if not union_name:
                start_point = node.start_point
                name_hash = hashlib.md5(node.text).hexdigest()[:6]
                union_name = f"__anon_union_{start_point[0]}_{start_point[1]}_{name_hash}"
                self.logger.debug(f"生成匿名联合体: {union_name}")

            # 2. 解析字段列表
            for child in node.children:
                if child.type == 'field_declaration_list':
                    for field_node in child.children:
                        if field_node.type == 'field_declaration':
                            field_info = self._parse_field(field_node)
                            if field_info and field_info['name']:
                                fields.append(field_info)
                                self.logger.debug(f"Added field: {field_info['name']}")
            
            # 3. 检查字段有效性
            if fields:
                self.logger.info(f"解析到 {len(fields)} 个字段")
                for field in fields:
                    if field.get('bit_field') is not None:
                        self.logger.debug(f"字段 {field['name']} 是位域，大小: {field['bit_field']}")
                    if field.get('array_size'):
                        self.logger.debug(f"字段 {field['name']} 是数组，维度: {field['array_size']}")
                    if field.get('nested_fields'):
                        self.logger.debug(f"字段 {field['name']} 包含 {len(field['nested_fields'])} 个嵌套字段")
            else:
                self.logger.warning("未找到任何字段")
            
            # 获取属性和元数据
            attributes = {}
            comment = None

            union_info = {
                'kind': 'union',
                'name': union_name,
                'fields': fields,
                'size': self._calc_union_size(fields),
                'alignment': self._calc_union_alignment(fields),
                'location': self._get_node_location(node),
                'attributes': attributes,
                'comment': comment
            }

            self._add_type_with_logging(union_name, union_info)

            return union_name, fields    
                
        except Exception as e:
            self.logger.exception(f"联合体解析错误: {str(e)}")
            return None, None

    def _parse_enum_definition(self, node):
        """解析枚举定义
        
        Args:
            node: 枚举定义节点
            
        Returns:
            (enum_name, enum_values): 枚举名称和枚举值字典
        """
        self.logger.info("\n=== Parsing Enum Definition ===")
        self.logger.debug(f"Node text: {node.text.decode('utf8')}")
        
        enum_name = None
        enum_values = {}
        current_value = 0
        
        try:
            # 1. 获取枚举名称
            for child in node.children:
                if child.type == 'type_identifier':
                    base_name = child.text.decode('utf8')
                    enum_name = f"enum {base_name}"
                    self.logger.info(f"Found enum name: {enum_name}")
                    break
            
            # 2. 解析枚举值列表
            for child in node.children:
                if child.type == 'enumerator_list':
                    for enumerator in child.children:
                        if enumerator.type == 'enumerator':
                            enumerator_name = None
                            enumerator_value = current_value
                            
                            for enum_child in enumerator.children:
                                if enum_child.type == 'identifier':
                                    enumerator_name = enum_child.text.decode('utf8')
                                elif enum_child.type == 'number_literal':
                                    enumerator_value = int(enum_child.text.decode('utf8'))
                                elif enum_child.type == 'binary_expression':
                                    try:
                                        value, value_type = ExpressionParser.parse(
                                            enum_child.text.decode('utf8'),
                                            self.type_manager.get_enum_values(),
                                            self.type_manager.get_macro_definition()
                                        )
                                        if value_type == 'number' and isinstance(value, int):
                                            enumerator_value = value
                                        else:
                                            self.logger.warning(f"Invalid enumerator value: {enum_child.text.decode('utf8')}")
                                    except Exception as e:
                                        self.logger.exception(f"Error parsing enumerator value: {e}")
                            
                            if enumerator_name:
                                enum_values[enumerator_name] = enumerator_value
                                self.logger.debug(f"Added enumerator: {enumerator_name} = {enumerator_value}")
                                current_value = enumerator_value + 1
            
            # 3. 检查枚举值有效性
            if enum_values:
                self.logger.info(f"解析到 {len(enum_values)} 个枚举值")
            else:
                self.logger.warning("未找到任何枚举值")
            
            # 获取属性和元数据
            attributes = {}
            location = {'file': 'unknown', 'line': 0}
            comment = None
            
            # 尝试获取位置信息
            try:
                start_point = node.start_point
                location = {
                    'file': self.current_file,
                    'line': start_point[0] + 1
                }
            except Exception as e:
                self.logger.exception(f"Failed to get location info: {e}")
            
            # 尝试获取注释
            try:
                comment_node = node.prev_sibling
                if comment_node and comment_node.type == 'comment':
                    comment = comment_node.text.decode('utf8').strip('/* \n\t')
            except Exception as e:
                self.logger.exception(f"Failed to get comment: {e}")
            
            # 添加枚举类型并打印信息
            self._add_type_with_logging(enum_name, {
                'kind': 'enum',
                'name': enum_name,
                'values': enum_values,
                'size': 4,  # 通常枚举类型是int大小
                'alignment': 4,
                'location': location,
                'comment': comment
            })

            return enum_name, enum_values
            
        except Exception as e:
            self.logger.exception(f"枚举解析错误: {str(e)}")
            return None, None

    def _parse_macro_definition(self, node):
        """解析宏定义
        
        Args:
            node: 宏定义节点
            
        Returns:
            (macro_name, macro_value): 宏名称和值
        """
        self.logger.info("\n=== Parsing Macro Definition ===")
        self.logger.debug(f"Node text: {node.text.decode('utf8')}")
        
        macro_name = None
        macro_value = None
        
        try:
            # 1. 获取宏名称
            for child in node.children:
                if child.type == 'identifier':
                    if not macro_name:
                        macro_name = child.text.decode('utf8')
                        self.logger.info(f"Found macro name: {macro_name}")
                        break
            
            # 2. 解析宏值
            for child in node.children:
                if child.type in [
                    'preproc_arg', 'number_literal', 'binary_expression',
                    'hex_literal', 'octal_literal', 'decimal_literal',
                    'string_literal', 'char_literal'
                ]:
                    text = child.text.decode('utf8').strip()
                    self.logger.debug(f"Processing macro value: {text}")
                    
                    # 处理括号包围的表达式
                    if text.startswith('(') and text.endswith(')'):
                        text = text[1:-1].strip()
                    
                    try:
                        # 尝试解析表达式
                        value, value_type = ExpressionParser.parse(
                            text,
                            self.type_manager.get_enum_values(),
                            self.type_manager.get_macro_definition()
                        )
                        
                        if value_type == 'number':
                            macro_value = value
                            self.logger.debug(f"Parsed numeric value: {value}")
                        elif value_type == 'string':
                            macro_value = text if text.startswith(("'", '"')) else f'"{text}"'
                            self.logger.debug(f"Parsed string value: {macro_value}")
                        else:
                            self.logger.error(f"Expression evaluation failed: {text}")
                            macro_value = text
                            
                    except Exception as e:
                        self.logger.exception(f"Error parsing macro value: {text}, error: {e}")
                        macro_value = text
            
            if macro_name and macro_value is not None:
                self.logger.info(f"Successfully parsed macro: {macro_name} = {macro_value}")
            else:
                self.logger.warning("Incomplete macro definition")

            if macro_name and macro_value is not None:
                self.type_manager.add_macro_definition(macro_name, macro_value)
                self.logger.debug(f"Added macro: {macro_name}")

            return macro_name, macro_value
            
        except Exception as e:
            self.logger.exception(f"宏定义解析错误: {str(e)}")
            return None, None

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
                'nested_fields': None,
                'qualifiers': {  # 添加类型限定符信息
                    'is_const': False,
                    'is_volatile': False,
                    'is_restrict': False
                }
            }
            
            # 1. 获取字段名称
            for child in node.children:
                if child.type == 'field_identifier':
                    field_info['name'] = child.text.decode('utf8')
                    break
            
            # 2. 处理类型
            for child in node.children:
                # 处理类型限定符
                if child.type == 'type_qualifier':
                    qualifier = child.text.decode('utf8')
                    if qualifier == 'const':
                        field_info['qualifiers']['is_const'] = True
                    elif qualifier == 'volatile':
                        field_info['qualifiers']['is_volatile'] = True
                    elif qualifier == 'restrict':
                        field_info['qualifiers']['is_restrict'] = True
                    
                # 处理基本类型
                elif child.type in ['primitive_type', 'sized_type_specifier', 'type_identifier']:
                    type_name = child.text.decode('utf8')
                    field_info['type'] = type_name
                    field_info['original_type'] = type_name
                    
                # 处理嵌套类型
                elif child.type == 'struct_specifier':
                    nested_name, nested_fields = self._parse_struct_definition(child)
                    field_info['nested_type'] = nested_name
                    field_info['type'] = nested_name
                    field_info['nested_fields'] = nested_fields
                elif child.type == 'union_specifier':
                    nested_name, nested_fields = self._parse_union_definition(child)
                    field_info['nested_type'] = nested_name
                    field_info['type'] = nested_name
                    field_info['original_type'] = nested_name
                    field_info['nested_fields'] = nested_fields
            
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
                            value, expression = self._parse_bitfield_value(bitfield_child)
                            if value is not None:
                                field_info['bit_field'] = value
                                self.logger.debug(f"解析位域值: {value}")
                            else:
                                field_info['bit_field'] = expression
                                self.logger.warning(f"使用原始表达式作为位域值: {expression}")
            
            self.logger.debug(f"解析字段: {field_info['name']} (类型: {field_info['type']})")
            if field_info['array_size']:
                self.logger.debug(f"- 数组大小: {field_info['array_size']}")
            if field_info['bit_field']:
                self.logger.debug(f"- 位域大小: {field_info['bit_field']}")
            if field_info['nested_fields']:
                self.logger.debug(f"- 嵌套字段数: {len(field_info['nested_fields'])}")
            
            return field_info
            
        except Exception as e:
            self.logger.exception(f"字段解析错误: {str(e)}")
            return None

    def _parse_array_dimensions(self, declarator):
        """解析数组维度
        
        Args:
            declarator: 数组声明节点
            
        Returns:
            (array_sizes, name): 数组维度列表和数组名称
        """
        array_sizes = []
        name = None
        current = declarator
        
        def find_identifier(node):
            """递归查找标识符"""
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
        self.logger.debug(f"Found array name: {name}")
        
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
                
                # 处理数组大小表达式
                if child.type in [
                    'number_literal', 'hex_literal', 'octal_literal',
                    'decimal_literal', 'binary_expression', 'identifier',
                    'preproc_arg'
                ]:
                    try:
                        value, value_type = ExpressionParser.parse(
                            child.text.decode('utf8'),
                            self.type_manager.get_enum_values(),
                            self.type_manager.get_macro_definition()
                        )
                        
                        if isinstance(value, (int, float)):
                            array_sizes.append(int(value))
                            size_found = True
                            self.logger.debug(f"Found array size: {value}")
                        else:
                            self.logger.warning(f"Invalid array size value: {value}")
                    except Exception as e:
                        self.logger.exception(f"Error parsing array size: {e}")
                        
                # 处理变量大小数组
                elif child.type == 'identifier' and child.text.decode('utf8') != name:
                    size_var = child.text.decode('utf8')
                    array_sizes.append(f"var({size_var})")
                    size_found = True
                    self.logger.debug(f"Found variable array size: {size_var}")
            
            # 处理动态数组
            if not size_found:
                array_sizes.append("dynamic")
                self.logger.debug("Found dynamic array size")
            
            current = next_declarator
        
        # 反转维度列表以保持正确的顺序
        array_sizes.reverse()
        self.logger.debug(f"Final array dimensions: {array_sizes}")
        
        return array_sizes, name

    def _get_node_location(self, node: Node) -> Dict:
        """获取节点位置信息"""
        try:
            line, col = node.start_point
            return {
                'file': self.current_file,
                'line': line + 1,
                'column': col
            }
        except Exception as e:
            return {'file': self.current_file, 'line': 0}
        
    def _parse_includes(self, text: str) -> List[str]:
        """解析包含的头文件
        
        Args:
            text: 源代码文本
            
        Returns:
            包含文件路径列表
        """
        includes = []
        for line in text.splitlines():
            if line.strip().startswith('#include'):
                match = re.search(r'["<](.*?)[">]', line)
                if match:
                    includes.append(match.group(1))
        return includes 

    def _parse_function_pointer(self, node) -> Dict[str, Any]:
        """解析函数指针类型
        
        Args:
            node: 函数指针声明节点
            
        Returns:
            包含函数指针信息的字典
        """
        function_info = {
            'is_function_pointer': True,
            'return_type': None,
            'parameters': [],
            'is_variadic': False,
            'qualifiers': {
                'is_const': False,
                'is_volatile': False,
                'is_restrict': False
            }
        }
        
        # 解析返回类型
        return_type_node = next(
            (child for child in node.children if child.type in [
                'primitive_type', 'sized_type_specifier', 'type_identifier'
            ]),
            None
        )
        if return_type_node:
            function_info['return_type'] = return_type_node.text.decode('utf8')
        
        # 解析参数列表
        param_list = next(
            (child for child in node.children if child.type == 'parameter_list'),
            None
        )
        
        if param_list:
            for param in param_list.children:
                if param.type == 'parameter_declaration':
                    param_info = self._parse_parameter(param)
                    if param_info:
                        function_info['parameters'].append(param_info)
                elif param.type == '...':
                    function_info['is_variadic'] = True
        
        return function_info

    def _parse_parameter(self, node) -> Dict[str, Any]:
        """解析函数参数
        
        Args:
            node: 参数声明节点
            
        Returns:
            包含参数信息的字典
        """
        param_info = {
            'name': None,
            'type': None,
            'qualifiers': {
                'is_const': False,
                'is_volatile': False,
                'is_restrict': False
            },
            'is_pointer': False,
            'pointer_level': 0
        }
        
        # 解析参数类型
        for child in node.children:
            # 处理类型限定符
            if child.type == 'type_qualifier':
                qualifier = child.text.decode('utf8')
                if qualifier == 'const':
                    param_info['qualifiers']['is_const'] = True
                elif qualifier == 'volatile':
                    param_info['qualifiers']['is_volatile'] = True
                elif qualifier == 'restrict':
                    param_info['qualifiers']['is_restrict'] = True
            
            # 处理基本类型
            elif child.type in ['primitive_type', 'sized_type_specifier', 'type_identifier']:
                param_info['type'] = child.text.decode('utf8')
            
            # 处理指针
            elif child.type == 'pointer_declarator':
                param_info['is_pointer'] = True
                param_info['pointer_level'] += 1
                
                # 获取参数名称
                for ptr_child in child.children:
                    if ptr_child.type == 'identifier':
                        param_info['name'] = ptr_child.text.decode('utf8')
                        break
            
            # 处理参数名称
            elif child.type == 'identifier':
                param_info['name'] = child.text.decode('utf8')
        
        return param_info 

    def _parse_bitfield_value(self, node) -> Tuple[Optional[int], Optional[str]]:
        """解析位域值
        
        Args:
            node: 位域值节点
            
        Returns:
            (value, expression): 解析后的值和原始表达式
        """
        try:
            text = node.text.decode('utf8').strip()
            if text.startswith('(') and text.endswith(')'):
                text = text[1:-1].strip()
            
            # 尝试解析表达式
            value, value_type = ExpressionParser.parse(
                text,
                self.type_manager.get_enum_values(),
                self.type_manager.get_macro_definition()
            )
            
            # 检查值的有效性
            if value_type == 'number' and isinstance(value, int):
                if 0 <= value <= 64:  # 位域大小的合理范围
                    return value, text
                else:
                    self.logger.warning(f"位域大小超出合理范围: {value}")
                    return None, text
            else:
                self.logger.warning(f"位域值不是整数: {text}")
                return None, text
            
        except Exception as e:
            self.logger.exception(f"解析位域值失败: {text}, 错误: {e}")
            return None, text 

    def _calc_struct_layout(self, fields: List) -> Dict:
        """结构体布局计算"""
        max_align = 1
        current_offset = 0
        total_size = 1
        
        # for field in fields:
        #     type_info = self.type_manager.get_type_size_info(field['type'])
        #     size = type_info.get('size', 0) if type_info else 0
        #     align = type_info.get('alignment', 1) if type_info else 1
            
        #     padding = (-current_offset) % align
        #     current_offset += padding
        #     field['offset'] = current_offset
        #     current_offset += size
        #     max_align = max(max_align, align)
        
        # total_size = current_offset + (-current_offset) % max_align
        return {'size': total_size, 'alignment': max_align}

    def _calc_union_size(self, fields: List) -> int:
        """联合体大小计算"""
        max_size = 0
        # for field in fields:
        #     type_info = self.type_manager.get_type_size_info(field['type'])
        #     size = type_info.get('size', 0) if type_info else 0
        #     max_size = max(max_size, size)
        return 1

    def _calc_union_alignment(self, fields: List) -> int:
        """联合体对齐计算"""
        max_align = 1
        # for field in fields:
        #     type_info = self.type_manager.get_type_size_info(field['type'])
        #     align = type_info.get('alignment', 1) if type_info else 1
        #     max_align = max(max_align, align)
        return max_align
    def _print_type_info(self, type_name: str, type_info: Dict[str, Any], indent: int = 0):
        """打印类型信息
        
        Args:
            type_name: 类型名称
            type_info: 类型信息字典
            indent: 缩进级别
        """
        prefix = "  " * indent
        kind = type_info.get('kind', 'unknown')
        
        self.logger.info(f"\n{prefix}=== Type: {type_name} ({kind}) ===")
        
        # 打印基本信息
        if 'size' in type_info:
            self.logger.info(f"{prefix}Size: {type_info['size']} bytes")
        if 'alignment' in type_info:
            self.logger.info(f"{prefix}Alignment: {type_info['alignment']} bytes")
        
        # 打印类型特定信息
        if kind == 'struct' or kind == 'union':
            self.logger.info(f"{prefix}Fields:")
            for field in type_info.get('fields', []):
                field_type = field.get('type', 'unknown')
                field_name = field.get('name', 'unnamed')
                field_offset = field.get('offset', 0)
                self.logger.info(f"{prefix}  - {field_name}: {field_type} (offset: {field_offset})")
                
                # 打印嵌套字段
                if isinstance(field_type, dict):
                    self._print_type_info(field_name, field_type, indent + 2)
                
        elif kind == 'enum':
            self.logger.info(f"{prefix}Values:")
            for name, value in type_info.get('values', {}).items():
                self.logger.info(f"{prefix}  - {name} = {value}")
                
        elif kind == 'typedef':
            base_type = type_info.get('base_type', 'unknown')
            self.logger.info(f"{prefix}Base type: {base_type}")
            
            # 如果基类型是复杂类型，递归打印
            if isinstance(base_type, dict):
                self._print_type_info(f"{type_name}_base", base_type, indent + 1)
        
        # 打印属性和元数据
        if 'attributes' in type_info:
            self.logger.info(f"{prefix}Attributes: {type_info['attributes']}")
        if 'location' in type_info:
            loc = type_info['location']
            self.logger.info(f"{prefix}Defined at: {loc.get('file', 'unknown')}:{loc.get('line', '?')}")
        if 'comment' in type_info:
            self.logger.info(f"{prefix}Comment: {type_info['comment']}")

    def _add_type_with_logging(self, type_name: str, type_info: Dict[str, Any]):
        """添加类型并打印详细信息"""
        # 添加类型
        self.type_manager.register_type(type_name, type_info)
        
        # 打印类型信息
        self._print_type_info(type_name, type_info) 
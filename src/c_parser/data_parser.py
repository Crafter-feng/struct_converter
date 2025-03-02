from typing import Dict, Any, Optional, List, Tuple, Union
from pathlib import Path
from utils.logger import logger 
from .core.tree_sitter_utils import TreeSitterUtils
from .core.expression_parser import ExpressionParser
from .core.data_manager import DataManager
from .type_parser import CTypeParser
from .core.type_manager import TypeManager




class CDataParser:
    """C数据解析器"""
    
    def __init__(self, type_manager: TypeManager = None):
        logger.info("=== Initializing CDataParser ===")
        self.type_manager = type_manager or TypeManager()
        self.tree_sitter = TreeSitterUtils.get_instance()
        self.data_manager = DataManager()
        self.type_parser = CTypeParser()
        
        # 输出类型统计信息
        type_info = self.data_manager.get_type_info()
        logger.info("\nLoaded type definitions:")
        logger.info(f"- Typedefs:   {len(type_info['current']['typedef_types'])} items")
        logger.info(f"- Structs:    {len(type_info['current']['struct_info'])} items")
        logger.info(f"- Unions:     {len(type_info['current']['union_info'])} items")
        logger.info(f"- Enums:      {len(type_info['current']['enum_types'])} items")
        logger.info("=== Initialization Complete ===\n")
        
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """解析C头文件"""
        logger.info(f"\n=== Parsing File: {file_path} ===")
        
        # 解析文件
        logger.info("Step 1: Parsing source file...")
        ast = self.tree_sitter.parse_source(file_path)
        
        # 处理AST
        logger.info("\nStep 2: Processing AST...")
        self._process_ast(ast)
        
        # 获取结果
        logger.info("\nStep 3: Collecting results...")
        result = self.data_manager.get_all_data()
        
        # 输出统计信息
        logger.info("\nParsing results:")
        logger.info(f"- Structs:    {len(result['structs'])} items")
        logger.info(f"- Unions:     {len(result['unions'])} items")
        logger.info(f"- Enums:      {len(result['enums'])} items")
        logger.info(f"- Typedefs:   {len(result['typedefs'])} items")
        logger.info(f"- Variables:  {len(result['variables']['variables'])} items")
        logger.info(f"- Arrays:     {len(result['variables']['array_vars'])} items")
        logger.info(f"- Pointers:   {len(result['variables']['pointer_vars'])} items")
        logger.info(f"- Structs:    {len(result['variables']['struct_vars'])} items")
        
        logger.info("=== Parsing Complete ===\n")
        return result
        
    def parse_global_variables(self, source_code: str) -> Dict[str, Any]:
        """解析全局变量定义"""
        logger.info("\n=== Parsing Global Variables ===")
        
        # 解析代码
        logger.info("Step 1: Parsing source code...")
        ast = self.tree_sitter.parse_source(source_code)
        
        # 解析类型定义
        logger.info("\nStep 2: Parsing type definitions...")
        self._parse_current_file_types(ast)
        
        # 处理AST
        logger.info("\nStep 3: Processing AST...")
        self._process_ast(ast)
        
        # 获取结果
        logger.info("\nStep 4: Collecting results...")
        result = {
            'types': self.data_manager.get_type_info(),
            'variables': self.data_manager.get_variables()
        }
        
        # 输出统计信息
        logger.info("\nParsing results:")
        logger.info(f"- Basic variables:    {len(result['variables']['variables'])} items")
        logger.info(f"- Struct variables:   {len(result['variables']['struct_vars'])} items")
        logger.info(f"- Pointer variables:  {len(result['variables']['pointer_vars'])} items")
        logger.info(f"- Array variables:    {len(result['variables']['array_vars'])} items")
        
        logger.info("=== Parsing Complete ===\n")
        return result
        
    def _process_ast(self, ast: Dict[str, Any]) -> None:
        """处理AST"""
        try:
            # 处理类型定义
            for name, typedef in ast.get('typedefs', {}).items():
                type_info = self._process_type_definition(typedef)
                self.data_manager.add_typedef(name, type_info)
                
            # 处理结构体
            for name, struct in ast.get('structs', {}).items():
                struct_info = self._process_struct(struct)
                self.data_manager.add_struct(name, struct_info)
                
            # 处理联合体
            for name, union in ast.get('unions', {}).items():
                union_info = self._process_union(union)
                self.data_manager.add_union(name, union_info)
                
            # 处理枚举
            for name, enum in ast.get('enums', {}).items():
                enum_info = self._process_enum(enum)
                self.data_manager.add_enum(name, enum_info)
                
            # 处理宏定义
            for name, value in ast.get('defines', {}).items():
                self.data_manager.add_define(name, value)
                
            # 处理包含文件
            for include in ast.get('includes', []):
                self.data_manager.add_include(include)
                
            # 处理变量声明
            self._collect_variable_definitions(ast)
            
        except Exception as e:
            logger.error(f"Failed to process AST: {e}")
            raise
            
    def _process_struct(self, struct: Dict[str, Any]) -> Dict[str, Any]:
        """处理结构体信息"""
        logger.debug(f"\nProcessing struct: {struct.get('name')}")
        try:
            fields = []
            current_offset = 0
            max_alignment = 1
            
            # 处理结构体属性
            attributes = self._process_attributes(struct.get('attributes', {}))
            logger.debug(f"Struct attributes: {attributes}")
            
            for field in struct['fields']:
                logger.debug(f"\nProcessing field: {field.get('name')}")
                field_type = self.data_manager.type_manager.parse_type(field['type'])
                alignment = self.data_manager.type_manager.get_alignment(field_type)
                max_alignment = max(max_alignment, alignment)
                
                # 计算字段偏移
                if not attributes.get('packed'):
                    padding = (alignment - (current_offset % alignment)) % alignment
                    current_offset += padding
                    logger.debug(f"Field alignment: {alignment}, padding: {padding}")
                
                field_info = {
                    'name': field['name'],
                    'type': field_type,
                    'offset': current_offset,
                    'size': self.data_manager.type_manager.get_type_size(field_type),
                    'alignment': alignment,
                    'bit_offset': field.get('bit_offset'),
                    'bit_width': field.get('bit_width'),
                    'comments': self._process_comments(field)
                }
                logger.debug(f"Field info: {field_info}")
                
                # 处理嵌套结构体
                if field.get('nested_struct'):
                    nested_struct = self._process_struct(field['nested_struct'])
                    field_info['nested_struct'] = nested_struct
                    # 更新字段类型和大小
                    field_info['type'] = nested_struct['name']
                    field_info['size'] = nested_struct['size']
                    field_info['alignment'] = nested_struct['alignment']
                
                fields.append(field_info)
                
                # 更新偏移
                if field.get('bit_width') is not None:
                    bits = current_offset * 8 + field['bit_width']
                    current_offset = (bits + 7) // 8
                else:
                    current_offset += field_info['size']
            
            # 计算结构体总大小，考虑尾部填充
            if not attributes.get('packed'):
                padding = (max_alignment - (current_offset % max_alignment)) % max_alignment
                current_offset += padding
            
            logger.debug(f"\nStruct processing complete: {struct.get('name')}")
            logger.debug(f"Total size: {current_offset}, alignment: {max_alignment}")
            return {
                'name': struct['name'],
                'fields': fields,
                'size': current_offset,
                'alignment': max_alignment if not attributes.get('packed') else 1,
                'attributes': attributes,
                'is_union': False,
                'comments': self._process_comments(struct)
            }
            
        except Exception as e:
            logger.error(f"Failed to process struct {struct.get('name')}: {e}")
            logger.error(f"Struct data: {struct}")
            raise
            
    def _process_union(self, union: Dict[str, Any]) -> Dict[str, Any]:
        """处理联合体信息"""
        try:
            fields = []
            max_size = 0
            max_alignment = 1
            
            for field in union['fields']:
                field_type = self.data_manager.type_manager.parse_type(field['type'])
                field_size = self.data_manager.type_manager.get_type_size(field_type)
                field_alignment = self.data_manager.type_manager.get_alignment(field_type)
                
                field_info = {
                    'name': field['name'],
                    'type': field_type,
                    'offset': 0,  # 联合体所有字段偏移都是0
                    'size': field_size,
                    'alignment': field_alignment,
                    'bit_offset': field.get('bit_offset'),
                    'bit_width': field.get('bit_width'),
                    'comments': self._process_comments(field)
                }
                fields.append(field_info)
                
                max_size = max(max_size, field_size)
                max_alignment = max(max_alignment, field_alignment)
                
            return {
                'name': union['name'],
                'fields': fields,
                'size': max_size,
                'alignment': max_alignment,
                'is_union': True,
                'comments': self._process_comments(union)
            }
            
        except Exception as e:
            logger.error(f"Failed to process union: {e}")
            raise
            
    def _process_enum(self, enum: Dict[str, Any]) -> Dict[str, Any]:
        """处理枚举信息"""
        try:
            values = {}
            current_value = 0
            
            for enumerator in enum['values']:
                name = enumerator['name']
                if 'value' in enumerator:
                    value_expr = enumerator['value']
                    current_value = self._evaluate_constant_expression(value_expr)
                values[name] = current_value
                current_value += 1
                
            return {
                'name': enum['name'],
                'values': values,
                'size': 4,  # 枚举类型通常是int
                'alignment': 4,
                'comments': self._process_comments(enum)
            }
            
        except Exception as e:
            logger.error(f"Failed to process enum: {e}")
            raise
            
    def _process_type_definition(self, typedef: Dict[str, Any]) -> Dict[str, Any]:
        """处理类型定义"""
        try:
            base_type = typedef['type']
            type_info = self.data_manager.type_manager.parse_type(base_type)
            
            result = {
                'name': typedef['name'],
                'base_type': type_info,
                'is_pointer': typedef.get('is_pointer', False),
                'pointer_level': typedef.get('pointer_level', 0),
                'array_size': typedef.get('array_size'),
                'size': self.data_manager.type_manager.get_type_size(type_info),
                'alignment': self.data_manager.type_manager.get_alignment(type_info),
                'comments': self._process_comments(typedef)
            }
            
            if typedef.get('is_function_pointer'):
                result.update({
                    'is_function_pointer': True,
                    'return_type': typedef.get('return_type'),
                    'parameters': typedef.get('parameters', [])
                })
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to process typedef: {e}")
            raise
            
    def _process_declaration(self, decl: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理变量声明"""
        try:
            # 首先检查是否是全局变量或extern声明
            if not self._is_global_declaration(decl) or self._is_extern_declaration(decl):
                logger.debug("Skipping non-global or extern declaration")
                return None
            
            # 提取类型信息
            type_info = self._extract_type_info(decl)
            type_name = type_info['type']
            original_type = type_info['original_type']
            
            var_info = {
                'name': decl.get('name'),
                'type': type_name,
                'original_type': original_type,
                'is_pointer': decl.get('is_pointer', False),
                'pointer_level': decl.get('pointer_level', 0),
                'array_size': None,
                'bit_field': decl.get('bit_field'),
                'comments': self._process_comments(decl),
                'value': None
            }
            
            # 如果是指针，更新类型名和原始类型
            if var_info['is_pointer']:
                var_info['type'] = f"{type_name}{'*' * var_info['pointer_level']}"
                var_info['original_type'] = f"{original_type}{'*' * var_info['pointer_level']}"
            
            # 处理数组大小
            if 'array_size' in decl:
                if isinstance(decl['array_size'], list):
                    # 多维数组
                    sizes = []
                    for size_expr in decl['array_size']:
                        size = self._solve_array_size(size_expr)
                        sizes.append(size if size is not None else 'dynamic')
                    var_info['array_size'] = sizes
                    
                    # 处理动态数组大小
                    if 'dynamic' in sizes and 'initializer' in decl:
                        var_info['array_size'] = self._solve_dynamic_array_size(
                            decl['initializer'],
                            sizes
                        )
                else:
                    # 一维数组
                    size = self._solve_array_size(decl['array_size'])
                    var_info['array_size'] = size if size is not None else 'dynamic'
                    
                    # 处理动态数组大小
                    if var_info['array_size'] == 'dynamic' and 'initializer' in decl:
                        var_info['array_size'] = self._solve_dynamic_array_size(
                            decl['initializer'],
                            [var_info['array_size']]
                        )[0]
            
            # 处理初始化器
            if 'initializer' in decl:
                var_info['value'] = self._evaluate_constant_expression(decl['initializer'])
                
                # 处理动态数组大小
                if var_info.get('array_size') == 'dynamic' and var_info['value']:
                    if isinstance(var_info['value'], (list, str)):
                        var_info['array_size'] = len(var_info['value'])
            
            return var_info
            
        except Exception as e:
            logger.error(f"Failed to process declaration: {e}")
            return None
            
    def _evaluate_constant_expression(self, expr: Any) -> Any:
        """计算常量表达式"""
        try:
            logger.debug(f"Evaluating expression: {expr}")
            value, _ = ExpressionParser.parse(
                expr,
                self.data_manager.type_manager.get_enum_values(),
                self.data_manager.type_manager.get_macro_definition()
            )
            logger.debug(f"Evaluated value: {value}")
            return value
        except Exception as e:
            logger.error(f"Failed to evaluate expression: {expr}")
            logger.error(f"Error details: {str(e)}")
            logger.error(f"Available enums: {self.data_manager.type_manager.get_enum_info()}")
            logger.error(f"Available macros: {self.data_manager.type_manager.get_macro_definition()}")
            return None
            
    def _process_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """处理类型属性"""
        result = {}
        try:
            for attr_name, attr_value in attributes.items():
                if attr_name == 'packed':
                    result['packed'] = True
                elif attr_name == 'aligned':
                    result['aligned'] = int(attr_value)
                elif attr_name == 'deprecated':
                    result['deprecated'] = True
            return result
        except Exception as e:
            logger.error(f"Failed to process attributes: {e}")
            return {}
            
    def _process_comments(self, node: Dict[str, Any]) -> List[str]:
        """处理注释信息"""
        comments = []
        try:
            for comment in node.get('comments', []):
                text = comment['text'].strip()
                if text.startswith('//'):
                    comments.append(text[2:].strip())
                elif text.startswith('/**') and text.endswith('*/'):
                    # 处理文档注释
                    doc_lines = []
                    for line in text[3:-2].split('\n'):
                        line = line.strip().lstrip('*').strip()
                        if line:
                            doc_lines.append(line)
                    if doc_lines:
                        comments.extend(doc_lines)
                elif text.startswith('/*') and text.endswith('*/'):
                    comments.append(text[2:-2].strip())
            return comments
        except Exception as e:
            logger.error(f"Failed to process comments: {e}")
            return []
            
    def _is_global_declaration(self, decl: Dict[str, Any]) -> bool:
        """检查是否是全局变量声明"""
        storage = decl.get('storage_class')
        if storage in ['auto', 'register', 'extern']:
            return False
        if decl.get('is_local'):
            return False
        return True 
            
    def _solve_array_size(self, size_expr: Any) -> Optional[int]:
        """解析数组大小表达式
        
        Args:
            size_expr: 数组大小表达式
            
        Returns:
            数组大小，如果无法解析则返回None
        """
        try:
            if isinstance(size_expr, dict):
                if size_expr.get('type') == 'sizeof_expression':
                    # 处理sizeof表达式
                    target_type = size_expr.get('target_type')
                    if target_type:
                        return self.data_manager.type_manager.get_type_size(target_type)
                        
            # 使用ExpressionParser处理其他表达式
            value, _ = ExpressionParser.parse(
                size_expr,
                self.data_manager.type_manager.get_enum_values(),
                self.data_manager.type_manager.get_macro_definition()
            )
            return value
            
        except Exception as e:
            logger.error(f"Failed to solve array size: {e}")
            return None 
            
    def _process_bit_field(self, field: Dict[str, Any], current_offset: int) -> Tuple[int, Dict[str, Any]]:
        """处理位域字段
        
        Args:
            field: 字段信息
            current_offset: 当前偏移量
            
        Returns:
            Tuple[int, Dict[str, Any]]: (新偏移量, 处理后的字段信息)
        """
        try:
            field_type = self.data_manager.type_manager.parse_type(field['type'])
            base_size = self.data_manager.type_manager.get_type_size(field_type)
            bit_width = field['bit_width']
            
            # 计算位偏移
            bit_offset = (current_offset * 8) % (base_size * 8)
            
            # 检查是否需要新的存储单元
            if bit_offset + bit_width > base_size * 8:
                current_offset = ((current_offset * 8 + (base_size * 8 - 1)) // (base_size * 8)) * base_size
                bit_offset = 0
                
            field_info = {
                'name': field['name'],
                'type': field_type,
                'offset': current_offset,
                'size': base_size,
                'bit_offset': bit_offset,
                'bit_width': bit_width,
                'comments': self._process_comments(field)
            }
            
            # 更新偏移
            if bit_offset + bit_width >= base_size * 8:
                current_offset += base_size
                
            return current_offset, field_info
            
        except Exception as e:
            logger.error(f"Failed to process bit field: {e}")
            raise 
            
    def _print_type_definitions(self) -> None:
        """打印所有可用的类型定义"""
        logger.info("\n=== Available Type Definitions ===")
        
        # 获取类型信息
        type_info = self.data_manager.get_type_info()
        
        # 打印结构体定义
        if self.data_manager.structs:
            logger.info("\nStruct Definitions:")
            for struct_name, info in self.data_manager.structs.items():
                logger.info(f"struct {struct_name} {{")
                for field in info.get('fields', []):
                    type_str = field.get('type', 'unknown')
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
        if self.data_manager.unions:
            logger.info("\nUnion Definitions:")
            for union_name, info in self.data_manager.unions.items():
                logger.info(f"union {union_name} {{")
                for field in info.get('fields', []):
                    type_str = field.get('type', 'unknown')
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
        if self.data_manager.typedefs:
            logger.info("\nTypedef Definitions:")
            for typedef_name, typedef_info in self.data_manager.typedefs.items():
                base_type = typedef_info.get('base_type', 'unknown')
                logger.info(f"typedef {base_type} {typedef_name};")
        
        # 打印枚举定义
        if self.data_manager.enums:
            logger.info("\nEnum Definitions:")
            for enum_name, enum_info in self.data_manager.enums.items():
                logger.info(f"enum {enum_name} {{")
                for name, value in enum_info.get('values', {}).items():
                    logger.info(f"    {name} = {value},")
                logger.info("};")
        
        logger.info("\n=== End of Type Definitions ===\n") 
            
    def _is_extern_declaration(self, decl: Dict[str, Any]) -> bool:
        """检查是否是extern声明
        
        Args:
            decl: 声明节点
            
        Returns:
            bool: 是否是extern声明
        """
        storage = decl.get('storage_class')
        return storage == 'extern' 
            
    def _solve_dynamic_array_size(self, initializer: Dict[str, Any], array_sizes: List[Any]) -> List[Any]:
        """解析动态数组的实际大小"""
        solved_sizes = array_sizes.copy()
        
        if 'dynamic' not in solved_sizes:
            return solved_sizes
        
        try:
            # 处理字符串字面量
            if initializer.get('type') == 'string_literal':
                text = initializer.get('value', '')
                # 处理转义字符
                text = bytes(text, "utf-8").decode("unicode_escape")
                # 字符串长度加1（为了包含null终止符）
                size = len(text) + 1
                dynamic_index = solved_sizes.index('dynamic')
                solved_sizes[dynamic_index] = size
                return solved_sizes
                
            # 处理初始化列表
            if initializer.get('type') == 'initializer_list':
                elements = initializer.get('elements', [])
                if elements:
                    dynamic_index = solved_sizes.index('dynamic')
                    solved_sizes[dynamic_index] = len(elements)
                return solved_sizes
                
            return solved_sizes
            
        except Exception as e:
            logger.error(f"Failed to solve dynamic array size: {e}")
            return solved_sizes 
            
    def _extract_type_info(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """提取类型信息
        
        Args:
            node: 类型节点
            
        Returns:
            类型信息字典
        """
        logger.debug(f"Extracting type info from: {node}")
        
        type_parts = []
        original_type = None
        
        # 处理基本类型
        if node.get('type') in ['primitive_type', 'sized_type_specifier', 'type_identifier']:
            type_text = node.get('text', '')
            type_parts.append(type_text)
            
            # 记录原始类型
            if not original_type:
                if self.data_manager.type_manager.is_basic_type(type_text):
                    original_type = type_text
                else:
                    original_type = self.data_manager.type_manager.get_real_type(type_text)
                if not original_type:
                    logger.error(f"Unknown type: {type_text}")
                    original_type = type_text
                    
        # 处理结构体
        elif node.get('type') == 'struct_specifier':
            type_parts.append('struct')
            struct_name = node.get('name')
            if struct_name:
                type_parts.append(struct_name)
                if not original_type:
                    original_type = f"struct {struct_name}"
                    
        # 处理联合体
        elif node.get('type') == 'union_specifier':
            type_parts.append('union')
            union_name = node.get('name')
            if union_name:
                type_parts.append(union_name)
                if not original_type:
                    original_type = f"union {union_name}"
        
        type_str = ' '.join(type_parts)
        logger.debug(f"Extracted type: {type_str}")
        logger.debug(f"Original type: {original_type}")
        
        return {
            "type": type_str,
            "original_type": original_type
        } 
            
    def _parse_array_dimensions(self, declarator: Dict[str, Any]) -> Tuple[List[Any], str]:
        """解析数组维度
        
        Args:
            declarator: 数组声明器节点
            
        Returns:
            Tuple[List[Any], str]: (数组维度列表, 数组名称)
        """
        array_sizes = []
        name = None
        
        # 获取变量名
        name = declarator.get('name')
        if not name:
            logger.error("Array declarator missing name")
            return [], None
        
        # 获取数组维度
        dimensions = declarator.get('dimensions', [])
        for dim in dimensions:
            if dim.get('type') == 'number_literal':
                # 固定大小
                size = int(dim.get('value', 0))
                array_sizes.append(size)
            elif dim.get('type') == 'identifier':
                # 变量大小
                size_var = dim.get('name')
                if size_var != name:  # 避免使用数组名本身
                    array_sizes.append(f"var({size_var})")
                else:
                    array_sizes.append("dynamic")
            else:
                # 动态大小
                array_sizes.append("dynamic")
        
        logger.debug(f"Array declaration analysis: sizes: {array_sizes}, name: {name}")
        return array_sizes, name 
            
    def _parse_current_file_types(self, ast: Dict[str, Any]) -> None:
        """解析当前文件中的类型定义"""
        logger.info("解析当前文件的类型定义")
        
        # 使用CTypeParser解析当前文件的类型定义
        current_types = self.type_parser.parse_declarations(ast)
        
        # 更新类型管理器
        self.data_manager.type_manager.update_type_info(current_types)
        
        logger.debug("当前文件类型解析完成:")
        debug_info = self.data_manager.get_type_info()
        logger.debug(f"- 类型定义(typedef): {len(debug_info['current']['typedef_types'])} 个")
        logger.debug(f"- 结构体(struct): {len(debug_info['current']['struct_info'])} 个")
        logger.debug(f"- 联合体(union): {len(debug_info['current']['union_info'])} 个")
        logger.debug(f"- 枚举(enum): {len(debug_info['current']['enum_types'])} 个") 
            
    def _collect_variable_definitions(self, ast: Dict[str, Any]) -> None:
        """收集所有变量定义"""
        for decl in ast.get('declarations', []):
            if decl.get('type') == 'declaration':
                var_info = self._process_declaration(decl)
                if var_info and var_info.get('name'):
                    self.data_manager.add_variable(var_info)
                    logger.debug(f"Collected variable definition: {var_info['name']}") 
            
    def _categorize_variable(self, var_info: Dict[str, Any]) -> None:
        """将变量分类到相应的类别
        
        Args:
            var_info: 变量信息
        """
        logger.debug(f"\nCategorizing variable: {var_info.get('name')}")
        logger.debug(f"Variable data: {var_info}")
        
        # 首先检查是否是指针
        if var_info.get('is_pointer') or self.data_manager.type_manager.is_pointer_type(var_info['type']):
            logger.debug(f"Categorized as pointer variable: {var_info.get('name')}")
            self.data_manager.add_variable(var_info, 'pointer_vars')
            return
        
        # 然后检查是否是数组
        if var_info.get('array_size'):
            logger.debug(f"Categorized as array variable: {var_info.get('name')}")
            self.data_manager.add_variable(var_info, 'array_vars')
            return
        
        # 检查是否是结构体类型
        if self.data_manager.type_manager.is_struct_type(var_info['type']):
            logger.debug(f"Categorized as struct variable: {var_info.get('name')}")
            self.data_manager.add_variable(var_info, 'struct_vars')
        else:
            logger.debug(f"Categorized as basic variable: {var_info.get('name')}")
            self.data_manager.add_variable(var_info, 'variables') 
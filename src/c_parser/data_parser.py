from typing import Dict, Any, Optional, List, Tuple, Union
from utils.logger import logger 
from pathlib import Path
from .core.tree_sitter_utils import TreeSitterUtils
from .core.data_manager import DataManager
from .core.expression_parser import ExpressionParser
from .type_parser import CTypeParser
from .core.type_manager import TypeManager
from tree_sitter import Node
import json
import copy


class CDataParser:
    """C数据解析器 - 重构版本
    
    主要功能：
    1. 解析C文件中的类型定义（结构体、联合体、枚举等）
    2. 解析全局变量定义
    3. 基于AST节点的统一解析流程
    4. 支持嵌套结构体和结构体数组
    5. 集成了原ValueParser的功能
    """
    
    def __init__(self, type_manager: TypeManager = None):
        logger.info("=== Initializing CDataParser (Refactored) ===")
        self.type_manager = type_manager or TypeManager()
        self.tree_sitter = TreeSitterUtils.get_instance()
        self.data_manager = DataManager(self.type_manager)
        self.type_parser = CTypeParser(self.type_manager)
        self.current_file = None
        
        # 输出类型统计信息
        self._log_initialization_stats()
        logger.info("=== Initialization Complete ===\n")
        
    def _log_initialization_stats(self) -> None:
        """记录初始化统计信息"""
        type_info = self.data_manager.get_type_info()
        logger.info("\nLoaded type definitions:")
        logger.info(f"- types:   {len(type_info['global']['types'])} items")
        logger.info(f"- pointer_types:    {len(type_info['global']['pointer_types'])} items")
        logger.info(f"- macro_definitions:     {len(type_info['global']['macro_definitions'])} items")
        
    def parse_file(self, source: Union[str, Path]) -> Dict[str, Any]:
        """解析C文件
        
        解析步骤：
        1. 读取文件内容
        2. 解析类型定义（必须先于变量解析）
        3. 解析全局变量
        4. 收集和返回结果
        
        Args:
            source: C文件路径或者文件内容
            
        Returns:
            Dict[str, Any]: 解析结果，包含类型定义和变量信息
        """
        logger.info(f"\n=== Parsing File: {source} ===")
        
        try:
            # Step 1: 读取文件
            if isinstance(source, str):
                # 如果source是字符串，检查是否为文件路径
                if Path(source).exists():
                    text = self._read_file(source)
                else:
                    text = source  # 作为源代码字符串处理
            else:
                text = self._read_file(source)
            
            # Step 2: 解析类型定义（必须先于变量解析）
            logger.info("Step 1: Parsing type definitions...")
            self.type_parser.parse_declarations(text)
            
            # Step 3: 解析全局变量
            logger.info("\nStep 2: Parsing global variables...")
            ast = self.tree_sitter.parse(text)
            # 如果ast是Tree对象，获取其root_node
            if hasattr(ast, 'root_node'):
                ast = ast.root_node
            self._parse_global_variables(ast)
            
            # Step 4: 收集结果
            logger.info("\nStep 3: Collecting results...")
            result = self.data_manager.get_all_data()
            
            # 输出统计信息
            self._log_parsing_results(result)
            
            logger.info("=== Parsing Complete ===\n")
            return result
            
        except Exception as e:
            logger.exception(f"Failed to parse file {source}: {e}")
            raise
    
    def _read_file(self, file_path: str) -> str:
        """读取文件内容"""
        file_path_obj = Path(file_path)
        self.current_file = str(file_path_obj)
        
        try:
            text = file_path_obj.read_text(encoding='utf-8')
            logger.debug(f"成功读取文件: {file_path_obj}")
            logger.debug(f"文件内容长度: {len(text)}")
            logger.debug(f"文件内容预览: {text[:200]}...")
            return text
        except Exception as e:
            logger.error(f"读取文件失败: {file_path_obj}, 错误: {e}")
            raise
    
    def _log_parsing_results(self, result: Dict[str, Any]) -> None:
        """记录解析结果统计信息"""
        logger.info("\nParsing results:")
        logger.info(f"- Structs:    {len(result['structs'])} items")
        logger.info(f"- Unions:     {len(result['unions'])} items")
        logger.info(f"- Enums:      {len(result['enums'])} items")
        logger.info(f"- Typedefs:   {len(result['typedefs'])} items")
        logger.info(f"- Variables:  {len(result['variables']['variables'])} items")
        logger.info(f"- Arrays:     {len(result['variables']['array_vars'])} items")
        logger.info(f"- Pointers:   {len(result['variables']['pointer_vars'])} items")
        logger.info(f"- Struct vars: {len(result['variables']['struct_vars'])} items")
        
    def _parse_global_variables(self, ast_node: Node) -> None:
        """解析全局变量定义
        
        Args:
            ast_node: AST根节点
        """
        logger.info("\n=== Parsing Global Variables ===")
        
        try:
            self._process_ast_node(ast_node)
            logger.info("=== Global Variables Parsing Complete ===\n")
        except Exception as e:
            logger.exception(f"Failed to parse global variables: {e}")
            raise
        
    def _process_ast_node(self, node: Node) -> None:
        """处理AST节点，递归查找变量声明
        
        Args:
            node: 要处理的AST节点
        """
        try:
            for child in node.children:
                if child.type == 'declaration':
                    if self._is_variable_declaration(child):
                        self._parse_variable_declaration(child)
                elif child.type == 'translation_unit':
                    self._process_ast_node(child)  # 递归处理
            
        except Exception as e:
            logger.exception(f"Failed to process AST node: {e}")
            raise
    
    def _is_variable_declaration(self, node: Node) -> bool:
        """判断是否为变量声明（而不是函数声明）"""
        try:    
            # 检查是否包含变量声明的关键节点
            for child in node.children:
                if child.type in ['init_declarator', 'identifier', 'array_declarator', 'pointer_declarator']:
                    return True
                elif child.type == 'function_declarator':
                    return False
            
            return True
            
        except Exception as e:
            logger.exception(f"Error checking if variable declaration: {e}")
            return False
            
    def _parse_variable_declaration(self, node: Node) -> None:
        """解析变量声明节点 - 基于AST节点的新流程
        
        Args:
            node: 变量声明的AST节点
        """
        try:
            node_text = self.tree_sitter.get_node_text(node)
            display_text = node_text[:100] + '...' if len(node_text) > 100 else node_text
            logger.info(f"\n=== Parsing Variable Declaration (AST-based): {display_text} ===")
            
            # 初始化变量信息
            variable_info = self._init_variable_info(node)
            
            # 基于AST节点解析完整的变量信息
            self._parse_variable_from_ast(node, variable_info)
            
            # 记录和存储结果
            self._log_and_store_variable(variable_info)
            
        except Exception as e:
            logger.exception(f"Failed to parse variable declaration: {e}")
            raise
    
    def _init_variable_info(self, node: Node) -> Dict[str, Any]:
        """初始化变量信息结构"""
        return {
            'name': None,
            'type': None,
            'is_const': False,
            'is_volatile': False,
            'is_restrict': False,
            'storage_class': None,
            'is_pointer': False,
            'pointer_level': 0,
            'array_size': [],
            'initial_value': None,
            'parsed_value': None,
            'initializer_node': None,
            'location': self._get_node_location(node),
            'typeinfo': None
        }
    
    def _parse_variable_from_ast(self, node: Node, variable_info: Dict[str, Any]) -> None:
        """基于AST节点解析变量的完整信息
        
        Args:
            node: 变量声明的AST节点
            variable_info: 变量信息字典
        """
        logger.debug(f"Parsing variable from AST node: {node.type}")
        
        # 第一步：解析类型限定符和存储类
        self._extract_qualifiers_and_storage(node, variable_info)
        
        # 第二步：解析基础类型
        self._extract_base_type(node, variable_info)
        
        # 第三步：解析声明符（变量名、指针、数组）
        self._extract_declarator_info(node, variable_info)
        
        # 第四步：解析初始化器
        self._extract_initializer(node, variable_info)
        
        # 第五步：构建完整类型信息
        self._build_complete_type_info(variable_info)
        
        # 第六步：解析初始化值
        self._parse_initialization_value(variable_info)
    
    def _extract_qualifiers_and_storage(self, node: Node, variable_info: Dict[str, Any]) -> None:
        """提取类型限定符和存储类信息"""
        for child in node.children:
            if child.type == 'type_qualifier':
                qualifier = self.tree_sitter.get_node_text(child)
                if qualifier == 'const':
                    variable_info['is_const'] = True
                elif qualifier == 'volatile':
                    variable_info['is_volatile'] = True
                elif qualifier == 'restrict':
                    variable_info['is_restrict'] = True
            elif child.type == 'storage_class_specifier':
                variable_info['storage_class'] = self.tree_sitter.get_node_text(child)
    
    def _extract_base_type(self, node: Node, variable_info: Dict[str, Any]) -> None:
        """提取基础类型信息"""
        type_parts = []
        
        for child in node.children:
            if child.type in ['primitive_type', 'sized_type_specifier', 'type_identifier']:
                type_parts.append(self.tree_sitter.get_node_text(child))
            elif child.type in ['struct_specifier', 'union_specifier', 'enum_specifier']:
                # 处理复合类型
                type_name = self._extract_composite_type_name(child)
                if type_name:
                    type_parts.append(type_name)
        
        if type_parts:
            base_type = ' '.join(type_parts)
            variable_info['type'] = base_type
  
            logger.debug(f"Extracted base type: {base_type}")
   
    def _extract_composite_type_name(self, node: Node) -> Optional[str]:
        """提取复合类型名称（struct/union/enum）"""
        prefix = node.type.replace('_specifier', '')
        
        # 查找类型标识符
        for child in node.children:
            if child.type == 'type_identifier':
                name = self.tree_sitter.get_node_text(child)
                return f"{prefix} {name}"
        
        # 如果没有名称，可能是匿名类型
        return None
    
    def _extract_declarator_info(self, node: Node, variable_info: Dict[str, Any]) -> None:
        """提取声明符信息（变量名、指针、数组）"""
        # 查找主要的声明符节点
        declarator_node = self._find_main_declarator(node)
        
        if declarator_node:
            self._parse_declarator_node(declarator_node, variable_info)
        else:
            raise ValueError(f"No declarator node found for variable: {variable_info['name']}")
    
    def _find_main_declarator(self, node: Node) -> Optional[Node]:
        """查找主要的声明符节点"""
        for child in node.children:
            if child.type == 'init_declarator':
                # 从init_declarator中查找声明符
                for init_child in child.children:
                    if init_child.type in ['identifier', 'pointer_declarator', 'array_declarator']:
                        return init_child
            elif child.type in ['identifier', 'pointer_declarator', 'array_declarator']:
                return child
        return None
    
    def _parse_declarator_node(self, declarator_node: Node, variable_info: Dict[str, Any]) -> None:
        """解析声明符节点"""
        if declarator_node.type == 'identifier':
            variable_info['name'] = self.tree_sitter.get_node_text(declarator_node)
            
        elif declarator_node.type == 'pointer_declarator':
            self._parse_pointer_declarator(declarator_node, variable_info)
            
        elif declarator_node.type == 'array_declarator':
            self._parse_array_declarator(declarator_node, variable_info)
    
    def _parse_pointer_declarator(self, node: Node, variable_info: Dict[str, Any]) -> None:
        """解析指针声明符"""
        pointer_level = 0
        current_node = node
        
        # 计算指针级别并找到最终的标识符
        while current_node and current_node.type == 'pointer_declarator':
            pointer_level += 1
            next_node = None
            
            for child in current_node.children:
                if child.type == 'identifier':
                    variable_info['name'] = self.tree_sitter.get_node_text(child)
                    break
                elif child.type in ['pointer_declarator', 'array_declarator']:
                    next_node = child
                    break
            
            current_node = next_node
        
        # 处理最后的数组声明符
        if current_node and current_node.type == 'array_declarator':
            self._parse_array_declarator(current_node, variable_info)
        
        variable_info['is_pointer'] = pointer_level > 0
        variable_info['pointer_level'] = pointer_level
        
        logger.debug(f"Parsed pointer: level={pointer_level}, name={variable_info['name']}")
    
    def _parse_array_declarator(self, node: Node, variable_info: Dict[str, Any]) -> None:
        """解析数组声明符"""
        array_sizes = []
        current_node = node
        
        # 递归解析嵌套的数组声明符
        while current_node and current_node.type == 'array_declarator':
            dimension = self._extract_array_dimension(current_node)
            if dimension is not None:
                array_sizes.append(dimension)
            
            # 查找下一层或标识符
            next_node = None
            for child in current_node.children:
                if child.type == 'identifier':
                    variable_info['name'] = self.tree_sitter.get_node_text(child)
                elif child.type in ['array_declarator', 'pointer_declarator']:
                    next_node = child
                    break
            
            current_node = next_node
        
        # 处理最后的指针声明符
        if current_node and current_node.type == 'pointer_declarator':
            self._parse_pointer_declarator(current_node, variable_info)
        
        # 反转数组维度以保持正确的顺序
        array_sizes.reverse()
        
        variable_info['array_size'] = array_sizes
        
        logger.debug(f"Parsed array: sizes={array_sizes}, name={variable_info['name']}")
    
    def _extract_array_dimension(self, array_node: Node) -> Union[int, str, None]:
        """提取数组维度"""
        array_close = [0, 0]
        array_size = 'dynamic'
        for child in array_node.children:

            if child.type == '[':
                array_close[0] += 1
            elif child.type == ']':
                array_close[1] += 1
            # 处理数组大小表达式
            elif child.type in [
                'number_literal', 'hex_literal', 'octal_literal',
                'decimal_literal', 'binary_expression','preproc_arg'
            ] or( array_close[0] and array_close[0] != array_close[1]):
                try:
                    raw_value = self.tree_sitter.get_node_text(child)
                    
                    # 使用ExpressionParser解析
                    parsed_value, value_type = ExpressionParser.parse(
                        raw_value,
                        self.type_manager.get_enum_values(),
                        self.type_manager.get_macro_definition()
                    )
                    
                    if isinstance(parsed_value, (int, float)):
                        array_size = int(parsed_value)
                    else:
                        array_size = raw_value
                        
                except Exception as e:
                    logger.warning(f"Could not parse array size expression: {raw_value}, error: {e}")
                    array_size = self.tree_sitter.get_node_text(child)

        if array_close[0] != array_close[1]:
            raise ValueError(f"Array dimension mismatch: {array_close}")
        # 如果没有找到大小表达式，返回'dynamic'表示动态数组
        return array_size
    
    def _extract_simple_identifier(self, node: Node, variable_info: Dict[str, Any]) -> None:
        """提取简单标识符（当没有声明符时）"""
        for child in node.children:
            if child.type == 'identifier':
                variable_info['name'] = self.tree_sitter.get_node_text(child)
                break
    
    def _extract_initializer(self, node: Node, variable_info: Dict[str, Any]) -> None:
        """提取初始化器信息"""
        # 查找init_declarator节点
        init_declarator = None
        for child in node.children:
            if child.type == 'init_declarator':
                init_declarator = child
                break
        
        if not init_declarator:
            return
        
        # 在init_declarator中查找初始化器
        for child in init_declarator.children:
            if child.type in [
                'initializer_list', 'assignment_expression', 'binary_expression',
                'number_literal', 'string_literal', 'char_literal'
            ]:
                variable_info['initializer_node'] = child
                variable_info['initial_value'] = self.tree_sitter.get_node_text(child)
                logger.debug(f"Found initializer: {variable_info['initial_value']}")
                break
    
    def _build_complete_type_info(self, variable_info: Dict[str, Any]) -> None:
        """构建完整的类型信息"""
        base_type = variable_info.get('type', '')
        pointer_level = variable_info['pointer_level']
        array_sizes = variable_info.get('array_size', [])
        
        # 构建完整类型字符串
        type_parts = [base_type]
        
        # 添加指针
        if pointer_level > 0:
            type_parts.append('*' * pointer_level)
        
        # 解析类型信息
        type_context = {
            'is_const': variable_info['is_const'],
            'is_volatile': variable_info['is_volatile'],
            'is_restrict': variable_info['is_restrict'],
            'storage_class': variable_info['storage_class'],
            'pointer_level': pointer_level,
            'array_size': array_sizes
        }
        
        resolved_info = self.type_manager.resolve_type(variable_info['type'], type_context)
        variable_info['typeinfo'] = resolved_info
    
        logger.debug(f"Built complete type: {variable_info['type']}")
    
    def _parse_initialization_value(self, variable_info: Dict[str, Any]) -> None:
        """解析初始化值"""
        if not variable_info.get('initializer_node'):
            # 如果没有初始化器，不创建默认值，保持为 None
            variable_info['parsed_value'] = None
            return
        
        try:
            initializer_node = variable_info['initializer_node']
            # 根据节点类型进行解析
            if initializer_node.type == 'initializer_list':
                # 初始化列表：执行两步解析
                parsed_value = self._parse_initializer_direct(initializer_node, variable_info)
            else:
                # 其他类型：直接解析
                parsed_value = self._parse_value_from_node(initializer_node)
            
            variable_info['parsed_value'] = parsed_value
                
        except Exception as e:
            logger.exception(f"Failed to parse initialization value for {variable_info['name']}: {e}")
            variable_info['parsed_value'] = None
    
    def _parse_initializer_direct(self, node: Node, variable_info: Dict[str, Any]) -> Any:
        """直接解析初始化器：两步解析法"""

        if variable_info['name'] == "test_data_values":
            logger.info("")

        # 第一步：按C语言语法解析原始数据
        raw_data = self._parse_raw_initializer(node)

        del variable_info['initializer_node']

        # 第二步：如果是动态数组，尝试从初始化器推断维度
        if variable_info.get('array_size'):
            self._infer_dynamic_array_sizes(raw_data, variable_info)

        # 第三步：根据类型信息进行填充
        parsed_value = self._wapper_raw_data(raw_data, variable_info)
        
        return parsed_value
        
    def _wapper_raw_data(self, raw_data: Union[List[Any], Any], variable_info: Dict[str, Any]) -> List[Any]:
        """将原始数据转换为JSON格式"""

        array_size = variable_info.get('array_size', [])
        is_struct = variable_info['typeinfo'].get('is_struct', False)
        is_union = variable_info['typeinfo'].get('is_union', False)
        is_pointer = variable_info['typeinfo'].get('is_pointer', False)

        if array_size:
            # 变量定义为数组：使用数组展开函数
            child_size = array_size[0]
            variable_info_child = copy.deepcopy(variable_info)
            variable_info_child['array_size'].pop(0)   

            expanded_data = []
            raw_data_length = len(raw_data)
            for i in range(min(child_size, raw_data_length)):
                if (is_struct or is_union) and not is_pointer:
                    data = self._wapper_raw_data(raw_data[i], variable_info_child)
                else:
                    data = raw_data[i]
                expanded_data.append(data) 
            return expanded_data
        
        elif (is_struct or is_union) and not is_pointer:
            return self._fill_field_data(raw_data, variable_info)
        else:
            return raw_data

    def _parse_value_from_node(self, node: Node) -> Any:
        """从AST节点解析值 - 原ValueParser的核心功能"""
        try:
            if not node:
                return None
                
            logger.debug(f"Parsing value from node type: {node.type}")
            
            # 根据节点类型进行解析
            if node.type in ['number_literal', 'hex_literal', 'octal_literal', 'binary_literal']:
                return self._parse_literal_or_identifier_node(node, lambda text: 0)
            elif node.type == 'string_literal':
                return self._parse_literal_or_identifier_node(node, lambda text: text.strip('"'))
            elif node.type == 'char_literal':
                return self._parse_literal_or_identifier_node(node, lambda text: text.strip("'"))
            elif node.type == 'identifier':
                 return self._parse_literal_or_identifier_node(node)
            elif node.type == 'assignment_expression':
                return self._parse_assignment_expression_node(node)
            elif node.type in ['true', 'false']:
                return node.type == 'true'
            elif node.type in ['null', 'NULL']:
                return None
            else:
                # 对于其他类型，尝试解析为表达式
                return self._parse_literal_or_identifier_node(node)
                
        except Exception as e:
            logger.exception(f"Failed to parse value from node {node.type}: {str(e)}")
            return None
    
    def _parse_raw_initializer(self, node: Node) -> Union[List[Any], Any]:
        """解析原始初始化器数据（按C语言语法）"""
        result = []
        
        for child in node.children:
            if child.type == 'initializer_pair':
                # 指定初始化 {.field = value} - 转换为dict并放入list
                field_name, field_value = self._parse_designated_initializer(child)
                if field_name and field_value is not None:
                    result.append({field_name: field_value})
            elif child.type == 'initializer_list':
                # 嵌套初始化列表
                nested_value = self._parse_raw_initializer(child)
                result.append(nested_value)
            elif child.type == 'sizeof_expression':
                result.append(child.text.decode('utf8'))
            elif self._is_value_node(child):
                # 单个值
                value = self._parse_value_from_node(child)
                result.append(value)
        
        return result
    
    def _fill_field_data(self, raw_data: List[Any], variable_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """根据结构定义填充数据"""
        info = variable_info['typeinfo'].get('info')
        if not info or 'fields' not in info:
            raise ValueError(f"No  fields found for struct: {variable_info['typeinfo'].get('type', 'unknown')}")

        if info['kind'] == 'union':
            union_fields = [info['fields'][0]]
            for i in raw_data:
                if isinstance(i, dict):
                    fields_name = list(i.keys())[0]
                    union_fields = [field for field in info['fields'] if field['name'] == fields_name]
                    break
            fields = union_fields
        else:
            fields = info['fields']
            
        result = {}
        for i in range(min(len(fields), len(raw_data))):
            field = fields[i]
            field_name = field['name']
            array_size = field['array_size']
            field_type_info = self.type_manager.resolve_type(field['type'])
            is_struct = field_type_info['is_struct']
            is_union = field_type_info['is_union']
            is_pointer = field_type_info['is_pointer']
            field_raw_value = raw_data[i]

            field_variable_info = {
                'name': field_name, 
                'type': field['type'], 
                'array_size': array_size,
                'typeinfo': field_type_info
                }

            if array_size and (is_struct or is_union):
                result[field_name] = self._wapper_raw_data(field_raw_value, field_variable_info)
            elif (is_struct or is_union) and not is_pointer:
                result[field_name] = self._fill_field_data(field_raw_value, field_variable_info)
            elif isinstance(field_raw_value, dict):
                result.update(field_raw_value)
            else:
                result[field_name] = field_raw_value
            
        return result
    def _parse_literal_or_identifier_node(self, node: Node, fallback_handler=None) -> Any:
        """统一解析字面量和标识符节点 - 使用 ExpressionParser"""
        text = self.tree_sitter.get_node_text(node)
        
        try:
            # 统一使用 ExpressionParser 处理所有类型
            value, _ = ExpressionParser.parse(
                text,
                self.type_manager.get_enum_values() if self.type_manager else {},
                self.type_manager.get_macro_definition() if self.type_manager else {}
            )
            return value
        except Exception as e:
            # 如果 ExpressionParser 失败，使用后备处理器
            if fallback_handler:
                return fallback_handler(text)
            else:
                logger.debug(f"Failed to parse {node.type} '{text}': {e}")
                return text
    
    def _parse_assignment_expression_node(self, node: Node) -> Any:
        """解析赋值表达式节点"""
        # 获取右侧的值
        value_node = node.child_by_field_name('right')
        if value_node:
            return self._parse_value_from_node(value_node)
        return None

    def _parse_designated_initializer(self, node: Node) -> Tuple[Optional[Union[str, int]], Any]:
            """解析指定初始化器节点 {.field = value} 或 {[index] = value}"""
            field_name = None
            field_value = None
            
            for child in node.children:
                if child.type == 'field_designator':
                    # 获取字段名 {.field = value}
                    for designator_child in child.children:
                        if designator_child.type == 'field_identifier':
                            field_name = self.tree_sitter.get_node_text(designator_child)
                            break
                elif child.type == 'subscript_designator':
                    # 获取数组索引 {[index] = value}
                    for designator_child in child.children:
                        if designator_child.type in ['number_literal', 'identifier']:
                            index_text = self.tree_sitter.get_node_text(designator_child)
                            try:
                                field_name = int(index_text)
                            except ValueError:
                                field_name = index_text
                            break
                elif child.type == 'initializer_list':
                    field_value = self._parse_raw_initializer(child)
                elif child.type == 'initializer_pair':
                    field_value = self._parse_designated_initializer(child)
                elif self._is_value_node(child):
                    # 获取字段值
                    field_value = self._parse_value_from_node(child)
            
            return field_name, field_value    
    def _is_value_node(self, node: Node) -> bool:
        """判断节点是否为值节点"""
        return node.type in [
            'number_literal', 'hex_literal', 'octal_literal', 'binary_literal',
            'string_literal', 'char_literal', 'identifier', 'true', 'false',
            'null', 'NULL', 'assignment_expression', 'binary_expression',
            'unary_expression', 'call_expression', 'parenthesized_expression',
            'conditional_expression', 'cast_expression', 'field_expression',
            'subscript_expression', 'pointer_expression', 'compound_literal_expression'
        ]
    
    def _infer_dynamic_array_sizes(self, parsed_value: Union[List[Any], Any], variable_info: Dict[str, Any]) -> None:
        """从初始化器推断动态数组的维度"""
        try:
            if not isinstance(parsed_value, list) or not variable_info.get('array_size'):
                return
            
            array_sizes =  variable_info['array_size']
            dim_length = len(array_sizes)
            current_data = parsed_value
            
            logger.debug(f"Inferring array sizes for {variable_info['name']}, current sizes: {array_sizes}, data length: {len(current_data)}")
            
            # 遍历每个维度，推断动态大小
            for i in range(dim_length):
                dim_size = array_sizes[i]
                if dim_size == 'dynamic' and isinstance(current_data, list):
                    inferred_size = len(current_data)
                    array_sizes[i] = inferred_size
                    logger.debug(f"Inferred dimension {i} size: {inferred_size}")
                    
                    # 移动到下一层数据（如果存在嵌套数组）
                    if current_data and isinstance(current_data[0], list):
                        current_data = current_data[0]
                    else:
                        break
                elif dim_size == 'dynamic':
                    # 如果不是列表，说明是单个元素，推断为1
                    array_sizes[i] = 1
                    logger.debug(f"Inferred dimension {i} size: 1 (single element)")
                    break
            
            logger.debug(f"Final array sizes for {variable_info['name']}: {array_sizes}")
            
        except Exception as e:
            logger.warning(f"Failed to infer array dimensions for {variable_info['name']}: {e}")
    
    def _log_and_store_variable(self, variable_info: Dict[str, Any]) -> None:
        """记录和存储变量信息"""
        logger.info(f"Parsed variable: {variable_info['name']}, "
                    f"Type: {variable_info.get('type')}, "
                    f"Value: {variable_info['initial_value']}")
        
        if variable_info['parsed_value'] is not None:
            logger.debug(f"Structured data: {json.dumps(variable_info['parsed_value'], indent=2, default=str)}")
        
        # 创建一个副本用于存储，移除不可序列化的 AST 节点
        storable_info = variable_info.copy()
        if 'initializer_node' in storable_info:
            del storable_info['initializer_node']
        
        self.data_manager.add_variable(storable_info)
    
    def _get_node_location(self, node: Node) -> Dict[str, Any]:
        """获取节点位置信息"""
        line, col = node.start_point
        return {
            'file': self.current_file,
            'line': line + 1,
            'column': col
        }
    
    def get_simplified_output(self) -> Dict[str, Any]:
        """获取简化的输出数据，只包含核心字段
        
        Returns:
            Dict[str, Any]: 简化的数据结构，包含：
            - variables: 所有变量的简化信息（只包含name、type、array_size、parsed_value）
        """
        try:
            # 获取完整数据
            full_data = self.data_manager.get_all_data()
            
            # 构建简化的变量数据
            simplified_variables = []
            
            # 处理结构体变量
            for var in full_data.get('variables', {}).get('struct_vars', []):
                simplified_var = self._create_simplified_variable(var)
                if simplified_var:
                    simplified_variables.append(simplified_var)
            
            # 处理数组变量
            for var in full_data.get('variables', {}).get('array_vars', []):
                simplified_var = self._create_simplified_variable(var)
                if simplified_var:
                    simplified_variables.append(simplified_var)
            
            # 处理指针变量
            for var in full_data.get('variables', {}).get('pointer_vars', []):
                simplified_var = self._create_simplified_variable(var)
                if simplified_var:
                    simplified_variables.append(simplified_var)
            
            # 处理普通变量
            for var in full_data.get('variables', {}).get('variables', []):
                simplified_var = self._create_simplified_variable(var)
                if simplified_var:
                    simplified_variables.append(simplified_var)
            
            result = {
                'variables': simplified_variables
            }
            
            logger.info(f"Generated simplified output with {len(simplified_variables)} variables")
            return result
            
        except Exception as e:
            logger.exception(f"Failed to generate simplified output: {e}")
            raise
    
    def _create_simplified_variable(self, var: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建简化的变量信息，只包含核心字段
        
        Args:
            var: 原始变量信息
            
        Returns:
            Optional[Dict[str, Any]]: 简化的变量信息，只包含：
            - name: 变量名
            - type: 变量类型
            - array_size: 数组维度
            - parsed_value: 解析后的值
        """
        try:
            if not var.get('name'):
                return None
                
            simplified = {
                'name': var['name'],
                'type': var.get('type', ''),
                'array_size': var.get('array_size', []),
                'parsed_value': var.get('parsed_value')
            }

            if not simplified.get('array_size'):
                del simplified['array_size']
            
            return simplified
            
        except Exception as e:
            logger.warning(f"Failed to simplify variable {var.get('name', 'unknown')}: {e}")
            return None
    
    def export_simplified_json(self, output_path: str = None) -> str:
        """导出简化的JSON数据
        
        Args:
            output_path: 输出文件路径，如果为None则返回JSON字符串
            
        Returns:
            str: JSON字符串或文件路径
        """
        try:
            simplified_data = self.get_simplified_output()
            
            if output_path:
                # 写入文件
                import json
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(simplified_data, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"Simplified data exported to: {output_path}")
                return output_path
            else:
                # 返回JSON字符串
                import json
                return json.dumps(simplified_data, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            logger.exception(f"Failed to export simplified JSON: {e}")
            raise
    

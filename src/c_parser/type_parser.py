from typing import Dict, Any, Optional, List
from utils.logger_config import get_logger
from utils.tree_sitter_util import TreeSitterUtil
from struct_converter.core.exceptions import ParseError, TypeError
from .expression_parser import ExpressionParser

logger = get_logger("TypeParser")

class TypeParser:
    """C语言类型解析器"""
    
    def __init__(self, type_manager=None):
        self.type_manager = type_manager
        self.util = TreeSitterUtil()
        self.expr_parser = ExpressionParser()
        
    def parse_type(self, node) -> Dict[str, Any]:
        """解析类型声明
        
        Args:
            node: 类型声明节点
            
        Returns:
            Dict: 包含类型信息的字典
        """
        try:
            # 获取基本类型
            base_type = self._get_base_type(node)
            
            # 获取类型限定符
            qualifiers = self._get_type_qualifiers(node)
            
            # 获取存储类说明符
            storage = self._get_storage_class(node)
            
            # 获取指针级别
            pointer_level = self._get_pointer_level(node)
            
            # 获取数组维度
            array_dims = self._get_array_dimensions(node)
            
            result = {
                'base_type': base_type,
                'qualifiers': qualifiers,
                'storage': storage
            }
            
            if pointer_level > 0:
                result['pointer_level'] = pointer_level
                
            if array_dims:
                result['array_dimensions'] = array_dims
                
            return result
            
        except Exception as e:
            raise ParseError("Failed to parse type declaration", node) from e
            
    def _get_base_type(self, node) -> str:
        """获取基本类型"""
        try:
            type_parts = []
            current = node
            
            while current:
                if self.util.is_node_type(current, (
                    'primitive_type',
                    'type_identifier',
                    'sized_type_specifier'
                )):
                    type_parts.append(self.util.get_node_text(current))
                current = current.next_sibling
                
            if not type_parts:
                raise TypeError("Missing base type", node)
                
            return ' '.join(type_parts)
            
        except Exception as e:
            raise ParseError("Failed to get base type", node) from e
            
    def _get_type_qualifiers(self, node) -> List[str]:
        """获取类型限定符"""
        qualifiers = []
        current = node
        
        while current:
            if self.util.is_node_type(current, ('const', 'volatile', 'restrict')):
                qualifiers.append(self.util.get_node_text(current))
            current = current.next_sibling
            
        return qualifiers
        
    def _get_storage_class(self, node) -> Optional[str]:
        """获取存储类说明符"""
        current = node
        
        while current:
            if self.util.is_node_type(current, ('static', 'extern', 'auto', 'register')):
                return self.util.get_node_text(current)
            current = current.next_sibling
            
        return None
        
    def _get_pointer_level(self, node) -> int:
        """获取指针级别"""
        level = 0
        current = node
        
        while current:
            if self.util.is_node_type(current, 'pointer_declarator'):
                level += 1
            current = current.parent
            
        return level
        
    def _get_array_dimensions(self, node) -> List[int]:
        """获取数组维度"""
        try:
            dimensions = []
            array_nodes = self.util.find_children_by_type(node, 'array_declarator')
            
            for array_node in array_nodes:
                size_node = self.util.get_node_field(array_node, 'size')
                if size_node:
                    # 使用 ExpressionParser 解析数组大小表达式
                    value, _ = self.expr_parser.parse(
                        self.util.get_node_text(size_node),
                        self.type_manager.get_enum_info() if self.type_manager else {},
                        self.type_manager.get_macro_definition() if self.type_manager else {}
                    )
                    
                    if isinstance(value, (int, float)):
                        dimensions.append(int(value))
                    else:
                        logger.warning(f"Array size must be a number: {self.util.get_node_text(size_node)}")
                        dimensions.append(0)  # 使用0表示未知大小
                        
            return dimensions
            
        except Exception as e:
            logger.error(f"Failed to get array dimensions: {e}")
            return [] 
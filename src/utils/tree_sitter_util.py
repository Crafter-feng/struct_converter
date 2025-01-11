from typing import Optional, List, Any
from tree_sitter import Node
from utils.logger_config import setup_logger

logger = setup_logger('TreeSitterUtil')

class TreeSitterUtil:
    """Tree-sitter 工具类"""
    
    @staticmethod
    def get_node_text(node: Node, encoding: str = 'utf8') -> str:
        """获取节点文本"""
        try:
            return node.text.decode(encoding)
        except Exception as e:
            logger.error(f"Failed to decode node text: {str(e)}")
            return ''
            
    @staticmethod
    def find_child_by_type(node: Node, type_name: str) -> Optional[Node]:
        """查找指定类型的子节点"""
        for child in node.children:
            if child.type == type_name:
                return child
        return None
        
    @staticmethod
    def find_children_by_type(node: Node, type_name: str) -> List[Node]:
        """查找所有指定类型的子节点"""
        return [child for child in node.children if child.type == type_name]
        
    @staticmethod
    def find_first_named_child(node: Node) -> Optional[Node]:
        """查找第一个命名子节点"""
        for child in node.children:
            if child.is_named:
                return child
        return None
        
    @staticmethod
    def get_node_range(node: Node) -> tuple:
        """获取节点的位置范围"""
        return (
            (node.start_point[0], node.start_point[1]),
            (node.end_point[0], node.end_point[1])
        )
        
    @staticmethod
    def is_node_type(node: Node, type_name: str) -> bool:
        """检查节点类型"""
        return node.type == type_name
        
    @staticmethod
    def get_node_field(node: Node, field_name: str) -> Optional[Node]:
        """获取节点的字段"""
        try:
            return node.child_by_field_name(field_name)
        except Exception:
            return None 
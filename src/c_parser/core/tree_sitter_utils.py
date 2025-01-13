from typing import Dict, Any, Optional, List, Tuple, Union
from pathlib import Path
from tree_sitter import Language, Parser, Node
from loguru import logger
from config import TreeSitterConfig

logger = logger.bind(name="TreeSitterUtils")

class TreeSitterUtils:
    """Tree-sitter工具类，提供基础的AST解析功能"""
    
    _instance = None
    _parser = None
    _language = None
    
    @classmethod
    def get_instance(cls, config: Optional[TreeSitterConfig] = None) -> 'TreeSitterUtils':
        """获取单例实例"""
        if not cls._instance:
            cls._instance = cls(config)
        return cls._instance
        
    def __init__(self, config: Optional[TreeSitterConfig] = None):
        """初始化工具类
        
        Args:
            config: tree-sitter配置,可选
        """
        if TreeSitterUtils._parser:
            return
            
        self.config = config or TreeSitterConfig()
        TreeSitterUtils._parser = Parser()
        self._init_language()
        
    def _init_language(self):
        """初始化tree-sitter C语言支持"""
        try:
            # 构建语言库
            if not TreeSitterUtils._language:
                Language.build_library(
                    # 生成动态库文件
                    self.config.get_library_path(),
                    # 语言定义文件路径
                    [self.config.c_parser_path]
                )
                # 加载语言
                TreeSitterUtils._language = Language(
                    self.config.get_library_path(),
                    self.config.language_name
                )
                
            # 设置解析器语言
            TreeSitterUtils._parser.set_language(TreeSitterUtils._language)
            logger.info("Tree-sitter language initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize tree-sitter language: {e}")
            raise

    @staticmethod
    def parse_source(source: str) -> Node:
        """解析源代码字符串
        
        Args:
            source: 源代码字符串
            
        Returns:
            Node: AST根节点
        """
        try:
            # 将源码转换为bytes
            source_bytes = bytes(source, 'utf8')
            # 解析生成语法树
            tree = TreeSitterUtils._parser.parse(source_bytes)
            return tree.root_node
        except Exception as e:
            logger.error(f"Failed to parse source: {e}")
            raise

    @staticmethod
    def parse_file(file_path: Union[str, Path]) -> Node:
        """解析源文件
        
        Args:
            file_path: 源文件路径
            
        Returns:
            Node: AST根节点
        """
        try:
            if isinstance(file_path, str):
                file_path = Path(file_path)
                
            # 读取文件内容
            source = file_path.read_text(encoding='utf8', errors='ignore')
            return TreeSitterUtils.parse_source(source)
        except Exception as e:
            logger.error(f"Failed to parse file {file_path}: {e}")
            raise

    @staticmethod
    def parse_type_string(type_str: str) -> Optional[Node]:
        """解析类型声明字符串
        
        Args:
            type_str: 类型声明字符串
            
        Returns:
            Optional[Node]: 类型节点,解析失败返回None
        """
        try:
            # 包装成完整的声明
            source = f"typedef {type_str} test_t;"
            root = TreeSitterUtils.parse_source(source)
            
            # 从typedef中提取类型节点
            for child in root.children:
                if child.type == 'type_definition':
                    # 遍历所有子节点查找类型
                    for node in child.children:
                        if node.type in [
                            'primitive_type',
                            'type_identifier', 
                            'pointer_declarator',
                            'array_declarator',
                            'function_declarator',
                            'struct_specifier',
                            'union_specifier',
                            'enum_specifier'
                        ]:
                            return node
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse type string: {type_str}")
            logger.error(f"Error: {e}")
            return None

    @staticmethod
    def get_node_text(node: Node) -> str:
        """获取节点文本
        
        Args:
            node: AST节点
            
        Returns:
            str: 节点文本
        """
        try:
            return node.text.decode('utf8')
        except:
            return ""

    @staticmethod
    def get_child_by_field(node: Node, field: str) -> Optional[Node]:
        """获取指定字段的子节点
        
        Args:
            node: AST节点
            field: 字段名
            
        Returns:
            Optional[Node]: 子节点,不存在返回None
        """
        try:
            return node.child_by_field_name(field)
        except:
            return None 
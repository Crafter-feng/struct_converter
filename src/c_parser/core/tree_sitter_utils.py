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
    def parse(source: Union[str, Path]) -> Node:
        """解析源代码或源文件（自适应）
        
        Args:
            source: 源代码字符串或文件路径
            
        Returns:
            Node: AST根节点
        """
        try:
            # 检查是否为文件路径
            if isinstance(source, (str, Path)):
                # 尝试判断是否为文件路径
                if isinstance(source, Path) or (isinstance(source, str) and TreeSitterUtils._looks_like_file_path(source)):
                    # 作为文件路径处理
                    if isinstance(source, str):
                        source = Path(source)
                    
                    # 读取文件内容
                    source_text = source.read_text(encoding='utf8', errors='ignore')
                    logger.debug(f"Parsing file: {source}")
                else:
                    # 作为源代码字符串处理
                    source_text = source
                    logger.debug("Parsing source code string")
            else:
                raise ValueError(f"Unsupported source type: {type(source)}")
            
            # 添加调试信息
            logger.debug(f"Source text length: {len(source_text)}")
            logger.debug(f"Source text preview: {source_text[:200]}...")
            
            # 将源码转换为bytes
            source_bytes = bytes(source_text, 'utf8')
            # 解析生成语法树
            tree = TreeSitterUtils._parser.parse(source_bytes)
            return tree
            
        except Exception as e:
            logger.exception(f"Failed to parse source: {e}")
            raise
    
    @staticmethod
    def parse_source_code(source_text: str) -> Node:
        """直接解析源代码字符串
        
        Args:
            source_text: 源代码字符串
            
        Returns:
            Node: AST根节点
        """
        try:
            # 添加调试信息
            logger.debug(f"Source text length: {len(source_text)}")
            logger.debug(f"Source text preview: {source_text[:200]}...")
            
            # 将源码转换为bytes
            source_bytes = bytes(source_text, 'utf8')
            # 解析生成语法树
            tree = TreeSitterUtils._parser.parse(source_bytes)
            return tree
            
        except Exception as e:
            logger.exception(f"Failed to parse source code: {e}")
            raise

    @staticmethod
    def _looks_like_file_path(source: str) -> bool:
        """判断字符串是否看起来像文件路径
        
        Args:
            source: 待检查的字符串
            
        Returns:
            bool: 如果看起来像文件路径返回True，否则返回False
        """
        # 快速检查：如果包含C语言关键字或语法，肯定不是文件路径
        c_keywords = ['int', 'char', 'float', 'double', 'struct', 'union', 'enum', 'typedef', 
                     'if', 'else', 'for', 'while', 'return', '#include', '{', '}', ';']
        if any(keyword in source for keyword in c_keywords):
            return False
        
        # 如果字符串很长（超过256字符），很可能不是文件路径
        if len(source) > 256:
            return False
        
        # 如果包含换行符，肯定不是文件路径
        if '\n' in source or '\r' in source:
            return False
        
        # 检查是否包含常见的C/C++文件扩展名
        if '.' in source and source.count('.') <= 3:  # 避免误判浮点数
            extensions = ['.c', '.h', '.cpp', '.hpp', '.cc', '.cxx']
            if any(source.lower().endswith(ext) for ext in extensions):
                return True
        
        # 检查是否包含路径分隔符（但不包含其他非路径字符）
        if ('/' in source or '\\' in source) and not any(c in source for c in ['=', '(', ')', '{', '}', ';']):
            return True
        
        # 检查是否存在作为文件（只对短字符串进行文件系统检查）
        if len(source) < 100:
            try:
                path = Path(source)
                return path.exists() and path.is_file()
            except:
                return False
        
        return False
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
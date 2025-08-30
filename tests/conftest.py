import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
from tree_sitter import Node, Language, Parser

# 添加src目录到Python路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from c_parser.core.tree_sitter_utils import TreeSitterUtils
from c_parser.core.type_manager import TypeManager
from c_parser.core.data_manager import DataManager
from c_parser.core.expression_parser import ExpressionParser
from c_parser.type_parser import CTypeParser
from c_parser.data_parser import CDataParser


@pytest.fixture
def sample_c_code():
    """提供示例C代码用于测试"""
    return """
    #include <stdint.h>
    
    typedef uint8_t u8;
    typedef uint16_t u16;
    
    typedef struct Point {
        int x;
        int y;
    } Point;
    
    typedef enum Color {
        RED = 0,
        GREEN = 1,
        BLUE = 2
    } Color;
    
    #define MAX_SIZE 100
    #define PI 3.14159
    
    static int global_var = 42;
    static Point test_point = {10, 20};
    static u8 buffer[256];
    """


@pytest.fixture
def sample_c_file(sample_c_code):
    """创建临时C文件用于测试"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write(sample_c_code)
        temp_file = f.name
    
    yield temp_file
    
    # 清理
    try:
        os.unlink(temp_file)
    except:
        pass


@pytest.fixture
def mock_tree_sitter_parser():
    """模拟Tree-sitter解析器"""
    with patch('c_parser.core.tree_sitter_utils.Parser') as mock_parser_class:
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        
        # 模拟解析结果
        mock_node = Mock(spec=Node)
        mock_node.text = b"test content"
        mock_tree = Mock()
        mock_tree.root_node = mock_node
        mock_parser.parse.return_value = mock_tree
        
        yield mock_parser


@pytest.fixture
def mock_language():
    """模拟Tree-sitter语言"""
    with patch('c_parser.core.tree_sitter_utils.Language') as mock_language_class:
        mock_lang = Mock(spec=Language)
        mock_language_class.return_value = mock_lang
        yield mock_lang


@pytest.fixture
def type_manager():
    """创建TypeManager实例"""
    return TypeManager()


@pytest.fixture
def data_manager(type_manager):
    """创建DataManager实例"""
    return DataManager(type_manager)


@pytest.fixture
def expression_parser():
    """创建ExpressionParser实例"""
    return ExpressionParser()


@pytest.fixture
def type_parser(type_manager):
    """创建CTypeParser实例"""
    return CTypeParser(type_manager)


@pytest.fixture
def data_parser(type_manager):
    """创建CDataParser实例"""
    return CDataParser(type_manager)


@pytest.fixture
def test_structs_h_path():
    """返回test_structs.h文件路径"""
    return Path(__file__).parent / "fixtures" / "c_files" / "test_structs.h"


@pytest.fixture
def test_data_c_path():
    """返回test_data.c文件路径"""
    return Path(__file__).parent / "fixtures" / "c_files" / "test_data.c"


class MockNode:
    """模拟AST节点"""
    def __init__(self, node_type="", text="", children=None):
        self.type = node_type
        self.text = text.encode('utf-8') if isinstance(text, str) else text
        self.children = children or []
        self.start_byte = 0
        self.end_byte = len(self.text) if self.text else 0
    
    def child_by_field_name(self, field_name):
        """模拟字段访问"""
        for child in self.children:
            if hasattr(child, 'field_name') and child.field_name == field_name:
                return child
        return None
    
    def __iter__(self):
        return iter(self.children)


def create_mock_node(node_type, text="", children=None, field_name=None):
    """创建带字段名的模拟节点"""
    node = MockNode(node_type, text, children)
    if field_name:
        node.field_name = field_name
    return node

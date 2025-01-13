import pytest
from c_parser.core.tree_sitter_base import TreeSitterParser
from c_parser.data_parser import DataParser

def test_parse_and_generate_struct():
    c_code = """
    struct Point {
        int x;
        int y;
    };
    """
    
    # 解析C代码
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    
    # 生成Python代码
    data_parser = DataParser()
    python_code = data_parser.generate_python(ast)
    
    assert "class Point:" in python_code
    assert "self.x" in python_code
    assert "self.y" in python_code

def test_parse_and_generate_complex_struct():
    c_code = """
    struct Rectangle {
        struct Point top_left;
        struct Point bottom_right;
        int area;
    };
    """
    
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    
    data_parser = DataParser()
    python_code = data_parser.generate_python(ast)
    
    assert "class Rectangle:" in python_code
    assert "self.top_left" in python_code
    assert "self.bottom_right" in python_code 
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from tree_sitter import Node, Language, Parser

from c_parser.core.tree_sitter_utils import TreeSitterUtils


class TestTreeSitterUtils:
    """TreeSitterUtils测试类"""
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        # 重置单例
        TreeSitterUtils._instance = None
        TreeSitterUtils._parser = None
        TreeSitterUtils._language = None
        
        # 创建第一个实例
        instance1 = TreeSitterUtils.get_instance()
        assert instance1 is not None
        
        # 创建第二个实例，应该返回同一个对象
        instance2 = TreeSitterUtils.get_instance()
        assert instance1 is instance2
    
    @patch('c_parser.core.tree_sitter_utils.Language')
    @patch('c_parser.core.tree_sitter_utils.Parser')
    def test_initialization(self, mock_parser_class, mock_language_class):
        """测试初始化过程"""
        # 重置单例
        TreeSitterUtils._instance = None
        TreeSitterUtils._parser = None
        TreeSitterUtils._language = None
        
        # 模拟组件
        mock_parser = Mock()
        mock_language = Mock()
        mock_parser_class.return_value = mock_parser
        mock_language_class.return_value = mock_language
        
        # 创建实例
        utils = TreeSitterUtils()
        
        # 验证初始化调用
        mock_parser_class.assert_called_once()
        mock_language.build_library.assert_called_once()
        mock_language_class.assert_called_once()
        mock_parser.set_language.assert_called_once_with(mock_language)
    
    @patch('c_parser.core.tree_sitter_utils.Language')
    @patch('c_parser.core.tree_sitter_utils.Parser')
    def test_parse_source_code_string(self, mock_parser_class, mock_language_class):
        """测试解析源代码字符串"""
        # 重置单例
        TreeSitterUtils._instance = None
        TreeSitterUtils._parser = None
        TreeSitterUtils._language = None
        
        # 模拟组件
        mock_parser = Mock()
        mock_language = Mock()
        mock_parser_class.return_value = mock_parser
        mock_language_class.return_value = mock_language
        
        # 模拟解析结果
        mock_node = Mock(spec=Node)
        mock_tree = Mock()
        mock_tree.root_node = mock_node
        mock_parser.parse.return_value = mock_tree
        
        # 创建实例
        utils = TreeSitterUtils()
        
        # 测试解析源代码字符串
        source_code = "int main() { return 0; }"
        result = TreeSitterUtils.parse(source_code)
        
        # 验证结果
        assert result is mock_node
        mock_parser.parse.assert_called_once()
        call_args = mock_parser.parse.call_args[0][0]
        assert call_args == b"int main() { return 0; }"
    
    @patch('c_parser.core.tree_sitter_utils.Language')
    @patch('c_parser.core.tree_sitter_utils.Parser')
    def test_parse_file_path(self, mock_parser_class, mock_language_class, sample_c_file):
        """测试解析文件路径"""
        # 重置单例
        TreeSitterUtils._instance = None
        TreeSitterUtils._parser = None
        TreeSitterUtils._language = None
        
        # 模拟组件
        mock_parser = Mock()
        mock_language = Mock()
        mock_parser_class.return_value = mock_parser
        mock_language_class.return_value = mock_language
        
        # 模拟解析结果
        mock_node = Mock(spec=Node)
        mock_tree = Mock()
        mock_tree.root_node = mock_node
        mock_parser.parse.return_value = mock_tree
        
        # 创建实例
        utils = TreeSitterUtils()
        
        # 测试解析文件路径
        result = TreeSitterUtils.parse(sample_c_file)
        
        # 验证结果
        assert result is mock_node
        mock_parser.parse.assert_called_once()
    
    @patch('c_parser.core.tree_sitter_utils.Language')
    @patch('c_parser.core.tree_sitter_utils.Parser')
    def test_parse_path_object(self, mock_parser_class, mock_language_class, sample_c_file):
        """测试解析Path对象"""
        # 重置单例
        TreeSitterUtils._instance = None
        TreeSitterUtils._parser = None
        TreeSitterUtils._language = None
        
        # 模拟组件
        mock_parser = Mock()
        mock_language = Mock()
        mock_parser_class.return_value = mock_parser
        mock_language_class.return_value = mock_language
        
        # 模拟解析结果
        mock_node = Mock(spec=Node)
        mock_tree = Mock()
        mock_tree.root_node = mock_node
        mock_parser.parse.return_value = mock_tree
        
        # 创建实例
        utils = TreeSitterUtils()
        
        # 测试解析Path对象
        path_obj = Path(sample_c_file)
        result = TreeSitterUtils.parse(path_obj)
        
        # 验证结果
        assert result is mock_node
        mock_parser.parse.assert_called_once()
    
    def test_looks_like_file_path(self):
        """测试文件路径判断逻辑"""
        # 测试C代码字符串（应该返回False）
        assert not TreeSitterUtils._looks_like_file_path("int main() { return 0; }")
        assert not TreeSitterUtils._looks_like_file_path("struct Point { int x; int y; };")
        assert not TreeSitterUtils._looks_like_file_path("#include <stdio.h>")
        
        # 测试长字符串（应该返回False）
        long_string = "a" * 300
        assert not TreeSitterUtils._looks_like_file_path(long_string)
        
        # 测试包含换行符的字符串（应该返回False）
        assert not TreeSitterUtils._looks_like_file_path("file.c\n")
        assert not TreeSitterUtils._looks_like_file_path("file.c\r\n")
        
        # 测试文件路径（应该返回True）
        assert TreeSitterUtils._looks_like_file_path("test.c")
        assert TreeSitterUtils._looks_like_file_path("test.h")
        assert TreeSitterUtils._looks_like_file_path("test.cpp")
        assert TreeSitterUtils._looks_like_file_path("test.hpp")
        assert TreeSitterUtils._looks_like_file_path("test.cc")
        assert TreeSitterUtils._looks_like_file_path("test.cxx")
        assert TreeSitterUtils._looks_like_file_path("/path/to/file.c")
        assert TreeSitterUtils._looks_like_file_path("C:\\path\\to\\file.c")
        
        # 测试包含路径分隔符但不包含C语法的字符串
        assert TreeSitterUtils._looks_like_file_path("/usr/include/test.h")
        assert TreeSitterUtils._looks_like_file_path("src\\main.c")
    
    def test_get_node_text(self):
        """测试获取节点文本"""
        # 创建模拟节点
        mock_node = Mock(spec=Node)
        mock_node.text = b"test content"
        
        # 测试正常情况
        result = TreeSitterUtils.get_node_text(mock_node)
        assert result == "test content"
        
        # 测试异常情况
        mock_node.text = None
        result = TreeSitterUtils.get_node_text(mock_node)
        assert result == ""
    
    def test_get_child_by_field(self):
        """测试获取指定字段的子节点"""
        # 创建模拟节点
        mock_node = Mock(spec=Node)
        mock_child = Mock(spec=Node)
        mock_node.child_by_field_name.return_value = mock_child
        
        # 测试正常情况
        result = TreeSitterUtils.get_child_by_field(mock_node, "test_field")
        assert result is mock_child
        mock_node.child_by_field_name.assert_called_once_with("test_field")
        
        # 测试字段不存在的情况
        mock_node.child_by_field_name.return_value = None
        result = TreeSitterUtils.get_child_by_field(mock_node, "nonexistent_field")
        assert result is None
    
    @patch('c_parser.core.tree_sitter_utils.Language')
    @patch('c_parser.core.tree_sitter_utils.Parser')
    def test_parse_invalid_source_type(self, mock_parser_class, mock_language_class):
        """测试解析无效的源类型"""
        # 重置单例
        TreeSitterUtils._instance = None
        TreeSitterUtils._parser = None
        TreeSitterUtils._language = None
        
        # 模拟组件
        mock_parser = Mock()
        mock_language = Mock()
        mock_parser_class.return_value = mock_parser
        mock_language_class.return_value = mock_language
        
        # 创建实例
        utils = TreeSitterUtils()
        
        # 测试无效类型
        with pytest.raises(ValueError, match="Unsupported source type"):
            TreeSitterUtils.parse(123)
    
    @patch('c_parser.core.tree_sitter_utils.Language')
    @patch('c_parser.core.tree_sitter_utils.Parser')
    def test_parse_file_not_found(self, mock_parser_class, mock_language_class):
        """测试解析不存在的文件"""
        # 重置单例
        TreeSitterUtils._instance = None
        TreeSitterUtils._parser = None
        TreeSitterUtils._language = None
        
        # 模拟组件
        mock_parser = Mock()
        mock_language = Mock()
        mock_parser_class.return_value = mock_parser
        mock_language_class.return_value = mock_language
        
        # 创建实例
        utils = TreeSitterUtils()
        
        # 测试不存在的文件
        with pytest.raises(Exception):
            TreeSitterUtils.parse("nonexistent_file.c")
    
    @patch('c_parser.core.tree_sitter_utils.Language')
    @patch('c_parser.core.tree_sitter_utils.Parser')
    def test_parse_parser_error(self, mock_parser_class, mock_language_class):
        """测试解析器错误处理"""
        # 重置单例
        TreeSitterUtils._instance = None
        TreeSitterUtils._parser = None
        TreeSitterUtils._language = None
        
        # 模拟组件
        mock_parser = Mock()
        mock_language = Mock()
        mock_parser_class.return_value = mock_parser
        mock_language_class.return_value = mock_language
        
        # 模拟解析错误
        mock_parser.parse.side_effect = Exception("Parser error")
        
        # 创建实例
        utils = TreeSitterUtils()
        
        # 测试解析错误
        with pytest.raises(Exception, match="Parser error"):
            TreeSitterUtils.parse("int main() { return 0; }")

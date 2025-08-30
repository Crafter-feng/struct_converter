import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from tree_sitter import Node

from c_parser.type_parser import CTypeParser
from c_parser.core.type_manager import TypeManager


class TestCTypeParser:
    """CTypeParser测试类"""
    
    def test_initialization(self):
        """测试初始化"""
        # 测试默认初始化
        parser = CTypeParser()
        assert parser.type_manager is not None
        assert isinstance(parser.type_manager, TypeManager)
        assert parser.pointer_size == 8
        assert parser.ts_util is not None
        
        # 测试自定义TypeManager
        custom_tm = TypeManager()
        parser = CTypeParser(custom_tm)
        assert parser.type_manager is custom_tm
    
    @patch('c_parser.type_parser.TreeSitterUtils')
    def test_parse_declarations_with_string(self, mock_ts_utils):
        """测试解析字符串形式的声明"""
        # 模拟TreeSitterUtils
        mock_ts_instance = Mock()
        mock_ts_utils.get_instance.return_value = mock_ts_instance
        
        # 模拟AST节点
        mock_node = Mock(spec=Node)
        mock_ts_instance.parse.return_value = mock_node
        
        parser = CTypeParser()
        
        # 测试解析字符串
        source_code = """
        typedef struct Point {
            int x;
            int y;
        } Point;
        
        typedef enum Color {
            RED = 0,
            GREEN = 1
        } Color;
        """
        
        result = parser.parse_declarations(source_code)
        
        # 验证TreeSitterUtils被调用
        mock_ts_instance.parse.assert_called_once_with(source_code)
    
    @patch('c_parser.type_parser.TreeSitterUtils')
    def test_parse_declarations_with_file_path(self, mock_ts_utils, sample_c_file):
        """测试解析文件路径形式的声明"""
        # 模拟TreeSitterUtils
        mock_ts_instance = Mock()
        mock_ts_utils.get_instance.return_value = mock_ts_instance
        
        # 模拟AST节点
        mock_node = Mock(spec=Node)
        mock_ts_instance.parse.return_value = mock_node
        
        parser = CTypeParser()
        
        # 测试解析文件
        result = parser.parse_declarations(sample_c_file)
        
        # 验证TreeSitterUtils被调用
        mock_ts_instance.parse.assert_called_once()
    
    @patch('c_parser.type_parser.TreeSitterUtils')
    def test_parse_declarations_with_path_object(self, mock_ts_utils, sample_c_file):
        """测试解析Path对象形式的声明"""
        # 模拟TreeSitterUtils
        mock_ts_instance = Mock()
        mock_ts_utils.get_instance.return_value = mock_ts_instance
        
        # 模拟AST节点
        mock_node = Mock(spec=Node)
        mock_ts_instance.parse.return_value = mock_node
        
        parser = CTypeParser()
        
        # 测试解析Path对象
        path_obj = Path(sample_c_file)
        result = parser.parse_declarations(path_obj)
        
        # 验证TreeSitterUtils被调用
        mock_ts_instance.parse.assert_called_once()
    
    @patch('c_parser.type_parser.TreeSitterUtils')
    def test_parse_declarations_with_existing_tree(self, mock_ts_utils):
        """测试使用现有AST树解析声明"""
        # 模拟TreeSitterUtils
        mock_ts_instance = Mock()
        mock_ts_utils.get_instance.return_value = mock_ts_instance
        
        # 模拟AST节点
        mock_node = Mock(spec=Node)
        
        parser = CTypeParser()
        
        # 测试使用现有树
        result = parser.parse_declarations("test source", tree=mock_node)
        
        # 验证TreeSitterUtils没有被调用（因为提供了现有的树）
        mock_ts_instance.parse.assert_not_called()
    
    @patch('c_parser.type_parser.TreeSitterUtils')
    def test_parse_declarations_file_not_found(self, mock_ts_utils):
        """测试解析不存在的文件"""
        # 模拟TreeSitterUtils
        mock_ts_instance = Mock()
        mock_ts_utils.get_instance.return_value = mock_ts_instance
        
        parser = CTypeParser()
        
        # 测试不存在的文件
        result = parser.parse_declarations("nonexistent_file.c")
        
        # 应该返回None
        assert result is None
    
    @patch('c_parser.type_parser.TreeSitterUtils')
    def test_parse_declarations_parser_error(self, mock_ts_utils):
        """测试解析器错误处理"""
        # 模拟TreeSitterUtils抛出异常
        mock_ts_instance = Mock()
        mock_ts_utils.get_instance.return_value = mock_ts_instance
        mock_ts_instance.parse.side_effect = Exception("Parser error")
        
        parser = CTypeParser()
        
        # 测试解析错误
        result = parser.parse_declarations("int main() { return 0; }")
        
        # 应该返回None
        assert result is None
    
    def test_parse_includes(self):
        """测试解析包含文件"""
        parser = CTypeParser()
        
        # 测试包含文件解析
        source_code = """
        #include <stdio.h>
        #include <stdlib.h>
        #include "test.h"
        #include "config.h"
        """
        
        includes = parser._parse_includes(source_code)
        
        # 验证包含文件被正确解析
        assert len(includes) == 4
        assert "stdio.h" in includes
        assert "stdlib.h" in includes
        assert "test.h" in includes
        assert "config.h" in includes
    
    def test_parse_includes_no_includes(self):
        """测试没有包含文件的代码"""
        parser = CTypeParser()
        
        source_code = """
        int main() {
            return 0;
        }
        """
        
        includes = parser._parse_includes(source_code)
        
        # 应该返回空列表
        assert includes == []
    
    def test_parse_includes_complex_patterns(self):
        """测试复杂的包含文件模式"""
        parser = CTypeParser()
        
        source_code = """
        #include <stdio.h>
        #include <stdint.h>
        #include "local.h"
        #include "../include/config.h"
        #include "subdir/header.h"
        #include <system/header.h>
        """
        
        includes = parser._parse_includes(source_code)
        
        # 验证所有包含文件被解析
        assert len(includes) == 6
        assert "stdio.h" in includes
        assert "stdint.h" in includes
        assert "local.h" in includes
        assert "../include/config.h" in includes
        assert "subdir/header.h" in includes
        assert "system/header.h" in includes
    
    @patch('c_parser.type_parser.TreeSitterUtils')
    def test_parse_declarations_with_includes(self, mock_ts_utils, sample_c_file):
        """测试解析包含其他文件的声明"""
        # 模拟TreeSitterUtils
        mock_ts_instance = Mock()
        mock_ts_utils.get_instance.return_value = mock_ts_instance
        
        # 模拟AST节点
        mock_node = Mock(spec=Node)
        mock_ts_instance.parse.return_value = mock_node
        
        parser = CTypeParser()
        
        # 创建包含其他文件的代码
        source_code = """
        #include "test.h"
        #include <stdio.h>
        
        typedef struct Point {
            int x;
            int y;
        } Point;
        """
        
        # 模拟文件存在检查
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.parent', return_value=Path('/tmp')):
                result = parser.parse_declarations(source_code)
        
        # 验证解析过程
        assert mock_ts_instance.parse.called
    
    def test_parse_declarations_error_handling(self):
        """测试声明解析的错误处理"""
        parser = CTypeParser()
        
        # 测试无效输入
        with pytest.raises(Exception):
            parser.parse_declarations(None)
    
    @patch('c_parser.type_parser.TreeSitterUtils')
    def test_parse_declarations_empty_result(self, mock_ts_utils):
        """测试解析返回空结果"""
        # 模拟TreeSitterUtils返回None
        mock_ts_instance = Mock()
        mock_ts_utils.get_instance.return_value = mock_ts_instance
        mock_ts_instance.parse.return_value = None
        
        parser = CTypeParser()
        
        # 测试解析返回None
        result = parser.parse_declarations("test source")
        
        # 应该返回None
        assert result is None
    
    def test_pointer_size_configuration(self):
        """测试指针大小配置"""
        # 测试默认64位
        parser = CTypeParser()
        assert parser.pointer_size == 8
        
        # 测试32位配置
        parser = CTypeParser()
        parser.pointer_size = 4
        assert parser.pointer_size == 4
    
    def test_current_file_tracking(self):
        """测试当前文件跟踪"""
        parser = CTypeParser()
        
        # 初始状态
        assert parser.current_file is None
        
        # 设置当前文件
        parser.current_file = "test.c"
        assert parser.current_file == "test.c"
    
    @patch('c_parser.type_parser.TreeSitterUtils')
    def test_parse_declarations_logging(self, mock_ts_utils, caplog):
        """测试解析过程的日志记录"""
        # 模拟TreeSitterUtils
        mock_ts_instance = Mock()
        mock_ts_utils.get_instance.return_value = mock_ts_instance
        
        # 模拟AST节点
        mock_node = Mock(spec=Node)
        mock_ts_instance.parse.return_value = mock_node
        
        parser = CTypeParser()
        
        # 测试解析并检查日志
        source_code = "typedef int test_type;"
        parser.parse_declarations(source_code)
        
        # 验证日志记录（这里只是检查方法被调用，实际日志内容取决于实现）
        assert mock_ts_instance.parse.called
    
    def test_parse_declarations_with_complex_source(self):
        """测试解析复杂源代码"""
        parser = CTypeParser()
        
        complex_source = """
        // 复杂的C代码示例
        #include <stdint.h>
        
        // 基本类型定义
        typedef uint8_t u8;
        typedef uint16_t u16;
        typedef uint32_t u32;
        
        // 结构体定义
        typedef struct Point {
            int x;
            int y;
        } Point;
        
        // 枚举定义
        typedef enum Color {
            RED = 0,
            GREEN = 1,
            BLUE = 2
        } Color;
        
        // 宏定义
        #define MAX_SIZE 100
        #define PI 3.14159
        
        // 全局变量
        static int global_var = 42;
        static Point test_point = {10, 20};
        """
        
        # 模拟TreeSitterUtils
        with patch('c_parser.type_parser.TreeSitterUtils') as mock_ts_utils:
            mock_ts_instance = Mock()
            mock_ts_utils.get_instance.return_value = mock_ts_instance
            
            # 模拟AST节点
            mock_node = Mock(spec=Node)
            mock_ts_instance.parse.return_value = mock_node
            
            result = parser.parse_declarations(complex_source)
            
            # 验证解析被调用
            mock_ts_instance.parse.assert_called_once_with(complex_source)
    
    def test_parse_declarations_with_unicode(self):
        """测试解析包含Unicode字符的源代码"""
        parser = CTypeParser()
        
        unicode_source = """
        // 包含Unicode注释的代码
        typedef struct 点 {
            int x;
            int y;
        } 点;
        
        // 中文注释
        typedef enum 颜色 {
            RED = 0,
            GREEN = 1
        } 颜色;
        """
        
        # 模拟TreeSitterUtils
        with patch('c_parser.type_parser.TreeSitterUtils') as mock_ts_utils:
            mock_ts_instance = Mock()
            mock_ts_utils.get_instance.return_value = mock_ts_instance
            
            # 模拟AST节点
            mock_node = Mock(spec=Node)
            mock_ts_instance.parse.return_value = mock_node
            
            result = parser.parse_declarations(unicode_source)
            
            # 验证解析被调用
            mock_ts_instance.parse.assert_called_once_with(unicode_source)
    
    def test_parse_declarations_with_preprocessor(self):
        """测试解析包含预处理指令的代码"""
        parser = CTypeParser()
        
        preprocessor_source = """
        #ifdef DEBUG
        #define LOG(msg) printf(msg)
        #else
        #define LOG(msg)
        #endif
        
        #if defined(WINDOWS)
        typedef int platform_int;
        #elif defined(LINUX)
        typedef long platform_int;
        #else
        typedef int platform_int;
        #endif
        
        typedef struct Test {
            platform_int value;
        } Test;
        """
        
        # 模拟TreeSitterUtils
        with patch('c_parser.type_parser.TreeSitterUtils') as mock_ts_utils:
            mock_ts_instance = Mock()
            mock_ts_utils.get_instance.return_value = mock_ts_instance
            
            # 模拟AST节点
            mock_node = Mock(spec=Node)
            mock_ts_instance.parse.return_value = mock_node
            
            result = parser.parse_declarations(preprocessor_source)
            
            # 验证解析被调用
            mock_ts_instance.parse.assert_called_once_with(preprocessor_source)

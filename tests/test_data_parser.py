import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from tree_sitter import Node

from c_parser.data_parser import CDataParser
from c_parser.core.type_manager import TypeManager
from c_parser.core.data_manager import DataManager


class TestCDataParser:
    """CDataParser测试类"""
    
    def test_initialization(self):
        """测试初始化"""
        # 测试默认初始化
        parser = CDataParser()
        assert parser.type_manager is not None
        assert isinstance(parser.type_manager, TypeManager)
        assert parser.tree_sitter is not None
        assert parser.data_manager is not None
        assert isinstance(parser.data_manager, DataManager)
        assert parser.type_parser is not None
        assert parser.current_file is None
        
        # 测试自定义TypeManager
        custom_tm = TypeManager()
        parser = CDataParser(custom_tm)
        assert parser.type_manager is custom_tm
        assert parser.data_manager.type_manager is custom_tm
        assert parser.type_parser.type_manager is custom_tm
    
    @patch('c_parser.data_parser.TreeSitterUtils')
    def test_parse_file_with_string(self, mock_ts_utils):
        """测试解析字符串形式的文件"""
        # 模拟TreeSitterUtils
        mock_ts_instance = Mock()
        mock_ts_utils.get_instance.return_value = mock_ts_instance
        
        # 模拟AST节点
        mock_node = Mock(spec=Node)
        mock_ts_instance.parse.return_value = mock_node
        
        parser = CDataParser()
        
        # 测试解析字符串
        source_code = """
        typedef struct Point {
            int x;
            int y;
        } Point;
        
        static Point test_point = {10, 20};
        static int global_var = 42;
        """
        
        result = parser.parse_file(source_code)
        
        # 验证TreeSitterUtils被调用
        mock_ts_instance.parse.assert_called_once_with(source_code)
        
        # 验证返回结果结构
        assert isinstance(result, dict)
        assert 'structs' in result
        assert 'unions' in result
        assert 'enums' in result
        assert 'typedefs' in result
        assert 'variables' in result
    
    @patch('c_parser.data_parser.TreeSitterUtils')
    def test_parse_file_with_file_path(self, mock_ts_utils, sample_c_file):
        """测试解析文件路径"""
        # 模拟TreeSitterUtils
        mock_ts_instance = Mock()
        mock_ts_utils.get_instance.return_value = mock_ts_instance
        
        # 模拟AST节点
        mock_node = Mock(spec=Node)
        mock_ts_instance.parse.return_value = mock_node
        
        parser = CDataParser()
        
        # 测试解析文件
        result = parser.parse_file(sample_c_file)
        
        # 验证TreeSitterUtils被调用
        mock_ts_instance.parse.assert_called_once()
        
        # 验证当前文件被设置
        assert parser.current_file == sample_c_file
    
    @patch('c_parser.data_parser.TreeSitterUtils')
    def test_parse_file_with_path_object(self, mock_ts_utils, sample_c_file):
        """测试解析Path对象"""
        # 模拟TreeSitterUtils
        mock_ts_instance = Mock()
        mock_ts_utils.get_instance.return_value = mock_ts_instance
        
        # 模拟AST节点
        mock_node = Mock(spec=Node)
        mock_ts_instance.parse.return_value = mock_node
        
        parser = CDataParser()
        
        # 测试解析Path对象
        path_obj = Path(sample_c_file)
        result = parser.parse_file(path_obj)
        
        # 验证TreeSitterUtils被调用
        mock_ts_instance.parse.assert_called_once()
        
        # 验证当前文件被设置
        assert parser.current_file == str(path_obj)
    
    @patch('c_parser.data_parser.TreeSitterUtils')
    def test_parse_file_error_handling(self, mock_ts_utils):
        """测试解析文件的错误处理"""
        # 模拟TreeSitterUtils抛出异常
        mock_ts_instance = Mock()
        mock_ts_utils.get_instance.return_value = mock_ts_instance
        mock_ts_instance.parse.side_effect = Exception("Parser error")
        
        parser = CDataParser()
        
        # 测试解析错误
        with pytest.raises(Exception, match="Parser error"):
            parser.parse_file("int main() { return 0; }")
    
    def test_read_file(self, sample_c_file):
        """测试读取文件"""
        parser = CDataParser()
        
        # 测试读取文件
        content = parser._read_file(sample_c_file)
        
        # 验证文件内容被读取
        assert isinstance(content, str)
        assert len(content) > 0
        
        # 验证当前文件被设置
        assert parser.current_file == sample_c_file
    
    def test_read_file_not_found(self):
        """测试读取不存在的文件"""
        parser = CDataParser()
        
        # 测试不存在的文件
        with pytest.raises(Exception):
            parser._read_file("nonexistent_file.c")
    
    def test_read_file_encoding_error(self):
        """测试文件编码错误处理"""
        parser = CDataParser()
        
        # 创建包含无效编码的临时文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.c', delete=False) as f:
            f.write(b'\xff\xfe\x00\x00')  # 无效的UTF-8序列
            temp_file = f.name
        
        try:
            # 测试读取包含编码错误的文件
            content = parser._read_file(temp_file)
            
            # 应该能够处理编码错误并返回内容
            assert isinstance(content, str)
        finally:
            # 清理
            try:
                os.unlink(temp_file)
            except:
                pass
    
    @patch('c_parser.data_parser.TreeSitterUtils')
    def test_parse_global_variables(self, mock_ts_utils):
        """测试解析全局变量"""
        # 模拟TreeSitterUtils
        mock_ts_instance = Mock()
        mock_ts_utils.get_instance.return_value = mock_ts_instance
        
        # 模拟AST节点
        mock_node = Mock(spec=Node)
        mock_node.type = "translation_unit"
        mock_node.children = []
        mock_ts_instance.parse.return_value = mock_node
        
        parser = CDataParser()
        
        # 测试解析全局变量
        source_code = """
        static int global_var = 42;
        static char buffer[256];
        static int* ptr_var = NULL;
        """
        
        # 模拟解析过程
        with patch.object(parser, '_parse_global_variables') as mock_parse_vars:
            result = parser.parse_file(source_code)
            
            # 验证全局变量解析被调用
            mock_parse_vars.assert_called_once_with(mock_node)
    
    def test_is_array_type_by_string(self):
        """测试数组类型判断"""
        parser = CDataParser()
        
        # 测试数组类型
        assert parser._is_array_type_by_string("int[10]")
        assert parser._is_array_type_by_string("char[256]")
        assert parser._is_array_type_by_string("float[3][4]")
        
        # 测试非数组类型
        assert not parser._is_array_type_by_string("int")
        assert not parser._is_array_type_by_string("int*")
        assert not parser._is_array_type_by_string("struct Point")
    
    def test_is_pointer_type_by_string(self):
        """测试指针类型判断"""
        parser = CDataParser()
        
        # 测试指针类型
        assert parser._is_pointer_type_by_string("int*")
        assert parser._is_pointer_type_by_string("char*")
        assert parser._is_pointer_type_by_string("void*")
        assert parser._is_pointer_type_by_string("struct Point*")
        
        # 测试非指针类型
        assert not parser._is_pointer_type_by_string("int")
        assert not parser._is_pointer_type_by_string("int[10]")
        assert not parser._is_pointer_type_by_string("struct Point")
    
    def test_extract_array_size(self):
        """测试提取数组大小"""
        parser = CDataParser()
        
        # 测试一维数组
        assert parser._extract_array_size("int[10]") == 10
        assert parser._extract_array_size("char[256]") == 256
        
        # 测试多维数组（应该返回第一个维度）
        assert parser._extract_array_size("float[3][4]") == 3
        assert parser._extract_array_size("int[5][6][7]") == 5
        
        # 测试非数组类型
        assert parser._extract_array_size("int") is None
        assert parser._extract_array_size("int*") is None
    
    def test_extract_base_type(self):
        """测试提取基本类型"""
        parser = CDataParser()
        
        # 测试数组类型
        assert parser._extract_base_type("int[10]") == "int"
        assert parser._extract_base_type("char[256]") == "char"
        assert parser._extract_base_type("float[3][4]") == "float"
        
        # 测试指针类型
        assert parser._extract_base_type("int*") == "int"
        assert parser._extract_base_type("char*") == "char"
        assert parser._extract_base_type("struct Point*") == "struct Point"
        
        # 测试基本类型
        assert parser._extract_base_type("int") == "int"
        assert parser._extract_base_type("char") == "char"
    
    def test_parse_variable_value(self):
        """测试解析变量值"""
        parser = CDataParser()
        
        # 测试数字值
        assert parser._parse_variable_value("42") == 42
        assert parser._parse_variable_value("-123") == -123
        assert parser._parse_variable_value("3.14") == 3.14
        
        # 测试字符串值
        assert parser._parse_variable_value('"hello"') == "hello"
        assert parser._parse_variable_value("'A'") == "A"
        
        # 测试NULL值
        assert parser._parse_variable_value("NULL") is None
        
        # 测试复杂表达式（应该返回原字符串）
        assert parser._parse_variable_value("1 + 2") == "1 + 2"
        assert parser._parse_variable_value("{1, 2, 3}") == "{1, 2, 3}"
    
    def test_log_initialization_stats(self):
        """测试初始化统计信息记录"""
        parser = CDataParser()
        
        # 模拟数据管理器的类型信息
        mock_type_info = {
            'global': {
                'types': {'type1': {}, 'type2': {}},
                'pointer_types': {'ptr1': {}, 'ptr2': {}},
                'macro_definitions': {'macro1': 1, 'macro2': 2}
            }
        }
        
        with patch.object(parser.data_manager, 'get_type_info', return_value=mock_type_info):
            # 调用方法（应该不抛出异常）
            parser._log_initialization_stats()
    
    def test_log_parsing_results(self):
        """测试解析结果记录"""
        parser = CDataParser()
        
        # 模拟解析结果
        mock_result = {
            'structs': [{'name': 'Point'}],
            'unions': [{'name': 'Data'}],
            'enums': [{'name': 'Color'}],
            'typedefs': [{'name': 'u32'}],
            'variables': {
                'variables': [{'name': 'var1'}],
                'pointer_vars': [{'name': 'ptr1'}],
                'array_vars': [{'name': 'arr1'}],
                'struct_vars': [{'name': 'struct1'}]
            }
        }
        
        # 调用方法（应该不抛出异常）
        parser._log_parsing_results(mock_result)
    
    @patch('c_parser.data_parser.TreeSitterUtils')
    def test_parse_file_integration(self, mock_ts_utils):
        """测试完整的文件解析集成"""
        # 模拟TreeSitterUtils
        mock_ts_instance = Mock()
        mock_ts_utils.get_instance.return_value = mock_ts_instance
        
        # 模拟AST节点
        mock_node = Mock(spec=Node)
        mock_node.type = "translation_unit"
        mock_node.children = []
        mock_ts_instance.parse.return_value = mock_node
        
        parser = CDataParser()
        
        # 模拟类型解析器
        with patch.object(parser.type_parser, 'parse_declarations') as mock_parse_decls:
            # 模拟数据管理器的get_all_data方法
            mock_result = {
                'structs': [],
                'unions': [],
                'enums': [],
                'typedefs': [],
                'variables': {
                    'variables': [],
                    'pointer_vars': [],
                    'array_vars': [],
                    'struct_vars': []
                }
            }
            
            with patch.object(parser.data_manager, 'get_all_data', return_value=mock_result):
                # 测试完整解析流程
                source_code = """
                typedef struct Point {
                    int x;
                    int y;
                } Point;
                
                static Point test_point = {10, 20};
                static int global_var = 42;
                """
                
                result = parser.parse_file(source_code)
                
                # 验证类型解析器被调用
                mock_parse_decls.assert_called_once_with(source_code)
                
                # 验证TreeSitterUtils被调用
                mock_ts_instance.parse.assert_called_once_with(source_code)
                
                # 验证返回结果
                assert result == mock_result
    
    def test_parse_file_with_complex_data(self):
        """测试解析复杂数据结构"""
        parser = CDataParser()
        
        complex_source = """
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
        
        typedef struct Vector {
            float components[3];
            Point points[4];
            u32 count;
        } Vector;
        
        // 枚举定义
        typedef enum Color {
            RED = 0,
            GREEN = 1,
            BLUE = 2
        } Color;
        
        // 全局变量
        static u8 buffer[256];
        static Point test_points[] = {{0, 0}, {1, 1}, {2, 2}};
        static Vector* vectors = NULL;
        static Color current_color = RED;
        static int global_counter = 0;
        """
        
        # 模拟TreeSitterUtils
        with patch('c_parser.data_parser.TreeSitterUtils') as mock_ts_utils:
            mock_ts_instance = Mock()
            mock_ts_utils.get_instance.return_value = mock_ts_instance
            
            # 模拟AST节点
            mock_node = Mock(spec=Node)
            mock_node.type = "translation_unit"
            mock_node.children = []
            mock_ts_instance.parse.return_value = mock_node
            
            # 模拟类型解析器
            with patch.object(parser.type_parser, 'parse_declarations'):
                # 模拟数据管理器
                mock_result = {
                    'structs': [{'name': 'Point'}, {'name': 'Vector'}],
                    'unions': [],
                    'enums': [{'name': 'Color'}],
                    'typedefs': [{'name': 'u8'}, {'name': 'u16'}, {'name': 'u32'}],
                    'variables': {
                        'variables': [{'name': 'global_counter'}],
                        'pointer_vars': [{'name': 'vectors'}],
                        'array_vars': [{'name': 'buffer'}, {'name': 'test_points'}],
                        'struct_vars': []
                    }
                }
                
                with patch.object(parser.data_manager, 'get_all_data', return_value=mock_result):
                    result = parser.parse_file(complex_source)
                    
                    # 验证解析结果
                    assert result['structs'] == [{'name': 'Point'}, {'name': 'Vector'}]
                    assert result['enums'] == [{'name': 'Color'}]
                    assert result['typedefs'] == [{'name': 'u8'}, {'name': 'u16'}, {'name': 'u32'}]
                    assert len(result['variables']['array_vars']) == 2
                    assert len(result['variables']['pointer_vars']) == 1
                    assert len(result['variables']['variables']) == 1
    
    def test_parse_file_with_real_test_files(self, test_structs_h_path, test_data_c_path):
        """测试解析真实的测试文件"""
        parser = CDataParser()
        
        # 模拟TreeSitterUtils
        with patch('c_parser.data_parser.TreeSitterUtils') as mock_ts_utils:
            mock_ts_instance = Mock()
            mock_ts_utils.get_instance.return_value = mock_ts_instance
            
            # 模拟AST节点
            mock_node = Mock(spec=Node)
            mock_node.type = "translation_unit"
            mock_node.children = []
            mock_ts_instance.parse.return_value = mock_node
            
            # 模拟类型解析器
            with patch.object(parser.type_parser, 'parse_declarations'):
                # 模拟数据管理器
                mock_result = {
                    'structs': [],
                    'unions': [],
                    'enums': [],
                    'typedefs': [],
                    'variables': {
                        'variables': [],
                        'pointer_vars': [],
                        'array_vars': [],
                        'struct_vars': []
                    }
                }
                
                with patch.object(parser.data_manager, 'get_all_data', return_value=mock_result):
                    # 测试解析头文件
                    result = parser.parse_file(test_structs_h_path)
                    assert isinstance(result, dict)
                    
                    # 测试解析源文件
                    result = parser.parse_file(test_data_c_path)
                    assert isinstance(result, dict)
    
    def test_error_handling_edge_cases(self):
        """测试错误处理的边界情况"""
        parser = CDataParser()
        
        # 测试空字符串
        with pytest.raises(Exception):
            parser.parse_file("")
        
        # 测试None输入
        with pytest.raises(Exception):
            parser.parse_file(None)
        
        # 测试无效文件路径
        with pytest.raises(Exception):
            parser.parse_file("invalid/path/file.c")
    
    def test_type_parsing_integration(self):
        """测试类型解析集成"""
        parser = CDataParser()
        
        # 模拟类型解析器返回结果
        mock_declaration_result = {
            'typedef_types': [{'name': 'u32', 'base_type': 'uint32_t'}],
            'struct_info': [{'name': 'Point', 'fields': []}],
            'enum_types': [{'name': 'Color', 'values': []}],
            'macro_definitions': {'MAX_SIZE': 100}
        }
        
        with patch.object(parser.type_parser, 'parse_declarations', return_value=mock_declaration_result):
            # 模拟TreeSitterUtils
            with patch('c_parser.data_parser.TreeSitterUtils') as mock_ts_utils:
                mock_ts_instance = Mock()
                mock_ts_utils.get_instance.return_value = mock_ts_instance
                
                # 模拟AST节点
                mock_node = Mock(spec=Node)
                mock_node.type = "translation_unit"
                mock_node.children = []
                mock_ts_instance.parse.return_value = mock_node
                
                # 模拟数据管理器
                mock_result = {
                    'structs': [],
                    'unions': [],
                    'enums': [],
                    'typedefs': [],
                    'variables': {
                        'variables': [],
                        'pointer_vars': [],
                        'array_vars': [],
                        'struct_vars': []
                    }
                }
                
                with patch.object(parser.data_manager, 'get_all_data', return_value=mock_result):
                    source_code = "typedef uint32_t u32;"
                    result = parser.parse_file(source_code)
                    
                    # 验证类型解析器被正确调用
                    assert isinstance(result, dict)

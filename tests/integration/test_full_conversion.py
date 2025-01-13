import pytest
from c_parser.core.type_manager import TypeManager
from c_parser.core.tree_sitter_base import TreeSitterParser
from struct_converter.generators.c_generator import CGenerator

class TestFullConversion:
    """完整转换流程测试"""
    
    @pytest.fixture
    def setup_conversion(self):
        """设置转换环境"""
        type_manager = TypeManager()
        parser = TreeSitterParser()
        generator = CGenerator(type_manager)
        return type_manager, parser, generator
        
    def test_basic_struct_conversion(self, setup_conversion, tmp_path):
        """测试基本结构体转换"""
        type_manager, parser, generator = setup_conversion
        
        # 准备输入文件
        input_code = """
        struct Point {
            int x;
            int y;
        };
        """
        input_file = tmp_path / "test.h"
        input_file.write_text(input_code)
        
        # 解析和转换
        parser.parse_file(str(input_file))
        output = generator.generate_code()
        
        # 验证输出
        assert 'struct Point' in output
        assert 'x: int' in output
        assert 'y: int' in output 
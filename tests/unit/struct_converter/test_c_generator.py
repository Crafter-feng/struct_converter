import pytest
from struct_converter.generators.c_generator import CGenerator
from c_parser.core.type_manager import TypeManager

class TestCGenerator:
    """CGenerator单元测试"""
    
    @pytest.fixture
    def generator(self):
        """创建C代码生成器实例"""
        type_manager = TypeManager()
        return CGenerator(type_manager)
        
    def test_struct_generation(self, generator):
        """测试结构体代码生成"""
        # 注册测试结构体
        generator.type_manager.register_struct('Point', [
            {'name': 'x', 'type': {'base_type': 'int'}},
            {'name': 'y', 'type': {'base_type': 'int'}}
        ])
        
        # 生成代码
        code = generator.generate_code()
        
        # 验证生成的代码
        assert 'struct Point' in code
        assert 'int x;' in code
        assert 'int y;' in code 

    def test_complex_struct_generation(self, generator):
        """测试复杂结构体生成"""
        # 注册嵌套结构体
        generator.type_manager.register_struct('Point', [
            {'name': 'x', 'type': {'base_type': 'int'}},
            {'name': 'y', 'type': {'base_type': 'int'}}
        ])
        
        generator.type_manager.register_struct('Rectangle', [
            {'name': 'top_left', 'type': {'base_type': 'Point'}},
            {'name': 'bottom_right', 'type': {'base_type': 'Point'}}
        ])
        
        code = generator.generate_code()
        
        # 验证生成的代码
        assert 'struct Point' in code
        assert 'struct Rectangle' in code
        assert 'Point top_left;' in code
        assert 'Point bottom_right;' in code 
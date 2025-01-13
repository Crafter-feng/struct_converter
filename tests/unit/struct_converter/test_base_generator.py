import pytest
from struct_converter.generators.base_generator import BaseGenerator
from c_parser.core.type_manager import TypeManager

class TestBaseGenerator:
    """BaseGenerator单元测试"""
    
    @pytest.fixture
    def generator(self):
        """创建生成器实例"""
        type_manager = TypeManager()
        return BaseGenerator(type_manager)
        
    def test_basic_generation(self, generator):
        """测试基本代码生成"""
        # 注册测试结构体
        generator.type_manager.register_struct('Point', [
            {'name': 'x', 'type': {'base_type': 'int'}},
            {'name': 'y', 'type': {'base_type': 'int'}}
        ])
        
        # 生成代码
        code = generator.generate_code()
        
        # 验证基本结构
        assert code is not None
        assert isinstance(code, str) 
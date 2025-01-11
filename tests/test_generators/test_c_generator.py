import pytest
from pathlib import Path
from struct_converter.generators.c_generator import CGenerator
from struct_converter.core.config import GeneratorConfig
from struct_converter.core.exceptions import CodeGenerationError

@pytest.fixture
def generator():
    return CGenerator(GeneratorConfig())

@pytest.fixture
def sample_parse_result():
    return {
        'module_name': 'test_module',
        'structs': {
            'Point': {
                'fields': [
                    {'name': 'x', 'type': 'int32_t'},
                    {'name': 'y', 'type': 'int32_t'}
                ],
                'metadata': {'is_packed': False}
            }
        },
        'enums': {
            'Color': {
                'values': [
                    {'name': 'RED', 'value': 0},
                    {'name': 'GREEN', 'value': 1},
                    {'name': 'BLUE', 'value': 2}
                ]
            }
        },
        'unions': {},
        'typedefs': {},
        'macros': {}
    }

def test_generate_basic(generator, sample_parse_result):
    """测试基本代码生成"""
    result = generator.generate(sample_parse_result)
    
    assert 'header' in result
    assert 'source' in result
    
    header = result['header']
    source = result['source']
    
    # 检查头文件
    assert '#ifndef __TEST_MODULE_H__' in header
    assert 'typedef enum' in header
    assert 'typedef struct' in header
    assert 'Point_serialize' in header
    assert 'Point_deserialize' in header
    
    # 检查源文件
    assert '#include "test_module.h"' in source
    assert 'Point_serialize' in source
    assert 'Point_deserialize' in source

def test_generate_with_bitfields(generator):
    """测试位域代码生成"""
    parse_result = {
        'module_name': 'test_module',
        'structs': {
            'Flags': {
                'fields': [
                    {'name': 'flag1', 'type': 'uint8_t', 'bit_width': 1},
                    {'name': 'flag2', 'type': 'uint8_t', 'bit_width': 2},
                    {'name': 'flag3', 'type': 'uint8_t', 'bit_width': 5}
                ],
                'metadata': {'is_packed': True}
            }
        },
        'enums': {},
        'unions': {},
        'typedefs': {},
        'macros': {}
    }
    
    result = generator.generate(parse_result)
    
    # 检查位域处理
    assert 'uint8_t flag1 : 1;' in result['header']
    assert 'uint8_t flag2 : 2;' in result['header']
    assert 'uint8_t flag3 : 5;' in result['header']

def test_generate_with_arrays(generator):
    """测试数组代码生成"""
    parse_result = {
        'module_name': 'test_module',
        'structs': {
            'Matrix': {
                'fields': [
                    {'name': 'data', 'type': 'int32_t', 'array_size': [2, 3]},
                    {'name': 'size', 'type': 'size_t'}
                ],
                'metadata': {'is_packed': False}
            }
        },
        'enums': {},
        'unions': {},
        'typedefs': {},
        'macros': {}
    }
    
    result = generator.generate(parse_result)
    
    # 检查数组声明
    assert 'int32_t data[2][3];' in result['header']

def test_generate_invalid_input(generator):
    """测试无效输入"""
    with pytest.raises(CodeGenerationError):
        generator.generate({})
        
    with pytest.raises(CodeGenerationError):
        generator.generate({'module_name': 'test'})  # 缺少必要字段

def test_format_code(generator):
    """测试代码格式化"""
    unformatted_code = 'void  test  (  )  {  return  ;  }'
    formatted = generator._format_code(unformatted_code, 'c')
    
    # 检查基本格式化
    assert 'void test() {' in formatted
    assert 'return;' in formatted

def test_version_control(generator):
    """测试版本控制"""
    parse_result = {
        'module_name': 'test_module',
        'structs': {
            'Data': {
                'fields': [{'name': 'value', 'type': 'int32_t'}],
                'metadata': {
                    'is_packed': False,
                    'version': '1.2.3'
                }
            }
        },
        'enums': {},
        'unions': {},
        'typedefs': {},
        'macros': {}
    }
    
    result = generator.generate(parse_result)
    
    # 检查版本信息
    assert '"1.2.3"' in result['source']
    assert 'check_version' in result['source'] 
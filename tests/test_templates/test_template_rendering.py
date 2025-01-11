import pytest
from pathlib import Path
from jinja2 import Environment, PackageLoader, select_autoescape
from struct_converter.core.type_converter import TypeConverter
from struct_converter.core.config import GeneratorConfig

@pytest.fixture
def env():
    """创建Jinja2环境"""
    env = Environment(
        loader=PackageLoader('struct_converter', 'templates'),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True
    )
    env.filters['to_c_type'] = TypeConverter.c_to_ctypes_type
    env.filters['array_dims'] = lambda dims: ''.join(f'[{dim}]' for dim in dims or [])
    return env

@pytest.fixture
def sample_struct_data():
    """示例结构体数据"""
    return {
        'module_name': 'test_module',
        'structs': {
            'Point': {
                'fields': [
                    {
                        'name': 'x',
                        'type': 'int32_t',
                        'doc_comment': 'X coordinate'
                    },
                    {
                        'name': 'y',
                        'type': 'int32_t',
                        'doc_comment': 'Y coordinate'
                    }
                ],
                'metadata': {
                    'is_packed': False,
                    'version': '1.0.0'
                },
                'doc_comment': {
                    'text': 'A 2D point structure'
                }
            }
        },
        'enums': {
            'Color': {
                'values': [
                    {'name': 'RED', 'value': 0, 'doc_comment': 'Red color'},
                    {'name': 'GREEN', 'value': 1, 'doc_comment': 'Green color'},
                    {'name': 'BLUE', 'value': 2, 'doc_comment': 'Blue color'}
                ],
                'doc_comment': {
                    'text': 'Basic colors'
                }
            }
        },
        'unions': {},
        'typedefs': {},
        'macros': {}
    }

def test_c_header_template(env, sample_struct_data):
    """测试C头文件模板渲染"""
    template = env.get_template('c/header.h.jinja')
    result = template.render(**sample_struct_data)
    
    # 检查基本结构
    assert '#ifndef __TEST_MODULE_H__' in result
    assert '#define __TEST_MODULE_H__' in result
    assert '#include <stdint.h>' in result
    
    # 检查枚举定义
    assert 'typedef enum' in result
    assert 'RED = 0' in result
    assert 'GREEN = 1' in result
    assert 'BLUE = 2' in result
    assert '} Color;' in result
    
    # 检查结构体定义
    assert 'typedef struct' in result
    assert 'int32_t x;' in result
    assert 'int32_t y;' in result
    assert '} Point;' in result
    
    # 检查文档注释
    assert '* A 2D point structure' in result
    assert '* X coordinate' in result
    assert '* Basic colors' in result

def test_c_source_template(env, sample_struct_data):
    """测试C源文件模板渲染"""
    template = env.get_template('c/source.c.jinja')
    result = template.render(**sample_struct_data)
    
    # 检查基本结构
    assert '#include "test_module.h"' in result
    assert '#include <string.h>' in result
    
    # 检查序列化函数
    assert 'Point_serialize' in result
    assert 'Point_deserialize' in result
    
    # 检查版本控制
    assert 'write_version' in result
    assert 'check_version' in result
    assert '"1.0.0"' in result

def test_template_with_arrays(env):
    """测试数组字段的模板渲染"""
    data = {
        'module_name': 'test_module',
        'structs': {
            'Matrix': {
                'fields': [
                    {
                        'name': 'data',
                        'type': 'int32_t',
                        'array_size': [2, 3],
                        'doc_comment': '2x3 matrix'
                    }
                ],
                'metadata': {'is_packed': False}
            }
        },
        'enums': {},
        'unions': {},
        'typedefs': {},
        'macros': {}
    }
    
    template = env.get_template('c/header.h.jinja')
    result = template.render(**data)
    
    assert 'int32_t data[2][3];' in result

def test_template_with_bitfields(env):
    """测试位域的模板渲染"""
    data = {
        'module_name': 'test_module',
        'structs': {
            'Flags': {
                'fields': [
                    {
                        'name': 'flag1',
                        'type': 'uint8_t',
                        'bit_width': 1,
                        'doc_comment': 'First flag'
                    },
                    {
                        'name': 'flag2',
                        'type': 'uint8_t',
                        'bit_width': 2,
                        'doc_comment': 'Second flag'
                    }
                ],
                'metadata': {'is_packed': True}
            }
        },
        'enums': {},
        'unions': {},
        'typedefs': {},
        'macros': {}
    }
    
    template = env.get_template('c/header.h.jinja')
    result = template.render(**data)
    
    assert 'uint8_t flag1 : 1;' in result
    assert 'uint8_t flag2 : 2;' in result
    assert '#pragma pack(push, 1)' in result

def test_template_error_handling(env):
    """测试模板错误处理"""
    # 缺少必要字段
    with pytest.raises(Exception):
        template = env.get_template('c/header.h.jinja')
        template.render(module_name='test')
    
    # 无效的模板变量
    with pytest.raises(Exception):
        template = env.get_template('c/header.h.jinja')
        template.render(invalid_key='value') 
import pytest
from pathlib import Path
import tempfile
from config import GeneratorConfig
from struct_converter.generators import CGenerator
from c_parser.core.tree_sitter_base import CTreeSitterParser
from c_parser.core.type_manager import TypeManager
from struct_converter.core.exceptions import (
    ParserError as ParseError,
    GenerationError as CodeGenerationError
)

@pytest.fixture
def edge_case_headers():
    """边界情况的头文件集合"""
    return {
        'empty_struct': """
        typedef struct {
        } EmptyStruct;
        """,
        
        'nested_structs': """
        typedef struct {
            int x;
        } Inner;
        
        typedef struct {
            Inner inner1;
            struct {
                int y;
            } inner2;
            union {
                int z;
                float w;
            } inner3;
        } NestedStruct;
        """,
        
        'recursive_struct': """
        typedef struct Node {
            int value;
            struct Node* next;
        } Node;
        """,
        
        'complex_bitfields': """
        typedef struct {
            unsigned int a : 3;
            unsigned int   : 2;  // unnamed
            unsigned int b : 1;
            unsigned int   : 0;  // zero width
            unsigned int c : 4;
        } ComplexBitfields;
        """,
        
        'mixed_declarations': """
        #define ARRAY_SIZE 10
        
        typedef enum { A, B, C } ABC;
        
        struct Forward;  // forward declaration
        
        typedef struct {
            ABC enum_field;
            struct Forward* ptr_field;
            int array_field[ARRAY_SIZE];
        } MixedStruct;
        """
    }

def test_empty_struct(edge_case_headers, temp_workspace):
    """测试空结构体"""
    input_file = temp_workspace / "empty.h"
    input_file.write_text(edge_case_headers['empty_struct'])
    
    parser = CTreeSitterParser()
    result = parser.parse_file(str(input_file))
    
    # 检查解析结果
    assert 'EmptyStruct' in result['structs']
    assert len(result['structs']['EmptyStruct']['fields']) == 0
    
    # 生成代码
    generator = CGenerator(GeneratorConfig())
    generated = generator.generate({
        'module_name': 'test',
        **result
    })
    
    # 检查生成的代码
    assert 'typedef struct {' in generated['header']
    assert '} EmptyStruct;' in generated['header']
    assert 'EmptyStruct_serialize' in generated['source']

def test_nested_structures(edge_case_headers, temp_workspace):
    """测试嵌套结构体"""
    input_file = temp_workspace / "nested.h"
    input_file.write_text(edge_case_headers['nested_structs'])
    
    parser = CTreeSitterParser()
    result = parser.parse_file(str(input_file))
    
    # 检查解析结果
    assert 'Inner' in result['structs']
    assert 'NestedStruct' in result['structs']
    
    nested = result['structs']['NestedStruct']
    assert any(f['name'] == 'inner1' for f in nested['fields'])
    assert any(f['name'] == 'inner2' for f in nested['fields'])
    assert any(f['name'] == 'inner3' for f in nested['fields'])

def test_recursive_structure(edge_case_headers, temp_workspace):
    """测试递归结构体"""
    input_file = temp_workspace / "recursive.h"
    input_file.write_text(edge_case_headers['recursive_struct'])
    
    parser = CTreeSitterParser()
    result = parser.parse_file(str(input_file))
    
    # 检查解析结果
    node_struct = result['structs']['Node']
    next_field = next(f for f in node_struct['fields'] if f['name'] == 'next')
    assert next_field['pointer_level'] == 1
    assert 'Node' in next_field['type']

def test_complex_bitfields(edge_case_headers, temp_workspace):
    """测试复杂位域"""
    input_file = temp_workspace / "bitfields.h"
    input_file.write_text(edge_case_headers['complex_bitfields'])
    
    parser = CTreeSitterParser()
    result = parser.parse_file(str(input_file))
    
    struct_info = result['structs']['ComplexBitfields']
    fields = struct_info['fields']
    
    # 检查位域
    assert len(fields) >= 3  # 至少有a,b,c三个命名字段
    assert any(f['name'] == 'a' and f['bit_width'] == 3 for f in fields)
    assert any(f['name'] == 'b' and f['bit_width'] == 1 for f in fields)
    assert any(f['name'] == 'c' and f['bit_width'] == 4 for f in fields)

def test_mixed_declarations(edge_case_headers, temp_workspace):
    """测试混合声明"""
    input_file = temp_workspace / "mixed.h"
    input_file.write_text(edge_case_headers['mixed_declarations'])
    
    parser = CTreeSitterParser()
    result = parser.parse_file(str(input_file))
    
    # 检查宏定义
    assert 'ARRAY_SIZE' in result['macros']
    assert result['macros']['ARRAY_SIZE'] == '10'
    
    # 检查枚举
    assert 'ABC' in result['enums']
    enum_values = result['enums']['ABC']['values']
    assert [v['name'] for v in enum_values] == ['A', 'B', 'C']
    
    # 检查结构体字段
    struct_info = result['structs']['MixedStruct']
    fields = {f['name']: f for f in struct_info['fields']}
    
    assert 'enum_field' in fields
    assert 'ptr_field' in fields
    assert 'array_field' in fields
    assert fields['array_field']['array_size'] == [10]

def test_error_cases():
    """测试错误情况"""
    config = GeneratorConfig()
    generator = CGenerator(config)
    
    # 测试无效的结构体定义
    with pytest.raises(CodeGenerationError):
        generator.generate({
            'module_name': 'test',
            'structs': {
                'Invalid': {
                    'fields': [
                        {'name': 'field'}  # 缺少类型
                    ]
                }
            }
        })
    
    # 测试无效的位域
    with pytest.raises(CodeGenerationError):
        generator.generate({
            'module_name': 'test',
            'structs': {
                'Invalid': {
                    'fields': [
                        {
                            'name': 'field',
                            'type': 'int',
                            'bit_width': 33  # 超过整型大小
                        }
                    ]
                }
            }
        }) 

def test_complex_type_handling():
    """测试复杂类型处理"""
    type_manager = TypeManager()
    
    # 注册复杂类型
    type_manager.register_type('ComplexStruct', {
        'kind': 'struct',
        'name': 'ComplexStruct',
        'fields': [
            {
                'name': 'func_ptr',
                'type': 'void(*)(int, char*)',
                'attributes': {'deprecated': True}
            },
            {
                'name': 'bit_field',
                'type': 'int',
                'bit_width': 3
            },
            {
                'name': 'flexible_array',
                'type': 'char[]'
            }
        ],
        'details': {
            'packed': True,
            'attributes': {'aligned': 8}
        }
    })
    
    # 验证类型信息
    type_info = type_manager.get_type('ComplexStruct')
    assert type_info is not None
    
    # 验证函数指针字段
    field_info = type_manager.get_field_info('ComplexStruct', 'func_ptr')
    assert field_info is not None
    assert type_manager.is_function_pointer(field_info['type'])
    
    # 验证位域字段
    field_info = type_manager.get_field_info('ComplexStruct', 'bit_field')
    assert field_info['is_bitfield']
    assert field_info['bit_width'] == 3 
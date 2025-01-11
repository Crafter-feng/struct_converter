import pytest
from pathlib import Path
import tempfile
from struct_converter.core.config import GeneratorConfig
from struct_converter.generators.c_generator import CGenerator
from c_parser.tree_sitter_parser import CTreeSitterParser

@pytest.fixture
def complex_types_header():
    """包含复杂类型的头文件"""
    return """
    typedef struct {
        // 位域测试
        unsigned int flag1 : 1;
        unsigned int flag2 : 2;
        unsigned int : 0;  // 填充到下一个单元
        unsigned int flag3 : 3;
        
        // 数组测试
        int matrix[2][3][4];
        char string[64];
        
        // 指针测试
        void* ptr1;
        void** ptr2;
        int (*func_ptr)(int, int);
        
        // 联合体测试
        union {
            int i;
            float f;
            char bytes[4];
        } data;
        
        // 对齐测试
        char c;
        int i;
        char d;
    } __attribute__((packed)) ComplexTypes;
    """

def test_complex_type_parsing(complex_types_header, temp_workspace):
    """测试复杂类型的解析"""
    input_file = temp_workspace / "complex_types.h"
    input_file.write_text(complex_types_header)
    
    parser = CTreeSitterParser()
    result = parser.parse_file(str(input_file))
    
    struct_info = result['structs']['ComplexTypes']
    
    # 检查位域
    assert any(field.get('bit_width') == 1 for field in struct_info['fields'])
    assert any(field.get('bit_width') == 2 for field in struct_info['fields'])
    assert any(field.get('bit_width') == 3 for field in struct_info['fields'])
    
    # 检查数组
    matrix_field = next(f for f in struct_info['fields'] if f['name'] == 'matrix')
    assert matrix_field['array_size'] == [2, 3, 4]
    
    # 检查指针
    ptr_field = next(f for f in struct_info['fields'] if f['name'] == 'ptr2')
    assert ptr_field['pointer_level'] == 2
    
    # 检查联合体
    assert 'data' in {f['name'] for f in struct_info['fields']}

def test_alignment_and_packing():
    """测试对齐和打包"""
    config = GeneratorConfig(default_alignment=4)
    generator = CGenerator(config)
    
    # 测试不同对齐方式的结构体
    test_cases = [
        {
            'fields': [
                {'name': 'c', 'type': 'char'},
                {'name': 'i', 'type': 'int32_t'},
                {'name': 'd', 'type': 'char'}
            ],
            'metadata': {'is_packed': False}
        },
        {
            'fields': [
                {'name': 'c', 'type': 'char'},
                {'name': 'i', 'type': 'int32_t'},
                {'name': 'd', 'type': 'char'}
            ],
            'metadata': {'is_packed': True}
        }
    ]
    
    for struct_info in test_cases:
        # 计算字段偏移
        offsets = []
        for field in struct_info['fields']:
            offset = generator._get_field_offset(field, struct_info)
            offsets.append(offset)
        
        if struct_info['metadata']['is_packed']:
            # 紧凑模式下应该没有填充
            assert offsets == [0, 1, 5]
        else:
            # 对齐模式下应该有填充
            assert offsets == [0, 4, 8]

def test_serialization_with_endianness():
    """测试不同字节序的序列化"""
    config = GeneratorConfig(byte_order='little')
    generator = CGenerator(config)
    
    # 生成序列化代码
    parse_result = {
        'module_name': 'test',
        'structs': {
            'TestStruct': {
                'fields': [
                    {'name': 'i16', 'type': 'int16_t'},
                    {'name': 'i32', 'type': 'int32_t'},
                    {'name': 'f32', 'type': 'float'}
                ],
                'metadata': {'is_packed': False}
            }
        }
    }
    
    generated = generator.generate(parse_result)
    
    # 检查字节序转换代码
    assert 'SWAP16' in generated['source']
    assert 'SWAP32' in generated['source']
    assert 'swap_float' in generated['source']

def test_pointer_handling():
    """测试指针处理"""
    config = GeneratorConfig(pointer_size=8)
    generator = CGenerator(config)
    
    parse_result = {
        'module_name': 'test',
        'structs': {
            'PointerStruct': {
                'fields': [
                    {'name': 'ptr', 'type': 'void*', 'pointer_level': 1},
                    {'name': 'ptr_ptr', 'type': 'void*', 'pointer_level': 2}
                ],
                'metadata': {'is_packed': False}
            }
        }
    }
    
    generated = generator.generate(parse_result)
    
    # 检查指针序列化代码
    assert 'uint64_t ptr_value' in generated['source']
    assert 'void*' in generated['header'] 
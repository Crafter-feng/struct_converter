import pytest
from pathlib import Path
import tempfile
import json
from struct_converter.core.config import GeneratorConfig
from struct_converter.generators.c_generator import CGenerator
from c_parser.tree_sitter_parser import CTreeSitterParser
from utils.code_formatter import CodeFormatter

@pytest.fixture
def complex_c_header():
    """创建一个复杂的C头文件"""
    return """
    /**
     * @brief Complex data structures
     */
    #include <stdint.h>
    
    #define MAX_SIZE 100
    #define VERSION "1.0.0"
    
    typedef enum {
        SUCCESS = 0,
        ERROR_INVALID_PARAM = -1,
        ERROR_OUT_OF_MEMORY = -2
    } ErrorCode;
    
    typedef struct {
        uint8_t r;
        uint8_t g;
        uint8_t b;
        uint8_t a;
    } __attribute__((packed)) Color;
    
    typedef struct {
        uint32_t flags : 4;
        uint32_t mode : 2;
        uint32_t reserved : 26;
    } BitFlags;
    
    typedef union {
        uint32_t value;
        float f_value;
        struct {
            uint16_t low;
            uint16_t high;
        } parts;
    } DataValue;
    
    typedef struct {
        char name[32];
        int32_t data[MAX_SIZE];
        size_t data_size;
        Color color;
        BitFlags flags;
        DataValue value;
        void* extra_data;
    } ComplexStruct;
    """

@pytest.fixture
def temp_workspace():
    """创建临时工作目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

def test_full_conversion_flow(complex_c_header, temp_workspace):
    """测试完整的转换流程"""
    # 准备输入文件
    input_file = temp_workspace / "input.h"
    input_file.write_text(complex_c_header)
    
    # 创建配置
    config = GeneratorConfig(
        output_dir=str(temp_workspace / "output"),
        enable_serialization=True,
        enable_version_control=True,
        byte_order='little'
    )
    
    # 解析C代码
    parser = CTreeSitterParser()
    parse_result = parser.parse_file(str(input_file))
    
    # 生成C代码
    generator = CGenerator(config)
    generated_files = generator.generate({
        'module_name': 'complex',
        **parse_result
    })
    
    # 检查生成的文件
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    header_file = output_dir / "complex.h"
    source_file = output_dir / "complex.c"
    
    with open(header_file, 'w') as f:
        f.write(generated_files['header'])
    with open(source_file, 'w') as f:
        f.write(generated_files['source'])
        
    # 验证生成的代码
    assert header_file.exists()
    assert source_file.exists()
    
    header_content = header_file.read_text()
    source_content = source_file.read_text()
    
    # 检查头文件内容
    assert '#define MAX_SIZE 100' in header_content
    assert 'typedef enum' in header_content
    assert 'typedef struct' in header_content
    assert 'typedef union' in header_content
    assert '__attribute__((packed))' in header_content
    assert 'uint32_t flags : 4' in header_content
    
    # 检查源文件内容
    assert '#include "complex.h"' in source_content
    assert 'ComplexStruct_serialize' in source_content
    assert 'ComplexStruct_deserialize' in source_content
    
    # 检查序列化函数的正确性
    assert 'memcpy' in source_content
    assert 'write_version' in source_content
    assert 'check_version' in source_content

def test_error_handling(temp_workspace):
    """测试错误处理"""
    # 测试无效的C代码
    invalid_c_code = """
    struct Invalid {
        int missing_semicolon
    }
    """
    
    input_file = temp_workspace / "invalid.h"
    input_file.write_text(invalid_c_code)
    
    parser = CTreeSitterParser()
    with pytest.raises(Exception):
        parser.parse_file(str(input_file))
        
    # 测试无效的配置
    with pytest.raises(Exception):
        GeneratorConfig(byte_order='invalid')
        
    # 测试无效的输出目录
    with pytest.raises(Exception):
        config = GeneratorConfig(output_dir='/nonexistent/directory')
        generator = CGenerator(config)
        generator.generate({'module_name': 'test'})

def test_format_generated_code(complex_c_header, temp_workspace):
    """测试代码格式化"""
    # 准备输入文件
    input_file = temp_workspace / "input.h"
    input_file.write_text(complex_c_header)
    
    # 解析和生成
    parser = CTreeSitterParser()
    parse_result = parser.parse_file(str(input_file))
    
    generator = CGenerator(GeneratorConfig())
    generated_files = generator.generate({
        'module_name': 'complex',
        **parse_result
    })
    
    # 格式化代码
    formatter = CodeFormatter()
    formatted_header = formatter.format_c(generated_files['header'])
    formatted_source = formatter.format_c(generated_files['source'])
    
    # 检查格式化结果
    assert formatted_header != generated_files['header']  # 应该有格式变化
    assert formatted_source != generated_files['source']  # 应该有格式变化
    
    # 检查基本格式规则
    assert not any(line.rstrip().endswith('  ') for line in formatted_header.splitlines())
    assert not any(line.rstrip().endswith('  ') for line in formatted_source.splitlines())

def test_version_compatibility(complex_c_header, temp_workspace):
    """测试版本兼容性"""
    # 生成两个不同版本的代码
    versions = ['1.0.0', '2.0.0']
    generated_codes = {}
    
    for version in versions:
        config = GeneratorConfig()
        generator = CGenerator(config)
        
        parse_result = {
            'module_name': 'test',
            'structs': {
                'TestStruct': {
                    'fields': [{'name': 'value', 'type': 'int32_t'}],
                    'metadata': {'version': version}
                }
            },
            'enums': {},
            'unions': {},
            'typedefs': {},
            'macros': {}
        }
        
        generated_codes[version] = generator.generate(parse_result)
    
    # 检查版本信息
    for version, code in generated_codes.items():
        assert version in code['source']
        assert 'check_version' in code['source'] 
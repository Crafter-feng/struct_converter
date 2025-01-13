import pytest
from pathlib import Path
import tempfile
from config import GeneratorConfig, EncryptionConfig
from struct_converter.generators.c_generator import CGenerator
from struct_converter.generators.python_generator import PythonGenerator
from c_parser.core.tree_sitter_base import CTreeSitterParser

TEST_HEADER = """
// 基本类型测试
typedef struct {
    int8_t i8;
    uint8_t u8;
    int16_t i16;
    uint16_t u16;
    int32_t i32;
    uint32_t u32;
    int64_t i64;
    uint64_t u64;
    float f32;
    double f64;
    bool flag;
    char str[32];
} BasicTypes;

// 嵌套结构体测试
typedef struct {
    int x;
    int y;
} Point;

typedef struct {
    Point top_left;
    Point bottom_right;
    float area;
} Rectangle;

// 数组测试
typedef struct {
    int numbers[10];
    Point points[5];
    char strings[3][64];
} ArrayTypes;
"""

@pytest.fixture
def parser():
    return CTreeSitterParser()

@pytest.fixture
def generator_config():
    config = GeneratorConfig()
    config.output_dir = "test_output"
    config.enable_field_encryption = True
    config.field_encryption_salt = "test_salt"
    return config

def test_c_generator(parser, config, tmp_path):
    """测试C代码生成器"""
    # 准备测试文件
    input_file = tmp_path / "test.h"
    input_file.write_text(TEST_HEADER)
    
    # 解析代码
    parse_result = parser.parse_file(str(input_file))
    
    # 生成C代码
    generator = CGenerator(config)
    generated = generator.generate({
        'module_name': 'test',
        **parse_result
    })
    
    # 验证生成的文件
    assert "h" in generated
    assert "c" in generated
    
    header = generated["h"]
    source = generated["c"]
    
    # 验证基本类型
    assert "typedef struct" in header
    assert "BasicTypes" in header
    assert "int8_t i8" in header
    assert "uint64_t u64" in header
    assert "char str[32]" in header
    
    # 验证嵌套结构体
    assert "Point" in header
    assert "Rectangle" in header
    assert "Point top_left" in header
    
    # 验证数组
    assert "ArrayTypes" in header
    assert "int numbers[10]" in header
    assert "Point points[5]" in header
    
    # 验证序列化函数
    assert "test_serialize" in source
    assert "test_deserialize" in source
    assert "SWAP16" in source
    assert "SWAP32" in source
    assert "SWAP64" in source

def test_python_generator(parser, config, tmp_path):
    """测试Python代码生成器"""
    input_file = tmp_path / "test.h"
    input_file.write_text(TEST_HEADER)
    
    parse_result = parser.parse_file(str(input_file))
    
    generator = PythonGenerator(config)
    generated = generator.generate({
        'module_name': 'test',
        **parse_result
    })
    
    # 验证生成的Python代码
    assert "py" in generated
    python_code = generated["py"]
    
    # 验证类定义
    assert "class BasicTypes:" in python_code
    assert "class Point:" in python_code
    assert "class Rectangle:" in python_code
    assert "class ArrayTypes:" in python_code
    
    # 验证类型注解
    assert "i8: int" in python_code
    assert "u64: int" in python_code
    assert "str: str" in python_code
    assert "top_left: Point" in python_code
    
    # 验证序列化方法
    assert "def serialize(self)" in python_code
    assert "def deserialize(cls, data: bytes)" in python_code
    assert "@classmethod" in python_code

def test_mixed_features(parser, tmp_path):
    """测试混合特性"""
    # 创建不同配置组合的测试
    configs = [
        GeneratorConfig(enable_serialization=True, enable_version_control=False),
        GeneratorConfig(enable_serialization=False, enable_version_control=True),
        GeneratorConfig(enable_doc_comments=True, enable_type_checking=False),
        GeneratorConfig(
            enable_field_encryption=True,
            field_encryption_salt="test",
            encryption=EncryptionConfig(
                enable=True,
                encrypted_fields={"BasicTypes": ["i8", "u64"]}
            )
        )
    ]
    
    input_file = tmp_path / "test.h"
    input_file.write_text(TEST_HEADER)
    parse_result = parser.parse_file(str(input_file))
    
    for config in configs:
        # 测试C生成器
        c_gen = CGenerator(config)
        c_result = c_gen.generate({
            'module_name': 'test',
            **parse_result
        })
        assert "h" in c_result
        assert "c" in c_result
        
        # 测试Python生成器
        py_gen = PythonGenerator(config)
        py_result = py_gen.generate({
            'module_name': 'test',
            **parse_result
        })
        assert "py" in py_result

def test_error_handling(parser, config, tmp_path):
    """测试错误处理"""
    # 测试无效的C代码
    invalid_header = """
    typedef struct {
        invalid_type x;  // 未定义的类型
        int y
    } InvalidStruct;  // 缺少分号
    """
    
    input_file = tmp_path / "invalid.h"
    input_file.write_text(invalid_header)
    
    # 解析应该失败但不应崩溃
    with pytest.raises(Exception):
        parser.parse_file(str(input_file))
    
    # 测试无效的配置
    with pytest.raises(Exception):
        GeneratorConfig(byte_order="invalid") 
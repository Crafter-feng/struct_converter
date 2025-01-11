import pytest
from pathlib import Path
from struct_converter.core.config import GeneratorConfig
from struct_converter.core.encryption_config import EncryptionConfig
from struct_converter.generators.c_generator import CGenerator
from c_parser.tree_sitter_parser import CTreeSitterParser

TEST_HEADER = """
typedef struct {
    int sensitive_data;
    char secret_key[32];
    float public_value;
} TestStruct;

typedef struct {
    char username[16];
    char password[32];
} UserData;
"""

@pytest.fixture
def config():
    return GeneratorConfig(
        output_dir="generated",
        encryption=EncryptionConfig(
            enable=True,
            salt="test_salt",
            encrypted_fields={
                "TestStruct": ["sensitive_data", "secret_key"],
                "UserData": ["password"]
            }
        )
    )

def test_full_generation(config, tmp_path):
    """测试完整的代码生成流程"""
    # 准备测试文件
    input_file = tmp_path / "test.h"
    input_file.write_text(TEST_HEADER)
    
    # 创建解析器和生成器
    parser = CTreeSitterParser()
    generator = CGenerator(config)
    
    # 解析代码
    parse_result = parser.parse_file(str(input_file))
    
    # 生成代码
    generated = generator.generate({
        'module_name': 'test',
        **parse_result
    })
    
    # 检查生成的文件
    assert "h" in generated
    assert "c" in generated
    assert "field_map.h" in generated
    
    header = generated["h"]
    source = generated["c"]
    field_map = generated["field_map.h"]
    
    # 验证字段加密
    assert "sensitive_data" not in header
    assert "secret_key" not in header
    assert "public_value" in header  # 未加密字段
    assert "password" not in header
    assert "username" in header  # 未加密字段
    
    # 验证字段映射
    assert "struct field_map_entry" in field_map
    assert "get_field_name" in field_map
    assert "get_encrypted_name" in field_map
    
    # 验证序列化函数
    assert "test_serialize" in source
    assert "test_deserialize" in source
    assert "test_from_json" in source
    assert "test_to_json" in source

def test_json_handling(config, tmp_path):
    """测试JSON处理"""
    # 准备测试文件
    input_file = tmp_path / "test.h"
    input_file.write_text(TEST_HEADER)
    
    # 创建解析器和生成器
    parser = CTreeSitterParser()
    generator = CGenerator(config)
    
    # 生成代码
    parse_result = parser.parse_file(str(input_file))
    generated = generator.generate({
        'module_name': 'test',
        **parse_result
    })
    
    # 保存生成的代码
    output_dir = tmp_path / "generated"
    output_dir.mkdir()
    
    for ext, content in generated.items():
        with open(output_dir / f"test.{ext}", "w") as f:
            f.write(content)
            
    # 编译和测试生成的代码
    # TODO: 添加实际的编译和运行测试 
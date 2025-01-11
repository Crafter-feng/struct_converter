import pytest
from pathlib import Path
import json
from struct_converter.core.config import GeneratorConfig
from struct_converter.generators.c_generator import CGenerator
from c_parser.tree_sitter_parser import CTreeSitterParser

def test_field_encryption(temp_workspace):
    """测试字段加密功能"""
    # 准备测试数据
    header_content = """
    typedef struct {
        int sensitive_data;
        char secret_key[32];
        void* private_ptr;
    } SecureStruct;
    """
    
    input_file = temp_workspace / "secure.h"
    input_file.write_text(header_content)
    
    # 配置加密
    config = GeneratorConfig(
        output_dir=str(temp_workspace),
        enable_field_encryption=True,
        field_encryption_salt="test_salt"
    )
    
    # 解析和生成
    parser = CTreeSitterParser()
    result = parser.parse_file(str(input_file))
    
    generator = CGenerator(config)
    generated = generator.generate({
        'module_name': 'secure',
        **result
    })
    
    # 检查生成的代码
    header_content = generated['header']
    
    # 检查是否包含加密的字段名
    assert 'Q_' in header_content
    assert '/* sensitive_data */' in header_content
    assert '/* secret_key */' in header_content
    assert '/* private_ptr */' in header_content
    
    # 检查字段映射文件
    field_map_h = temp_workspace / "field_map.h"
    field_map_json = temp_workspace / "field_map.json"
    
    assert field_map_h.exists()
    assert field_map_json.exists()
    
    # 检查JSON映射
    with open(field_map_json) as f:
        mapping = json.load(f)
        
    assert 'encrypted_fields' in mapping
    assert 'SecureStruct' in mapping['encrypted_fields']
    assert len(mapping['encrypted_fields']['SecureStruct']) == 3
    
    # 检查字段名是否一致
    struct_fields = mapping['encrypted_fields']['SecureStruct']
    assert 'sensitive_data' in struct_fields
    assert 'secret_key' in struct_fields
    assert 'private_ptr' in struct_fields 
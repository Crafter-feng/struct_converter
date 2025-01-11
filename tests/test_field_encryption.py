import pytest
from struct_converter.core.field_encryptor import FieldEncryptor
from struct_converter.core.field_validator import FieldValidator
from struct_converter.core.encryption_config import EncryptionConfig
import json

@pytest.fixture
def encryptor():
    return FieldEncryptor(salt="test_salt")

@pytest.fixture
def validator():
    return FieldValidator()

def test_field_name_format():
    """测试加密名称格式"""
    encryptor = FieldEncryptor(salt="test")
    name = encryptor.encrypt_field_name("TestStruct", "test_field")
    
    assert len(name) == 4
    assert name[:2].isalpha() and name[:2].isupper()
    assert all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567' for c in name[2:])

def test_struct_prefix():
    """测试结构体前缀"""
    encryptor = FieldEncryptor(salt="test")
    name1 = encryptor.encrypt_field_name("TestStruct", "field1")
    name2 = encryptor.encrypt_field_name("TestStruct", "field2")
    
    assert name1[:2] == name2[:2]  # 同一结构体应该有相同前缀

def test_name_collision():
    """测试名称冲突处理"""
    encryptor = FieldEncryptor(salt="test")
    names = set()
    
    # 生成100个名称
    for i in range(100):
        name = encryptor.encrypt_field_name("TestStruct", f"field_{i}")
        assert name not in names  # 确保没有重复
        names.add(name) 

def test_field_map_generation(encryptor, tmp_path):
    """测试字段映射文件生成"""
    # 添加一些测试数据
    encryptor.encrypt_field_name("TestStruct", "field1")
    encryptor.encrypt_field_name("TestStruct", "field2")
    encryptor.encrypt_field_name("OtherStruct", "data")
    
    # 生成并保存映射文件
    encryptor.save_field_map(str(tmp_path))
    
    # 检查生成的文件
    header_file = tmp_path / "field_map.h"
    json_file = tmp_path / "field_map.json"
    
    assert header_file.exists()
    assert json_file.exists()
    
    # 检查头文件内容
    header_content = header_file.read_text()
    assert "#pragma pack(push, 1)" in header_content
    assert "struct field_map_entry" in header_content
    assert "char key[4]" in header_content
    assert "const char* name" in header_content
    
    # 检查JSON文件内容
    with open(json_file) as f:
        mapping = json.load(f)
    assert "encrypted_fields" in mapping
    assert "field_comments" in mapping
    assert "TestStruct" in mapping["encrypted_fields"]
    assert len(mapping["encrypted_fields"]["TestStruct"]) == 2

def test_error_handling(encryptor):
    """测试错误处理"""
    # 测试无效的结构体名
    name = encryptor.encrypt_field_name("", "field")
    assert name.startswith("F")  # 应该返回后备名称
    
    # 测试无效的字段名
    name = encryptor.encrypt_field_name("TestStruct", "")
    assert name.startswith("F")
    
    # 测试异常情况
    name = encryptor.encrypt_field_name("TestStruct", None)  # type: ignore
    assert name.startswith("F")

def test_name_validation(validator):
    """测试名称验证"""
    # 有效的名称
    assert validator.validate_encrypted_name("TEAB")
    assert validator.validate_encrypted_name("ST23")
    
    # 无效的名称
    assert not validator.validate_encrypted_name("te12")  # 小写字母
    assert not validator.validate_encrypted_name("TE1")   # 长度错误
    assert not validator.validate_encrypted_name("TE1@")  # 无效字符
    assert not validator.validate_encrypted_name("12AB")  # 前缀必须是字母

def test_struct_prefix_conflicts(validator):
    """测试结构体前缀冲突"""
    # 第一个前缀应该成功
    assert validator.validate_struct_prefix("TestStruct", "TE")
    
    # 相同的前缀应该失败
    assert not validator.validate_struct_prefix("TemplateStruct", "TE")
    
    # 不同的前缀应该成功
    assert validator.validate_struct_prefix("DataStruct", "DA")

def test_integration(encryptor, validator, tmp_path):
    """集成测试"""
    # 生成加密名称
    names = []
    for i in range(10):
        name = encryptor.encrypt_field_name(f"Struct{i}", "field")
        names.append(name)
        
        # 验证名称格式
        assert validator.validate_encrypted_name(name)
        
        # 验证前缀
        assert validator.validate_struct_prefix(f"Struct{i}", name[:2])
        
    # 确保没有重复
    assert len(set(names)) == len(names)
    
    # 生成并验证映射文件
    encryptor.save_field_map(str(tmp_path))
    header_file = tmp_path / "field_map.h"
    assert header_file.exists()
    
    content = header_file.read_text()
    for name in names:
        assert name in content

def test_json_format(encryptor, tmp_path):
    """测试JSON格式"""
    # 添加测试数据
    encryptor.encrypt_field_name("TestStruct", "sensitive_data")
    encryptor.encrypt_field_name("TestStruct", "secret_key")
    
    # 保存映射文件
    encryptor.save_field_map(str(tmp_path))
    json_file = tmp_path / "field_map.json"
    
    # 验证JSON格式
    with open(json_file) as f:
        data = json.load(f)
        
    assert isinstance(data, dict)
    assert "encrypted_fields" in data
    assert "field_comments" in data
    
    test_struct = data["encrypted_fields"]["TestStruct"]
    assert isinstance(test_struct, dict)
    assert len(test_struct) == 2
    
    # 验证字段名映射
    for original, encrypted in test_struct.items():
        assert len(encrypted) == 4
        assert encrypted[:2].isalpha()
        assert encrypted[:2].isupper() 
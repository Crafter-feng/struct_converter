import pytest
from pathlib import Path
from struct_converter.core.encryption_config import EncryptionConfig
from struct_converter.core.field_encryptor import FieldEncryptor

@pytest.fixture
def config():
    return EncryptionConfig(
        enable=True,
        salt="test_salt",
        encrypt_all=False,
        encrypted_fields={
            "TestStruct": ["sensitive_data", "secret_key"],
            "UserData": ["password", "token"]
        },
        excluded_fields={
            "PublicStruct": ["public_field"]
        }
    )

def test_config_load_save(config, tmp_path):
    """测试配置的保存和加载"""
    config_file = tmp_path / "encrypt_config.json"
    
    # 保存配置
    config.save(config_file)
    assert config_file.exists()
    
    # 加载配置
    loaded = EncryptionConfig.load(config_file)
    assert loaded.enable == config.enable
    assert loaded.salt == config.salt
    assert loaded.encrypted_fields == config.encrypted_fields

def test_field_encryption_with_config(config):
    """测试基于配置的字段加密"""
    encryptor = FieldEncryptor(config)
    
    # 应该加密的字段
    name1 = encryptor.encrypt_field_name("TestStruct", "sensitive_data")
    assert name1 != "sensitive_data"  # 应该被加密
    
    # 不应该加密的字段
    name2 = encryptor.encrypt_field_name("TestStruct", "normal_field")
    assert name2 == "normal_field"  # 不应该被加密
    
    # 排除列表中的字段
    name3 = encryptor.encrypt_field_name("PublicStruct", "public_field")
    assert name3 == "public_field"  # 不应该被加密

def test_encrypt_all_mode(config):
    """测试全部加密模式"""
    config.encrypt_all = True
    encryptor = FieldEncryptor(config)
    
    # 所有字段都应该被加密
    name1 = encryptor.encrypt_field_name("AnyStruct", "any_field")
    assert name1 != "any_field"
    
    # 排除列表中的字段仍然不应该被加密
    name2 = encryptor.encrypt_field_name("PublicStruct", "public_field")
    assert name2 == "public_field"

def test_config_validation():
    """测试配置验证"""
    # 无效的字段名列表
    with pytest.raises(ValueError):
        EncryptionConfig(
            enable=True,
            encrypted_fields={"TestStruct": None}
        )
    
    # 无效的排除列表
    with pytest.raises(ValueError):
        EncryptionConfig(
            enable=True,
            excluded_fields={"TestStruct": [123]}  # type: ignore
        ) 
import pytest
from struct_converter.core.exceptions import (
    StructConverterError,
    ValidationError,
    ConfigError,
    GenerationError,
)
from struct_converter.core.config import GeneratorConfig
from struct_converter.core.encryption_config import EncryptionConfig
from struct_converter.generators.c_generator import CGenerator
from struct_converter.core.field_encryptor import FieldEncryptor

def test_invalid_config():
    """测试无效配置"""
    # 无效的字节序
    with pytest.raises(ValidationError):
        GeneratorConfig(byte_order="invalid")
        
    # 无效的指针大小
    with pytest.raises(ValidationError):
        GeneratorConfig(pointer_size=3)
        
    # 无效的对齐方式
    with pytest.raises(ValidationError):
        GeneratorConfig(default_alignment=0)

def test_invalid_encryption_config():
    """测试无效的加密配置"""
    # 无效的字段列表
    with pytest.raises(ValidationError):
        EncryptionConfig(
            enable=True,
            encrypted_fields={"TestStruct": None}
        )
        
    # 无效的排除列表
    with pytest.raises(ValidationError):
        EncryptionConfig(
            enable=True,
            excluded_fields={"TestStruct": [123]}  # type: ignore
        )

def test_field_encryption_errors():
    """测试字段加密错误"""
    config = EncryptionConfig(enable=True)
    encryptor = FieldEncryptor(config)
    
    # 空结构体名
    name = encryptor.encrypt_field_name("", "field")
    assert name.startswith("F")  # 应该返回后备名称
    
    # 空字段名
    name = encryptor.encrypt_field_name("TestStruct", "")
    assert name.startswith("F")
    
    # None值
    name = encryptor.encrypt_field_name("TestStruct", None)  # type: ignore
    assert name.startswith("F")

def test_generator_error_handling():
    """测试生成器错误处理"""
    config = GeneratorConfig()
    generator = CGenerator(config)
    
    # 缺少必要的字段
    with pytest.raises(Exception):
        generator.generate({})
        
    # 无效的结构体定义
    with pytest.raises(Exception):
        generator.generate({
            'module_name': 'test',
            'structs': {'InvalidStruct': None}
        }) 
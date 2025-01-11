import pytest
import tempfile
from pathlib import Path
from struct_converter.core.config import GeneratorConfig
from struct_converter.core.exceptions import ValidationError

def test_default_config():
    """测试默认配置"""
    config = GeneratorConfig()
    
    assert config.output_dir == "generated"
    assert config.enable_serialization is True
    assert config.enable_version_control is True
    assert config.enable_doc_comments is True
    assert config.byte_order == 'native'
    assert config.pointer_size == 8
    assert config.default_alignment == 4

def test_config_from_dict():
    """测试从字典创建配置"""
    data = {
        'output_dir': 'test_output',
        'enable_serialization': False,
        'byte_order': 'little',
        'pointer_size': 4
    }
    
    config = GeneratorConfig.from_dict(data)
    
    assert config.output_dir == 'test_output'
    assert config.enable_serialization is False
    assert config.byte_order == 'little'
    assert config.pointer_size == 4
    
    # 未指定的选项应该使用默认值
    assert config.enable_version_control is True
    assert config.default_alignment == 4

def test_invalid_config():
    """测试无效配置"""
    # 无效的字节序
    with pytest.raises(ValidationError):
        GeneratorConfig.from_dict({'byte_order': 'invalid'})
        
    # 无效的指针大小
    with pytest.raises(ValidationError):
        GeneratorConfig.from_dict({'pointer_size': 3})
        
    # 无效的对齐值
    with pytest.raises(ValidationError):
        GeneratorConfig.from_dict({'default_alignment': 3})

def test_config_save_load():
    """测试配置的保存和加载"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / 'test_config.json'
        
        # 创建配置并保存
        config = GeneratorConfig(
            output_dir='test_output',
            enable_serialization=False,
            byte_order='little'
        )
        config.save(str(config_file))
        
        # 加载配置并验证
        loaded_config = GeneratorConfig.load(str(config_file))
        
        assert loaded_config.output_dir == 'test_output'
        assert loaded_config.enable_serialization is False
        assert loaded_config.byte_order == 'little'
        
        # 未指定的选项应该使用默认值
        assert loaded_config.enable_version_control is True
        assert loaded_config.default_alignment == 4

def test_config_validation():
    """测试配置验证"""
    config = GeneratorConfig()
    
    # 测试输出目录验证
    with pytest.raises(ValidationError):
        config.output_dir = ''  # 空目录名
        
    # 测试字节序验证
    with pytest.raises(ValidationError):
        config.byte_order = 'invalid'  # 无效的字节序
        
    # 测试指针大小验证
    with pytest.raises(ValidationError):
        config.pointer_size = 16  # 无效的指针大小
        
    # 测试对齐值验证
    with pytest.raises(ValidationError):
        config.default_alignment = 0  # 无效的对齐值 
import pytest
from struct_converter.core.field_validator import FieldValidator

@pytest.fixture
def validator():
    return FieldValidator()

def test_name_format_validation(validator):
    """测试名称格式验证"""
    # 有效的名称
    valid_names = [
        "TEAB", "ST23", "PQRS", "WXYZ",
        "AB45", "CD67", "EF23", "GH45"
    ]
    for name in valid_names:
        assert validator.validate_encrypted_name(name)
        
    # 无效的名称
    invalid_names = [
        "te12",     # 小写字母
        "TE1",      # 长度错误
        "TE12345",  # 长度错误
        "TE1@",     # 无效字符
        "12AB",     # 前缀必须是字母
        "T!AB",     # 无效字符
        "TABC",     # 后缀必须包含数字
    ]
    for name in invalid_names:
        assert not validator.validate_encrypted_name(name)

def test_name_conflict_detection(validator):
    """测试名称冲突检测"""
    # 第一次使用名称应该成功
    assert not validator.check_name_conflict("TEAB")
    
    # 再次使用相同名称应该失败
    assert validator.check_name_conflict("TEAB")
    
    # 使用不同名称应该成功
    assert not validator.check_name_conflict("ST23")

def test_struct_prefix_validation(validator):
    """测试结构体前缀验证"""
    # 第一个结构体的前缀应该成功
    assert validator.validate_struct_prefix("TestStruct", "TE")
    
    # 不同结构体使用相同前缀应该失败
    assert not validator.validate_struct_prefix("TemplateStruct", "TE")
    
    # 不同结构体使用不同前缀应该成功
    assert validator.validate_struct_prefix("DataStruct", "DA")
    
    # 无效的前缀格式
    invalid_prefixes = [
        "t1",   # 小写字母
        "1T",   # 数字开头
        "T",    # 长度不足
        "TEA",  # 长度过长
        "T!",   # 无效字符
    ]
    for prefix in invalid_prefixes:
        assert not validator.validate_struct_prefix("TestStruct", prefix)

def test_prefix_reuse_after_reset(validator):
    """测试重置后重用前缀"""
    # 使用前缀
    assert validator.validate_struct_prefix("TestStruct", "TE")
    assert not validator.validate_struct_prefix("TemplateStruct", "TE")
    
    # 重置验证器
    validator.reset()
    
    # 应该可以重用前缀
    assert validator.validate_struct_prefix("TestStruct", "TE")

def test_concurrent_validation(validator):
    """测试并发验证"""
    import threading
    
    def validate_names():
        for i in range(100):
            name = f"TE{i:02d}"
            validator.validate_encrypted_name(name)
            
    threads = [threading.Thread(target=validate_names) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    # 验证没有重复名称
    assert len(validator.used_names) == 100

def test_validation_with_special_cases(validator):
    """测试特殊情况"""
    # 空名称
    assert not validator.validate_encrypted_name("")
    
    # None
    assert not validator.validate_encrypted_name(None)  # type: ignore
    
    # 非字符串类型
    assert not validator.validate_encrypted_name(123)  # type: ignore
    
    # Unicode字符
    assert not validator.validate_encrypted_name("TE你好")
    
    # 空格
    assert not validator.validate_encrypted_name("TE 1") 
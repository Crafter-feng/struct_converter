import pytest
from struct_converter.core.type_converter import TypeConverter

@pytest.fixture
def converter():
    return TypeConverter()

def test_c_to_python_type(converter):
    """测试C类型到Python类型的转换"""
    # 基本类型测试
    assert converter.c_to_python_type('int8_t') == 'int'
    assert converter.c_to_python_type('uint8_t') == 'int'
    assert converter.c_to_python_type('float') == 'float'
    assert converter.c_to_python_type('char') == 'str'
    assert converter.c_to_python_type('bool') == 'bool'
    assert converter.c_to_python_type('void') == 'None'
    
    # 未知类型应该保持不变
    assert converter.c_to_python_type('custom_type') == 'custom_type'

def test_c_to_ctypes_type(converter):
    """测试C类型到ctypes类型的转换"""
    assert converter.c_to_ctypes_type('int8_t') == 'ctypes.c_int8'
    assert converter.c_to_ctypes_type('uint8_t') == 'ctypes.c_uint8'
    assert converter.c_to_ctypes_type('float') == 'ctypes.c_float'
    assert converter.c_to_ctypes_type('char') == 'ctypes.c_char'
    assert converter.c_to_ctypes_type('bool') == 'ctypes.c_bool'
    
    # 未知类型应该保持不变
    assert converter.c_to_ctypes_type('custom_type') == 'custom_type'

def test_c_to_cpp_type(converter):
    """测试C类型到C++类型的转换"""
    assert converter.c_to_cpp_type('int8_t') == 'std::int8_t'
    assert converter.c_to_cpp_type('uint8_t') == 'std::uint8_t'
    assert converter.c_to_cpp_type('float') == 'float'
    assert converter.c_to_cpp_type('char') == 'char'
    assert converter.c_to_cpp_type('bool') == 'bool'
    
    # 未知类型应该保持不变
    assert converter.c_to_cpp_type('custom_type') == 'custom_type' 
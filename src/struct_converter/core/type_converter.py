from typing import Dict, Any, Optional

class TypeConverter:
    """类型转换工具类"""
    
    @staticmethod
    def c_to_python_type(c_type: str) -> str:
        """C类型转Python类型"""
        basic_types = {
            'int8_t': 'int',
            'uint8_t': 'int',
            'int16_t': 'int',
            'uint16_t': 'int',
            'int32_t': 'int',
            'uint32_t': 'int',
            'int64_t': 'int',
            'uint64_t': 'int',
            'float': 'float',
            'double': 'float',
            'char': 'str',
            'bool': 'bool',
            'void': 'None'
        }
        return basic_types.get(c_type, c_type)
        
    @staticmethod
    def c_to_ctypes_type(c_type: str) -> str:
        """C类型转ctypes类型"""
        basic_types = {
            'int8_t': 'ctypes.c_int8',
            'uint8_t': 'ctypes.c_uint8',
            'int16_t': 'ctypes.c_int16',
            'uint16_t': 'ctypes.c_uint16',
            'int32_t': 'ctypes.c_int32',
            'uint32_t': 'ctypes.c_uint32',
            'int64_t': 'ctypes.c_int64',
            'uint64_t': 'ctypes.c_uint64',
            'float': 'ctypes.c_float',
            'double': 'ctypes.c_double',
            'char': 'ctypes.c_char',
            'bool': 'ctypes.c_bool',
            'void': 'None'
        }
        return basic_types.get(c_type, c_type)
        
    @staticmethod
    def c_to_cpp_type(c_type: str) -> str:
        """C类型转C++类型"""
        basic_types = {
            'int8_t': 'std::int8_t',
            'uint8_t': 'std::uint8_t',
            'int16_t': 'std::int16_t',
            'uint16_t': 'std::uint16_t',
            'int32_t': 'std::int32_t',
            'uint32_t': 'std::uint32_t',
            'int64_t': 'std::int64_t',
            'uint64_t': 'std::uint64_t',
            'float': 'float',
            'double': 'double',
            'char': 'char',
            'bool': 'bool',
            'void': 'void'
        }
        return basic_types.get(c_type, c_type) 
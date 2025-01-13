import json
import os
import pytest
from c_parser.core.type_manager import TypeManager

@pytest.fixture
def type_info():
    """测试用的类型信息"""
    return {
        'struct_types': {
            'Point': {
                'name': 'Point',
                'fields': [
                    {'name': 'x', 'type': 'int'},
                    {'name': 'y', 'type': 'int'}
                ]
            },
            'Vector': {
                'name': 'Vector',
                'fields': [
                    {'name': 'x', 'type': 'float'},
                    {'name': 'y', 'type': 'float'},
                    {'name': 'z', 'type': 'float'}
                ]
            }
        },
        'union_types': {
            'DataValue': {
                'name': 'DataValue',
                'fields': [
                    {'name': 'i', 'type': 'int'},
                    {'name': 'f', 'type': 'float'},
                    {'name': 'c', 'type': 'char'}
                ]
            }
        },
        'enum_types': {
            'LogLevel': {
                'name': 'LogLevel',
                'values': {
                    'DEBUG': 0,
                    'INFO': 1,
                    'WARNING': 2,
                    'ERROR': 3
                }
            }
        },
        'typedef_types': {
            'u8': {
                'base_type': 'unsigned char',
                'is_typedef': True
            },
            'i32': {
                'base_type': 'int',
                'is_typedef': True
            },
            'f32': {
                'base_type': 'float',
                'is_typedef': True
            },
            'PointPtr': {
                'base_type': 'struct Point*',
                'is_typedef': True
            }
        }
    }

class TestTypeManager:
    @pytest.fixture
    def type_manager(self, type_info):
        """创建TypeManager实例"""
        return TypeManager(type_info)

    def test_init_without_type_info(self):
        """测试不带类型信息的初始化"""
        tm = TypeManager()
        assert len(tm.basic_types) > 0
        assert len(tm.struct_types) == 0
        assert len(tm.union_types) == 0

    def test_init_with_type_info(self, type_info):
        """测试带类型信息的初始化"""
        tm = TypeManager(type_info)
        assert 'Point' in tm.struct_types
        assert 'DataValue' in tm.union_types
        assert 'LogLevel' in tm.enum_types
        assert 'u8' in tm.typedef_types

    def test_basic_types(self, type_manager):
        """测试基本类型判断"""
        # 基本类型
        assert type_manager.is_basic_type('int')
        assert type_manager.is_basic_type('char')
        assert type_manager.is_basic_type('float')
        assert type_manager.is_basic_type('double')
        
        # 非基本类型
        assert not type_manager.is_basic_type('Point')
        assert not type_manager.is_basic_type('DataValue')
        assert not type_manager.is_basic_type('u8')  # typedef类型

    def test_struct_types(self, type_manager):
        """测试结构体类型判断"""
        assert type_manager.is_struct_type('Point')
        assert type_manager.is_struct_type('Vector')
        assert type_manager.is_struct_type('struct Point')
        
        # 非结构体类型
        assert not type_manager.is_struct_type('int')
        assert not type_manager.is_struct_type('DataValue')
        assert not type_manager.is_struct_type('LogLevel')

    def test_union_types(self, type_manager):
        """测试联合体类型判断"""
        assert type_manager.is_union_type('DataValue')
        assert type_manager.is_union_type('union DataValue')
        
        # 非联合体类型
        assert not type_manager.is_union_type('Point')
        assert not type_manager.is_union_type('int')

    def test_enum_types(self, type_manager):
        """测试枚举类型判断"""
        assert type_manager.is_enum_type('LogLevel')
        
        # 非枚举类型
        assert not type_manager.is_enum_type('Point')
        assert not type_manager.is_enum_type('int')

    def test_pointer_types(self, type_manager):
        """测试指针类型判断"""
        assert type_manager.is_pointer_type('int*')
        assert type_manager.is_pointer_type('char*')
        assert type_manager.is_pointer_type('PointPtr')
        
        # 非指针类型
        assert not type_manager.is_pointer_type('int')
        assert not type_manager.is_pointer_type('Point')

    def test_real_type_resolution(self, type_manager):
        """测试类型解析"""
        assert type_manager.get_real_type('u8') == 'unsigned char'
        assert type_manager.get_real_type('i32') == 'int'
        assert type_manager.get_real_type('f32') == 'float'
        
        # 非typedef类型应该保持不变
        assert type_manager.get_real_type('int') == 'int'
        assert type_manager.get_real_type('Point') == 'Point'

    def test_type_info_export(self, type_manager, type_info):
        """测试类型信息导出"""
        exported = type_manager.export_type_info()
        
        # 验证导出的类型信息
        assert 'typedef_types' in exported
        assert 'struct_types' in exported
        assert 'union_types' in exported
        assert 'enum_types' in exported
        assert 'struct_info' in exported
        assert 'union_info' in exported
        
        # 验证内容
        assert exported['typedef_types'] == type_info['typedef_types']
        assert exported['struct_types'] == type_info['struct_types']
        assert exported['union_types'] == type_info['union_types']
        assert exported['enum_types'] == type_info['enum_types'] 

    def test_type_details(self, type_manager):
        """测试类型详细信息"""
        struct_info = {
            'kind': 'struct',
            'name': 'TestStruct',
            'fields': [{'name': 'x', 'type': 'int'}],
            'details': {
                'attributes': {'packed': True},
                'visibility': 'private',
                'storage_class': 'static',
                'packed': True
            },
            'location': {
                'file': 'test.h',
                'line': 1,
                'column': 0
            },
            'comment': '// Test struct'
        }
        
        type_manager.register_type('TestStruct', struct_info)
        
        # 验证详细信息
        details = type_manager.get_type_details('TestStruct')
        assert details['attributes']['packed'] is True
        assert details['visibility'] == 'private'
        assert details['storage_class'] == 'static'
        
        # 验证位置信息
        location = type_manager.get_type_location('TestStruct')
        assert location['file'] == 'test.h'
        assert location['line'] == 1
        
        # 验证注释
        comment = type_manager.get_type_comment('TestStruct')
        assert comment == '// Test struct'

    def test_type_compatibility(self, type_manager):
        """测试类型兼容性"""
        # 基本类型兼容性
        assert type_manager.is_compatible_types('int', 'int32_t')
        assert not type_manager.is_compatible_types('int', 'char')
        
        # 指针类型兼容性
        assert type_manager.is_compatible_types('void *', 'int *')  # 注意空格
        assert type_manager.is_compatible_types('void*', 'char*')
        assert type_manager.is_compatible_types('int*', 'int*')
        assert not type_manager.is_compatible_types('int*', 'int**')
        assert not type_manager.is_compatible_types('char*', 'int*')
        
        # void*特殊情况
        assert type_manager.is_compatible_types('void*', 'int*')
        assert type_manager.is_compatible_types('void*', 'char*')
        assert type_manager.is_compatible_types('void*', 'struct Point*')
        
        # 数组类型兼容性
        assert type_manager.is_compatible_types('int[10]', 'int[10]')
        assert not type_manager.is_compatible_types('int[10]', 'int[20]')
        assert not type_manager.is_compatible_types('int[10]', 'char[10]')

    def test_type_string_parsing(self, type_manager):
        """测试类型字符串解析"""
        # 测试基本类型
        result = type_manager.parse_type_string('const int* volatile')
        assert result['base_type'] == 'int'
        assert set(result['qualifiers']) == {'const', 'volatile'}
        assert result['pointer_level'] == 1
        
        # 测试数组类型
        result = type_manager.parse_type_string('char[10][20]')
        assert result['base_type'] == 'char'
        assert result['array_dims'] == [10, 20]
        
        # 测试复杂类型
        result = type_manager.parse_type_string('static const struct Point* restrict')
        assert result['base_type'] == 'struct Point'
        assert set(result['qualifiers']) == {'const', 'restrict'}
        assert result['storage_class'] == 'static'
        assert result['pointer_level'] == 1 
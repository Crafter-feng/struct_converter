import json
import os
import pytest
from c_parser import TypeManager


class TestTypeManager:
    @pytest.fixture
    def type_info(self):
        """加载测试数据"""
        cache_file = os.path.join(os.path.dirname(__file__), '../.cache/test_structs.h.json')
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    @pytest.fixture
    def type_manager(self, type_info):
        """创建TypeManager实例"""
        return TypeManager(type_info)

    def test_basic_types(self, type_manager):
        """测试基本类型判断"""
        # 基本类型
        assert type_manager.is_basic_type('int')
        assert type_manager.is_basic_type('char')
        assert type_manager.is_basic_type('float')
        assert type_manager.is_basic_type('double')
        
        # 基本类型别名
        assert type_manager.is_basic_type('u8')
        assert type_manager.is_basic_type('i32')
        assert type_manager.is_basic_type('f32')
        
        # 非基本类型
        assert not type_manager.is_basic_type('Point')
        assert not type_manager.is_basic_type('Node')
        assert not type_manager.is_basic_type('DataValue')
        
    def test_struct_types(self, type_manager):
        """测试结构体类型判断"""
        # 直接结构体类型
        assert type_manager.is_struct_type('Point')
        assert type_manager.is_struct_type('Vector')
        assert type_manager.is_struct_type('Node')
        
        # typedef的结构体类型
        assert type_manager.is_struct_type('struct Point')
        
        # 非结构体类型
        assert not type_manager.is_struct_type('int')
        assert not type_manager.is_struct_type('DataValue')
        assert not type_manager.is_struct_type('LogLevel')
        
    def test_union_types(self, type_manager):
        """测试联合体类型判断"""
        # 直接联合体类型
        assert type_manager.is_union_type('DataValue')
        assert type_manager.is_union_type('union DataValue')
        
        # 非联合体类型
        assert not type_manager.is_union_type('Point')
        assert not type_manager.is_union_type('int')
        assert not type_manager.is_union_type('LogLevel')
        
    def test_enum_types(self, type_manager):
        """测试枚举类型判断"""
        # 直接枚举类型
        assert type_manager.is_enum_type('LogLevel')
        assert type_manager.is_enum_type('Direction')
        assert type_manager.is_enum_type('Status')
        
        # 非枚举类型
        assert not type_manager.is_enum_type('Point')
        assert not type_manager.is_enum_type('int')
        assert not type_manager.is_enum_type('DataValue')
        
    def test_pointer_types(self, type_manager):
        """测试指针类型判断"""
        # 直接指针类型
        assert type_manager.is_pointer_type('int*')
        assert type_manager.is_pointer_type('char*')
        assert type_manager.is_pointer_type('void*')
        
        # typedef的指针类型
        assert type_manager.is_pointer_type('PointPtr')
        assert type_manager.is_pointer_type('VectorPtr')
        
        # 非指针类型
        assert not type_manager.is_pointer_type('int')
        assert not type_manager.is_pointer_type('Point')
        assert not type_manager.is_pointer_type('DataValue')
        
    def test_real_type_resolution(self, type_manager):
        """测试类型解析"""
        # 基本类型别名
        assert type_manager.get_real_type('u8') == 'uint8_t'
        assert type_manager.get_real_type('i32') == 'int32_t'
        assert type_manager.get_real_type('f32') == 'float'
        
        # 结构体类型
        assert type_manager.get_real_type('Point') == 'struct Point'
        assert type_manager.get_real_type('Vector') == 'struct Vector'
        
        # 指针类型
        assert type_manager.get_real_type('PointPtr') == 'struct Point*'
        
        # 原始类型保持不变
        assert type_manager.get_real_type('int') == 'int'
        assert type_manager.get_real_type('char*') == 'char*'
        
    def test_type_info_export(self, type_manager, type_info):
        """测试类型信息导出"""
        exported = type_manager.export_type_info()
        
        # 验证导出的类型信息
        assert 'typedef_types' in exported
        assert 'struct_types' in exported
        assert 'union_types' in exported
        assert 'pointer_types' in exported
        assert 'struct_info' in exported
        assert 'union_info' in exported
        assert 'enum_types' in exported
        
        # 验证类型数量
        assert len(exported['struct_types']) == len(type_info['struct_types'])
        assert len(exported['union_types']) == len(type_info['union_types'])
        assert len(exported['pointer_types']) == len(type_info['pointer_types']) 
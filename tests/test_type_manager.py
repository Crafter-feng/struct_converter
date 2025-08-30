import pytest
from unittest.mock import Mock, patch

from c_parser.core.type_manager import TypeManager


class TestTypeManager:
    """TypeManager测试类"""
    
    def test_initialization(self):
        """测试初始化"""
        # 测试默认初始化
        tm = TypeManager()
        assert tm._global_types == []
        assert tm._current_types == []
        assert tm._global_pointer_types == set()
        assert tm._current_pointer_types == set()
        assert tm._global_macro_definitions == {}
        assert tm._current_macro_definitions == {}
    
    def test_initialization_with_type_info(self):
        """测试带类型信息的初始化"""
        type_info = {
            'types': [
                {'name': 'Point', 'kind': 'struct', 'fields': []},
                {'name': 'Color', 'kind': 'enum', 'values': []}
            ],
            'pointer_types': {'int*', 'char*'},
            'macro_definitions': {'MAX_SIZE': 100}
        }
        
        tm = TypeManager(type_info)
        
        assert len(tm._global_types) == 2
        assert 'int*' in tm._global_pointer_types
        assert 'char*' in tm._global_pointer_types
        assert tm._global_macro_definitions['MAX_SIZE'] == 100
    
    def test_basic_types_property(self):
        """测试基本类型属性"""
        tm = TypeManager()
        basic_types = tm.basic_types
        
        # 验证基本类型存在
        assert 'int' in basic_types
        assert 'char' in basic_types
        assert 'float' in basic_types
        assert 'double' in basic_types
        
        # 验证类型信息完整性
        assert basic_types['int']['size'] == 4
        assert basic_types['int']['signed'] == True
        assert basic_types['int']['alignment'] == 4
        
        assert basic_types['char']['size'] == 1
        assert basic_types['char']['signed'] == True
        assert basic_types['char']['alignment'] == 1
    
    def test_struct_types_property(self):
        """测试结构体类型属性"""
        tm = TypeManager()
        
        # 初始状态应该为空
        assert tm.struct_types == []
        
        # 添加结构体类型
        tm._global_types.append({'name': 'Point', 'kind': 'struct', 'fields': []})
        tm._current_types.append({'name': 'Vector', 'kind': 'struct', 'fields': []})
        
        struct_types = tm.struct_types
        assert len(struct_types) == 2
        assert any(s['name'] == 'Point' for s in struct_types)
        assert any(s['name'] == 'Vector' for s in struct_types)
    
    def test_union_types_property(self):
        """测试联合体类型属性"""
        tm = TypeManager()
        
        # 初始状态应该为空
        assert tm.union_types == []
        
        # 添加联合体类型
        tm._global_types.append({'name': 'Data', 'kind': 'union', 'fields': []})
        
        union_types = tm.union_types
        assert len(union_types) == 1
        assert union_types[0]['name'] == 'Data'
    
    def test_enum_types_property(self):
        """测试枚举类型属性"""
        tm = TypeManager()
        
        # 初始状态应该为空
        assert tm.enum_types == []
        
        # 添加枚举类型
        tm._current_types.append({'name': 'Color', 'kind': 'enum', 'values': []})
        
        enum_types = tm.enum_types
        assert len(enum_types) == 1
        assert enum_types[0]['name'] == 'Color'
    
    def test_typedef_types_property(self):
        """测试类型别名属性"""
        tm = TypeManager()
        
        # 初始状态应该为空
        assert tm.typedef_types == []
        
        # 添加类型别名
        tm._global_types.append({'name': 'u32', 'kind': 'typedef', 'base_type': 'uint32_t'})
        
        typedef_types = tm.typedef_types
        assert len(typedef_types) == 1
        assert typedef_types[0]['name'] == 'u32'
    
    def test_add_macro_definition(self):
        """测试添加宏定义"""
        tm = TypeManager()
        
        # 添加宏定义
        tm.add_macro_definition('MAX_SIZE', 100)
        tm.add_macro_definition('PI', 3.14159)
        
        assert tm._current_macro_definitions['MAX_SIZE'] == 100
        assert tm._current_macro_definitions['PI'] == 3.14159
        assert len(tm._current_macro_definitions) == 2
    
    def test_export_types_all_scope(self):
        """测试导出所有类型信息"""
        tm = TypeManager()
        
        # 添加全局类型
        tm._global_types.append({'name': 'GlobalStruct', 'kind': 'struct'})
        tm._global_pointer_types.add('int*')
        tm._global_macro_definitions['GLOBAL_MACRO'] = 1
        
        # 添加当前类型
        tm._current_types.append({'name': 'CurrentStruct', 'kind': 'struct'})
        tm._current_pointer_types.add('char*')
        tm._current_macro_definitions['CURRENT_MACRO'] = 2
        
        result = tm.export_types('all')
        
        assert len(result['types']) == 2
        assert len(result['pointer_types']) == 2
        assert len(result['macro_definitions']) == 2
        assert 'int*' in result['pointer_types']
        assert 'char*' in result['pointer_types']
        assert result['macro_definitions']['GLOBAL_MACRO'] == 1
        assert result['macro_definitions']['CURRENT_MACRO'] == 2
    
    def test_export_types_global_scope(self):
        """测试导出全局类型信息"""
        tm = TypeManager()
        
        # 添加全局和当前类型
        tm._global_types.append({'name': 'GlobalStruct', 'kind': 'struct'})
        tm._current_types.append({'name': 'CurrentStruct', 'kind': 'struct'})
        tm._global_macro_definitions['GLOBAL_MACRO'] = 1
        tm._current_macro_definitions['CURRENT_MACRO'] = 2
        
        result = tm.export_types('global')
        
        assert len(result['types']) == 1
        assert result['types'][0]['name'] == 'GlobalStruct'
        assert len(result['macro_definitions']) == 1
        assert 'GLOBAL_MACRO' in result['macro_definitions']
        assert 'CURRENT_MACRO' not in result['macro_definitions']
    
    def test_export_types_current_scope(self):
        """测试导出当前类型信息"""
        tm = TypeManager()
        
        # 添加全局和当前类型
        tm._global_types.append({'name': 'GlobalStruct', 'kind': 'struct'})
        tm._current_types.append({'name': 'CurrentStruct', 'kind': 'struct'})
        tm._global_macro_definitions['GLOBAL_MACRO'] = 1
        tm._current_macro_definitions['CURRENT_MACRO'] = 2
        
        result = tm.export_types('current')
        
        assert len(result['types']) == 1
        assert result['types'][0]['name'] == 'CurrentStruct'
        assert len(result['macro_definitions']) == 1
        assert 'CURRENT_MACRO' in result['macro_definitions']
        assert 'GLOBAL_MACRO' not in result['macro_definitions']
    
    def test_export_types_invalid_scope(self):
        """测试导出无效范围"""
        tm = TypeManager()
        
        # 添加一些类型
        tm._global_types.append({'name': 'TestStruct', 'kind': 'struct'})
        
        # 测试无效范围（应该回退到'all'）
        result = tm.export_types('invalid_scope')
        
        assert len(result['types']) == 1
        assert result['types'][0]['name'] == 'TestStruct'
    
    def test_type_aliases(self):
        """测试类型别名"""
        tm = TypeManager()
        
        # 验证预定义的类型别名
        assert tm.TYPE_ALIASES['u8'] == 'uint8_t'
        assert tm.TYPE_ALIASES['u32'] == 'uint32_t'
        assert tm.TYPE_ALIASES['i8'] == 'int8_t'
        assert tm.TYPE_ALIASES['f32'] == 'float'
        assert tm.TYPE_ALIASES['f64'] == 'double'
    
    def test_printf_formats(self):
        """测试printf格式映射"""
        tm = TypeManager()
        
        # 验证printf格式
        assert tm.PRINTF_FORMATS['int'] == '%d'
        assert tm.PRINTF_FORMATS['float'] == '%.6f'
        assert tm.PRINTF_FORMATS['double'] == '%.6lf'
        assert tm.PRINTF_FORMATS['char'] == '"%c"'
        assert tm.PRINTF_FORMATS['uint32_t'] == '%u'
    
    def test_load_type_info_with_typedef_types(self):
        """测试加载包含typedef的类型信息"""
        type_info = {
            'typedef_types': [
                {'name': 'custom_u32', 'base_type': 'uint32_t'},
                {'name': 'custom_ptr', 'base_type': 'int*'}
            ]
        }
        
        tm = TypeManager(type_info)
        
        # 验证类型别名被添加
        assert tm.TYPE_ALIASES['custom_u32'] == 'uint32_t'
        assert tm.TYPE_ALIASES['custom_ptr'] == 'int*'
    
    def test_load_type_info_with_types(self):
        """测试加载包含types的类型信息"""
        type_info = {
            'types': [
                {'name': 'custom_u32', 'kind': 'typedef', 'base_type': 'uint32_t'},
                {'name': 'Point', 'kind': 'struct', 'fields': []}
            ]
        }
        
        tm = TypeManager(type_info)
        
        # 验证类型别名被添加
        assert tm.TYPE_ALIASES['custom_u32'] == 'uint32_t'
        # 验证类型被加载
        assert len(tm._global_types) == 2
    
    def test_cache_clearing(self):
        """测试缓存清理"""
        tm = TypeManager()
        
        # 模拟缓存被填充
        tm._kind_cache['test'] = 'value'
        tm._find_cache['test'] = 'value'
        
        # 验证缓存存在
        assert 'test' in tm._kind_cache
        assert 'test' in tm._find_cache
        
        # 清理缓存
        tm._clear_cache()
        
        # 验证缓存被清空
        assert len(tm._kind_cache) == 0
        assert len(tm._find_cache) == 0
    
    def test_load_type_info_error_handling(self):
        """测试加载类型信息的错误处理"""
        tm = TypeManager()
        
        # 测试无效的类型信息
        with pytest.raises(Exception):
            tm._load_type_info(None)
    
    def test_export_types_empty_manager(self):
        """测试空管理器的导出"""
        tm = TypeManager()
        
        result = tm.export_types('all')
        
        assert result['types'] == []
        assert result['pointer_types'] == []
        assert result['macro_definitions'] == {}
    
    def test_macro_definition_overwrite(self):
        """测试宏定义覆盖"""
        tm = TypeManager()
        
        # 添加宏定义
        tm.add_macro_definition('TEST_MACRO', 1)
        assert tm._current_macro_definitions['TEST_MACRO'] == 1
        
        # 覆盖宏定义
        tm.add_macro_definition('TEST_MACRO', 2)
        assert tm._current_macro_definitions['TEST_MACRO'] == 2
        assert len(tm._current_macro_definitions) == 1
    
    def test_pointer_types_union(self):
        """测试指针类型集合的合并"""
        tm = TypeManager()
        
        # 添加全局指针类型
        tm._global_pointer_types.add('int*')
        tm._global_pointer_types.add('char*')
        
        # 添加当前指针类型
        tm._current_pointer_types.add('float*')
        tm._current_pointer_types.add('int*')  # 重复的
        
        result = tm.export_types('all')
        
        # 验证合并结果（去重）
        assert len(result['pointer_types']) == 3
        assert 'int*' in result['pointer_types']
        assert 'char*' in result['pointer_types']
        assert 'float*' in result['pointer_types']
    
    def test_macro_definitions_merge(self):
        """测试宏定义的合并"""
        tm = TypeManager()
        
        # 添加全局宏定义
        tm._global_macro_definitions['GLOBAL_MACRO'] = 1
        tm._global_macro_definitions['SHARED_MACRO'] = 10
        
        # 添加当前宏定义
        tm._current_macro_definitions['CURRENT_MACRO'] = 2
        tm._current_macro_definitions['SHARED_MACRO'] = 20  # 覆盖全局的
        
        result = tm.export_types('all')
        
        # 验证合并结果（当前覆盖全局）
        assert len(result['macro_definitions']) == 3
        assert result['macro_definitions']['GLOBAL_MACRO'] == 1
        assert result['macro_definitions']['CURRENT_MACRO'] == 2
        assert result['macro_definitions']['SHARED_MACRO'] == 20

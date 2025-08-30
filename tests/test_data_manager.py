import pytest
from unittest.mock import Mock, patch

from c_parser.core.data_manager import DataManager
from c_parser.core.type_manager import TypeManager


class TestDataManager:
    """DataManager测试类"""
    
    def test_initialization(self):
        """测试初始化"""
        # 测试默认初始化
        dm = DataManager()
        assert dm.type_manager is not None
        assert isinstance(dm.type_manager, TypeManager)
        
        # 测试自定义TypeManager
        custom_tm = TypeManager()
        dm = DataManager(custom_tm)
        assert dm.type_manager is custom_tm
        
        # 验证初始变量结构
        expected_structure = {
            'variables': [],
            'struct_vars': [],
            'pointer_vars': [],
            'array_vars': [],
        }
        assert dm.variables == expected_structure
    
    def test_add_basic_variable(self):
        """测试添加基本类型变量"""
        dm = DataManager()
        
        # 添加基本类型变量
        var_info = {
            'name': 'test_var',
            'type': 'int',
            'value': 42,
            'is_pointer': False,
            'array_size': None
        }
        
        dm.add_variable(var_info)
        
        assert len(dm.variables['variables']) == 1
        assert dm.variables['variables'][0] == var_info
        assert len(dm.variables['struct_vars']) == 0
        assert len(dm.variables['pointer_vars']) == 0
        assert len(dm.variables['array_vars']) == 0
    
    def test_add_pointer_variable(self):
        """测试添加指针变量"""
        dm = DataManager()
        
        # 添加指针变量
        var_info = {
            'name': 'ptr_var',
            'type': 'int',
            'value': None,
            'is_pointer': True,
            'array_size': None
        }
        
        dm.add_variable(var_info)
        
        assert len(dm.variables['pointer_vars']) == 1
        assert dm.variables['pointer_vars'][0] == var_info
        assert len(dm.variables['variables']) == 0
        assert len(dm.variables['struct_vars']) == 0
        assert len(dm.variables['array_vars']) == 0
    
    def test_add_array_variable(self):
        """测试添加数组变量"""
        dm = DataManager()
        
        # 添加数组变量
        var_info = {
            'name': 'array_var',
            'type': 'int',
            'value': [1, 2, 3],
            'is_pointer': False,
            'array_size': 3
        }
        
        dm.add_variable(var_info)
        
        assert len(dm.variables['array_vars']) == 1
        assert dm.variables['array_vars'][0] == var_info
        assert len(dm.variables['variables']) == 0
        assert len(dm.variables['struct_vars']) == 0
        assert len(dm.variables['pointer_vars']) == 0
    
    def test_add_struct_variable(self):
        """测试添加结构体变量"""
        dm = DataManager()
        
        # 模拟TypeManager的is_struct_type方法
        with patch.object(dm.type_manager, 'is_struct_type', return_value=True):
            var_info = {
                'name': 'struct_var',
                'type': 'Point',
                'value': {'x': 10, 'y': 20},
                'is_pointer': False,
                'array_size': None
            }
            
            dm.add_variable(var_info)
            
            assert len(dm.variables['struct_vars']) == 1
            assert dm.variables['struct_vars'][0] == var_info
            assert len(dm.variables['variables']) == 0
            assert len(dm.variables['pointer_vars']) == 0
            assert len(dm.variables['array_vars']) == 0
    
    def test_add_multiple_variables(self):
        """测试添加多个不同类型的变量"""
        dm = DataManager()
        
        # 模拟TypeManager的is_struct_type方法
        with patch.object(dm.type_manager, 'is_struct_type', side_effect=lambda t: t == 'Point'):
            variables = [
                {'name': 'int_var', 'type': 'int', 'value': 42, 'is_pointer': False, 'array_size': None},
                {'name': 'ptr_var', 'type': 'int', 'value': None, 'is_pointer': True, 'array_size': None},
                {'name': 'array_var', 'type': 'char', 'value': 'hello', 'is_pointer': False, 'array_size': 5},
                {'name': 'struct_var', 'type': 'Point', 'value': {'x': 1, 'y': 2}, 'is_pointer': False, 'array_size': None},
            ]
            
            for var_info in variables:
                dm.add_variable(var_info)
            
            assert len(dm.variables['variables']) == 1
            assert len(dm.variables['pointer_vars']) == 1
            assert len(dm.variables['array_vars']) == 1
            assert len(dm.variables['struct_vars']) == 1
    
    def test_get_type_info(self):
        """测试获取类型信息"""
        dm = DataManager()
        
        # 模拟TypeManager的export方法
        mock_global_info = {'types': {'int': {'size': 4}}, 'pointer_types': {}, 'macro_definitions': {}}
        mock_current_info = {'types': {'float': {'size': 4}}, 'pointer_types': {}, 'macro_definitions': {}}
        
        with patch.object(dm.type_manager, 'export_global_type_info', return_value=mock_global_info), \
             patch.object(dm.type_manager, 'export_current_type_info', return_value=mock_current_info):
            
            type_info = dm.get_type_info()
            
            assert type_info['global'] == mock_global_info
            assert type_info['current'] == mock_current_info
    
    def test_get_variables(self):
        """测试获取变量信息"""
        dm = DataManager()
        
        # 添加一些测试变量
        test_vars = [
            {'name': 'var1', 'type': 'int', 'value': 1, 'is_pointer': False, 'array_size': None},
            {'name': 'var2', 'type': 'int', 'value': None, 'is_pointer': True, 'array_size': None},
        ]
        
        for var_info in test_vars:
            dm.add_variable(var_info)
        
        variables = dm.get_variables()
        
        assert variables == dm.variables
        assert len(variables['variables']) == 1
        assert len(variables['pointer_vars']) == 1
    
    def test_get_all_data(self):
        """测试获取所有数据"""
        dm = DataManager()
        
        # 模拟TypeManager的find_types_by_kind方法
        mock_structs = [{'name': 'Point', 'fields': []}]
        mock_unions = [{'name': 'Data', 'fields': []}]
        mock_enums = [{'name': 'Color', 'values': []}]
        mock_typedefs = [{'name': 'u32', 'type': 'uint32_t'}]
        
        with patch.object(dm.type_manager, 'find_types_by_kind') as mock_find:
            mock_find.side_effect = lambda kind, scope: {
                'struct': mock_structs,
                'union': mock_unions,
                'enum': mock_enums,
                'typedef': mock_typedefs
            }[kind]
            
            # 添加一些测试变量
            dm.add_variable({'name': 'test_var', 'type': 'int', 'value': 42, 'is_pointer': False, 'array_size': None})
            
            all_data = dm.get_all_data()
            
            assert all_data['structs'] == mock_structs
            assert all_data['unions'] == mock_unions
            assert all_data['enums'] == mock_enums
            assert all_data['typedefs'] == mock_typedefs
            assert all_data['variables'] == dm.variables
    
    def test_clear(self):
        """测试清空数据"""
        dm = DataManager()
        
        # 添加一些测试数据
        dm.add_variable({'name': 'test_var', 'type': 'int', 'value': 42, 'is_pointer': False, 'array_size': None})
        
        # 验证数据已添加
        assert len(dm.variables['variables']) == 1
        
        # 清空数据
        dm.clear()
        
        # 验证数据已清空
        expected_structure = {
            'variables': [],
            'struct_vars': [],
            'pointer_vars': [],
            'array_vars': [],
        }
        assert dm.variables == expected_structure
    
    def test_variable_classification_edge_cases(self):
        """测试变量分类的边界情况"""
        dm = DataManager()
        
        # 测试同时是指针和数组的情况（数组优先级更高）
        var_info = {
            'name': 'ptr_array',
            'type': 'int',
            'value': None,
            'is_pointer': True,
            'array_size': 10
        }
        
        dm.add_variable(var_info)
        assert len(dm.variables['array_vars']) == 1
        assert len(dm.variables['pointer_vars']) == 0
        
        # 测试结构体指针
        with patch.object(dm.type_manager, 'is_struct_type', return_value=True):
            struct_ptr_info = {
                'name': 'struct_ptr',
                'type': 'Point',
                'value': None,
                'is_pointer': True,
                'array_size': None
            }
            
            dm.add_variable(struct_ptr_info)
            assert len(dm.variables['pointer_vars']) == 1
            assert len(dm.variables['struct_vars']) == 0
    
    def test_variable_info_structure(self):
        """测试变量信息结构的完整性"""
        dm = DataManager()
        
        # 测试完整的变量信息
        complete_var_info = {
            'name': 'complete_var',
            'type': 'int',
            'value': 42,
            'is_pointer': False,
            'array_size': None,
            'line': 10,
            'column': 5,
            'file': 'test.c',
            'comment': 'Test variable'
        }
        
        dm.add_variable(complete_var_info)
        
        # 验证信息被完整保存
        saved_var = dm.variables['variables'][0]
        assert saved_var == complete_var_info
        assert saved_var['name'] == 'complete_var'
        assert saved_var['line'] == 10
        assert saved_var['comment'] == 'Test variable'
    
    def test_type_manager_integration(self):
        """测试与TypeManager的集成"""
        dm = DataManager()
        
        # 测试TypeManager方法调用
        with patch.object(dm.type_manager, 'is_struct_type') as mock_is_struct, \
             patch.object(dm.type_manager, 'export_global_type_info') as mock_export_global, \
             patch.object(dm.type_manager, 'export_current_type_info') as mock_export_current, \
             patch.object(dm.type_manager, 'find_types_by_kind') as mock_find:
            
            # 调用方法触发TypeManager交互
            dm.add_variable({'name': 'test', 'type': 'Point', 'value': None, 'is_pointer': False, 'array_size': None})
            dm.get_type_info()
            dm.get_all_data()
            
            # 验证方法被调用
            mock_is_struct.assert_called_once_with('Point')
            mock_export_global.assert_called_once()
            mock_export_current.assert_called_once()
            mock_find.assert_called()

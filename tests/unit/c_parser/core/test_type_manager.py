import unittest
from typing import Dict, Any
from c_parser.core.type_manager import TypeManager

class TestTypeManagerBasic(unittest.TestCase):
    """测试 TypeManager 的基本功能"""
    
    def setUp(self):
        # TypeManager 已经在 BASIC_TYPES 和 TYPE_ALIASES 中定义了基本类型
        self.type_manager = TypeManager()

    def test_basic_type_check(self):
        """测试基本类型检查"""
        # 测试基本类型
        self.assertTrue(self.type_manager.is_basic_type('int'))
        self.assertTrue(self.type_manager.is_basic_type('char'))
        self.assertTrue(self.type_manager.is_basic_type('float'))
        self.assertTrue(self.type_manager.is_basic_type('double'))
        
        # 测试类型别名
        self.assertTrue(self.type_manager.is_basic_type('uint8_t'))
        self.assertTrue(self.type_manager.is_basic_type('int32_t'))
        
        # 测试非基本类型
        self.assertFalse(self.type_manager.is_basic_type('struct test'))
        self.assertFalse(self.type_manager.is_basic_type('enum color'))

    def test_type_aliases(self):
        """测试类型别名"""
        # 测试内置别名
        self.assertEqual(self.type_manager.get_real_type('u8'), 'uint8_t')
        self.assertEqual(self.type_manager.get_real_type('i32'), 'int32_t')
        
        # 测试自定义别名
        self.type_manager.add_typedef_type('my_int', 'int')
        self.assertEqual(self.type_manager.get_real_type('my_int'), 'int')

    def test_type_size_and_alignment(self):
        """测试类型大小和对齐"""
        # 测试基本类型的大小
        self.assertEqual(self.type_manager.get_type_size('char'), 1)
        self.assertEqual(self.type_manager.get_type_size('int'), 4)
        self.assertEqual(self.type_manager.get_type_size('long'), 8)
        
        # 测试基本类型的对齐
        self.assertEqual(self.type_manager.get_type_alignment('char'), 1)
        self.assertEqual(self.type_manager.get_type_alignment('int'), 4)
        self.assertEqual(self.type_manager.get_type_alignment('long'), 8)

    def test_complex_type_aliases(self):
        """测试复杂类型别名"""
        # 测试多级别类型别名
        self.type_manager.add_typedef_type('int_alias', 'int')
        self.type_manager.add_typedef_type('my_int', 'int_alias')
        self.type_manager.add_typedef_type('number', 'my_int')
        
        self.assertEqual(self.type_manager.get_real_type('number'), 'int')
        self.assertTrue(self.type_manager.is_basic_type('number'))

    def test_type_compatibility(self):
        """测试类型兼容性"""
        # 测试基本类型兼容性
        self.assertTrue(self.type_manager.is_compatible_types('int', 'int32_t'))
        self.assertTrue(self.type_manager.is_compatible_types('unsigned int', 'uint32_t'))
        self.assertFalse(self.type_manager.is_compatible_types('int', 'char'))
        
        # 测试类型别名兼容性
        self.type_manager.add_typedef_type('my_int', 'int')
        self.assertTrue(self.type_manager.is_compatible_types('my_int', 'int'))
        self.assertTrue(self.type_manager.is_compatible_types('my_int', 'int32_t'))


class TestTypeManagerStruct(unittest.TestCase):
    """测试结构体相关功能"""
    
    def setUp(self):
        self.type_manager = TypeManager()
        # 创建一个测试结构体
        self.struct_info = {
            'kind': 'struct',
            'name': 'test_struct',
            'fields': [
                {'name': 'a', 'type': 'int'},
                {'name': 'b', 'type': 'char'},
                {'name': 'c', 'type': 'float'}
            ],
            'size': 12,
            'alignment': 4
        }
        self.type_manager.add_struct_type('test_struct', self.struct_info)

    def test_struct_type_check(self):
        """测试结构体类型检查"""
        self.assertTrue(self.type_manager.is_struct_type('test_struct'))
        self.assertTrue(self.type_manager.is_struct_type('struct test_struct'))
        self.assertFalse(self.type_manager.is_struct_type('int'))

    def test_struct_info(self):
        """测试结构体信息获取"""
        info = self.type_manager.get_struct_info('test_struct')
        self.assertEqual(info['size'], 12)
        self.assertEqual(info['alignment'], 4)
        self.assertEqual(len(info['fields']), 3)

    def test_field_offset(self):
        """测试字段偏移量计算"""
        # int 字段应该在偏移量 0
        self.assertEqual(self.type_manager.calculate_field_offset('test_struct', 'a'), 0)
        # char 字段应该在偏移量 4
        self.assertEqual(self.type_manager.calculate_field_offset('test_struct', 'b'), 4)
        # float 字段应该在偏移量 8
        self.assertEqual(self.type_manager.calculate_field_offset('test_struct', 'c'), 8)

    def test_nested_struct(self):
        """测试嵌套结构体"""
        # 创建嵌套结构体
        inner_struct = {
            'kind': 'struct',
            'name': 'inner',
            'fields': [{'name': 'x', 'type': 'int'}],
            'size': 4,
            'alignment': 4
        }
        
        outer_struct = {
            'kind': 'struct',
            'name': 'outer',
            'fields': [
                {'name': 'inner_field', 'type': 'inner'},
                {'name': 'value', 'type': 'int'}
            ],
            'size': 8,
            'alignment': 4
        }
        
        self.type_manager.add_struct_type('inner', inner_struct)
        self.type_manager.add_struct_type('outer', outer_struct)
        
        # 验证嵌套结构体的字段偏移量
        self.assertEqual(
            self.type_manager.calculate_field_offset('outer', 'inner_field'),
            0
        )
        self.assertEqual(
            self.type_manager.calculate_field_offset('outer', 'value'),
            4
        )

    def test_struct_with_array(self):
        """测试带数组的结构体"""
        struct_info = {
            'kind': 'struct',
            'name': 'array_struct',
            'fields': [
                {'name': 'arr', 'type': 'int', 'array_dims': [3]},
                {'name': 'value', 'type': 'char'}
            ]
        }
        self.type_manager.add_struct_type('array_struct', struct_info)
        
        # 验证数组字段的解析
        type_info = self.type_manager.resolve_type('array_struct')
        self.assertTrue(type_info['is_struct'])
        field_info = self.type_manager.get_field_info('array_struct', 'arr')
        self.assertEqual(field_info.get('array_dims'), [3])


class TestTypeManagerEnum(unittest.TestCase):
    """测试枚举相关功能"""
    
    def setUp(self):
        self.type_manager = TypeManager()
        # 创建一个测试枚举
        self.enum_values = {
            'RED': 0,
            'GREEN': 1,
            'BLUE': 2
        }
        self.type_manager.add_enum_type('color', self.enum_values)

    def test_enum_type_check(self):
        """测试枚举类型检查"""
        self.assertTrue(self.type_manager.is_enum_type('color'))
        self.assertTrue(self.type_manager.is_enum_type('enum color'))
        self.assertFalse(self.type_manager.is_enum_type('int'))

    def test_enum_values(self):
        """测试枚举值获取"""
        values = self.type_manager.get_enum_values('color')
        self.assertEqual(values['RED'], 0)
        self.assertEqual(values['GREEN'], 1)
        self.assertEqual(values['BLUE'], 2)

    def test_enum_value(self):
        """测试单个枚举值获取"""
        self.assertEqual(self.type_manager.get_enum_value('color', 'RED'), 0)
        self.assertEqual(self.type_manager.get_enum_value('color', 'GREEN'), 1)
        self.assertIsNone(self.type_manager.get_enum_value('color', 'YELLOW'))

    def test_enum_with_expressions(self):
        """测试带表达式的枚举"""
        enum_values = {
            'A': 1,
            'B': '(A + 1)',  # 表达式值
            'C': '(B * 2)',  # 依赖前面的值
            'MAX': '0xFF'    # 十六进制值
        }
        self.type_manager.add_enum_type('complex_enum', enum_values)
        
        values = self.type_manager.get_enum_values('complex_enum')
        self.assertEqual(values['A'], 1)
        self.assertEqual(values['B'], '(A + 1)')
        self.assertEqual(values['C'], '(B * 2)')

    def test_enum_scope(self):
        """测试枚举作用域"""
        # 添加全局枚举
        global_enum = {'RED': 0, 'GREEN': 1}
        global_info = {
            'enum_types': ['colors'],
            'enum_info': {'colors': {'values': global_enum}}
        }
        self.type_manager.merge_type_info(global_info, to_global=True)
        
        # 添加局部枚举
        local_enum = {'SMALL': 0, 'MEDIUM': 1}
        self.type_manager.add_enum_type('sizes', local_enum)
        
        # 验证作用域
        self.assertEqual(self.type_manager.get_type_scope('colors'), 'global')
        self.assertEqual(self.type_manager.get_type_scope('sizes'), 'file')


class TestTypeManagerTypeInfo(unittest.TestCase):
    """测试类型信息管理功能"""
    
    def setUp(self):
        self.type_manager = TypeManager()

    def test_type_info_export_import(self):
        """测试类型信息的导出和导入"""
        # 添加一些测试类型
        self.type_manager.add_typedef_type('my_int', 'int')
        self.type_manager.add_struct_type('test_struct', {
            'kind': 'struct',
            'name': 'test_struct',
            'fields': [{'name': 'x', 'type': 'int'}]
        })
        
        # 导出类型信息
        type_info = self.type_manager.export_type_info()
        
        # 创建新的类型管理器并导入类型信息
        new_manager = TypeManager(type_info)
        
        # 验证类型信息是否正确导入
        self.assertTrue(new_manager.is_typedef_type('my_int'))
        self.assertTrue(new_manager.is_struct_type('test_struct'))

    def test_type_info_merge(self):
        """测试类型信息合并"""
        # 创建要合并的类型信息
        other_info = {
            'typedef_types': {'my_char': 'char'},
            'struct_types': ['point'],
            'struct_info': {
                'point': {
                    'kind': 'struct',
                    'name': 'point',
                    'fields': [
                        {'name': 'x', 'type': 'int'},
                        {'name': 'y', 'type': 'int'}
                    ]
                }
            }
        }
        
        # 合并类型信息
        self.type_manager.merge_type_info(other_info, to_global=True)
        
        # 验证合并结果
        self.assertTrue(self.type_manager.is_typedef_type('my_char'))
        self.assertTrue(self.type_manager.is_struct_type('point'))


class TestTypeManagerValidation(unittest.TestCase):
    """测试类型验证功能"""
    
    def setUp(self):
        self.type_manager = TypeManager()

    def test_validate_struct_info(self):
        """测试结构体信息验证"""
        # 有效的结构体信息
        valid_struct = {
            'kind': 'struct',
            'name': 'test',
            'fields': [
                {'name': 'x', 'type': 'int'},
                {'name': 'y', 'type': 'int'}
            ]
        }
        self.assertTrue(self.type_manager.validate_type_info(valid_struct))
        
        # 无效的结构体信息（缺少字段）
        invalid_struct = {
            'kind': 'struct',
            'name': 'test'
        }
        self.assertFalse(self.type_manager.validate_type_info(invalid_struct))

    def test_validate_enum_info(self):
        """测试枚举信息验证"""
        # 有效的枚举信息
        valid_enum = {
            'kind': 'enum',
            'name': 'color',
            'values': {'RED': 0, 'GREEN': 1}
        }
        self.assertTrue(self.type_manager.validate_type_info(valid_enum))
        
        # 无效的枚举信息（values 不是字典）
        invalid_enum = {
            'kind': 'enum',
            'name': 'color',
            'values': [0, 1, 2]
        }
        self.assertFalse(self.type_manager.validate_type_info(invalid_enum))


class TestTypeManagerUnion(unittest.TestCase):
    """测试联合体相关功能"""
    
    def setUp(self):
        self.type_manager = TypeManager()
        # 创建一个测试联合体
        self.union_info = {
            'kind': 'union',
            'name': 'test_union',
            'fields': [
                {'name': 'i', 'type': 'int'},
                {'name': 'f', 'type': 'float'},
                {'name': 'c', 'type': 'char'}
            ],
            'size': 4,  # 最大字段的大小
            'alignment': 4
        }
        self.type_manager.add_union_type('test_union', self.union_info)

    def test_union_type_check(self):
        """测试联合体类型检查"""
        self.assertTrue(self.type_manager.is_union_type('test_union'))
        self.assertTrue(self.type_manager.is_union_type('union test_union'))
        self.assertFalse(self.type_manager.is_union_type('int'))

    def test_union_info(self):
        """测试联合体信息获取"""
        info = self.type_manager.get_union_info('test_union')
        self.assertEqual(info['size'], 4)
        self.assertEqual(info['alignment'], 4)
        self.assertEqual(len(info['fields']), 3)

    def test_union_field_offset(self):
        """测试联合体字段偏移量"""
        # 联合体所有字段的偏移量都应该是0
        for field_name in ['i', 'f', 'c']:
            field_info = self.type_manager.get_field_info('test_union', field_name)
            self.assertEqual(field_info['offset'], 0)


class TestTypeManagerPointer(unittest.TestCase):
    """测试指针相关功能"""
    
    def setUp(self):
        self.type_manager = TypeManager()

    def test_pointer_type_check(self):
        """测试指针类型检查"""
        # 直接指针语法
        self.assertTrue(self.type_manager.is_pointer_type('int*'))
        self.assertTrue(self.type_manager.is_pointer_type('char**'))
        
        # typedef 指针类型
        self.type_manager.add_pointer_type('int_ptr', True)
        self.assertTrue(self.type_manager.is_pointer_type('int_ptr'))

    def test_pointer_size(self):
        """测试指针大小"""
        # 所有指针类型的大小都应该是8（64位系统）
        self.assertEqual(self.type_manager.get_type_size('int*'), 8)
        self.assertEqual(self.type_manager.get_type_size('char**'), 8)
        self.assertEqual(self.type_manager.get_type_size('void*'), 8)

    def test_pointer_compatibility(self):
        """测试指针兼容性"""
        # void* 可以与任何指针类型兼容
        self.assertTrue(self.type_manager.is_compatible_types('void*', 'int*'))
        self.assertTrue(self.type_manager.is_compatible_types('int*', 'void*'))
        
        # 相同类型的指针兼容
        self.assertTrue(self.type_manager.is_compatible_types('int*', 'int*'))
        
        # 不同类型的指针不兼容
        self.assertFalse(self.type_manager.is_compatible_types('int*', 'char*'))
        
        # 不同级别的指针不兼容
        self.assertFalse(self.type_manager.is_compatible_types('int*', 'int**'))

    def test_complex_pointer_types(self):
        """测试复杂指针类型"""
        # 函数指针
        self.type_manager.add_pointer_type('func_ptr', True)  # void (*)(int)
        
        # 指向数组的指针
        self.assertTrue(self.type_manager.is_pointer_type('int (*)[10]'))
        
        # 多级指针
        self.assertTrue(self.type_manager.is_pointer_type('int***'))
        self.assertEqual(self.type_manager.get_type_size('int***'), 8)

    def test_pointer_to_incomplete_type(self):
        """测试指向不完整类型的指针"""
        # 前向声明的结构体指针
        struct_info = {'kind': 'struct', 'name': 'forward_struct'}
        self.type_manager.add_struct_type('forward_struct', struct_info)
        
        # 指向不完整类型的指针仍然是有效的
        self.assertTrue(self.type_manager.is_pointer_type('forward_struct*'))
        self.assertEqual(self.type_manager.get_type_size('forward_struct*'), 8)


class TestTypeManagerTypeHierarchy(unittest.TestCase):
    """测试类型层次结构功能"""
    
    def setUp(self):
        self.type_manager = TypeManager()
        
        # 添加测试用的结构体类型
        self.type_manager.add_struct_type('node', {
            'kind': 'struct',
            'name': 'node',
            'fields': [
                {'name': 'data', 'type': 'int'},
                {'name': 'next', 'type': 'node*'}
            ]
        })
        
        # 添加嵌套结构体
        self.type_manager.add_struct_type('inner', {
            'kind': 'struct',
            'name': 'inner',
            'fields': [{'name': 'x', 'type': 'int'}]
        })
        
        self.type_manager.add_struct_type('outer', {
            'kind': 'struct',
            'name': 'outer',
            'fields': [
                {'name': 'inner_field', 'type': 'inner'},
                {'name': 'value', 'type': 'int'}
            ]
        })

    def test_type_hierarchy(self):
        """测试类型层次结构获取"""
        # 添加 line 结构体定义
        self.type_manager.add_struct_type('line', {
            'kind': 'struct',
            'name': 'line',
            'fields': [
                {'name': 'start', 'type': 'point'},
                {'name': 'end', 'type': 'point'}
            ]
        })
        
        hierarchy = self.type_manager.get_type_hierarchy('line')
        
        # 验证基本结构
        self.assertEqual(hierarchy['type'], 'struct')
        self.assertEqual(len(hierarchy['fields']), 2)

    def test_type_dependencies(self):
        """测试类型依赖关系"""
        deps = self.type_manager.get_type_dependencies('outer')
        self.assertIn('inner', deps)
        self.assertIn('int', deps)

    def test_circular_dependency(self):
        """测试循环依赖"""
        hierarchy = self.type_manager.get_type_hierarchy('node')
        next_field = next(f for f in hierarchy['fields'] if f['field_name'] == 'next')
        self.assertEqual(next_field['type'], 'pointer')

    def test_complex_type_dependencies(self):
        """测试复杂类型依赖"""
        deps = self.type_manager.get_type_dependencies('outer')
        self.assertIn('inner', deps)
        self.assertIn('int', deps)


class TestTypeManagerMetadata(unittest.TestCase):
    """测试类型元数据功能"""
    
    def setUp(self):
        self.type_manager = TypeManager()
        
        # 添加测试结构体，包含完整的元数据
        struct_info = {
            'kind': 'struct',
            'name': 'test_struct',
            'fields': [{'name': 'x', 'type': 'int'}],
            'location': {'file': 'test.h', 'line': 10},
            'comment': 'Test structure',
            'attributes': {'packed': True},
            'details': {
                'packed': True,
                'alignment': 4,
                'visibility': 'public'
            }
        }
        self.type_manager.add_struct_type('test_struct', struct_info)
        
        # 更新类型信息
        self.type_manager.type_info['test_struct'] = struct_info

    def test_type_attributes(self):
        """测试类型属性"""
        attrs = self.type_manager.get_type_attributes('test_struct')
        self.assertTrue(attrs.get('packed'))

    def test_type_metadata(self):
        """测试类型元数据"""
        location = self.type_manager.get_type_location('test_struct')
        self.assertEqual(location, {'file': 'test.h', 'line': 10})

    def test_type_status(self):
        """测试类型状态"""
        status = self.type_manager.get_type_status('test_struct')
        self.assertTrue(status['is_complete'])
        self.assertTrue(status['is_defined'])
        self.assertEqual(status['scope'], 'file')

    def test_type_summary(self):
        """测试类型摘要"""
        summary = self.type_manager.get_type_summary('test_struct')
        self.assertEqual(summary['category'], 'struct')
        self.assertTrue(summary['status']['is_defined'])
        self.assertEqual(summary['status']['scope'], 'file')

    def test_type_qualifiers(self):
        """测试类型限定符"""
        type_str = 'const volatile int* restrict'
        parsed = self.type_manager.parse_type_string(type_str)
        
        self.assertTrue(parsed['is_const'])
        self.assertTrue(parsed['is_volatile'])
        self.assertTrue(parsed['is_restrict'])
        self.assertEqual(parsed['pointer_level'], 1)
        self.assertEqual(parsed['base_type'], 'int')

    def test_type_attributes(self):
        """测试类型属性"""
        struct_info = {
            'kind': 'struct',
            'name': 'packed_struct',
            'fields': [{'name': 'x', 'type': 'char'}],
            'attributes': {
                'packed': True,
                'aligned': 1,
                'deprecated': True
            }
        }
        self.type_manager.add_struct_type('packed_struct', struct_info)
        
        attrs = self.type_manager.get_type_attributes('packed_struct')
        self.assertTrue(attrs['packed'])
        self.assertEqual(attrs['aligned'], 1)
        self.assertTrue(attrs['deprecated'])


class TestTypeManagerScope(unittest.TestCase):
    """测试类型作用域功能"""
    
    def setUp(self):
        self.type_manager = TypeManager()

    def test_scope_management(self):
        """测试作用域管理"""
        # 添加全局类型
        global_info = {
            'typedef_types': {'global_int': 'int'},
            'struct_types': ['global_struct'],
            'struct_info': {
                'global_struct': {
                    'kind': 'struct',
                    'name': 'global_struct',
                    'fields': []
                }
            }
        }
        self.type_manager.merge_type_info(global_info, to_global=True)
        
        # 添加文件作用域类型
        self.type_manager.add_typedef_type('file_int', 'int')
        
        # 测试作用域判断
        self.assertEqual(self.type_manager.get_type_scope('global_int'), 'global')
        self.assertEqual(self.type_manager.get_type_scope('file_int'), 'file')
        self.assertEqual(self.type_manager.get_type_scope('int'), 'global')
        self.assertEqual(self.type_manager.get_type_scope('unknown_type'), 'unknown')

    def test_scope_reset(self):
        """测试作用域重置"""
        # 添加一些类型
        self.type_manager.add_typedef_type('file_type', 'int')
        self.type_manager.add_struct_type('file_struct', {'kind': 'struct', 'name': 'file_struct', 'fields': []})
        
        # 重置当前文件作用域
        self.type_manager.reset_current_type_info()
        
        # 验证重置结果
        self.assertFalse(self.type_manager.is_typedef_type('file_type'))
        self.assertFalse(self.type_manager.is_struct_type('file_struct'))


if __name__ == '__main__':
    unittest.main() 
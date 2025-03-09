import unittest
from typing import Dict, Any
from c_parser.core.type_manager import TypeManager

class TestTypeManagerBasic(unittest.TestCase):
    """测试 TypeManager 的基本功能"""
    
    def setUp(self):
        # 初始化 TypeManager 实例
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
        typedef_info = {
            'kind': 'typedef',
            'name': 'my_int',
            'base_type': 'int'
        }
        self.type_manager.register_type('my_int', typedef_info)
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
        self.type_manager.register_type('int_alias', {
            'kind': 'typedef',
            'name': 'int_alias',
            'base_type': 'int'
        })
        
        self.type_manager.register_type('my_int', {
            'kind': 'typedef',
            'name': 'my_int',
            'base_type': 'int_alias'
        })
        
        self.type_manager.register_type('number', {
            'kind': 'typedef',
            'name': 'number',
            'base_type': 'my_int'
        })
        
        self.assertEqual(self.type_manager.get_real_type('number'), 'int')
        self.assertTrue(self.type_manager.is_basic_type('number'))

    def test_type_compatibility(self):
        """测试类型兼容性"""
        # 测试基本类型兼容性
        self.assertTrue(self.type_manager.is_compatible_types('int', 'int32_t'))
        self.assertTrue(self.type_manager.is_compatible_types('unsigned int', 'uint32_t'))
        self.assertFalse(self.type_manager.is_compatible_types('int', 'char'))
        
        # 测试类型别名兼容性
        self.type_manager.register_type('my_int', {
            'kind': 'typedef',
            'name': 'my_int',
            'base_type': 'int'
        })
        self.assertTrue(self.type_manager.is_compatible_types('my_int', 'int'))
        self.assertTrue(self.type_manager.is_compatible_types('my_int', 'int32_t'))

    def test_type_category(self):
        """测试类型分类"""
        # 测试基本类型分类
        self.assertEqual(self.type_manager.get_type_category('int'), 'basic')
        self.assertEqual(self.type_manager.get_type_category('float'), 'basic')
        
        # 添加结构体类型并测试
        struct_info = {
            'kind': 'struct',
            'name': 'test_struct',
            'fields': [{'name': 'x', 'type': 'int'}]
        }
        self.type_manager.register_type('test_struct', struct_info)
        self.assertEqual(self.type_manager.get_type_category('test_struct'), 'struct')
        
        # 测试指针类型分类
        self.assertEqual(self.type_manager.get_type_category('int*'), 'pointer')
        
        # 测试未知类型分类
        self.assertEqual(self.type_manager.get_type_category('unknown_type'), 'unknown')

    def test_parse_type_string(self):
        """测试类型字符串解析"""
        # 测试简单类型
        result = self.type_manager.parse_type_string('int')
        self.assertEqual(result['base_type'], 'int')
        self.assertEqual(result['pointer_level'], 0)
        self.assertFalse(result['is_const'])
        
        # 测试带限定符的类型
        result = self.type_manager.parse_type_string('const int')
        self.assertEqual(result['base_type'], 'int')
        self.assertTrue(result['is_const'])
        
        # 测试指针类型
        result = self.type_manager.parse_type_string('int*')
        self.assertEqual(result['base_type'], 'int')
        self.assertEqual(result['pointer_level'], 1)
        
        # 测试复杂类型
        result = self.type_manager.parse_type_string('const volatile int* restrict')
        self.assertEqual(result['base_type'], 'int')
        self.assertEqual(result['pointer_level'], 1)
        self.assertTrue(result['is_const'])
        self.assertTrue(result['is_volatile'])
        self.assertTrue(result['is_restrict'])
        
        # 测试带存储类的类型
        result = self.type_manager.parse_type_string('static int')
        self.assertEqual(result['base_type'], 'int')
        self.assertEqual(result['storage_class'], 'static')
        
        # 测试数组类型
        result = self.type_manager.parse_type_string('int[10]')
        self.assertEqual(result['base_type'], 'int')
        self.assertEqual(result['array_dims'], [10])

    def test_resolve_type(self):
        """测试类型解析"""
        # 测试基本类型解析
        type_info = self.type_manager.resolve_type('int')
        self.assertEqual(type_info['type'], 'int')
        self.assertEqual(type_info['base_type'], 'int')
        self.assertTrue(type_info['is_basic'])
        self.assertFalse(type_info['is_pointer'])
        
        # 测试指针类型解析
        type_info = self.type_manager.resolve_type('int*')
        self.assertEqual(type_info['type'], 'int*')
        self.assertEqual(type_info['base_type'], 'int')
        self.assertTrue(type_info['is_pointer'])
        self.assertEqual(type_info['pointer_level'], 1)
        
        # 测试多级指针类型解析
        type_info = self.type_manager.resolve_type('int**')
        self.assertEqual(type_info['base_type'], 'int')
        self.assertEqual(type_info['pointer_level'], 2)
        
        # 添加结构体类型并测试解析
        struct_info = {
            'kind': 'struct',
            'name': 'point',
            'fields': [
                {'name': 'x', 'type': 'int'},
                {'name': 'y', 'type': 'int'}
            ]
        }
        self.type_manager.register_type('point', struct_info)
        
        type_info = self.type_manager.resolve_type('point')
        self.assertEqual(type_info['base_type'], 'point')
        self.assertTrue(type_info['is_struct'])
        self.assertFalse(type_info['is_basic'])

    def test_printf_format(self):
        """测试 printf 格式化字符串获取"""
        # 测试基本类型的格式化字符串
        self.assertEqual(self.type_manager.get_printf_format('int'), '%d')
        self.assertEqual(self.type_manager.get_printf_format('char'), '"%c"')
        self.assertEqual(self.type_manager.get_printf_format('float'), '%.6f')
        
        # 测试指针类型的格式化字符串
        self.assertEqual(self.type_manager.get_printf_format('int*'), '"0x%p"')
        self.assertEqual(self.type_manager.get_printf_format('void*'), '"0x%p"')
        
        # 添加枚举类型并测试格式化字符串
        enum_info = {
            'kind': 'enum',
            'name': 'color',
            'values': {'RED': 0, 'GREEN': 1, 'BLUE': 2}
        }
        self.type_manager.register_type('color', enum_info)
        self.assertEqual(self.type_manager.get_printf_format('color'), '%d')
        
        # 测试类型别名的格式化字符串
        self.type_manager.register_type('my_int', {
            'kind': 'typedef',
            'name': 'my_int',
            'base_type': 'int'
        })
        self.assertEqual(self.type_manager.get_printf_format('my_int'), '%d')


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
        self.type_manager.register_type('test_struct', self.struct_info)

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
        
        self.type_manager.register_type('inner', inner_struct)
        self.type_manager.register_type('outer', outer_struct)
        
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
        self.type_manager.register_type('array_struct', struct_info)
        
        # 验证数组字段的解析
        type_info = self.type_manager.resolve_type('array_struct')
        self.assertTrue(type_info['is_struct'])
        field_info = self.type_manager.get_field_info('array_struct', 'arr')
        self.assertEqual(field_info.get('array_dims'), [3])

    def test_field_info(self):
        """测试字段信息获取"""
        field_info = self.type_manager.get_field_info('test_struct', 'a')
        self.assertEqual(field_info['name'], 'a')
        self.assertEqual(field_info['type'], 'int')
        self.assertEqual(field_info['offset'], 0)
        
        field_info = self.type_manager.get_field_info('test_struct', 'b')
        self.assertEqual(field_info['name'], 'b')
        self.assertEqual(field_info['type'], 'char')
        self.assertEqual(field_info['offset'], 4)

    def test_anonymous_struct(self):
        """测试匿名结构体"""
        anon_struct = {
            'kind': 'struct',
            'name': 'anonymous_1',
            'fields': [{'name': 'x', 'type': 'int'}],
            'is_anonymous': True
        }
        self.type_manager.register_type('anonymous_1', anon_struct)
        
        # 验证匿名结构体检查
        self.assertTrue(self.type_manager.is_anonymous_type('anonymous_1'))
        self.assertFalse(self.type_manager.is_anonymous_type('test_struct'))

    def test_struct_with_bit_fields(self):
        """测试带位域的结构体"""
        struct_info = {
            'kind': 'struct',
            'name': 'bit_field_struct',
            'fields': [
                {'name': 'a', 'type': 'int', 'bit_field': 1},
                {'name': 'b', 'type': 'int', 'bit_field': 2},
                {'name': 'c', 'type': 'int', 'bit_field': 3}
            ]
        }
        self.type_manager.register_type('bit_field_struct', struct_info)
        
        # 验证位域字段
        field_info = self.type_manager.get_field_info('bit_field_struct', 'a')
        self.assertEqual(field_info['bit_field'], 1)
        
        field_info = self.type_manager.get_field_info('bit_field_struct', 'b')
        self.assertEqual(field_info['bit_field'], 2)

    def test_packed_struct(self):
        """测试紧凑结构体"""
        packed_struct = {
            'kind': 'struct',
            'name': 'packed_struct',
            'fields': [
                {'name': 'a', 'type': 'char'},
                {'name': 'b', 'type': 'int'},
                {'name': 'c', 'type': 'char'}
            ],
            'packed': True,
            'alignment': 1  # 紧凑结构体对齐为1
        }
        self.type_manager.register_type('packed_struct', packed_struct)
        
        # 验证紧凑结构体
        self.assertTrue(self.type_manager.is_packed_type('packed_struct'))
        self.assertEqual(self.type_manager.get_type_alignment('packed_struct'), 1)
        
        # 在紧凑结构体中，字段应该紧密排列，没有填充
        self.assertEqual(self.type_manager.calculate_field_offset('packed_struct', 'a'), 0)
        self.assertEqual(self.type_manager.calculate_field_offset('packed_struct', 'b'), 1)  # 紧接着a
        self.assertEqual(self.type_manager.calculate_field_offset('packed_struct', 'c'), 5)  # 紧接着b (1+4)


class TestTypeManagerEnum(unittest.TestCase):
    """测试枚举相关功能"""
    
    def setUp(self):
        self.type_manager = TypeManager()
        # 创建一个测试枚举
        self.enum_info = {
            'kind': 'enum',
            'name': 'color',
            'values': {
                'RED': 0,
                'GREEN': 1,
                'BLUE': 2
            }
        }
        self.type_manager.register_type('color', self.enum_info)

    def test_enum_type_check(self):
        """测试枚举类型检查"""
        self.assertTrue(self.type_manager.is_enum_type('color'))
        self.assertTrue(self.type_manager.is_enum_type('enum color'))
        self.assertFalse(self.type_manager.is_enum_type('int'))

    def test_enum_values(self):
        """测试枚举值获取"""
        values = self.type_manager.get_enum_values('color')
        self.assertEqual(values['color']['RED'], 0)
        self.assertEqual(values['color']['GREEN'], 1)
        self.assertEqual(values['color']['BLUE'], 2)

    def test_enum_value(self):
        """测试单个枚举值获取"""
        self.assertEqual(self.type_manager.get_enum_value('color', 'RED'), 0)
        self.assertEqual(self.type_manager.get_enum_value('color', 'GREEN'), 1)
        self.assertIsNone(self.type_manager.get_enum_value('color', 'YELLOW'))

    def test_enum_with_expressions(self):
        """测试带表达式的枚举"""
        enum_info = {
            'kind': 'enum',
            'name': 'complex_enum',
            'values': {
                'A': 1,
                'B': '(A + 1)',  # 表达式值
                'C': '(B * 2)',  # 依赖前面的值
                'MAX': '0xFF'    # 十六进制值
            }
        }
        self.type_manager.register_type('complex_enum', enum_info)
        
        values = self.type_manager.get_enum_values('complex_enum')
        self.assertEqual(values['complex_enum']['A'], 1)
        self.assertEqual(values['complex_enum']['B'], '(A + 1)')
        self.assertEqual(values['complex_enum']['C'], '(B * 2)')

    def test_enum_scope(self):
        """测试枚举作用域"""
        # 添加全局枚举
        global_enum = {
            'kind': 'enum',
            'name': 'colors',
            'values': {'RED': 0, 'GREEN': 1}
        }
        self.type_manager.merge_type_info({'types': [global_enum]}, to_global=True)
        
        # 添加局部枚举
        local_enum = {
            'kind': 'enum',
            'name': 'sizes',
            'values': {'SMALL': 0, 'MEDIUM': 1}
        }
        self.type_manager.register_type('sizes', local_enum)
        
        # 验证作用域
        self.assertEqual(self.type_manager.get_type_scope('colors'), 'global')
        self.assertEqual(self.type_manager.get_type_scope('sizes'), 'file')

    def test_enum_type_info(self):
        """测试枚举类型信息"""
        enum_info = self.type_manager.get_enum_info('color')
        self.assertEqual(enum_info['kind'], 'enum')
        self.assertEqual(enum_info['name'], 'color')
        self.assertEqual(len(enum_info['values']), 3)

    def test_enum_in_typedef(self):
        """测试枚举在typedef中的使用"""
        # 创建一个typedef，基类型是枚举
        typedef_info = {
            'kind': 'typedef',
            'name': 'color_t',
            'base_type': 'color'
        }
        self.type_manager.register_type('color_t', typedef_info)
        
        # 验证typedef的基类型是枚举
        self.assertTrue(self.type_manager.is_enum_type('color_t'))
        self.assertEqual(self.type_manager.get_real_type('color_t'), 'color')
        
        # 通过typedef获取枚举值
        self.assertEqual(self.type_manager.get_enum_value('color_t', 'RED'), 0)

    def test_anonymous_enum(self):
        """测试匿名枚举"""
        anon_enum = {
            'kind': 'enum',
            'name': 'anonymous_enum_1',
            'values': {'ONE': 1, 'TWO': 2},
            'is_anonymous': True
        }
        self.type_manager.register_type('anonymous_enum_1', anon_enum)
        
        # 验证匿名枚举
        self.assertTrue(self.type_manager.is_anonymous_type('anonymous_enum_1'))
        self.assertEqual(self.type_manager.get_enum_value('anonymous_enum_1', 'ONE'), 1)

    def test_enum_printf_format(self):
        """测试枚举的printf格式"""
        # 枚举应该使用%d格式
        self.assertEqual(self.type_manager.get_printf_format('color'), '%d')
        
        # 通过typedef的枚举也应该使用%d格式
        typedef_info = {
            'kind': 'typedef',
            'name': 'color_t',
            'base_type': 'color'
        }
        self.type_manager.register_type('color_t', typedef_info)
        self.assertEqual(self.type_manager.get_printf_format('color_t'), '%d')


class TestTypeManagerTypeInfo(unittest.TestCase):
    """测试类型信息管理功能"""
    
    def setUp(self):
        self.type_manager = TypeManager()

    def test_type_info_export_import(self):
        """测试类型信息的导出和导入"""
        # 添加一些测试类型
        self.type_manager.register_type('my_int', {
            'kind': 'typedef',
            'name': 'my_int',
            'base_type': 'int'
        })
        
        self.type_manager.register_type('test_struct', {
            'kind': 'struct',
            'name': 'test_struct',
            'fields': [{'name': 'x', 'type': 'int'}]
        })
        
        # 导出类型信息
        type_info = self.type_manager.export_types()
        
        # 创建新的类型管理器并导入类型信息
        new_manager = TypeManager(type_info)
        
        # 验证类型信息是否正确导入
        self.assertTrue(new_manager.is_typedef_type('my_int'))
        self.assertTrue(new_manager.is_struct_type('test_struct'))

    def test_type_info_export_formats(self):
        """测试不同格式的类型信息导出"""
        # 添加一些测试类型
        self.type_manager.register_type('test_struct', {
            'kind': 'struct',
            'name': 'test_struct',
            'fields': [{'name': 'x', 'type': 'int'}]
        })
        
        self.type_manager.register_type('test_enum', {
            'kind': 'enum',
            'name': 'test_enum',
            'values': {'A': 1, 'B': 2}
        })
        
        # 导出统一格式
        unified_info = self.type_manager.export_types()
        self.assertIn('types', unified_info)
        
        # 导出分类格式
        categorized_info = self.type_manager.export_type_info()
        self.assertIn('struct_types', categorized_info)
        self.assertIn('enum_types', categorized_info)

    def test_type_info_merge(self):
        """测试类型信息合并"""
        # 创建要合并的类型信息
        other_info = {
            'types': [
                {
                    'kind': 'typedef',
                    'name': 'my_char',
                    'base_type': 'char'
                },
                {
                    'kind': 'struct',
                    'name': 'point',
                    'fields': [
                        {'name': 'x', 'type': 'int'},
                        {'name': 'y', 'type': 'int'}
                    ]
                }
            ]
        }
        
        # 合并类型信息
        self.type_manager.merge_type_info(other_info, to_global=True)
        
        # 验证合并结果
        self.assertTrue(self.type_manager.is_typedef_type('my_char'))
        self.assertTrue(self.type_manager.is_struct_type('point'))

    def test_type_info_scope(self):
        """测试类型信息作用域"""
        # 添加全局类型
        global_info = {
            'types': [
                {
                    'kind': 'typedef',
                    'name': 'global_int',
                    'base_type': 'int'
                }
            ]
        }
        self.type_manager.merge_type_info(global_info, to_global=True)
        
        # 添加当前文件类型
        self.type_manager.register_type('file_int', {
            'kind': 'typedef',
            'name': 'file_int',
            'base_type': 'int'
        })
        
        # 导出全局作用域类型
        global_types = self.type_manager.export_types(scope='global')
        global_type_names = [t['name'] for t in global_types['types']]
        self.assertIn('global_int', global_type_names)
        self.assertNotIn('file_int', global_type_names)
        
        # 导出当前文件作用域类型
        current_types = self.type_manager.export_types(scope='current')
        current_type_names = [t['name'] for t in current_types['types']]
        self.assertIn('file_int', current_type_names)
        self.assertNotIn('global_int', current_type_names)
        
        # 导出所有作用域类型
        all_types = self.type_manager.export_types(scope='all')
        all_type_names = [t['name'] for t in all_types['types']]
        self.assertIn('global_int', all_type_names)
        self.assertIn('file_int', all_type_names)

    def test_reset_type_info(self):
        """测试重置类型信息"""
        # 添加一些类型
        self.type_manager.register_type('test_typedef', {
            'kind': 'typedef',
            'name': 'test_typedef',
            'base_type': 'int'
        })
        
        self.type_manager.register_type('test_struct', {
            'kind': 'struct',
            'name': 'test_struct',
            'fields': [{'name': 'x', 'type': 'int'}]
        })
        
        # 重置类型信息
        self.type_manager.reset_type_info()
        
        # 验证类型已被重置
        self.assertFalse(self.type_manager.is_typedef_type('test_typedef'))
        self.assertFalse(self.type_manager.is_struct_type('test_struct'))

    def test_macro_definitions(self):
        """测试宏定义管理"""
        # 添加宏定义
        self.type_manager.add_macro_definition('MAX_SIZE', 100)
        self.type_manager.add_macro_definition('DEBUG', True)
        
        # 获取宏定义
        self.assertEqual(self.type_manager.get_macro_definition('MAX_SIZE'), 100)
        self.assertEqual(self.type_manager.get_macro_definition('DEBUG'), True)
        
        # 获取所有宏定义
        all_macros = self.type_manager.get_macro_definition()
        self.assertEqual(all_macros['MAX_SIZE'], 100)
        self.assertEqual(all_macros['DEBUG'], True)
        
        # 导出包含宏定义的类型信息
        type_info = self.type_manager.export_types()
        self.assertIn('macro_definitions', type_info)
        self.assertEqual(type_info['macro_definitions']['MAX_SIZE'], 100)

    def test_find_type_by_name(self):
        """测试按名称查找类型"""
        # 添加一些测试类型
        self.type_manager.register_type('test_struct', {
            'kind': 'struct',
            'name': 'test_struct',
            'fields': [{'name': 'x', 'type': 'int'}]
        })
        
        self.type_manager.register_type('test_enum', {
            'kind': 'enum',
            'name': 'test_enum',
            'values': {'A': 1, 'B': 2}
        })
        
        # 按名称查找
        struct_info = self.type_manager.find_type_by_name('test_struct')
        self.assertEqual(struct_info['kind'], 'struct')
        
        # 按名称和类型查找
        enum_info = self.type_manager.find_type_by_name('test_enum', 'enum')
        self.assertEqual(enum_info['kind'], 'enum')
        
        # 查找不存在的类型
        self.assertIsNone(self.type_manager.find_type_by_name('non_existent'))

    def test_find_types_by_kind(self):
        """测试按类型种类查找类型"""
        # 添加一些测试类型
        self.type_manager.register_type('test_struct1', {
            'kind': 'struct',
            'name': 'test_struct1',
            'fields': [{'name': 'x', 'type': 'int'}]
        })
        
        self.type_manager.register_type('test_struct2', {
            'kind': 'struct',
            'name': 'test_struct2',
            'fields': [{'name': 'y', 'type': 'float'}]
        })
        
        self.type_manager.register_type('test_enum', {
            'kind': 'enum',
            'name': 'test_enum',
            'values': {'A': 1, 'B': 2}
        })
        
        # 查找所有结构体
        structs = self.type_manager.find_types_by_kind('struct')
        self.assertEqual(len(structs), 2)
        struct_names = [s['name'] for s in structs]
        self.assertIn('test_struct1', struct_names)
        self.assertIn('test_struct2', struct_names)
        
        # 查找所有枚举
        enums = self.type_manager.find_types_by_kind('enum')
        self.assertEqual(len(enums), 1)
        self.assertEqual(enums[0]['name'], 'test_enum')


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
        self.type_manager.register_type('test_union', self.union_info)

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

    def test_nested_union(self):
        """测试嵌套联合体"""
        # 创建嵌套联合体
        inner_union = {
            'kind': 'union',
            'name': 'inner_union',
            'fields': [
                {'name': 'a', 'type': 'char'},
                {'name': 'b', 'type': 'short'}
            ],
            'size': 2,  # short的大小
            'alignment': 2
        }
        
        outer_struct = {
            'kind': 'struct',
            'name': 'outer_with_union',
            'fields': [
                {'name': 'u', 'type': 'inner_union'},
                {'name': 'value', 'type': 'int'}
            ],
            'size': 8,  # 联合体(2) + 对齐填充(2) + int(4)
            'alignment': 4
        }
        
        self.type_manager.register_type('inner_union', inner_union)
        self.type_manager.register_type('outer_with_union', outer_struct)
        
        # 验证嵌套联合体
        self.assertTrue(self.type_manager.is_union_type('inner_union'))
        
        # 验证结构体中的联合体字段
        field_info = self.type_manager.get_field_info('outer_with_union', 'u')
        self.assertEqual(field_info['type'], 'inner_union')
        self.assertEqual(field_info['offset'], 0)

    def test_union_with_array(self):
        """测试带数组的联合体"""
        union_info = {
            'kind': 'union',
            'name': 'array_union',
            'fields': [
                {'name': 'arr', 'type': 'char', 'array_dims': [4]},
                {'name': 'value', 'type': 'int'}
            ],
            'size': 4  # int和char[4]的大小相同
        }
        self.type_manager.register_type('array_union', union_info)
        
        # 验证数组字段
        field_info = self.type_manager.get_field_info('array_union', 'arr')
        self.assertEqual(field_info.get('array_dims'), [4])
        
        # 验证联合体大小
        self.assertEqual(self.type_manager.get_type_size('array_union'), 4)

    def test_anonymous_union(self):
        """测试匿名联合体"""
        anon_union = {
            'kind': 'union',
            'name': 'anonymous_union_1',
            'fields': [
                {'name': 'a', 'type': 'int'},
                {'name': 'b', 'type': 'float'}
            ],
            'is_anonymous': True
        }
        self.type_manager.register_type('anonymous_union_1', anon_union)
        
        # 验证匿名联合体
        self.assertTrue(self.type_manager.is_anonymous_type('anonymous_union_1'))
        self.assertTrue(self.type_manager.is_union_type('anonymous_union_1'))

    def test_union_in_typedef(self):
        """测试联合体在typedef中的使用"""
        # 创建一个typedef，基类型是联合体
        typedef_info = {
            'kind': 'typedef',
            'name': 'data_t',
            'base_type': 'test_union'
        }
        self.type_manager.register_type('data_t', typedef_info)
        
        # 验证typedef的基类型是联合体
        self.assertTrue(self.type_manager.is_union_type('data_t'))
        self.assertEqual(self.type_manager.get_real_type('data_t'), 'test_union')
        
        # 通过typedef获取联合体字段
        field_info = self.type_manager.get_field_info('data_t', 'i')
        self.assertEqual(field_info['type'], 'int')
        self.assertEqual(field_info['offset'], 0)

    def test_union_type_category(self):
        """测试联合体类型分类"""
        self.assertEqual(self.type_manager.get_type_category('test_union'), 'union')
        
        # 通过typedef的联合体
        typedef_info = {
            'kind': 'typedef',
            'name': 'data_t',
            'base_type': 'test_union'
        }
        self.type_manager.register_type('data_t', typedef_info)
        
        # 虽然data_t是typedef，但其实际类型是union
        self.assertEqual(self.type_manager.get_type_category('data_t'), 'typedef')


class TestTypeManagerPointer(unittest.TestCase):
    """测试指针相关功能"""
    
    def setUp(self):
        self.type_manager = TypeManager()

    def test_pointer_type_check(self):
        """测试指针类型检查"""
        # 直接指针语法
        self.assertTrue(self.type_manager.is_pointer_type('int*'))
        self.assertTrue(self.type_manager.is_pointer_type('char**'))
        
        # 通过typedef创建指针类型
        typedef_info = {
            'kind': 'typedef',
            'name': 'int_ptr',
            'base_type': 'int*'
        }
        self.type_manager.register_type('int_ptr', typedef_info)
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
        typedef_info = {
            'kind': 'typedef',
            'name': 'func_ptr',
            'base_type': 'void (*)(int)',
            'is_function_pointer': True
        }
        self.type_manager.register_type('func_ptr', typedef_info)
        self.assertTrue(self.type_manager.is_pointer_type('func_ptr'))
        
        # 指向数组的指针
        self.assertTrue(self.type_manager.is_pointer_type('int (*)[10]'))
        
        # 多级指针
        self.assertTrue(self.type_manager.is_pointer_type('int***'))
        self.assertEqual(self.type_manager.get_type_size('int***'), 8)

    def test_pointer_to_incomplete_type(self):
        """测试指向不完整类型的指针"""
        # 前向声明的结构体指针
        struct_info = {'kind': 'struct', 'name': 'forward_struct'}
        self.type_manager.register_type('forward_struct', struct_info)
        
        # 指向不完整类型的指针仍然是有效的
        self.assertTrue(self.type_manager.is_pointer_type('forward_struct*'))
        self.assertEqual(self.type_manager.get_type_size('forward_struct*'), 8)

    def test_pointer_resolve(self):
        """测试指针类型解析"""
        # 解析简单指针
        type_info = self.type_manager.resolve_type('int*')
        self.assertEqual(type_info['base_type'], 'int')
        self.assertEqual(type_info['pointer_level'], 1)
        self.assertTrue(type_info['is_pointer'])
        
        # 解析多级指针
        type_info = self.type_manager.resolve_type('char***')
        self.assertEqual(type_info['base_type'], 'char')
        self.assertEqual(type_info['pointer_level'], 3)
        
        # 解析指向结构体的指针
        struct_info = {
            'kind': 'struct',
            'name': 'test_struct',
            'fields': [{'name': 'x', 'type': 'int'}]
        }
        self.type_manager.register_type('test_struct', struct_info)
        
        type_info = self.type_manager.resolve_type('test_struct*')
        self.assertEqual(type_info['base_type'], 'test_struct')
        self.assertEqual(type_info['pointer_level'], 1)
        self.assertTrue(type_info['is_pointer'])
        self.assertFalse(type_info['is_basic'])

    def test_pointer_to_array(self):
        """测试指向数组的指针"""
        # 解析指向数组的指针
        type_info = self.type_manager.parse_type_string('int (*)[10]')
        self.assertEqual(type_info['base_type'], 'int')
        self.assertTrue(type_info['is_pointer'])
        self.assertEqual(type_info['array_dims'], [10])
        
        # 指向数组的指针大小仍然是8字节
        self.assertEqual(self.type_manager.get_type_size('int (*)[10]'), 8)

    def test_pointer_to_function(self):
        """测试函数指针"""
        # 创建函数指针类型
        typedef_info = {
            'kind': 'typedef',
            'name': 'callback_t',
            'base_type': 'void (*)(int, char*)',
            'is_function_pointer': True,
            'return_type': 'void',
            'param_types': ['int', 'char*']
        }
        self.type_manager.register_type('callback_t', typedef_info)
        
        # 验证函数指针
        self.assertTrue(self.type_manager.is_pointer_type('callback_t'))
        self.assertEqual(self.type_manager.get_type_size('callback_t'), 8)
        
        # 解析函数指针
        type_info = self.type_manager.resolve_type('callback_t')
        self.assertTrue(type_info['is_pointer'])
        self.assertEqual(type_info['base_type'], 'void (*)(int, char*)')

    def test_const_pointer(self):
        """测试常量指针和指向常量的指针"""
        # 解析指向常量的指针 (const int*)
        type_info = self.type_manager.parse_type_string('const int*')
        self.assertEqual(type_info['base_type'], 'int')
        self.assertTrue(type_info['is_pointer'])
        self.assertTrue(type_info['is_const'])
        self.assertEqual(type_info['pointer_level'], 1)
        
        # 解析常量指针 (int* const)
        type_info = self.type_manager.parse_type_string('int* const')
        self.assertEqual(type_info['base_type'], 'int')
        self.assertTrue(type_info['is_pointer'])
        self.assertTrue(type_info['is_const_pointer'])
        self.assertEqual(type_info['pointer_level'], 1)
        
        # 解析指向常量的常量指针 (const int* const)
        type_info = self.type_manager.parse_type_string('const int* const')
        self.assertEqual(type_info['base_type'], 'int')
        self.assertTrue(type_info['is_pointer'])
        self.assertTrue(type_info['is_const'])
        self.assertTrue(type_info['is_const_pointer'])
        self.assertEqual(type_info['pointer_level'], 1)


class TestTypeManagerTypeHierarchy(unittest.TestCase):
    """测试类型层次结构功能"""
    
    def setUp(self):
        self.type_manager = TypeManager()
        
        # 添加测试用的结构体类型
        self.type_manager.register_type('node', {
            'kind': 'struct',
            'name': 'node',
            'fields': [
                {'name': 'data', 'type': 'int'},
                {'name': 'next', 'type': 'node*'}
            ]
        })
        
        # 添加嵌套结构体
        self.type_manager.register_type('inner', {
            'kind': 'struct',
            'name': 'inner',
            'fields': [{'name': 'x', 'type': 'int'}]
        })
        
        self.type_manager.register_type('outer', {
            'kind': 'struct',
            'name': 'outer',
            'fields': [
                {'name': 'inner_field', 'type': 'inner'},
                {'name': 'value', 'type': 'int'}
            ]
        })

    def test_type_hierarchy(self):
        """测试类型层次结构获取"""
        # 添加 point 和 line 结构体定义
        self.type_manager.register_type('point', {
            'kind': 'struct',
            'name': 'point',
            'fields': [
                {'name': 'x', 'type': 'int'},
                {'name': 'y', 'type': 'int'}
            ]
        })
        
        self.type_manager.register_type('line', {
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
        
        # 验证嵌套字段
        start_field = next(f for f in hierarchy['fields'] if f['field_name'] == 'start')
        self.assertEqual(start_field['type'], 'struct')
        self.assertEqual(start_field['type_name'], 'point')

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
        self.assertEqual(next_field['base_type'], 'node')

    def test_complex_type_dependencies(self):
        """测试复杂类型依赖"""
        # 创建更复杂的类型依赖
        self.type_manager.register_type('complex_struct', {
            'kind': 'struct',
            'name': 'complex_struct',
            'fields': [
                {'name': 'node_ptr', 'type': 'node*'},
                {'name': 'inner_obj', 'type': 'inner'},
                {'name': 'outer_ptr', 'type': 'outer*'},
                {'name': 'data', 'type': 'int'}
            ]
        })
        
        deps = self.type_manager.get_type_dependencies('complex_struct')
        self.assertIn('node', deps)
        self.assertIn('inner', deps)
        self.assertIn('outer', deps)
        self.assertIn('int', deps)
        
        # 验证依赖层次
        hierarchy = self.type_manager.get_type_hierarchy('complex_struct')
        self.assertEqual(hierarchy['type'], 'struct')
        self.assertEqual(len(hierarchy['fields']), 4)


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
        self.type_manager.register_type('test_struct', struct_info)

    def test_type_attributes(self):
        """测试类型属性"""
        attrs = self.type_manager.get_type_attributes('test_struct')
        self.assertTrue(attrs.get('packed'))

    def test_type_location(self):
        """测试类型位置信息"""
        location = self.type_manager.get_type_location('test_struct')
        self.assertEqual(location['file'], 'test.h')
        self.assertEqual(location['line'], 10)

    def test_type_comment(self):
        """测试类型注释"""
        comment = self.type_manager.get_type_comment('test_struct')
        self.assertEqual(comment, 'Test structure')

    def test_type_status(self):
        """测试类型状态"""
        status = self.type_manager.get_type_status('test_struct')
        self.assertTrue(status['is_complete'])
        self.assertTrue(status['is_defined'])
        self.assertEqual(status['scope'], 'file')

    def test_type_summary(self):
        """测试类型摘要"""
        summary = self.type_manager.get_type_summary('test_struct')
        self.assertEqual(summary['name'], 'test_struct')
        self.assertEqual(summary['kind'], 'struct')
        self.assertTrue(summary['status']['is_defined'])

    def test_type_details(self):
        """测试类型详细信息"""
        details = self.type_manager.get_type_details('test_struct')
        self.assertTrue(details['packed'])
        self.assertEqual(details['alignment'], 4)
        self.assertEqual(details['visibility'], 'public')

    def test_incomplete_type(self):
        """测试不完整类型"""
        # 添加前向声明的结构体
        self.type_manager.register_type('forward_struct', {
            'kind': 'struct',
            'name': 'forward_struct',
            'is_forward_declaration': True
        })
        
        status = self.type_manager.get_type_status('forward_struct')
        self.assertFalse(status['is_complete'])
        self.assertTrue(status['is_defined'])

    def test_type_qualifiers(self):
        """测试类型限定符"""
        # 添加带限定符的类型
        typedef_info = {
            'kind': 'typedef',
            'name': 'const_int',
            'base_type': 'const int',
            'is_const': True
        }
        self.type_manager.register_type('const_int', typedef_info)
        
        type_info = self.type_manager.resolve_type('const_int')
        self.assertTrue(type_info['is_const'])
        self.assertEqual(type_info['base_type'], 'int')


class TestTypeManagerScope(unittest.TestCase):
    """测试类型作用域功能"""
    
    def setUp(self):
        self.type_manager = TypeManager()

    def test_scope_management(self):
        """测试作用域管理"""
        # 添加全局类型
        global_info = {
            'types': [
                {
                    'kind': 'typedef',
                    'name': 'global_int',
                    'base_type': 'int'
                },
                {
                    'kind': 'struct',
                    'name': 'global_struct',
                    'fields': []
                }
            ]
        }
        self.type_manager.merge_type_info(global_info, to_global=True)
        
        # 添加文件作用域类型
        self.type_manager.register_type('file_int', {
            'kind': 'typedef',
            'name': 'file_int',
            'base_type': 'int'
        })
        
        # 测试作用域判断
        self.assertEqual(self.type_manager.get_type_scope('global_int'), 'global')
        self.assertEqual(self.type_manager.get_type_scope('file_int'), 'file')
        self.assertEqual(self.type_manager.get_type_scope('int'), 'global')
        self.assertEqual(self.type_manager.get_type_scope('unknown_type'), 'unknown')

    def test_scope_reset(self):
        """测试作用域重置"""
        # 添加一些类型
        self.type_manager.register_type('file_type', {
            'kind': 'typedef',
            'name': 'file_type',
            'base_type': 'int'
        })
        
        self.type_manager.register_type('file_struct', {
            'kind': 'struct',
            'name': 'file_struct',
            'fields': []
        })
        
        # 重置当前文件作用域
        self.type_manager.reset_current_type_info()
        
        # 验证重置结果
        self.assertFalse(self.type_manager.is_typedef_type('file_type'))
        self.assertFalse(self.type_manager.is_struct_type('file_struct'))

    def test_scope_isolation(self):
        """测试作用域隔离"""
        # 添加全局类型
        global_info = {
            'types': [
                {
                    'kind': 'struct',
                    'name': 'common_struct',
                    'fields': [{'name': 'global_field', 'type': 'int'}]
                }
            ]
        }
        self.type_manager.merge_type_info(global_info, to_global=True)
        
        # 添加同名的文件作用域类型
        self.type_manager.register_type('common_struct', {
            'kind': 'struct',
            'name': 'common_struct',
            'fields': [{'name': 'file_field', 'type': 'int'}]
        })
        
        # 验证当前文件作用域的类型优先
        struct_info = self.type_manager.get_struct_info('common_struct')
        self.assertEqual(len(struct_info['fields']), 1)
        self.assertEqual(struct_info['fields'][0]['name'], 'file_field')
        
        # 重置当前文件作用域
        self.type_manager.reset_current_type_info()
        
        # 验证现在可以访问全局作用域的类型
        struct_info = self.type_manager.get_struct_info('common_struct')
        self.assertEqual(len(struct_info['fields']), 1)
        self.assertEqual(struct_info['fields'][0]['name'], 'global_field')

    def test_scope_export(self):
        """测试作用域导出"""
        # 添加全局类型
        global_info = {
            'types': [
                {
                    'kind': 'typedef',
                    'name': 'global_type',
                    'base_type': 'int'
                }
            ]
        }
        self.type_manager.merge_type_info(global_info, to_global=True)
        
        # 添加文件作用域类型
        self.type_manager.register_type('file_type', {
            'kind': 'typedef',
            'name': 'file_type',
            'base_type': 'int'
        })
        
        # 导出全局作用域
        global_types = self.type_manager.export_types(scope='global')
        global_type_names = [t['name'] for t in global_types['types']]
        self.assertIn('global_type', global_type_names)
        self.assertNotIn('file_type', global_type_names)
        
        # 导出文件作用域
        file_types = self.type_manager.export_types(scope='current')
        file_type_names = [t['name'] for t in file_types['types']]
        self.assertIn('file_type', file_type_names)
        self.assertNotIn('global_type', file_type_names)


if __name__ == '__main__':
    unittest.main() 
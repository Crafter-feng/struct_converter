import pytest
from c_parser.type_parser import CTypeParser
from c_parser.core.type_manager import TypeManager
from c_parser.core.tree_sitter_utils import TreeSitterUtils

@pytest.fixture
def type_manager():
    return TypeManager()

@pytest.fixture
def parser(type_manager):
    return CTypeParser(type_manager)

def test_parse_basic_types(parser):
    """测试基本类型解析"""
    # 测试int
    int_type = parser.parse_type("int")
    assert int_type['name'] == 'int'
    assert int_type['size'] == 4
    assert int_type['signed'] is True
    
    # 测试char
    char_type = parser.parse_type("char")
    assert char_type['name'] == 'char'
    assert char_type['size'] == 1
    
    # 测试float
    float_type = parser.parse_type("float")
    assert float_type['name'] == 'float'
    assert float_type['size'] == 4
    
    # 测试void
    void_type = parser.parse_type("void")
    assert void_type['name'] == 'void'
    assert void_type['size'] == 0

def test_parse_pointer_types(parser):
    """测试指针类型解析"""
    # 测试int*
    int_ptr = parser.parse_type("int*")
    assert int_ptr['pointer_level'] == 1
    assert int_ptr['base_type'] == 'int'
    assert int_ptr['size'] == 8  # 64位指针
    
    # 测试void*
    void_ptr = parser.parse_type("void*")
    assert void_ptr['pointer_level'] == 1
    assert void_ptr['base_type'] == 'void'
    
    # 测试多级指针
    multi_ptr = parser.parse_type("int**")
    assert multi_ptr['pointer_level'] == 2
    assert multi_ptr['base_type'] == 'int'

def test_parse_array_types(parser):
    """测试数组类型解析"""
    # 测试一维数组
    array1 = parser.parse_type("int[10]")
    assert array1['array_dims'] == [10]
    assert array1['base_type'] == 'int'
    assert array1['size'] == 40  # 4 * 10
    
    # 测试二维数组
    array2 = parser.parse_type("int[2][3]")
    assert array2['array_dims'] == [2, 3]
    assert array2['base_type'] == 'int'
    assert array2['size'] == 24  # 4 * 2 * 3
    
    # 测试不定长数组
    array3 = parser.parse_type("int[]")
    assert array3['array_dims'] == ['dynamic']
    assert array3['base_type'] == 'int'

def test_parse_function_pointer_types(parser):
    """测试函数指针类型解析"""
    # 无参数函数指针
    void_func = parser.parse_type("void (*)(void)")
    assert void_func['is_function_pointer'] is True
    assert void_func['function_info']['return_type']['name'] == 'void'
    assert not void_func['function_info']['parameters']
    
    # 带参数函数指针
    param_func = parser.parse_type("int (*)(int, float)")
    assert param_func['is_function_pointer'] is True
    assert param_func['function_info']['return_type']['name'] == 'int'
    assert len(param_func['function_info']['parameters']) == 2
    assert param_func['function_info']['parameters'][0]['name'] == 'int'
    assert param_func['function_info']['parameters'][1]['name'] == 'float'

def test_parse_complex_types(parser):
    assert parser.parse_type("const char*") == "str"
    assert parser.parse_type("volatile int") == "int"
    assert parser.parse_type("unsigned int") == "int"
    assert parser.parse_type("long long") == "int"

def test_parse_struct_types(parser):
    assert parser.parse_type("struct Point") == "Point"
    assert parser.parse_type("struct Point*") == "Optional[Point]"
    assert parser.parse_type("struct Point[]") == "List[Point]"

def test_parse_enum_types(parser):
    assert parser.parse_type("enum Color") == "Color"
    assert parser.parse_type("enum Status*") == "Optional[Status]"

def test_invalid_types(parser):
    with pytest.raises(ValueError):
        parser.parse_type("invalid_type")
    with pytest.raises(ValueError):
        parser.parse_type("int[invalid]")

def test_enum_value_reference(parser, tmp_path):
    """测试枚举值之间的引用"""
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    enum Test {
        A = 1,
        B = A + 1,  // 引用A
        C = B * 2,  // 引用B
        D = C + A   // 引用C和A
    };
    """)
    
    result = parser.parse_declarations(test_file)
    enum_info = result['enum_types']['Test']
    
    assert enum_info['values']['A'] == 1
    assert enum_info['values']['B'] == 2
    assert enum_info['values']['C'] == 4
    assert enum_info['values']['D'] == 5

def test_enum_with_expressions(parser, tmp_path):
    """测试带表达式的枚举值"""
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    enum Flags {
        F1 = 1 << 0,
        F2 = 1 << 1,
        F3 = F1 | F2,
        F4 = F1 << 2
    };
    """)
    
    result = parser.parse_declarations(test_file)
    enum_info = result['enum_types']['Flags']
    
    assert enum_info['values']['F1'] == 1
    assert enum_info['values']['F2'] == 2
    assert enum_info['values']['F3'] == 3
    assert enum_info['values']['F4'] == 4

def test_anonymous_enum(parser, tmp_path):
    """测试匿名枚举"""
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    enum {
        X = 1,
        Y = 2,
        Z = 3
    } anon_enum_var;
    """)
    
    result = parser.parse_declarations(test_file)
    # 检查是否正确生成了匿名枚举名称
    enum_name = next(name for name in result['enum_types'] 
                    if name.startswith('anonymous_enum_'))
    enum_info = result['enum_types'][enum_name]
    
    assert enum_info['is_anonymous'] is True
    assert enum_info['values']['X'] == 1
    assert enum_info['values']['Y'] == 2
    assert enum_info['values']['Z'] == 3

def test_enum_with_typedef(parser, tmp_path):
    """测试带typedef的枚举"""
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    typedef enum {
        RED = 1,
        GREEN = 2,
        BLUE = 3
    } Color;
    """)
    
    result = parser.parse_declarations(test_file)
    assert 'Color' in result['typedef_types']
    enum_info = result['enum_types'].get('Color')
    assert enum_info is not None
    assert enum_info['values']['RED'] == 1
    assert enum_info['values']['GREEN'] == 2
    assert enum_info['values']['BLUE'] == 3

def test_enum_value_errors(parser, tmp_path):
    """测试枚举值错误处理"""
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    enum Errors {
        E1 = UNDEFINED,  // 未定义的引用
        E2 = 1 / 0,     // 除零错误
        E3 = 1,         // 正常值
        E4 = E3 + UNDEFINED  // 引用未定义值
    };
    """)
    
    result = parser.parse_declarations(test_file)
    enum_info = result['enum_types']['Errors']
    
    # 错误情况应该保留原始表达式
    assert enum_info['values']['E1'] == 'UNDEFINED'  # 保留未定义的标识符
    assert enum_info['values']['E2'] == '1 / 0'      # 保留除零表达式
    assert enum_info['values']['E3'] == 1            # 正常值正确解析
    assert enum_info['values']['E4'] == 'E3 + UNDEFINED'  # 保留部分无效的表达式

def test_enum_type_manager_integration(parser, type_manager):
    """测试枚举与TypeManager的集成"""
    source = """
    enum Test {
        A = 1,
        B = A + 1
    };
    """
    
    parser.parse_declarations(source)
    
    # 检查TypeManager中的枚举信息
    enum_info = type_manager.get_enum_info()
    assert 'Test' in enum_info
    assert enum_info['Test']['values']['A'] == 1
    assert enum_info['Test']['values']['B'] == 2

def test_enum_in_struct(parser, tmp_path):
    """测试结构体中的枚举"""
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    struct Data {
        enum {
            IDLE = 0,
            BUSY = 1,
            ERROR = 2
        } state;
        int value;
    };
    """)
    
    result = parser.parse_declarations(test_file)
    struct_info = result['struct_types']['Data']
    
    # 检查匿名枚举字段
    state_field = next(f for f in struct_info['fields'] if f['name'] == 'state')
    assert state_field['type'].startswith('enum')
    
    # 检查枚举值是否被正确解析
    enum_name = state_field['type'].replace('enum ', '')
    enum_info = result['enum_types'][enum_name]
    assert enum_info['values']['IDLE'] == 0
    assert enum_info['values']['BUSY'] == 1
    assert enum_info['values']['ERROR'] == 2 

def test_struct_attributes(parser, tmp_path):
    """测试结构体属性"""
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    struct __attribute__((packed)) PackedStruct {
        char a;
        int b;
    };

    struct __attribute__((aligned(8))) AlignedStruct {
        char x;
        short y;
    };
    """)
    
    result = parser.parse_declarations(test_file)
    
    # 测试packed属性
    packed_info = result['struct_types']['PackedStruct']
    assert packed_info['attributes'].get('packed') is True
    assert packed_info['size'] == 5  # 无填充
    
    # 测试aligned属性
    aligned_info = result['struct_types']['AlignedStruct']
    assert aligned_info['attributes'].get('alignment') == 8
    assert aligned_info['size'] == 8  # 考虑8字节对齐

def test_union_attributes(parser, tmp_path):
    """测试联合体属性"""
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    union __attribute__((packed)) PackedUnion {
        char a;
        int b;
    };

    union __attribute__((aligned(16))) AlignedUnion {
        char x;
        double y;
    };
    """)
    
    result = parser.parse_declarations(test_file)
    
    # 测试packed属性
    packed_info = result['union_types']['PackedUnion']
    assert packed_info['attributes'].get('packed') is True
    
    # 测试aligned属性
    aligned_info = result['union_types']['AlignedUnion']
    assert aligned_info['attributes'].get('alignment') == 16 

def test_nested_types(parser, tmp_path):
    """测试嵌套类型"""
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    struct Outer {
        struct {
            int x;
            int y;
            union {
                float f;
                double d;
            };
        } nested;
        enum {
            A = 1,
            B = 2
        } flags;
    };
    """)
    
    result = parser.parse_declarations(test_file)
    outer_info = result['struct_types']['Outer']
    
    # 检查嵌套结构体
    nested_field = next(f for f in outer_info['fields'] if f['name'] == 'nested')
    assert nested_field['is_anonymous'] is True
    assert len(nested_field['nested_fields']) == 3
    
    # 检查嵌套联合体
    union_field = next(f for f in nested_field['nested_fields'] 
                      if f.get('is_union'))
    assert union_field['is_anonymous'] is True
    
    # 检查嵌套枚举
    enum_field = next(f for f in outer_info['fields'] if f['name'] == 'flags')
    enum_type = enum_field['type'].replace('enum ', '')
    enum_info = result['enum_types'][enum_type]
    assert enum_info['values']['A'] == 1
    assert enum_info['values']['B'] == 2 

def test_type_parsing_cache(parser):
    """测试类型解析缓存"""
    # 第一次解析
    type1 = parser.parse_type("struct Point*")
    
    # 第二次解析应该使用缓存
    type2 = parser.parse_type("struct Point*")
    
    assert type1 is type2  # 应该是同一个对象

def test_cache_invalidation(parser, type_manager):
    """测试缓存失效"""
    # 第一次解析
    type1 = parser.parse_type("struct Test")
    
    # 修改类型管理器中的类型信息
    type_manager.register_struct("Test", [{'name': 'x', 'type': 'int'}])
    
    # 再次解析，应该获取新的结果
    type2 = parser.parse_type("struct Test")
    
    assert type1 is not type2 

def test_error_handling(parser, tmp_path):
    """测试错误处理"""
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    // 不完整的结构体
    struct Incomplete {
        int a;
        unknown_type b;  // 未知类型
        struct Undefined *ptr;  // 未定义的结构体
    };
    
    // 语法错误
    struct Invalid {
        int x;;  // 多余的分号
        int y
    };
    """)
    
    result = parser.parse_declarations(test_file)
    
    # 应该能够部分解析成功
    incomplete = result['struct_types'].get('Incomplete')
    assert incomplete is not None
    assert len(incomplete['fields']) >= 1  # 至少解析出了a字段
    
    # 错误的结构体应该被跳过
    assert 'Invalid' not in result['struct_types'] 

def test_enum_value_error_handling(parser, tmp_path):
    """测试枚举值错误处理"""
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    enum Test {
        A = UNDEFINED_MACRO,  // 未定义的宏
        B = 1 / 0,           // 除零错误
        C = SOME_ENUM + 1,   // 未定义的枚举值
        D = 1               // 正常值
    };
    """)
    
    result = parser.parse_declarations(test_file)
    enum_info = result['enum_types']['Test']
    
    # 检查错误处理
    assert enum_info['values']['A'] == 'UNDEFINED_MACRO'  # 保留原始表达式
    assert enum_info['values']['B'] == '1 / 0'           # 保留原始表达式
    assert enum_info['values']['C'] == 'SOME_ENUM + 1'   # 保留原始表达式
    assert enum_info['values']['D'] == 1                 # 正常值被正确解析

def test_complex_enum_expressions(parser, tmp_path):
    """测试复杂枚举表达式"""
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    enum Complex {
        A = 1,
        B = A << 1,          // 位运算
        C = (B * 2) + 1,     // 算术运算
        D = B | (1 << 2),    // 复杂位运算
        E = INVALID_OP @ 1   // 无效运算符
    };
    """)
    
    result = parser.parse_declarations(test_file)
    enum_info = result['enum_types']['Complex']
    
    assert enum_info['values']['A'] == 1
    assert enum_info['values']['B'] == 2
    assert enum_info['values']['C'] == 5
    assert enum_info['values']['D'] == 6
    assert enum_info['values']['E'] == 'INVALID_OP @ 1'  # 保留原始表达式 

def test_complex_expression_errors(parser, tmp_path):
    """测试复杂表达式错误处理"""
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    enum Test {
        A = 1,
        B = A << -1,        // 无效的左移
        C = (A >> 2) + X,   // 未定义的变量X
        D = 1 @ 2,          // 无效的运算符
        E = (1 + 2         // 语法错误：未闭合的括号
    };
    """)
    
    result = parser.parse_declarations(test_file)
    enum_info = result['enum_types']['Test']
    
    assert enum_info['values']['A'] == 1                # 正常值
    assert enum_info['values']['B'] == 'A << -1'        # 保留无效的左移
    assert enum_info['values']['C'] == '(A >> 2) + X'   # 保留包含未定义变量的表达式
    assert enum_info['values']['D'] == '1 @ 2'          # 保留无效运算符
    assert enum_info['values']['E'] == '(1 + 2'         # 保留未闭合的表达式 

def test_macro_and_enum_references(parser, tmp_path):
    """测试宏定义和枚举引用"""
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    #define MAX_VALUE 100
    #define MIN_VALUE 0
    
    enum Values {
        A = MAX_VALUE,          // 有效的宏引用
        B = UNDEFINED_MACRO,    // 未定义的宏
        C = A - MIN_VALUE,      // 有效的表达式
        D = B + MIN_VALUE      // 引用无效值
    };
    """)
    
    result = parser.parse_declarations(test_file)
    enum_info = result['enum_types']['Values']
    
    assert enum_info['values']['A'] == 100              # 正确解析宏值
    assert enum_info['values']['B'] == 'UNDEFINED_MACRO' # 保留未定义的宏
    assert enum_info['values']['C'] == 100              # 正确计算表达式
    assert enum_info['values']['D'] == 'B + MIN_VALUE'  # 保留包含无效值的表达式 

def test_bitfield_expressions(parser, tmp_path):
    """测试位域表达式"""
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    struct Test {
        int a : 1 + 2;          // 有效表达式
        int b : INVALID;        // 无效标识符
        int c : (1 << 3);       // 有效的位运算
        int d : MAX + 1;        // 未定义的宏
        int e : -1;             // 无效的位域大小
    };
    """)
    
    result = parser.parse_declarations(test_file)
    struct_info = result['struct_types']['Test']
    
    assert struct_info['fields'][0]['bitfield_size'] == 3     # 正确计算
    assert struct_info['fields'][1]['bitfield_size'] == 'INVALID'  # 保留无效标识符
    assert struct_info['fields'][2]['bitfield_size'] == 8     # 正确计算位运算
    assert struct_info['fields'][3]['bitfield_size'] == 'MAX + 1'  # 保留未定义的宏
    assert struct_info['fields'][4]['bitfield_size'] == '-1'  # 保留无效大小 

def test_parse_source(parser):
    source = "int x = 1;"
    node = TreeSitterUtils.get_instance().parse_source(source)
    assert node is not None 
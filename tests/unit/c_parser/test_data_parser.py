import pytest
from c_parser.data_parser import CDataParser

@pytest.fixture
def parser():
    return CDataParser()

def test_initialization(parser):
    """测试初始化"""
    assert parser is not None
    assert parser.tree_sitter_parser is not None
    assert parser.data_manager is not None
    assert parser.type_parser is not None

def test_parse_file(parser, tmp_path):
    """测试文件解析"""
    # 创建测试文件
    test_file = tmp_path / "test.h"
    test_file.write_text("""
    struct Point {
        int x;
        int y;
    };
    
    enum Color {
        RED,
        GREEN,
        BLUE
    };
    
    typedef struct Point Point_t;
    
    Point_t origin = {0, 0};
    """)
    
    result = parser.parse_file(str(test_file))
    
    assert result is not None
    assert 'Point' in result['structs']
    assert 'Color' in result['enums']
    assert 'Point_t' in result['typedefs']
    assert len(result['variables']['struct_vars']) == 1

def test_parse_global_variables(parser):
    """测试全局变量解析"""
    source_code = """
    int global_var = 42;
    char* string_var = "hello";
    struct Point point = {1, 2};
    int numbers[3] = {1, 2, 3};
    """
    
    result = parser.parse_global_variables(source_code)
    
    assert result is not None
    assert len(result['variables']['variables']) >= 1  # 基本类型变量
    assert len(result['variables']['pointer_vars']) >= 1  # 指针变量
    assert len(result['variables']['array_vars']) >= 1  # 数组变量

def test_process_struct(parser):
    """测试结构体处理"""
    struct = {
        'name': 'Point',
        'fields': [
            {'name': 'x', 'type': 'int'},
            {'name': 'y', 'type': 'int'}
        ],
        'attributes': {'packed': True}
    }
    
    result = parser._process_struct(struct)
    
    assert result['name'] == 'Point'
    assert len(result['fields']) == 2
    assert result['attributes']['packed'] is True

def test_process_union(parser):
    """测试联合体处理"""
    union = {
        'name': 'Data',
        'fields': [
            {'name': 'i', 'type': 'int'},
            {'name': 'f', 'type': 'float'}
        ]
    }
    
    result = parser._process_union(union)
    
    assert result['name'] == 'Data'
    assert len(result['fields']) == 2
    assert result['is_union'] is True

def test_process_enum(parser):
    """测试枚举处理"""
    enum = {
        'name': 'Color',
        'values': [
            {'name': 'RED', 'value': 0},
            {'name': 'GREEN', 'value': 1},
            {'name': 'BLUE', 'value': 2}
        ]
    }
    
    result = parser._process_enum(enum)
    
    assert result['name'] == 'Color'
    assert len(result['values']) == 3
    assert result['values']['RED'] == 0

def test_process_bit_fields(parser):
    """测试位域处理"""
    field = {
        'name': 'flags',
        'type': 'unsigned int',
        'bit_width': 3
    }
    
    current_offset = 0
    new_offset, field_info = parser._process_bit_field(field, current_offset)
    
    assert new_offset > current_offset
    assert field_info['bit_width'] == 3
    assert field_info['bit_offset'] == 0

def test_array_dimensions(parser):
    """测试数组维度解析"""
    declarator = {
        'name': 'array',
        'dimensions': [
            {'type': 'number_literal', 'value': 10},
            {'type': 'identifier', 'name': 'SIZE'}
        ]
    }
    
    sizes, name = parser._parse_array_dimensions(declarator)
    
    assert name == 'array'
    assert len(sizes) == 2
    assert sizes[0] == 10
    assert isinstance(sizes[1], str)

def test_dynamic_array_size(parser):
    """测试动态数组大小解析"""
    initializer = {
        'type': 'string_literal',
        'value': 'hello'
    }
    array_sizes = ['dynamic']
    
    result = parser._solve_dynamic_array_size(initializer, array_sizes)
    
    assert len(result) == 1
    assert result[0] == 6  # 包含null终止符

def test_type_info_extraction(parser):
    """测试类型信息提取"""
    node = {
        'type': 'struct_specifier',
        'name': 'Point'
    }
    
    type_info = parser._extract_type_info(node)
    
    assert type_info['type'] == 'struct Point'
    assert type_info['original_type'] == 'struct Point'

def test_comments_processing(parser):
    """测试注释处理"""
    node = {
        'comments': [
            {'text': '// Single line comment'},
            {'text': '/* Multi-line comment */'},
            {'text': '/** Documentation comment */'}
        ]
    }
    
    comments = parser._process_comments(node)
    
    assert len(comments) == 3
    assert 'Single line comment' in comments[0]

def test_error_handling(parser):
    """测试错误处理"""
    # 测试无效的结构体
    with pytest.raises(Exception):
        parser._process_struct({})
    
    # 测试无效的联合体
    with pytest.raises(Exception):
        parser._process_union({})
    
    # 测试无效的枚举
    with pytest.raises(Exception):
        parser._process_enum({})

def test_complex_declarations(parser):
    """测试复杂声明"""
    source_code = """
    struct Complex {
        union {
            struct {
                int x, y;
            } point;
            struct {
                float r, g, b;
            } color;
        } data;
        int type;
    };
    
    Complex obj = {{.point = {1, 2}}, 0};
    """
    
    result = parser.parse_global_variables(source_code)
    assert result is not None
    assert len(result['variables']['struct_vars']) == 1

def test_type_definitions(parser):
    """测试类型定义"""
    source_code = """
    typedef int* IntPtr;
    typedef void (*Callback)(void*);
    typedef struct {
        int width;
        int height;
    } Size;
    """
    
    result = parser.parse_global_variables(source_code)
    assert 'IntPtr' in result['types']['current']['typedef_types']
    assert 'Callback' in result['types']['current']['typedef_types']
    assert 'Size' in result['types']['current']['typedef_types'] 

def test_nested_struct_processing(parser):
    """测试嵌套结构体处理"""
    source_code = """
    struct Outer {
        struct {  // 匿名结构体
            int x;
            int y;
        } point;
        struct Inner {  // 命名内部结构体
            float r;
            float theta;
        } polar;
        struct {  // 另一个匿名结构体
            char r;
            char g;
            char b;
        };  // 无名字段，直接展开
    };
    
    struct Outer obj = {
        .point = {1, 2},
        .polar = {3.14, 1.57},
        .r = 255,
        .g = 128,
        .b = 0
    };
    """
    
    result = parser.parse_global_variables(source_code)
    assert result is not None
    
    # 检查结构体定义
    structs = result['types']['current']['struct_info']
    assert 'Outer' in structs
    outer_struct = structs['Outer']
    
    # 检查字段
    fields = outer_struct['fields']
    assert len(fields) >= 5  # point(x,y) + polar(r,theta) + rgb
    
    # 检查匿名结构体字段
    point_field = next(f for f in fields if f['name'] == 'point')
    assert 'nested_struct' in point_field
    assert len(point_field['nested_struct']['fields']) == 2
    
    # 检查命名内部结构体
    assert 'Inner' in structs
    
    # 检查变量定义
    vars = result['variables']['struct_vars']
    assert len(vars) == 1
    obj = vars[0]
    assert obj['type'] == 'Outer'

def test_anonymous_union_in_struct(parser):
    """测试结构体中的匿名联合体"""
    source_code = """
    struct Data {
        int type;
        union {  // 匿名联合体
            struct {
                int x, y;
            } point;
            struct {
                float radius;
                float angle;
            } polar;
            int raw_data[4];
        };  // 无名字段，直接展开
    };
    
    struct Data data = {
        .type = 1,
        .point = {10, 20}
    };
    """
    
    result = parser.parse_global_variables(source_code)
    
    # 检查结构体定义
    structs = result['types']['current']['struct_info']
    assert 'Data' in structs
    data_struct = structs['Data']
    
    # 检查字段
    fields = data_struct['fields']
    assert len(fields) >= 2  # type + anonymous union
    
    # 检查匿名联合体
    union_field = next(f for f in fields if f.get('is_anonymous'))
    assert union_field['is_union']
    assert len(union_field['nested_fields']) >= 3

def test_nested_anonymous_structs(parser):
    """测试多层嵌套的匿名结构体"""
    source_code = """
    struct Complex {
        struct {  // 第一层匿名结构体
            struct {  // 第二层匿名结构体
                int x;
                int y;
                struct {  // 第三层匿名结构体
                    char r;
                    char g;
                    char b;
                } color;
            } position;
            float scale;
        } rendering;
        int flags;
    };
    
    struct Complex obj = {
        .rendering.position = {
            .x = 100,
            .y = 200,
            .color = {255, 128, 0}
        },
        .rendering.scale = 2.0f,
        .flags = 1
    };
    """
    
    result = parser.parse_global_variables(source_code)
    
    # 检查结构体定义
    structs = result['types']['current']['struct_info']
    assert 'Complex' in structs
    complex_struct = structs['Complex']
    
    # 检查嵌套层级
    rendering_field = next(f for f in complex_struct['fields'] if f['name'] == 'rendering')
    assert 'nested_struct' in rendering_field
    
    position_field = next(f for f in rendering_field['nested_struct']['fields'] 
                         if f['name'] == 'position')
    assert 'nested_struct' in position_field
    
    color_field = next(f for f in position_field['nested_struct']['fields'] 
                      if f['name'] == 'color')
    assert 'nested_struct' in color_field

def test_mixed_anonymous_members(parser):
    """测试混合的匿名成员（结构体和联合体）"""
    source_code = """
    struct Mixed {
        union {  // 匿名联合体
            struct {  // 匿名结构体
                int x, y;
            };  // 直接展开
            struct {
                float angle;
                float distance;
            } polar;
            int raw[2];
        };  // 直接展开
        struct {  // 匿名结构体
            unsigned char flags;
            union {  // 嵌套的匿名联合体
                unsigned int value;
                struct {
                    unsigned char b1: 1;
                    unsigned char b2: 1;
                    unsigned char b3: 1;
                } bits;
            };
        } attributes;
    };
    
    struct Mixed data = {
        .x = 10,  // 直接访问匿名结构体成员
        .y = 20,
        .attributes = {
            .flags = 1,
            .value = 0xFF
        }
    };
    """
    
    result = parser.parse_global_variables(source_code)
    
    # 检查结构体定义
    structs = result['types']['current']['struct_info']
    assert 'Mixed' in structs
    mixed_struct = structs['Mixed']
    
    # 检查字段
    fields = mixed_struct['fields']
    assert len(fields) >= 2  # anonymous union + attributes
    
    # 检查匿名联合体
    union_field = next(f for f in fields if f.get('is_anonymous') and f.get('is_union'))
    assert len(union_field['nested_fields']) >= 3
    
    # 检查attributes字段
    attrs_field = next(f for f in fields if f['name'] == 'attributes')
    assert 'nested_struct' in attrs_field
    
    # 检查变量定义
    vars = result['variables']['struct_vars']
    assert len(vars) == 1
    data = vars[0]
    assert data['type'] == 'Mixed' 
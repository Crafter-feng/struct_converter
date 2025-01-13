import pytest
from c_parser.core.tree_sitter_base import TreeSitterParser
from c_parser.data_parser import DataParser

def test_empty_struct():
    c_code = """
    struct Empty {
    };
    """
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    assert ast is not None

def test_struct_with_comments_only():
    c_code = """
    struct CommentOnly {
        // Just a comment
        /* Another comment */
    };
    """
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    assert ast is not None

def test_deeply_nested_structs():
    c_code = """
    struct Level3 {
        int data;
    };
    
    struct Level2 {
        struct Level3 l3;
    };
    
    struct Level1 {
        struct Level2 l2;
    };
    """
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    assert ast is not None 

def test_struct_with_bit_fields():
    c_code = """
    struct BitFields {
        unsigned int a : 1;
        int : 0;  // unnamed bit field
        signed int b : 2;
        int c : 3;
    };
    """
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    assert ast is not None
    
    data_parser = DataParser()
    python_code = data_parser.generate_python(ast)
    
    # 验证生成的Python代码
    assert "class BitFields:" in python_code
    assert "self.a: int" in python_code  # 1位无符号整数
    assert "self.b: int" in python_code  # 2位有符号整数
    assert "self.c: int" in python_code  # 3位整数

def test_struct_with_function_pointers():
    c_code = """
    struct Callbacks {
        void (*on_init)(void);
        int (*calculate)(int, int);
        void (*on_error)(const char* message);
    };
    """
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    assert ast is not None
    # TODO: Add assertions for function pointer parsing

def test_struct_with_arrays():
    c_code = """
    struct Arrays {
        int fixed_array[10];
        char string[256];
        float matrix[4][4];
        int flexible[];  // flexible array member
    };
    """
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    assert ast is not None
    # TODO: Add assertions for array parsing

def test_struct_with_unions():
    c_code = """
    struct WithUnion {
        int type;
        union {
            int i;
            float f;
            char c;
        } data;
    };
    """
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    assert ast is not None
    # TODO: Add assertions for union parsing

def test_struct_with_packed_attribute():
    c_code = """
    struct __attribute__((packed)) Packed {
        char a;
        int b;
        short c;
    };
    """
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    assert ast is not None
    # TODO: Add assertions for packed attribute

def test_struct_with_typedef():
    c_code = """
    typedef struct Point {
        int x;
        int y;
    } Point_t;
    """
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    assert ast is not None
    # TODO: Add assertions for typedef handling 

def test_invalid_struct_syntax():
    c_code = """
    struct Invalid {
        int missing_semicolon
        int x;
    };
    """
    parser = TreeSitterParser()
    with pytest.raises(Exception) as exc_info:
        ast = parser.parse(c_code)
    assert "syntax error" in str(exc_info.value).lower()

def test_invalid_bit_field():
    c_code = """
    struct InvalidBitField {
        int x : -1;  // negative bit field size
        int y : 999999;  // too large bit field
    };
    """
    parser = TreeSitterParser()
    with pytest.raises(Exception) as exc_info:
        ast = parser.parse(c_code)
    assert "invalid bit field" in str(exc_info.value).lower() 
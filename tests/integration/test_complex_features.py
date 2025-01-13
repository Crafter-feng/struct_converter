import pytest
from c_parser.core.tree_sitter_base import TreeSitterParser
from c_parser.data_parser import DataParser

def test_struct_with_all_features():
    c_code = """
    #define MAX_SIZE 100
    #define BUFFER_SIZE 1024

    typedef struct Node Node;

    struct Node {
        int value;
        Node* next;
        Node* prev;
    };

    typedef struct {
        char name[32];
        int age;
        union {
            struct {
                float x;
                float y;
            } point;
            struct {
                int width;
                int height;
            } size;
        } data;
        void (*callback)(void*);
        unsigned int flags : 8;
        char buffer[BUFFER_SIZE];
    } ComplexStruct;
    """
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    assert ast is not None
    
    data_parser = DataParser()
    python_code = data_parser.generate_python(ast)
    
    # 验证生成的Python代码
    assert "class Node:" in python_code
    assert "class ComplexStruct:" in python_code
    assert "self.next: Optional[Node]" in python_code
    assert "self.prev: Optional[Node]" in python_code
    assert "self.callback: Callable" in python_code

def test_struct_with_preprocessor_conditions():
    c_code = """
    #ifdef __cplusplus
    extern "C" {
    #endif

    struct ConditionalStruct {
    #if defined(PLATFORM_32BIT)
        int ptr_size;
    #else
        long ptr_size;
    #endif
        
    #ifdef DEBUG
        char debug_info[256];
    #endif
    };

    #ifdef __cplusplus
    }
    #endif
    """
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    assert ast is not None

def test_struct_with_complex_types():
    c_code = """
    struct ComplexTypes {
        const char* const* argv;
        int (*matrix)[4];
        void* (*allocator)(size_t size);
        int volatile atomic_counter;
        const struct {
            long value;
        } embedded;
    };
    """
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    assert ast is not None
    
    data_parser = DataParser()
    python_code = data_parser.generate_python(ast)
    
    assert "class ComplexTypes:" in python_code
    assert "self.argv: List[str]" in python_code
    assert "self.matrix: List[List[int]]" in python_code
    assert "self.allocator: Callable[[int], Any]" in python_code 

def test_struct_with_volatile_and_const():
    c_code = """
    struct VolatileAndConst {
        volatile int counter;
        const char* message;
        const volatile unsigned long status;
        const int* const* ptr_to_const_ptr;
    };
    """
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    assert ast is not None
    
    data_parser = DataParser()
    python_code = data_parser.generate_python(ast)
    
    assert "class VolatileAndConst:" in python_code
    assert "self.counter: int" in python_code
    assert "self.message: str" in python_code
    assert "self.status: int" in python_code
    assert "self.ptr_to_const_ptr: List[int]" in python_code

def test_struct_with_function_array():
    c_code = """
    struct FunctionArray {
        void (*handlers[10])(void);
        int (*matrix[3][3])(float);
        void (*callback_array[])(int);  // flexible array of function pointers
    };
    """
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    assert ast is not None
    
    data_parser = DataParser()
    python_code = data_parser.generate_python(ast)
    
    assert "class FunctionArray:" in python_code
    assert "self.handlers: List[Callable[[], None]]" in python_code
    assert "self.matrix: List[List[Callable[[float], int]]]" in python_code
    assert "self.callback_array: List[Callable[[int], None]]" in python_code 

def test_nested_union_and_struct():
    c_code = """
    struct NestedUnionStruct {
        union {
            struct {
                int x, y;
                union {
                    float f;
                    double d;
                } nested_union;
            } point;
            struct {
                char name[32];
                union {
                    int code;
                    char symbol;
                } id;
            } label;
        } data;
    };
    """
    parser = TreeSitterParser()
    ast = parser.parse(c_code)
    assert ast is not None
    
    data_parser = DataParser()
    python_code = data_parser.generate_python(ast)
    
    assert "class NestedUnionStruct:" in python_code
    assert "class Point:" in python_code
    assert "class Label:" in python_code
    assert "class NestedUnion:" in python_code
    assert "class Id:" in python_code 
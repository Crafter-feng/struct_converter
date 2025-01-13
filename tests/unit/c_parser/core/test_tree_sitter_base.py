import pytest
from c_parser.core.tree_sitter_base import TreeSitterParser

@pytest.fixture
def parser():
    return TreeSitterParser()

def test_parse_multiple_declarations(parser):
    code = """
    struct Point;
    struct Size;
    
    struct Point {
        int x, y;
    };
    
    struct Size {
        int width, height;
    };
    """
    result = parser.parse(code)
    assert result is not None
    assert len(result.declarations) == 2

def test_parse_with_includes(parser):
    code = """
    #include <stdint.h>
    #include "config.h"
    
    struct Data {
        uint32_t value;
        struct Config* config;
    };
    """
    result = parser.parse(code)
    assert result is not None
    assert result.includes == ["stdint.h", "config.h"]

def test_parse_with_defines(parser):
    code = """
    #define MAX_SIZE 100
    #define MIN(a,b) ((a) < (b) ? (a) : (b))
    #define DEBUG
    
    struct Buffer {
        char data[MAX_SIZE];
    };
    """
    result = parser.parse(code)
    assert result is not None
    assert "MAX_SIZE" in result.defines
    assert "MIN" in result.defines
    assert "DEBUG" in result.defines

def test_parse_with_conditional_compilation(parser):
    code = """
    #ifdef DEBUG
    struct DebugInfo {
        char* message;
        int line;
    };
    #endif
    
    struct Data {
    #ifdef PLATFORM_32
        int32_t value;
    #else
        int64_t value;
    #endif
    };
    """
    result = parser.parse(code)
    assert result is not None
    # 验证条件编译的处理 

def test_parse_enum_declarations(parser):
    code = """
    enum Color {
        RED = 0,
        GREEN = 1,
        BLUE = 2
    };

    enum Status {
        OK,
        ERROR = -1,
        PENDING = 1
    };
    """
    result = parser.parse(code)
    assert result is not None
    assert len(result.enums) == 2
    assert "Color" in result.enums
    assert "Status" in result.enums

def test_parse_typedef_declarations(parser):
    code = """
    typedef unsigned int uint32_t;
    typedef struct Point Point;
    typedef enum { LEFT, RIGHT } Direction;
    typedef void (*Callback)(void*);
    """
    result = parser.parse(code)
    assert result is not None
    assert len(result.typedefs) == 4
    assert "uint32_t" in result.typedefs
    assert "Point" in result.typedefs
    assert "Direction" in result.typedefs
    assert "Callback" in result.typedefs

def test_parse_macro_definitions(parser):
    code = """
    #define VERSION_MAJOR 1
    #define VERSION_MINOR 0
    #define VERSION_STR "1.0"
    #define MAX(a, b) ((a) > (b) ? (a) : (b))
    #define UNUSED(x) (void)(x)
    """
    result = parser.parse(code)
    assert result is not None
    assert len(result.macros) == 5
    assert result.macros["VERSION_MAJOR"] == "1"
    assert result.macros["VERSION_STR"] == '"1.0"'
    assert "MAX" in result.macros
    assert "UNUSED" in result.macros

def test_parse_struct_with_attributes(parser):
    code = """
    struct __attribute__((packed)) PackedStruct {
        char a;
        int b;
    } __attribute__((aligned(4)));

    struct __attribute__((deprecated)) OldStruct {
        int x;
    };
    """
    result = parser.parse(code)
    assert result is not None
    assert "PackedStruct" in result.structs
    assert "OldStruct" in result.structs
    assert result.structs["PackedStruct"].attributes["packed"] is True
    assert result.structs["PackedStruct"].attributes["aligned"] == 4

def test_parse_with_comments(parser):
    code = """
    // Single line comment
    /* Multi-line
       comment */
    struct /* inline comment */ Point {
        int x;  // Field comment
        int y;  /* Another comment */
    };
    """
    result = parser.parse(code)
    assert result is not None
    assert len(result.comments) > 0
    assert any("Single line comment" in c for c in result.comments)
    assert any("Multi-line\n       comment" in c for c in result.comments)
    assert any("Field comment" in c for c in result.comments)

def test_parse_with_error_handling(parser):
    invalid_codes = [
        "struct {",  # 未完成的结构体
        "enum {",    # 未完成的枚举
        "#include",  # 未完成的include
        "typedef",   # 未完成的typedef
        "struct Point { invalid type field; };"  # 无效的类型
    ]
    
    for code in invalid_codes:
        with pytest.raises(Exception):
            parser.parse(code)

def test_parse_with_preprocessor_branches(parser):
    code = """
    #if defined(PLATFORM_WINDOWS)
        typedef unsigned long DWORD;
        #define CALLBACK __stdcall
    #elif defined(PLATFORM_LINUX)
        typedef unsigned int DWORD;
        #define CALLBACK
    #else
        #error "Unsupported platform"
    #endif

    struct PlatformSpecific {
    #ifdef PLATFORM_WINDOWS
        DWORD win_field;
    #else
        int unix_field;
    #endif
    };
    """
    result = parser.parse(code)
    assert result is not None
    assert result.has_platform_specific_code is True

def test_parse_with_includes_resolution(parser):
    code = """
    #include <stdio.h>
    #include "mylib.h"
    #include <stdlib.h>
    
    struct Data {
        FILE* file;
        void* ptr;
    };
    """
    result = parser.parse(code)
    assert result is not None
    assert len(result.system_includes) >= 2
    assert "stdio.h" in result.system_includes
    assert "stdlib.h" in result.system_includes
    assert "mylib.h" in result.local_includes 
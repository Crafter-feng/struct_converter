#ifndef TEST_STRUCTS_H
#define TEST_STRUCTS_H

#include <stdint.h>
#include <stdbool.h>

// 基本数据类型的typedef
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef int8_t i8;
typedef int16_t i16;
typedef int32_t i32;
typedef float f32;
typedef double f64;

// 简单结构体
typedef struct Point {
    i32 x;
    i32 y;
} Point, *PointPtr;

// 指针类型定义
typedef struct Vector* VectorPtr;

// 带数组的结构体
typedef struct {
    f32 components[3];
    Point points[4];
    u32 count;
} Vector;

// 链表节点
typedef struct Node {
    i32 value;
    struct Node* next;
    struct Node* prev;
} Node;

// 复杂数据结构
typedef struct ComplexData {
    u8 id;
    char name[32];
    Point position;
    Vector* movement;    // 结构体指针
    PointPtr targets;   // 指针数组
    Node* head;         // 链表
    f32 matrix[4][4];   // 二维数组
    void* extra_data;   // void指针
    u32 flags;
} ComplexData;

// 带位域的结构体
typedef struct BitFields {
    u32 flag1 : 1;
    u32 flag2 : 1;
    u32 value : 6;
    u32 reserved : 24;
} BitFields;

// 联合体
typedef union DataValue {
    i32 as_int;
    f32 as_float;
    u8 as_bytes[2][2];
} DataValue;

// 嵌套结构体
typedef struct NestedStruct {
    Point origin;
    Vector vectors[2][4];
    DataValue values[4];
    BitFields flags;
    struct {
        u16 year;
        u8 month;
        u8 day;
    } date;
} NestedStruct;

// 环形缓冲区
typedef struct RingBuffer {
    u8* buffer;
    u32 size;
    u32 read_pos;
    u32 write_pos;
    struct {
        u32 is_full : 1;
        u32 is_empty : 1;
        u32 reserved : 30;
    } status;
} RingBuffer;

// 字符串处理
typedef struct StringView {
    const char* data;
    size_t length;
} StringView;

typedef struct StringBuilder {
    char* buffer;
    size_t capacity;
    size_t length;
} StringBuilder;

// 配置结构体
typedef struct Config {
    struct {
        u32 max_items;
        u32 max_depth;
        f32 threshold;
    } limits;
    
    struct {
        char host[64];
        u16 port;
        u32 timeout_ms;
    } network;
    
    struct {
        u8 level;
        bool enabled;
        char file[256];
    } logging;
    
    void* user_context;
} Config;

// 测试用枚举定义
typedef enum LogLevel {
    LOG_LEVEL_DEBUG = 0,
    LOG_LEVEL_INFO = 1,
    LOG_LEVEL_WARN = 2,
    LOG_LEVEL_ERROR = 3,
    LOG_LEVEL_FATAL = 4
} LogLevel;

typedef enum Direction {
    DIR_NONE = 0,
    DIR_UP = 1 << 0,
    DIR_DOWN = 1 << 1,
    DIR_LEFT = 1 << 2,
    DIR_RIGHT = 1 << 3,
    DIR_ALL = DIR_UP | DIR_DOWN | DIR_LEFT | DIR_RIGHT
} Direction;

// 测试用宏定义
#define MAX_BUFFER_SIZE 1024
#define MIN_BUFFER_SIZE 64
#define DEFAULT_TIMEOUT 5000
#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof((arr)[0]))
#define IS_POWER_OF_TWO(x) (((x) != 0) && (((x) & ((x) - 1)) == 0))
#define ALIGN_UP(x, align) (((x) + ((align) - 1)) & ~((align) - 1))

// 位掩码宏定义
#define FLAG_NONE        0x00000000
#define FLAG_READABLE    0x00000001
#define FLAG_WRITABLE    0x00000002
#define FLAG_EXECUTABLE  0x00000004
#define FLAG_HIDDEN      0x00000008
#define FLAG_SYSTEM      0x00000010
#define FLAG_ALL         0x0000001F

// 版本信息宏定义
#define MAJOR_VERSION 1
#define MINOR_VERSION 0
#define PATCH_VERSION 0
#define VERSION_STRING "1.0.0"

// 错误码定义
typedef enum ErrorCode {
    ERROR_NONE = 0,
    ERROR_INVALID_PARAM = -1,
    ERROR_OUT_OF_MEMORY = -2,
    ERROR_BUFFER_OVERFLOW = -3,
    ERROR_NOT_FOUND = -4,
    ERROR_NOT_SUPPORTED = -5
} ErrorCode;

// 状态码定义
typedef enum Status {
    STATUS_IDLE = 0,
    STATUS_RUNNING,
    STATUS_PAUSED,
    STATUS_STOPPED,
    STATUS_ERROR
} Status;

// 打印函数声明
void print_test_data(void);
void print_point(const Point* p);
void print_vector(const Vector* v);
void print_node(const Node* n);
void print_complex_data(const ComplexData* cd);
void print_bit_fields(const BitFields* bf);
void print_data_value(const DataValue* dv);
void print_nested_struct(const NestedStruct* ns);
void print_ring_buffer(const RingBuffer* rb);
void print_string_view(const StringView* sv);
void print_string_builder(const StringBuilder* sb);
void print_config(const Config* cfg);

// 数值常量宏定义
#define PI              3.14159265359f
#define E               2.71828182846f
#define GOLDEN_RATIO    1.61803398875f
#define SQRT_2          1.41421356237f
#define EPSILON         0.000001f
#define INF             (1.0f / 0.0f)

// 不同进制的整数常量
#define BINARY_CONST    0b10101010
#define OCTAL_CONST     0777
#define HEX_CONST       0xDEADBEEF
#define UNSIGNED_CONST  4294967295UL
#define LONG_CONST      9223372036854775807L
#define ULONG_CONST     18446744073709551615ULL

// 浮点数常量
#define FLOAT_CONST     0.123456f
#define DOUBLE_CONST    0.123456789012345
#define SCIENTIFIC_F    1.23e-4f
#define SCIENTIFIC_D    1.23e-15

// 字符和字符串常量
#define NEWLINE         '\n'
#define TAB             '\t'
#define SINGLE_QUOTE    '\''
#define DOUBLE_QUOTE    '\"'
#define BACKSLASH       '\\'
#define NULL_CHAR       '\0'
#define UTF8_CHAR       '\u00A9'    // copyright symbol

// 字符串常量
#define EMPTY_STR       ""
#define NULL_STR        "\0"
#define ESCAPE_STR      "Hello\tWorld\n"
#define LONG_STR        "This is a very long string that " \
                       "spans multiple lines in the source code"
#define UTF8_STR        "Hello 世界"

// 特殊用途的宏
#define KILOBYTE        (1024UL)
#define MEGABYTE        (1024UL * KILOBYTE)
#define GIGABYTE        (1024UL * MEGABYTE)
#define TERABYTE        (1024ULL * GIGABYTE)

// 位操作宏
#define BIT(x)          (1UL << (x))
#define BITS_SET(x,y)   ((x) |= (y))
#define BITS_CLEAR(x,y) ((x) &= ~(y))
#define BITS_FLIP(x,y)  ((x) ^= (y))
#define BITS_TEST(x,y)  (!!((x) & (y)))

// 数学计算宏
#define MIN(a,b)        ((a) < (b) ? (a) : (b))
#define MAX(a,b)        ((a) > (b) ? (a) : (b))
#define ABS(x)          ((x) < 0 ? -(x) : (x))
#define CLAMP(x,min,max) (MIN(MAX((x), (min)), (max)))
#define SQUARE(x)       ((x) * (x))
#define CUBE(x)         ((x) * (x) * (x))

// 颜色相关宏
#define RGB(r,g,b)      ((u32)((r) << 16) | ((g) << 8) | (b))
#define RGBA(r,g,b,a)   ((u32)((a) << 24) | ((r) << 16) | ((g) << 8) | (b))
#define COLOR_BLACK     0x000000
#define COLOR_WHITE     0xFFFFFF
#define COLOR_RED       0xFF0000
#define COLOR_GREEN     0x00FF00
#define COLOR_BLUE      0X0000FF

// 调试相关宏
#define STRINGIFY(x)    #x
#define TOSTRING(x)     STRINGIFY(x)
#define CONCAT(a,b)     a##b
#define FILE_LINE       __FILE__ ":" TOSTRING(__LINE__)
#define FUNCTION_NAME   __func__

#endif // TEST_STRUCTS_H 
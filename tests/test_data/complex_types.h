/**
 * 复杂类型测试
 */

// 枚举定义
typedef enum {
    RED = 0,
    GREEN = 1,
    BLUE = 2
} Color;

// 位域结构体
typedef struct {
    unsigned int a : 1;
    unsigned int b : 2;
    unsigned int c : 3;
} BitFields;

// 嵌套结构体
typedef struct {
    int x;
    int y;
} Point;

typedef struct {
    Point start;
    Point end;
} Line;

// 数组
typedef struct {
    int numbers[10];
    char name[32];
    Point points[4];
} Arrays;

// 指针
typedef struct {
    int* ptr;
    char* str;
    void* data;
} Pointers; 
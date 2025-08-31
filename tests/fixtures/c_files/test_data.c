#include "test_structs.h"
#include <string.h>
#include <stdio.h>
#include <stdbool.h>

// 创建一些测试用的Point实例 - 使用整体赋值
static Point test_points[] = {
    {0, 0},                // 原点
    {100, 200},            // 正常值
    {-1, -1},              // 负值
    {INT32_MAX, INT32_MIN} // 边界值
};

// 创建一些测试用的Dynamic Point实例 - 使用整体赋值
static Point test_dynamic_points[][5] = {
    {{0, 0}, {1, 1}, {2, 2}, {3, 3}, {4, 4}},
    {{1, 1}, {2, 2}, {3, 3}, {4, 4}, {5, 5}},
    {{2, 2}, {3, 3}, {4, 4}, {5, 5}, {6, 6}},
    {{3, 3}, {4, 4}, {5, 5}, {6, 6}, {7, 7}}};

// 创建Vector测试实例 - 使用位置赋值
static Vector test_vectors[] = {
    // 零向量
    {
        {0.0f, 0.0f, 0.0f},               // components
        {{0, 0}, {0, 0}, {0, 0}, {0, 0}}, // points
        0                                 // count
    },
    // 单位向量
    {
        {1.0f, 1.0f, 1.0f},               // components
        {{1, 1}, {2, 2}, {3, 3}, {4, 4}}, // points
        4                                 // count
    }};

// 创建Vector测试实例 - 使用位置赋值
static Vector test_div2_vectors[2][2] = {
    {
        {{0.0f, 0.0f, 0.0f}, {{0, 0}, {0, 0}, {0, 0}, {0, 0}}, 0},
        {{1.0f, 1.0f, 1.0f}, {{1, 1}, {2, 2}, {3, 3}, {4, 4}}, 4}
    }
};

// 创建链表节点 - 使用位置赋值
static Node test_nodes[] = {
    {1, &test_nodes[1], NULL},
    {2, &test_nodes[2], &test_nodes[0]},
    {3, NULL, &test_nodes[1]}};

// 创建ComplexData测试实例 - 使用位置赋值
static ComplexData test_complex_data = {
    123,                 // id
    "Test Complex Data", // name
    {10, 20},            // position
    &test_vectors[0],    // movement
    test_points,         // targets
    &test_nodes[0],      // head
    {                    // matrix
     {1.0f, 0.0f, 0.0f, 0.0f},
     {0.0f, 1.0f, 0.0f, 0.0f},
     {0.0f, 0.0f, 1.0f, 0.0f},
     {0.0f, 0.0f, 0.0f, 1.0f}},
    NULL,      // extra_data
    0xFFFFFFFF // flags
};

// 创建BitFields测试实例 - 使用整体赋值
static BitFields test_bit_fields[] = {
    {1, 0, 63, 0},
    {0, 1, 0, 0xFFFFFF}};

// 创建DataValue测试实例 - 使用联合体不同成员赋值
static DataValue test_data_values[] = {
    {.as_int = 0x12345678},
    {.as_float = 3.14159f},
    {.as_bytes = {{0x12, 0x34}, {0x56, 0x78}}}};

// 创建NestedStruct测试实例 - 使用位置赋值
static NestedStruct test_nested = {
    {0, 0}, // origin
    {       // vectors[2][4]
     {      // vectors[0]
      {
          // vectors[0][0]
          {1.0f, 2.0f, 3.0f},               // components
          {{0, 0}, {0, 0}, {0, 0}, {0, 0}}, // points
          1                                 // count
      },
      {// vectors[0][1]
       {4.0f, 5.0f, 6.0f},
       {{0, 0}, {0, 0}, {0, 0}, {0, 0}},
       1}},
     { // vectors[1]
      {// vectors[1][0]
       {7.0f, 8.0f, 9.0f},
       {{0, 0}, {0, 0}, {0, 0}, {0, 0}},
       1},
      {// vectors[1][1]
       {10.0f, 11.0f, 12.0f},
       {{0, 0}, {0, 0}, {0, 0}, {0, 0}},
       1}}},
    {// values
     {.as_int = 1},
     {.as_float = 2.0f},
     {.as_int = 3},
     {.as_float = 4.0f}},
    {1, 1, 60, 0}, // flags
    {2024, 3, 20}  // date
};

// 创建RingBuffer测试实例
static u8 buffer_data[256] = {1, 2, 3, 4, 5}; // 预填充一些数据
static RingBuffer test_ring_buffer = {
    buffer_data,         // buffer
    sizeof(buffer_data), // size
    0,                   // read_pos
    5,                   // write_pos
    {0, 0, 0}            // status
};

// 创建StringView测试实例
static const char test_str[] = "Hello, World!";
static StringView test_string_view = {
    test_str,
    sizeof(test_str) - 1};

// 创建StringBuilder测试实例
static char string_buffer[1024] = "Initial content";
static StringBuilder test_string_builder = {
    string_buffer,
    sizeof(string_buffer),
    15 // strlen("Initial content")
};

// 创建Config测试实例
static Config test_config = {
    {1000, 10, 0.75f},          // limits
    {"localhost", 8080, 5000},  // network
    {3, 1, "/var/log/app.log"}, // logging
    NULL                        // user_context
};

// 打印函数声明
void print_point(const Point *p);
void print_vector(const Vector *v);
void print_node(const Node *n);
void print_complex_data(const ComplexData *cd);
void print_bit_fields(const BitFields *bf);
void print_data_value(const DataValue *dv);
void print_nested_struct(const NestedStruct *ns);
void print_ring_buffer(const RingBuffer *rb);
void print_string_view(const StringView *sv);
void print_string_builder(const StringBuilder *sb);
void print_config(const Config *cfg);

// 打印所有测试数据
void print_test_data(void)
{
    printf("\n=== Test Points ===\n");
    for (size_t i = 0; i < sizeof(test_points) / sizeof(test_points[0]); i++)
    {
        printf("Point[%zu]: ", i);
        print_point(&test_points[i]);
    }

    printf("\n=== Test Vectors ===\n");
    for (size_t i = 0; i < sizeof(test_vectors) / sizeof(test_vectors[0]); i++)
    {
        printf("Vector[%zu]:\n", i);
        print_vector(&test_vectors[i]);
    }

    printf("\n=== Test Nodes ===\n");
    const Node *current = &test_nodes[0];
    while (current)
    {
        print_node(current);
        current = current->next;
    }

    printf("\n=== Complex Data ===\n");
    print_complex_data(&test_complex_data);

    printf("\n=== Bit Fields ===\n");
    for (size_t i = 0; i < sizeof(test_bit_fields) / sizeof(test_bit_fields[0]); i++)
    {
        printf("BitFields[%zu]: ", i);
        print_bit_fields(&test_bit_fields[i]);
    }

    printf("\n=== Data Values ===\n");
    for (size_t i = 0; i < sizeof(test_data_values) / sizeof(test_data_values[0]); i++)
    {
        printf("DataValue[%zu]: ", i);
        print_data_value(&test_data_values[i]);
    }

    printf("\n=== Nested Struct ===\n");
    print_nested_struct(&test_nested);

    printf("\n=== Ring Buffer ===\n");
    print_ring_buffer(&test_ring_buffer);

    printf("\n=== String View ===\n");
    print_string_view(&test_string_view);

    printf("\n=== String Builder ===\n");
    print_string_builder(&test_string_builder);

    printf("\n=== Config ===\n");
    print_config(&test_config);
}

// 具体打印函数实现
void print_point(const Point *p)
{
    printf("(%d, %d)\n", p->x, p->y);
}

void print_vector(const Vector *v)
{
    printf("  Components: [%.2f, %.2f, %.2f]\n",
           v->components[0], v->components[1], v->components[2]);
    printf("  Points:\n");
    for (size_t i = 0; i < 4; i++)
    {
        printf("    [%zu]: ", i);
        print_point(&v->points[i]);
    }
    printf("  Count: %u\n", v->count);
}

void print_node(const Node *n)
{
    printf("Node(value=%d, prev=%p, next=%p)\n",
           n->value, (void *)n->prev, (void *)n->next);
}

void print_complex_data(const ComplexData *cd)
{
    printf("ID: %u\n", cd->id);
    printf("Name: %s\n", cd->name);
    printf("Position: ");
    print_point(&cd->position);
    printf("Matrix:\n");
    for (int i = 0; i < 4; i++)
    {
        printf("  [");
        for (int j = 0; j < 4; j++)
        {
            printf("%.2f ", cd->matrix[i][j]);
        }
        printf("]\n");
    }
    printf("Flags: 0x%08X\n", cd->flags);
}

void print_bit_fields(const BitFields *bf)
{
    printf("flag1=%u, flag2=%u, value=%u, reserved=0x%06X\n",
           bf->flag1, bf->flag2, bf->value, bf->reserved);
}

void print_data_value(const DataValue *dv)
{
    printf("as_int=0x%08X, as_float=%.6f, bytes={{0x%02X,0x%02X},{0x%02X,0x%02X}}\n",
           dv->as_int, dv->as_float,
           dv->as_bytes[0][0], dv->as_bytes[0][1],
           dv->as_bytes[1][0], dv->as_bytes[1][1]);
}

void print_nested_struct(const NestedStruct *ns)
{
    printf("Origin: ");
    print_point(&ns->origin);
    printf("Date: %u-%02u-%02u\n",
           ns->date.year, ns->date.month, ns->date.day);
}

void print_ring_buffer(const RingBuffer *rb)
{
    printf("Size: %u, Read: %u, Write: %u\n",
           rb->size, rb->read_pos, rb->write_pos);
    printf("Status: full=%u, empty=%u\n",
           rb->status.is_full, rb->status.is_empty);
}

void print_string_view(const StringView *sv)
{
    printf("Data: \"%.*s\", Length: %zu\n",
           (int)sv->length, sv->data, sv->length);
}

void print_string_builder(const StringBuilder *sb)
{
    printf("Buffer: \"%s\", Length: %zu, Capacity: %zu\n",
           sb->buffer, sb->length, sb->capacity);
}

void print_config(const Config *cfg)
{
    printf("Limits:\n");
    printf("  Max Items: %u\n", cfg->limits.max_items);
    printf("  Max Depth: %u\n", cfg->limits.max_depth);
    printf("  Threshold: %.2f\n", cfg->limits.threshold);
    printf("Network:\n");
    printf("  Host: %s\n", cfg->network.host);
    printf("  Port: %u\n", cfg->network.port);
    printf("  Timeout: %u ms\n", cfg->network.timeout_ms);
    printf("Logging:\n");
    printf("  Level: %u\n", cfg->logging.level);
    printf("  Enabled: %s\n", cfg->logging.enabled ? "yes" : "no");
    printf("  File: %s\n", cfg->logging.file);
}
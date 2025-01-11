#ifndef STRUCT_CONVERTER_H
#define STRUCT_CONVERTER_H

// 结构体转换配置
// 设置为1启用相应结构体的转换功能

#define ENABLE_BITFIELDS_CONVERTER 1  // 默认启用
#define ENABLE_COMPLEXDATA_CONVERTER 1  // 默认启用
#define ENABLE_CONFIG_CONVERTER 1  // 默认启用
#define ENABLE_NESTEDSTRUCT_CONVERTER 1  // 默认启用
#define ENABLE_NODE_CONVERTER 1  // 默认启用
#define ENABLE_POINT_CONVERTER 1  // 默认启用
#define ENABLE_RINGBUFFER_CONVERTER 1  // 默认启用
#define ENABLE_STRINGBUILDER_CONVERTER 1  // 默认启用
#define ENABLE_STRINGVIEW_CONVERTER 1  // 默认启用
#define ENABLE_VECTOR_CONVERTER 1  // 默认启用

// 结构体依赖关系检查

#if ENABLE_COMPLEXDATA_CONVERTER
#if !ENABLE_NODE_CONVERTER
#error struct ComplexData converter requires Node converter to be enabled
#endif
#if !ENABLE_POINT_CONVERTER
#error struct ComplexData converter requires Point converter to be enabled
#endif
#if !ENABLE_VECTOR_CONVERTER
#error struct ComplexData converter requires Vector converter to be enabled
#endif
#endif

#if ENABLE_VECTOR_CONVERTER
#if !ENABLE_POINT_CONVERTER
#error struct Vector converter requires Point converter to be enabled
#endif
#endif

#if ENABLE_NESTEDSTRUCT_CONVERTER
#if !ENABLE_BITFIELDS_CONVERTER
#error struct NestedStruct converter requires BitFields converter to be enabled
#endif
#if !ENABLE_POINT_CONVERTER
#error struct NestedStruct converter requires Point converter to be enabled
#endif
#if !ENABLE_VECTOR_CONVERTER
#error struct NestedStruct converter requires Vector converter to be enabled
#endif
#endif

#include <cjson/cJSON.h>
#include <stddef.h>
#include <stdbool.h>

// 转换状态码
typedef enum {
    CONVERT_SUCCESS = 0,
    CONVERT_MALLOC_ERROR,
    CONVERT_PARSE_ERROR,
    CONVERT_INVALID_PARAM
} convert_status_t;

// 数组转换辅助函数宏定义
#define DECLARE_ARRAY_CONVERTERS(type) \
    cJSON* type##_array_to_json(const type* data, const type* default_data, size_t size); \
    convert_status_t json_to_##type##_array(const cJSON* json, const type* default_data, type* data, size_t size);

// 结构体转换函数声明

#if ENABLE_BITFIELDS_CONVERTER

// BitFields 转换函数
cJSON* bitfields_to_json(const struct BitFields* data, const struct BitFields* default_data);
convert_status_t json_to_bitfields(const cJSON* json, const struct BitFields* default_data, struct BitFields* data);

// BitFields 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct BitFields)

// BitFields 打印函数
void print_bitfields(const struct BitFields* data);

#endif  // ENABLE_BITFIELDS_CONVERTER


#if ENABLE_NODE_CONVERTER

// Node 转换函数
cJSON* node_to_json(const struct Node* data, const struct Node* default_data);
convert_status_t json_to_node(const cJSON* json, const struct Node* default_data, struct Node* data);

// Node 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct Node)

// Node 打印函数
void print_node(const struct Node* data);

#endif  // ENABLE_NODE_CONVERTER


#if ENABLE_POINT_CONVERTER

// Point 转换函数
cJSON* point_to_json(const struct Point* data, const struct Point* default_data);
convert_status_t json_to_point(const cJSON* json, const struct Point* default_data, struct Point* data);

// Point 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct Point)

// Point 打印函数
void print_point(const struct Point* data);

#endif  // ENABLE_POINT_CONVERTER


#if ENABLE_VECTOR_CONVERTER

// Vector 转换函数
cJSON* vector_to_json(const struct Vector* data, const struct Vector* default_data);
convert_status_t json_to_vector(const cJSON* json, const struct Vector* default_data, struct Vector* data);

// Vector 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct Vector)

// Vector 打印函数
void print_vector(const struct Vector* data);

#endif  // ENABLE_VECTOR_CONVERTER


#if ENABLE_COMPLEXDATA_CONVERTER

// ComplexData 转换函数
cJSON* complexdata_to_json(const struct ComplexData* data, const struct ComplexData* default_data);
convert_status_t json_to_complexdata(const cJSON* json, const struct ComplexData* default_data, struct ComplexData* data);

// ComplexData 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct ComplexData)

// ComplexData 打印函数
void print_complexdata(const struct ComplexData* data);

#endif  // ENABLE_COMPLEXDATA_CONVERTER


#if ENABLE_CONFIG_CONVERTER

// Config 转换函数
cJSON* config_to_json(const struct Config* data, const struct Config* default_data);
convert_status_t json_to_config(const cJSON* json, const struct Config* default_data, struct Config* data);

// Config 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct Config)

// Config 打印函数
void print_config(const struct Config* data);

#endif  // ENABLE_CONFIG_CONVERTER


#if ENABLE_NESTEDSTRUCT_CONVERTER

// NestedStruct 转换函数
cJSON* nestedstruct_to_json(const struct NestedStruct* data, const struct NestedStruct* default_data);
convert_status_t json_to_nestedstruct(const cJSON* json, const struct NestedStruct* default_data, struct NestedStruct* data);

// NestedStruct 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct NestedStruct)

// NestedStruct 打印函数
void print_nestedstruct(const struct NestedStruct* data);

#endif  // ENABLE_NESTEDSTRUCT_CONVERTER


#if ENABLE_RINGBUFFER_CONVERTER

// RingBuffer 转换函数
cJSON* ringbuffer_to_json(const struct RingBuffer* data, const struct RingBuffer* default_data);
convert_status_t json_to_ringbuffer(const cJSON* json, const struct RingBuffer* default_data, struct RingBuffer* data);

// RingBuffer 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct RingBuffer)

// RingBuffer 打印函数
void print_ringbuffer(const struct RingBuffer* data);

#endif  // ENABLE_RINGBUFFER_CONVERTER


#if ENABLE_STRINGBUILDER_CONVERTER

// StringBuilder 转换函数
cJSON* stringbuilder_to_json(const struct StringBuilder* data, const struct StringBuilder* default_data);
convert_status_t json_to_stringbuilder(const cJSON* json, const struct StringBuilder* default_data, struct StringBuilder* data);

// StringBuilder 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct StringBuilder)

// StringBuilder 打印函数
void print_stringbuilder(const struct StringBuilder* data);

#endif  // ENABLE_STRINGBUILDER_CONVERTER


#if ENABLE_STRINGVIEW_CONVERTER

// StringView 转换函数
cJSON* stringview_to_json(const struct StringView* data, const struct StringView* default_data);
convert_status_t json_to_stringview(const cJSON* json, const struct StringView* default_data, struct StringView* data);

// StringView 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct StringView)

// StringView 打印函数
void print_stringview(const struct StringView* data);

#endif  // ENABLE_STRINGVIEW_CONVERTER


#endif // STRUCT_CONVERTER_H
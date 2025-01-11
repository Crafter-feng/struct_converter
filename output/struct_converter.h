#ifndef STRUCT_CONVERTER_H
#define STRUCT_CONVERTER_H

// 结构体转换配置
// 设置为1启用相应结构体的转换功能

#define ENABLE_STRUCT_BITFIELDS_CONVERTER 1  // 默认启用
#define ENABLE_STRUCT_COMPLEXDATA_CONVERTER 1  // 默认启用
#define ENABLE_STRUCT_CONFIG_CONVERTER 1  // 默认启用
#define ENABLE_STRUCT_NESTEDSTRUCT_CONVERTER 1  // 默认启用
#define ENABLE_STRUCT_NODE_CONVERTER 1  // 默认启用
#define ENABLE_STRUCT_POINT_CONVERTER 1  // 默认启用
#define ENABLE_STRUCT_RINGBUFFER_CONVERTER 1  // 默认启用
#define ENABLE_STRUCT_STRINGBUILDER_CONVERTER 1  // 默认启用
#define ENABLE_STRUCT_STRINGVIEW_CONVERTER 1  // 默认启用
#define ENABLE_STRUCT_VECTOR_CONVERTER 1  // 默认启用

// 结构体依赖关系检查

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

#if ENABLE_STRUCT_BITFIELDS_CONVERTER

// struct struct BitFields 转换函数
cJSON* struct_struct bitfields_to_json(const struct struct BitFields* data, const struct struct BitFields* default_data);
convert_status_t json_to_struct_struct bitfields(const cJSON* json, const struct struct BitFields* default_data, struct struct BitFields* data);

// struct struct BitFields 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct struct BitFields)

#endif  // ENABLE_STRUCT_BITFIELDS_CONVERTER


#if ENABLE_STRUCT_COMPLEXDATA_CONVERTER

// struct struct ComplexData 转换函数
cJSON* struct_struct complexdata_to_json(const struct struct ComplexData* data, const struct struct ComplexData* default_data);
convert_status_t json_to_struct_struct complexdata(const cJSON* json, const struct struct ComplexData* default_data, struct struct ComplexData* data);

// struct struct ComplexData 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct struct ComplexData)

#endif  // ENABLE_STRUCT_COMPLEXDATA_CONVERTER


#if ENABLE_STRUCT_CONFIG_CONVERTER

// struct struct Config 转换函数
cJSON* struct_struct config_to_json(const struct struct Config* data, const struct struct Config* default_data);
convert_status_t json_to_struct_struct config(const cJSON* json, const struct struct Config* default_data, struct struct Config* data);

// struct struct Config 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct struct Config)

#endif  // ENABLE_STRUCT_CONFIG_CONVERTER


#if ENABLE_STRUCT_NESTEDSTRUCT_CONVERTER

// struct struct NestedStruct 转换函数
cJSON* struct_struct nestedstruct_to_json(const struct struct NestedStruct* data, const struct struct NestedStruct* default_data);
convert_status_t json_to_struct_struct nestedstruct(const cJSON* json, const struct struct NestedStruct* default_data, struct struct NestedStruct* data);

// struct struct NestedStruct 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct struct NestedStruct)

#endif  // ENABLE_STRUCT_NESTEDSTRUCT_CONVERTER


#if ENABLE_STRUCT_NODE_CONVERTER

// struct struct Node 转换函数
cJSON* struct_struct node_to_json(const struct struct Node* data, const struct struct Node* default_data);
convert_status_t json_to_struct_struct node(const cJSON* json, const struct struct Node* default_data, struct struct Node* data);

// struct struct Node 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct struct Node)

#endif  // ENABLE_STRUCT_NODE_CONVERTER


#if ENABLE_STRUCT_POINT_CONVERTER

// struct struct Point 转换函数
cJSON* struct_struct point_to_json(const struct struct Point* data, const struct struct Point* default_data);
convert_status_t json_to_struct_struct point(const cJSON* json, const struct struct Point* default_data, struct struct Point* data);

// struct struct Point 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct struct Point)

#endif  // ENABLE_STRUCT_POINT_CONVERTER


#if ENABLE_STRUCT_RINGBUFFER_CONVERTER

// struct struct RingBuffer 转换函数
cJSON* struct_struct ringbuffer_to_json(const struct struct RingBuffer* data, const struct struct RingBuffer* default_data);
convert_status_t json_to_struct_struct ringbuffer(const cJSON* json, const struct struct RingBuffer* default_data, struct struct RingBuffer* data);

// struct struct RingBuffer 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct struct RingBuffer)

#endif  // ENABLE_STRUCT_RINGBUFFER_CONVERTER


#if ENABLE_STRUCT_STRINGBUILDER_CONVERTER

// struct struct StringBuilder 转换函数
cJSON* struct_struct stringbuilder_to_json(const struct struct StringBuilder* data, const struct struct StringBuilder* default_data);
convert_status_t json_to_struct_struct stringbuilder(const cJSON* json, const struct struct StringBuilder* default_data, struct struct StringBuilder* data);

// struct struct StringBuilder 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct struct StringBuilder)

#endif  // ENABLE_STRUCT_STRINGBUILDER_CONVERTER


#if ENABLE_STRUCT_STRINGVIEW_CONVERTER

// struct struct StringView 转换函数
cJSON* struct_struct stringview_to_json(const struct struct StringView* data, const struct struct StringView* default_data);
convert_status_t json_to_struct_struct stringview(const cJSON* json, const struct struct StringView* default_data, struct struct StringView* data);

// struct struct StringView 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct struct StringView)

#endif  // ENABLE_STRUCT_STRINGVIEW_CONVERTER


#if ENABLE_STRUCT_VECTOR_CONVERTER

// struct struct Vector 转换函数
cJSON* struct_struct vector_to_json(const struct struct Vector* data, const struct struct Vector* default_data);
convert_status_t json_to_struct_struct vector(const cJSON* json, const struct struct Vector* default_data, struct struct Vector* data);

// struct struct Vector 数组转换函数
DECLARE_ARRAY_CONVERTERS(struct struct Vector)

#endif  // ENABLE_STRUCT_VECTOR_CONVERTER


#endif // STRUCT_CONVERTER_H
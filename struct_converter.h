#ifndef STRUCT_CONVERTER_H
#define STRUCT_CONVERTER_H

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

// 转换函数声明

// [START_BITFIELDS_HEADER_INTERFACE]

// BitFields 转换函数
cJSON* bitfields_to_json(const BitFields* data, const BitFields* default_data);
convert_status_t json_to_bitfields(const cJSON* json, const BitFields* default_data, BitFields* data);

// BitFields 数组转换函数
DECLARE_ARRAY_CONVERTERS(BitFields)
// [END_BITFIELDS_HEADER_INTERFACE]

// [START_COMPLEXDATA_HEADER_INTERFACE]

// ComplexData 转换函数
cJSON* complexdata_to_json(const ComplexData* data, const ComplexData* default_data);
convert_status_t json_to_complexdata(const cJSON* json, const ComplexData* default_data, ComplexData* data);

// ComplexData 数组转换函数
DECLARE_ARRAY_CONVERTERS(ComplexData)
// [END_COMPLEXDATA_HEADER_INTERFACE]

// [START_CONFIG_HEADER_INTERFACE]

// Config 转换函数
cJSON* config_to_json(const Config* data, const Config* default_data);
convert_status_t json_to_config(const cJSON* json, const Config* default_data, Config* data);

// Config 数组转换函数
DECLARE_ARRAY_CONVERTERS(Config)
// [END_CONFIG_HEADER_INTERFACE]

// [START_NESTEDSTRUCT_HEADER_INTERFACE]

// NestedStruct 转换函数
cJSON* nestedstruct_to_json(const NestedStruct* data, const NestedStruct* default_data);
convert_status_t json_to_nestedstruct(const cJSON* json, const NestedStruct* default_data, NestedStruct* data);

// NestedStruct 数组转换函数
DECLARE_ARRAY_CONVERTERS(NestedStruct)
// [END_NESTEDSTRUCT_HEADER_INTERFACE]

// [START_NODE_HEADER_INTERFACE]

// Node 转换函数
cJSON* node_to_json(const Node* data, const Node* default_data);
convert_status_t json_to_node(const cJSON* json, const Node* default_data, Node* data);

// Node 数组转换函数
DECLARE_ARRAY_CONVERTERS(Node)
// [END_NODE_HEADER_INTERFACE]

// [START_POINT_HEADER_INTERFACE]

// Point 转换函数
cJSON* point_to_json(const Point* data, const Point* default_data);
convert_status_t json_to_point(const cJSON* json, const Point* default_data, Point* data);

// Point 数组转换函数
DECLARE_ARRAY_CONVERTERS(Point)
// [END_POINT_HEADER_INTERFACE]

// [START_RINGBUFFER_HEADER_INTERFACE]

// RingBuffer 转换函数
cJSON* ringbuffer_to_json(const RingBuffer* data, const RingBuffer* default_data);
convert_status_t json_to_ringbuffer(const cJSON* json, const RingBuffer* default_data, RingBuffer* data);

// RingBuffer 数组转换函数
DECLARE_ARRAY_CONVERTERS(RingBuffer)
// [END_RINGBUFFER_HEADER_INTERFACE]

// [START_STRINGBUILDER_HEADER_INTERFACE]

// StringBuilder 转换函数
cJSON* stringbuilder_to_json(const StringBuilder* data, const StringBuilder* default_data);
convert_status_t json_to_stringbuilder(const cJSON* json, const StringBuilder* default_data, StringBuilder* data);

// StringBuilder 数组转换函数
DECLARE_ARRAY_CONVERTERS(StringBuilder)
// [END_STRINGBUILDER_HEADER_INTERFACE]

// [START_STRINGVIEW_HEADER_INTERFACE]

// StringView 转换函数
cJSON* stringview_to_json(const StringView* data, const StringView* default_data);
convert_status_t json_to_stringview(const cJSON* json, const StringView* default_data, StringView* data);

// StringView 数组转换函数
DECLARE_ARRAY_CONVERTERS(StringView)
// [END_STRINGVIEW_HEADER_INTERFACE]

// [START_VECTOR_HEADER_INTERFACE]

// Vector 转换函数
cJSON* vector_to_json(const Vector* data, const Vector* default_data);
convert_status_t json_to_vector(const cJSON* json, const Vector* default_data, Vector* data);

// Vector 数组转换函数
DECLARE_ARRAY_CONVERTERS(Vector)
// [END_VECTOR_HEADER_INTERFACE]

#endif // STRUCT_CONVERTER_H
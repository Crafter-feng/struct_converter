#include "struct_converter.h"
#include <string.h>
#include <stdlib.h>

// 数组转换辅助宏
#define DEFINE_ARRAY_CONVERTERS(type) \
cJSON* type##_array_to_json(const type* data, const type* default_data, size_t size) { \
    if (!data) return NULL; \
    cJSON* array = cJSON_CreateArray(); \
    if (!array) return NULL; \
    for (size_t i = 0; i < size; i++) { \
        cJSON* item = type##_to_json(&data[i], default_data ? &default_data[i] : NULL); \
        if (item) { \
            cJSON_AddItemToArray(array, item); \
        } \
    } \
    return array; \
} \
\
convert_status_t json_to_##type##_array(const cJSON* json, const type* default_data, type* data, size_t size) { \
    if (!json || !data) return CONVERT_INVALID_PARAM; \
    if (!cJSON_IsArray(json)) return CONVERT_PARSE_ERROR; \
    size_t json_size = cJSON_GetArraySize(json); \
    size_t copy_size = (json_size < size) ? json_size : size; \
    for (size_t i = 0; i < copy_size; i++) { \
        cJSON* item = cJSON_GetArrayItem(json, i); \
        convert_status_t status = json_to_##type(item, default_data ? &default_data[i] : NULL, &data[i]); \
        if (status != CONVERT_SUCCESS) return status; \
    } \
    if (default_data && json_size < size) { \
        for (size_t i = json_size; i < size; i++) { \
            data[i] = default_data[i]; \
        } \
    } \
    return CONVERT_SUCCESS; \
}
#if ENABLE_POINT_CONVERTER

DEFINE_ARRAY_CONVERTERS(struct Point)

cJSON* point_to_json(const struct Point* data, const struct Point* default_data) {
    if (!data) return NULL;
    cJSON* root = cJSON_CreateObject();
    if (!root) return NULL;

    // 处理i32类型字段 x
    if (!default_data || data->x != default_data->x) {
        cJSON_AddNumberToObject(root, "x", data->x);
    }

    // 处理i32类型字段 y
    if (!default_data || data->y != default_data->y) {
        cJSON_AddNumberToObject(root, "y", data->y);
    }

    return root;
}

convert_status_t json_to_point(const cJSON* json, const struct Point* default_data, struct Point* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 x 字段
    cJSON* x_json = cJSON_GetObjectItem(json, "x");
    if (x_json && cJSON_IsNumber(x_json)) {
        data->x = x_json->valueint;
    }

    // 处理 y 字段
    cJSON* y_json = cJSON_GetObjectItem(json, "y");
    if (y_json && cJSON_IsNumber(y_json)) {
        data->y = y_json->valueint;
    }

    return CONVERT_SUCCESS;
}

// 打印函数
void print_point(const struct Point* data) {
    if (!data) {
        printf("NULL\n");
        return;
    }

    printf("struct Point {\n");
    printf("    x: ");
    printf(%d, data->x);
    printf("\n");
    printf("    y: ");
    printf(%d, data->y);
    printf("\n");
    printf("}\n");
}

#endif  // ENABLE_POINT_CONVERTER
#if ENABLE_RINGBUFFER_CONVERTER

DEFINE_ARRAY_CONVERTERS(struct RingBuffer)

cJSON* ringbuffer_to_json(const struct RingBuffer* data, const struct RingBuffer* default_data) {
    if (!data) return NULL;
    cJSON* root = cJSON_CreateObject();
    if (!root) return NULL;

    // 处理u8*类型字段 buffer
    if (!default_data || data->buffer != default_data->buffer) {
        cJSON_AddNumberToObject(root, "buffer", data->buffer);
    }

    // 处理u32类型字段 size
    if (!default_data || data->size != default_data->size) {
        cJSON_AddNumberToObject(root, "size", data->size);
    }

    // 处理u32类型字段 read_pos
    if (!default_data || data->read_pos != default_data->read_pos) {
        cJSON_AddNumberToObject(root, "read_pos", data->read_pos);
    }

    // 处理u32类型字段 write_pos
    if (!default_data || data->write_pos != default_data->write_pos) {
        cJSON_AddNumberToObject(root, "write_pos", data->write_pos);
    }

    // 处理struct类型字段 status
    if (!default_data || data->status != default_data->status) {
        cJSON_AddNumberToObject(root, "status", data->status);
    }

    return root;
}

convert_status_t json_to_ringbuffer(const cJSON* json, const struct RingBuffer* default_data, struct RingBuffer* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 buffer 字段
    cJSON* buffer_json = cJSON_GetObjectItem(json, "buffer");
    if (buffer_json && cJSON_IsNumber(buffer_json)) {
        data->buffer = buffer_json->valueint;
    }

    // 处理 size 字段
    cJSON* size_json = cJSON_GetObjectItem(json, "size");
    if (size_json && cJSON_IsNumber(size_json)) {
        data->size = size_json->valueint;
    }

    // 处理 read_pos 字段
    cJSON* read_pos_json = cJSON_GetObjectItem(json, "read_pos");
    if (read_pos_json && cJSON_IsNumber(read_pos_json)) {
        data->read_pos = read_pos_json->valueint;
    }

    // 处理 write_pos 字段
    cJSON* write_pos_json = cJSON_GetObjectItem(json, "write_pos");
    if (write_pos_json && cJSON_IsNumber(write_pos_json)) {
        data->write_pos = write_pos_json->valueint;
    }

    // 处理 status 字段
    cJSON* status_json = cJSON_GetObjectItem(json, "status");
    if (status_json && cJSON_IsNumber(status_json)) {
        data->status = status_json->valueint;
    }

    return CONVERT_SUCCESS;
}

// 打印函数
void print_ringbuffer(const struct RingBuffer* data) {
    if (!data) {
        printf("NULL\n");
        return;
    }

    printf("struct RingBuffer {\n");
    printf("    buffer: ");
    printf(%u, data->buffer);
    printf("\n");
    printf("    size: ");
    printf(%u, data->size);
    printf("\n");
    printf("    read_pos: ");
    printf(%u, data->read_pos);
    printf("\n");
    printf("    write_pos: ");
    printf(%u, data->write_pos);
    printf("\n");
    printf("    status: ");
    printf("0x%x", data->status);
    printf("\n");
    printf("}\n");
}

#endif  // ENABLE_RINGBUFFER_CONVERTER
#if ENABLE_BITFIELDS_CONVERTER

DEFINE_ARRAY_CONVERTERS(struct BitFields)

cJSON* bitfields_to_json(const struct BitFields* data, const struct BitFields* default_data) {
    if (!data) return NULL;
    cJSON* root = cJSON_CreateObject();
    if (!root) return NULL;

    // 处理u32类型字段 flag1
    if (!default_data || data->flag1 != default_data->flag1) {
        cJSON_AddNumberToObject(root, "flag1", data->flag1);
    }

    // 处理u32类型字段 flag2
    if (!default_data || data->flag2 != default_data->flag2) {
        cJSON_AddNumberToObject(root, "flag2", data->flag2);
    }

    // 处理u32类型字段 value
    if (!default_data || data->value != default_data->value) {
        cJSON_AddNumberToObject(root, "value", data->value);
    }

    // 处理u32类型字段 reserved
    if (!default_data || data->reserved != default_data->reserved) {
        cJSON_AddNumberToObject(root, "reserved", data->reserved);
    }

    return root;
}

convert_status_t json_to_bitfields(const cJSON* json, const struct BitFields* default_data, struct BitFields* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 flag1 字段
    cJSON* flag1_json = cJSON_GetObjectItem(json, "flag1");
    if (flag1_json && cJSON_IsNumber(flag1_json)) {
        data->flag1 = flag1_json->valueint;
    }

    // 处理 flag2 字段
    cJSON* flag2_json = cJSON_GetObjectItem(json, "flag2");
    if (flag2_json && cJSON_IsNumber(flag2_json)) {
        data->flag2 = flag2_json->valueint;
    }

    // 处理 value 字段
    cJSON* value_json = cJSON_GetObjectItem(json, "value");
    if (value_json && cJSON_IsNumber(value_json)) {
        data->value = value_json->valueint;
    }

    // 处理 reserved 字段
    cJSON* reserved_json = cJSON_GetObjectItem(json, "reserved");
    if (reserved_json && cJSON_IsNumber(reserved_json)) {
        data->reserved = reserved_json->valueint;
    }

    return CONVERT_SUCCESS;
}

// 打印函数
void print_bitfields(const struct BitFields* data) {
    if (!data) {
        printf("NULL\n");
        return;
    }

    printf("struct BitFields {\n");
    printf("    flag1: ");
    printf(%u, data->flag1);
    printf("\n");
    printf("    flag2: ");
    printf(%u, data->flag2);
    printf("\n");
    printf("    value: ");
    printf(%u, data->value);
    printf("\n");
    printf("    reserved: ");
    printf(%u, data->reserved);
    printf("\n");
    printf("}\n");
}

#endif  // ENABLE_BITFIELDS_CONVERTER
#if ENABLE_STRINGBUILDER_CONVERTER

DEFINE_ARRAY_CONVERTERS(struct StringBuilder)

cJSON* stringbuilder_to_json(const struct StringBuilder* data, const struct StringBuilder* default_data) {
    if (!data) return NULL;
    cJSON* root = cJSON_CreateObject();
    if (!root) return NULL;

    // 处理char*类型字段 buffer
    if (!default_data || data->buffer != default_data->buffer) {
        cJSON_AddNumberToObject(root, "buffer", data->buffer);
    }

    // 处理size_t类型字段 capacity
    if (!default_data || data->capacity != default_data->capacity) {
        cJSON_AddNumberToObject(root, "capacity", data->capacity);
    }

    // 处理size_t类型字段 length
    if (!default_data || data->length != default_data->length) {
        cJSON_AddNumberToObject(root, "length", data->length);
    }

    return root;
}

convert_status_t json_to_stringbuilder(const cJSON* json, const struct StringBuilder* default_data, struct StringBuilder* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 buffer 字段
    cJSON* buffer_json = cJSON_GetObjectItem(json, "buffer");
    if (buffer_json && cJSON_IsNumber(buffer_json)) {
        data->buffer = buffer_json->valueint;
    }

    // 处理 capacity 字段
    cJSON* capacity_json = cJSON_GetObjectItem(json, "capacity");
    if (capacity_json && cJSON_IsNumber(capacity_json)) {
        data->capacity = capacity_json->valueint;
    }

    // 处理 length 字段
    cJSON* length_json = cJSON_GetObjectItem(json, "length");
    if (length_json && cJSON_IsNumber(length_json)) {
        data->length = length_json->valueint;
    }

    return CONVERT_SUCCESS;
}

// 打印函数
void print_stringbuilder(const struct StringBuilder* data) {
    if (!data) {
        printf("NULL\n");
        return;
    }

    printf("struct StringBuilder {\n");
    printf("    buffer: ");
    printf("%c", data->buffer);
    printf("\n");
    printf("    capacity: ");
    printf(%zu, data->capacity);
    printf("\n");
    printf("    length: ");
    printf(%zu, data->length);
    printf("\n");
    printf("}\n");
}

#endif  // ENABLE_STRINGBUILDER_CONVERTER
#if ENABLE_COMPLEXDATA_CONVERTER

DEFINE_ARRAY_CONVERTERS(struct ComplexData)

cJSON* complexdata_to_json(const struct ComplexData* data, const struct ComplexData* default_data) {
    if (!data) return NULL;
    cJSON* root = cJSON_CreateObject();
    if (!root) return NULL;

    // 处理u8类型字段 id
    if (!default_data || data->id != default_data->id) {
        cJSON_AddNumberToObject(root, "id", data->id);
    }

    // 处理char类型字段 name
    if (!default_data || data->name != default_data->name) {
        cJSON_AddNumberToObject(root, "name", data->name);
    }

    // 处理Point类型字段 position
    if (!default_data || data->position != default_data->position) {
        cJSON_AddNumberToObject(root, "position", data->position);
    }

    // 处理Vector*类型字段 movement
    if (!default_data || data->movement != default_data->movement) {
        cJSON_AddNumberToObject(root, "movement", data->movement);
    }

    // 处理PointPtr类型字段 targets
    if (!default_data || data->targets != default_data->targets) {
        cJSON_AddNumberToObject(root, "targets", data->targets);
    }

    // 处理Node*类型字段 head
    if (!default_data || data->head != default_data->head) {
        cJSON_AddNumberToObject(root, "head", data->head);
    }

    // 处理f32类型字段 matrix
    if (!default_data || data->matrix != default_data->matrix) {
        cJSON_AddNumberToObject(root, "matrix", data->matrix);
    }

    // 处理void*类型字段 extra_data
    if (!default_data || data->extra_data != default_data->extra_data) {
        cJSON_AddNumberToObject(root, "extra_data", data->extra_data);
    }

    // 处理u32类型字段 flags
    if (!default_data || data->flags != default_data->flags) {
        cJSON_AddNumberToObject(root, "flags", data->flags);
    }

    return root;
}

convert_status_t json_to_complexdata(const cJSON* json, const struct ComplexData* default_data, struct ComplexData* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 id 字段
    cJSON* id_json = cJSON_GetObjectItem(json, "id");
    if (id_json && cJSON_IsNumber(id_json)) {
        data->id = id_json->valueint;
    }

    // 处理 name 字段
    cJSON* name_json = cJSON_GetObjectItem(json, "name");
    if (name_json && cJSON_IsNumber(name_json)) {
        data->name = name_json->valueint;
    }

    // 处理 position 字段
    cJSON* position_json = cJSON_GetObjectItem(json, "position");
    if (position_json && cJSON_IsNumber(position_json)) {
        data->position = position_json->valueint;
    }

    // 处理 movement 字段
    cJSON* movement_json = cJSON_GetObjectItem(json, "movement");
    if (movement_json && cJSON_IsNumber(movement_json)) {
        data->movement = movement_json->valueint;
    }

    // 处理 targets 字段
    cJSON* targets_json = cJSON_GetObjectItem(json, "targets");
    if (targets_json && cJSON_IsNumber(targets_json)) {
        data->targets = targets_json->valueint;
    }

    // 处理 head 字段
    cJSON* head_json = cJSON_GetObjectItem(json, "head");
    if (head_json && cJSON_IsNumber(head_json)) {
        data->head = head_json->valueint;
    }

    // 处理 matrix 字段
    cJSON* matrix_json = cJSON_GetObjectItem(json, "matrix");
    if (matrix_json && cJSON_IsNumber(matrix_json)) {
        data->matrix = matrix_json->valueint;
    }

    // 处理 extra_data 字段
    cJSON* extra_data_json = cJSON_GetObjectItem(json, "extra_data");
    if (extra_data_json && cJSON_IsNumber(extra_data_json)) {
        data->extra_data = extra_data_json->valueint;
    }

    // 处理 flags 字段
    cJSON* flags_json = cJSON_GetObjectItem(json, "flags");
    if (flags_json && cJSON_IsNumber(flags_json)) {
        data->flags = flags_json->valueint;
    }

    return CONVERT_SUCCESS;
}

// 打印函数
void print_complexdata(const struct ComplexData* data) {
    if (!data) {
        printf("NULL\n");
        return;
    }

    printf("struct ComplexData {\n");
    printf("    id: ");
    printf(%u, data->id);
    printf("\n");
    printf("    name: ");
    printf("%c", data->name);
    printf("\n");
    printf("    position: ");
    printf("\n");
    print_point(&data->position);
    printf("    movement: ");
    printf("\n");
    print_vector(&data->movement);
    printf("    targets: ");
    printf("0x%p", data->targets);
    printf("\n");
    printf("    head: ");
    printf("\n");
    print_node(&data->head);
    printf("    matrix: ");
    printf(%.6f, data->matrix);
    printf("\n");
    printf("    extra_data: ");
    printf("0x%x", data->extra_data);
    printf("\n");
    printf("    flags: ");
    printf(%u, data->flags);
    printf("\n");
    printf("}\n");
}

#endif  // ENABLE_COMPLEXDATA_CONVERTER
#if ENABLE_VECTOR_CONVERTER

DEFINE_ARRAY_CONVERTERS(struct Vector)

cJSON* vector_to_json(const struct Vector* data, const struct Vector* default_data) {
    if (!data) return NULL;
    cJSON* root = cJSON_CreateObject();
    if (!root) return NULL;

    // 处理f32类型字段 components
    if (!default_data || data->components != default_data->components) {
        cJSON_AddNumberToObject(root, "components", data->components);
    }

    // 处理Point类型字段 points
    if (!default_data || data->points != default_data->points) {
        cJSON_AddNumberToObject(root, "points", data->points);
    }

    // 处理u32类型字段 count
    if (!default_data || data->count != default_data->count) {
        cJSON_AddNumberToObject(root, "count", data->count);
    }

    return root;
}

convert_status_t json_to_vector(const cJSON* json, const struct Vector* default_data, struct Vector* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 components 字段
    cJSON* components_json = cJSON_GetObjectItem(json, "components");
    if (components_json && cJSON_IsNumber(components_json)) {
        data->components = components_json->valueint;
    }

    // 处理 points 字段
    cJSON* points_json = cJSON_GetObjectItem(json, "points");
    if (points_json && cJSON_IsNumber(points_json)) {
        data->points = points_json->valueint;
    }

    // 处理 count 字段
    cJSON* count_json = cJSON_GetObjectItem(json, "count");
    if (count_json && cJSON_IsNumber(count_json)) {
        data->count = count_json->valueint;
    }

    return CONVERT_SUCCESS;
}

// 打印函数
void print_vector(const struct Vector* data) {
    if (!data) {
        printf("NULL\n");
        return;
    }

    printf("struct Vector {\n");
    printf("    components: ");
    printf(%.6f, data->components);
    printf("\n");
    printf("    points: ");
    printf("\n");
    print_point(&data->points);
    printf("    count: ");
    printf(%u, data->count);
    printf("\n");
    printf("}\n");
}

#endif  // ENABLE_VECTOR_CONVERTER
#if ENABLE_NESTEDSTRUCT_CONVERTER

DEFINE_ARRAY_CONVERTERS(struct NestedStruct)

cJSON* nestedstruct_to_json(const struct NestedStruct* data, const struct NestedStruct* default_data) {
    if (!data) return NULL;
    cJSON* root = cJSON_CreateObject();
    if (!root) return NULL;

    // 处理Point类型字段 origin
    if (!default_data || data->origin != default_data->origin) {
        cJSON_AddNumberToObject(root, "origin", data->origin);
    }

    // 处理Vector类型字段 vectors
    if (!default_data || data->vectors != default_data->vectors) {
        cJSON_AddNumberToObject(root, "vectors", data->vectors);
    }

    // 处理DataValue类型字段 values
    if (!default_data || data->values != default_data->values) {
        cJSON_AddNumberToObject(root, "values", data->values);
    }

    // 处理BitFields类型字段 flags
    if (!default_data || data->flags != default_data->flags) {
        cJSON_AddNumberToObject(root, "flags", data->flags);
    }

    // 处理struct类型字段 date
    if (!default_data || data->date != default_data->date) {
        cJSON_AddNumberToObject(root, "date", data->date);
    }

    return root;
}

convert_status_t json_to_nestedstruct(const cJSON* json, const struct NestedStruct* default_data, struct NestedStruct* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 origin 字段
    cJSON* origin_json = cJSON_GetObjectItem(json, "origin");
    if (origin_json && cJSON_IsNumber(origin_json)) {
        data->origin = origin_json->valueint;
    }

    // 处理 vectors 字段
    cJSON* vectors_json = cJSON_GetObjectItem(json, "vectors");
    if (vectors_json && cJSON_IsNumber(vectors_json)) {
        data->vectors = vectors_json->valueint;
    }

    // 处理 values 字段
    cJSON* values_json = cJSON_GetObjectItem(json, "values");
    if (values_json && cJSON_IsNumber(values_json)) {
        data->values = values_json->valueint;
    }

    // 处理 flags 字段
    cJSON* flags_json = cJSON_GetObjectItem(json, "flags");
    if (flags_json && cJSON_IsNumber(flags_json)) {
        data->flags = flags_json->valueint;
    }

    // 处理 date 字段
    cJSON* date_json = cJSON_GetObjectItem(json, "date");
    if (date_json && cJSON_IsNumber(date_json)) {
        data->date = date_json->valueint;
    }

    return CONVERT_SUCCESS;
}

// 打印函数
void print_nestedstruct(const struct NestedStruct* data) {
    if (!data) {
        printf("NULL\n");
        return;
    }

    printf("struct NestedStruct {\n");
    printf("    origin: ");
    printf("\n");
    print_point(&data->origin);
    printf("    vectors: ");
    printf("\n");
    print_vector(&data->vectors);
    printf("    values: ");
    printf("0x%x", data->values);
    printf("\n");
    printf("    flags: ");
    printf("\n");
    print_bitfields(&data->flags);
    printf("    date: ");
    printf("0x%x", data->date);
    printf("\n");
    printf("}\n");
}

#endif  // ENABLE_NESTEDSTRUCT_CONVERTER
#if ENABLE_STRINGVIEW_CONVERTER

DEFINE_ARRAY_CONVERTERS(struct StringView)

cJSON* stringview_to_json(const struct StringView* data, const struct StringView* default_data) {
    if (!data) return NULL;
    cJSON* root = cJSON_CreateObject();
    if (!root) return NULL;

    // 处理char*类型字段 data
    if (!default_data || data->data != default_data->data) {
        cJSON_AddNumberToObject(root, "data", data->data);
    }

    // 处理size_t类型字段 length
    if (!default_data || data->length != default_data->length) {
        cJSON_AddNumberToObject(root, "length", data->length);
    }

    return root;
}

convert_status_t json_to_stringview(const cJSON* json, const struct StringView* default_data, struct StringView* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 data 字段
    cJSON* data_json = cJSON_GetObjectItem(json, "data");
    if (data_json && cJSON_IsNumber(data_json)) {
        data->data = data_json->valueint;
    }

    // 处理 length 字段
    cJSON* length_json = cJSON_GetObjectItem(json, "length");
    if (length_json && cJSON_IsNumber(length_json)) {
        data->length = length_json->valueint;
    }

    return CONVERT_SUCCESS;
}

// 打印函数
void print_stringview(const struct StringView* data) {
    if (!data) {
        printf("NULL\n");
        return;
    }

    printf("struct StringView {\n");
    printf("    data: ");
    printf("%c", data->data);
    printf("\n");
    printf("    length: ");
    printf(%zu, data->length);
    printf("\n");
    printf("}\n");
}

#endif  // ENABLE_STRINGVIEW_CONVERTER
#if ENABLE_CONFIG_CONVERTER

DEFINE_ARRAY_CONVERTERS(struct Config)

cJSON* config_to_json(const struct Config* data, const struct Config* default_data) {
    if (!data) return NULL;
    cJSON* root = cJSON_CreateObject();
    if (!root) return NULL;

    // 处理struct类型字段 limits
    if (!default_data || data->limits != default_data->limits) {
        cJSON_AddNumberToObject(root, "limits", data->limits);
    }

    // 处理struct类型字段 network
    if (!default_data || data->network != default_data->network) {
        cJSON_AddNumberToObject(root, "network", data->network);
    }

    // 处理struct类型字段 logging
    if (!default_data || data->logging != default_data->logging) {
        cJSON_AddNumberToObject(root, "logging", data->logging);
    }

    // 处理void*类型字段 user_context
    if (!default_data || data->user_context != default_data->user_context) {
        cJSON_AddNumberToObject(root, "user_context", data->user_context);
    }

    return root;
}

convert_status_t json_to_config(const cJSON* json, const struct Config* default_data, struct Config* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 limits 字段
    cJSON* limits_json = cJSON_GetObjectItem(json, "limits");
    if (limits_json && cJSON_IsNumber(limits_json)) {
        data->limits = limits_json->valueint;
    }

    // 处理 network 字段
    cJSON* network_json = cJSON_GetObjectItem(json, "network");
    if (network_json && cJSON_IsNumber(network_json)) {
        data->network = network_json->valueint;
    }

    // 处理 logging 字段
    cJSON* logging_json = cJSON_GetObjectItem(json, "logging");
    if (logging_json && cJSON_IsNumber(logging_json)) {
        data->logging = logging_json->valueint;
    }

    // 处理 user_context 字段
    cJSON* user_context_json = cJSON_GetObjectItem(json, "user_context");
    if (user_context_json && cJSON_IsNumber(user_context_json)) {
        data->user_context = user_context_json->valueint;
    }

    return CONVERT_SUCCESS;
}

// 打印函数
void print_config(const struct Config* data) {
    if (!data) {
        printf("NULL\n");
        return;
    }

    printf("struct Config {\n");
    printf("    limits: ");
    printf("0x%x", data->limits);
    printf("\n");
    printf("    network: ");
    printf("0x%x", data->network);
    printf("\n");
    printf("    logging: ");
    printf("0x%x", data->logging);
    printf("\n");
    printf("    user_context: ");
    printf("0x%x", data->user_context);
    printf("\n");
    printf("}\n");
}

#endif  // ENABLE_CONFIG_CONVERTER
#if ENABLE_NODE_CONVERTER

DEFINE_ARRAY_CONVERTERS(struct Node)

cJSON* node_to_json(const struct Node* data, const struct Node* default_data) {
    if (!data) return NULL;
    cJSON* root = cJSON_CreateObject();
    if (!root) return NULL;

    // 处理i32类型字段 value
    if (!default_data || data->value != default_data->value) {
        cJSON_AddNumberToObject(root, "value", data->value);
    }

    // 处理struct Node*类型字段 next
    if (!default_data || data->next != default_data->next) {
        cJSON_AddNumberToObject(root, "next", data->next);
    }

    // 处理struct Node*类型字段 prev
    if (!default_data || data->prev != default_data->prev) {
        cJSON_AddNumberToObject(root, "prev", data->prev);
    }

    return root;
}

convert_status_t json_to_node(const cJSON* json, const struct Node* default_data, struct Node* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 value 字段
    cJSON* value_json = cJSON_GetObjectItem(json, "value");
    if (value_json && cJSON_IsNumber(value_json)) {
        data->value = value_json->valueint;
    }

    // 处理 next 字段
    cJSON* next_json = cJSON_GetObjectItem(json, "next");
    if (next_json && cJSON_IsNumber(next_json)) {
        data->next = next_json->valueint;
    }

    // 处理 prev 字段
    cJSON* prev_json = cJSON_GetObjectItem(json, "prev");
    if (prev_json && cJSON_IsNumber(prev_json)) {
        data->prev = prev_json->valueint;
    }

    return CONVERT_SUCCESS;
}

// 打印函数
void print_node(const struct Node* data) {
    if (!data) {
        printf("NULL\n");
        return;
    }

    printf("struct Node {\n");
    printf("    value: ");
    printf(%d, data->value);
    printf("\n");
    printf("    next: ");
    printf("\n");
    print_node(&data->next);
    printf("    prev: ");
    printf("\n");
    print_node(&data->prev);
    printf("}\n");
}

#endif  // ENABLE_NODE_CONVERTER
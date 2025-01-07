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

// [START_BITFIELDS_IMPL_INTERFACE]
DEFINE_ARRAY_CONVERTERS(BitFields)

cJSON* bitfields_to_json(const BitFields* data, const BitFields* default_data) {
    if (!data) return NULL;
    cJSON* json = cJSON_CreateObject();
    if (!json) return NULL;

    // 比较 flag1
    if (!default_data || data->flag1 != default_data->flag1) {
        cJSON_AddNumberToObject(json, "flag1", data->flag1);
    }

    // 比较 flag2
    if (!default_data || data->flag2 != default_data->flag2) {
        cJSON_AddNumberToObject(json, "flag2", data->flag2);
    }

    // 比较 value
    if (!default_data || data->value != default_data->value) {
        cJSON_AddNumberToObject(json, "value", data->value);
    }

    // 比较 reserved
    if (!default_data || data->reserved != default_data->reserved) {
        cJSON_AddNumberToObject(json, "reserved", data->reserved);
    }

    return json;
}

convert_status_t json_to_bitfields(const cJSON* json, const BitFields* default_data, BitFields* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 flag1 字段
    cJSON* flag1_json = cJSON_GetObjectItem(json, "flag1");
    if (flag1_json && cJSON_IsNumber(flag1_json)) data->flag1 = flag1_json->valueint;
    // 处理 flag2 字段
    cJSON* flag2_json = cJSON_GetObjectItem(json, "flag2");
    if (flag2_json && cJSON_IsNumber(flag2_json)) data->flag2 = flag2_json->valueint;
    // 处理 value 字段
    cJSON* value_json = cJSON_GetObjectItem(json, "value");
    if (value_json && cJSON_IsNumber(value_json)) data->value = value_json->valueint;
    // 处理 reserved 字段
    cJSON* reserved_json = cJSON_GetObjectItem(json, "reserved");
    if (reserved_json && cJSON_IsNumber(reserved_json)) data->reserved = reserved_json->valueint;

    return CONVERT_SUCCESS;
}
// [END_BITFIELDS_IMPL_INTERFACE]

// [START_COMPLEXDATA_IMPL_INTERFACE]
DEFINE_ARRAY_CONVERTERS(ComplexData)

cJSON* complexdata_to_json(const ComplexData* data, const ComplexData* default_data) {
    if (!data) return NULL;
    cJSON* json = cJSON_CreateObject();
    if (!json) return NULL;

    // 比较 id
    if (!default_data || data->id != default_data->id) {
        cJSON_AddNumberToObject(json, "id", data->id);
    }

    // 比较 name 数组
    if (!default_data || memcmp(&data->name, &default_data->name, sizeof(data->name)) != 0) {
        cJSON_AddStringToObject(json, "name", data->name);
    // 比较 position
    if (!default_data || data->position != default_data->position) {
        cJSON* position_obj = point_to_json(&data->position,
            default_data ? &default_data->position : NULL);
        if (position_obj) {
            cJSON_AddItemToObject(json, "position", position_obj);
        }
    }

    // 比较 movement
    if (!default_data || data->movement != default_data->movement) {
        if (data->movement) {
            cJSON* movement_obj = vector_to_json(data->movement,
                default_data ? default_data->movement : NULL);
            if (movement_obj) {
                cJSON_AddItemToObject(json, "movement", movement_obj);
            }
        }
    // 比较 targets
    if (!default_data || data->targets != default_data->targets) {
        cJSON* targets_obj = point_to_json(&data->targets,
            default_data ? &default_data->targets : NULL);
        if (targets_obj) {
            cJSON_AddItemToObject(json, "targets", targets_obj);
        }
    }

    // 比较 head
    if (!default_data || data->head != default_data->head) {
        if (data->head) {
            cJSON* head_obj = node_to_json(data->head,
                default_data ? default_data->head : NULL);
            if (head_obj) {
                cJSON_AddItemToObject(json, "head", head_obj);
            }
        }
    // 比较 matrix 数组
    if (!default_data || memcmp(&data->matrix, &default_data->matrix, sizeof(data->matrix)) != 0) {
        cJSON* matrix_array = cJSON_CreateArray();
        if (matrix_array) {
            for (size_t i = 0; i < 4; i++) {
                cJSON* row = cJSON_CreateArray();
                if (row) {
                    for (size_t j = 0; j < 4; j++) {
                        cJSON_AddItemToArray(row, cJSON_CreateNumber(data->matrix[i][j]));
                    }
                    cJSON_AddItemToArray(matrix_array, row);
                }
                cJSON_AddItemToObject(json, "matrix", matrix_array);
            }
    // 比较 extra_data
    if (!default_data || data->extra_data != default_data->extra_data) {
        if (data->extra_data) {
        }
    // 比较 flags
    if (!default_data || data->flags != default_data->flags) {
        cJSON_AddNumberToObject(json, "flags", data->flags);
    }

    return json;
}

convert_status_t json_to_complexdata(const cJSON* json, const ComplexData* default_data, ComplexData* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 id 字段
    cJSON* id_json = cJSON_GetObjectItem(json, "id");
    if (id_json && cJSON_IsNumber(id_json)) data->id = id_json->valueint;
    // 处理 name 字段
    cJSON* name_json = cJSON_GetObjectItem(json, "name");
    if (name_json && cJSON_IsString(name_json)) {
        strncpy(data->name, name_json->valuestring, 32-1);
        data->name[32-1] = '\0';
    }
    // 处理 position 字段
    cJSON* position_json = cJSON_GetObjectItem(json, "position");
    if (position_json && cJSON_IsObject(position_json)) {
        convert_status_t status = json_to_point(position_json,
            default_data ? &default_data->position : NULL,
            &data->position);
        if (status != CONVERT_SUCCESS) return status;
    }
    // 处理 movement 字段
    cJSON* movement_json = cJSON_GetObjectItem(json, "movement");
    if (movement_json && cJSON_IsObject(movement_json)) {
        if (!data->movement) {
            data->movement = malloc(sizeof(Vector));
            if (!data->movement) return CONVERT_MALLOC_ERROR;
        }
        convert_status_t status = json_to_vector(movement_json,
            default_data ? default_data->movement : NULL,
            data->movement);
        if (status != CONVERT_SUCCESS) return status;
    }
    // 处理 targets 字段
    cJSON* targets_json = cJSON_GetObjectItem(json, "targets");
    if (targets_json && cJSON_IsObject(targets_json)) {
        convert_status_t status = json_to_point(targets_json,
            default_data ? &default_data->targets : NULL,
            &data->targets);
        if (status != CONVERT_SUCCESS) return status;
    }
    // 处理 head 字段
    cJSON* head_json = cJSON_GetObjectItem(json, "head");
    if (head_json && cJSON_IsObject(head_json)) {
        if (!data->head) {
            data->head = malloc(sizeof(Node));
            if (!data->head) return CONVERT_MALLOC_ERROR;
        }
        convert_status_t status = json_to_node(head_json,
            default_data ? default_data->head : NULL,
            data->head);
        if (status != CONVERT_SUCCESS) return status;
    }
    // 处理 matrix 字段
    cJSON* matrix_json = cJSON_GetObjectItem(json, "matrix");
    if (matrix_json && cJSON_IsArray(matrix_json)) {
        size_t rows = cJSON_GetArraySize(matrix_json);
        size_t copy_rows = (rows < 4) ? rows : 4;
        for (size_t i = 0; i < copy_rows; i++) {
            cJSON* row = cJSON_GetArrayItem(matrix_json, i);
            if (row && cJSON_IsArray(row)) {
                size_t cols = cJSON_GetArraySize(row);
                size_t copy_cols = (cols < 4) ? cols : 4;
                for (size_t j = 0; j < copy_cols; j++) {
                    cJSON* item = cJSON_GetArrayItem(row, j);
                    if (cJSON_IsNumber(item)) data->matrix[i][j] = item->valuedouble;
                }
            }
        }
    }
    // 处理 extra_data 字段
    cJSON* extra_data_json = cJSON_GetObjectItem(json, "extra_data");
    if (extra_data_json) {
        if (!data->extra_data) {
            data->extra_data = malloc(sizeof(void));
            if (!data->extra_data) return CONVERT_MALLOC_ERROR;
        }
    }
    // 处理 flags 字段
    cJSON* flags_json = cJSON_GetObjectItem(json, "flags");
    if (flags_json && cJSON_IsNumber(flags_json)) data->flags = flags_json->valueint;

    return CONVERT_SUCCESS;
}
// [END_COMPLEXDATA_IMPL_INTERFACE]

// [START_CONFIG_IMPL_INTERFACE]
DEFINE_ARRAY_CONVERTERS(Config)

cJSON* config_to_json(const Config* data, const Config* default_data) {
    if (!data) return NULL;
    cJSON* json = cJSON_CreateObject();
    if (!json) return NULL;

    // 比较 limits 结构体
    if (!default_data || memcmp(&data->limits, &default_data->limits, sizeof(data->limits)) != 0) {
        cJSON* limits_obj = cJSON_CreateObject();
        if (limits_obj) {
            cJSON_AddNumberToObject(limits_obj, "max_items", data->limits.max_items);
            cJSON_AddNumberToObject(limits_obj, "max_depth", data->limits.max_depth);
            cJSON_AddNumberToObject(limits_obj, "threshold", data->limits.threshold);
            cJSON_AddItemToObject(json, "limits", limits_obj);
        }
    // 比较 network 结构体
    if (!default_data || memcmp(&data->network, &default_data->network, sizeof(data->network)) != 0) {
        cJSON* network_obj = cJSON_CreateObject();
        if (network_obj) {
            cJSON_AddStringToObject(network_obj, "host", &data->network.host);
            cJSON_AddNumberToObject(network_obj, "port", data->network.port);
            cJSON_AddNumberToObject(network_obj, "timeout_ms", data->network.timeout_ms);
            cJSON_AddItemToObject(json, "network", network_obj);
        }
    // 比较 logging 结构体
    if (!default_data || memcmp(&data->logging, &default_data->logging, sizeof(data->logging)) != 0) {
        cJSON* logging_obj = cJSON_CreateObject();
        if (logging_obj) {
            cJSON_AddNumberToObject(logging_obj, "level", data->logging.level);
            cJSON_AddBoolToObject(logging_obj, "enabled", data->logging.enabled);
            cJSON_AddStringToObject(logging_obj, "file", &data->logging.file);
            cJSON_AddItemToObject(json, "logging", logging_obj);
        }
    // 比较 user_context
    if (!default_data || data->user_context != default_data->user_context) {
        if (data->user_context) {
        }
    return json;
}

convert_status_t json_to_config(const cJSON* json, const Config* default_data, Config* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 limits 字段
    cJSON* limits_json = cJSON_GetObjectItem(json, "limits");
    // 处理 network 字段
    cJSON* network_json = cJSON_GetObjectItem(json, "network");
    // 处理 logging 字段
    cJSON* logging_json = cJSON_GetObjectItem(json, "logging");
    // 处理 user_context 字段
    cJSON* user_context_json = cJSON_GetObjectItem(json, "user_context");
    if (user_context_json) {
        if (!data->user_context) {
            data->user_context = malloc(sizeof(void));
            if (!data->user_context) return CONVERT_MALLOC_ERROR;
        }
    }

    return CONVERT_SUCCESS;
}
// [END_CONFIG_IMPL_INTERFACE]

// [START_NESTEDSTRUCT_IMPL_INTERFACE]
DEFINE_ARRAY_CONVERTERS(NestedStruct)

cJSON* nestedstruct_to_json(const NestedStruct* data, const NestedStruct* default_data) {
    if (!data) return NULL;
    cJSON* json = cJSON_CreateObject();
    if (!json) return NULL;

    // 比较 origin
    if (!default_data || data->origin != default_data->origin) {
        cJSON* origin_obj = point_to_json(&data->origin,
            default_data ? &default_data->origin : NULL);
        if (origin_obj) {
            cJSON_AddItemToObject(json, "origin", origin_obj);
        }
    }

    // 比较 vectors 数组
    if (!default_data || memcmp(&data->vectors, &default_data->vectors, sizeof(data->vectors)) != 0) {
        cJSON* vectors_array = cJSON_CreateArray();
        if (vectors_array) {
            for (size_t i = 0; i < 2; i++) {
                cJSON* row = cJSON_CreateArray();
                if (row) {
                    for (size_t j = 0; j < 4; j++) {
                        cJSON* item = vector[2][4]_to_json(&data->vectors[i][j], NULL);
                        if (item) {
                            cJSON_AddItemToArray(row, item);
                        }
                    }
                    cJSON_AddItemToArray(vectors_array, row);
                }
                cJSON_AddItemToObject(json, "vectors", vectors_array);
            }
    // 比较 values 数组
    if (!default_data || memcmp(&data->values, &default_data->values, sizeof(data->values)) != 0) {
        cJSON* values_array = cJSON_CreateArray();
        if (values_array) {
            for (size_t i = 0; i < 4; i++) {
                cJSON* item = datavalue[4]_to_json(&data->values[i], NULL);
                if (item) {
                    cJSON_AddItemToArray(values_array, item);
                }
            }
            cJSON_AddItemToObject(json, "values", values_array);
        }
    // 比较 flags
    if (!default_data || data->flags != default_data->flags) {
        cJSON* flags_obj = bitfields_to_json(&data->flags,
            default_data ? &default_data->flags : NULL);
        if (flags_obj) {
            cJSON_AddItemToObject(json, "flags", flags_obj);
        }
    }

    // 比较 date 结构体
    if (!default_data || memcmp(&data->date, &default_data->date, sizeof(data->date)) != 0) {
        cJSON* date_obj = cJSON_CreateObject();
        if (date_obj) {
            cJSON_AddNumberToObject(date_obj, "year", data->date.year);
            cJSON_AddNumberToObject(date_obj, "month", data->date.month);
            cJSON_AddNumberToObject(date_obj, "day", data->date.day);
            cJSON_AddItemToObject(json, "date", date_obj);
        }
    return json;
}

convert_status_t json_to_nestedstruct(const cJSON* json, const NestedStruct* default_data, NestedStruct* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 origin 字段
    cJSON* origin_json = cJSON_GetObjectItem(json, "origin");
    if (origin_json && cJSON_IsObject(origin_json)) {
        convert_status_t status = json_to_point(origin_json,
            default_data ? &default_data->origin : NULL,
            &data->origin);
        if (status != CONVERT_SUCCESS) return status;
    }
    // 处理 vectors 字段
    cJSON* vectors_json = cJSON_GetObjectItem(json, "vectors");
    if (vectors_json && cJSON_IsArray(vectors_json)) {
        size_t rows = cJSON_GetArraySize(vectors_json);
        size_t copy_rows = (rows < 2) ? rows : 2;
        for (size_t i = 0; i < copy_rows; i++) {
            cJSON* row = cJSON_GetArrayItem(vectors_json, i);
            if (row && cJSON_IsArray(row)) {
                size_t cols = cJSON_GetArraySize(row);
                size_t copy_cols = (cols < 4) ? cols : 4;
                for (size_t j = 0; j < copy_cols; j++) {
                    cJSON* item = cJSON_GetArrayItem(row, j);
                    if (item) {
                        convert_status_t status = json_to_vector[2][4](item,
                            default_data ? &default_data->vectors[i][j] : NULL,
                            &data->vectors[i][j]);
                        if (status != CONVERT_SUCCESS) return status;
                    }
    // 处理 values 字段
    cJSON* values_json = cJSON_GetObjectItem(json, "values");
    if (values_json && cJSON_IsArray(values_json)) {
        size_t array_size = cJSON_GetArraySize(values_json);
        size_t copy_size = (array_size < 4) ? array_size : 4;
        for (size_t i = 0; i < copy_size; i++) {
            cJSON* item = cJSON_GetArrayItem(values_json, i);
            if (item) {
                convert_status_t status = json_to_datavalue[4](item,
                    default_data ? &default_data->values[i] : NULL,
                    &data->values[i]);
                if (status != CONVERT_SUCCESS) return status;
            }
        }
    }
    // 处理 flags 字段
    cJSON* flags_json = cJSON_GetObjectItem(json, "flags");
    if (flags_json && cJSON_IsObject(flags_json)) {
        convert_status_t status = json_to_bitfields(flags_json,
            default_data ? &default_data->flags : NULL,
            &data->flags);
        if (status != CONVERT_SUCCESS) return status;
    }
    // 处理 date 字段
    cJSON* date_json = cJSON_GetObjectItem(json, "date");

    return CONVERT_SUCCESS;
}
// [END_NESTEDSTRUCT_IMPL_INTERFACE]

// [START_NODE_IMPL_INTERFACE]
DEFINE_ARRAY_CONVERTERS(Node)

cJSON* node_to_json(const Node* data, const Node* default_data) {
    if (!data) return NULL;
    cJSON* json = cJSON_CreateObject();
    if (!json) return NULL;

    // 比较 value
    if (!default_data || data->value != default_data->value) {
        cJSON_AddNumberToObject(json, "value", data->value);
    }

    // 比较 next
    if (!default_data || data->next != default_data->next) {
        if (data->next) {
        }
    // 比较 prev
    if (!default_data || data->prev != default_data->prev) {
        if (data->prev) {
        }
    return json;
}

convert_status_t json_to_node(const cJSON* json, const Node* default_data, Node* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 value 字段
    cJSON* value_json = cJSON_GetObjectItem(json, "value");
    if (value_json && cJSON_IsNumber(value_json)) data->value = value_json->valueint;
    // 处理 next 字段
    cJSON* next_json = cJSON_GetObjectItem(json, "next");
    if (next_json) {
        if (!data->next) {
            data->next = malloc(sizeof(struct));
            if (!data->next) return CONVERT_MALLOC_ERROR;
        }
    }
    // 处理 prev 字段
    cJSON* prev_json = cJSON_GetObjectItem(json, "prev");
    if (prev_json) {
        if (!data->prev) {
            data->prev = malloc(sizeof(struct));
            if (!data->prev) return CONVERT_MALLOC_ERROR;
        }
    }

    return CONVERT_SUCCESS;
}
// [END_NODE_IMPL_INTERFACE]

// [START_POINT_IMPL_INTERFACE]
DEFINE_ARRAY_CONVERTERS(Point)

cJSON* point_to_json(const Point* data, const Point* default_data) {
    if (!data) return NULL;
    cJSON* json = cJSON_CreateObject();
    if (!json) return NULL;

    // 比较 x
    if (!default_data || data->x != default_data->x) {
        cJSON_AddNumberToObject(json, "x", data->x);
    }

    // 比较 y
    if (!default_data || data->y != default_data->y) {
        cJSON_AddNumberToObject(json, "y", data->y);
    }

    return json;
}

convert_status_t json_to_point(const cJSON* json, const Point* default_data, Point* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 x 字段
    cJSON* x_json = cJSON_GetObjectItem(json, "x");
    if (x_json && cJSON_IsNumber(x_json)) data->x = x_json->valueint;
    // 处理 y 字段
    cJSON* y_json = cJSON_GetObjectItem(json, "y");
    if (y_json && cJSON_IsNumber(y_json)) data->y = y_json->valueint;

    return CONVERT_SUCCESS;
}
// [END_POINT_IMPL_INTERFACE]

// [START_RINGBUFFER_IMPL_INTERFACE]
DEFINE_ARRAY_CONVERTERS(RingBuffer)

cJSON* ringbuffer_to_json(const RingBuffer* data, const RingBuffer* default_data) {
    if (!data) return NULL;
    cJSON* json = cJSON_CreateObject();
    if (!json) return NULL;

    // 比较 buffer
    if (!default_data || data->buffer != default_data->buffer) {
        if (data->buffer) {
            cJSON_AddNumberToObject(json, "buffer", *data->buffer);
        }
    // 比较 size
    if (!default_data || data->size != default_data->size) {
        cJSON_AddNumberToObject(json, "size", data->size);
    }

    // 比较 read_pos
    if (!default_data || data->read_pos != default_data->read_pos) {
        cJSON_AddNumberToObject(json, "read_pos", data->read_pos);
    }

    // 比较 write_pos
    if (!default_data || data->write_pos != default_data->write_pos) {
        cJSON_AddNumberToObject(json, "write_pos", data->write_pos);
    }

    // 比较 status 结构体
    if (!default_data || memcmp(&data->status, &default_data->status, sizeof(data->status)) != 0) {
        cJSON* status_obj = cJSON_CreateObject();
        if (status_obj) {
            cJSON_AddNumberToObject(status_obj, "is_full", data->status.is_full);
            cJSON_AddNumberToObject(status_obj, "is_empty", data->status.is_empty);
            cJSON_AddNumberToObject(status_obj, "reserved", data->status.reserved);
            cJSON_AddItemToObject(json, "status", status_obj);
        }
    return json;
}

convert_status_t json_to_ringbuffer(const cJSON* json, const RingBuffer* default_data, RingBuffer* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 buffer 字段
    cJSON* buffer_json = cJSON_GetObjectItem(json, "buffer");
    if (buffer_json) {
        if (!data->buffer) {
            data->buffer = malloc(sizeof(uint8_t));
            if (!data->buffer) return CONVERT_MALLOC_ERROR;
        }
        if (cJSON_IsNumber(buffer_json)) *data->buffer = buffer_json->valueint;
    }
    // 处理 size 字段
    cJSON* size_json = cJSON_GetObjectItem(json, "size");
    if (size_json && cJSON_IsNumber(size_json)) data->size = size_json->valueint;
    // 处理 read_pos 字段
    cJSON* read_pos_json = cJSON_GetObjectItem(json, "read_pos");
    if (read_pos_json && cJSON_IsNumber(read_pos_json)) data->read_pos = read_pos_json->valueint;
    // 处理 write_pos 字段
    cJSON* write_pos_json = cJSON_GetObjectItem(json, "write_pos");
    if (write_pos_json && cJSON_IsNumber(write_pos_json)) data->write_pos = write_pos_json->valueint;
    // 处理 status 字段
    cJSON* status_json = cJSON_GetObjectItem(json, "status");

    return CONVERT_SUCCESS;
}
// [END_RINGBUFFER_IMPL_INTERFACE]

// [START_STRINGBUILDER_IMPL_INTERFACE]
DEFINE_ARRAY_CONVERTERS(StringBuilder)

cJSON* stringbuilder_to_json(const StringBuilder* data, const StringBuilder* default_data) {
    if (!data) return NULL;
    cJSON* json = cJSON_CreateObject();
    if (!json) return NULL;

    // 比较 buffer
    if (!default_data || data->buffer != default_data->buffer) {
        if (data->buffer) {
            cJSON_AddStringToObject(json, "buffer", data->buffer);
        }
    // 比较 capacity
    if (!default_data || data->capacity != default_data->capacity) {
    }

    // 比较 length
    if (!default_data || data->length != default_data->length) {
    }

    return json;
}

convert_status_t json_to_stringbuilder(const cJSON* json, const StringBuilder* default_data, StringBuilder* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 buffer 字段
    cJSON* buffer_json = cJSON_GetObjectItem(json, "buffer");
    if (buffer_json) {
        if (!data->buffer) {
            data->buffer = malloc(sizeof(char));
            if (!data->buffer) return CONVERT_MALLOC_ERROR;
        }
        if (cJSON_IsString(buffer_json)) strcpy(data->buffer, buffer_json->valuestring);
    }
    // 处理 capacity 字段
    cJSON* capacity_json = cJSON_GetObjectItem(json, "capacity");
    // 处理 length 字段
    cJSON* length_json = cJSON_GetObjectItem(json, "length");

    return CONVERT_SUCCESS;
}
// [END_STRINGBUILDER_IMPL_INTERFACE]

// [START_STRINGVIEW_IMPL_INTERFACE]
DEFINE_ARRAY_CONVERTERS(StringView)

cJSON* stringview_to_json(const StringView* data, const StringView* default_data) {
    if (!data) return NULL;
    cJSON* json = cJSON_CreateObject();
    if (!json) return NULL;

    // 比较 data
    if (!default_data || data->data != default_data->data) {
        if (data->data) {
            cJSON_AddStringToObject(json, "data", data->data);
        }
    // 比较 length
    if (!default_data || data->length != default_data->length) {
    }

    return json;
}

convert_status_t json_to_stringview(const cJSON* json, const StringView* default_data, StringView* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 data 字段
    cJSON* data_json = cJSON_GetObjectItem(json, "data");
    if (data_json) {
        if (!data->data) {
            data->data = malloc(sizeof(char));
            if (!data->data) return CONVERT_MALLOC_ERROR;
        }
        if (cJSON_IsString(data_json)) strcpy(data->data, data_json->valuestring);
    }
    // 处理 length 字段
    cJSON* length_json = cJSON_GetObjectItem(json, "length");

    return CONVERT_SUCCESS;
}
// [END_STRINGVIEW_IMPL_INTERFACE]

// [START_VECTOR_IMPL_INTERFACE]
DEFINE_ARRAY_CONVERTERS(Vector)

cJSON* vector_to_json(const Vector* data, const Vector* default_data) {
    if (!data) return NULL;
    cJSON* json = cJSON_CreateObject();
    if (!json) return NULL;

    // 比较 components 数组
    if (!default_data || memcmp(&data->components, &default_data->components, sizeof(data->components)) != 0) {
        cJSON* components_array = cJSON_CreateArray();
        if (components_array) {
            for (size_t i = 0; i < 3; i++) {
                cJSON_AddItemToArray(components_array, cJSON_CreateNumber(data->components[i]));
            }
            cJSON_AddItemToObject(json, "components", components_array);
        }
    // 比较 points 数组
    if (!default_data || memcmp(&data->points, &default_data->points, sizeof(data->points)) != 0) {
        cJSON* points_array = cJSON_CreateArray();
        if (points_array) {
            for (size_t i = 0; i < 4; i++) {
                cJSON* item = point[4]_to_json(&data->points[i], NULL);
                if (item) {
                    cJSON_AddItemToArray(points_array, item);
                }
            }
            cJSON_AddItemToObject(json, "points", points_array);
        }
    // 比较 count
    if (!default_data || data->count != default_data->count) {
        cJSON_AddNumberToObject(json, "count", data->count);
    }

    return json;
}

convert_status_t json_to_vector(const cJSON* json, const Vector* default_data, Vector* data) {
    if (!json || !data) return CONVERT_INVALID_PARAM;
    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;

    // 如果有默认值，先复制默认值
    if (default_data) {
        *data = *default_data;
    }

    // 处理 components 字段
    cJSON* components_json = cJSON_GetObjectItem(json, "components");
    if (components_json && cJSON_IsArray(components_json)) {
        size_t array_size = cJSON_GetArraySize(components_json);
        size_t copy_size = (array_size < 3) ? array_size : 3;
        for (size_t i = 0; i < copy_size; i++) {
            cJSON* item = cJSON_GetArrayItem(components_json, i);
            if (cJSON_IsNumber(item)) data->components[i] = item->valuedouble;
        }
    }
    // 处理 points 字段
    cJSON* points_json = cJSON_GetObjectItem(json, "points");
    if (points_json && cJSON_IsArray(points_json)) {
        size_t array_size = cJSON_GetArraySize(points_json);
        size_t copy_size = (array_size < 4) ? array_size : 4;
        for (size_t i = 0; i < copy_size; i++) {
            cJSON* item = cJSON_GetArrayItem(points_json, i);
            if (item) {
                convert_status_t status = json_to_point[4](item,
                    default_data ? &default_data->points[i] : NULL,
                    &data->points[i]);
                if (status != CONVERT_SUCCESS) return status;
            }
        }
    }
    // 处理 count 字段
    cJSON* count_json = cJSON_GetObjectItem(json, "count");
    if (count_json && cJSON_IsNumber(count_json)) data->count = count_json->valueint;

    return CONVERT_SUCCESS;
}
// [END_VECTOR_IMPL_INTERFACE]
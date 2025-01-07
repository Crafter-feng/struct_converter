import os
import re
import json
from pathlib import Path
from logger_config import setup_logger

logger = setup_logger('cJsonCodeGenerator')

class cJsonCodeGenerator:
    """C结构体代码生成器，负责生成转换代码"""
    
    def __init__(self, parse_result, cache_dir='.cache'):
        logger.info("Initializing cJsonCodeGenerator")
        
        # 保存解析结果
        self.typedef_types = parse_result['typedef_types']
        self.struct_types = set(parse_result['struct_types'])
        self.pointer_types = parse_result['pointer_types']
        self.struct_info = parse_result['struct_info']
        self.enum_types = parse_result.get('enum_types', {})
        self.macro_definitions = parse_result.get('macro_definitions', {})
        
        # 缓存目录
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug("Generator initialization completed")
    
    def generate_converter_code(self, output_dir, struct_names=None):
        """生成转换器代码
        
        Args:
            output_dir: 输出目录
            struct_names: 指定要生成的结构体名列表，如果为None则生成所有
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        header_path = output_dir / "struct_converter.h"
        impl_path = output_dir / "struct_converter.c"
        
        logger.info(f"开始生成转换代码到目录: {output_dir}")
        logger.info(f"头文件: {header_path}")
        logger.info(f"实现文件: {impl_path}")
        
        if not struct_names:
            # 完全重新生成
            logger.info("重新生成所有转换代码")
            
            # 创建基本框架
            self._create_header_framework(header_path)
            self._create_impl_framework(impl_path)
            
            # 生成所有结构体的声明和实现
            header_content = []
            impl_content = []
            
            # 读取框架内容
            with open(header_path, 'r', encoding='utf-8') as f:
                header_content = f.read().rstrip().split('\n')
            
            with open(impl_path, 'r', encoding='utf-8') as f:
                impl_content = f.read().rstrip().split('\n')
            
            # 添加所有结构体的转换函数
            for struct_name in sorted(self.struct_info.keys()):
                logger.info(f"生成结构体 {struct_name} 的转换函数")
                
                # 添加头文件声明
                start_marker, end_marker, decl = self._generate_header_declarations(struct_name)
                header_content.extend([
                    "",
                    start_marker,
                    decl.rstrip(),
                    end_marker
                ])
                logger.debug(f"生成头文件声明:\n{decl}")
                
                # 添加实现文件代码
                start_marker, end_marker, impl_code = self._generate_implementation_functions(
                    struct_name, 
                    self.struct_info[struct_name]
                )
                impl_content.extend([
                    "",
                    start_marker,
                    impl_code,
                    end_marker
                ])
                logger.debug(f"生成实现代码:\n{impl_code}")
            
            # 添加头文件结尾
            header_content.append("\n#endif // STRUCT_CONVERTER_H")
            
            # 写入文件
            with open(header_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(header_content))
            logger.info(f"头文件生成完成: {header_path}")
            
            with open(impl_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(impl_content))
            logger.info(f"实现文件生成完成: {impl_path}")
        else:
            # 动态更新指定结构体
            logger.info(f"更新指定结构体: {', '.join(struct_names)}")
            # 确保文件存在
            if not header_path.exists():
                self._create_header_framework(header_path)
            if not impl_path.exists():
                self._create_impl_framework(impl_path)
            
            # 检查无效的结构体名
            invalid_structs = set(struct_names) - set(self.struct_info.keys())
            if invalid_structs:
                logger.warning(f"找不到以下结构体: {', '.join(invalid_structs)}")
                return
            
            # 读取现有文件内容
            with open(header_path, 'r', encoding='utf-8') as f:
                header_content = f.read()
            
            with open(impl_path, 'r', encoding='utf-8') as f:
                impl_content = f.read()
            
            # 更新每个指定的结构体
            for struct_name in struct_names:
                if struct_name not in self.struct_info:
                    continue
                
                # 更新头文件
                start_marker, end_marker, header_decl = self._generate_header_declarations(struct_name)
                pattern = f"{start_marker}.*?{end_marker}"
                if re.search(pattern, header_content, re.DOTALL):
                    header_content = re.sub(
                        pattern,
                        f"{start_marker}\n{header_decl}{end_marker}",
                        header_content,
                        flags=re.DOTALL
                    )
                else:
                    # 在 #endif 之前插入新的声明
                    endif_pos = header_content.rfind('#endif')
                    if endif_pos != -1:
                        header_content = (
                            header_content[:endif_pos] +
                            f"\n{start_marker}\n{header_decl}{end_marker}\n\n" +
                            header_content[endif_pos:]
                        )
                
                # 更新实现文件
                start_marker, end_marker, impl_code = self._generate_implementation_functions(
                    struct_name, 
                    self.struct_info[struct_name]
                )
                pattern = f"{start_marker}.*?{end_marker}"
                if re.search(pattern, impl_content, re.DOTALL):
                    impl_content = re.sub(
                        pattern,
                        f"{start_marker}\n{impl_code}\n{end_marker}",
                        impl_content,
                        flags=re.DOTALL
                    )
                else:
                    impl_content += f"\n\n{start_marker}\n{impl_code}\n{end_marker}\n"
            
            # 写入文件
            with open(header_path, 'w', encoding='utf-8') as f:
                f.write(header_content)
            
            with open(impl_path, 'w', encoding='utf-8') as f:
                f.write(impl_content)
        
        logger.info(f"转换代码已生成到目录: {output_dir}")

    def _generate_interface_markers(self, struct_name, interface_type):
        """生成接口标识标记"""
        start_marker = f"// [START_{struct_name.upper()}_{interface_type}_INTERFACE]"
        end_marker = f"// [END_{struct_name.upper()}_{interface_type}_INTERFACE]"
        return start_marker, end_marker

    def _update_file_content(self, file_path, new_content, start_marker, end_marker):
        """更新文件中的特定部分"""
        if not os.path.exists(file_path):
            return new_content
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找标记之间的内容
        pattern = f"{start_marker}.*?{end_marker}"
        if re.search(pattern, content, re.DOTALL):
            # 替换已存在的内容
            updated_content = re.sub(
                pattern,
                f"{start_marker}\n{new_content}\n{end_marker}",
                content,
                flags=re.DOTALL
            )
        else:
            # 添加新内容到文件末尾
            updated_content = f"{content}\n\n{start_marker}\n{new_content}\n{end_marker}"
        
        return updated_content

    def _generate_header_declarations(self, struct_name):
        """生成头文件声明"""
        start_marker = f"// [START_{struct_name.upper()}_HEADER_INTERFACE]"
        end_marker = f"// [END_{struct_name.upper()}_HEADER_INTERFACE]"
        
        declarations = [
            "",
            f"// {struct_name} 转换函数",
            f"cJSON* {struct_name.lower()}_to_json(const {struct_name}* data, const {struct_name}* default_data);",
            f"convert_status_t json_to_{struct_name.lower()}(const cJSON* json, const {struct_name}* default_data, {struct_name}* data);",
            "",
            f"// {struct_name} 数组转换函数",
            f"DECLARE_ARRAY_CONVERTERS({struct_name})",
            ""
        ]
        
        return start_marker, end_marker, '\n'.join(declarations)

    def _generate_implementation_functions(self, struct_name, fields):
        """生成实现文件函数"""
        start_marker, end_marker = self._generate_interface_markers(struct_name, "IMPL")
        
        # 生成基本转换函数
        to_json_func = self._generate_to_json_function(struct_name, fields)
        to_struct_func = self._generate_to_struct_function(struct_name, fields)
        
        # 生成数组转换函数
        array_converters = f"DEFINE_ARRAY_CONVERTERS({struct_name})"
        
        implementations = [
            array_converters,
            "",
            to_json_func,
            "",
            to_struct_func
        ]
        
        impl_code = '\n'.join(implementations)
        logger.debug(f"Generated implementation for {struct_name}:")
        logger.debug(f"{start_marker}")
        logger.debug(f"{impl_code}")
        logger.debug(f"{end_marker}")
        
        return start_marker, end_marker, impl_code

    def _create_header_framework(self, header_path):
        """创建头文件基本框架"""
        content = [
            "#ifndef STRUCT_CONVERTER_H",
            "#define STRUCT_CONVERTER_H",
            "",
            "#include <cjson/cJSON.h>",
            "#include <stddef.h>",
            "#include <stdbool.h>",
            "",
            "// 转换状态码",
            "typedef enum {",
            "    CONVERT_SUCCESS = 0,",
            "    CONVERT_MALLOC_ERROR,",
            "    CONVERT_PARSE_ERROR,",
            "    CONVERT_INVALID_PARAM",
            "} convert_status_t;",
            "",
            "// 数组转换辅助函数宏定义",
            "#define DECLARE_ARRAY_CONVERTERS(type) \\",
            "    cJSON* type##_array_to_json(const type* data, const type* default_data, size_t size); \\",
            "    convert_status_t json_to_##type##_array(const cJSON* json, const type* default_data, type* data, size_t size);",
            "",
            "// 转换函数声明"
        ]
        
        with open(header_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content) + '\n')

    def _create_impl_framework(self, impl_path):
        """创建实现文件基本框架"""
        content = """#include "struct_converter.h"
#include <string.h>
#include <stdlib.h>

// 数组转换辅助宏
#define DEFINE_ARRAY_CONVERTERS(type) \\
cJSON* type##_array_to_json(const type* data, const type* default_data, size_t size) { \\
    if (!data) return NULL; \\
    cJSON* array = cJSON_CreateArray(); \\
    if (!array) return NULL; \\
    for (size_t i = 0; i < size; i++) { \\
        cJSON* item = type##_to_json(&data[i], default_data ? &default_data[i] : NULL); \\
        if (item) { \\
            cJSON_AddItemToArray(array, item); \\
        } \\
    } \\
    return array; \\
} \\
\\
convert_status_t json_to_##type##_array(const cJSON* json, const type* default_data, type* data, size_t size) { \\
    if (!json || !data) return CONVERT_INVALID_PARAM; \\
    if (!cJSON_IsArray(json)) return CONVERT_PARSE_ERROR; \\
    size_t json_size = cJSON_GetArraySize(json); \\
    size_t copy_size = (json_size < size) ? json_size : size; \\
    for (size_t i = 0; i < copy_size; i++) { \\
        cJSON* item = cJSON_GetArrayItem(json, i); \\
        convert_status_t status = json_to_##type(item, default_data ? &default_data[i] : NULL, &data[i]); \\
        if (status != CONVERT_SUCCESS) return status; \\
    } \\
    if (default_data && json_size < size) { \\
        for (size_t i = json_size; i < size; i++) { \\
            data[i] = default_data[i]; \\
        } \\
    } \\
    return CONVERT_SUCCESS; \\
}
"""
        with open(impl_path, 'w', encoding='utf-8') as f:
            f.write(content) 

    def _get_struct_type(self, field_type):
        """从字段类型中提取结构体类型名"""
        # 移除指针标记
        base_type = field_type.rstrip('*')
        
        # 处理 "struct X" 格式
        if base_type.startswith('struct '):
            return base_type.split()[1]
        
        # 处理直接使用类型名的情况
        if base_type in self.struct_types:
            return base_type
        
        # 处理 typedef 的情况
        if base_type in self.typedef_types:
            typedef_type = self.typedef_types[base_type]
            if typedef_type.startswith('struct '):
                return typedef_type.split()[1]
            return typedef_type
        
        return None

    def _generate_to_json_function(self, struct_name, fields):
        """生成结构体转JSON的函数，支持增量保存"""
        lines = [
            f"cJSON* {struct_name.lower()}_to_json(const {struct_name}* data, const {struct_name}* default_data) {{",
            "    if (!data) return NULL;",
            "    cJSON* json = cJSON_CreateObject();",
            "    if (!json) return NULL;",
            ""
        ]

        # 处理每个字段
        for field in fields:
            field_name = field['name']
            field_type = field['type']
            is_pointer = field.get('is_pointer', False)
            is_array = field.get('is_array', False)
            array_size = field.get('array_size', [])
            nested_fields = field.get('nested_fields', [])
            
            # 如果是匿名结构体或数组，添加整块比较
            if nested_fields or is_array:
                lines.extend([
                    f"    // 比较 {field_name} {'数组' if is_array else '结构体'}",
                    f"    if (!default_data || memcmp(&data->{field_name}, &default_data->{field_name}, sizeof(data->{field_name})) != 0) {{"
                ])
            else:
                # 其他字段使用普通比较
                lines.extend([
                    f"    // 比较 {field_name}",
                    f"    if (!default_data || data->{field_name} != default_data->{field_name}) {{"
                ])

            # 生成字段转换代码
            if is_array:
                # 处理数组
                if len(array_size) == 1:
                    # 一维数组
                    if field_type.startswith('char'):
                        # 字符数组特殊处理为字符串
                        lines.append(f"        cJSON_AddStringToObject(json, \"{field_name}\", data->{field_name});")
                    else:
                        # 其他类型数组，整块保存
                        lines.extend([
                            f"        cJSON* {field_name}_array = cJSON_CreateArray();",
                            f"        if ({field_name}_array) {{",
                            f"            for (size_t i = 0; i < {array_size[0]}; i++) {{"
                        ])
                        
                        struct_type = self._get_struct_type(field_type)
                        if struct_type:
                            # 结构体数组
                            lines.extend([
                                f"                cJSON* item = {struct_type.lower()}_to_json(&data->{field_name}[i], NULL);",
                                "                if (item) {",
                                f"                    cJSON_AddItemToArray({field_name}_array, item);",
                                "                }"
                            ])
                        else:
                            # 基本类型数组
                            if field_type.startswith('float') or field_type.startswith('double'):
                                lines.append(f"                cJSON_AddItemToArray({field_name}_array, cJSON_CreateNumber(data->{field_name}[i]));")
                            elif field_type.startswith('int') or field_type.startswith('uint'):
                                lines.append(f"                cJSON_AddItemToArray({field_name}_array, cJSON_CreateNumber(data->{field_name}[i]));")
                            elif field_type.startswith('bool'):
                                lines.append(f"                cJSON_AddItemToArray({field_name}_array, cJSON_CreateBool(data->{field_name}[i]));")
                        
                        lines.extend([
                            "            }",
                            f"            cJSON_AddItemToObject(json, \"{field_name}\", {field_name}_array);",
                            "        }"
                        ])
                
                elif len(array_size) == 2:
                    # 二维数组，整块保存
                    lines.extend([
                        f"        cJSON* {field_name}_array = cJSON_CreateArray();",
                        f"        if ({field_name}_array) {{",
                        f"            for (size_t i = 0; i < {array_size[0]}; i++) {{",
                        "                cJSON* row = cJSON_CreateArray();",
                        "                if (row) {",
                        f"                    for (size_t j = 0; j < {array_size[1]}; j++) {{"
                    ])
                    
                    struct_type = self._get_struct_type(field_type)
                    if struct_type:
                        # 结构体二维数组
                        lines.extend([
                            f"                        cJSON* item = {struct_type.lower()}_to_json(&data->{field_name}[i][j], NULL);",
                            "                        if (item) {",
                            "                            cJSON_AddItemToArray(row, item);",
                            "                        }"
                        ])
                    else:
                        # 基本类型二维数组
                        if field_type.startswith('float') or field_type.startswith('double'):
                            lines.append(f"                        cJSON_AddItemToArray(row, cJSON_CreateNumber(data->{field_name}[i][j]));")
                        elif field_type.startswith('int') or field_type.startswith('uint'):
                            lines.append(f"                        cJSON_AddItemToArray(row, cJSON_CreateNumber(data->{field_name}[i][j]));")
                        elif field_type.startswith('bool'):
                            lines.append(f"                        cJSON_AddItemToArray(row, cJSON_CreateBool(data->{field_name}[i][j]));")
                    
                    lines.extend([
                        "                    }",
                        f"                    cJSON_AddItemToArray({field_name}_array, row);",
                        "                }",
                        f"                cJSON_AddItemToObject(json, \"{field_name}\", {field_name}_array);",
                        "            }"
                    ])
            
            elif nested_fields:
                # 匿名结构体，整块保存
                lines.extend([
                    f"        cJSON* {field_name}_obj = cJSON_CreateObject();",
                    f"        if ({field_name}_obj) {{"
                ])
                
                for nested_field in nested_fields:
                    nested_name = nested_field['name']
                    nested_type = nested_field['type']
                    
                    if nested_type.startswith('float') or nested_type.startswith('double'):
                        lines.append(f"            cJSON_AddNumberToObject({field_name}_obj, \"{nested_name}\", data->{field_name}.{nested_name});")
                    elif nested_type.startswith('int') or nested_type.startswith('uint'):
                        lines.append(f"            cJSON_AddNumberToObject({field_name}_obj, \"{nested_name}\", data->{field_name}.{nested_name});")
                    elif nested_type.startswith('bool'):
                        lines.append(f"            cJSON_AddBoolToObject({field_name}_obj, \"{nested_name}\", data->{field_name}.{nested_name});")
                    elif nested_type.startswith('char'):
                        lines.append(f"            cJSON_AddStringToObject({field_name}_obj, \"{nested_name}\", &data->{field_name}.{nested_name});")
                
                lines.extend([
                    f"            cJSON_AddItemToObject(json, \"{field_name}\", {field_name}_obj);",
                    "        }"
                ])
            
            elif is_pointer:
                # 处理指针类型
                struct_type = self._get_struct_type(field_type)
                if struct_type:
                    # 结构体指针
                    lines.extend([
                        f"        if (data->{field_name}) {{",
                        f"            cJSON* {field_name}_obj = {struct_type.lower()}_to_json(data->{field_name},",
                        f"                default_data ? default_data->{field_name} : NULL);",
                        f"            if ({field_name}_obj) {{",
                        f"                cJSON_AddItemToObject(json, \"{field_name}\", {field_name}_obj);",
                        "            }",
                        "        }"
                    ])
                else:
                    # 基本类型指针
                    lines.extend([
                        f"        if (data->{field_name}) {{"
                    ])
                    
                    if field_type.startswith('char'):
                        lines.append(f"            cJSON_AddStringToObject(json, \"{field_name}\", data->{field_name});")
                    elif field_type.startswith('float') or field_type.startswith('double'):
                        lines.append(f"            cJSON_AddNumberToObject(json, \"{field_name}\", *data->{field_name});")
                    elif field_type.startswith('int') or field_type.startswith('uint'):
                        lines.append(f"            cJSON_AddNumberToObject(json, \"{field_name}\", *data->{field_name});")
                    elif field_type.startswith('bool'):
                        lines.append(f"            cJSON_AddBoolToObject(json, \"{field_name}\", *data->{field_name});")
                    
                    lines.append("        }")
            
            else:
                # 处理普通字段
                struct_type = self._get_struct_type(field_type)
                if struct_type:
                    # 嵌入的结构体
                    lines.extend([
                        f"        cJSON* {field_name}_obj = {struct_type.lower()}_to_json(&data->{field_name},",
                        f"            default_data ? &default_data->{field_name} : NULL);",
                        f"        if ({field_name}_obj) {{",
                        f"            cJSON_AddItemToObject(json, \"{field_name}\", {field_name}_obj);",
                        "        }"
                    ])
                else:
                    # 基本类型
                    if field_type.startswith('char'):
                        lines.append(f"        cJSON_AddStringToObject(json, \"{field_name}\", &data->{field_name});")
                    elif field_type.startswith('float') or field_type.startswith('double'):
                        lines.append(f"        cJSON_AddNumberToObject(json, \"{field_name}\", data->{field_name});")
                    elif field_type.startswith('int') or field_type.startswith('uint'):
                        lines.append(f"        cJSON_AddNumberToObject(json, \"{field_name}\", data->{field_name});")
                    elif field_type.startswith('bool'):
                        lines.append(f"        cJSON_AddBoolToObject(json, \"{field_name}\", data->{field_name});")
                
                # 关闭条件块
                lines.append("    }")
                lines.append("")
            
        # 函数结尾
        lines.extend([
            "    return json;",
            "}"
        ])
        
        return '\n'.join(lines)

    def _generate_to_struct_function(self, struct_name, fields):
        """生成JSON转结构体的函数"""
        lines = [
            f"convert_status_t json_to_{struct_name.lower()}(const cJSON* json, const {struct_name}* default_data, {struct_name}* data) {{",
            "    if (!json || !data) return CONVERT_INVALID_PARAM;",
            "    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;",
            "",
            "    // 如果有默认值，先复制默认值",
            "    if (default_data) {",
            f"        *data = *default_data;",
            "    }",
            ""
        ]

        # 处理每个字段
        for field in fields:
            field_name = field['name']
            field_type = field['type']
            is_pointer = field.get('is_pointer', False)
            is_array = field.get('is_array', False)
            array_size = field.get('array_size', [])
            
            lines.append(f"    // 处理 {field_name} 字段")
            lines.append(f"    cJSON* {field_name}_json = cJSON_GetObjectItem(json, \"{field_name}\");")
            
            if is_array:
                # 处理数组
                if len(array_size) == 1:
                    # 一维数组
                    if field_type.startswith('char'):
                        # 字符数组作为字符串处理
                        lines.extend([
                            f"    if ({field_name}_json && cJSON_IsString({field_name}_json)) {{",
                            f"        strncpy(data->{field_name}, {field_name}_json->valuestring, {array_size[0]}-1);",
                            f"        data->{field_name}[{array_size[0]}-1] = '\\0';",
                            "    }"
                        ])
                    else:
                        # 其他类型数组
                        lines.extend([
                            f"    if ({field_name}_json && cJSON_IsArray({field_name}_json)) {{",
                            f"        size_t array_size = cJSON_GetArraySize({field_name}_json);",
                            f"        size_t copy_size = (array_size < {array_size[0]}) ? array_size : {array_size[0]};",
                            "        for (size_t i = 0; i < copy_size; i++) {",
                            f"            cJSON* item = cJSON_GetArrayItem({field_name}_json, i);"
                        ])
                        
                        if field_type.startswith('struct'):
                            # 结构体数组
                            struct_type = field_type.split()[1].rstrip('*')
                            lines.extend([
                                "            if (item) {",
                                f"                convert_status_t status = json_to_{struct_type.lower()}(item,",
                                f"                    default_data ? &default_data->{field_name}[i] : NULL,",
                                f"                    &data->{field_name}[i]);",
                                "                if (status != CONVERT_SUCCESS) return status;",
                                "            }"
                            ])
                        else:
                            # 基本类型数组
                            if field_type.startswith('float') or field_type.startswith('double'):
                                lines.append(f"            if (cJSON_IsNumber(item)) data->{field_name}[i] = item->valuedouble;")
                            elif field_type.startswith('int') or field_type.startswith('uint'):
                                lines.append(f"            if (cJSON_IsNumber(item)) data->{field_name}[i] = item->valueint;")
                            elif field_type.startswith('bool'):
                                lines.append(f"            if (cJSON_IsBool(item)) data->{field_name}[i] = cJSON_IsTrue(item);")
                            
                        lines.extend([
                            "        }",
                            "    }"
                        ])
                
                elif len(array_size) == 2:
                    # 二维数组
                    lines.extend([
                        f"    if ({field_name}_json && cJSON_IsArray({field_name}_json)) {{",
                        f"        size_t rows = cJSON_GetArraySize({field_name}_json);",
                        f"        size_t copy_rows = (rows < {array_size[0]}) ? rows : {array_size[0]};",
                        "        for (size_t i = 0; i < copy_rows; i++) {",
                        f"            cJSON* row = cJSON_GetArrayItem({field_name}_json, i);",
                        "            if (row && cJSON_IsArray(row)) {",
                        "                size_t cols = cJSON_GetArraySize(row);",
                        f"                size_t copy_cols = (cols < {array_size[1]}) ? cols : {array_size[1]};",
                        "                for (size_t j = 0; j < copy_cols; j++) {",
                        "                    cJSON* item = cJSON_GetArrayItem(row, j);"
                    ])
                    
                    if field_type.startswith('struct'):
                        # 结构体二维数组
                        struct_type = field_type.split()[1].rstrip('*')
                        lines.extend([
                            "                    if (item) {",
                            f"                        convert_status_t status = json_to_{struct_type.lower()}(item,",
                            f"                            default_data ? &default_data->{field_name}[i][j] : NULL,",
                            f"                            &data->{field_name}[i][j]);",
                            "                        if (status != CONVERT_SUCCESS) return status;",
                            "                    }"
                        ])
                    else:
                        # 基本类型二维数组
                        if field_type.startswith('float') or field_type.startswith('double'):
                            lines.append(f"                    if (cJSON_IsNumber(item)) data->{field_name}[i][j] = item->valuedouble;")
                        elif field_type.startswith('int') or field_type.startswith('uint'):
                            lines.append(f"                    if (cJSON_IsNumber(item)) data->{field_name}[i][j] = item->valueint;")
                        elif field_type.startswith('bool'):
                            lines.append(f"                    if (cJSON_IsBool(item)) data->{field_name}[i][j] = cJSON_IsTrue(item);")
                        
                        lines.extend([
                            "                }",
                            "            }",
                            "        }",
                            "    }"
                        ])
            
            elif is_pointer:
                # 处理指针类型
                struct_type = self._get_struct_type(field_type)
                if struct_type:
                    # 结构体指针
                    lines.extend([
                        f"    if ({field_name}_json && cJSON_IsObject({field_name}_json)) {{",
                        f"        if (!data->{field_name}) {{",
                        f"            data->{field_name} = malloc(sizeof({struct_type}));",
                        f"            if (!data->{field_name}) return CONVERT_MALLOC_ERROR;",
                        "        }",
                        f"        convert_status_t status = json_to_{struct_type.lower()}({field_name}_json,",
                        f"            default_data ? default_data->{field_name} : NULL,",
                        f"            data->{field_name});",
                        "        if (status != CONVERT_SUCCESS) return status;",
                        "    }"
                    ])
                else:
                    # 基本类型指针
                    lines.extend([
                        f"    if ({field_name}_json) {{",
                        f"        if (!data->{field_name}) {{",
                        f"            data->{field_name} = malloc(sizeof({field_type.rstrip('*')}));",
                        f"            if (!data->{field_name}) return CONVERT_MALLOC_ERROR;",
                        "        }"
                    ])
                    
                    if field_type.startswith('char'):
                        lines.append(f"        if (cJSON_IsString({field_name}_json)) strcpy(data->{field_name}, {field_name}_json->valuestring);")
                    elif field_type.startswith('float') or field_type.startswith('double'):
                        lines.append(f"        if (cJSON_IsNumber({field_name}_json)) *data->{field_name} = {field_name}_json->valuedouble;")
                    elif field_type.startswith('int') or field_type.startswith('uint'):
                        lines.append(f"        if (cJSON_IsNumber({field_name}_json)) *data->{field_name} = {field_name}_json->valueint;")
                    elif field_type.startswith('bool'):
                        lines.append(f"        if (cJSON_IsBool({field_name}_json)) *data->{field_name} = cJSON_IsTrue({field_name}_json);")
                    
                    lines.append("    }")
            
            else:
                # 处理普通字段
                struct_type = self._get_struct_type(field_type)
                if struct_type:
                    # 嵌入的结构体
                    lines.extend([
                        f"    if ({field_name}_json && cJSON_IsObject({field_name}_json)) {{",
                        f"        convert_status_t status = json_to_{struct_type.lower()}({field_name}_json,",
                        f"            default_data ? &default_data->{field_name} : NULL,",
                        f"            &data->{field_name});",
                        "        if (status != CONVERT_SUCCESS) return status;",
                        "    }"
                    ])
                else:
                    # 基本类型
                    if field_type.startswith('char'):
                        lines.append(f"    if ({field_name}_json && cJSON_IsString({field_name}_json)) data->{field_name} = {field_name}_json->valuestring[0];")
                    elif field_type.startswith('float') or field_type.startswith('double'):
                        lines.append(f"    if ({field_name}_json && cJSON_IsNumber({field_name}_json)) data->{field_name} = {field_name}_json->valuedouble;")
                    elif field_type.startswith('int') or field_type.startswith('uint'):
                        lines.append(f"    if ({field_name}_json && cJSON_IsNumber({field_name}_json)) data->{field_name} = {field_name}_json->valueint;")
                    elif field_type.startswith('bool'):
                        lines.append(f"    if ({field_name}_json && cJSON_IsBool({field_name}_json)) data->{field_name} = cJSON_IsTrue({field_name}_json);")
        
        # 函数结尾
        lines.extend([
            "",
            "    return CONVERT_SUCCESS;",
            "}"
        ])
        
        return '\n'.join(lines) 

    def _collect_variable_definitions(self, node, variable_definitions):
        """收集所有变量定义"""
        if node.type == 'declaration':
            var_data = self._process_declaration(node, variable_definitions)
            if var_data and var_data.get('name'):
                variable_definitions[var_data['name']] = var_data
                logger.debug(f"Collected variable definition: {var_data['name']}")
        
        for child in node.children:
            self._collect_variable_definitions(child, variable_definitions)

    def _resolve_dynamic_size(self, initializer, array_sizes):
        """解析动态数组大小，只处理第一维度的动态大小"""
        if not array_sizes or array_sizes[0] != "dynamic":
            # 如果第一维不是动态的，直接返回原始大小
            return array_sizes
        
        # 只处理第一维的动态大小
        resolved_sizes = list(array_sizes)  # 复制数组大小列表
        
        # 检查初始化器类型
        if initializer.type == 'string_literal':
            # 对于字符串字面量，大小是字符串长度+1（包含null终止符）
            text = initializer.text.decode('utf8').strip('"\'')
            # 处理转义字符
            text = bytes(text, "utf-8").decode("unicode_escape")
            resolved_sizes[0] = len(text) + 1
            logger.debug(f"Resolved string array size to {resolved_sizes[0]} (including null terminator)")
        elif initializer.type == 'initializer_list':
            # 对于初始化列表，计算元素数量
            first_dim_size = len([child for child in initializer.children 
                                if child.type not in ['comment', ',', '{', '}']])
            resolved_sizes[0] = first_dim_size
            logger.debug(f"Resolved array size to {first_dim_size} from initializer list")
        else:
            logger.debug("Could not resolve dynamic size for first dimension")
        
        return resolved_sizes

    def _categorize_variables(self, variable_definitions, var_info):
        """将变量分类到相应的列表中"""
        for var in variable_definitions.values():
            if var['is_pointer']:
                var_info['pointer_vars'].append(var)
            elif var['array_size'] is not None:  # 使用 array_size 判断是否为数组
                var_info['array_vars'].append(var)
            elif var['original_type'].startswith('struct '):
                var_info['struct_vars'].append(var)
            else:
                var_info['variables'].append(var)

    def _process_declaration(self, node, variable_definitions=None):
        """处理声明节点，解析C变量声明"""
        logger.debug(f"处理声明节点: {node.text.decode('utf8')}")
        
        # 跳过 extern 声明
        if self._is_extern_declaration(node):
            logger.debug("跳过 extern 声明")
            return None
        
        # 检查是否是全局变量
        if not self._is_global_declaration(node):
            logger.debug("跳过局部变量声明")
            return None
        
        # 初始化变量数据
        var_data = {
            "name": None,          # 变量名
            "type": None,          # 完整类型字符串（包含所有修饰符）
            "original_type": None, # 原始映射类型（基础类型，不含修饰符）
            "array_size": None,    # 数组大小，不为None表示是数组
            "is_pointer": None,    # 是否是指针
            "pointer_level": None, # 指针级别（用于多级指针）
        }
        
        # 提取声明器（等号前的部分）
        declarator = self._extract_declaration_before_equals(node)
        if not declarator:
            return None
        
        # 解析类型信息
        var_data.update(self._extract_type_info(node))
        
        # 解析声明器信息（变量名、数组、指针等）
        var_data.update(self._extract_declarator_info(declarator, variable_definitions))

        # 提取等号后的初始化器
        initializer = self._extract_declaration_after_equals(node)
        if initializer:
            logger.debug(f"Processing initializer for {var_data['name']}")
            logger.debug(f"Type: {var_data['original_type']}")
            logger.debug(f"Array size: {var_data['array_size']}")
            
            # 特殊处理字符数组的字符串初始化
            if (var_data['original_type'] == 'char' and 
                var_data.get('array_size') and 
                initializer.type == 'string_literal'):
                # 直接获取字符串值
                text = initializer.text.decode('utf8').strip('"\'')
                # 处理转义字符
                text = bytes(text, "utf-8").decode("unicode_escape")
                var_data['value'] = text
                
                # 如果是动态大小数组，设置实际大小（包含null终止符）
                if isinstance(var_data['array_size'], list) and var_data['array_size'][0] == "dynamic":
                    var_data['array_size'] = [len(text) + 1]  # +1 for null terminator
                logger.debug(f"Processed string literal: {text}, array size: {var_data['array_size']}")
            else:
                # 如果数组大小是动态的，则进一步解析
                if isinstance(var_data['array_size'], list) and "dynamic" in var_data['array_size']:
                    var_data['array_size'] = self._resolve_dynamic_size(initializer, var_data['array_size'])
                    logger.debug(f"Resolved array size: {var_data['array_size']}")

                # 解析初始化值
                value = self._parse_initializer(initializer, var_data['original_type'], 
                                              var_data['array_size'], variable_definitions)
                logger.debug(f"Parsed value: {value}")
                var_data['value'] = value

        # 过滤掉 None 值并记录日志
        filtered_data = {k: v for k, v in var_data.items() if v is not None}
        logger.debug(f"处理后的变量声明: {json.dumps(filtered_data, indent=2)}")
        return var_data
    def _is_extern_declaration(self, node):
        """检查是否是 extern 声明"""
        for child in node.children:
            if (child.type == 'storage_class_specifier' and 
                child.text.decode('utf8') == 'extern'):
                return True
        return False

    def _is_global_declaration(self, node):
        """检查是否是全局变量声明
        
        全局变量的特征：
        1. 在函数定义之外
        2. 可能有 static 修饰符
        3. 不在结构体、联合体或枚举定义内部
        
        Args:
            node: 声明节点
            
        Returns:
            bool: 是否是全局变量声明
        """
        # 检查父节点链，确保不在函数定义内
        current = node
        while current:
            if current.type in ['function_definition', 'compound_statement']:
                # 在函数定义或代码块内，说明是局部变量
                logger.debug("Found local variable in function or block")
                return False
            elif current.type in ['struct_specifier', 'union_specifier', 'enum_specifier']:
                # 在结构体、联合体或枚举定义内
                logger.debug("Found declaration in struct/union/enum")
                return False
            current = current.parent
        
        # 检查存储类型说明符
        for child in node.children:
            if child.type == 'storage_class_specifier':
                storage_type = child.text.decode('utf8')
                if storage_type == 'auto' or storage_type == 'register':
                    # auto 和 register 只用于局部变量
                    logger.debug(f"Found {storage_type} storage class specifier")
                    return False
        
        # 检查是否有初始化器
        has_initializer = False
        for child in node.children:
            if child.type == 'init_declarator':
                for init_child in child.children:
                    if init_child.type == 'initializer':
                        has_initializer = True
                        break
        
        if has_initializer:
            logger.debug("Found global variable with initializer")
        else:
            logger.debug("Found global variable declaration without initializer")
        
        return True

    def _extract_type_info(self, node):
        """提取类型信息
        
        Returns:
            dict: 包含类型信息的字典
        """
        type_str, original_type = self._parse_type_info(node)
        return {
            "type": type_str,
            "original_type": original_type
        }

    def _extract_declarator_info(self, declarator, variable_definitions):
        """提取声明器信息（变量名、数组、指针等）
        
        Args:
            declarator: 声明器节点
            variable_definitions: 变量定义字典
            
        Returns:
            dict: 包含声明器信息的字典
        """
        info = {}
        
        if declarator.type == 'array_declarator':
            # 处理数组声明
            array_size, name = self._parse_array_dimensions(declarator)
            info['array_size'] = array_size
            info['name'] = name
        
        elif declarator.type == 'pointer_declarator':
            # 处理指针声明
            info.update(self._extract_pointer_info(declarator))
        
        elif declarator.type == 'identifier':
            # 处理简单变量声明
            info['name'] = declarator.text.decode('utf8')
        
        return info

    def _extract_pointer_info(self, declarator):
        """提取指针相关信息
        
        Returns:
            dict: 包含指针信息的字典
        """
        info = {
            'is_pointer': True,
            'name': None
        }
        
        # 获取指针变量名
        for child in declarator.children:
            if child.type == 'identifier':
                info['name'] = child.text.decode('utf8')
                break
        
        # 计算指针级别（可选）
        pointer_level = 0
        current = declarator
        while current and current.type == 'pointer_declarator':
            pointer_level += 1
            for child in current.children:
                if child.type != 'pointer_declarator':
                    current = None
                    break
                current = child
        
        if pointer_level > 0:
            info['pointer_level'] = pointer_level
        
        return info

    def _parse_type_info(self, node):
        """解析类型信息
        
        Args:
            node: 声明节点
            
        Returns:
            tuple: (type_str, original_type)
                - type_str: 完整类型字符串，包含所有修饰符
                - original_type: 原始映射类型，不含修饰符
        """
        type_parts = []
        original_type = None
        
        for child in node.children:
            if child.type in ['primitive_type', 'sized_type_specifier', 'type_identifier']:
                type_text = child.text.decode('utf8')
                type_parts.append(type_text)
                logger.debug(f"发现类型部分: {type_text}")
                
                # 记录原始类型
                if not original_type:
                    if type_text in self.c_type_mapping:
                        original_type = self.c_type_mapping[type_text]
                    elif type_text in self.typedef_types:
                        original_type = self.typedef_types[type_text]
                    elif type_text in self.struct_types:
                        original_type = f"struct {type_text}"
                    else:
                        original_type = type_text
            
            elif child.type == 'struct_specifier':
                type_parts.append('struct')
                for struct_child in child.children:
                    if struct_child.type == 'type_identifier':
                        struct_type = struct_child.text.decode('utf8')
                        type_parts.append(struct_type)
                        if not original_type:
                            original_type = f"struct {struct_type}"
        
        type_str = ' '.join(type_parts)
        return type_str, original_type

    def _convert_to_struct_dict(self, values, struct_type):
        """将传入的值填充到结构体字典中，完成转换
        
        Args:
            values: 要填充的值（列表或字典）
            struct_type: 结构体类型名
            
        Returns:
            dict: 填充后的结构体字典
        """
        if not struct_type or struct_type not in self.struct_info:
            return values
        
        logger.debug(f"Converting values for struct {struct_type} {values}")
        struct_fields = self.struct_info[struct_type]
        result = {}
        
        # 如果传入的值是列表或元组，按顺序填充
        if isinstance(values, (list, tuple)):
            for i, field in enumerate(struct_fields):
                if i >= len(values):
                    break  # 如果传入的值不够，跳过剩余字段
                
                field_name = field['name']
                field_value = values[i]
                
                # 处理嵌套结构体字段
                if field.get('nested_fields'):
                    if isinstance(field_value, (list, tuple)):
                        nested_dict = {}
                        nested_fields = field['nested_fields']
                        for j, nested_field in enumerate(nested_fields):
                            if j < len(field_value):
                                nested_dict[nested_field['name']] = field_value[j]
                        result[field_name] = nested_dict
                    else:
                        result[field_name] = field_value
                
                # 处理数组字段
                elif field.get('is_array'):
                    if isinstance(field_value, (list, tuple)):
                        if field.get('struct_type'):
                            # 处理结构体数组
                            result[field_name] = [
                                self._convert_to_struct_dict(item, field['struct_type'])
                                if isinstance(item, (list, tuple, dict)) else item
                                for item in field_value
                            ]
                        else:
                            # 普通类型数组
                            result[field_name] = list(field_value)
                    else:
                        result[field_name] = field_value
                
                # 处理嵌套结构体字段
                elif field.get('struct_type'):
                    if isinstance(field_value, (list, tuple, dict)):
                        result[field_name] = self._convert_to_struct_dict(field_value, field['struct_type'])
                    else:
                        result[field_name] = field_value
                
                # 处理基本类型字段
                else:
                    result[field_name] = field_value
        
        # 如果传入的值是字典，按字段名填充
        elif isinstance(values, dict):
            for field in struct_fields:
                field_name = field['name']
                if field_name in values:
                    field_value = values[field_name]
                    
                    # 处理嵌套结构体
                    if field.get('struct_type') and isinstance(field_value, (list, tuple, dict)):
                        result[field_name] = self._convert_to_struct_dict(field_value, field['struct_type'])
                    # 处理匿名结构体
                    elif field.get('nested_fields') and isinstance(field_value, (list, tuple)):
                        nested_dict = {}
                        nested_fields = field['nested_fields']
                        for j, nested_field in enumerate(nested_fields):
                            if j < len(field_value):
                                nested_dict[nested_field['name']] = field_value[j]
                        result[field_name] = nested_dict
                    else:
                        result[field_name] = field_value
                else:
                    # 如果字段名不在传入的字典中，跳过该字段
                    logger.debug(f"Field {field_name} not found in input values")
        
        logger.debug(f"Converted struct dict: {json.dumps(result, indent=2)}")
        return result

    def _parse_initializer(self, initializer, original_type, array_size=None, variable_definitions=None):
        """解析初始化器，根据类型和数组大小提取数据"""
        def parse_basic_value(node):
            """解析基本类型的值"""
            if not node:
                return None
                
            if node.type == 'string_literal':
                # 处理字符串字面量
                text = node.text.decode('utf8')
                # 去除引号
                text = text.strip('"\'')
                # 处理转义字符
                text = bytes(text, "utf-8").decode("unicode_escape")
                return text
            elif node.type == 'number_literal':
                text = node.text.decode('utf8').lower()
                # 处理十六进制数
                if text.startswith('0x'):
                    return int(text, 16)
                # 处理浮点数
                elif '.' in text or 'f' in text:
                    return float(text.rstrip('f'))
                # 处理八进制数
                elif text.startswith('0') and len(text) > 1 and text[1] not in '.e':
                    return int(text, 8)
                # 处理普通十进制数
                return int(text)
            elif node.type == 'true':
                return True
            elif node.type == 'false':
                return False
            elif node.type == 'null':
                return None
            return node.text.decode('utf8')

        def get_initializer_elements(node):
            """获取初始化器中的有效元素"""
            if not node or node.type not in ['initializer_list', 'initializer']:
                return []
            return [child for child in node.children 
                    if child.type not in ['comment', ',', '{', '}', '[', ']']]

        def parse_struct(node, struct_type):
            """解析结构体初始化器
            
            Args:
                node: 初始化器节点
                struct_type: 结构体类型名（不含'struct'前缀）
                
            Returns:
                dict: 解析后的结构体数据
            """
            # 处理指针类型
            if struct_type.endswith('*'):
                base_type = struct_type.rstrip('*')
                if base_type in self.struct_info:
                    # 如果是结构体指针，返回 NULL 或具体的指针值
                    value = parse_basic_value(node)
                    logger.debug(f"Parsed pointer value for {struct_type}: {value}")
                    return value
                else:
                    logger.warning(f"Unknown struct type for pointer: {base_type}")
                    return None

            # 查找结构体信息
            struct_info = None
            if struct_type in self.struct_info:
                struct_info = self.struct_info[struct_type]
            else:
                logger.warning(f"Unknown struct type: {struct_type}")
                return None

            result = {}
            elements = get_initializer_elements(node)
            
            logger.debug(f"Parsing struct {struct_type} with {len(elements)} elements")
            logger.debug(f"Struct fields: {json.dumps(struct_info, indent=2)}")
            
            # 遍历结构体字段
            field_index = 0
            for field in struct_info:
                if field_index >= len(elements):
                    break

                field_name = field['name']
                field_type = field.get('original_type', field.get('type'))
                field_array_size = field.get('array_size')
                element = elements[field_index]
                
                logger.debug(f"Processing field '{field_name}' of type '{field_type}'")
                logger.debug(f"Element type: {element.type}, text: {element.text.decode('utf8')}")
                
                # 处理字符数组字段
                if field_array_size and field_type == 'char':
                    if element.type == 'string_literal':
                        # 直接处理字符串字面量
                        text = parse_basic_value(element)
                        logger.debug(f"Found string literal for char array: '{text}'")
                        result[field_name] = text
                    else:
                        # 处理其他形式的字符数组初始化
                        value = parse_array(element, field_type, field_array_size)
                        logger.debug(f"Parsed char array: {value}")
                        result[field_name] = value
                
                # 处理匿名结构体
                elif field.get('nested_fields'):
                    nested_result = {}
                    nested_elements = get_initializer_elements(element)
                    logger.debug(f"Processing anonymous struct with {len(nested_elements)} elements")
                    
                    for nested_field, nested_element in zip(field['nested_fields'], nested_elements):
                        nested_name = nested_field['name']
                        nested_type = nested_field.get('original_type', nested_field.get('type'))
                        
                        if nested_field.get('array_size'):
                            nested_result[nested_name] = parse_array(
                                nested_element, nested_type, nested_field['array_size'])
                        else:
                            nested_result[nested_name] = parse_basic_value(nested_element)
                    
                    result[field_name] = nested_result
                    logger.debug(f"Parsed anonymous struct: {nested_result}")
                
                # 处理普通数组字段
                elif field_array_size:
                    value = parse_array(element, field_type, field_array_size)
                    logger.debug(f"Parsed array field: {value}")
                    result[field_name] = value
                
                # 处理嵌套结构体字段
                elif field_type.startswith('struct '):
                    inner_struct_type = field_type.split(' ')[1]
                    value = parse_struct(element, inner_struct_type)
                    logger.debug(f"Parsed nested struct: {value}")
                    result[field_name] = value
                
                # 处理基本类型字段
                else:
                    value = parse_basic_value(element)
                    logger.debug(f"Parsed basic value: {value}")
                    result[field_name] = value
                
                field_index += 1

            logger.debug(f"Parsed struct {struct_type}: {json.dumps(result, indent=2)}")
            return result

        def parse_array(node, element_type, dimensions):
            """解析数组初始化器"""
            if not node:
                logger.debug("No node provided for array parsing")
                return []
            
            result = []
            elements = get_initializer_elements(node)
            logger.debug(f"Parsing array of type {element_type} with dimensions {dimensions}")
            logger.debug(f"Found {len(elements)} elements in initializer")
            
            # 特殊处理字符数组的字符串初始化
            if (element_type in ['char', 'int8_t', 'uint8_t', 'u8', 'i8'] and 
                len(elements) == 1):
                element = elements[0]
                logger.debug(f"Processing potential string initialization: {element.type}")
                
                # 处理字符串字面量
                if element.type == 'string_literal':
                    text = parse_basic_value(element)
                    logger.debug(f"Found string literal: '{text}'")
                    if dimensions and dimensions[0] != "dynamic":
                        logger.debug(f"Array size is {dimensions[0]}")
                        # 如果字符串长度超过数组大小，截断
                        if len(text) > dimensions[0] - 1:  # 留一个位置给 null 终止符
                            text = text[:dimensions[0] - 1]
                            logger.debug(f"Truncated string to fit array size: '{text}'")
                    return text
                # 处理单个字符
                elif element.type == 'char_literal':
                    value = parse_basic_value(element)
                    logger.debug(f"Found char literal: '{value}'")
                    return value
            
            # 处理普通数组初始化
            logger.debug("Processing regular array initialization")
            for i, element in enumerate(elements):
                logger.debug(f"Processing element {i}: {element.type}")
                if element.type == 'initializer_list':
                    if len(dimensions) > 1:
                        # 多维数组
                        value = parse_array(element, element_type, dimensions[1:])
                        logger.debug(f"Parsed multidimensional array element: {value}")
                    elif element_type.startswith('struct '):
                        # 结构体数组
                        struct_type = element_type.split(' ')[1]
                        value = parse_struct(element, struct_type)
                        logger.debug(f"Parsed struct array element: {value}")
                    else:
                        # 一维基本类型数组
                        value = [parse_basic_value(e) for e in get_initializer_elements(element)]
                        if len(value) == 1:
                            value = value[0]
                        logger.debug(f"Parsed basic type array element: {value}")
                elif element.type == 'string_literal' and element_type == 'char':
                    # 直接处理字符串字面量
                    value = parse_basic_value(element)
                    logger.debug(f"Parsed string literal in array: '{value}'")
                else:
                    # 单个元素
                    value = parse_basic_value(element)
                    logger.debug(f"Parsed single element: {value}")
                
                result.append(value)
            
            # 如果是字符数组且只有一个元素是字符串，直接返回该字符串
            if (element_type == 'char' and len(result) == 1 and 
                isinstance(result[0], str)):
                logger.debug(f"Returning single string from array: '{result[0]}'")
                return result[0]
            
            # 如果是固定大小数组（非字符数组），确保结果长度正确
            if (dimensions and dimensions[0] != "dynamic" and 
                len(result) < dimensions[0] and 
                element_type not in ['char', 'int8_t', 'uint8_t', 'u8', 'i8']):
                # 根据类型填充默认值
                result.extend([0] * (dimensions[0] - len(result)))
                logger.debug(f"Extended array to match dimension size: {len(result)}")
            
            logger.debug(f"Final array result: {result}")
            return result

        # 主处理逻辑
        try:
            if array_size:
                # 特殊处理字符数组的字符串初始化
                if (original_type == 'char' and 
                    initializer.type == 'string_literal'):
                    text = parse_basic_value(initializer)
                    # 如果是动态大小数组，直接返回字符串
                    if array_size[0] == "dynamic":
                        return text
                    # 如果是固定大小数组，确保不超过数组大小
                    if len(text) >= array_size[0]:
                        text = text[:array_size[0] - 1]  # 留出空间给 null 终止符
                    return text
                # 其他数组类型
                return parse_array(initializer, original_type, array_size)
            elif original_type.startswith('struct '):
                # 结构体类型
                struct_type = original_type.split(' ')[1]
                return parse_struct(initializer, struct_type)
            else:
                # 基本类型
                return parse_basic_value(initializer)
        except Exception as e:
            logger.error(f"Error parsing initializer: {str(e)}")
            logger.error(f"Initializer text: {initializer.text.decode('utf8')}")
            return None

    def _extract_declaration_before_equals(self, node):
        """提取等号之前的声明部分"""
        for child in node.children:
            if child.type == 'init_declarator':
                # 只获取声明器部分，不处理初始化器
                declarator = child.child_by_field_name('declarator')
                if declarator:
                    return declarator   
                
            elif child.type == 'identifier':
                # 简单声明
                return child
        return None
    
    def _extract_declaration_after_equals(self, node):
        """提取等号之后的初始化器部分
        
        Args:
            node: 声明节点
            
        Returns:
            node: 初始化器节点，或者 None
        """
        logger.debug(f"Extracting initializer from: {node.text.decode('utf8')}")
        
        for child in node.children:
            if child.type == 'init_declarator':
                # 遍历 init_declarator 的子节点
                for init_child in child.children:
                    if init_child.type == 'string_literal':
                        # 直接处理字符串字面量
                        logger.debug(f"Found string literal initializer: {init_child.text.decode('utf8')}")
                        return init_child
                    elif init_child.type == 'initializer':
                        logger.debug(f"Found initializer: {init_child.text.decode('utf8')}")
                        return init_child
                    elif init_child.type == 'initializer_list':
                        logger.debug(f"Found initializer_list: {init_child.text.decode('utf8')}")
                        return init_child
                    elif init_child.type == 'array_initializer':
                        logger.debug(f"Found array_initializer: {init_child.text.decode('utf8')}")
                        return init_child
                    elif init_child.type == 'compound_statement':
                        # 处理复合语句形式的初始化
                        for stmt_child in init_child.children:
                            if stmt_child.type in ['initializer_list', 'array_initializer']:
                                logger.debug(f"Found initializer in compound statement: {stmt_child.text.decode('utf8')}")
                                return stmt_child
        
        logger.debug("No initializer found")
        return None

    def _parse_array_dimensions(self, declarator):
        """解析数组维度
        
        Args:
            declarator: 数组声明器节点
            
        Returns:
            tuple: (array_sizes, name)
                - array_sizes: 数组各维度的大小列表
                - name: 变量名
        """
        array_sizes = []
        name = None
        current = declarator
        
        # 首先尝试获取最内层的标识符（变量名）
        def find_identifier(node):
            if node.type == 'identifier':
                return node.text.decode('utf8')
            for child in node.children:
                if child.type == 'identifier':
                    return child.text.decode('utf8')
                elif child.type == 'array_declarator':
                    result = find_identifier(child)
                    if result:
                        return result
            return None
        
        # 先尝试获取变量名
        name = find_identifier(declarator)
        
        while current and current.type == 'array_declarator':
            size_found = False
            next_declarator = None
            
            for child in current.children:
                if child.type == '[':
                    continue
                elif child.type == ']':
                    continue
                elif child.type == 'array_declarator':
                    next_declarator = child
                    continue
                elif child.type == 'identifier':
                    continue  # 已经在前面处理过变量名
                
                if child.type == 'number_literal':
                    # 固定大小
                    size = int(child.text.decode('utf8'))
                    array_sizes.append(size)
                    size_found = True
                    logger.debug(f"Found fixed size {size}")
                elif child.type == 'identifier' and child.text.decode('utf8') != name:
                    # 变量大小
                    size_var = child.text.decode('utf8')
                    array_sizes.append(f"var({size_var})")
                    size_found = True
                    logger.debug(f"Found variable size {size_var}")
            
            if not size_found:
                array_sizes.append("dynamic")
                logger.debug("Found dynamic size []")
            
            current = next_declarator
        
        array_sizes.reverse()
        logger.debug(f"Array declaration analysis: sizes: {array_sizes}, name: {name}")
        return array_sizes, name

    def _parse_enum_definition(self, node):
        """解析枚举定义
        
        Args:
            node: 枚举定义节点
            
        Returns:
            tuple: (enum_name, enum_values)
                - enum_name: 枚举类型名
                - enum_values: 枚举值字典
        """
        enum_name = None
        enum_values = {}
        current_value = 0
        
        # 获取枚举名称
        for child in node.children:
            if child.type == 'type_identifier':
                enum_name = child.text.decode('utf8')
                break
        
        # 获取枚举值列表
        enumerator_list = None
        for child in node.children:
            if child.type == 'enumerator_list':
                enumerator_list = child
                break
        
        if enumerator_list:
            for child in enumerator_list.children:
                if child.type == 'enumerator':
                    identifier = None
                    value = None
                    
                    # 获取标识符
                    for enum_child in child.children:
                        if enum_child.type == 'identifier':
                            identifier = enum_child.text.decode('utf8')
                        elif enum_child.type == 'number_literal':
                            # 直接数字赋值
                            try:
                                value = self._evaluate_expression(enum_child.text.decode('utf8'))
                                current_value = value
                            except:
                                logger.error(f"Failed to parse enum value: {enum_child.text.decode('utf8')}")
                        elif enum_child.type == 'binary_expression':
                            # 处理表达式
                            try:
                                expr = child.text.decode('utf8')
                                value = self._evaluate_expression(expr)
                                current_value = value
                            except:
                                logger.error(f"Failed to evaluate enum expression: {expr}")
                    
                    if identifier:
                        if value is None:
                            value = current_value
                        enum_values[identifier] = value
                        current_value += 1
        
        logger.debug(f"Parsed enum {enum_name}: {enum_values}")
        return enum_name, enum_values

    def _parse_macro_definition(self, node):
        """解析宏定义
        
        Args:
            node: 预处理器定义节点
            
        Returns:
            tuple: (macro_name, macro_value)
        """
        macro_name = None
        macro_value = None
        
        # 获取宏名称
        for child in node.children:
            if child.type == 'identifier':
                macro_name = child.text.decode('utf8')
                break
        
        # 获取宏值
        try:
            # 获取完整的宏定义文本
            full_text = node.text.decode('utf8')
            # 分离宏名和值
            parts = full_text.split(None, 2)
            if len(parts) > 2:  # 确保有值部分
                value_text = parts[2].strip()
                
                # 尝试作为数值表达式求值
                try:
                    if all(c.isdigit() or c in '+-*/%()' for c in value_text):
                        macro_value = self._evaluate_expression(value_text)
                    else:
                        # 处理字符串字面量
                        if value_text.startswith('"') and value_text.endswith('"'):
                            macro_value = value_text[1:-1]  # 去除引号
                        elif value_text.startswith('\'') and value_text.endswith('\''):
                            macro_value = value_text[1:-1]  # 去除引号
                        else:
                            macro_value = value_text
                except:
                    # 如果不是有效的表达式，保留原始文本
                    macro_value = value_text
        except:
            logger.error(f"Failed to parse macro definition: {node.text.decode('utf8')}")
        
        logger.debug(f"Parsed macro {macro_name}: {macro_value}")
        return macro_name, macro_value

    def _evaluate_expression(self, expr):
        """计算数值表达式
        
        Args:
            expr: 表达式字符串
            
        Returns:
            计算结果
        """
        # 移除所有空白字符
        expr = ''.join(expr.split())
        
        # 处理十六进制数
        def replace_hex(match):
            return str(int(match.group(0), 16))
        expr = re.sub(r'0x[0-9a-fA-F]+', replace_hex, expr)
        
        # 处理八进制数
        def replace_oct(match):
            return str(int(match.group(0), 8))
        expr = re.sub(r'0[0-7]+', replace_oct, expr)
        
        # 确保表达式只包含安全的字符
        if not re.match(r'^[\d\+\-\*/%\(\)]+$', expr):
            raise ValueError(f"Invalid expression: {expr}")
        
        # 使用 eval 计算表达式
        try:
            return eval(expr)
        except:
            raise ValueError(f"Failed to evaluate expression: {expr}")

    def _collect_enums_and_macros(self, tree):
        """收集枚举和宏定义"""
        def visit_node(node):
            if node.type == 'enum_specifier':
                enum_name, enum_values = self._parse_enum_definition(node)
                if enum_name:
                    self.enum_types[enum_name] = enum_values
            elif node.type == 'preproc_def':
                macro_name, macro_value = self._parse_macro_definition(node)
                if macro_name and macro_value is not None:
                    # 只保存数据和字符串宏，跳过函数宏
                    if not '(' in macro_name:
                        self.macro_definitions[macro_name] = macro_value
            
            # 递归访问子节点
            for child in node.children:
                visit_node(child)
        
        visit_node(tree.root_node)
 
import json
from pathlib import Path
from utils.logger import logger 
import time
from c_parser.core.type_manager import TypeManager

# 创建全局 logger


class StructCache:
    """结构体代码缓存"""
    def __init__(self):
        self.header_decls = {}  # 头文件声明缓存
        self.impl_codes = {}    # 实现代码缓存
        self.dependencies = {}  # 依赖关系缓存
        self.enable_macros = {} # 启用宏缓存

class cJsonCodeGenerator:
    def __init__(self, type_info):
        """初始化代码生成器
        
        Args:
            type_info: 包含结构体信息的字典
        """
        if not isinstance(type_info, dict):
            raise ValueError("type_info must be a dictionary")
        
        struct_info = type_info.get('struct_info', {})
        if not isinstance(struct_info, dict):
            raise ValueError("struct_info must be a dictionary")
        
        # 验证结构体信息格式
        for struct_name, struct_data in struct_info.items():
            if not isinstance(struct_data, dict):
                logger.warning(f"Invalid struct data format for {struct_name}")
                continue
            if 'fields' not in struct_data:
                logger.warning(f"Missing fields in struct {struct_name}")
                continue
            if not isinstance(struct_data['fields'], list):
                logger.warning(f"Invalid fields format in struct {struct_name}")
                continue
            
        self.struct_info = struct_info
        self.cache = StructCache()
        self.type_manager = TypeManager(type_info)
        
        logger.info(f"Initialized with {len(self.struct_info)} structs")
        for struct_name in sorted(self.struct_info.keys()):
            logger.debug(f"Found struct: {struct_name}")
        
    def generate_converter_code(self, output_dir, struct_names=None):
        """生成转换器代码"""
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建测试目录
            test_dir = output_dir / "tests"
            test_dir.mkdir(exist_ok=True)
            
            # 处理每个结构体
            for struct_name in struct_names or sorted(self.struct_info.keys()):
                # 生成主要代码
                self._update_struct_cache(struct_name, output_dir / ".cache")
                
                # 生成测试代码
                test_code = self.generate_test_code(struct_name)
                test_file = test_dir / f"test_{struct_name.lower()}.c"
                with open(test_file, 'w') as f:
                    f.write(test_code)
            
            # 生成最终代码文件
            self._generate_code_from_cache(
                output_dir / "struct_converter.h",
                output_dir / "struct_converter.c"
            )
            
        except Exception as e:
            logger.error(f"Error generating converter code: {str(e)}")
            raise
        
    def _update_struct_cache(self, struct_name, cache_dir):
        """更新结构体的代码缓存"""
        if struct_name not in self.struct_info:
            logger.warning(f"找不到结构体: {struct_name}")
            return
            
        struct_data = self.struct_info[struct_name]
        # 检查结构体信息格式
        if not isinstance(struct_data, dict):
            logger.error(f"Invalid struct info format for {struct_name}: not a dictionary")
            return
            
        fields = struct_data.get('fields', [])
        if not isinstance(fields, list):
            logger.error(f"Invalid fields format for {struct_name}: not a list")
            return
            
        # 生成代码
        header_decl = self._generate_header_declarations(struct_name)
        impl_code = self._generate_implementation_functions(struct_name, fields)
        deps = self._get_nested_structs(struct_name)
        enable_macro = f"ENABLE_{self._generate_struct_markers(struct_name)}_CONVERTER"
        
        # 更新缓存
        cache_file = cache_dir / f"{struct_name}.cache"
        cache_data = {
            'header_decl': header_decl,
            'impl_code': impl_code,
            'dependencies': deps,
            'enable_macro': enable_macro,
            'timestamp': time.time()
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
            
        # 更新内存缓存
        self.cache.header_decls[struct_name] = header_decl
        self.cache.impl_codes[struct_name] = impl_code
        self.cache.dependencies[struct_name] = deps
        self.cache.enable_macros[struct_name] = enable_macro
        
    def _generate_code_from_cache(self, header_path, impl_path):
        """从缓存生成最终代码"""
        # 生成头文件框架
        header_content = self._create_header_framework_content()
        
        # 按依赖顺序处理结构体
        processed = set()
        
        def process_struct(struct_name):
            if struct_name in processed:
                return
            # 先处理依赖
            for dep in self.cache.dependencies.get(struct_name, []):
                process_struct(dep)
            # 添加当前结构体的代码
            if struct_name in self.cache.header_decls:
                header_content.extend(self.cache.header_decls[struct_name])
                processed.add(struct_name)
        
        # 处理所有结构体
        for struct_name in sorted(self.cache.header_decls.keys()):
            process_struct(struct_name)
        
        # 添加头文件结尾
        header_content.append("\n#endif // STRUCT_CONVERTER_H")
        
        # 生成实现文件
        impl_content = self._create_impl_framework_content()
        for struct_name in processed:
            if struct_name in self.cache.impl_codes:
                impl_content.extend(self.cache.impl_codes[struct_name])
        
        # 写入文件
        with open(header_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(header_content))
        
        with open(impl_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(impl_content))

    def _create_header_framework_content(self):
        """创建头文件基本框架内容"""
        content = [
            "#ifndef STRUCT_CONVERTER_H",
            "#define STRUCT_CONVERTER_H",
            "",
            "// 结构体转换配置",
            "// 设置为1启用相应结构体的转换功能",
            ""
        ]

        # 添加配置宏定义
        for struct_name in sorted(self.struct_info.keys()):
            enable_macro = self.cache.enable_macros.get(struct_name)
            if enable_macro:
                content.append(f"#define {enable_macro} 1  // 默认启用")

        content.extend([
            "",
            "// 结构体依赖关系检查"
        ])

        # 添加依赖检查
        for struct_name, deps in self.cache.dependencies.items():
            if deps:
                enable_macro = self.cache.enable_macros.get(struct_name)
                if enable_macro:
                    content.append("")
                    content.append(f"#if {enable_macro}")
                    for dep in deps:
                        dep_macro = self.cache.enable_macros.get(dep)
                        if dep_macro:
                            content.extend([
                                f"#if !{dep_macro}",
                                f"#error struct {struct_name} converter requires {dep} converter to be enabled",
                                "#endif"
                            ])
                    content.append("#endif")

        # 添加标准头文件
        content.extend([
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
            "// 结构体转换函数声明"
        ])
        
        return content

    def _create_impl_framework_content(self):
        """创建实现文件基本框架内容"""
        return [
            '#include "struct_converter.h"',
            "#include <string.h>",
            "#include <stdlib.h>",
            "",
            "// 数组转换辅助宏",
            "#define DEFINE_ARRAY_CONVERTERS(type) \\",
            "cJSON* type##_array_to_json(const type* data, const type* default_data, size_t size) { \\",
            "    if (!data) return NULL; \\",
            "    cJSON* array = cJSON_CreateArray(); \\",
            "    if (!array) return NULL; \\",
            "    for (size_t i = 0; i < size; i++) { \\",
            "        cJSON* item = type##_to_json(&data[i], default_data ? &default_data[i] : NULL); \\",
            "        if (item) { \\",
            "            cJSON_AddItemToArray(array, item); \\",
            "        } \\",
            "    } \\",
            "    return array; \\",
            "} \\",
            "\\",
            "convert_status_t json_to_##type##_array(const cJSON* json, const type* default_data, type* data, size_t size) { \\",
            "    if (!json || !data) return CONVERT_INVALID_PARAM; \\",
            "    if (!cJSON_IsArray(json)) return CONVERT_PARSE_ERROR; \\",
            "    size_t json_size = cJSON_GetArraySize(json); \\",
            "    size_t copy_size = (json_size < size) ? json_size : size; \\",
            "    for (size_t i = 0; i < copy_size; i++) { \\",
            "        cJSON* item = cJSON_GetArrayItem(json, i); \\",
            "        convert_status_t status = json_to_##type(item, default_data ? &default_data[i] : NULL, &data[i]); \\",
            "        if (status != CONVERT_SUCCESS) return status; \\",
            "    } \\",
            "    if (default_data && json_size < size) { \\",
            "        for (size_t i = json_size; i < size; i++) { \\",
            "            data[i] = default_data[i]; \\",
            "        } \\",
            "    } \\",
            "    return CONVERT_SUCCESS; \\",
            "}"
        ]

    def _generate_struct_markers(self, struct_name):
        """生成结构体标记"""
        struct_name = struct_name.replace(' ', '_').upper()
        return struct_name

    def _get_nested_structs(self, struct_name):
        """获取结构体中的所有非匿名嵌套结构体类型"""
        nested_structs = set()
        logger.debug(f"\nAnalyzing dependencies for struct: {struct_name}")
        
        def normalize_struct_name(name):
            """标准化结构体名称"""
            # 处理 "struct X" 格式
            if name.startswith('struct '):
                name = name.replace('struct ', '')
            # 移除指针标记
            name = name.rstrip('*')
            # 如果名称以 "struct " 开头，移除它
            if name.startswith('struct '):
                name = name[7:]
            return name
        
        def collect_nested_structs(fields):
            for field in fields:
                if not isinstance(field, dict):
                    logger.warning(f"Invalid field format in struct {struct_name}: {field}")
                    continue
                
                logger.debug(f"Checking field: {field.get('name', 'unknown')}")
                logger.debug(f"Field details: {json.dumps(field, indent=2)}")
                
                # 检查原始类型
                original_type = field.get('original_type', '')
                logger.debug(f"Original type: {original_type}")
                if original_type:
                    normalized_type = normalize_struct_name(original_type)
                    if normalized_type in self.struct_info and normalized_type != normalize_struct_name(struct_name):
                        logger.debug(f"Found struct dependency from original_type: {normalized_type}")
                        nested_structs.add(normalized_type)
                
                # 检查字段类型
                field_type = field.get('type', '')
                logger.debug(f"Field type: {field_type}")
                if field_type:
                    normalized_type = normalize_struct_name(field_type)
                    if normalized_type in self.struct_info and normalized_type != normalize_struct_name(struct_name):
                        logger.debug(f"Found struct dependency from field_type: {normalized_type}")
                        nested_structs.add(normalized_type)
                
                # 检查数组元素类型
                array_type = field.get('array_type', '')
                logger.debug(f"Array type: {array_type}")
                if array_type:
                    normalized_type = normalize_struct_name(array_type)
                    if normalized_type in self.struct_info and normalized_type != normalize_struct_name(struct_name):
                        logger.debug(f"Found struct dependency from array_type: {normalized_type}")
                        nested_structs.add(normalized_type)
                
                # 检查指针类型
                pointer_type = field.get('pointer_type', '')
                logger.debug(f"Pointer type: {pointer_type}")
                if pointer_type:
                    normalized_type = normalize_struct_name(pointer_type)
                    if normalized_type in self.struct_info and normalized_type != normalize_struct_name(struct_name):
                        logger.debug(f"Found struct dependency from pointer_type: {normalized_type}")
                        nested_structs.add(normalized_type)
                
                # 检查嵌套字段
                nested_fields = field.get('nested_fields')
                if nested_fields:
                    logger.debug(f"Checking nested fields for {field.get('name', 'unknown')}")
                    collect_nested_structs(nested_fields)
        
        struct_data = self.struct_info.get(struct_name, {})
        if isinstance(struct_data, dict):
            fields = struct_data.get('fields', [])
            if isinstance(fields, list):
                logger.debug(f"Processing {len(fields)} fields")
                collect_nested_structs(fields)
                logger.debug(f"Final nested structs for {struct_name}: {nested_structs}")
            else:
                logger.error(f"Invalid fields format for {struct_name}")
        else:
            logger.error(f"Invalid struct info format for {struct_name}")
        
        # 打印最终的依赖列表
        result = sorted(list(nested_structs)) if nested_structs else []
        logger.info(f"Dependencies for {struct_name}: {result}")
        return result

    def _generate_header_declarations(self, struct_name):
        """生成头文件声明"""
        # 移除可能的 struct 前缀
        clean_name = struct_name.replace('struct ', '')
        
        declarations = [
            "",
            f"#if ENABLE_{self._generate_struct_markers(struct_name)}_CONVERTER",
            "",
            f"// {struct_name} 转换函数",
            f"cJSON* {clean_name.lower()}_to_json(const struct {clean_name}* data, const struct {clean_name}* default_data);",
            f"convert_status_t json_to_{clean_name.lower()}(const cJSON* json, const struct {clean_name}* default_data, struct {clean_name}* data);",
            "",
            f"// {struct_name} 数组转换函数",
            f"DECLARE_ARRAY_CONVERTERS(struct {clean_name})",
            "",
            f"// {struct_name} 打印函数",
            f"void print_{clean_name.lower()}(const struct {clean_name}* data);",
            "",
            f"#endif  // ENABLE_{self._generate_struct_markers(struct_name)}_CONVERTER",
            ""
        ]
        
        return declarations

    def _generate_implementation_functions(self, struct_name, fields):
        """生成实现文件函数"""
        # 移除可能的 struct 前缀
        clean_name = struct_name.replace('struct ', '')
        
        implementations = [
            f"#if ENABLE_{self._generate_struct_markers(struct_name)}_CONVERTER",
            "",
            f"DEFINE_ARRAY_CONVERTERS(struct {clean_name})",
            "",
            self._generate_to_json_function(clean_name, fields),
            "",
            self._generate_to_struct_function(clean_name, fields),
            "",
            "// 打印函数",
            self._generate_print_functions(clean_name, fields),
            "",
            f"#endif  // ENABLE_{self._generate_struct_markers(struct_name)}_CONVERTER"
        ]
        
        return implementations

    def _generate_to_json_function(self, struct_name, fields):
        """生成结构体转JSON的函数"""
        lines = [
            f"cJSON* {struct_name.lower()}_to_json(const struct {struct_name}* data, const struct {struct_name}* default_data) {{",
            "    if (!data) return NULL;",
            "    cJSON* root = cJSON_CreateObject();",
            "    if (!root) return NULL;",
            ""
        ]
        
        # 生成每个字段的转换代码
        for field in fields:
            field_name = field['name']
            field_type = field['type']
            is_pointer = field.get('is_pointer', False)
            is_array = field.get('is_array', False)
            array_size = field.get('array_size', [])
            
            # 添加字段注释
            lines.append(f"    // 处理{field_type}类型字段 {field_name}")
            
            # 生成字段比较代码
            if is_pointer:
                lines.extend([
                    f"    if (!default_data || data->{field_name} != default_data->{field_name}) {{",
                    f"        if (data->{field_name}) {{"
                ])
                if field_type.startswith('struct '):
                    struct_type = field_type.split()[1]
                    lines.extend([
                        f"            cJSON* {field_name}_json = struct_{struct_type.lower()}_to_json(data->{field_name}, "
                        f"default_data ? default_data->{field_name} : NULL);",
                        f"            if ({field_name}_json) {{",
                        f"                cJSON_AddItemToObject(root, \"{field_name}\", {field_name}_json);",
                        "            }"
                    ])
                else:
                    lines.append(f"            cJSON_AddNumberToObject(root, \"{field_name}\", *data->{field_name});")
                lines.extend([
                    "        }",
                    "    }"
                ])
            elif is_array:
                if field_type == 'char':
                    lines.extend([
                        f"    if (!default_data || strcmp(data->{field_name}, default_data->{field_name}) != 0) {{",
                        f"        cJSON_AddStringToObject(root, \"{field_name}\", data->{field_name});",
                        "    }"
                    ])
                else:
                    size_expr = ' * '.join(str(s) for s in array_size)
                    lines.extend([
                        f"    if (!default_data || memcmp(data->{field_name}, default_data->{field_name}, "
                        f"sizeof({field_type}) * ({size_expr})) != 0) {{",
                        f"        cJSON* {field_name}_array = cJSON_CreateArray();",
                        f"        if ({field_name}_array) {{",
                        f"            for (size_t i = 0; i < {size_expr}; i++) {{",
                        f"                cJSON_AddNumberToObject({field_name}_array, NULL, data->{field_name}[i]);",
                        "            }",
                        f"            cJSON_AddItemToObject(root, \"{field_name}\", {field_name}_array);",
                        "        }",
                        "    }"
                    ])
            else:
                lines.extend([
                    f"    if (!default_data || data->{field_name} != default_data->{field_name}) {{",
                    f"        cJSON_AddNumberToObject(root, \"{field_name}\", data->{field_name});",
                    "    }"
                ])
            
            lines.append("")
        
        lines.extend([
            "    return root;",
            "}"
        ])
        
        return '\n'.join(lines)

    def _generate_to_struct_function(self, struct_name, fields):
        """生成JSON转结构体的函数"""
        lines = [
            f"convert_status_t json_to_{struct_name.lower()}(const cJSON* json, const struct {struct_name}* default_data, struct {struct_name}* data) {{",
            "    if (!json || !data) return CONVERT_INVALID_PARAM;",
            "    if (!cJSON_IsObject(json)) return CONVERT_PARSE_ERROR;",
            "",
            "    // 如果有默认值，先复制默认值",
            "    if (default_data) {",
            "        *data = *default_data;",
            "    }",
            ""
        ]
        
        # 生成每个字段的转换代码
        for field in fields:
            field_name = field['name']
            field_type = field['type']
            is_pointer = field.get('is_pointer', False)
            is_array = field.get('is_array', False)
            
            # 添加字段注释
            lines.append(f"    // 处理 {field_name} 字段")
            lines.append(f"    cJSON* {field_name}_json = cJSON_GetObjectItem(json, \"{field_name}\");")
            
            if is_pointer:
                if field_type.startswith('struct '):
                    struct_type = field_type.split()[1]
                    lines.extend([
                        f"    if ({field_name}_json && cJSON_IsObject({field_name}_json)) {{",
                        f"        convert_status_t status = json_to_struct_{struct_type.lower()}({field_name}_json,",
                        f"            default_data ? default_data->{field_name} : NULL,",
                        f"            &data->{field_name});",
                        "        if (status != CONVERT_SUCCESS) return status;",
                        "    }"
                    ])
                else:
                    lines.extend([
                        f"    if ({field_name}_json && cJSON_IsNumber({field_name}_json)) {{",
                        f"        data->{field_name} = {field_name}_json->valueint;",
                        "    }"
                    ])
            elif is_array:
                if field_type == 'char':
                    lines.extend([
                        f"    if ({field_name}_json && cJSON_IsString({field_name}_json)) {{",
                        f"        strncpy(data->{field_name}, {field_name}_json->valuestring, sizeof(data->{field_name}) - 1);",
                        f"        data->{field_name}[sizeof(data->{field_name}) - 1] = '\\0';",
                        "    }"
                    ])
                else:
                    lines.extend([
                        f"    if ({field_name}_json && cJSON_IsArray({field_name}_json)) {{",
                        f"        size_t size = cJSON_GetArraySize({field_name}_json);",
                        f"        for (size_t i = 0; i < size && i < sizeof(data->{field_name})/sizeof(data->{field_name}[0]); i++) {{",
                        f"            cJSON* item = cJSON_GetArrayItem({field_name}_json, i);",
                        f"            if (item && cJSON_IsNumber(item)) {{",
                        f"                data->{field_name}[i] = item->valueint;",
                        "            }",
                        "        }",
                        "    }"
                    ])
            else:
                lines.extend([
                    f"    if ({field_name}_json && cJSON_IsNumber({field_name}_json)) {{",
                    f"        data->{field_name} = {field_name}_json->valueint;",
                    "    }"
                ])
            
            lines.append("")
        
        lines.extend([
            "    return CONVERT_SUCCESS;",
            "}"
        ])
        
        return '\n'.join(lines)

    def _generate_print_functions(self, struct_name, fields):
        """生成结构体打印函数"""
        lines = [
            f"void print_{struct_name.lower()}(const struct {struct_name}* data) {{",
            "    if (!data) {",
            '        printf("NULL\\n");',
            "        return;",
            "    }",
            "",
            f'    printf("struct {struct_name} {{\\n");'
        ]
        
        # 生成每个字段的打印代码
        for field in fields:
            field_name = field['name']
            field_type = field.get('original_type', field['type'])
            is_array = field.get('is_array', False)
            array_size = field.get('array_size', [])
            is_pointer = field.get('is_pointer', False)
            
            lines.append(f'    printf("    {field_name}: ");')
            
            if is_array:
                # 处理数组
                if len(array_size) == 1:
                    # 一维数组
                    lines.extend([
                        f'    printf("[\\n");',
                        f"    for (size_t i = 0; i < {array_size[0]}; i++) {{",
                        "        if (i > 0) printf(\",\\n\");",  # 每个元素后换行
                        "        printf(\"        \");"  # 缩进
                    ])
                    
                    if self._is_struct_type(field_type):
                        # 结构体数组
                        clean_type = self._get_clean_type_name(field_type)
                        lines.append(f"        print_{clean_type.lower()}(&data->{field_name}[i]);")
                    else:
                        # 基本类型数组
                        lines.append("        " + self._generate_print_value(f"data->{field_name}[i]", field_type))
                    
                    lines.extend([
                        "    }",
                        f'    printf("    ]\\n");'  # 数组结束
                    ])
                else:
                    # 多维数组
                    dims = len(array_size)
                    indent = "    " * (dims + 1)
                    loops = []
                    indexes = []
                    
                    for i, size in enumerate(array_size):
                        idx = f"i{i}"
                        indexes.append(idx)
                        loops.append(f"    for (size_t {idx} = 0; {idx} < {size}; {idx}++) {{")
                    
                    lines.extend([
                        f'    printf("[\\n");'
                    ])
                    
                    # 添加所有循环
                    lines.extend(loops)
                    
                    # 处理分隔符和缩进
                    lines.extend([
                        f"{indent}if ({' > 0 || '.join(indexes)} > 0) printf(\",\\n\");",
                        f"{indent}printf(\"{indent}\");"
                    ])
                    
                    if self._is_struct_type(field_type):
                        # 结构体数组
                        clean_type = self._get_clean_type_name(field_type)
                        lines.append(f"{indent}print_{clean_type.lower()}(&data->{field_name}[{']['.join(indexes)}]);")
                    else:
                        # 基本类型数组
                        lines.append(indent + self._generate_print_value(f"data->{field_name}[{']['.join(indexes)}]", field_type))
                    
                    # 关闭所有循环
                    for _ in range(dims):
                        lines.append("    }")
                    
                    lines.append(f'    printf("    ]\\n");')  # 数组结束
            
            elif is_pointer:
                # 处理指针
                lines.extend([
                    f"    printf(\"0x%p \", (void*)data->{field_name});",
                    f"    if (data->{field_name}) {{"
                ])
                
                if self._is_struct_type(field_type):
                    # 结构体指针
                    clean_type = self._get_clean_type_name(field_type)
                    lines.extend([
                        "        printf(\"-> \");",
                        f"        print_{clean_type.lower()}(data->{field_name});"
                    ])
                else:
                    # 基本类型指针
                    lines.extend([
                        "        printf(\"-> \");",
                        "        " + self._generate_print_value(f"*data->{field_name}", field_type)
                    ])
                
                lines.extend([
                    "    } else {",
                    '        printf("(NULL)");',
                    "    }",
                    '    printf("\\n");'
                ])
            
            else:
                # 处理普通字段
                if self._is_struct_type(field_type):
                    # 嵌套结构体
                    clean_type = self._get_clean_type_name(field_type)
                    lines.extend([
                        "    printf(\"\\n\");",
                        f"    print_{clean_type.lower()}(&data->{field_name});"
                    ])
                else:
                    # 基本类型
                    lines.extend([
                        self._generate_print_value(f"data->{field_name}", field_type),
                        '    printf("\\n");'
                    ])
        
        lines.extend([
            '    printf("}\\n");',
            "}"
        ])
        
        return '\n'.join(lines)

    def _generate_print_value(self, expr: str, type_name: str) -> str:
        """生成值打印代码"""
        # 使用类型管理器判断类型
        if self.type_manager.is_struct_type(type_name):
            clean_type = self._get_clean_type_name(type_name)
            return f'    print_{clean_type.lower()}(&{expr});'
        
        # 获取打印格式
        fmt = self.type_manager.get_printf_format(type_name)
        
        # 处理布尔类型
        if self.type_manager.get_real_type(type_name) == 'bool':
            return f'    printf({fmt}, {expr} ? "true" : "false");'
        
        return f'    printf({fmt}, {expr});'

    def _is_struct_type(self, type_name: str) -> bool:
        """检查是否为结构体类型"""
        return self.type_manager.is_struct_type(type_name)

    def _get_clean_type_name(self, type_name: str) -> str:
        """获取清理后的类型名称"""
        return self.type_manager._clean_type_name(type_name)

    def _generate_memory_management_functions(self, struct_name):
        """生成内存管理相关函数"""
        clean_name = self._get_clean_type_name(struct_name)
        
        code = [
            f"// 内存管理函数",
            f"void {clean_name.lower()}_init(struct {clean_name}* data) {{",
            "    if (!data) return;",
            "    memset(data, 0, sizeof(*data));",
            "}",
            "",
            f"void {clean_name.lower()}_cleanup(struct {clean_name}* data) {{",
            "    if (!data) return;",
            ""
        ]
        
        # 处理需要清理的字段
        for field in self.struct_info[struct_name]['fields']:
            if field.get('pointer_type'):
                field_name = field['name']
                code.extend([
                    f"    // 清理指针字段 {field_name}",
                    f"    if (data->{field_name}) {{",
                    f"        free(data->{field_name});",
                    f"        data->{field_name} = NULL;",
                    "    }"
                ])
        
        code.extend([
            "}",
            "",
            f"struct {clean_name}* {clean_name.lower()}_create(void) {{",
            f"    struct {clean_name}* data = malloc(sizeof(struct {clean_name}));",
            "    if (data) {",
            f"        {clean_name.lower()}_init(data);",
            "    }",
            "    return data;",
            "}",
            "",
            f"void {clean_name.lower()}_destroy(struct {clean_name}* data) {{",
            "    if (!data) return;",
            f"    {clean_name.lower()}_cleanup(data);",
            "    free(data);",
            "}"
        ])
        
        return '\n'.join(code)

    def _generate_type_validation_functions(self, struct_name):
        """生成类型验证函数"""
        clean_name = self._get_clean_type_name(struct_name)
        
        code = [
            f"// 类型验证函数",
            f"typedef enum {{",
            f"    {clean_name.upper()}_VALID = 0,",
            f"    {clean_name.upper()}_NULL_PTR,",
            f"    {clean_name.upper()}_INVALID_FIELD",
            f"}} {clean_name}_validation_t;",
            "",
            f"{clean_name}_validation_t {clean_name.lower()}_validate(const struct {clean_name}* data) {{",
            "    if (!data) return {}_NULL_PTR;".format(clean_name.upper()),
            ""
        ]
        
        # 添加字段验证
        for field in self.struct_info[struct_name]['fields']:
            field_name = field['name']
            field_type = field['type']
            
            if field.get('pointer_type'):
                # 指针字段验证
                code.extend([
                    f"    // 验证指针字段 {field_name}",
                    f"    if (data->{field_name} && !{self._generate_pointer_validation(field)}) {{",
                    f"        return {clean_name.upper()}_INVALID_FIELD;",
                    "    }"
                ])
            elif field.get('array_size'):
                # 数组字段验证
                code.extend([
                    f"    // 验证数组字段 {field_name}",
                    f"    if (!{self._generate_array_validation(field)}) {{",
                    f"        return {clean_name.upper()}_INVALID_FIELD;",
                    "    }"
                ])
        
        code.extend([
            "",
            f"    return {clean_name.upper()}_VALID;",
            "}"
        ])
        
        return '\n'.join(code)

    def _generate_pointer_validation(self, field):
        """生成指针验证代码"""
        ptr_type = field.get('pointer_type')
        if ptr_type == 'void':
            return "1"  # void指针不做验证
        elif ptr_type == 'char':
            return "strlen(data->{}) < MAX_STRING_LENGTH".format(field['name'])
        else:
            clean_type = self._get_clean_type_name(ptr_type)
            return f"{clean_type.lower()}_validate(data->{field['name']}) == {clean_type.upper()}_VALID"

    def _generate_array_validation(self, field):
        """生成数组验证代码"""
        if field['type'] == 'char':
            return f"strlen(data->{field['name']}) < sizeof(data->{field['name']})"
        else:
            return "1"  # 基本类型数组不做特殊验证

    def _generate_debug_functions(self, struct_name):
        """生成调试相关函数"""
        clean_name = self._get_clean_type_name(struct_name)
        
        code = [
            f"// 调试函数",
            "#ifdef DEBUG",
            f"void {clean_name.lower()}_debug_print(const struct {clean_name}* data, int indent_level) {{",
            "    char indent[256] = {0};",
            "    for (int i = 0; i < indent_level && i < sizeof(indent)-1; i++) {",
            '        strcat(indent, "    ");',
            "    }",
            "",
            "    if (!data) {",
            f'        printf("%sNULL {clean_name}\\n", indent);',
            "        return;",
            "    }",
            "",
            f'    printf("%s{clean_name} {{\\n", indent);'
        ]
        
        # 添加字段打印
        for field in self.struct_info[struct_name]['fields']:
            field_name = field['name']
            code.extend(self._generate_debug_field_print(field, "indent"))
        
        code.extend([
            f'    printf("%s}}\\n", indent);',
            "}",
            "#endif // DEBUG"
        ])
        
        return '\n'.join(code)

    def _generate_json_format_options(self):
        """生成JSON格式化选项"""
        return """
// JSON格式化选项
typedef struct {
    bool pretty_print;     // 是否美化输出
    int indent_size;       // 缩进大小
    bool sort_keys;        // 是否对键进行排序
    bool escape_unicode;   // 是否转义Unicode字符
} json_format_options_t;

// 默认格式化选项
static const json_format_options_t DEFAULT_FORMAT_OPTIONS = {
    .pretty_print = true,
    .indent_size = 4,
    .sort_keys = false,
    .escape_unicode = true
};
"""

    def _generate_documentation(self, struct_name):
        """生成文档注释"""
        clean_name = self._get_clean_type_name(struct_name)
        
        doc = [
            "/**",
            f" * @brief {clean_name} 结构体的JSON转换函数",
            " *",
            " * @details 该模块提供以下功能：",
            f" * - 将 {clean_name} 结构体转换为JSON",
            f" * - 将JSON转换为 {clean_name} 结构体",
            " * - 内存管理和清理",
            " * - 类型验证",
            " * - 调试打印",
            " *",
            " * @example",
            " * ```c",
            f" * struct {clean_name} data = {{0}};",
            f" * {clean_name.lower()}_init(&data);",
            " * ",
            " * // 转换为JSON",
            f" * cJSON* json = {clean_name.lower()}_to_json(&data, NULL);",
            " * char* json_str = cJSON_Print(json);",
            " * printf(\"%s\\n\", json_str);",
            " * free(json_str);",
            " * cJSON_Delete(json);",
            " * ",
            f" * // 从JSON转换回结构体",
            f" * struct {clean_name} new_data = {{0}};",
            f" * json_to_{clean_name.lower()}(json, NULL, &new_data);",
            " * ```",
            " */",
            ""
        ]
        
        return '\n'.join(doc)

    def generate_test_code(self, struct_name):
        """生成测试代码"""
        clean_name = self._get_clean_type_name(struct_name)
        
        test_code = [
            f"#include <unity.h>",
            f"#include \"{clean_name.lower()}_converter.h\"",
            "",
            "void setUp(void) {}",
            "void tearDown(void) {}",
            "",
            f"void test_{clean_name.lower()}_init(void) {{",
            f"    struct {clean_name} data;",
            f"    {clean_name.lower()}_init(&data);",
            "    // TODO: Add initialization checks",
            "}",
            "",
            f"void test_{clean_name.lower()}_json_conversion(void) {{",
            f"    struct {clean_name} data = {{0}};",
            "    // TODO: Set test data",
            "",
            f"    cJSON* json = {clean_name.lower()}_to_json(&data, NULL);",
            "    TEST_ASSERT_NOT_NULL(json);",
            "",
            f"    struct {clean_name} new_data = {{0}};",
            f"    convert_status_t status = json_to_{clean_name.lower()}(json, NULL, &new_data);",
            "    TEST_ASSERT_EQUAL(CONVERT_SUCCESS, status);",
            "",
            "    // TODO: Add comparison checks",
            "",
            "    cJSON_Delete(json);",
            "}",
            "",
            "int main(void) {",
            "    UNITY_BEGIN();",
            f"    RUN_TEST(test_{clean_name.lower()}_init);",
            f"    RUN_TEST(test_{clean_name.lower()}_json_conversion);",
            "    return UNITY_END();",
            "}"
        ]
        
        return '\n'.join(test_code)

    def _generate_cache_mechanism(self):
        """生成缓存机制代码"""
        return """
// JSON缓存机制
#ifdef CONVERTER_USE_CACHE
#include <uthash.h>

typedef struct {
    char* key;           // 缓存键
    cJSON* json;         // 缓存的JSON对象
    time_t timestamp;    // 缓存时间戳
    UT_hash_handle hh;   // uthash句柄
} json_cache_entry_t;

static json_cache_entry_t* g_json_cache = NULL;

// 缓存清理函数
static void cleanup_expired_cache(void) {
    json_cache_entry_t *entry, *tmp;
    time_t now = time(NULL);
    
    HASH_ITER(hh, g_json_cache, entry, tmp) {
        if (now - entry->timestamp > CACHE_TTL) {
            HASH_DEL(g_json_cache, entry);
            cJSON_Delete(entry->json);
            free(entry->key);
            free(entry);
        }
    }
}
#endif
"""

    def _generate_debug_field_print(self, field, indent_var):
        """生成字段调试打印代码"""
        field_name = field['name']
        field_type = field['type']
        code = []
        
        # 添加字段名称打印
        code.append(f'    printf("%s  {field_name}: ", {indent_var});')
        
        if field.get('pointer_type'):
            # 指针字段打印
            code.extend([
                f"    if (data->{field_name}) {{",
                f"        {self._generate_print_value(f'*data->{field_name}', field['pointer_type'])}",
                "    } else {",
                '        printf("NULL");',
                "    }"
            ])
        elif field.get('array_size'):
            # 数组字段打印
            dims = len(field['array_size'])
            code.extend(self._generate_array_debug_print(field, indent_var))
        else:
            # 普通字段打印
            code.append(self._generate_print_value(f"data->{field_name}", field_type))
        
        code.append('    printf("\\n");')
        return code
 
from pathlib import Path
import json
from typing import Dict, Any, List, Optional
from utils.logger_config import setup_logger

logger = setup_logger('DataGenerator')

class DataGenerator:
    """数据定义生成器"""
    
    def __init__(self, type_info: Dict[str, Any]):
        """初始化数据生成器
        
        Args:
            type_info: 包含类型信息的字典
        """
        self.type_info = type_info
        self.struct_info = type_info.get('struct_info', {})
        
    def generate_data_definition(self, output_path: Path) -> None:
        """生成数据定义文件
        
        Args:
            output_path: 输出文件路径
        """
        definitions = []
        
        # 生成结构体定义
        for struct_name, struct_data in self.struct_info.items():
            definitions.extend(self._generate_struct_definition(struct_name, struct_data))
            
        # 写入文件
        output_path.write_text('\n'.join(definitions), encoding='utf-8')
        
    def generate_variable_definitions(self, json_data: Dict[str, Any], output_path: Path) -> None:
        """根据JSON数据生成变量定义
        
        Args:
            json_data: JSON数据
            output_path: 输出文件路径
        """
        definitions = []
        
        # 添加头文件包含
        definitions.extend(self._generate_includes())
        definitions.append("")
        
        # 处理变量定义
        if 'variables' in json_data:
            # 处理普通变量
            for var in json_data['variables']:
                definitions.extend(self._generate_variable_definition(var['name'], var))
        
        if 'struct_vars' in json_data:
            # 处理结构体变量
            for var in json_data['struct_vars']:
                definitions.extend(self._generate_variable_definition(var['name'], var))
        
        if 'array_vars' in json_data:
            # 处理数组变量
            for var in json_data['array_vars']:
                definitions.extend(self._generate_variable_definition(var['name'], var))
        
        if 'pointer_vars' in json_data:
            # 处理指针变量
            for var in json_data['pointer_vars']:
                definitions.extend(self._generate_variable_definition(var['name'], var))
        
        # 写入文件
        output_path.write_text('\n'.join(definitions), encoding='utf-8')
        
    def _generate_struct_definition(self, struct_name: str, struct_data: Dict[str, Any]) -> List[str]:
        """生成结构体定义
        
        Args:
            struct_name: 结构体名称
            struct_data: 结构体数据
        
        Returns:
            结构体定义代码列表
        """
        lines = [
            f"struct {struct_name} {{",
        ]
        
        # 添加字段定义
        for field in struct_data.get('fields', []):
            field_def = self._generate_field_definition(field)
            lines.append(f"    {field_def};")
            
        lines.extend([
            "};",
            ""
        ])
        
        return lines
        
    def _generate_field_definition(self, field: Dict[str, Any]) -> str:
        """生成字段定义
        
        Args:
            field: 字段信息
            
        Returns:
            字段定义字符串
        """
        field_type = field['type']
        field_name = field['name']
        
        # 处理数组
        if field.get('is_array'):
            array_dims = field.get('array_size', [])
            array_suffix = ''.join(f'[{dim}]' for dim in array_dims)
            return f"{field_type} {field_name}{array_suffix}"
            
        # 处理指针
        if field.get('is_pointer'):
            return f"{field_type}* {field_name}"
            
        return f"{field_type} {field_name}" 

    def _generate_variable_definition(self, var_name: str, var_data: Dict[str, Any]) -> List[str]:
        """生成变量定义
        
        Args:
            var_name: 变量名称
            var_data: 变量数据
            
        Returns:
            变量定义代码列表
        """
        definitions = []
        
        # 获取变量类型信息
        var_type = var_data.get('type', '')
        original_type = var_data.get('original_type', '')
        is_pointer = var_data.get('is_pointer', False)
        array_size = var_data.get('array_size', [])
        value = var_data.get('value')
        
        # 生成变量声明
        if array_size:
            # 数组变量
            array_dims = ''.join(f'[{dim}]' for dim in array_size)
            decl = f"{original_type} {var_name}{array_dims}"
        elif is_pointer:
            # 指针变量
            decl = f"{original_type}* {var_name}"
        else:
            # 普通变量
            decl = f"{original_type} {var_name}"
        
        # 生成初始化代码
        if value is not None:
            init = self._generate_initializer(value, original_type, array_size)
            definitions.append(f"{decl} = {init};")
        else:
            definitions.append(f"{decl};")
        
        definitions.append("")  # 添加空行
        return definitions

    def _generate_initializer(self, value: Any, type_name: str, array_dims: List[int] = None) -> str:
        """生成初始化表达式
        
        Args:
            value: 初始值
            type_name: 类型名称
            array_dims: 数组维度
            
        Returns:
            初始化表达式字符串
        """
        # 处理字符串
        if isinstance(value, str):
            if value.startswith('"') or value.isidentifier():
                return value
            return f'"{value}"'
        
        # 处理数组
        if isinstance(value, (list, tuple)):
            if not array_dims:
                return str(value[0])  # 非数组类型，取第一个值
            
            # 处理多维数组
            if len(array_dims) > 1:
                items = [
                    self._generate_initializer(item, type_name, array_dims[1:])
                    for item in value
                ]
                return "{\n    " + ",\n    ".join(items) + "\n}"
            
            # 处理一维数组
            items = [
                self._generate_initializer(item, type_name, None)
                for item in value
            ]
            return "{" + ", ".join(items) + "}"
        
        # 处理结构体
        if isinstance(value, dict):
            if type_name.startswith('struct '):
                struct_name = type_name.split()[1]
                if struct_name in self.struct_info:
                    items = []
                    struct_fields = self.struct_info[struct_name].get('fields', [])
                    for field in struct_fields:
                        field_name = field['name']
                        field_value = value.get(field_name)
                        if field_value is not None:
                            field_type = field['original_type']
                            field_array = field.get('array_size')
                            init = self._generate_initializer(field_value, field_type, field_array)
                            items.append(f".{field_name} = {init}")
                    return "{" + ", ".join(items) + "}"
            return str(value)
        
        # 处理基本类型
        return str(value)

    def _get_type_info(self, var_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """获取类型信息
        
        Args:
            var_data: 变量数据
            
        Returns:
            类型信息字典
        """
        type_name = var_data.get('type', '')
        
        # 检查结构体类型
        if type_name.startswith('struct '):
            struct_name = type_name.split()[1]
            return self.struct_info.get(struct_name)
        
        return None

    def _format_value(self, value: Any) -> str:
        """格式化值
        
        Args:
            value: 要格式化的值
            
        Returns:
            格式化后的字符串
        """
        if isinstance(value, str):
            if value.startswith('"'):
                return value
            return f'"{value}"'
        if isinstance(value, (list, tuple)):
            items = [self._format_value(item) for item in value]
            return "{" + ", ".join(items) + "}"
        if isinstance(value, dict):
            items = [f".{k} = {self._format_value(v)}" for k, v in value.items()]
            return "{" + ", ".join(items) + "}"
        return str(value) 

    def _generate_includes(self) -> List[str]:
        """生成头文件包含语句
        
        Returns:
            头文件包含语句列表
        """
        includes = [
            "// 自动生成的变量定义",
            "#include <stdint.h>",
            "#include <stddef.h>",
            "#include <stdbool.h>",
            "#include <string.h>",
            "#include <limits.h>",
            "#include <float.h>"
        ]
        
        # 添加自定义头文件
        includes.append('#include "test_data.h"')
        
        return includes

    def _generate_array_initializer(self, value: List[Any], type_name: str, dims: List[int]) -> str:
        """生成数组初始化表达式
        
        Args:
            value: 数组值
            type_name: 类型名称
            dims: 数组维度
            
        Returns:
            初始化表达式字符串
        """
        if not dims:
            return self._generate_initializer(value, type_name)
        
        if len(dims) == 1:
            # 一维数组
            items = []
            for item in value[:dims[0]]:
                items.append(self._generate_initializer(item, type_name))
            return "{" + ", ".join(items) + "}"
        else:
            # 多维数组
            items = []
            for subarray in value[:dims[0]]:
                init = self._generate_array_initializer(subarray, type_name, dims[1:])
                items.append(init)
            return "{\n    " + ",\n    ".join(items) + "\n}"

    def _generate_struct_initializer(self, value: Dict[str, Any], struct_name: str) -> str:
        """生成结构体初始化表达式
        
        Args:
            value: 结构体值
            struct_name: 结构体名称
            
        Returns:
            初始化表达式字符串
        """
        if struct_name not in self.struct_info:
            return str(value)
        
        struct_def = self.struct_info[struct_name]
        items = []
        
        for field in struct_def.get('fields', []):
            field_name = field['name']
            if field_name in value:
                field_value = value[field_name]
                field_type = field.get('original_type', field['type'])
                
                # 处理字段初始化
                if field.get('is_array'):
                    init = self._generate_array_initializer(
                        field_value,
                        field_type,
                        field.get('array_size', [])
                    )
                elif field.get('is_pointer'):
                    init = self._format_pointer_value(field_value)
                else:
                    init = self._generate_initializer(field_value, field_type)
                    
                items.append(f".{field_name} = {init}")
                
        return "{" + ", ".join(items) + "}"

    def _format_pointer_value(self, value: Any) -> str:
        """格式化指针值
        
        Args:
            value: 指针值
            
        Returns:
            格式化后的字符串
        """
        if value is None:
            return "NULL"
        if isinstance(value, str):
            if value.startswith('&'):
                return value
            if value.startswith('"'):
                return value
            return f"&{value}"
        return str(value) 

    def generate_header_file(self, output_path: Path) -> None:
        """生成头文件
        
        Args:
            output_path: 输出文件路径
        """
        definitions = []
        
        # 添加头文件保护
        header_guard = output_path.stem.upper() + '_H'
        definitions.extend([
            f"#ifndef {header_guard}",
            f"#define {header_guard}",
            "",
            "// 标准头文件",
            "#include <stdint.h>",
            "#include <stddef.h>",
            "#include <stdbool.h>",
            "",
            "// 类型定义",
            "typedef uint8_t u8;",
            "typedef uint16_t u16;",
            "typedef uint32_t u32;",
            "typedef uint64_t u64;",
            "",
            "typedef int8_t i8;",
            "typedef int16_t i16;",
            "typedef int32_t i32;",
            "typedef int64_t i64;",
            "",
            "typedef float f32;",
            "typedef double f64;",
            "",
            "// 结构体前向声明"
        ])
        
        # 添加结构体前向声明
        forward_decls = self._generate_forward_declarations()
        if forward_decls:
            definitions.extend(forward_decls)
            definitions.append("")
        
        # 添加结构体定义
        definitions.append("// 结构体定义")
        for struct_name, struct_data in self.struct_info.items():
            definitions.extend(self._generate_struct_definition(struct_name, struct_data))
        
        # 添加外部变量声明
        definitions.extend([
            "// 外部变量声明",
            self._generate_external_declarations(),
            "",
            f"#endif  // {header_guard}"
        ])
        
        # 写入文件
        output_path.write_text('\n'.join(definitions), encoding='utf-8')

    def _generate_forward_declarations(self) -> List[str]:
        """生成结构体前向声明
        
        Returns:
            前向声明列表
        """
        declarations = []
        
        # 收集所有需要前向声明的结构体
        forward_decls = set()
        for struct_name, struct_data in self.struct_info.items():
            for field in struct_data.get('fields', []):
                field_type = field.get('type', '')
                if field_type.startswith('struct '):
                    type_name = field_type.split()[1].rstrip('*')
                    if type_name != struct_name:  # 避免自引用
                        forward_decls.add(type_name)
        
        # 生成前向声明
        for struct_name in sorted(forward_decls):
            declarations.append(f"struct {struct_name};")
        
        return declarations

    def _generate_external_declarations(self) -> str:
        """生成外部变量声明
        
        Returns:
            外部变量声明字符串
        """
        declarations = []
        
        # 添加数组声明
        declarations.extend([
            "// 缓冲区声明",
            "extern uint8_t buffer_data[256];",
            "extern char string_buffer[1024];",
            "",
            "// 测试数据声明",
            "extern struct Point test_points[4];",
            "extern struct Point test_dynamic_points[4][5];",
            "extern struct Vector test_vectors[2];",
            "extern struct Vector test_div2_vectors[2][2];",
            "extern struct Node test_nodes[3];",
            "extern struct BitFields test_bit_fields[2];",
            "",
            "// 结构体变量声明",
            "extern struct ComplexData test_complex_data;",
            "extern struct NestedStruct test_nested;",
            "extern struct RingBuffer test_ring_buffer;",
            "extern struct StringView test_string_view;",
            "extern struct StringBuilder test_string_builder;",
            "extern struct Config test_config;"
        ])
        
        return '\n'.join(declarations)

    def _generate_source_file(self, output_path: Path, header_path: Path) -> None:
        """生成源文件
        
        Args:
            output_path: 输出文件路径
            header_path: 头文件路径
        """
        definitions = []
        
        # 添加头文件包含
        definitions.extend([
            f'#include "{header_path.name}"',
            "#include <string.h>",
            "#include <limits.h>",
            "#include <float.h>",
            ""
        ])
        
        # 添加变量定义
        definitions.extend(self._generate_variable_definitions())
        
        # 写入文件
        output_path.write_text('\n'.join(definitions), encoding='utf-8') 
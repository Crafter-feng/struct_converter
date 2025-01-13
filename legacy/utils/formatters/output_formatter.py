from utils.logger import logger 
import click
import json




class OutputFormatter:
    """输出格式化工具类"""
    
    @staticmethod
    def print_struct_info(generator):
        """打印结构体信息
        
        Args:
            generator: 代码生成器实例
        """
        print("\n=== 结构体定义 ===")
        for struct_name, struct_info in generator.struct_info.items():
            print(f"struct {struct_name} {{")
            
            # 获取字段列表，处理不同的数据结构
            if isinstance(struct_info, dict):
                fields = struct_info.get('fields', [])
            elif isinstance(struct_info, list):
                fields = struct_info
            else:
                fields = []
            
            logger.debug(f"Struct {struct_name} info: {json.dumps(struct_info, indent=2)}")
            logger.debug(f"Fields: {json.dumps(fields, indent=2)}")
            
            if not fields:
                print("    // 无字段")
            else:
                for field in fields:
                    try:
                        field_str = OutputFormatter.format_field_info(field)
                        print(f"    {field_str};")
                    except Exception as e:
                        logger.error(f"Error formatting field {field}: {str(e)}")
                        print(f"    // Error: {str(e)}")
            
            print("};")

    @staticmethod
    def print_text_output(result):
        """打印文本格式的输出到控制台
        
        Args:
            result: 解析结果字典
        """
        # 显示类型定义
        click.echo("=== 类型定义 ===")
        
        # 打印结构体定义
        if result['types']['structs']:
            click.echo("\n结构体定义:")
            for struct_name, fields in result['types']['structs'].items():
                click.echo(f"结构体 {struct_name}:")
                for field in fields:
                    field_str = OutputFormatter.format_field_info(field)
                    click.echo(f"  - {field['name']}: {field_str}")
        
        # 打印类型定义
        if result['types']['typedefs']:
            click.echo("\n类型定义:")
            for typedef_name, typedef_type in result['types']['typedefs'].items():
                click.echo(f"  {typedef_name} -> {typedef_type}")
        
        # 打印枚举定义
        if result['types']['enums']:
            click.echo("\n枚举定义:")
            for enum_name, enum_values in result['types']['enums'].items():
                click.echo(f"枚举 {enum_name}:")
                for name, value in enum_values.items():
                    click.echo(f"  {name} = {value}")
        
        # 打印宏定义
        if result['types']['macros']:
            click.echo("\n宏定义:")
            for macro_name, macro_value in result['types']['macros'].items():
                click.echo(f"  {macro_name} = {macro_value}")
        
        # 显示变量定义
        click.echo("\n=== 变量定义 ===")
        OutputFormatter._print_variables(result['variables'])

    @staticmethod
    def _print_variables(var_info):
        """打印变量信息到控制台
        
        Args:
            var_info: 变量信息字典
        """
        if var_info['variables']:
            click.echo("\n基本变量:")
            for var in var_info['variables']:
                click.echo(f"  - {OutputFormatter.format_var_info(var)}")
        
        if var_info['struct_vars']:
            click.echo("\n结构体变量:")
            for var in var_info['struct_vars']:
                click.echo(f"  - {OutputFormatter.format_var_info(var)}")
        
        if var_info['pointer_vars']:
            click.echo("\n指针变量:")
            for var in var_info['pointer_vars']:
                click.echo(f"  - {OutputFormatter.format_var_info(var)}")
        
        if var_info['array_vars']:
            click.echo("\n数组变量:")
            for var in var_info['array_vars']:
                click.echo(f"  - {OutputFormatter.format_var_info(var)}")

    @staticmethod
    def format_field_info(field):
        """格式化字段信息
        
        Args:
            field: 字段信息字典或字符串
            
        Returns:
            str: 格式化后的字段信息
        """
        if isinstance(field, str):
            return field
            
        if isinstance(field, dict):
            field_str = []
            
            # 添加类型信息
            type_str = field.get('type', 'unknown')
            if field.get('is_pointer'):
                type_str += '*'
            field_str.append(type_str)
            
            # 添加字段名
            name = field.get('name', 'unnamed')
            field_str.append(name)
            
            # 处理数组
            if field.get('array_size'):
                array_dims = field['array_size']
                if isinstance(array_dims, list):
                    for dim in array_dims:
                        field_str[-1] += f"[{dim}]"
                else:
                    field_str[-1] += f"[{array_dims}]"
            
            # 处理位域
            if field.get('bit_field') is not None:
                field_str[-1] += f" : {field['bit_field']}"
            
            # 处理函数指针
            if field.get('is_function_pointer'):
                return f"{type_str} (*{name})({', '.join(field.get('parameters', []))})"
            
            # 处理嵌套结构体
            if field.get('nested_fields'):
                nested_str = "{\n"
                for nested_field in field['nested_fields']:
                    nested_field_str = OutputFormatter.format_field_info(nested_field)
                    nested_str += f"        {nested_field_str};\n"
                nested_str += "    }"
                field_str.append(nested_str)
            
            return ' '.join(field_str)
        
        return str(field)

    @staticmethod
    def format_var_info(var_data):
        """格式化变量信息
        
        Args:
            var_data: 变量信息字典
            
        Returns:
            str: 格式化后的变量信息
        """
        parts = []
        parts.append(var_data['name'])
        parts.append(f"类型: {var_data['type']}")
        
        if var_data.get('is_pointer'):
            parts.append("指针类型")
            if var_data.get('pointer_target'):
                parts.append(f"指向: {var_data['pointer_target']}")
        
        if var_data.get('array_size'):
            dims = 'x'.join(str(x) for x in var_data['array_size'])
            parts.append(f"数组维度: [{dims}]")
        
        if var_data.get('struct_type'):
            parts.append(f"结构体类型: {var_data['struct_type']}")
            
        if var_data.get('value') is not None:
            parts.append(f"值: {var_data['value']}")
            
        if var_data.get('is_const'):
            parts.append("常量")
            
        if var_data.get('is_volatile'):
            parts.append("易变")
            
        if var_data.get('is_static'):
            parts.append("静态")
            
        if var_data.get('is_extern'):
            parts.append("外部")
        
        return ' | '.join(parts)

    @staticmethod
    def format_union_info(union_info):
        """格式化联合体信息
        
        Args:
            union_info: 联合体信息字典
            
        Returns:
            str: 格式化后的联合体信息
        """
        result = [f"union {union_info['name']} {{"]
        
        for field in union_info['fields']:
            field_str = OutputFormatter.format_field_info(field)
            result.append(f"    {field_str};")
            
        result.append("};")
        return '\n'.join(result)

    @staticmethod
    def format_enum_info(enum_name, enum_values):
        """格式化枚举信息
        
        Args:
            enum_name: 枚举名称
            enum_values: 枚举值字典
            
        Returns:
            str: 格式化后的枚举信息
        """
        result = [f"enum {enum_name} {{"]
        
        for name, value in enum_values.items():
            result.append(f"    {name} = {value},")
            
        result.append("};")
        return '\n'.join(result)

    @staticmethod
    def simplify_var_info(var_info):
        """简化变量信息，只保留关键数据
        
        Args:
            var_info: 原始变量信息
        
        Returns:
            dict: 简化后的变量信息
        """
        simplified = {}
        
        # 合并所有变量
        all_vars = (var_info['variables'] + 
                   var_info['struct_vars'] + 
                   var_info['pointer_vars'] + 
                   var_info['array_vars'])
        
        # 提取每个变量的关键信息
        for var in all_vars:
            var_name = var['name']
            var_data = {
                'type': var['original_type']
            }
            
            # 只有数组类型才添加 array_size
            if var.get('array_size'):
                var_data['array_size'] = var['array_size']
            
            # 如果有值，添加 value
            if 'value' in var and var['value'] is not None:
                if (var.get('array_size') and 
                    var['original_type'] == 'char' and 
                    isinstance(var['value'], str)):
                    var_data['value'] = var['value']
                else:
                    var_data['value'] = var['value']
            
            # 如果是指针类型，在类型中添加 *
            if var.get('is_pointer'):
                var_data['type'] = f"{var_data['type']}*"
                if var.get('pointer_level', 1) > 1:
                    var_data['type'] += '*' * (var['pointer_level'] - 1)
            
            simplified[var_name] = var_data
        
        return simplified
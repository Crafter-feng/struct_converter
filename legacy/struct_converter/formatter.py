from typing import List, Union
from utils.logger_config import setup_logger

logger = setup_logger('CodeFormatter')

class CodeFormatter:
    """代码格式化工具"""
    
    def __init__(self, indent_size: int = 4):
        self.indent_size = indent_size
        self.indent_char = ' ' * indent_size
        
    def format_code(self, code: Union[str, List[str]]) -> str:
        """格式化代码"""
        if isinstance(code, list):
            code = '\n'.join(code)
            
        try:
            lines = code.split('\n')
            formatted_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                
                # 处理缩进级别
                if stripped.endswith('{'):
                    formatted_lines.append(self.indent_char * indent_level + stripped)
                    indent_level += 1
                elif stripped.startswith('}'):
                    indent_level = max(0, indent_level - 1)
                    formatted_lines.append(self.indent_char * indent_level + stripped)
                else:
                    formatted_lines.append(self.indent_char * indent_level + stripped)
                    
            return '\n'.join(formatted_lines)
            
        except Exception as e:
            logger.error(f"Failed to format code: {str(e)}")
            return code
            
    def format_struct_definition(self, struct_name: str, fields: List[dict]) -> str:
        """格式化结构体定义"""
        lines = [f"struct {struct_name} {{"]
        
        # 计算字段名称的最大长度，用于对齐
        max_type_len = max(len(field.get('type', '')) for field in fields)
        max_name_len = max(len(field.get('name', '')) for field in fields)
        
        for field in fields:
            field_type = field.get('type', '').ljust(max_type_len)
            field_name = field.get('name', '').ljust(max_name_len)
            
            if field.get('array_size'):
                array_dims = ''.join(f'[{size}]' for size in field['array_size'])
                line = f"{self.indent_char}{field_type} {field_name}{array_dims};"
            else:
                line = f"{self.indent_char}{field_type} {field_name};"
                
            lines.append(line)
            
        lines.append("};")
        return '\n'.join(lines)
        
    def format_function_declaration(self, return_type: str, name: str, 
                                  params: List[tuple], comment: str = '') -> str:
        """格式化函数声明"""
        param_str = ', '.join(f"{type_} {name}" for type_, name in params)
        
        if comment:
            return f"// {comment}\n{return_type} {name}({param_str});"
        return f"{return_type} {name}({param_str});" 
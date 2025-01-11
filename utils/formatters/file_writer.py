from pathlib import Path
from .output_formatter import OutputFormatter

class FileWriter:
    """文件写入工具类"""
    
    @staticmethod
    def write_text_output(result, output_path):
        """将结果写入文本文件"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            FileWriter._write_types(f, result['types'])
            f.write("\n=== 变量定义 ===\n")
            FileWriter._write_variables(f, result['variables'])
    
    @staticmethod
    def _write_types(f, types):
        """写入类型定义"""
        f.write("=== 类型定义 ===\n")
        
        if types['structs']:
            f.write("\n结构体定义:\n")
            for struct_name, fields in types['structs'].items():
                f.write(f"结构体 {struct_name}:\n")
                for field in fields:
                    field_str = OutputFormatter.format_field_info(field)
                    f.write(f"  - {field['name']}: {field_str}\n")
        
        # 写入其他类型定义...
        # (typedefs, enums, macros的处理保持不变)
    
    @staticmethod
    def _write_variables(f, var_info):
        """写入变量信息"""
        for var_type, vars_list in [
            ('基本变量', var_info['variables']),
            ('结构体变量', var_info['struct_vars']),
            ('指针变量', var_info['pointer_vars']),
            ('数组变量', var_info['array_vars'])
        ]:
            if vars_list:
                f.write(f"\n{var_type}:\n")
                for var in vars_list:
                    f.write(f"  - {OutputFormatter.format_var_info(var)}\n") 
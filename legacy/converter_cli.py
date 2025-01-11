import click
import json
from pathlib import Path
from c_parser import CParser
from struct_converter.code_generator import cJsonCodeGenerator
from utils import OutputFormatter, FileWriter
from struct_converter.data_generator import DataGenerator

@click.group()
def cli():
    """C结构体与JSON转换器生成工具"""
    pass

@cli.command()
@click.argument('header_file', type=click.Path(exists=True), required=False)
def parse(header_file):
    """解析C头文件并生成转换器代码。如果不提供头文件，则从缓存读取。"""
    parser = CParser()
    
    if header_file:
        # 从头文件解析
        type_info = parser.parse_declarations(header_file, use_cache=False)
    else:
        # 从缓存读取
        type_info = parser.get_type_info()
        if not type_info:
            click.echo("错误：未提供头文件且无法从缓存读取", err=True)
            return
    
    # 使用类型信息创建代码生成器
    generator = cJsonCodeGenerator(type_info)
    
    # 打印结构体和类型信息
    OutputFormatter.print_struct_info(generator)

@cli.command()
@click.argument('source_file', type=click.Path(exists=True))
@click.option('--header_file', type=click.Path(exists=True), help='头文件路径')
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'json-simple']), default='text',
              help='输出格式：text(默认)、json(完整)或json-simple(精简)')
def analyze(source_file, header_file, output, format):
    """解析C源文件中的变量定义"""
    parser = CParser()
    
    # 如果提供了头文件，先解析头文件
    if header_file:
        parser.parse_declarations(header_file)
    
    # 解析源文件
    output_data = parser.parse_global_variables(source_file)
    
    if not output_data:
        click.echo("错误：解析失败", err=True)
        return
    
    
    if format == 'text':
        # 使用FileWriter输出文本格式
        if output:
            FileWriter.write_text_output(output_data, output)
            click.echo(f"解析结果已保存到: {output}")
        else:
            # 直接打印到控制台
            OutputFormatter.print_text_output(output_data)
    else:
        # JSON格式输出
        if format == 'json-simple':
            # 使用OutputFormatter简化输出
            output_data['variables'] = OutputFormatter.simplify_var_info(output_data['variables'])
        
        json_str = json.dumps(output_data, indent=2, ensure_ascii=False)
        
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
            click.echo(f"解析结果已保存到: {output_path}")
        else:
            # 直接打印JSON
            click.echo(json_str)

@cli.command()
def clear_cache():
    """清除解析缓存"""
    parser = CParser()
    parser.clear_cache()
    click.echo("缓存已清除")

@cli.command()
@click.argument('output_dir', type=click.Path(), default='output')
@click.option('--header_file', type=click.Path(exists=True), required=False)
@click.option('--structs', '-s', multiple=True, help='指定要生成的结构体，不指定则生成所有')
@click.option('--force', '-f', is_flag=True, help='强制重新生成，忽略缓存')
def generate(output_dir, header_file, structs, force):
    """生成结构体转换代码。如果不提供头文件，则从缓存读取。"""
    parser = CParser()
    
    if header_file:
        # 从头文件解析
        type_info = parser.parse_declarations(header_file, use_cache=not force)
    else:
        # 从缓存读取
        type_info = parser.get_type_info()
        if not type_info or not type_info.get('struct_info'):
            click.echo("错误：未提供头文件且无法从缓存读取结构体定义", err=True)
            return
    
    # 使用类型信息创建代码生成器
    generator = cJsonCodeGenerator(type_info)
    
    # 打印结构体信息
    OutputFormatter.print_struct_info(generator)
    
    # 在生成代码之前添加
    click.echo("Debug: Struct info content:")
    click.echo(json.dumps(generator.struct_info, indent=2))
    
    # 获取所有可用的结构体
    available_structs = set(generator.struct_info.keys())
    if not structs:
        target_structs = list(available_structs)
    else:
        # 验证指定的结构体
        invalid_structs = set(structs) - available_structs
        if invalid_structs:
            click.echo(f"错误：找不到以下结构体：{', '.join(invalid_structs)}", err=True)
            return
        target_structs = list(structs)
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # 添加调试信息
        click.echo("Debug: Target structs:")
        for struct in target_structs:
            click.echo(f"  - {struct}")
        click.echo("Debug: Struct info keys:")
        for key in generator.struct_info.keys():
            click.echo(f"  - {key}")
            
        # 生成转换代码
        generator.generate_converter_code(output_dir, target_structs)
        click.echo(f"转换代码已生成到目录：{output_dir}")
        click.echo(f"生成的结构体：{', '.join(target_structs)}")
    except Exception as e:
        click.echo(f"错误：生成代码失败 - {str(e)}", err=True)
        import traceback  # 添加这行来获取完整的错误堆栈
        click.echo(traceback.format_exc(), err=True)
        return

@cli.command()
@click.argument('json_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
@click.option('--header-file', type=click.Path(exists=True), help='头文件路径')
def generate_data(json_file, output, header_file):
    """根据JSON数据生成C语言变量定义"""
    try:
        # 解析JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            
        # 解析头文件（如果提供）
        parser = CParser()
        if header_file:
            type_info = parser.parse_declarations(header_file)
        else:
            type_info = parser.get_type_info()
            
        if not type_info:
            click.echo("错误：无法获取类型信息", err=True)
            return
            
        # 创建数据生成器
        generator = DataGenerator(type_info)
        
        # 生成变量定义
        output_path = Path(output) if output else Path('output/data_definitions.c')
        generator.generate_variable_definitions(json_data, output_path)
        
        click.echo(f"变量定义已生成到：{output_path}")
        
    except Exception as e:
        click.echo(f"错误：{str(e)}", err=True)
        return

if __name__ == '__main__':
    cli() 
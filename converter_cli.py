import click
import json
from pathlib import Path
from c_parser import CParser
from code_generator import cJsonCodeGenerator
from utils import OutputFormatter, FileWriter

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
        type_info = parser.parse_header(header_file, use_cache=False)
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
        parser.parse_header(header_file)
    
    # 解析源文件
    declarations = parser.parse_declarations(source_file)
    
    if not declarations:
        click.echo("错误：解析失败", err=True)
        return
    
    # 准备输出结果
    output_data = {
        'types': {
            'structs': declarations['struct_info'],
            'typedefs': declarations['typedef_types'],
            'enums': declarations['enum_types'],
            'macros': declarations['macro_definitions']
        },
        'variables': declarations['variables']
    }
    
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
@click.argument('output_dir', type=click.Path(), default='.')
@click.option('--header_file', type=click.Path(exists=True), required=False)
@click.option('--structs', '-s', multiple=True, help='指定要生成的结构体，不指定则生成所有')
@click.option('--force', '-f', is_flag=True, help='强制重新生成，忽略缓存')
def generate(output_dir, header_file, structs, force):
    """生成结构体转换代码。如果不提供头文件，则从缓存读取。"""
    parser = CParser()
    
    if header_file:
        # 从头文件解析
        type_info = parser.parse_header(header_file, use_cache=not force)
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
    
    # 获取所有可用的结构体
    available_structs = set(generator.struct_info.keys())
    if not available_structs:
        click.echo("错误：未找到任何结构体定义", err=True)
        return
    
    # 验证指定的结构体
    if structs:
        invalid_structs = set(structs) - available_structs
        if invalid_structs:
            click.echo(f"错误：找不到以下结构体：{', '.join(invalid_structs)}", err=True)
            return
        target_structs = list(structs)
    else:
        target_structs = list(available_structs)
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # 生成转换代码
        generator.generate_converter_code(output_dir, target_structs)
        click.echo(f"转换代码已生成到目录：{output_dir}")
        click.echo(f"生成的结构体：{', '.join(target_structs)}")
    except Exception as e:
        click.echo(f"错误：生成代码失败 - {str(e)}", err=True)
        return

if __name__ == '__main__':
    cli() 
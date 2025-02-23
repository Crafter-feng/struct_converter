import click
from pathlib import Path
from typing import List, Optional, Dict, Any
from loguru import logger
from config import GeneratorConfig
from config import EncryptionConfig
from struct_converter.generators import CGenerator
from struct_converter.generators import PythonGenerator
from c_parser import TypeManager,CTypeParser,CDataParser
from utils.logger import logger 
import json

@click.group()
@click.option('--log-file', type=click.Path(), help='日志文件路径')
@click.option('--log-level', 
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO',
              help='日志级别')
@click.version_option(version='0.1.0')
def cli(log_file: Optional[str], log_level: str):
    """C结构体转换工具
    
    用于将C语言结构体转换为其他语言的数据结构。
    支持字段加密、类型转换和代码生成。
    """
    # 设置日志配置
    if log_file:
        logger.add(
            log_file,
            log_level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>",
            rotation="1 day",
            retention="7 days",
            compression="zip"
            )
    
    # 初始化全局配置
    if not hasattr(cli, 'config'):
        cli.config = {
            'generator': GeneratorConfig(),
            'encryption': EncryptionConfig(),
            'type_manager': TypeManager(),
            'parser': None
        }

@cli.command()
@click.argument('input_files', nargs=-1, type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(), help='输出目录')
@click.option('--lang', '-l', 
              type=click.Choice(['c', 'python']), 
              default='c', 
              help='目标语言')
@click.option('--config', '-c', 
              type=click.Path(exists=True), 
              help='配置文件路径')
@click.option('--encrypt/--no-encrypt', 
              default=False, 
              help='启用字段加密')
@click.option('--encrypt-salt', 
              help='字段加密盐值')
@click.option('--encrypt-config', 
              type=click.Path(exists=True),
              help='加密配置文件路径')
def convert(input_files: List[str], 
           output_dir: Optional[str], 
           lang: str,
           config: Optional[str],
           encrypt: bool,
           encrypt_salt: Optional[str],
           encrypt_config: Optional[str]):
    """转换C头文件到目标语言"""
    try:
        # 加载配置
        if config:
            cli.config['generator'] = GeneratorConfig.load(config)
            
        # 加载加密配置
        if encrypt_config:
            cli.config['encryption'] = EncryptionConfig.load(encrypt_config)
            cli.config['generator'].encryption = cli.config['encryption']
            
        # 更新配置
        if output_dir:
            cli.config['generator'].output_dir = output_dir
        if encrypt:
            cli.config['generator'].enable_field_encryption = True
        if encrypt_salt:
            cli.config['generator'].field_encryption_salt = encrypt_salt
            
        # 创建生成器
        if lang == 'c':
            generator = CGenerator(cli.config['generator'])
        else:
            generator = PythonGenerator(cli.config['generator'])
            
        # 创建解析器
        if not cli.config['parser']:
            cli.config['parser'] = CTypeParser(cli.config['type_manager'])
            
        # 处理每个输入文件
        for input_file in input_files:
            logger.info(f"Processing {input_file}...")
            
            # 解析C代码
            parse_result = cli.config['parser'].parse_declarations(input_file)
            
            # 生成代码
            module_name = Path(input_file).stem
            generated = generator.generate({
                'module_name': module_name,
                **parse_result
            })
            
            # 保存生成的代码
            output_path = Path(cli.config['generator'].output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            for ext, content in generated.items():
                output_file = output_path / f"{module_name}.{ext}"
                with open(output_file, 'w') as f:
                    f.write(content)
                logger.info(f"Generated {output_file}")
                
    except Exception as e:
        logger.error(f"Failed to convert files: {e}")
        raise click.ClickException(str(e))

@cli.command()
@click.argument('config_file', type=click.Path())
@click.option('--force/--no-force', default=False, help='强制覆盖已存在的配置文件')
def init_config(config_file: str, force: bool):
    """初始化配置文件
    
    创建一个包含默认配置的配置文件。
    
    示例：
    \b
    c-converter init-config config.json
    """
    try:
        config_path = Path(config_file)
        if config_path.exists() and not force:
            raise click.ClickException(
                f"Config file {config_file} already exists. Use --force to overwrite."
            )
            
        config = GeneratorConfig()
        config.save(config_file)
        logger.info(f"Created config file: {config_file}")
        
    except Exception as e:
        logger.error(f"Failed to create config file: {e}")
        raise click.ClickException(str(e))

@cli.command()
@click.argument('config_file', type=click.Path())
@click.option('--struct', '-s', multiple=True, help='要加密的结构体字段 (struct:field)')
@click.option('--exclude', '-e', multiple=True, help='要排除的结构体字段 (struct:field)')
@click.option('--encrypt-all/--no-encrypt-all', default=False, help='加密所有字段')
@click.option('--salt', help='加密盐值')
@click.option('--force/--no-force', default=False, help='强制覆盖已存在的配置文件')
def init_encrypt_config(config_file: str,
                       struct: List[str],
                       exclude: List[str],
                       encrypt_all: bool,
                       salt: Optional[str],
                       force: bool):
    """初始化加密配置文件
    
    创建一个包含字段加密配置的配置文件。
    可以指定需要加密的字段和排除的字段。
    
    示例：
    \b
    # 加密特定字段
    c-converter init-encrypt-config encrypt.json -s User:password -s User:token
    
    \b
    # 加密所有字段，但排除某些字段
    c-converter init-encrypt-config encrypt.json --encrypt-all -e User:name
    """
    try:
        config_path = Path(config_file)
        if config_path.exists() and not force:
            raise click.ClickException(
                f"Config file {config_file} already exists. Use --force to overwrite."
            )
            
        # 解析结构体字段
        encrypted_fields = {}
        for s in struct:
            struct_name, field_name = s.split(':')
            if struct_name not in encrypted_fields:
                encrypted_fields[struct_name] = []
            encrypted_fields[struct_name].append(field_name)
            
        # 解析排除字段
        excluded_fields = {}
        for e in exclude:
            struct_name, field_name = e.split(':')
            if struct_name not in excluded_fields:
                excluded_fields[struct_name] = []
            excluded_fields[struct_name].append(field_name)
            
        config = EncryptionConfig(
            enable=True,
            salt=salt or "struct_converter",
            encrypt_all=encrypt_all,
            encrypted_fields=encrypted_fields,
            excluded_fields=excluded_fields
        )
        
        config.save(config_path)
        logger.info(f"Created encryption config file: {config_file}")
        
    except Exception as e:
        logger.error(f"Failed to create encryption config: {e}")
        raise click.ClickException(str(e))

@cli.command()
@click.argument('header_file', type=click.Path(exists=True), required=False)
def parse(header_file):
    """解析C头文件并显示类型信息。如果不提供头文件，则从缓存读取。"""
    try:
        parser = CTypeParser()
        
        if header_file:
            # 从头文件解析
            type_info = parser.parse_declarations(Path(header_file))
            with open(Path(header_file).stem + ".json", "w") as f:
                json.dump(type_info, f, indent=4)
        else:
            # 从缓存读取
            type_info = parser.get_type_info()
            if not type_info:
                raise click.ClickException("未提供头文件且无法从缓存读取")
                
    except Exception as e:
        logger.error(f"解析失败: {e}")
        raise click.ClickException(str(e))

@cli.command()
@click.argument('source_file', type=click.Path(exists=True))
@click.option('--header_file', type=click.Path(exists=True), help='头文件路径')
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
@click.option('--format', '-f', 
              type=click.Choice(['text', 'json', 'json-simple']), 
              default='text',
              help='输出格式：text(默认)、json(完整)或json-simple(精简)')
def analyze(source_file, header_file, output, format):
    """解析C源文件中的变量定义"""
    try:
        parser = CTypeParser()
        
        # 如果提供了头文件，先解析头文件
        if header_file:
            parser.parse_declarations(header_file)
        
        # 解析源文件
        output_data = parser.parse_declarations(source_file)
        
        if not output_data:
            raise click.ClickException("解析失败")
        
        # 格式化输出
        if format == 'text':
            formatted = _format_text_output(output_data)
        else:
            if format == 'json-simple':
                output_data = _simplify_output(output_data)
            formatted = json.dumps(output_data, indent=2, ensure_ascii=False)
            
        # 输出结果
        if output:
            Path(output).write_text(formatted, encoding='utf-8')
            click.echo(f"解析结果已保存到: {output}")
        else:
            click.echo(formatted)
            
    except Exception as e:
        logger.error(f"解析失败: {e}")
        raise click.ClickException(str(e))

def _format_text_output(data: Dict[str, Any]) -> str:
    """格式化文本输出"""
    lines = []
    
    for category, items in data.items():
        lines.append(f"\n=== {category} ===")
        for name, info in items.items():
            lines.append(f"\n{name}:")
            lines.extend(f"  {k}: {v}" for k, v in info.items())
            
    return '\n'.join(lines)

def _simplify_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """简化输出数据"""
    simplified = {}
    
    for category, items in data.items():
        simplified[category] = {}
        for name, info in items.items():
            if isinstance(info, dict):
                simplified[category][name] = {
                    k: v for k, v in info.items()
                    if k in {'type', 'size', 'value', 'fields'}
                }
            else:
                simplified[category][name] = info
                
    return simplified

if __name__ == '__main__':
    cli() 
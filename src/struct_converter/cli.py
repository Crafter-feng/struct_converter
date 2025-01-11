import click
from pathlib import Path
from typing import List, Optional
from loguru import logger
from .core.config import GeneratorConfig
from .core.encryption_config import EncryptionConfig
from .generators.c_generator import CGenerator
from .generators.python_generator import PythonGenerator
from c_parser.tree_sitter_parser import CTreeSitterParser
from utils.logger import setup_logger

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
    setup_logger(log_file, log_level)

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
    """转换C头文件到目标语言
    
    支持批量转换多个头文件，可以指定输出目录和目标语言。
    可以通过配置文件自定义转换行为，支持字段加密功能。
    
    示例：
    \b
    # 转换单个文件
    struct-converter convert input.h -o output
    
    \b
    # 转换为Python
    struct-converter convert input.h -o output -l python
    
    \b
    # 启用字段加密
    struct-converter convert input.h -o output --encrypt
    """
    try:
        # 加载配置
        if config:
            generator_config = GeneratorConfig.load(config)
        else:
            generator_config = GeneratorConfig()
            
        # 加载加密配置
        if encrypt_config:
            encryption_config = EncryptionConfig.load(encrypt_config)
            generator_config.encryption = encryption_config
            
        # 更新配置
        if output_dir:
            generator_config.output_dir = output_dir
        if encrypt:
            generator_config.enable_field_encryption = True
        if encrypt_salt:
            generator_config.field_encryption_salt = encrypt_salt
            
        # 创建生成器
        if lang == 'c':
            generator = CGenerator(generator_config)
        else:
            generator = PythonGenerator(generator_config)
            
        # 创建解析器
        parser = CTreeSitterParser()
        
        # 处理每个输入文件
        for input_file in input_files:
            logger.info(f"Processing {input_file}...")
            
            # 解析C代码
            parse_result = parser.parse_file(str(input_file))
            
            # 生成代码
            module_name = Path(input_file).stem
            generated = generator.generate({
                'module_name': module_name,
                **parse_result
            })
            
            # 保存生成的代码
            output_path = Path(generator_config.output_dir)
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
    struct-converter init-config config.json
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
    struct-converter init-encrypt-config encrypt.json -s User:password -s User:token
    
    \b
    # 加密所有字段，但排除某些字段
    struct-converter init-encrypt-config encrypt.json --encrypt-all -e User:name
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

if __name__ == '__main__':
    cli() 
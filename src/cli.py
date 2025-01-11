import click
from loguru import logger
from pathlib import Path
from struct_converter.core.config import GeneratorConfig
from struct_converter.generators.c_generator import CGenerator
from struct_converter.generators.python_generator import PythonGenerator
from c_parser.tree_sitter_parser import CTreeSitterParser
from utils.logger import setup_logger
from utils.profiler import Profiler
from struct_converter.core.encryption_config import EncryptionConfig

@click.group()
@click.option('--log-file', type=click.Path(), help='日志文件路径')
@click.option('--log-level', 
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO',
              help='日志级别')
def cli(log_file: str, log_level: str):
    """结构体转换工具"""
    setup_logger(log_file, log_level)

@cli.command()
@click.argument('input_files', nargs=-1, type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(), help='输出目录')
@click.option('--lang', '-l', type=click.Choice(['c', 'python']), default='c', help='目标语言')
@click.option('--config', '-c', type=click.Path(exists=True), help='配置文件路径')
@click.option('--profile/--no-profile', default=False, help='启用性能分析')
@click.option('--encrypt/--no-encrypt', default=False, help='启用字段加密')
@click.option('--encrypt-salt', default=None, help='字段加密盐值')
@click.pass_context
def convert(ctx, input_files, output_dir, lang, config, profile, encrypt, encrypt_salt):
    """转换C头文件"""
    try:
        # 加载配置
        if config:
            generator_config = GeneratorConfig.load(config)
        else:
            generator_config = GeneratorConfig()
            
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
        
        with Profiler() as profiler:
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
                    
        if profile:
            logger.info("\nProfiling results:")
            logger.info(profiler.get_stats())
            
    except Exception as e:
        logger.error(f"Failed to convert files: {e}")
        if ctx.obj['debug']:
            logger.exception(e)
        raise click.ClickException(str(e))

@cli.command()
@click.argument('config_file', type=click.Path())
@click.option('--force/--no-force', default=False, help='强制覆盖已存在的配置文件')
@click.pass_context
def init_config(ctx, config_file, force):
    """初始化配置文件"""
    try:
        config_path = Path(config_file)
        if config_path.exists() and not force:
            raise click.ClickException(f"Config file {config_file} already exists. Use --force to overwrite.")
            
        config = GeneratorConfig()
        config.save(config_file)
        logger.info(f"Created config file: {config_file}")
        
    except Exception as e:
        logger.error(f"Failed to create config file: {e}")
        if ctx.obj['debug']:
            logger.exception(e)
        raise click.ClickException(str(e))

@cli.command()
@click.argument('config_file', type=click.Path())
@click.option('--struct', '-s', multiple=True, help='要加密的结构体字段 (struct:field)')
@click.option('--exclude', '-e', multiple=True, help='要排除的结构体字段 (struct:field)')
@click.option('--encrypt-all/--no-encrypt-all', default=False, help='加密所有字段')
@click.option('--salt', help='加密盐值')
@click.option('--force/--no-force', default=False, help='强制覆盖已存在的配置文件')
@click.pass_context
def init_encrypt_config(ctx, config_file, struct, exclude, encrypt_all, salt, force):
    """初始化加密配置文件"""
    try:
        config_path = Path(config_file)
        if config_path.exists() and not force:
            raise click.ClickException(f"Config file {config_file} already exists. Use --force to overwrite.")
            
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
        if ctx.obj['debug']:
            logger.exception(e)
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli(obj={}) 
import pytest
from click.testing import CliRunner
from pathlib import Path
import tempfile
from cli import cli

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def sample_c_file():
    content = """
    typedef struct {
        int x;
        int y;
    } Point;
    
    typedef enum {
        RED = 0,
        GREEN = 1,
        BLUE = 2
    } Color;
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
        f.write(content)
    yield Path(f.name)
    Path(f.name).unlink()

def test_cli_help(runner):
    """测试帮助信息"""
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'C结构体转换工具' in result.output

def test_cli_convert_basic(runner, sample_c_file):
    """测试基本转换功能"""
    with tempfile.TemporaryDirectory() as temp_dir:
        result = runner.invoke(cli, [
            'convert',
            str(sample_c_file),
            '--output-dir', temp_dir,
            '--lang', 'c'
        ])
        
        assert result.exit_code == 0
        
        # 检查生成的文件
        output_dir = Path(temp_dir)
        assert (output_dir / f"{sample_c_file.stem}.h").exists()
        assert (output_dir / f"{sample_c_file.stem}.c").exists()

def test_cli_convert_multiple_files(runner):
    """测试多文件转换"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件
        files = []
        for i in range(3):
            content = f"""
            typedef struct {{
                int value{i};
            }} Struct{i};
            """
            file_path = Path(temp_dir) / f"test{i}.h"
            file_path.write_text(content)
            files.append(str(file_path))
        
        # 执行转换
        result = runner.invoke(cli, [
            'convert',
            *files,
            '--output-dir', str(Path(temp_dir) / 'output'),
            '--lang', 'c'
        ])
        
        assert result.exit_code == 0
        
        # 检查生成的文件
        output_dir = Path(temp_dir) / 'output'
        assert (output_dir / "test0.h").exists()
        assert (output_dir / "test0.c").exists()

def test_cli_convert_with_config(runner, sample_c_file):
    """测试使用配置文件"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建配置文件
        config_file = Path(temp_dir) / 'config.json'
        result = runner.invoke(cli, [
            'init-config',
            str(config_file)
        ])
        assert result.exit_code == 0
        
        # 使用配置文件进行转换
        result = runner.invoke(cli, [
            'convert',
            str(sample_c_file),
            '--config', str(config_file),
            '--output-dir', temp_dir,
            '--lang', 'c'
        ])
        
        assert result.exit_code == 0

def test_cli_convert_with_profiling(runner, sample_c_file):
    """测试性能分析功能"""
    with tempfile.TemporaryDirectory() as temp_dir:
        result = runner.invoke(cli, [
            'convert',
            str(sample_c_file),
            '--output-dir', temp_dir,
            '--lang', 'c',
            '--profile'
        ])
        
        assert result.exit_code == 0
        assert 'Profiling results' in result.output

def test_cli_convert_invalid_input(runner):
    """测试无效输入"""
    result = runner.invoke(cli, [
        'convert',
        'nonexistent.h',
        '--lang', 'c'
    ])
    
    assert result.exit_code != 0
    assert 'Error' in result.output

def test_cli_init_config_overwrite(runner):
    """测试配置文件覆盖"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / 'config.json'
        
        # 第一次创建
        result = runner.invoke(cli, [
            'init-config',
            str(config_file)
        ])
        assert result.exit_code == 0
        
        # 尝试覆盖（不使用 --force）
        result = runner.invoke(cli, [
            'init-config',
            str(config_file)
        ])
        assert result.exit_code != 0
        
        # 使用 --force 覆盖
        result = runner.invoke(cli, [
            'init-config',
            str(config_file),
            '--force'
        ])
        assert result.exit_code == 0

def test_cli_debug_mode(runner, sample_c_file):
    """测试调试模式"""
    with tempfile.TemporaryDirectory() as temp_dir:
        result = runner.invoke(cli, [
            '--debug',
            'convert',
            str(sample_c_file),
            '--output-dir', temp_dir,
            '--lang', 'c'
        ])
        
        assert result.exit_code == 0
        # 调试模式应该输出更多信息
        assert 'DEBUG' in result.output 
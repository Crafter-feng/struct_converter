import pytest
from pathlib import Path
import tempfile
from click.testing import CliRunner
from config import GeneratorConfig
from cli import cli

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def sample_header():
    return """
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

def test_cli_help(runner):
    """测试帮助信息"""
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'C结构体转换工具' in result.output

def test_cli_convert(runner, sample_header):
    """测试基本转换功能"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件
        input_file = Path(temp_dir) / "test.h"
        input_file.write_text(sample_header)
        
        # 执行转换
        result = runner.invoke(cli, [
            'convert',
            str(input_file),
            '--output-dir', temp_dir,
            '--lang', 'c'
        ])
        
        assert result.exit_code == 0
        assert (Path(temp_dir) / "test.h").exists()
        assert (Path(temp_dir) / "test.c").exists()

def test_cli_convert_with_encryption(runner, sample_header):
    """测试带加密的转换"""
    with tempfile.TemporaryDirectory() as temp_dir:
        input_file = Path(temp_dir) / "test.h"
        input_file.write_text(sample_header)
        
        result = runner.invoke(cli, [
            'convert',
            str(input_file),
            '--output-dir', temp_dir,
            '--encrypt',
            '--encrypt-salt', 'test'
        ])
        
        assert result.exit_code == 0
        
        # 检查生成的代码中是否包含加密的字段名
        output_h = Path(temp_dir) / "test.h"
        assert output_h.exists()
        content = output_h.read_text()
        assert "Q_" in content

def test_cli_init_config(runner):
    """测试配置文件初始化"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.yaml"
        
        # 测试正常创建
        result = runner.invoke(cli, [
            'init-config',
            str(config_file)
        ])
        assert result.exit_code == 0
        assert config_file.exists()
        
        # 测试强制覆盖
        result = runner.invoke(cli, [
            'init-config',
            str(config_file),
            '--force'
        ])
        assert result.exit_code == 0 
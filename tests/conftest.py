import pytest
import os

@pytest.fixture
def test_files_dir():
    """返回测试文件目录路径"""
    return os.path.join(os.path.dirname(__file__), 'fixtures')

@pytest.fixture
def c_files_dir(test_files_dir):
    """返回C源文件目录路径"""
    return os.path.join(test_files_dir, 'c_files')

@pytest.fixture
def expected_files_dir(test_files_dir):
    """返回期望输出文件目录路径"""
    return os.path.join(test_files_dir, 'expected') 
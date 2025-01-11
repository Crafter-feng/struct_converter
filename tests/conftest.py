import os
import sys
from pathlib import Path

# 添加源代码目录到 Python 路径
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

@pytest.fixture
def test_data_dir():
    return Path(__file__).parent / "test_data"

@pytest.fixture
def parser():
    from c_parser.data_parser import CDataParser
    return CDataParser()

@pytest.fixture
def generator():
    from struct_converter.generator.struct import StructGenerator
    return StructGenerator({}) 
from dataclasses import dataclass
from typing import Optional

@dataclass
class GeneratorConfig:
    """生成器配置"""
    cache_ttl: int = 3600  # 缓存过期时间(秒)
    indent_size: int = 4   # 缩进大小
    add_comments: bool = True  # 是否添加注释
    generate_tests: bool = True  # 是否生成测试
    max_line_length: int = 80  # 最大行长度
    
    # 输出选项
    output_dir: Optional[str] = None  # 输出目录
    header_file: str = "struct_converter.h"  # 头文件名
    source_file: str = "struct_converter.c"  # 源文件名
    
    # 格式化选项
    pretty_print: bool = True  # 是否美化输出
    sort_keys: bool = False  # 是否对键排序
    escape_unicode: bool = True  # 是否转义Unicode 
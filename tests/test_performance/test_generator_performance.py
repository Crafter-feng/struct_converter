import pytest
import time
from struct_converter.core.config import GeneratorConfig
from struct_converter.generators.c_generator import CGenerator
from struct_converter.generators.python_generator import PythonGenerator
from c_parser.tree_sitter_parser import CTreeSitterParser

def generate_large_header(num_structs: int, fields_per_struct: int) -> str:
    """生成大型测试头文件"""
    lines = []
    for i in range(num_structs):
        lines.append(f"typedef struct {{")
        for j in range(fields_per_struct):
            lines.append(f"    int field_{j};")
        lines.append(f"}} Struct{i};")
    return "\n".join(lines)

def test_parser_performance():
    """测试解析器性能"""
    parser = CTreeSitterParser()
    
    # 测试不同规模的解析
    sizes = [(10, 10), (50, 20), (100, 50)]  # (结构体数量, 每个结构体的字段数)
    times = {}
    
    for num_structs, fields_per_struct in sizes:
        header = generate_large_header(num_structs, fields_per_struct)
        
        start_time = time.time()
        parse_result = parser.parse_string(header)
        end_time = time.time()
        
        times[(num_structs, fields_per_struct)] = end_time - start_time
        
        # 验证解析结果
        assert len(parse_result["structs"]) == num_structs
        for struct in parse_result["structs"].values():
            assert len(struct["fields"]) == fields_per_struct

def test_generator_performance():
    """测试生成器性能"""
    parser = CTreeSitterParser()
    config = GeneratorConfig()
    
    # 测试不同规模的代码生成
    sizes = [(10, 10), (50, 20), (100, 50)]
    times = {"c": {}, "python": {}}
    
    for num_structs, fields_per_struct in sizes:
        header = generate_large_header(num_structs, fields_per_struct)
        parse_result = parser.parse_string(header)
        
        # 测试C生成器
        c_gen = CGenerator(config)
        start_time = time.time()
        c_result = c_gen.generate({
            'module_name': 'test',
            **parse_result
        })
        end_time = time.time()
        times["c"][(num_structs, fields_per_struct)] = end_time - start_time
        
        # 测试Python生成器
        py_gen = PythonGenerator(config)
        start_time = time.time()
        py_result = py_gen.generate({
            'module_name': 'test',
            **parse_result
        })
        end_time = time.time()
        times["python"][(num_structs, fields_per_struct)] = end_time - start_time
        
        # 验证生成的代码大小合理
        assert len(c_result["h"]) > 0
        assert len(c_result["c"]) > 0
        assert len(py_result["py"]) > 0 

def test_format_performance():
    """测试代码格式化性能"""
    generator = CGenerator(GeneratorConfig())
    
    code_sizes = [1000, 10000, 100000]
    times = {}
    
    for size in code_sizes:
        code = 'void test() {\n' + '    int x = 0;\n' * size + '}\n'
        
        start_time = time.time()
        formatted = generator._format_code(code, 'c')
        end_time = time.time()
        
        times[size] = end_time - start_time
        
        # 验证格式化结果
        assert formatted.count('\n') >= size  # 至少有原来的行数
        assert formatted.count('    int') == size  # 保留了所有变量声明
        
    # 检查格式化时间随代码大小的增长趋势
    for i in range(len(code_sizes) - 1):
        ratio = times[code_sizes[i+1]] / times[code_sizes[i]]
        size_ratio = code_sizes[i+1] / code_sizes[i]
        # 期望时间增长不超过代码大小增长的1.5倍
        assert ratio < size_ratio * 1.5

def test_memory_usage_during_generation():
    """测试代码生成过程中的内存使用"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # 生成大量代码
    header = generate_large_header(100, 50)  # 100个结构体，每个50个字段
    parser = CTreeSitterParser()
    parse_result = parser.parse_string(header)
    
    generator = CGenerator(GeneratorConfig())
    generated = generator.generate({
        'module_name': 'test',
        **parse_result
    })
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # 检查内存增长是否合理
    # 假设每个字段平均需要100字节，每个结构体需要200字节
    expected_memory = 100 * 50 * 100 + 100 * 200
    assert memory_increase < expected_memory * 2  # 允许2倍的开销 
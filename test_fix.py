#!/usr/bin/env python3
"""
测试数组解析修复
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.c_parser.data_parser import CDataParser
from src.c_parser.core.type_manager import TypeManager
from src.c_parser.type_parser import CTypeParser
import json

def test_array_parsing():
    """测试数组解析修复"""
    print("=== 测试数组解析修复 ===")
    
    # 初始化类型管理器
    type_manager = TypeManager()
    
    # 先解析头文件以加载类型定义
    print("Step 1: 解析头文件加载类型定义...")
    type_parser = CTypeParser(type_manager)
    header_result = type_parser.parse_declarations("tests/fixtures/c_files/test_structs.h")
    
    # 检查类型管理器中的类型
    print(f"\n类型管理器信息:")
    # 检查关键类型是否存在
    key_types = ['Point', 'Vector', 'Node', 'ComplexData', 'RingBuffer', 'StringView', 'StringBuilder', 'Config']
    for type_name in key_types:
        type_kind = type_manager._get_type_kind(type_name)
        is_struct = type_manager.is_struct_type(type_name)
        print(f"  - {type_name}: kind={type_kind}, is_struct={is_struct}")
    
    # 检查类型管理器中的类型列表
    print(f"\n类型管理器中的类型:")
    all_types = type_manager._current_types + type_manager._global_types
    for type_info in all_types:
        if isinstance(type_info, dict) and 'name' in type_info:
            print(f"  - {type_info['name']}: kind={type_info.get('kind')}, fields={len(type_info.get('fields', []))}")
    
    print(f"头文件解析完成:")
    print(f"  - 结构体: {len(header_result.get('structs', []))}")
    print(f"  - 联合体: {len(header_result.get('unions', []))}")
    print(f"  - 枚举: {len(header_result.get('enums', []))}")
    print(f"  - 类型定义: {len(header_result.get('typedefs', []))}")
    
    # 检查类型管理器中的类型
    print(f"\n类型管理器信息:")
    # 检查关键类型是否存在
    key_types = ['Point', 'Vector', 'Node', 'ComplexData', 'RingBuffer', 'StringView', 'StringBuilder', 'Config']
    for type_name in key_types:
        type_kind = type_manager._get_type_kind(type_name)
        is_struct = type_manager.is_struct_type(type_name)
        print(f"  - {type_name}: kind={type_kind}, is_struct={is_struct}")
    
    # 再解析数据文件
    print("\nStep 2: 解析数据文件...")
    parser = CDataParser(type_manager)
    result = parser.parse_file("tests/fixtures/c_files/test_data.c")
    
    # 保存结果
    with open("output/test_fix_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    
    print("解析完成，结果已保存到 output/test_fix_result.json")
    
    # 检查关键数组的解析结果
    variables = result.get('variables', {})
    array_vars = variables.get('array_vars', [])
    struct_vars = variables.get('struct_vars', [])
    
    print("\n=== 数组解析结果检查 ===")
    
    for var in array_vars:
        name = var.get('name', '')
        parsed_value = var.get('parsed_value', None)
        
        print(f"\n变量: {name}")
        print(f"类型: {var.get('type', '')}")
        print(f"数组大小: {var.get('array_size', [])}")
        print(f"是否为结构体: {var.get('is_struct', False)}")
        
        if parsed_value is not None:
            if isinstance(parsed_value, list):
                print(f"解析结果: {len(parsed_value)} 个元素")
                if len(parsed_value) > 0:
                    print(f"第一个元素: {parsed_value[0]}")
                    if isinstance(parsed_value[0], list):
                        print(f"第一个元素是数组，包含 {len(parsed_value[0])} 个子元素")
                    elif isinstance(parsed_value[0], dict):
                        print(f"第一个元素是结构体，包含字段: {list(parsed_value[0].keys())}")
            else:
                print(f"解析结果: {parsed_value}")
        else:
            print("解析结果: None")
    
    print("\n=== 结构体变量解析结果检查 ===")
    
    for var in struct_vars:
        name = var.get('name', '')
        parsed_value = var.get('parsed_value', None)
        
        print(f"\n变量: {name}")
        print(f"类型: {var.get('type', '')}")
        
        if parsed_value is not None:
            if isinstance(parsed_value, dict):
                print(f"解析结果: {len(parsed_value)} 个字段")
                print(f"字段: {list(parsed_value.keys())}")
            else:
                print(f"解析结果: {parsed_value}")
        else:
            print("解析结果: None")

if __name__ == "__main__":
    test_array_parsing()

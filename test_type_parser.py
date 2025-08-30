#!/usr/bin/env python3
"""
测试类型解析器
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.c_parser.core.type_manager import TypeManager
from src.c_parser.type_parser import CTypeParser

def test_type_parser():
    """测试类型解析器"""
    print("=== 测试类型解析器 ===")
    
    # 初始化类型管理器
    type_manager = TypeManager()
    
    # 创建类型解析器
    type_parser = CTypeParser(type_manager)
    
    # 测试解析头文件
    print("Step 1: 解析头文件...")
    result = type_parser.parse_declarations("tests/fixtures/c_files/test_structs.h")
    
    if result:
        print("解析成功！")
        print(f"类型数量: {len(result.get('types', []))}")
        
        # 检查关键类型
        types = result.get('types', [])
        for type_info in types:
            if isinstance(type_info, dict) and 'name' in type_info:
                name = type_info['name']
                kind = type_info.get('kind')
                print(f"  - {name}: kind={kind}")
                
                if kind == 'struct':
                    fields = type_info.get('fields', [])
                    print(f"    字段数量: {len(fields)}")
                    for field in fields:
                        print(f"      {field.get('name')}: {field.get('type')}")
    else:
        print("解析失败！")
    
    # 检查类型管理器
    print("\nStep 2: 检查类型管理器...")
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

if __name__ == "__main__":
    test_type_parser()

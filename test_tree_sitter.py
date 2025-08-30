#!/usr/bin/env python3
"""测试tree-sitter解析器"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from c_parser.core.tree_sitter_utils import TreeSitterUtils

def test_tree_sitter():
    """测试tree-sitter解析器"""
    ts_util = TreeSitterUtils.get_instance()
    
    # 读取头文件内容
    with open("tests/fixtures/c_files/test_structs.h", 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"File content length: {len(content)}")
    print(f"First 200 characters: {content[:200]}")
    
    # 解析文件
    tree = ts_util.parse(content)
    
    if tree:
        print(f"Tree node type: {tree.type}")
        print(f"Tree node text: {tree.text.decode('utf8')[:100]}...")
        
        # 遍历根节点的子节点
        print(f"\nRoot node children:")
        for i, child in enumerate(tree.children):
            print(f"  {i}: {child.type} - {child.text.decode('utf8')[:50]}...")
            
            # 如果是preproc_ifdef，显示其子节点
            if child.type == 'preproc_ifdef':
                print(f"    Preproc ifdef children:")
                for j, grandchild in enumerate(child.children):
                    print(f"      {j}: {grandchild.type} - {grandchild.text.decode('utf8')[:50]}...")
                    
                    # 如果是declaration，显示更多信息
                    if grandchild.type == 'declaration':
                        print(f"        Declaration children:")
                        for k, greatgrandchild in enumerate(grandchild.children):
                            print(f"          {k}: {greatgrandchild.type} - {greatgrandchild.text.decode('utf8')[:30]}...")
                    
                    # 如果是comment，显示内容
                    elif grandchild.type == 'comment':
                        print(f"        Comment: {grandchild.text.decode('utf8')}")
    else:
        print("Failed to parse file")

if __name__ == "__main__":
    test_tree_sitter()

import pytest
import time
from struct_converter.core.field_encryptor import FieldEncryptor

def test_encryption_performance():
    """测试加密性能"""
    encryptor = FieldEncryptor(salt="test")
    
    # 测试不同规模的加密
    sizes = [100, 1000, 10000]
    times = {}
    
    for size in sizes:
        start_time = time.time()
        
        # 生成大量字段名
        for i in range(size):
            struct_name = f"Struct{i // 100}"  # 每100个字段一个结构体
            field_name = f"field_{i}"
            encryptor.encrypt_field_name(struct_name, field_name)
            
        end_time = time.time()
        times[size] = end_time - start_time
        
    # 检查性能增长是否合理（应该接近线性）
    for i in range(len(sizes) - 1):
        ratio = times[sizes[i+1]] / times[sizes[i]]
        size_ratio = sizes[i+1] / sizes[i]
        assert ratio < size_ratio * 1.5  # 允许50%的性能开销增长

def test_lookup_performance():
    """测试查找性能"""
    encryptor = FieldEncryptor(salt="test")
    
    # 生成测试数据
    for i in range(1000):
        struct_name = f"Struct{i // 100}"
        field_name = f"field_{i}"
        encryptor.encrypt_field_name(struct_name, field_name)
    
    # 测试查找性能
    start_time = time.time()
    for _ in range(10000):
        struct_name = "Struct0"
        field_name = "field_0"
        encrypted = encryptor.encrypted_fields[struct_name][field_name]
        original = encryptor.field_comments[struct_name][encrypted]
        
    end_time = time.time()
    lookup_time = end_time - start_time
    
    # 每次查找应该在1微秒以内
    assert lookup_time / 10000 < 0.001

def test_memory_usage():
    """测试内存使用"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    encryptor = FieldEncryptor(salt="test")
    
    # 生成大量数据
    for i in range(10000):
        struct_name = f"Struct{i // 100}"
        field_name = f"field_{i}"
        encryptor.encrypt_field_name(struct_name, field_name)
        
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # 检查内存增长是否合理（每个映射项应该小于100字节）
    assert memory_increase / 10000 < 100 
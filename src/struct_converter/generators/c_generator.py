from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Template
from loguru import logger
from config import GeneratorConfig
from c_parser.core.type_manager import TypeManager
from .base_generator import BaseGenerator

logger = logger.bind(name="CGenerator")

class CGenerator(BaseGenerator):
    """C代码生成器"""
    
    def __init__(self, config: Optional[GeneratorConfig] = None):
        super().__init__(config or GeneratorConfig())
        self.type_manager = TypeManager()
        self.logger = logger
        
    def _generate(self, parse_result: Dict[str, Any]) -> Dict[str, str]:
        """生成C代码"""
        try:
            # 生成头文件
            header_template = self.env.get_template('c/header.h.jinja')
            header = header_template.render(**parse_result)
            
            # 生成源文件
            source_template = self.env.get_template('c/source.c.jinja')
            source = source_template.render(**parse_result)
            
            return {
                'h': header,
                'c': source
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate C code: {e}")
            raise
            
    def _to_c_type(self, type_info: Dict[str, Any]) -> str:
        """转换为C类型"""
        base_type = type_info.get('base_type', 'void')
        
        # 处理指针
        ptr_level = type_info.get('pointer_level', 0)
        ptr_str = '*' * ptr_level
        
        # 处理const修饰符
        const = 'const ' if type_info.get('is_const') else ''
        
        # 处理volatile修饰符
        volatile = 'volatile ' if type_info.get('is_volatile') else ''
        
        # 处理数组
        array_dims = type_info.get('array_dims', [])
        array_str = ''.join(f'[{d}]' for d in array_dims)
        
        # 处理位域
        bit_width = type_info.get('bit_width')
        bit_str = f' : {bit_width}' if bit_width is not None else ''
        
        return f'{const}{volatile}{base_type}{ptr_str}{array_str}{bit_str}'
        
    def _get_default_value(self, type_info: Dict[str, Any]) -> str:
        """获取C类型默认值"""
        base_type = type_info.get('base_type', 'void')
        
        if type_info.get('pointer_level', 0) > 0:
            return 'NULL'
            
        if base_type in {'char', 'int8_t', 'uint8_t', 'short', 'int16_t', 'uint16_t',
                        'int', 'int32_t', 'uint32_t', 'long', 'int64_t', 'uint64_t'}:
            return '0'
            
        if base_type in {'float', 'double'}:
            return '0.0'
            
        if base_type == 'bool':
            return 'false'
            
        return '{0}'  # 结构体默认值
        
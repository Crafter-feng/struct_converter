from typing import Dict, Any
from loguru import logger
from ..core.config import GeneratorConfig
from .base_generator import BaseGenerator
from utils.decorators import log_execution

class PythonGenerator(BaseGenerator):
    """Python代码生成器"""
    
    def __init__(self, config: GeneratorConfig = None):
        super().__init__(config)
        self.logger = logger.bind(generator="PythonGenerator")
        
        # C类型到Python类型的映射
        self.type_map = {
            'int8_t': 'int',
            'uint8_t': 'int',
            'int16_t': 'int',
            'uint16_t': 'int',
            'int32_t': 'int',
            'uint32_t': 'int',
            'int64_t': 'int',
            'uint64_t': 'int',
            'float': 'float',
            'double': 'float',
            'char': 'str',
            'bool': 'bool',
            'void': 'None',
        }
        
    def _generate(self, parse_result: Dict[str, Any]) -> Dict[str, str]:
        """生成Python代码"""
        try:
            template = self.env.get_template('python/structs.py.jinja')
            code = template.render(**parse_result)
            return {'py': code}
            
        except Exception as e:
            self.logger.error(f"Failed to generate Python code: {e}")
            raise
            
    def _to_python_type(self, type_info: Dict[str, Any]) -> str:
        """转换为Python类型"""
        base_type = type_info.get('base_type', 'void')
        python_type = self.type_map.get(base_type, base_type)
        
        # 处理指针
        if type_info.get('pointer_level', 0) > 0:
            return 'Optional[int]'  # 指针转换为可选整数
            
        # 处理数组
        array_dims = type_info.get('array_dims', [])
        if array_dims:
            if base_type == 'char':
                return 'str'  # 字符数组转换为字符串
            return f'List[{python_type}]' * len(array_dims)
            
        return python_type
        
    def _get_default_value(self, type_info: Dict[str, Any]) -> str:
        """获取Python类型默认值"""
        base_type = type_info.get('base_type', 'void')
        
        if type_info.get('pointer_level', 0) > 0:
            return 'None'
            
        if base_type in {'int8_t', 'uint8_t', 'int16_t', 'uint16_t',
                        'int32_t', 'uint32_t', 'int64_t', 'uint64_t',
                        'int', 'long'}:
            return '0'
            
        if base_type in {'float', 'double'}:
            return '0.0'
            
        if base_type == 'bool':
            return 'False'
            
        if base_type == 'char':
            if type_info.get('array_dims'):
                return '""'  # 字符数组默认为空字符串
            return "'\\0'"
            
        if type_info.get('array_dims'):
            return '[]'  # 数组默认为空列表
            
        return 'None'  # 其他类型默认为None 
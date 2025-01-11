from typing import Dict, Any, Optional
from loguru import logger
from jinja2 import Environment, PackageLoader, select_autoescape
from ..core.config import GeneratorConfig
from utils.code_formatter import CodeFormatter
from utils.decorators import log_execution

class BaseGenerator:
    """代码生成器基类"""
    
    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.config = config or GeneratorConfig()
        self.logger = logger.bind(generator=self.__class__.__name__)
        self.formatter = CodeFormatter()
        
        # 初始化模板环境
        self.env = Environment(
            loader=PackageLoader('struct_converter', 'templates'),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # 添加自定义过滤器
        self.env.filters.update({
            'to_c_type': self._to_c_type,
            'to_python_type': self._to_python_type,
            'format_array': self._format_array,
            'default_value': self._get_default_value
        })
        
    @log_execution()
    def generate(self, parse_result: Dict[str, Any]) -> Dict[str, str]:
        """生成代码
        
        Args:
            parse_result: 解析结果
            
        Returns:
            Dict[str, str]: 生成的代码文件，key为扩展名
        """
        try:
            # 预处理解析结果
            processed = self._preprocess(parse_result)
            
            # 生成代码
            result = self._generate(processed)
            
            # 格式化代码
            for ext, content in result.items():
                result[ext] = self.formatter.format_code(content)
                
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate code: {e}")
            raise
            
    def _preprocess(self, parse_result: Dict[str, Any]) -> Dict[str, Any]:
        """预处理解析结果"""
        return parse_result
        
    def _generate(self, parse_result: Dict[str, Any]) -> Dict[str, str]:
        """实际的代码生成逻辑，由子类实现"""
        raise NotImplementedError
        
    def _to_c_type(self, type_info: Dict[str, Any]) -> str:
        """转换为C类型"""
        raise NotImplementedError
        
    def _to_python_type(self, type_info: Dict[str, Any]) -> str:
        """转换为Python类型"""
        raise NotImplementedError
        
    def _format_array(self, dims: list) -> str:
        """格式化数组维度"""
        if not dims:
            return ""
        return "".join(f"[{d}]" for d in dims)
        
    def _get_default_value(self, type_info: Dict[str, Any]) -> str:
        """获取类型默认值"""
        raise NotImplementedError 
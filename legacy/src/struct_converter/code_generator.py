import logging
from typing import Dict, Any, Optional
from jinja2 import Environment, PackageLoader, select_autoescape
from utils.logging import log_execution
from utils.cache import cached, ThreadSafeCache
from utils.code_formatter import CodeFormatter

logger = logging.getLogger(__name__)

class CodeGenerator:
    """代码生成器基类"""
    
    def __init__(self):
        # 初始化Jinja2环境
        self.env = Environment(
            loader=PackageLoader('struct_converter', 'templates'),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
            # 启用异步支持
            enable_async=True,
            # 优化选项
            optimized=True,
            cache_size=200
        )
        
        # 初始化缓存
        self.template_cache = ThreadSafeCache()
        self.formatter = CodeFormatter()
        
    @cached(lambda self, template_name: f"template:{template_name}")
    def _get_template(self, template_name: str):
        """获取模板（带缓存）"""
        return self.env.get_template(template_name)
        
    @log_execution(logger)
    def generate(self, template_name: str, context: Dict[str, Any]) -> str:
        """生成代码
        
        Args:
            template_name: 模板名称
            context: 模板上下文
            
        Returns:
            str: 生成的代码
        """
        try:
            # 获取模板
            template = self._get_template(template_name)
            
            # 渲染代码
            code = template.render(**context)
            
            # 格式化代码
            formatted_code = self.formatter.format_code(code)
            
            return formatted_code
            
        except Exception as e:
            logger.error(f"Failed to generate code: {e}")
            raise
            
    def _preprocess_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """预处理模板上下文
        
        - 移除不需要的数据
        - 添加辅助函数
        - 优化数据结构
        """
        processed = {}
        
        # 只复制需要的数据
        for key in ['module_name', 'structs', 'enums', 'unions', 'typedefs']:
            if key in context:
                processed[key] = context[key]
                
        # 添加辅助函数
        processed.update({
            'to_c_type': self._to_c_type,
            'array_dims': self._format_array_dims,
            'struct_size': self._calc_struct_size
        })
        
        return processed
        
    def _to_c_type(self, type_info: Dict[str, Any]) -> str:
        """转换为C类型"""
        # 实现类型转换逻辑
        pass
        
    def _format_array_dims(self, dims: Optional[list]) -> str:
        """格式化数组维度"""
        if not dims:
            return ""
        return "".join(f"[{d}]" for d in dims)
        
    def _calc_struct_size(self, struct_info: Dict[str, Any]) -> int:
        """计算结构体大小"""
        # 实现结构体大小计算逻辑
        pass 
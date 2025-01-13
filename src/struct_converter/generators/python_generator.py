from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Template
from loguru import logger
from config import GeneratorConfig
from .base_generator import BaseGenerator

logger = logger.bind(name="PythonGenerator")

class PythonGenerator(BaseGenerator):
    """Python代码生成器"""
    
    def __init__(self, config: Optional[GeneratorConfig] = None):
        super().__init__(config or GeneratorConfig())
        self.logger = logger
        
    def _add_filters(self):
        """添加Python特定的模板过滤器"""
        self.env.filters['to_python_type'] = self._to_python_type
        
    def _generate(self, parse_result: Dict[str, Any]) -> Dict[str, str]:
        """生成Python代码"""
        try:
            template = self.env.get_template('python/module.py.jinja')
            code = template.render(**parse_result)
            return {'py': code}
        except Exception as e:
            self.logger.error(f"Failed to generate Python code: {e}")
            raise 
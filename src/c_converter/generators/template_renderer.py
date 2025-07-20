from typing import Dict, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from loguru import logger

logger = logger.bind(name="TemplateRenderer")

class TemplateRenderer:
    def __init__(self, config):
        self.config = config
        self.logger = logger
        
        # 初始化Jinja2环境
        template_dir = Path(self.config.template_dir)
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """渲染模板"""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            self.logger.error(f"Failed to render template {template_name}: {e}")
            raise 
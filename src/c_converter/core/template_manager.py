from jinja2 import Environment, FileSystemLoader
from pathlib import Path

class TemplateManager:
    """模板管理器"""
    def __init__(self, template_dir: Path):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def render_template(self, template_name: str, **kwargs) -> str:
        """渲染模板"""
        template = self.env.get_template(template_name)
        return template.render(**kwargs) 
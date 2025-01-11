from typing import Dict, Any
from jinja2 import Environment, PackageLoader, select_autoescape
from struct_converter.core.generator import CodeGenerator
from struct_converter.core.exceptions import CodeGenerationError
from utils.logger_config import get_logger

logger = get_logger("CppGenerator")

class CppGenerator(CodeGenerator):
    """C++代码生成器"""
    
    def __init__(self):
        self.env = Environment(
            loader=PackageLoader('struct_converter', 'templates/cpp'),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def generate(self, parse_result: Dict[str, Any]) -> str:
        """生成C++代码"""
        try:
            template = self.env.get_template('structs.hpp.jinja')
            return template.render(
                structs=parse_result.get('structs', {}),
                enums=parse_result.get('enums', {}),
                unions=parse_result.get('unions', {}),
                typedefs=parse_result.get('typedefs', {}),
                macros=parse_result.get('macros', {})
            )
        except Exception as e:
            logger.error(f"Failed to generate C++ code: {e}")
            raise CodeGenerationError(f"Failed to generate C++ code: {e}")
            
    def get_file_extension(self) -> str:
        return "hpp" 
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .type_converter import TypeConverter
from utils.logger_config import get_logger
from pathlib import Path
from .config import GeneratorConfig
from .exceptions import CodeGenerationError
from utils.code_formatter import CodeFormatter

logger = get_logger("CodeGenerator")

class CodeGenerator(ABC):
    """代码生成器基类"""
    
    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.type_converter = TypeConverter()
        self.config = config or GeneratorConfig()
        self.formatter = CodeFormatter()
        
    def _prepare_output_dir(self) -> None:
        """准备输出目录"""
        try:
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create output directory: {e}")
            raise CodeGenerationError(f"Failed to create output directory: {e}")
            
    def _get_template_context(self, parse_result: Dict[str, Any]) -> Dict[str, Any]:
        """获取模板上下文"""
        return {
            'config': self.config,
            'module_name': parse_result.get('module_name', 'generated'),
            'structs': parse_result.get('structs', {}),
            'enums': parse_result.get('enums', {}),
            'unions': parse_result.get('unions', {}),
            'typedefs': parse_result.get('typedefs', {}),
            'macros': parse_result.get('macros', {}),
            'type_converter': self.type_converter
        }
        
    @abstractmethod
    def generate(self, parse_result: Dict[str, Any]) -> Dict[str, str]:
        """生成代码
        
        Args:
            parse_result: 解析结果
            
        Returns:
            Dict[str, str]: 文件名到内容的映射
        """
        pass
        
    @abstractmethod
    def get_file_extension(self) -> str:
        """获取生成文件的扩展名"""
        pass
        
    def get_output_files(self, module_name: str) -> Dict[str, str]:
        """获取输出文件列表
        
        Args:
            module_name: 模块名
            
        Returns:
            Dict[str, str]: 文件名到路径的映射
        """
        return {
            'header': f"{module_name}.{self.get_file_extension()}",
            'source': f"{module_name}.c"
        }
        
    def validate_parse_result(self, parse_result: Dict[str, Any]) -> bool:
        """验证解析结果
        
        Args:
            parse_result: 解析结果
            
        Returns:
            bool: 是否有效
        """
        try:
            required_keys = {'module_name', 'structs', 'enums', 'unions', 'typedefs', 'macros'}
            if not all(key in parse_result for key in required_keys):
                logger.error(f"Missing required keys in parse result: {required_keys - parse_result.keys()}")
                return False
                
            # 检查结构体定义
            for struct_name, struct_info in parse_result['structs'].items():
                if 'fields' not in struct_info:
                    logger.error(f"Missing fields in struct {struct_name}")
                    return False
                    
                for field in struct_info['fields']:
                    if 'name' not in field or 'type' not in field:
                        logger.error(f"Invalid field in struct {struct_name}: {field}")
                        return False
                        
            # 检查枚举定义
            for enum_name, enum_info in parse_result['enums'].items():
                if 'values' not in enum_info:
                    logger.error(f"Missing values in enum {enum_name}")
                    return False
                    
                for value in enum_info['values']:
                    if 'name' not in value or 'value' not in value:
                        logger.error(f"Invalid value in enum {enum_name}: {value}")
                        return False
                        
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate parse result: {e}")
            return False 
        
    def _format_code(self, code: str, lang: str) -> str:
        """格式化生成的代码"""
        if not code:
            return code
            
        try:
            if lang == 'python':
                return self.formatter.format_python(code)
            elif lang in ('c', 'cpp'):
                return self.formatter.format_c(code)
            return code
        except Exception as e:
            logger.warning(f"Failed to format code: {e}")
            return code 
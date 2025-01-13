from typing import Optional, List
from pathlib import Path
from ..core.cache import StructCache
from ..core.formatter import CodeFormatter
from ..core.type_helper import TypeHelper
from c_parser.core.type_manager import TypeManager
from utils.logger import logger 



class BaseGenerator:
    """代码生成器基类"""
    
    def __init__(self, type_info: dict):
        """初始化生成器
        
        Args:
            type_info: 类型信息字典
        """
        self.type_info = type_info
        self.cache = StructCache()
        self.formatter = CodeFormatter()
        self.type_manager = TypeManager(type_info)
        self.type_helper = TypeHelper(self.type_manager)
        
    def validate_type_info(self) -> bool:
        """验证类型信息"""
        if not isinstance(self.type_info, dict):
            logger.error("type_info must be a dictionary")
            return False
            
        if 'struct_info' not in self.type_info:
            logger.error("Missing struct_info in type_info")
            return False
            
        return True
        
    def generate(self, output_dir: Path) -> bool:
        """生成代码
        
        Args:
            output_dir: 输出目录
            
        Returns:
            bool: 是否成功
        """
        raise NotImplementedError
        
    def _create_directories(self, output_dir: Path) -> None:
        """创建必要的目录"""
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "tests").mkdir(exist_ok=True)
        (output_dir / ".cache").mkdir(exist_ok=True) 
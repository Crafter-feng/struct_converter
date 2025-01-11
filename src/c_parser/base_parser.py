from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from loguru import logger
from utils.logging import log_execution

class BaseParser(ABC):
    """解析器基类"""
    
    def __init__(self):
        self.type_manager = None
        self.current_file = None
        self.logger = logger.bind(parser=self.__class__.__name__)
        
    @abstractmethod
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """解析文件"""
        pass
        
    @abstractmethod
    def parse_string(self, content: str) -> Dict[str, Any]:
        """解析字符串"""
        pass
        
    @log_execution(logger)
    def parse(self, source: str, is_file: bool = False) -> Dict[str, Any]:
        """通用解析入口"""
        try:
            if is_file:
                self.current_file = source
                return self.parse_file(source)
            else:
                return self.parse_string(source)
        finally:
            self.current_file = None
            
    def _create_error_context(self, line: int, column: int, message: str) -> str:
        """创建错误上下文信息"""
        if not self.current_file:
            return f"Error at line {line}, column {column}: {message}"
            
        try:
            with open(self.current_file) as f:
                lines = f.readlines()
                
            context = []
            start = max(0, line - 2)
            end = min(len(lines), line + 3)
            
            for i in range(start, end):
                if i == line - 1:
                    # 错误行
                    context.append(f"> {i+1:4d} | {lines[i].rstrip()}")
                    context.append(f"       {' ' * column}^")
                else:
                    context.append(f"  {i+1:4d} | {lines[i].rstrip()}")
                    
            return f"Error in {self.current_file} at line {line}, column {column}:\n" + \
                   f"{message}\n\n" + "\n".join(context)
                   
        except Exception:
            return f"Error in {self.current_file} at line {line}, column {column}: {message}" 
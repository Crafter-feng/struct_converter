import re
from typing import List, Optional, Tuple
from utils.cache import cached
from utils.logging import log_execution
from loguru import logger
from utils.logger import logger 



class CodeFormatter:
    """代码格式化器"""
    
    def __init__(self, indent_size=4, continuation_indent=4):
        self.indent_size = indent_size
        self.continuation_indent = continuation_indent
        
    def _handle_multiline_string(self, line: str, indent_level: int) -> str:
        """处理多行字符串
        
        支持以下格式：
        - 三引号字符串 (''' or \"\"\")
        - 字符串连接 ("..." "...")
        - 长字符串换行
        """
        base_indent = ' ' * (indent_level * self.indent_size)
        cont_indent = ' ' * (indent_level * self.indent_size + self.continuation_indent)
        
        # 处理三引号字符串
        if '"""' in line or "'''" in line:
            # 保持原有缩进
            return line
            
        # 处理字符串连接
        if '"' in line or "'" in line:
            parts = line.split('"')
            if len(parts) > 2:  # 有多个引号，可能是字符串连接
                return base_indent + ' '.join(parts)
                
        # 处理长字符串换行
        if line.endswith('\\'):
            return base_indent + line.rstrip('\\') + '\n' + cont_indent
            
        return base_indent + line

    @log_execution
    def format_code(self, code: str) -> str:
        """格式化代码"""
        lines = code.splitlines()
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            
            # 跳过空行
            if not stripped:
                formatted_lines.append('')
                continue
                
            # 处理缩进级别
            if stripped.startswith(('class ', 'def ', 'if ', 'else:', 'elif ', 'for ', 'while ', 'try:', 'except:', 'finally:')):
                formatted_line = ' ' * (indent_level * self.indent_size) + stripped
                formatted_lines.append(formatted_line)
                if not stripped.endswith(':'):
                    indent_level += 1
                continue
                
            # 处理结束缩进
            if stripped == 'return' or stripped.startswith('return '):
                indent_level = max(0, indent_level - 1)
                
            # 处理多行字符串
            if '"""' in stripped or "'''" in stripped or ('"' in stripped and stripped.count('"') > 1):
                formatted_line = self._handle_multiline_string(stripped, indent_level)
            else:
                formatted_line = ' ' * (indent_level * self.indent_size) + stripped
                
            formatted_lines.append(formatted_line)
            
        return '\n'.join(formatted_lines) 
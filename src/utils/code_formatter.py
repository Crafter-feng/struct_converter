import re
from typing import List, Optional, Tuple
from utils.cache import cached
from utils.logging import log_execution
from loguru import logger

logger = logger.bind(component="CodeFormatter")

class CodeFormatter:
    """代码格式化器"""
    
    def __init__(self):
        self.indent_size = 4
        self.max_line_length = 80
        self.continuation_indent = 8  # 续行缩进
        
        # 编译正则表达式以提高性能
        self._operator_pattern = re.compile(r'[+\-*/=<>!&|,]')
        self._bracket_pattern = re.compile(r'[{(\[]})\]]')
        
        self.logger = logger.bind(component="CodeFormatter")
        
    @cached(lambda self, code: f"format:{hash(code)}")
    @log_execution(logger)
    def format_code(self, code: str) -> str:
        """格式化代码（带缓存）"""
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        in_multiline_comment = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # 处理空行
            if not stripped:
                formatted_lines.append('')
                i += 1
                continue
                
            # 处理多行注释
            if stripped.startswith('/*'):
                in_multiline_comment = True
                formatted_lines.append(self._indent_line(stripped, indent_level))
                i += 1
                continue
                
            if in_multiline_comment:
                formatted_lines.append(self._indent_line(stripped, indent_level))
                if stripped.endswith('*/'):
                    in_multiline_comment = False
                i += 1
                continue
                
            # 处理预处理指令
            if stripped.startswith('#'):
                formatted_lines.append(stripped)
                i += 1
                continue
                
            # 调整缩进级别
            if any(stripped.startswith(c) for c in ['}', ')', ']']):
                indent_level = max(0, indent_level - 1)
                
            # 添加格式化的行
            current_line = self._indent_line(stripped, indent_level)
            
            # 处理长行
            if len(current_line) > self.max_line_length:
                # 检查是否有多行字符串
                if self._is_multiline_string(stripped):
                    wrapped = self._wrap_string_literal(current_line, indent_level)
                else:
                    wrapped = self._wrap_long_line(current_line, indent_level)
                formatted_lines.extend(wrapped)
            else:
                formatted_lines.append(current_line)
                
            # 更新缩进级别
            if any(stripped.endswith(c) for c in ['{', '(', '[']):
                indent_level += 1
                
            i += 1
            
        return '\n'.join(formatted_lines)
        
    def _indent_line(self, line: str, level: int) -> str:
        """添加缩进"""
        return ' ' * (level * self.indent_size) + line
        
    def _wrap_long_line(self, line: str, indent_level: int) -> List[str]:
        """处理长行"""
        # 尝试在操作符处换行
        if self._operator_pattern.search(line):
            return self._wrap_at_operator(line, indent_level)
            
        # 尝试在括号处换行
        if self._bracket_pattern.search(line):
            return self._wrap_at_bracket(line, indent_level)
            
        # 如果无法优雅换行，强制换行
        return self._force_wrap(line, indent_level)
        
    def _wrap_at_operator(self, line: str, indent_level: int) -> List[str]:
        """在操作符处换行"""
        base_indent = ' ' * (indent_level * self.indent_size)
        cont_indent = ' ' * (indent_level * self.indent_size + self.continuation_indent)
        
        parts = []
        current_part = []
        current_length = len(base_indent)
        
        tokens = self._tokenize_with_operators(line)
        for i, token in enumerate(tokens):
            token_length = len(token)
            
            if current_length + token_length > self.max_line_length and current_part:
                parts.append(''.join(current_part))
                current_part = []
                current_length = len(cont_indent)
                
            current_part.append(token)
            current_length += token_length
            
        if current_part:
            parts.append(''.join(current_part))
            
        return [base_indent + parts[0]] + [cont_indent + p.lstrip() for p in parts[1:]]
        
    def _wrap_at_bracket(self, line: str, indent_level: int) -> List[str]:
        """在括号处换行"""
        base_indent = ' ' * (indent_level * self.indent_size)
        cont_indent = ' ' * (indent_level * self.indent_size + self.continuation_indent)
        
        # 找到最外层括号
        stack = []
        brackets = {'{': '}', '(': ')', '[': ']'}
        parts = []
        start = 0
        
        for i, char in enumerate(line):
            if char in brackets:
                if not stack:
                    if i > start:
                        parts.append(line[start:i])
                    start = i
                stack.append(char)
            elif char in brackets.values():
                if stack:
                    stack.pop()
                    if not stack:
                        parts.append(line[start:i+1])
                        start = i + 1
                        
        if start < len(line):
            parts.append(line[start:])
            
        # 格式化每个部分
        result = []
        current_line = base_indent
        
        for part in parts:
            if len(current_line) + len(part) > self.max_line_length:
                if current_line != base_indent:
                    result.append(current_line)
                current_line = cont_indent + part
            else:
                current_line += part
                
        if current_line:
            result.append(current_line)
            
        return result
        
    def _force_wrap(self, line: str, indent_level: int) -> List[str]:
        """强制换行"""
        base_indent = ' ' * (indent_level * self.indent_size)
        cont_indent = ' ' * (indent_level * self.indent_size + self.continuation_indent)
        
        # 按最大长度分割
        max_content_length = self.max_line_length - len(base_indent)
        cont_max_length = self.max_line_length - len(cont_indent)
        
        result = []
        remaining = line.strip()
        
        # 第一行使用基本缩进
        if len(remaining) > max_content_length:
            result.append(base_indent + remaining[:max_content_length])
            remaining = remaining[max_content_length:]
        else:
            result.append(base_indent + remaining)
            remaining = ''
            
        # 后续行使用续行缩进
        while remaining:
            if len(remaining) > cont_max_length:
                result.append(cont_indent + remaining[:cont_max_length])
                remaining = remaining[cont_max_length:]
            else:
                result.append(cont_indent + remaining)
                break
                
        return result
        
    def _is_multiline_string(self, line: str) -> bool:
        """检查是否是多行字符串"""
        return '"""' in line or "'''" in line
        
    def _wrap_string_literal(self, line: str, indent_level: int) -> List[str]:
        """处理多行字符串
        
        支持以下格式：
        - 三引号字符串 (""" or ''')
        - 字符串连接 ("..." "...")
        - 长字符串换行
        """
        base_indent = ' ' * (indent_level * self.indent_size)
        cont_indent = ' ' * (indent_level * self.indent_size + self.continuation_indent)
        
        # 处理三引号字符串
        if '"""' in line or "'''" in line:
            return self._wrap_triple_quoted_string(line, base_indent, cont_indent)
        
        # 处理字符串连接
        if '"' in line or "'" in line:
            return self._wrap_concatenated_string(line, base_indent, cont_indent)
        
        return self._force_wrap(line, indent_level)
        
    def _wrap_triple_quoted_string(self, line: str, base_indent: str, cont_indent: str) -> List[str]:
        """处理三引号字符串"""
        # 找到字符串边界
        quote = '"""' if '"""' in line else "'''"
        start = line.index(quote)
        end = line.rindex(quote)
        
        # 分离前缀和后缀
        prefix = line[:start].rstrip()
        content = line[start:end + 3]
        suffix = line[end + 3:].lstrip()
        
        # 处理字符串内容
        content_lines = content.split('\n')
        if len(content_lines) == 1:
            # 单行但太长，需要换行
            if len(prefix) + len(content) + len(suffix) > self.max_line_length:
                result = [
                    f"{base_indent}{prefix}{quote}",
                    f"{cont_indent}{content[3:-3].strip()}",
                    f"{cont_indent}{quote}{suffix}"
                ]
                return [line for line in result if line.strip()]
        else:
            # 已经是多行
            result = [f"{base_indent}{prefix}{content_lines[0]}"]
            for content_line in content_lines[1:-1]:
                result.append(f"{cont_indent}{content_line.strip()}")
            result.append(f"{cont_indent}{content_lines[-1]}{suffix}")
            return result
        
        return [line]
        
    def _wrap_concatenated_string(self, line: str, base_indent: str, cont_indent: str) -> List[str]:
        """处理字符串连接"""
        # 分割字符串
        parts = []
        current = []
        in_string = False
        quote_char = None
        
        for char in line:
            if char in '"\'':
                if not in_string:
                    in_string = True
                    quote_char = char
                elif char == quote_char:
                    in_string = False
                    quote_char = None
                    current.append(char)
                    parts.append(''.join(current))
                    current = []
                    continue
            current.append(char)
        
        if current:
            parts.append(''.join(current))
        
        # 格式化各部分
        result = []
        current_line = base_indent
        
        for i, part in enumerate(parts):
            # 检查是否需要换行
            if len(current_line) + len(part) > self.max_line_length:
                if current_line != base_indent:
                    result.append(current_line.rstrip())
                current_line = cont_indent
            
            # 添加字符串连接操作符
            if i > 0 and not current_line.endswith(' '):
                current_line += ' '
            
            current_line += part.lstrip()
        
        if current_line:
            result.append(current_line)
        
        return result
        
    def _tokenize_with_operators(self, line: str) -> List[str]:
        """将代码行分解为标记"""
        tokens = []
        current_token = []
        
        for char in line:
            if self._operator_pattern.match(char):
                if current_token:
                    tokens.append(''.join(current_token))
                    current_token = []
                tokens.append(char)
            else:
                current_token.append(char)
                
        if current_token:
            tokens.append(''.join(current_token))
            
        return tokens 
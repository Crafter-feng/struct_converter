from typing import Any, Tuple, Dict, Optional
from utils.logger_config import setup_logger
import re

logger = setup_logger('ExpressionParser')

class ExpressionParser:
    """C语言表达式解析器"""
    
    OPERATORS = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y if y != 0 else 0,
        '<<': lambda x, y: x << y,
        '>>': lambda x, y: x >> y,
        '&': lambda x, y: x & y,
        '|': lambda x, y: x | y,
        '^': lambda x, y: x ^ y
    }
    
    @staticmethod
    def parse(expr: str, enum_info: Dict = None, macro_defs: Dict = None) -> Tuple[Any, str]:
        """解析表达式
        
        Args:
            expr: 表达式字符串
            enum_info: 枚举信息字典
            macro_defs: 宏定义字典
            
        Returns:
            (value, type): 解析结果和类型
        """
        try:
            # 预处理表达式
            expr = expr.strip()
            if not expr:
                return None, 'void'
                
            # 处理字符串字面量
            if expr.startswith('"'):
                return ExpressionParser._parse_string_literal(expr)
                
            # 处理字符字面量
            if expr.startswith("'"):
                return ExpressionParser._parse_char_literal(expr)
                
            # 处理数字字面量
            if ExpressionParser._is_number(expr):
                return ExpressionParser._parse_number_literal(expr)
                
            # 处理标识符
            if ExpressionParser._is_identifier(expr):
                return ExpressionParser._parse_identifier(expr, enum_info, macro_defs)
                
            # 处理表达式
            return ExpressionParser._parse_binary_expression(expr, enum_info, macro_defs)
            
        except Exception as e:
            logger.error(f"Failed to parse expression {expr}: {str(e)}")
            return None, 'void'
            
    @staticmethod
    def _parse_string_literal(expr: str) -> Tuple[str, str]:
        """解析字符串字面量"""
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1], 'char*'
        return expr, 'char*'
        
    @staticmethod
    def _parse_char_literal(expr: str) -> Tuple[str, str]:
        """解析字符字面量"""
        if expr.startswith("'") and expr.endswith("'"):
            return expr[1:-1], 'char'
        return expr, 'char'
        
    @staticmethod
    def _parse_number_literal(expr: str) -> Tuple[Union[int, float], str]:
        """解析数字字面量"""
        try:
            # 处理十六进制
            if expr.startswith('0x') or expr.startswith('0X'):
                return int(expr, 16), 'int'
                
            # 处理八进制
            if expr.startswith('0'):
                try:
                    return int(expr, 8), 'int'
                except ValueError:
                    pass
                    
            # 处理浮点数
            if '.' in expr or 'e' in expr.lower():
                return float(expr), 'float'
                
            # 处理整数
            return int(expr), 'int'
            
        except ValueError:
            logger.error(f"Invalid number literal: {expr}")
            return 0, 'int'
            
    @staticmethod
    def _parse_identifier(expr: str, enum_info: Dict, macro_defs: Dict) -> Tuple[Any, str]:
        """解析标识符"""
        # 检查枚举值
        if enum_info:
            for enum_type, values in enum_info.items():
                for value in values:
                    if value['name'] == expr:
                        return value['value'], 'int'
                        
        # 检查宏定义
        if macro_defs and expr in macro_defs:
            return macro_defs[expr], 'int'
            
        logger.warning(f"Unknown identifier: {expr}")
        return 0, 'int'
        
    @staticmethod
    def _parse_binary_expression(expr: str, enum_info: Dict, macro_defs: Dict) -> Tuple[Any, str]:
        """解析二元表达式"""
        # 分割表达式
        for op in ExpressionParser.OPERATORS:
            if op in expr:
                left, right = expr.split(op, 1)
                left_val, left_type = ExpressionParser.parse(left, enum_info, macro_defs)
                right_val, right_type = ExpressionParser.parse(right, enum_info, macro_defs)
                
                try:
                    result = ExpressionParser.OPERATORS[op](left_val, right_val)
                    return result, left_type
                except Exception as e:
                    logger.error(f"Failed to evaluate expression {expr}: {str(e)}")
                    return 0, 'int'
                    
        # 如果没有找到操作符，可能是括号表达式
        if expr.startswith('(') and expr.endswith(')'):
            return ExpressionParser.parse(expr[1:-1], enum_info, macro_defs)
            
        logger.error(f"Invalid expression: {expr}")
        return 0, 'int'
        
    @staticmethod
    def _is_number(expr: str) -> bool:
        """检查是否为数字字面量"""
        return bool(re.match(r'^[+-]?(?:0[xX][0-9a-fA-F]+|0[0-7]*|\d+\.?\d*(?:[eE][+-]?\d+)?)$', expr))
        
    @staticmethod
    def _is_identifier(expr: str) -> bool:
        """检查是否为标识符"""
        return bool(re.match(r'^[a-zA-Z_]\w*$', expr)) 
from typing import Dict, Any, Tuple, Optional
from loguru import logger

class ExpressionParser:
    """表达式解析器"""
    
    def __init__(self):
        """初始化表达式解析器"""
        self.logger = logger.bind(name="ExpressionParser")
        self.operators = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y,
            '%': lambda x, y: x % y,
            '<<': lambda x, y: x << y,
            '>>': lambda x, y: x >> y,
            '&': lambda x, y: x & y,
            '|': lambda x, y: x | y,
            '^': lambda x, y: x ^ y,
            '~': lambda x: ~x,
            '!': lambda x: not x,
            '&&': lambda x, y: x and y,
            '||': lambda x, y: x or y,
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y,
            '<': lambda x, y: x < y,
            '<=': lambda x, y: x <= y,
            '>': lambda x, y: x > y,
            '>=': lambda x, y: x >= y
        }

    @classmethod
    def parse(cls, expr: str, enum_values: Dict[str, Any], macro_values: Dict[str, Any]) -> Tuple[Any, str]:
        """解析表达式
        
        Args:
            expr: 表达式字符串
            enum_values: 枚举值字典
            macro_values: 宏定义字典
            
        Returns:
            Tuple[Any, str]: (解析结果, 结果类型)
        """
        try:
            parser = cls()
            # 首先尝试从枚举值和宏定义中查找
            if expr in enum_values:
                return enum_values[expr], 'enum'
            if expr in macro_values:
                return macro_values[expr], 'macro'
                
            # 尝试解析数值
            try:
                # 十六进制
                if expr.startswith('0x') or expr.startswith('0X'):
                    return int(expr, 16), 'int'
                # 八进制
                elif expr.startswith('0'):
                    return int(expr, 8), 'int'
                # 十进制
                else:
                    return int(expr), 'int'
            except ValueError:
                pass
                
            # 尝试解析表达式
            result = parser._evaluate_expression(expr, enum_values, macro_values)
            return result, 'expression'
            
        except Exception as e:
            logger.error(f"Failed to parse expression string {expr}: {e}")
            return expr, 'error'

    def _evaluate_expression(self, expr: str, enum_values: Dict[str, Any], macro_values: Dict[str, Any]) -> Any:
        """计算表达式的值"""
        try:
            # 处理括号
            if '(' in expr:
                return self._evaluate_parentheses(expr, enum_values, macro_values)
                
            # 处理运算符
            for op in self.operators:
                if op in expr:
                    left, right = expr.split(op, 1)
                    left_val = self._evaluate_expression(left.strip(), enum_values, macro_values)
                    right_val = self._evaluate_expression(right.strip(), enum_values, macro_values)
                    return self.operators[op](left_val, right_val)
                    
            # 处理标识符
            expr = expr.strip()
            if expr in enum_values:
                return enum_values[expr]
            if expr in macro_values:
                return macro_values[expr]
                
            # 尝试解析数值
            try:
                if expr.startswith('0x') or expr.startswith('0X'):
                    return int(expr, 16)
                elif expr.startswith('0'):
                    return int(expr, 8)
                else:
                    return int(expr)
            except ValueError:
                return expr
                
        except Exception as e:
            self.logger.error(f"Expression evaluation failed: {e}")
            return expr

    def _evaluate_parentheses(self, expr: str, enum_values: Dict[str, Any], macro_values: Dict[str, Any]) -> Any:
        """处理带括号的表达式"""
        try:
            # 找到最内层括号
            start = expr.rfind('(')
            if start == -1:
                return self._evaluate_expression(expr, enum_values, macro_values)
                
            end = expr.find(')', start)
            if end == -1:
                raise ValueError("Unmatched parentheses")
                
            # 计算括号内的表达式
            inner_result = self._evaluate_expression(
                expr[start + 1:end], 
                enum_values, 
                macro_values
            )
            
            # 替换括号部分并继续计算
            new_expr = expr[:start] + str(inner_result) + expr[end + 1:]
            return self._evaluate_expression(new_expr, enum_values, macro_values)
            
        except Exception as e:
            self.logger.error(f"Parentheses evaluation failed: {e}")
            return expr 
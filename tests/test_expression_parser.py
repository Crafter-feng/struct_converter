import pytest
from unittest.mock import Mock, patch

from c_parser.core.expression_parser import ExpressionParser


class TestExpressionParser:
    """ExpressionParser测试类"""
    
    def test_parse_string_literal(self):
        """测试解析字符串字面量"""
        # 测试单引号字符串
        result, result_type = ExpressionParser.parse("'hello'")
        assert result == "'hello'"
        assert result_type == 'string'
        
        # 测试双引号字符串
        result, result_type = ExpressionParser.parse('"world"')
        assert result == '"world"'
        assert result_type == 'string'
        
        # 测试空字符串
        result, result_type = ExpressionParser.parse('""')
        assert result == '""'
        assert result_type == 'string'
    
    def test_parse_number_literals(self):
        """测试解析数字字面量"""
        # 测试整数
        result, result_type = ExpressionParser.parse("42")
        assert result == 42
        assert result_type == 'number'
        
        # 测试负数
        result, result_type = ExpressionParser.parse("-123")
        assert result == -123
        assert result_type == 'number'
        
        # 测试十六进制
        result, result_type = ExpressionParser.parse("0xFF")
        assert result == 255
        assert result_type == 'number'
        
        result, result_type = ExpressionParser.parse("0xff")
        assert result == 255
        assert result_type == 'number'
        
        # 测试八进制
        result, result_type = ExpressionParser.parse("077")
        assert result == 63
        assert result_type == 'number'
        
        # 测试二进制
        result, result_type = ExpressionParser.parse("0b1010")
        assert result == 10
        assert result_type == 'number'
        
        # 测试浮点数
        result, result_type = ExpressionParser.parse("3.14")
        assert result == 3.14
        assert result_type == 'number'
        
        result, result_type = ExpressionParser.parse("2.5e3")
        assert result == 2500.0
        assert result_type == 'number'
        
        # 测试科学计数法
        result, result_type = ExpressionParser.parse("1.5e-2")
        assert result == 0.015
        assert result_type == 'number'
        
        # 测试带后缀的数字
        result, result_type = ExpressionParser.parse("42L")
        assert result == 42
        assert result_type == 'number'
        
        result, result_type = ExpressionParser.parse("3.14f")
        assert result == 3.14
        assert result_type == 'number'
    
    def test_parse_with_enum_values(self):
        """测试解析包含枚举值的表达式"""
        enum_values = {
            'Color': {
                'RED': 0,
                'GREEN': 1,
                'BLUE': 2
            },
            'Status': {
                'OK': 0,
                'ERROR': -1
            }
        }
        
        # 测试简单枚举值
        result, result_type = ExpressionParser.parse("RED", enum_values)
        assert result == 0
        assert result_type == 'number'
        
        # 测试枚举值运算
        result, result_type = ExpressionParser.parse("RED + 1", enum_values)
        assert result == 1
        assert result_type == 'number'
        
        # 测试多个枚举值运算
        result, result_type = ExpressionParser.parse("RED | GREEN", enum_values)
        assert result == 1
        assert result_type == 'number'
        
        # 测试不同枚举类型
        result, result_type = ExpressionParser.parse("RED + OK", enum_values)
        assert result == 0
        assert result_type == 'number'
    
    def test_parse_with_macro_values(self):
        """测试解析包含宏定义的表达式"""
        macro_values = {
            'MAX_SIZE': 100,
            'PI': 3.14159,
            'FLAG_ENABLED': 1,
            'FLAG_DISABLED': 0
        }
        
        # 测试简单宏值
        result, result_type = ExpressionParser.parse("MAX_SIZE", macro_values=macro_values)
        assert result == 100
        assert result_type == 'number'
        
        # 测试宏值运算
        result, result_type = ExpressionParser.parse("MAX_SIZE * 2", macro_values=macro_values)
        assert result == 200
        assert result_type == 'number'
        
        # 测试浮点数宏
        result, result_type = ExpressionParser.parse("PI * 2", macro_values=macro_values)
        assert result == 6.28318
        assert result_type == 'number'
        
        # 测试位运算
        result, result_type = ExpressionParser.parse("FLAG_ENABLED | FLAG_DISABLED", macro_values=macro_values)
        assert result == 1
        assert result_type == 'number'
    
    def test_parse_complex_expressions(self):
        """测试解析复杂表达式"""
        enum_values = {'Flags': {'FLAG_A': 1, 'FLAG_B': 2, 'FLAG_C': 4}}
        macro_values = {'MASK': 0xFF, 'SHIFT': 8}
        
        # 测试位运算表达式
        result, result_type = ExpressionParser.parse("(FLAG_A | FLAG_B) & MASK", enum_values, macro_values)
        assert result == 3
        assert result_type == 'number'
        
        # 测试移位运算
        result, result_type = ExpressionParser.parse("FLAG_A << SHIFT", enum_values, macro_values)
        assert result == 256
        assert result_type == 'number'
        
        # 测试混合运算
        result, result_type = ExpressionParser.parse("(FLAG_A + FLAG_B) * 2", enum_values, macro_values)
        assert result == 6
        assert result_type == 'number'
    
    def test_parse_expression_with_unknown_variables(self):
        """测试解析包含未知变量的表达式"""
        # 测试未知变量（应该返回原表达式）
        result, result_type = ExpressionParser.parse("unknown_var + 1")
        assert result == "unknown_var + 1"
        assert result_type == 'expression'
        
        # 测试部分已知变量
        enum_values = {'Color': {'RED': 0}}
        result, result_type = ExpressionParser.parse("RED + unknown_var", enum_values)
        assert result == "0 + unknown_var"
        assert result_type == 'expression'
    
    def test_parse_bytes_input(self):
        """测试解析字节输入"""
        # 测试字节字符串输入
        result, result_type = ExpressionParser.parse(b"42")
        assert result == 42
        assert result_type == 'number'
        
        result, result_type = ExpressionParser.parse(b"'hello'")
        assert result == "'hello'"
        assert result_type == 'string'
    
    def test_parse_edge_cases(self):
        """测试边界情况"""
        # 测试空字符串
        result, result_type = ExpressionParser.parse("")
        assert result == ""
        assert result_type == 'expression'
        
        # 测试只有空格的字符串
        result, result_type = ExpressionParser.parse("   ")
        assert result == ""
        assert result_type == 'expression'
        
        # 测试无效数字格式
        result, result_type = ExpressionParser.parse("invalid_number")
        assert result == "invalid_number"
        assert result_type == 'expression'
        
        # 测试无效十六进制
        result, result_type = ExpressionParser.parse("0xGG")
        assert result == "0xGG"
        assert result_type == 'expression'
    
    def test_parse_arithmetic_expressions(self):
        """测试算术表达式"""
        # 基本算术运算
        result, result_type = ExpressionParser.parse("2 + 3")
        assert result == 5
        assert result_type == 'number'
        
        result, result_type = ExpressionParser.parse("10 - 4")
        assert result == 6
        assert result_type == 'number'
        
        result, result_type = ExpressionParser.parse("6 * 7")
        assert result == 42
        assert result_type == 'number'
        
        result, result_type = ExpressionParser.parse("15 / 3")
        assert result == 5.0
        assert result_type == 'number'
        
        # 复杂算术表达式
        result, result_type = ExpressionParser.parse("(2 + 3) * 4")
        assert result == 20
        assert result_type == 'number'
        
        result, result_type = ExpressionParser.parse("10 - 2 * 3")
        assert result == 4
        assert result_type == 'number'
    
    def test_parse_bitwise_expressions(self):
        """测试位运算表达式"""
        # 位运算
        result, result_type = ExpressionParser.parse("5 & 3")
        assert result == 1
        assert result_type == 'number'
        
        result, result_type = ExpressionParser.parse("5 | 3")
        assert result == 7
        assert result_type == 'number'
        
        result, result_type = ExpressionParser.parse("5 ^ 3")
        assert result == 6
        assert result_type == 'number'
        
        result, result_type = ExpressionParser.parse("~5")
        assert result == -6
        assert result_type == 'number'
        
        # 移位运算
        result, result_type = ExpressionParser.parse("8 << 2")
        assert result == 32
        assert result_type == 'number'
        
        result, result_type = ExpressionParser.parse("32 >> 2")
        assert result == 8
        assert result_type == 'number'
    
    def test_parse_with_mixed_types(self):
        """测试混合类型解析"""
        enum_values = {'Status': {'OK': 0, 'ERROR': -1}}
        macro_values = {'MAX': 100}
        
        # 混合使用枚举、宏和字面量
        result, result_type = ExpressionParser.parse("OK + MAX + 1", enum_values, macro_values)
        assert result == 101
        assert result_type == 'number'
        
        # 字符串和数字混合（应该保持为表达式）
        result, result_type = ExpressionParser.parse("'status' + OK", enum_values, macro_values)
        assert result == "'status' + 0"
        assert result_type == 'expression'
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试除零错误
        result, result_type = ExpressionParser.parse("1 / 0")
        assert result == "1 / 0"
        assert result_type == 'expression'
        
        # 测试语法错误
        result, result_type = ExpressionParser.parse("1 + + 2")
        assert result == "1 + + 2"
        assert result_type == 'expression'
        
        # 测试未闭合的括号
        result, result_type = ExpressionParser.parse("(1 + 2")
        assert result == "(1 + 2"
        assert result_type == 'expression'

from tree_sitter import Language, Parser
from utils.logger_config import setup_logger

logger = setup_logger('TreeSitterUtil')


class TreeSitterUtil:
    """Tree-sitter工具类，负责管理tree-sitter的初始化和实例"""
    
    _instance = None
    _parser = None
    _language = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(TreeSitterUtil, cls).__new__(cls)
            cls._instance._init_tree_sitter()
        return cls._instance
    
    def _init_tree_sitter(self):
        """初始化tree-sitter"""
        logger.info("Initializing tree-sitter")
        try:
            self._language = Language('build/my-languages.so', 'c')
            logger.debug("Loaded existing language library")
        except:
            logger.info("Building language library")
            Language.build_library(
                'build/my-languages.so',
                ['tree-sitter-c']
            )
            self._language = Language('build/my-languages.so', 'c')
        
        self._parser = Parser()
        self._parser.set_language(self._language)
        logger.info("Tree-sitter initialization completed")
    
    @property
    def parser(self):
        """获取parser实例"""
        return self._parser
    
    @property
    def language(self):
        """获取language实例"""
        return self._language
    
    def parse_file(self, file_path):
        """解析文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            tree: 语法树
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.parser.parse(bytes(content, 'utf8'))
    
    def parse_content(self, content):
        """解析内容
        
        Args:
            content: 代码内容
            
        Returns:
            tree: 语法树
        """
        return self.parser.parse(bytes(content, 'utf8')) 

class ExpressionParser:
    """表达式解析和计算工具类"""
    
    @staticmethod
    def parse(expr, enum_values=None, macro_values=None):
        """解析表达式，返回结果和类型"""
        if isinstance(expr, bytes):
            expr = expr.decode('utf8')
        expr = expr.strip()
        
        # 检查合并enum_values
        if enum_values:
            enum_values = {k: v for d in enum_values.values() for k, v in d.items()}
            
        logger.debug(f"=== Parsing Expression ===")
        logger.debug(f"Input expression: {expr}")
        logger.debug(f"Available enum values: {enum_values}")
        logger.debug(f"Available macro values: {macro_values}")
        
        # 1. 检查字符串字面量
        if expr.startswith(("'", '"')) and expr.endswith(("'", '"')):
            logger.debug(f"Detected string literal: {expr}")
            return expr, 'string'
        
        # 2. 检查数字字面量
        try:
            value = ExpressionParser._parse_number(expr)
            logger.debug(f"Parsed number: {value}")
            return value, 'number'
        except ValueError:
            logger.warning(f"Failed to parse number: {expr}")
        
        # 3. 处理表达式
        try:
            # 首先替换所有变量
            processed_expr = ExpressionParser._replace_variables(expr, enum_values, macro_values)
            logger.debug(f"After variable replacement: {processed_expr}")
            
            # 然后尝试计算表达式
            result = ExpressionParser._evaluate(processed_expr)
            logger.debug(f"After evaluation: {result}")
            
            if isinstance(result, (int, float)):
                logger.debug(f"Final result (number): {result}")
                return result, 'number'
            
            logger.debug(f"Final result (expression): {result}")
            return result, 'expression'
            
        except Exception as e:
            logger.error(f"Failed to parse expression: {expr}, error: {e}")
            return expr, 'expression'
    
    @staticmethod
    def _parse_number(expr):
        """解析数字字面量"""
        expr = expr.strip()
        
        try:
            # 十六进制
            if expr.startswith(('0x', '0X')):
                return int(expr.rstrip('ULul'), 16)
            # 二进制
            elif expr.startswith(('0b', '0B')):
                return int(expr.rstrip('ULul')[2:], 2)
            # 八进制
            elif expr.startswith('0') and len(expr) > 1 and expr[1].isdigit():
                return int(expr.rstrip('ULul'), 8)
            # 浮点数
            elif '.' in expr or 'e' in expr.lower():
                return float(expr.rstrip('fFlL'))
            # 整数
            else:
                return int(expr.rstrip('ULul'))
        except ValueError:
            raise ValueError(f"Invalid number format: {expr}")
    
    @staticmethod
    def _replace_variables(expr, enum_values=None, macro_values=None):
        """替换表达式中的变量引用"""
        if not expr:
            return expr
        
        logger.debug(f"--- Variable Replacement ---")
        logger.debug(f"Input: {expr}")
        
        # 标准化运算符
        expr = ' '.join(expr.split())  # 标准化空格
        for op in ['<<', '>>', '|', '&', '^', '~', '+', '-', '*', '/', '(', ')']:
            expr = expr.replace(op, f" {op} ")
        logger.debug(f"After operator normalization: {expr}")
        
        # 分割并处理每个标记
        tokens = [t for t in expr.split() if t]
        logger.debug(f"Tokens: {tokens}")
        processed_tokens = []
        
        for token in tokens:
            logger.debug(f"Processing token: {token}")
            # 保留运算符
            if token in ['<<', '>>', '|', '&', '^', '~', '+', '-', '*', '/', '(', ')']:
                logger.debug(f"Operator token: {token}")
                processed_tokens.append(token)
                continue
            
            # 替换变量
            value = None
            if enum_values and token in enum_values:
                value = enum_values[token]
                logger.debug(f"Found enum value: {token} = {value}")
            elif macro_values and token in macro_values:
                value = macro_values[token]
                logger.debug(f"Found macro value: {token} = {value}")
            
            if value is not None:
                if isinstance(value, (int, float)):
                    processed_tokens.append(str(value))
                    logger.debug(f"Added numeric value: {value}")
                else:
                    # 递归处理引用的值
                    result, _ = ExpressionParser.parse(str(value), enum_values, macro_values)
                    processed_tokens.append(str(result))
                    logger.debug(f"Added processed value: {result}")
            else:
                # 尝试解析为数字
                try:
                    value = ExpressionParser._parse_number(token)
                    processed_tokens.append(str(value))
                    logger.debug(f"Parsed as number: {value}")
                except ValueError:
                    processed_tokens.append(token)
                    logger.debug(f"Kept as is: {token}")
        
        result = ' '.join(processed_tokens)
        logger.debug(f"Final processed expression: {result}")
        return result
    
    @staticmethod
    def _evaluate(expr):
        """计算表达式的值"""
        try:
            logger.debug(f"--- Expression Evaluation ---")
            logger.debug(f"Input: {expr}")
            
            # 检查是否所有token都是数值或运算符
            tokens = expr.split()
            operators = {'<<', '>>', '|', '&', '^', '~', '+', '-', '*', '/', '(', ')'}
            logger.debug(f"Tokens: {tokens}")
            
            # 确保所有非运算符的token都是数字
            for token in tokens:
                if token not in operators:
                    try:
                        float(token)
                        logger.debug(f"Valid numeric token: {token}")
                    except ValueError:
                        logger.debug(f"Non-numeric token found: {token}")
                        return expr
            
            # 计算表达式
            result = eval(expr)
            logger.debug(f"Evaluation result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to evaluate expression: {expr}, error: {e}")
            return expr 
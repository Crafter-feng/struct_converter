import json
from pathlib import Path
import click
from logger_config import setup_logger
from tree_sitter import Language, Parser

logger = setup_logger('Utils')

class ParserUtils:
    """解析器工具类，提供通用功能"""
    
    @staticmethod
    def save_to_cache(data, cache_path=None):
        """保存数据到缓存文件
        
        Args:
            data: 要缓存的数据
            cache_path: 缓存文件路径，默认为 .cache/test_structs_cache.json
        """
        if cache_path is None:
            cache_path = Path('.cache/test_structs_cache.json')
        
        try:
            # 确保缓存目录存在
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存数据
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Cache saved to: {cache_path}")
        except Exception as e:
            logger.error(f"Failed to save cache: {str(e)}")
            raise
    
    @staticmethod
    def load_from_cache(cache_path=None):
        """从缓存文件加载数据
        
        Args:
            cache_path: 缓存文件路径，默认为 .cache/test_structs_cache.json
            
        Returns:
            dict: 缓存的数据，如果加载失败返回 None
        """
        if cache_path is None:
            cache_path = Path('.cache/test_structs_cache.json')
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                logger.debug(f"Loaded cache from: {cache_path}")
                return {
                    'struct_info': cache_data.get('struct_info', {}),
                    'typedef_types': cache_data.get('typedef_types', {}),
                    'struct_types': cache_data.get('struct_types', []),
                    'pointer_types': cache_data.get('pointer_types', {}),
                    'enum_types': cache_data.get('enum_types', {}),
                    'macro_definitions': cache_data.get('macro_definitions', {})
                }
        except FileNotFoundError:
            logger.warning(f"Cache file not found: {cache_path}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Invalid cache file format: {cache_path}")
            return None
        except Exception as e:
            logger.error(f"Failed to load cache: {str(e)}")
            return None

class OutputFormatter:
    """输出格式化工具类"""
    
    @staticmethod
    def format_field_info(field):
        """格式化字段信息
        
        Args:
            field: 字段信息字典或字符串
            
        Returns:
            str: 格式化后的字段信息
        """
        # 如果field是字符串，直接返回
        if isinstance(field, str):
            return field
            
        # 处理字典类型的字段信息
        if isinstance(field, dict):
            # 构建基本字段信息
            field_str = []
            
            # 添加类型信息
            type_str = field.get('type', 'unknown')
            if field.get('is_pointer'):
                type_str += '*'
            field_str.append(type_str)
            
            # 添加字段名
            name = field.get('name', 'unnamed')
            field_str.append(name)
            
            # 处理数组
            if field.get('array_size'):
                array_dims = field['array_size']
                if isinstance(array_dims, list):
                    for dim in array_dims:
                        field_str[-1] += f"[{dim}]"
                else:
                    field_str[-1] += f"[{array_dims}]"
            
            # 处理位域
            if field.get('bit_field') is not None:
                field_str[-1] += f" : {field['bit_field']}"
            
            # 处理函数指针
            if field.get('is_function_pointer'):
                return f"{type_str} (*{name})({', '.join(field.get('parameters', []))})"
            
            return ' '.join(field_str)
        
        # 如果不是字典也不是字符串，尝试转换为字符串
        return str(field)
    
    @staticmethod
    def format_var_info(var_data):
        """格式化变量信息
        
        Args:
            var_data: 变量信息字典
            
        Returns:
            str: 格式化后的变量信息
        """
        parts = []
        parts.append(var_data['name'])
        parts.append(f"类型: {var_data['type']}")
        
        if var_data.get('is_pointer'):
            parts.append("指针类型")
            if var_data.get('pointer_target'):
                parts.append(f"指向: {var_data['pointer_target']}")
        
        if var_data.get('array_size'):
            dims = 'x'.join(str(x) for x in var_data['array_size'])
            parts.append(f"数组维度: [{dims}]")
        
        if var_data.get('struct_type'):
            parts.append(f"结构体类型: {var_data['struct_type']}")
        
        return ' | '.join(parts)
    
    @staticmethod
    def simplify_var_info(var_info):
        """简化变量信息，只保留关键数据
        
        Args:
            var_info: 原始变量信息
        
        Returns:
            dict: 简化后的变量信息
        """
        simplified = {}
        
        # 合并所有变量
        all_vars = (var_info['variables'] + 
                   var_info['struct_vars'] + 
                   var_info['pointer_vars'] + 
                   var_info['array_vars'])
        
        # 提取每个变量的关键信息
        for var in all_vars:
            var_name = var['name']
            var_data = {
                'type': var['original_type']
            }
            
            # 只有数组类型才添加 array_size
            if var.get('array_size'):
                var_data['array_size'] = var['array_size']
            
            # 如果有值，添加 value
            if 'value' in var and var['value'] is not None:
                if (var.get('array_size') and 
                    var['original_type'] == 'char' and 
                    isinstance(var['value'], str)):
                    var_data['value'] = var['value']
                else:
                    var_data['value'] = var['value']
            
            # 如果是指针类型，在类型中添加 *
            if var.get('is_pointer'):
                var_data['type'] = f"{var_data['type']}*"
                if var.get('pointer_level', 1) > 1:
                    var_data['type'] += '*' * (var['pointer_level'] - 1)
            
            simplified[var_name] = var_data
        
        return simplified
    
    @staticmethod
    def print_struct_info(generator):
        """打印结构体信息
        
        Args:
            generator: 代码生成器实例
        """
        print("\n=== 结构体定义 ===")
        for struct_name, struct_info in generator.struct_info.items():
            print(f"\nstruct {struct_name} {{")
            
            # 获取字段列表，处理不同的数据结构
            if isinstance(struct_info, dict):
                fields = struct_info.get('fields', [])
            elif isinstance(struct_info, list):
                fields = struct_info
            else:
                fields = []
            
            logger.debug(f"Struct {struct_name} info: {json.dumps(struct_info, indent=2)}")
            logger.debug(f"Fields: {json.dumps(fields, indent=2)}")
            
            if not fields:
                print("    // 无字段")
            else:
                for field in fields:
                    try:
                        field_str = OutputFormatter.format_field_info(field)
                        print(f"    {field_str};")
                    except Exception as e:
                        logger.error(f"Error formatting field {field}: {str(e)}")
                        print(f"    // Error: {str(e)}")
            
            print("};")
    
    @staticmethod
    def print_text_output(result):
        """打印文本格式的输出到控制台
        
        Args:
            result: 解析结果字典
        """
        # 显示类型定义
        click.echo("=== 类型定义 ===")
        
        if result['types']['structs']:
            click.echo("\n结构体定义:")
            for struct_name, fields in result['types']['structs'].items():
                click.echo(f"\n结构体 {struct_name}:")
                for field in fields:
                    field_str = OutputFormatter.format_field_info(field)
                    click.echo(f"  - {field['name']}: {field_str}")
        
        if result['types']['typedefs']:
            click.echo("\n类型定义:")
            for typedef_name, typedef_type in result['types']['typedefs'].items():
                click.echo(f"  {typedef_name} -> {typedef_type}")
        
        if result['types']['enums']:
            click.echo("\n枚举定义:")
            for enum_name, enum_values in result['types']['enums'].items():
                click.echo(f"\n枚举 {enum_name}:")
                for name, value in enum_values.items():
                    click.echo(f"  {name} = {value}")
        
        if result['types']['macros']:
            click.echo("\n宏定义:")
            for macro_name, macro_value in result['types']['macros'].items():
                click.echo(f"  {macro_name} = {macro_value}")
        
        # 显示变量定义
        click.echo("\n=== 变量定义 ===")
        if result['variables']['variables']:
            click.echo("\n基本变量:")
            for var in result['variables']['variables']:
                click.echo(f"  - {OutputFormatter.format_var_info(var)}")
        
        if result['variables']['struct_vars']:
            click.echo("\n结构体变量:")
            for var in result['variables']['struct_vars']:
                click.echo(f"  - {OutputFormatter.format_var_info(var)}")
        
        if result['variables']['pointer_vars']:
            click.echo("\n指针变量:")
            for var in result['variables']['pointer_vars']:
                click.echo(f"  - {OutputFormatter.format_var_info(var)}")
        
        if result['variables']['array_vars']:
            click.echo("\n数组变量:")
            for var in result['variables']['array_vars']:
                click.echo(f"  - {OutputFormatter.format_var_info(var)}")

class FileWriter:
    """文件写入工具类"""
    
    @staticmethod
    def write_text_output(result, output_path):
        """将结果写入文本文件
        
        Args:
            result: 解析结果
            output_path: 输出文件路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # 写入类型定义
            f.write("=== 类型定义 ===\n")
            
            if result['types']['structs']:
                f.write("\n结构体定义:\n")
                for struct_name, fields in result['types']['structs'].items():
                    f.write(f"\n结构体 {struct_name}:\n")
                    for field in fields:
                        field_str = OutputFormatter.format_field_info(field)
                        f.write(f"  - {field['name']}: {field_str}\n")
            
            if result['types']['typedefs']:
                f.write("\n类型定义:\n")
                for typedef_name, typedef_type in result['types']['typedefs'].items():
                    f.write(f"  {typedef_name} -> {typedef_type}\n")
            
            if result['types']['enums']:
                f.write("\n枚举定义:\n")
                for enum_name, enum_values in result['types']['enums'].items():
                    f.write(f"\n枚举 {enum_name}:\n")
                    for name, value in enum_values.items():
                        f.write(f"  {name} = {value}\n")
            
            if result['types']['macros']:
                f.write("\n宏定义:\n")
                for macro_name, macro_value in result['types']['macros'].items():
                    f.write(f"  {macro_name} = {macro_value}\n")
            
            # 写入变量定义
            f.write("\n=== 变量定义 ===\n")
            FileWriter._write_variables(f, result['variables'])
    
    @staticmethod
    def _write_variables(f, var_info):
        """写入变量信息到文件
        
        Args:
            f: 文件对象
            var_info: 变量信息
        """
        if var_info['variables']:
            f.write("\n基本变量:\n")
            for var in var_info['variables']:
                f.write(f"  - {OutputFormatter.format_var_info(var)}\n")
        
        if var_info['struct_vars']:
            f.write("\n结构体变量:\n")
            for var in var_info['struct_vars']:
                f.write(f"  - {OutputFormatter.format_var_info(var)}\n")
        
        if var_info['pointer_vars']:
            f.write("\n指针变量:\n")
            for var in var_info['pointer_vars']:
                f.write(f"  - {OutputFormatter.format_var_info(var)}\n")
        
        if var_info['array_vars']:
            f.write("\n数组变量:\n")
            for var in var_info['array_vars']:
                f.write(f"  - {OutputFormatter.format_var_info(var)}\n") 

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
            
        logger.debug(f"\n=== Parsing Expression ===")
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
            pass
        
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
        
        logger.debug(f"\n--- Variable Replacement ---")
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
            logger.debug(f"\nProcessing token: {token}")
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
        logger.debug(f"\nFinal processed expression: {result}")
        return result
    
    @staticmethod
    def _evaluate(expr):
        """计算表达式的值"""
        try:
            logger.debug(f"\n--- Expression Evaluation ---")
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
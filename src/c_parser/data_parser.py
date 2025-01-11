from typing import Dict, Any, Optional, List
from pathlib import Path
from .type_manager import TypeManager
from utils.logger_config import setup_logger
import re
from .tree_sitter_parser import CTreeSitterParser

logger = setup_logger('CDataParser')

class CDataParser:
    """C数据解析器"""
    def __init__(self):
        self.type_manager = TypeManager()
        self.tree_sitter_parser = CTreeSitterParser()
        self.value_parsers = {
            'int': self._parse_int,
            'float': self._parse_float,
            'char': self._parse_char,
            'bool': self._parse_bool,
            'string': self._parse_string,
            'array': self._parse_array,
            'struct': self._parse_struct
        }
        
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """解析C源文件"""
        try:
            # 使用 tree-sitter 解析
            parse_result = self.tree_sitter_parser.parse_file(file_path)
            
            # 注册类型
            self._register_types(parse_result)
            
            return parse_result
            
        except Exception as e:
            logger.error(f"Failed to parse file {file_path}: {str(e)}")
            raise
            
    def _register_types(self, parse_result: Dict[str, Any]) -> None:
        """注册解析到的类型"""
        # 注册结构体
        for struct_name, struct_info in parse_result['structs'].items():
            self.type_manager.register_struct(struct_name, struct_info['fields'])
            
        # 注册枚举
        for enum_name, enum_info in parse_result['enums'].items():
            self.type_manager.register_enum(enum_name, enum_info['values'])
            
        # 注册类型别名
        for alias, original in parse_result['typedefs'].items():
            self.type_manager.type_aliases[alias] = original
        
    def _parse_int(self, value: str) -> int:
        """解析整数值"""
        try:
            if value.startswith('0x'):
                return int(value, 16)
            elif value.startswith('0'):
                return int(value, 8)
            return int(value)
        except ValueError as e:
            logger.error(f"Failed to parse int value {value}: {str(e)}")
            return 0
            
    def _parse_float(self, value: str) -> float:
        """解析浮点数值"""
        try:
            return float(value)
        except ValueError as e:
            logger.error(f"Failed to parse float value {value}: {str(e)}")
            return 0.0
            
    def _parse_char(self, value: str) -> str:
        """解析字符值"""
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        return value
        
    def _parse_bool(self, value: str) -> bool:
        """解析布尔值"""
        return value.lower() in ('true', '1', 'yes')
        
    def _parse_string(self, value: str) -> str:
        """解析字符串值"""
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        return value
        
    def _parse_array(self, value: str, elem_type: str) -> list:
        """解析数组值"""
        try:
            # 移除大括号并分割元素
            value = value.strip('{}')
            if not value:
                return []
            
            elements = []
            current = ''
            brace_count = 0
            
            # 处理嵌套数组和结构体
            for char in value + ',':
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                elif char == ',' and brace_count == 0:
                    elements.append(current.strip())
                    current = ''
                    continue
                current += char
            
            # 解析每个元素
            result = []
            for elem in elements:
                if elem_type in self.value_parsers:
                    result.append(self.value_parsers[elem_type](elem))
                else:
                    logger.warning(f"Unknown element type: {elem_type}")
                    result.append(None)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse array: {str(e)}")
            return []
        
    def _parse_struct(self, value: str, struct_type: str) -> dict:
        """解析结构体值"""
        try:
            # 获取结构体信息
            struct_info = self.type_manager.get_type_info(struct_type)
            if not struct_info or 'fields' not in struct_info:
                logger.error(f"Invalid struct type: {struct_type}")
                return {}
            
            # 移除大括号
            value = value.strip('{}')
            if not value:
                return {}
            
            # 解析字段值
            result = {}
            fields = struct_info['fields']
            values = self._split_struct_values(value)
            
            for field, field_value in zip(fields, values):
                field_name = field['name']
                field_type = field['type']
                
                if field.get('array_size'):
                    # 处理数组字段
                    result[field_name] = self._parse_array(field_value, field_type)
                elif self.type_manager.is_struct_type(field_type):
                    # 处理嵌套结构体
                    result[field_name] = self._parse_struct(field_value, field_type)
                elif field_type in self.value_parsers:
                    # 处理基本类型
                    result[field_name] = self.value_parsers[field_type](field_value)
                else:
                    logger.warning(f"Unknown field type: {field_type}")
                    result[field_name] = None
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse struct: {str(e)}")
            return {}
        
    def _split_struct_values(self, value: str) -> list:
        """分割结构体值"""
        values = []
        current = ''
        brace_count = 0
        
        for char in value + ',':
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            elif char == ',' and brace_count == 0:
                values.append(current.strip())
                current = ''
                continue
            current += char
        
        return values 
        
    def _parse_enum_definition(self, stmt: str) -> Optional[Dict]:
        """解析枚举定义"""
        try:
            # 提取枚举名称
            name_match = re.search(r'typedef enum\s+(\w+)', stmt)
            if not name_match:
                return None
            
            enum_name = name_match.group(1)
            
            # 提取枚举值
            values_str = re.search(r'{(.*)}', stmt, re.DOTALL)
            if not values_str:
                return None
            
            values = []
            current_value = 0
            
            for value in values_str.group(1).split(','):
                value = value.strip()
                if not value:
                    continue
                
                # 解析枚举项
                if '=' in value:
                    name, val = value.split('=')
                    name = name.strip()
                    val = val.strip()
                    try:
                        current_value = self._parse_int(val)
                    except ValueError:
                        logger.warning(f"Invalid enum value: {val}")
                        continue
                else:
                    name = value.strip()
                    
                values.append({
                    'name': name,
                    'value': current_value
                })
                current_value += 1
                
            return {
                'name': enum_name,
                'values': values
            }
            
        except Exception as e:
            logger.error(f"Failed to parse enum definition: {str(e)}")
            return None
        
    def _parse_typedef(self, stmt: str) -> Optional[Dict[str, str]]:
        """解析类型别名定义"""
        try:
            # 移除typedef关键字
            stmt = stmt.replace('typedef', '').strip()
            
            # 分割类型和别名
            parts = stmt.split()
            if len(parts) < 2:
                return None
            
            alias = parts[-1].rstrip(';')
            original = ' '.join(parts[:-1])
            
            return {alias: original}
            
        except Exception as e:
            logger.error(f"Failed to parse typedef: {str(e)}")
            return None
        
    def _parse_variable_definition(self, stmt: str) -> Optional[Dict[str, Dict]]:
        """解析变量定义"""
        try:
            # 分割类型和初始化部分
            parts = stmt.split('=')
            if len(parts) != 2:
                return None
            
            decl = parts[0].strip()
            value = parts[1].strip().rstrip(';')
            
            # 解析类型和变量名
            decl_parts = decl.split()
            if len(decl_parts) < 2:
                return None
            
            var_name = decl_parts[-1]
            var_type = ' '.join(decl_parts[:-1])
            
            # 处理数组声明
            array_match = re.search(r'(\w+)\[(.*)\]', var_name)
            if array_match:
                var_name = array_match.group(1)
                array_dims = [int(d) for d in array_match.group(2).split('][')]
                return {
                    var_name: {
                        'type': var_type,
                        'array_size': array_dims,
                        'value': self._parse_array(value, var_type)
                    }
                }
            
            # 处理普通变量
            if var_type in self.value_parsers:
                return {
                    var_name: {
                        'type': var_type,
                        'value': self.value_parsers[var_type](value)
                    }
                }
            
            # 处理结构体变量
            if self.type_manager.is_struct_type(var_type):
                return {
                    var_name: {
                        'type': var_type,
                        'value': self._parse_struct(value, var_type)
                    }
                }
            
            logger.warning(f"Unknown variable type: {var_type}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse variable definition: {str(e)}")
            return None 
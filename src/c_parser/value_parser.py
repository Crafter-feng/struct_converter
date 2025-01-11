from typing import Any, List, Dict, Union, Optional
from utils.logger_config import setup_logger
from .expression_parser import ExpressionParser

logger = setup_logger('CValueParser')

class CValueParser:
    """C语言值解析器"""
    
    def __init__(self, type_manager=None):
        self.type_manager = type_manager
        self.expr_parser = ExpressionParser()
        
    def parse_value(self, value: str, type_name: str) -> Any:
        """解析值"""
        try:
            if not value:
                return None
                
            # 获取实际类型
            real_type = self.type_manager.get_real_type(type_name) if self.type_manager else type_name
            
            # 处理数组类型
            if self.type_manager and self.type_manager.is_array_type(real_type):
                return self._parse_array(value, real_type.replace('[]', ''))
                
            # 处理结构体类型
            if self.type_manager and self.type_manager.is_struct_type(real_type):
                return self._parse_struct(value, real_type)
                
            # 处理枚举类型
            if self.type_manager and self.type_manager.is_enum_type(real_type):
                return self._parse_enum(value, real_type)
                
            # 使用表达式解析器解析值
            value, _ = ExpressionParser.parse(
                value,
                self.type_manager.get_enum_info() if self.type_manager else {},
                self.type_manager.get_macro_definition() if self.type_manager else {}
            )
            
            return value
            
        except Exception as e:
            logger.error(f"Failed to parse value {value} as {type_name}: {str(e)}")
            return None
            
    def _parse_array(self, value: str, elem_type: str) -> List[Any]:
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
            return [self.parse_value(elem, elem_type) for elem in elements]
            
        except Exception as e:
            logger.error(f"Failed to parse array: {str(e)}")
            return []
            
    def _parse_struct(self, value: str, struct_type: str) -> Dict[str, Any]:
        """解析结构体值"""
        try:
            if not self.type_manager:
                return {}
                
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
                result[field_name] = self.parse_value(field_value, field_type)
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse struct: {str(e)}")
            return {}
            
    def _parse_enum(self, value: str, enum_type: str) -> Optional[int]:
        """解析枚举值"""
        try:
            if not self.type_manager:
                return None
                
            # 如果是数字，直接返回
            try:
                return int(value)
            except ValueError:
                pass
                
            # 尝试从枚举定义中查找值
            enum_info = self.type_manager.get_enum_info()
            if enum_type in enum_info:
                for enum_value in enum_info[enum_type]:
                    if enum_value['name'] == value:
                        return enum_value['value']
                        
            # 尝试从宏定义中查找值
            macro_defs = self.type_manager.get_macro_definition()
            if value in macro_defs:
                return macro_defs[value]
                
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse enum value {value}: {str(e)}")
            return None
            
    def _split_struct_values(self, value: str) -> List[str]:
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
from dataclasses import dataclass
from typing import List, Dict, Any
from pathlib import Path

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]

class ConfigValidator:
    """配置验证器"""
    def __init__(self):
        self.required_fields = {
            'output_dir': str,
            'header_file': str,
            'source_file': str
        }
        
        self.optional_fields = {
            'cache_ttl': int,
            'indent_size': int,
            'add_comments': bool,
            'generate_tests': bool,
            'max_line_length': int,
            'pretty_print': bool,
            'sort_keys': bool,
            'escape_unicode': bool
        }
        
    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """验证配置"""
        errors = []
        
        # 检查必需字段
        for field, field_type in self.required_fields.items():
            if field not in config:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(config[field], field_type):
                errors.append(f"Invalid type for {field}: expected {field_type.__name__}")
                
        # 检查可选字段
        for field, field_type in self.optional_fields.items():
            if field in config and not isinstance(config[field], field_type):
                errors.append(f"Invalid type for {field}: expected {field_type.__name__}")
                
        # 检查输出目录
        if 'output_dir' in config:
            output_dir = Path(config['output_dir'])
            if output_dir.exists() and not output_dir.is_dir():
                errors.append("output_dir exists but is not a directory")
                
        return ValidationResult(not bool(errors), errors) 
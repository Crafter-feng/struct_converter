from typing import Dict, Any, List, Optional
from .base_config import BaseConfig

class GeneratorConfig(BaseConfig):
    """代码生成器配置"""
    
    def __init__(self, config_file: Optional[str] = None):
        super().__init__(config_file)
        self.output_dir: str = "generated"
        self.template_dir: str = "templates"
        self.enable_field_encryption: bool = False
        self.field_encryption_salt: str = "default_salt"
        self.excluded_types: List[str] = []
        self.type_mappings: Dict[str, str] = {}
        
    def _validate_config(self) -> None:
        """验证生成器配置"""
        required_fields = ['output_dir', 'template_dir']
        for field in required_fields:
            if field not in self.config_data:
                raise ValueError(f"Missing required field: {field}")
                
    def _process_config(self) -> None:
        """处理生成器配置"""
        self.output_dir = self.config_data.get('output_dir', self.output_dir)
        self.template_dir = self.config_data.get('template_dir', self.template_dir)
        self.enable_field_encryption = self.config_data.get('enable_field_encryption', False)
        self.field_encryption_salt = self.config_data.get('field_encryption_salt', 'default_salt')
        self.excluded_types = self.config_data.get('excluded_types', [])
        self.type_mappings = self.config_data.get('type_mappings', {})
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'output_dir': self.output_dir,
            'template_dir': self.template_dir,
            'enable_field_encryption': self.enable_field_encryption,
            'field_encryption_salt': self.field_encryption_salt,
            'excluded_types': self.excluded_types,
            'type_mappings': self.type_mappings
        } 
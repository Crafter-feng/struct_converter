from typing import Dict, Any, Optional, List
from .base_config import BaseConfig

class ParserConfig(BaseConfig):
    """解析器配置"""
    
    def __init__(self, config_file: Optional[str] = None):
        super().__init__(config_file)
        self.include_paths: List[str] = []
        self.macro_definitions: Dict[str, str] = {}
        self.enable_doc_comments: bool = True
        self.enable_location_tracking: bool = True
        
    def _validate_config(self) -> None:
        """验证解析器配置"""
        if 'include_paths' in self.config_data:
            if not isinstance(self.config_data['include_paths'], list):
                raise ValueError("include_paths must be a list")
                
    def _process_config(self) -> None:
        """处理解析器配置"""
        self.include_paths = self.config_data.get('include_paths', [])
        self.macro_definitions = self.config_data.get('macro_definitions', {})
        self.enable_doc_comments = self.config_data.get('enable_doc_comments', True)
        self.enable_location_tracking = self.config_data.get('enable_location_tracking', True) 
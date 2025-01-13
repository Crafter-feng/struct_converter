import os
from typing import Dict, Any, Optional
from pathlib import Path
from .base_config import BaseConfig

class TreeSitterConfig(BaseConfig):
    """Tree-sitter配置"""
    
    def __init__(self, config_file: Optional[str] = None):
        super().__init__(config_file)
        self.c_parser_path: str = self._get_default_c_parser_path()
        self.build_dir: str = "build"
        self.library_file: str = "c.so"
        self.language_name: str = "c"
        
    def _get_default_c_parser_path(self) -> str:
        """获取默认的tree-sitter-c路径"""
        # 优先从环境变量获取
        if path := os.environ.get('TREE_SITTER_C_PATH'):
            return path
            
        # 其次从项目根目录查找
        root_dir = Path(__file__).parent.parent.parent
        default_path = str(root_dir / 'tree-sitter-c')
        return default_path
        
    def _validate_config(self) -> None:
        """验证tree-sitter配置"""
        if 'c_parser_path' in self.config_data:
            path = Path(self.config_data['c_parser_path'])
            if not path.exists():
                raise ValueError(f"Tree-sitter C parser path not found: {path}")
                
    def _process_config(self) -> None:
        """处理tree-sitter配置"""
        self.c_parser_path = self.config_data.get('c_parser_path', self.c_parser_path)
        self.build_dir = self.config_data.get('build_dir', self.build_dir)
        self.library_file = self.config_data.get('library_file', self.library_file)
        self.language_name = self.config_data.get('language_name', self.language_name)
        
    def get_library_path(self) -> str:
        """获取编译后的库文件路径"""
        return str(Path(self.build_dir) / self.library_file) 
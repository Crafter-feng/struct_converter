from pathlib import Path
from typing import Optional, List, Dict, Any
from .base import BaseGenerator
from utils.logger_config import setup_logger

logger = setup_logger('StructGenerator')

class StructGenerator(BaseGenerator):
    """结构体代码生成器"""
    
    def __init__(self, type_info: dict):
        super().__init__(type_info)
        self.struct_info = type_info.get('struct_info', {})
        
    def generate(self, output_dir: Path, struct_names: Optional[List[str]] = None) -> bool:
        """生成代码
        
        Args:
            output_dir: 输出目录
            struct_names: 要处理的结构体名称列表，None表示处理所有
            
        Returns:
            bool: 是否成功
        """
        try:
            if not self.validate_type_info():
                return False
                
            self._create_directories(output_dir)
            
            # 确定要处理的结构体
            if struct_names is None:
                struct_names = sorted(self.struct_info.keys())
                
            logger.info(f"Processing structs: {struct_names}")
            
            # 生成代码
            for struct_name in struct_names:
                if not self._generate_struct_code(struct_name, output_dir):
                    return False
                    
            # 生成最终文件
            self._generate_final_files(output_dir)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate code: {str(e)}")
            return False
            
    def _generate_struct_code(self, struct_name: str, output_dir: Path) -> bool:
        """生成单个结构体的代码"""
        try:
            # 获取结构体信息
            struct_data = self.struct_info.get(struct_name)
            if not struct_data:
                logger.error(f"Struct not found: {struct_name}")
                return False
                
            # 生成代码
            header_decl = self._generate_header_declarations(struct_name)
            impl_code = self._generate_implementation_functions(struct_name, struct_data['fields'])
            deps = self._get_nested_structs(struct_name)
            enable_macro = f"ENABLE_{self._generate_struct_markers(struct_name)}_CONVERTER"
            
            # 更新缓存
            self.cache.update_cache(
                struct_name,
                output_dir / ".cache",
                header_decl,
                impl_code,
                deps,
                enable_macro
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate code for {struct_name}: {str(e)}")
            return False 
from pathlib import Path
import json
import time
from typing import Dict, Any, Optional
from utils.logger_config import setup_logger

logger = setup_logger('StructCache')

class StructCache:
    """结构体代码缓存管理器"""
    
    def __init__(self):
        self.header_decls: Dict[str, list] = {}  # 头文件声明缓存
        self.impl_codes: Dict[str, list] = {}    # 实现代码缓存
        self.dependencies: Dict[str, list] = {}  # 依赖关系缓存
        self.enable_macros: Dict[str, str] = {}  # 启用宏缓存
        
    def update_cache(self, struct_name: str, cache_dir: Path, 
                    header_decl: list, impl_code: list,
                    deps: list, enable_macro: str) -> None:
        """更新缓存内容"""
        try:
            # 更新内存缓存
            self.header_decls[struct_name] = header_decl
            self.impl_codes[struct_name] = impl_code
            self.dependencies[struct_name] = deps
            self.enable_macros[struct_name] = enable_macro
            
            # 更新文件缓存
            cache_file = cache_dir / f"{struct_name}.cache"
            cache_data = {
                'header_decl': header_decl,
                'impl_code': impl_code,
                'dependencies': deps,
                'enable_macro': enable_macro,
                'timestamp': time.time()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
                
            logger.debug(f"Updated cache for struct: {struct_name}")
            
        except Exception as e:
            logger.error(f"Failed to update cache for {struct_name}: {str(e)}")
            raise
            
    def get_cached_data(self, struct_name: str, cache_dir: Path) -> Optional[Dict[str, Any]]:
        """获取缓存的数据"""
        try:
            cache_file = cache_dir / f"{struct_name}.cache"
            if not cache_file.exists():
                return None
                
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # 检查缓存是否过期
            if time.time() - cache_data['timestamp'] > 3600:  # 1小时过期
                logger.debug(f"Cache expired for struct: {struct_name}")
                return None
                
            return cache_data
            
        except Exception as e:
            logger.error(f"Failed to read cache for {struct_name}: {str(e)}")
            return None
            
    def clear_cache(self, cache_dir: Path) -> None:
        """清除所有缓存"""
        try:
            for cache_file in cache_dir.glob("*.cache"):
                cache_file.unlink()
            
            self.header_decls.clear()
            self.impl_codes.clear()
            self.dependencies.clear()
            self.enable_macros.clear()
            
            logger.info("Cleared all caches")
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
            raise 
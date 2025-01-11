import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger_config import get_logger
from struct_converter.core.exceptions import CacheError

logger = get_logger("CacheManager")

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = '.cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def get_cache_key(self, file_path: str, content: bytes) -> str:
        """生成缓存键
        
        使用文件路径和内容的哈希作为缓存键，确保内容变化时能检测到
        """
        try:
            path_hash = hashlib.sha256(str(file_path).encode()).hexdigest()[:8]
            content_hash = hashlib.sha256(content).hexdigest()[:8]
            return f"{path_hash}_{content_hash}"
        except Exception as e:
            raise CacheError(f"Failed to generate cache key: {e}")
            
    def get_cache_path(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.json"
        
    def load(self, file_path: str, content: bytes) -> Optional[Dict[str, Any]]:
        """加载缓存数据"""
        try:
            cache_key = self.get_cache_key(file_path, content)
            cache_path = self.get_cache_path(cache_key)
            
            if not cache_path.exists():
                return None
                
            # 检查缓存文件是否比源文件新
            source_path = Path(file_path)
            if source_path.exists() and cache_path.stat().st_mtime < source_path.stat().st_mtime:
                logger.debug(f"Cache for {file_path} is outdated")
                return None
                
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                logger.debug(f"Loaded cache for {file_path}")
                return cache_data
                
        except Exception as e:
            logger.warning(f"Failed to load cache for {file_path}: {e}")
            return None
            
    def save(self, file_path: str, content: bytes, data: Dict[str, Any]) -> None:
        """保存缓存数据"""
        try:
            cache_key = self.get_cache_key(file_path, content)
            cache_path = self.get_cache_path(cache_key)
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                logger.debug(f"Saved cache for {file_path}")
                
        except Exception as e:
            logger.error(f"Failed to save cache for {file_path}: {e}")
            raise CacheError(f"Failed to save cache: {e}")
            
    def clear(self, file_path: Optional[str] = None) -> None:
        """清除缓存
        
        Args:
            file_path: 如果指定，只清除该文件的缓存；否则清除所有缓存
        """
        try:
            if file_path:
                # 清除特定文件的缓存
                for cache_file in self.cache_dir.glob("*.json"):
                    if file_path in cache_file.read_text():
                        cache_file.unlink()
                        logger.debug(f"Cleared cache for {file_path}")
            else:
                # 清除所有缓存
                for cache_file in self.cache_dir.glob("*.json"):
                    cache_file.unlink()
                logger.debug("Cleared all cache")
                
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            raise CacheError(f"Failed to clear cache: {e}")
            
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            return {
                'cache_dir': str(self.cache_dir),
                'file_count': len(cache_files),
                'total_size': total_size,
                'files': [
                    {
                        'name': f.name,
                        'size': f.stat().st_size,
                        'mtime': f.stat().st_mtime
                    }
                    for f in cache_files
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache info: {e}")
            raise CacheError(f"Failed to get cache info: {e}") 
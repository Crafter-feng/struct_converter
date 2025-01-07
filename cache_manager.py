from pathlib import Path
from logger_config import setup_logger
from utils import ParserUtils
import json

logger = setup_logger('CacheManager')

class CacheManager:
    """缓存管理器，处理文件解析结果的缓存"""
    
    def __init__(self, cache_dir=None):
        """初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录路径，默认为 .cache
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path('.cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_path(self, file_path, cache_name=None):
        """获取缓存文件路径
        
        Args:
            file_path: 源文件路径
            cache_name: 自定义缓存名称
            
        Returns:
            Path: 缓存文件路径
        """
        if cache_name:
            return self.cache_dir / f"{cache_name}.json"
        return self.cache_dir / f"{Path(file_path).name}.json"
    
    def is_header_file(self, file_path):
        """检查是否是头文件"""
        return str(file_path).lower().endswith(('.h', '.hpp', '.hxx'))
    
    def load_header_caches(self, specific_headers=None):
        """加载头文件缓存"""
        logger.debug("Loading header caches")
        if specific_headers:
            logger.debug(f"Loading specific headers: {specific_headers}")
        else:
            logger.debug("Loading all header caches")
        
        merged_types = {
            'typedef_types': {},
            'struct_types': [],
            'union_types': [],
            'pointer_types': {},
            'struct_info': {},
            'union_info': {},
            'enum_types': {},
            'macro_definitions': {}
        }
        
        # 获取所有缓存文件
        cache_files = list(self.cache_dir.glob('*.json'))
        
        for cache_file in cache_files:
            # 检查是否是头文件缓存
            original_name = cache_file.stem + '.h'  # 假设原始文件是.h
            if specific_headers:
                # 只加载指定的头文件缓存
                if not any(Path(h).name == original_name for h in specific_headers):
                    continue
            else:
                # 如果没有指定头文件，则检查文件名是否看起来像头文件
                if not self.is_header_file(original_name):
                    continue
            
            logger.debug(f"Loading cache from: {cache_file}")
            cache_data = ParserUtils.load_from_cache(cache_file)
            
            if cache_data:
                # 合并类型信息
                for key, value in cache_data.items():
                    if key == 'struct_types':
                        # 对于列表类型，使用set去重
                        merged_types[key] = list(set(merged_types[key] + value))
                    elif isinstance(value, dict):
                        merged_types[key].update(value)
                    elif isinstance(value, list):
                        merged_types[key].extend(value)
                    else:
                        merged_types[key] = value
                logger.debug(f"Merged types from {cache_file}")
                logger.debug(f"Current merged types: {json.dumps(merged_types, indent=2)}")
        
        return merged_types
    
    def load_cache(self, file_path, cache_name=None, force=False):
        """加载缓存
        
        Args:
            file_path: 源文件路径
            cache_name: 自定义缓存名称
            force: 是否强制忽略缓存
            
        Returns:
            tuple: (cache_data, cache_path)
                - cache_data: 缓存数据，如果没有找到或强制忽略则为None
                - cache_path: 缓存文件路径
        """
        cache_path = self.get_cache_path(file_path, cache_name)
        
        if not force and cache_path.exists():
            cache_data = ParserUtils.load_from_cache(cache_path)
            if cache_data:
                logger.info(f"Using cached data from {cache_path}")
                return cache_data, cache_path
            else:
                logger.warning(f"Invalid cache file: {cache_path}")
        
        if cache_name and not force:
            logger.info(f"Cache '{cache_name}' not found or invalid, need to regenerate")
        elif force:
            logger.info("Forced reparse requested")
        
        return None, cache_path
    
    def save_cache(self, data, cache_path):
        """保存缓存
        
        Args:
            data: 要缓存的数据
            cache_path: 缓存文件路径
        """
        ParserUtils.save_to_cache(data, cache_path)
        logger.info(f"Saved data to cache: {cache_path}")
    
    def clear_cache(self):
        """清除所有缓存"""
        import shutil
        
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            logger.info("Cache directory cleared")
        
        self.cache_dir.mkdir(parents=True) 
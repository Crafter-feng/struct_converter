from pathlib import Path
from utils.logger_config import setup_logger
import json

logger = setup_logger('CacheManager')

class CacheFileUtils:
    """解析器工具类，提供通用功能"""
    
    @staticmethod
    def save_to_cache(data, cache_path=None):
        """保存数据到缓存文件
        
        Args:
            data: 要缓存的数据
            cache_path: 缓存文件路径，默认为 .cache/test_structs_cache.json
        """
        if cache_path is None:
            cache_path = Path('.cache/test_structs_cache.json')
        
        try:
            # 确保缓存目录存在
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存数据
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Cache saved to: {cache_path}")
        except Exception as e:
            logger.error(f"Failed to save cache: {str(e)}")
            raise
    
    @staticmethod
    def load_from_cache(cache_path=None):
        """从缓存文件加载数据
        
        Args:
            cache_path: 缓存文件路径，默认为 .cache/test_cache.json
            
        Returns:
            dict: 缓存的数据，如果加载失败返回 None
        """
        if cache_path is None:
            cache_path = Path('.cache/test_cache.json')
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                logger.debug(f"Loaded cache from: {cache_path}")
                if cache_data.get('types'):
                    return cache_data.get('types')
                else:
                    return cache_data
        except FileNotFoundError:
            logger.warning(f"Cache file not found: {cache_path}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Invalid cache file format: {cache_path}")
            return None
        except Exception as e:
            logger.error(f"Failed to load cache: {str(e)}")
            return None
        

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
        
        # 初始化合并类型的数据结构
        merged_types = {
            'typedef_types': {},      # 字典类型
            'struct_types': set(),    # 集合类型
            'union_types': set(),     # 集合类型
            'pointer_types': set(),   # 集合类型
            'struct_info': {},        # 字典类型
            'union_info': {},         # 字典类型
            'enum_types': {},         # 字典类型
            'enum_info': {},          # 字典类型
            'macro_definitions': {}   # 字典类型
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
            cache_data = CacheFileUtils.load_from_cache(cache_file)
            
            if cache_data:
                # 合并类型信息
                for key, value in cache_data.items():
                    if key not in merged_types:
                        logger.warning(f"Unexpected key in cache data: {key}")
                        continue
                        
                    if key in ['struct_types', 'union_types', 'pointer_types']:
                        # 对于集合类型，使用 update
                        if isinstance(value, (list, set)):
                            merged_types[key].update(value)
                        else:
                            merged_types[key].add(value)
                    elif isinstance(merged_types[key], dict):
                        # 对于字典类型，使用 update
                        if isinstance(value, dict):
                            merged_types[key].update(value)
                        else:
                            logger.warning(f"Unexpected value type for {key}: {type(value)}")
                    else:
                        merged_types[key] = value
                        
                logger.debug(f"Merged types from {cache_file}")
                
                # 输出调试信息
                debug_types = {
                    k: list(v) if isinstance(v, set) else v 
                    for k, v in merged_types.items()
                }
                logger.debug(f"Current merged types: {json.dumps(debug_types, indent=2)}")
        
        # 转换集合为列表并返回结果
        result = {
            'typedef_types': merged_types['typedef_types'],
            'struct_types': list(merged_types['struct_types']),
            'union_types': list(merged_types['union_types']),
            'pointer_types': list(merged_types['pointer_types']),
            'struct_info': merged_types['struct_info'],
            'union_info': merged_types['union_info'],
            'enum_types': merged_types['enum_types'],
            'enum_info': merged_types['enum_info'],
            'macro_definitions': merged_types['macro_definitions']
        }
        
        return result
    
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
            cache_data = CacheFileUtils.load_from_cache(cache_path)
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
        CacheFileUtils.save_to_cache(data, cache_path)
        logger.info(f"Saved data to cache: {cache_path}")
    
    def clear_cache(self):
        """清除所有缓存"""
        import shutil
        
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            logger.info("Cache directory cleared")
        
        self.cache_dir.mkdir(parents=True) 
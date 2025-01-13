from pathlib import Path
from utils.logger import logger 
from utils.cache_manager import CacheManager
from .type_parser import CTypeParser
from .data_parser import CDataParser
from .type_manager import TypeManager
import json

__all__ = ['CParser', 'TypeManager', 'CTypeParser', 'CDataParser']



class CParser:
    """C语言解析器，负责解析头文件和源文件"""
    
    def __init__(self, cache_dir=None):
        """初始化解析器
        
        Args:
            cache_dir: 缓存目录路径，默认为 .cache
        """
        logger.info("Initializing CParser")
        
        # 设置缓存目录
        self.cache_dir = Path(cache_dir) if cache_dir else Path('.cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化解析器
        self.type_parser = CTypeParser()
        self.data_parser = None  # 延迟初始化
        
        # 初始化类型信息，按文件名索引
        self._type_info = {}
        
        self.cache_manager = CacheManager(cache_dir)
    
    def get_type_info(self, source_file=None):
                    # 加载所有头文件缓存
        type_info = self.cache_manager.load_header_caches()
        logger.debug("Loaded all header caches")
        
        return type_info
    
    def parse_declarations(self, header_file, use_cache=True, ref_headers=None):
        """解析文件里面的类型定义
        
        Args:
            header_file: 头文件路径
            use_cache: 是否使用缓存（仅用于引用的头文件）
            ref_headers: 引用的头文件列表，如果提供则加载这些头文件的类型信息
            
        Returns:
            dict: 类型信息字典
        """
        header_path = Path(header_file)
        logger.info(f"Parsing header file: {header_path}")
        
        # 加载引用的头文件类型信息
        if ref_headers:
            ref_types = self.cache_manager.load_type_info(ref_headers)
            if ref_types:
                self.type_parser = CTypeParser(ref_types)
        
        # 直接解析当前头文件
        type_info = self.type_parser.parse_declarations(header_file)
        logger.debug(f"Parsed type info: {json.dumps(type_info, indent=2)}")
        
        if not type_info.get('struct_info'):
            logger.warning("No struct info found in parsed result")
        
        # 更新类型信息
        file_key = str(header_path.resolve())
        self._type_info[file_key] = type_info
        
        # 保存缓存
        cache_path = self.cache_manager.get_cache_path(header_path)
        self.cache_manager.save_cache(type_info, cache_path)
        
        return self.get_type_info()
    
    def parse_global_variables(self, source_file, header_files=None, cache_name=None, force=False):
        """解析源文件"""
        source_path = Path(source_file)
        logger.info(f"Parsing source file: {source_path}")
        
        # 加载头文件类型信息
        if header_files:
            # 加载指定的头文件缓存
            type_info = self.cache_manager.load_header_caches(header_files)
            logger.debug(f"Loaded specified header caches: {header_files}")
        else:
            # 加载所有头文件缓存
            type_info = self.cache_manager.load_header_caches()
            logger.debug("Loaded all header caches")
        
        # 打印加载的类型信息
        logger.debug("Loaded type info:")
        logger.debug(f"Typedefs: {json.dumps(type_info.get('typedef_types', {}), indent=2)}")
        logger.debug(f"Structs: {json.dumps(type_info.get('struct_info', {}), indent=2)}")
        
        # 解析源文件
        if not type_info or not type_info.get('struct_info'):
            logger.warning("No type definitions available. Parse header files first.")
        
        # 重新初始化DataParser，确保使用最新的类型信息
        self.data_parser = CDataParser(type_info)
        
        result = self.data_parser.parse_global_variables(source_file)
        
        # 确保结果包含正确的格式
        if 'types' not in result:
            result = {
                'types': result,
                'variables': {}
            }
        
        # 更新类型信息
        self._type_info[str(source_path.resolve())] = result['types']
        
        # 保存缓存
        cache_path = self.cache_manager.get_cache_path(source_path, cache_name)
        self.cache_manager.save_cache(result, cache_path)
        
        return result
    
    def clear_cache(self):
        """清除缓存"""
        import shutil
        
        # 清除缓存目录
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            logger.info("Cache directory cleared")
        
        # 重建缓存目录
        self.cache_dir.mkdir(parents=True)
        
        # 重置内存中的缓存
        self._type_info = {}

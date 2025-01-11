import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# 日志配置
LOG_DIR = 'logs'
LOG_FILE = 'parser.log'
LOG_PATH = Path(LOG_DIR) / LOG_FILE

def setup_logger(name):
    """设置日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 获取日志记录器
    logger = logging.getLogger(name)
    
    # 如果已经配置过，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    logger.setLevel(logging.DEBUG)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    try:
        # 确保日志目录存在
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # 检查是否是第一个记录器
        is_first_logger = not any(
            isinstance(handler, logging.FileHandler) 
            for logger in logging.root.manager.loggerDict.values()
            for handler in getattr(logger, 'handlers', [])
        )
        
        # 如果是第一个记录器，清除或创建日志文件
        if is_first_logger:
            # 备份旧的日志文件（如果存在）
            # if LOG_PATH.exists():
            #     backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            #     backup_path = LOG_PATH.parent / f'parser_{backup_time}.log'
            #     try:
            #         LOG_PATH.rename(backup_path)
            #     except Exception as e:
            #         print(f"Warning: Failed to backup old log file: {e}")
            
            # 创建新的日志文件
            try:
                with open(LOG_PATH, 'w', encoding='utf-8') as f:
                    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"=== Log started at {start_time} ===\n\n")
            except Exception as e:
                print(f"Warning: Failed to create new log file: {e}")
        
        # 创建文件处理器
        file_handler = logging.FileHandler(LOG_PATH, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 记录初始化成功
        if is_first_logger:
            logger.info(f"Logging initialized: {LOG_PATH}")
        logger.debug(f"Logger '{name}' configured successfully")
        
    except Exception as e:
        print(f"Error setting up logger: {str(e)}")
        # 如果文件处理器创建失败，至少确保有控制台输出
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.warning(f"Falling back to console-only logging due to error: {str(e)}")
    
    return logger 
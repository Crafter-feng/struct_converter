from loguru import logger
import sys
from pathlib import Path
from typing import Optional

def setup_logger(log_file: Optional[str] = None, level: str = "INFO"):
    """设置日志配置
    
    Args:
        log_file: 日志文件路径，如果为None则只输出到控制台
        level: 日志级别，默认INFO
    """
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台处理器
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            str(log_path),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
                   "{name}:{function}:{line} - {message}",
            level=level,
            rotation="1 day",    # 每天轮换
            retention="30 days", # 保留30天
            compression="zip"    # 压缩旧日志
        )
    
    return logger

# 创建默认logger
logger = setup_logger() 
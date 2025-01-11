from pathlib import Path
from loguru import logger
import sys

def setup_logger(name: str, level: str = "INFO") -> logger:
    """设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别，默认为 "INFO"
        
    Returns:
        loguru.logger: 配置好的日志记录器
    """
    # 移除默认的处理器
    logger.remove()
    
    # 创建日志目录
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        filter=lambda record: record["extra"].get("name", "") == name,
        level=level,
        colorize=True
    )
    
    # 添加文件处理器
    logger.add(
        log_dir / f"{name}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
               "{name}:{function}:{line} | {message}",
        filter=lambda record: record["extra"].get("name", "") == name,
        level=level,
        rotation="1 day",    # 每天轮换一次
        retention="30 days", # 保留30天
        compression="zip",   # 压缩旧日志
        encoding="utf-8"
    )
    
    # 创建带有名称的上下文记录器
    logger_with_context = logger.bind(name=name)
    
    return logger_with_context

def get_logger(name: str) -> logger:
    """获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        loguru.logger: 日志记录器
    """
    return logger.bind(name=name) 
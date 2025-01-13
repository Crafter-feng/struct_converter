import pytest
from utils.logger import logger 

class TestLogger:
    """日志工具测试"""
    
    def test_logger_setup(self):
        """测试日志器设置"""
        
        assert logger is not None
        assert logger.name == "test"
        
    def test_log_levels(self):
        """测试日志级别"""
        
        
        # 测试各个日志级别
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message") 
        
    def test_logger_context(self):
        """测试日志上下文"""
        
        with logger.contextualize(task="test_task"):
            logger.info("Test message with context")
        
    def test_logger_formatting(self):
        """测试日志格式化"""
        
        logger.info("Test message with {}", "formatting") 
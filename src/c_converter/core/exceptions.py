from loguru import logger

logger = logger.bind(name="Exceptions")

class StructConverterError(Exception):
    """基础异常类"""
    def __init__(self, message: str):
        super().__init__(message)
        logger.error(message)

class ValidationError(StructConverterError):
    """验证错误"""
    pass

class ConfigError(StructConverterError):
    """配置错误"""
    pass

class ParserError(StructConverterError):
    """解析错误"""
    pass

class GenerationError(StructConverterError):
    """代码生成错误"""
    pass

class EncryptionError(StructConverterError):
    """加密错误"""
    pass

# 别名
ParseError = ParserError
CodeGenerationError = GenerationError 
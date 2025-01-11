class StructConverterError(Exception):
    """结构体转换器基础异常类"""
    pass

class ValidationError(StructConverterError):
    """验证错误"""
    pass

class ConfigError(StructConverterError):
    """配置错误"""
    pass

class GenerationError(StructConverterError):
    """代码生成错误"""
    pass

class EncryptionError(StructConverterError):
    """加密错误"""
    pass

class ParserError(StructConverterError):
    """解析错误"""
    pass

class NameConflictError(ValidationError):
    """名称冲突错误"""
    pass

class InvalidNameError(ValidationError):
    """无效名称错误"""
    pass

class PrefixConflictError(ValidationError):
    """前缀冲突错误"""
    pass 
"""
异常定义模块
"""


class UncdError(Exception):
    """基础异常类"""
    pass


class InvalidUNCPathError(UncdError):
    """无效UNC路径异常"""
    pass


class MappingNotFoundError(UncdError):
    """映射关系未找到异常"""
    pass


class ConfigError(UncdError):
    """配置文件错误异常"""
    pass


class DirectoryNotFoundError(UncdError):
    """目录不存在异常"""
    pass

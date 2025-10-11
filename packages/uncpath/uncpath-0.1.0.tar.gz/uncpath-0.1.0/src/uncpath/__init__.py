"""
uncpath-py: A Python package for UNC path operations
"""

__version__ = "0.1.0"

# 导入核心功能
from .parser import UNCResolver, UNCPath
from .config import ConfigManager
from .mapper import PathMapper
from .exceptions import (
    UncdError,
    InvalidUNCPathError,
    MappingNotFoundError,
    ConfigError,
    DirectoryNotFoundError
)

# 向后兼容的函数
def is_unc_path(path: str) -> bool:
    """
    Check if a given path is a UNC path.
    
    UNC paths start with \\\\ or // or smb://
    
    Args:
        path: The path to check
        
    Returns:
        True if the path is a UNC path, False otherwise
    """
    if not path:
        return False
    return path.startswith(r"\\") or path.startswith("//") or path.startswith("smb://")


def normalize_unc_path(path: str) -> str:
    """
    Normalize a UNC path to use forward slashes.
    
    Args:
        path: The UNC path to normalize
        
    Returns:
        The normalized path
    """
    if not path:
        return path
    return path.replace("\\", "/")


def resolve_unc_path(path: str) -> str:
    """
    便捷函数，直接解析UNC路径并返回本地路径
    
    Args:
        path: UNC路径
        
    Returns:
        str: 映射后的本地路径
        
    Raises:
        InvalidUNCPathError: 当路径格式无效时
        MappingNotFoundError: 当找不到映射时
    """
    resolver = UNCResolver()
    config_manager = ConfigManager()
    mapper = PathMapper(config_manager)
    
    # 解析UNC路径
    unc_path = resolver.parse_unc_path(path)
    
    # 映射到本地路径
    return mapper.map_to_local(unc_path)


def get_config_path() -> str:
    """
    获取默认配置文件路径
    
    Returns:
        str: 配置文件路径
    """
    config_manager = ConfigManager()
    return str(config_manager.config_path)


def create_default_config(path: str) -> None:
    """
    创建默认配置文件
    
    Args:
        path: 配置文件路径
    """
    config_manager = ConfigManager(path)
    config_manager._create_default_config()


__all__ = [
    # 版本信息
    "__version__",
    
    # 核心类
    "UNCResolver",
    "UNCPath", 
    "ConfigManager",
    "PathMapper",
    
    # 异常类
    "UncdError",
    "InvalidUNCPathError",
    "MappingNotFoundError", 
    "ConfigError",
    "DirectoryNotFoundError",
    
    # 向后兼容函数
    "is_unc_path",
    "normalize_unc_path",
    
    # 便捷函数
    "resolve_unc_path",
    "get_config_path",
    "create_default_config",
]

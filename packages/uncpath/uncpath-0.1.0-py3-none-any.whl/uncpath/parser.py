"""
UNC路径解析器模块
"""
import re
from dataclasses import dataclass
from typing import Optional

from .exceptions import InvalidUNCPathError


@dataclass
class UNCPath:
    """UNC路径数据结构"""
    protocol: str  # 'smb', 'unc', 'windows'
    host: str       # 主机名或IP
    share: str      # 共享名
    path: str       # 路径部分
    original: str   # 原始路径
    
    def to_string(self) -> str:
        """将UNCPath对象转换为字符串"""
        return f"//{self.host}/{self.share}{self.path}"


class UNCResolver:
    """UNC路径解析器"""
    
    def parse_unc_path(self, path: str) -> UNCPath:
        """
        解析UNC路径并返回结构化的路径对象
        
        Args:
            path: 要解析的UNC路径
            
        Returns:
            UNCPath: 解析后的路径对象
            
        Raises:
            InvalidUNCPathError: 当路径格式无效时
        """
        if not path:
            raise InvalidUNCPathError("路径不能为空")
        
        # Windows UNC格式: \\host\share\path
        if path.startswith(r'\\'):
            # 移除开头的两个反斜杠（实际上是4个字符）
            remaining = path[2:]
            parts = remaining.split('\\')
            # 过滤空字符串
            parts = [p for p in parts if p]
            if len(parts) >= 2:
                host = parts[0]
                share = parts[1]
                path_part = '\\' + '\\'.join(parts[2:]) if len(parts) > 2 else ''
                return UNCPath(
                    protocol='windows',
                    host=host,
                    share=share,
                    path=path_part,
                    original=path
                )
        
        # Unix UNC格式: //host/share/path
        elif path.startswith('//'):
            # 移除开头的两个斜杠
            remaining = path[2:]
            parts = remaining.split('/')
            if len(parts) >= 2:
                host = parts[0]
                share = parts[1]
                path_part = '/' + '/'.join(parts[2:]) if len(parts) > 2 else ''
                return UNCPath(
                    protocol='unix',
                    host=host,
                    share=share,
                    path=path_part,
                    original=path
                )
        
        # SMB协议格式: smb://host/share/path
        elif path.startswith('smb://'):
            # 移除开头的smb://
            remaining = path[6:]
            parts = remaining.split('/')
            if len(parts) >= 2:
                host = parts[0]
                share = parts[1]
                path_part = '/' + '/'.join(parts[2:]) if len(parts) > 2 else ''
                return UNCPath(
                    protocol='smb',
                    host=host,
                    share=share,
                    path=path_part,
                    original=path
                )
        
        raise InvalidUNCPathError(f"无效的UNC路径格式: {path}")
    
    def normalize_unc_path(self, path: str) -> str:
        """
        标准化UNC路径格式
        
        Args:
            path: 要标准化的路径
            
        Returns:
            str: 标准化后的路径
        """
        try:
            unc_path = self.parse_unc_path(path)
            return unc_path.to_string()
        except InvalidUNCPathError:
            return path
    
    def is_valid_unc_path(self, path: str) -> bool:
        """
        验证路径是否为有效的UNC路径
        
        Args:
            path: 要验证的路径
            
        Returns:
            bool: 是否为有效的UNC路径
        """
        try:
            self.parse_unc_path(path)
            return True
        except InvalidUNCPathError:
            return False
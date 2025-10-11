"""
路径映射器模块
"""
import re
from typing import Optional, Dict, Any
from .parser import UNCPath
from .config import ConfigManager
from .exceptions import MappingNotFoundError


class PathMapper:
    """路径映射器"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self._mapping_cache: Optional[Dict[str, str]] = None
    
    def map_to_local(self, unc_path: UNCPath) -> str:
        """
        将UNC路径映射到本地路径
        
        Args:
            unc_path: UNC路径对象
            
        Returns:
            str: 映射后的本地路径
            
        Raises:
            MappingNotFoundError: 当找不到映射关系时
        """
        # 首先尝试精确映射
        exact_key = f"{unc_path.host}/{unc_path.share}"
        local_path = self._find_exact_mapping(exact_key)
        if local_path:
            return self._build_local_path(local_path, unc_path)
        
        # 尝试通配符映射
        local_path = self._find_wildcard_mapping(unc_path.host, unc_path.share)
        if local_path:
            return self._build_local_path(local_path, unc_path)
        
        # 尝试默认映射
        local_path = self._get_default_mapping(unc_path.host, unc_path.share)
        if local_path:
            return self._build_local_path(local_path, unc_path)
        
        raise MappingNotFoundError(f"未找到映射关系: {exact_key}")
    
    def _find_exact_mapping(self, key: str) -> Optional[str]:
        """查找精确映射"""
        mappings = self._get_mappings()
        return mappings.get(key)
    
    def _find_wildcard_mapping(self, host: str, share: str) -> Optional[str]:
        """查找通配符映射"""
        mappings = self._get_mappings()
        
        for pattern, local_path in mappings.items():
            if '*' in pattern:
                # 将模式转换为正则表达式
                regex_pattern = pattern.replace('*', '.*')
                regex_pattern = regex_pattern.replace('{host}', host)
                regex_pattern = regex_pattern.replace('{share}', share)
                
                if re.match(regex_pattern, f"{host}/{share}"):
                    return local_path
        
        return None
    
    def _get_default_mapping(self, host: str, share: str) -> Optional[str]:
        """获取默认映射"""
        defaults = self.config_manager.get_defaults()
        base_path = defaults.get('base_path', '/mnt/smb')
        
        return f"{base_path}/{host}/{share}"
    
    def _build_local_path(self, base_path: str, unc_path: UNCPath) -> str:
        """
        构建完整的本地路径
        
        Args:
            base_path: 基础路径
            unc_path: UNC路径对象
            
        Returns:
            str: 完整的本地路径
        """
        # 替换占位符
        local_path = base_path.replace('{host}', unc_path.host)
        local_path = local_path.replace('{share}', unc_path.share)
        
        # 添加路径部分
        if unc_path.path and unc_path.path != '/':
            local_path += unc_path.path
        
        return local_path
    
    def _get_mappings(self) -> Dict[str, str]:
        """获取映射关系"""
        if self._mapping_cache is None:
            self._mapping_cache = self.config_manager.get_mappings()
        return self._mapping_cache
    
    def find_mapping(self, host: str, share: str) -> Optional[str]:
        """
        查找host/share的映射关系
        
        Args:
            host: 主机名或IP
            share: 共享名称
            
        Returns:
            Optional[str]: 映射的本地路径，如果未找到则返回None
        """
        try:
            unc_path = UNCPath(
                protocol='unc',
                host=host,
                share=share,
                path='/',
                original=f"//{host}/{share}"
            )
            return self.map_to_local(unc_path)
        except MappingNotFoundError:
            return None

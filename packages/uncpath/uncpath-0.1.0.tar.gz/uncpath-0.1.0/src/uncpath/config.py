"""
配置管理模块
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

from .exceptions import ConfigError


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path or self._get_default_config_path())
        self._config_cache: Optional[Dict[str, Any]] = None
    
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        config_dir = Path.home() / '.config' / 'uncpath'
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / 'config.yaml')
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            Dict[str, Any]: 配置字典
            
        Raises:
            ConfigError: 当配置文件格式错误时
        """
        if self._config_cache is not None:
            return self._config_cache
        
        if not self.config_path.exists():
            self._create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.suffix == '.yaml':
                    try:
                        import yaml
                        config = yaml.safe_load(f)
                    except ImportError:
                        raise ConfigError("需要安装PyYAML来支持YAML配置文件")
                else:
                    config = json.load(f)
            
            self._validate_config(config)
            self._config_cache = config
            return config
            
        except Exception as e:
            raise ConfigError(f"加载配置文件失败: {e}")
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """
        保存配置到文件
        
        Args:
            config: 要保存的配置字典
            
        Raises:
            ConfigError: 当保存失败时
        """
        try:
            self._validate_config(config)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.suffix == '.yaml':
                    try:
                        import yaml
                        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                    except ImportError:
                        raise ConfigError("需要安装PyYAML来支持YAML配置文件")
                else:
                    json.dump(config, f, indent=2, ensure_ascii=False)
            
            self._config_cache = config
            
        except Exception as e:
            raise ConfigError(f"保存配置文件失败: {e}")
    
    def _create_default_config(self) -> None:
        """创建默认配置文件"""
        default_config = {
            'version': '1.0',
            'mappings': {},
            'defaults': {
                'base_path': '/mnt/smb',
                'auto_create': False,
                'create_mode': '0755'
            },
            'aliases': {}
        }
        self.save_config(default_config)
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        验证配置文件格式
        
        Args:
            config: 配置字典
            
        Raises:
            ConfigError: 当配置格式错误时
        """
        required_keys = ['version', 'mappings', 'defaults']
        for key in required_keys:
            if key not in config:
                raise ConfigError(f"配置文件缺少必需的键: {key}")
        
        if not isinstance(config['mappings'], dict):
            raise ConfigError("mappings必须是字典类型")
        
        if not isinstance(config['defaults'], dict):
            raise ConfigError("defaults必须是字典类型")
    
    def get_mappings(self) -> Dict[str, str]:
        """
        获取所有映射关系
        
        Returns:
            Dict[str, str]: 映射关系字典
        """
        config = self.load_config()
        return config.get('mappings', {})
    
    def add_mapping(self, key: str, value: str) -> None:
        """
        添加新的映射关系
        
        Args:
            key: UNC路径键 (格式: "host/share")
            value: 本地路径值
        """
        config = self.load_config()
        config['mappings'][key] = value
        self.save_config(config)
    
    def remove_mapping(self, key: str) -> None:
        """
        删除映射关系
        
        Args:
            key: 要删除的映射键
        """
        config = self.load_config()
        if key in config['mappings']:
            del config['mappings'][key]
            self.save_config(config)
    
    def get_defaults(self) -> Dict[str, Any]:
        """
        获取默认设置
        
        Returns:
            Dict[str, Any]: 默认设置字典
        """
        config = self.load_config()
        return config.get('defaults', {})
    
    def get_aliases(self) -> Dict[str, str]:
        """
        获取别名设置
        
        Returns:
            Dict[str, str]: 别名字典
        """
        config = self.load_config()
        return config.get('aliases', {})

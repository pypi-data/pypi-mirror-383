"""
命令行接口模块
"""
import os
import sys
import argparse
from pathlib import Path
from typing import Optional

from .parser import UNCResolver, InvalidUNCPathError
from .config import ConfigManager, ConfigError
from .mapper import PathMapper, MappingNotFoundError
from .exceptions import DirectoryNotFoundError


class UncdCLI:
    """命令行接口"""
    
    def __init__(self):
        self.resolver = UNCResolver()
        self.config_manager = ConfigManager()
        self.mapper = PathMapper(self.config_manager)
    
    def run(self, args: Optional[list] = None) -> int:
        """
        运行CLI
        
        Args:
            args: 命令行参数列表
            
        Returns:
            int: 退出码
        """
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)
        
        try:
            if parsed_args.init_config:
                return self._init_config()
            elif parsed_args.list_mappings:
                return self._list_mappings()
            elif parsed_args.add_mapping:
                return self._add_mapping(parsed_args.add_mapping)
            elif parsed_args.remove_mapping:
                return self._remove_mapping(parsed_args.remove_mapping)
            elif parsed_args.validate_config:
                return self._validate_config()
            elif parsed_args.unc_path:
                return self._change_directory(parsed_args.unc_path, parsed_args.path_only)
            else:
                parser.print_help()
                return 1
                
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            return 1
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """创建参数解析器"""
        parser = argparse.ArgumentParser(
            description="UNC路径转换工具",
            prog="uncd"
        )
        
        parser.add_argument(
            'unc_path',
            nargs='?',
            help='UNC路径'
        )
        
        parser.add_argument(
            '--path-only',
            action='store_true',
            help='只输出路径，不切换目录'
        )
        
        parser.add_argument(
            '--config',
            help='指定配置文件路径'
        )
        
        parser.add_argument(
            '--init-config',
            action='store_true',
            help='创建默认配置文件'
        )
        
        parser.add_argument(
            '--list-mappings',
            action='store_true',
            help='列出所有映射关系'
        )
        
        parser.add_argument(
            '--add-mapping',
            nargs=2,
            metavar=('KEY', 'VALUE'),
            help='添加映射关系'
        )
        
        parser.add_argument(
            '--remove-mapping',
            help='删除映射关系'
        )
        
        parser.add_argument(
            '--validate-config',
            action='store_true',
            help='验证配置文件'
        )
        
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s 0.1.0'
        )
        
        return parser
    
    def _change_directory(self, unc_path: str, path_only: bool) -> int:
        """
        切换目录
        
        Args:
            unc_path: UNC路径
            path_only: 是否只输出路径
            
        Returns:
            int: 退出码
        """
        try:
            # 解析UNC路径
            parsed_path = self.resolver.parse_unc_path(unc_path)
            
            # 映射到本地路径
            local_path = self.mapper.map_to_local(parsed_path)
            
            if path_only:
                print(local_path)
                return 0
            
            # 检查目录是否存在
            if not Path(local_path).exists():
                raise DirectoryNotFoundError(f"目录不存在: {local_path}")
            
            # 切换目录
            os.chdir(local_path)
            print(f"切换到: {local_path}")
            return 0
            
        except InvalidUNCPathError as e:
            print(f"无效的UNC路径: {e}", file=sys.stderr)
            return 1
        except MappingNotFoundError as e:
            print(f"未找到映射关系: {e}", file=sys.stderr)
            return 1
        except DirectoryNotFoundError as e:
            print(f"目录不存在: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"未知错误: {e}", file=sys.stderr)
            return 1
    
    def _init_config(self) -> int:
        """初始化配置文件"""
        try:
            self.config_manager._create_default_config()
            print(f"已创建默认配置文件: {self.config_manager.config_path}")
            return 0
        except Exception as e:
            print(f"创建配置文件失败: {e}", file=sys.stderr)
            return 1
    
    def _list_mappings(self) -> int:
        """列出所有映射关系"""
        try:
            mappings = self.config_manager.get_mappings()
            if not mappings:
                print("没有配置映射关系")
                return 0
            
            print("映射关系:")
            for key, value in mappings.items():
                print(f"  {key} -> {value}")
            return 0
        except Exception as e:
            print(f"列出映射关系失败: {e}", file=sys.stderr)
            return 1
    
    def _add_mapping(self, mapping_args: list) -> int:
        """添加映射关系"""
        try:
            key, value = mapping_args
            self.config_manager.add_mapping(key, value)
            print(f"已添加映射关系: {key} -> {value}")
            return 0
        except Exception as e:
            print(f"添加映射关系失败: {e}", file=sys.stderr)
            return 1
    
    def _remove_mapping(self, key: str) -> int:
        """删除映射关系"""
        try:
            self.config_manager.remove_mapping(key)
            print(f"已删除映射关系: {key}")
            return 0
        except Exception as e:
            print(f"删除映射关系失败: {e}", file=sys.stderr)
            return 1
    
    def _validate_config(self) -> int:
        """验证配置文件"""
        try:
            config = self.config_manager.load_config()
            print("配置文件格式正确")
            print(f"版本: {config.get('version', 'unknown')}")
            print(f"映射数量: {len(config.get('mappings', {}))}")
            return 0
        except Exception as e:
            print(f"配置文件验证失败: {e}", file=sys.stderr)
            return 1


def main():
    """主函数"""
    cli = UncdCLI()
    sys.exit(cli.run())

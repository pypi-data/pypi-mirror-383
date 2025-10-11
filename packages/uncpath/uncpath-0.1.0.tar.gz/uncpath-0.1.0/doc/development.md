# 开发指南

## 开发环境设置

### 1. 克隆项目

```bash
git clone https://github.com/JiashuaiXu/uncpath-py.git
cd uncpath-py
```

### 2. 安装开发依赖

```bash
# 使用uv（推荐）
uv sync --dev

# 或使用pip
pip install -e ".[dev]"
```

### 3. 开发依赖

项目使用以下开发工具：

- **pytest**: 测试框架
- **black**: 代码格式化
- **flake8**: 代码检查
- **mypy**: 类型检查
- **pre-commit**: Git钩子

### 4. 预提交钩子

```bash
# 安装pre-commit钩子
pre-commit install

# 手动运行所有钩子
pre-commit run --all-files
```

## 项目结构

```
uncpath-py/
├── src/
│   └── uncpath/
│       ├── __init__.py          # 核心API
│       ├── cli.py               # 命令行接口
│       ├── config.py            # 配置管理
│       ├── parser.py            # 路径解析
│       ├── mapper.py            # 路径映射
│       └── exceptions.py        # 异常定义
├── tests/
│   ├── test_uncpath.py          # 核心功能测试
│   ├── test_cli.py              # CLI测试
│   ├── test_config.py           # 配置管理测试
│   ├── test_parser.py           # 解析器测试
│   └── test_mapper.py           # 映射器测试
├── doc/                         # 文档目录
├── pyproject.toml              # 项目配置
└── README.md                    # 项目说明
```

## 核心模块开发

### 1. 路径解析器 (parser.py)

#### 设计目标
- 支持多种UNC路径格式
- 提供统一的解析接口
- 错误处理和验证

#### 实现要点

```python
import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class UNCPath:
    """UNC路径数据结构"""
    protocol: str
    host: str
    share: str
    path: str
    original: str
    
    def to_string(self) -> str:
        """转换为标准格式字符串"""
        return f"//{self.host}/{self.share}{self.path}"

class UNCResolver:
    """UNC路径解析器"""
    
    # 支持的正则表达式
    PATTERNS = {
        'windows': re.compile(r'^\\\\([^\\]+)\\([^\\]+)(.*)$'),
        'unix': re.compile(r'^//([^/]+)/([^/]+)(.*)$'),
        'smb': re.compile(r'^smb://([^/]+)/([^/]+)(.*)$')
    }
    
    def parse_unc_path(self, path: str) -> UNCPath:
        """解析UNC路径"""
        if not path:
            raise InvalidUNCPathError("路径不能为空")
        
        # 尝试匹配各种格式
        for protocol, pattern in self.PATTERNS.items():
            match = pattern.match(path)
            if match:
                host, share, path_part = match.groups()
                return UNCPath(
                    protocol=protocol,
                    host=host,
                    share=share,
                    path=path_part or '/',
                    original=path
                )
        
        raise InvalidUNCPathError(f"无效的UNC路径格式: {path}")
    
    def normalize_unc_path(self, path: str) -> str:
        """标准化UNC路径"""
        try:
            unc_path = self.parse_unc_path(path)
            return unc_path.to_string()
        except InvalidUNCPathError:
            return path
    
    def is_valid_unc_path(self, path: str) -> bool:
        """验证UNC路径格式"""
        try:
            self.parse_unc_path(path)
            return True
        except InvalidUNCPathError:
            return False
```

### 2. 配置管理器 (config.py)

#### 设计目标
- 支持YAML和JSON格式
- 提供默认配置
- 配置验证和错误处理

#### 实现要点

```python
import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional

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
        """加载配置文件"""
        if self._config_cache is not None:
            return self._config_cache
        
        if not self.config_path.exists():
            self._create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.suffix == '.yaml':
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
            
            self._validate_config(config)
            self._config_cache = config
            return config
            
        except Exception as e:
            raise ConfigError(f"加载配置文件失败: {e}")
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """保存配置文件"""
        try:
            self._validate_config(config)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.suffix == '.yaml':
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
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
        """验证配置文件格式"""
        required_keys = ['version', 'mappings', 'defaults']
        for key in required_keys:
            if key not in config:
                raise ConfigError(f"配置文件缺少必需的键: {key}")
        
        if not isinstance(config['mappings'], dict):
            raise ConfigError("mappings必须是字典类型")
        
        if not isinstance(config['defaults'], dict):
            raise ConfigError("defaults必须是字典类型")
```

### 3. 路径映射器 (mapper.py)

#### 设计目标
- 支持精确映射和通配符映射
- 支持占位符替换
- 高效的映射查找

#### 实现要点

```python
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
        """将UNC路径映射到本地路径"""
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
        config = self.config_manager.load_config()
        defaults = config.get('defaults', {})
        base_path = defaults.get('base_path', '/mnt/smb')
        
        return f"{base_path}/{host}/{share}"
    
    def _build_local_path(self, base_path: str, unc_path: UNCPath) -> str:
        """构建完整的本地路径"""
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
            config = self.config_manager.load_config()
            self._mapping_cache = config.get('mappings', {})
        return self._mapping_cache
```

### 4. 命令行接口 (cli.py)

#### 设计目标
- 简洁的命令行接口
- 完整的错误处理
- 友好的用户提示

#### 实现要点

```python
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
        """运行CLI"""
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
        """切换目录"""
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
```

## 测试开发

### 1. 测试结构

```python
# tests/test_parser.py
import pytest
from uncpath.parser import UNCResolver, UNCPath, InvalidUNCPathError

class TestUNCResolver:
    """测试UNC路径解析器"""
    
    def setup_method(self):
        self.resolver = UNCResolver()
    
    def test_parse_windows_unc_path(self):
        """测试Windows UNC路径解析"""
        path = r"\\192.168.10.172\sambaShare\folder\file.txt"
        result = self.resolver.parse_unc_path(path)
        
        assert result.protocol == "windows"
        assert result.host == "192.168.10.172"
        assert result.share == "sambaShare"
        assert result.path == "/folder/file.txt"
        assert result.original == path
    
    def test_parse_unix_unc_path(self):
        """测试Unix UNC路径解析"""
        path = "//server/share/folder/file.txt"
        result = self.resolver.parse_unc_path(path)
        
        assert result.protocol == "unix"
        assert result.host == "server"
        assert result.share == "share"
        assert result.path == "/folder/file.txt"
    
    def test_parse_smb_path(self):
        """测试SMB协议路径解析"""
        path = "smb://server/share/folder/file.txt"
        result = self.resolver.parse_unc_path(path)
        
        assert result.protocol == "smb"
        assert result.host == "server"
        assert result.share == "share"
        assert result.path == "/folder/file.txt"
    
    def test_invalid_path(self):
        """测试无效路径"""
        with pytest.raises(InvalidUNCPathError):
            self.resolver.parse_unc_path("invalid/path")
        
        with pytest.raises(InvalidUNCPathError):
            self.resolver.parse_unc_path("")
    
    def test_normalize_unc_path(self):
        """测试路径标准化"""
        result = self.resolver.normalize_unc_path(r"\\server\share\file.txt")
        assert result == "//server/share/file.txt"
    
    def test_is_valid_unc_path(self):
        """测试路径验证"""
        assert self.resolver.is_valid_unc_path(r"\\server\share\file.txt") is True
        assert self.resolver.is_valid_unc_path("//server/share/file.txt") is True
        assert self.resolver.is_valid_unc_path("smb://server/share/file.txt") is True
        assert self.resolver.is_valid_unc_path("C:\\Users\\file.txt") is False
        assert self.resolver.is_valid_unc_path("/home/user/file.txt") is False
```

### 2. 集成测试

```python
# tests/test_integration.py
import pytest
import tempfile
import os
from pathlib import Path
from uncpath.cli import UncdCLI
from uncpath.config import ConfigManager

class TestIntegration:
    """集成测试"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "config.yaml")
        self.cli = UncdCLI()
        self.cli.config_manager = ConfigManager(self.config_path)
        self.cli.mapper = PathMapper(self.cli.config_manager)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        # 创建测试配置
        config = {
            'version': '1.0',
            'mappings': {
                '192.168.10.172/sambaShare': '/tmp/test_samba'
            },
            'defaults': {
                'base_path': '/tmp/smb',
                'auto_create': True
            },
            'aliases': {}
        }
        self.cli.config_manager.save_config(config)
        
        # 创建测试目录
        os.makedirs('/tmp/test_samba', exist_ok=True)
        
        # 测试路径解析和映射
        unc_path = r"\\192.168.10.172\sambaShare\folder"
        parsed_path = self.cli.resolver.parse_unc_path(unc_path)
        local_path = self.cli.mapper.map_to_local(parsed_path)
        
        assert local_path == "/tmp/test_samba/folder"
    
    def test_cli_commands(self):
        """测试CLI命令"""
        # 测试初始化配置
        result = self.cli.run(['--init-config'])
        assert result == 0
        
        # 测试列出映射
        result = self.cli.run(['--list-mappings'])
        assert result == 0
        
        # 测试添加映射
        result = self.cli.run(['--add-mapping', 'server/test', '/tmp/test'])
        assert result == 0
```

### 3. 性能测试

```python
# tests/test_performance.py
import pytest
import time
from uncpath.parser import UNCResolver

class TestPerformance:
    """性能测试"""
    
    def setup_method(self):
        self.resolver = UNCResolver()
    
    def test_parse_performance(self):
        """测试解析性能"""
        test_paths = [
            r"\\192.168.10.172\sambaShare\folder\file.txt",
            "//server/share/folder/file.txt",
            "smb://server/share/folder/file.txt"
        ] * 1000
        
        start_time = time.time()
        for path in test_paths:
            self.resolver.parse_unc_path(path)
        end_time = time.time()
        
        # 应该在1秒内完成1000次解析
        assert end_time - start_time < 1.0
    
    def test_memory_usage(self):
        """测试内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 执行大量操作
        for i in range(10000):
            self.resolver.parse_unc_path(f"//server{i}/share/file.txt")
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 内存增长应该小于10MB
        assert memory_increase < 10 * 1024 * 1024
```

## 代码质量

### 1. 代码格式化

使用 `black` 进行代码格式化：

```bash
# 格式化所有Python文件
black src/ tests/

# 检查格式
black --check src/ tests/
```

### 2. 代码检查

使用 `flake8` 进行代码检查：

```bash
# 检查代码质量
flake8 src/ tests/
```

### 3. 类型检查

使用 `mypy` 进行类型检查：

```bash
# 类型检查
mypy src/
```

### 4. 测试覆盖率

使用 `pytest-cov` 检查测试覆盖率：

```bash
# 运行测试并生成覆盖率报告
pytest --cov=src/uncpath --cov-report=html
```

## 发布流程

### 1. 版本管理

使用语义化版本号：

```bash
# 更新版本号
# pyproject.toml: version = "0.1.1"

# 提交更改
git add pyproject.toml
git commit -m "Bump version to 0.1.1"
git tag v0.1.1
git push origin main --tags
```

### 2. 构建包

```bash
# 构建分发包
uv build

# 检查构建的包
twine check dist/*
```

### 3. 发布到PyPI

```bash
# 发布到PyPI
twine upload dist/*
```

### 4. 创建GitHub发布

```bash
# 创建GitHub发布
gh release create v0.1.1 \
  --title "Release v0.1.1" \
  --notes "新增CLI工具和配置管理功能" \
  dist/*
```

## 贡献指南

### 1. 开发流程

1. Fork 项目
2. 创建功能分支
3. 编写代码和测试
4. 运行测试和检查
5. 提交Pull Request

### 2. 代码规范

- 遵循PEP 8编码规范
- 使用类型注解
- 编写完整的文档字符串
- 保持测试覆盖率>90%

### 3. 提交信息

使用规范的提交信息格式：

```
类型(范围): 简短描述

详细描述

相关Issue: #123
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `test`: 测试相关
- `refactor`: 重构
- `perf`: 性能优化

### 4. Pull Request

- 提供清晰的描述
- 包含相关的测试
- 更新文档
- 确保CI通过

# uncpath-py

[![CI/CD Pipeline](https://github.com/JiashuaiXu/uncpath-py/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/JiashuaiXu/uncpath-py/actions/workflows/ci-cd.yml)
[![PyPI version](https://badge.fury.io/py/uncpath-py.svg)](https://pypi.org/project/uncpath-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个用于 UNC（通用命名约定）路径操作的 Python 包，支持将 Windows/SMB 的 UNC 路径一键转换为 Linux 本地挂载路径。

## ✨ 功能特性

### 🔍 UNC路径解析
- **多格式支持**：Windows UNC (`\\host\share\path`)、Unix UNC (`//host/share/path`)、SMB协议 (`smb://host/share/path`)
- **智能解析**：自动识别路径格式并提取主机、共享、路径信息
- **标准化**：统一转换为标准格式

### ⚙️ 配置管理
- **YAML支持**：使用PyYAML处理配置文件
- **自动配置**：首次使用时自动创建默认配置文件
- **映射管理**：支持添加、删除、列出映射关系
- **配置验证**：自动验证配置文件格式

### 🗺️ 路径映射
- **精确映射**：host/share到本地路径的直接映射
- **通配符映射**：支持`*`通配符和`{host}`、`{share}`占位符
- **默认映射**：当找不到映射时使用默认规则
- **智能查找**：按优先级查找映射关系

### 💻 命令行工具
- **uncd命令**：完整的命令行接口
- **路径转换**：直接切换目录或输出路径
- **配置管理**：命令行配置映射关系
- **帮助信息**：完整的帮助和版本信息

## 📦 安装

```bash
pip install uncpath-py
```

## 🚀 快速开始

### 1. 初始化配置

```bash
# 创建默认配置文件
uncd --init-config
```

### 2. 添加映射关系

```bash
# 添加精确映射
uncd --add-mapping "192.168.10.172/sambaShare" "/opt/samba"

# 添加通配符映射
uncd --add-mapping "192.168.*/samba*" "/mnt/smb/{host}/{share}"
```

### 3. 使用路径转换

```bash
# 切换到映射的目录
uncd \\192.168.10.172\sambaShare\folder

# 只输出路径，不切换目录
uncd --path-only \\192.168.10.172\sambaShare\folder
# 输出: /opt/samba\folder
```

## 📖 详细使用

### 命令行使用

```bash
# 基本用法
uncd <UNC_PATH>                    # 切换到映射的目录
uncd --path-only <UNC_PATH>        # 只输出路径

# 配置管理
uncd --init-config                 # 创建默认配置文件
uncd --list-mappings              # 列出所有映射关系
uncd --add-mapping KEY VALUE      # 添加映射关系
uncd --remove-mapping KEY         # 删除映射关系
uncd --validate-config            # 验证配置文件

# 帮助信息
uncd --help                       # 显示帮助信息
uncd --version                    # 显示版本信息
```

### Python API使用

#### 基本功能

```python
from uncpath import is_unc_path, normalize_unc_path

# 检查是否为UNC路径
is_unc_path(r"\\server\share\file.txt")  # True
is_unc_path("//server/share/file.txt")   # True
is_unc_path("smb://server/share/file.txt")  # True
is_unc_path("C:\\Users\\file.txt")       # False

# 标准化UNC路径
normalize_unc_path(r"\\server\share\folder\file.txt")
# 返回: "//server/share/folder/file.txt"
```

#### 高级功能

```python
from uncpath import UNCResolver, ConfigManager, PathMapper

# UNC路径解析
resolver = UNCResolver()
parsed = resolver.parse_unc_path(r"\\192.168.10.172\sambaShare\folder")
print(f"主机: {parsed.host}")      # 192.168.10.172
print(f"共享: {parsed.share}")     # sambaShare
print(f"路径: {parsed.path}")      # \folder
print(f"协议: {parsed.protocol}")  # windows

# 配置管理
config_manager = ConfigManager()
config_manager.add_mapping("192.168.10.172/sambaShare", "/opt/samba")

# 路径映射
mapper = PathMapper(config_manager)
local_path = mapper.map_to_local(parsed)
print(f"本地路径: {local_path}")   # /opt/samba\folder
```

#### 便捷函数

```python
from uncpath import resolve_unc_path

# 一步完成解析和映射
local_path = resolve_unc_path(r"\\192.168.10.172\sambaShare\folder")
print(local_path)  # /opt/samba\folder
```

### 配置文件格式

配置文件位置：`~/.config/uncpath/config.yaml`

```yaml
version: "1.0"

# 路径映射关系
mappings:
  # 精确映射
  "192.168.10.172/sambaShare": "/opt/samba"
  "server1/shared": "/mnt/smb/server1"
  
  # 通配符映射
  "192.168.*/samba*": "/mnt/smb/{host}/{share}"
  "*/shared": "/mnt/shared/{host}"

# 默认设置
defaults:
  base_path: "/mnt/smb"
  auto_create: false
  create_mode: "0755"

# 别名设置
aliases:
  "samba": "192.168.10.172/sambaShare"
  "docs": "server1/shared"
```

## 🔧 支持的路径格式

### Windows UNC格式
```bash
uncd \\192.168.10.172\sambaShare\folder\file.txt
uncd \\server\share\path
```

### Unix UNC格式
```bash
uncd //192.168.10.172/sambaShare/folder/file.txt
uncd //server/share/path
```

### SMB协议格式
```bash
uncd smb://192.168.10.172/sambaShare/folder/file.txt
uncd smb://server/share/path
```

## 📁 项目结构

```text
uncpath-py/
├── src/uncpath/
│   ├── __init__.py      # 主模块，包含所有API
│   ├── parser.py        # UNC路径解析器
│   ├── config.py        # 配置管理器
│   ├── mapper.py        # 路径映射器
│   ├── cli.py          # 命令行接口
│   └── exceptions.py    # 异常定义
├── tests/               # 测试文件
├── doc/                 # 文档目录
└── pyproject.toml      # 项目配置
```

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_uncpath.py -v
```

## 🛠️ 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 代码格式化

```bash
black src/ tests/
```

### 代码检查

```bash
flake8 src/ tests/
```

### 类型检查

```bash
mypy src/
```

## 📋 版本规划

- **v0.1.0** ✅ 基础UNC路径转换功能（当前版本）
- **v0.2.0** 🔄 Samba自动发现功能
- **v0.2.1** 📋 认证支持和缓存机制
- **v0.2.2** 🚀 高级扫描策略和批量操作

## 🤝 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [GitHub仓库](https://github.com/JiashuaiXu/uncpath-py)
- [PyPI包](https://pypi.org/project/uncpath-py/)
- [文档](doc/)
# API 文档

## 核心API

### UNCResolver 类

#### `parse_unc_path(path: str) -> UNCPath`
解析UNC路径并返回结构化的路径对象。

**参数：**
- `path` (str): 要解析的UNC路径

**返回：**
- `UNCPath`: 解析后的路径对象

**示例：**
```python
from uncpath import UNCResolver

resolver = UNCResolver()
unc_path = resolver.parse_unc_path(r"\\192.168.10.172\sambaShare\folder")
print(unc_path.host)    # "192.168.10.172"
print(unc_path.share)   # "sambaShare"
print(unc_path.path)    # "/folder"
```

#### `normalize_unc_path(path: str) -> str`
标准化UNC路径格式。

**参数：**
- `path` (str): 要标准化的路径

**返回：**
- `str`: 标准化后的路径

**示例：**
```python
normalized = resolver.normalize_unc_path(r"\\server\share\file.txt")
# 返回: "//server/share/file.txt"
```

#### `is_valid_unc_path(path: str) -> bool`
验证路径是否为有效的UNC路径。

**参数：**
- `path` (str): 要验证的路径

**返回：**
- `bool`: 是否为有效的UNC路径

**示例：**
```python
is_valid = resolver.is_valid_unc_path(r"\\server\share\file.txt")  # True
is_valid = resolver.is_valid_unc_path("C:\\Users\\file.txt")       # False
```

### UNCPath 数据类

#### 属性
- `protocol` (str): 协议类型 ('smb', 'unc', 'windows')
- `host` (str): 主机名或IP地址
- `share` (str): 共享名称
- `path` (str): 路径部分
- `original` (str): 原始路径

#### 方法

##### `to_string() -> str`
将UNCPath对象转换为字符串。

**返回：**
- `str`: 格式化的UNC路径字符串

**示例：**
```python
unc_path = UNCPath(
    protocol="windows",
    host="192.168.10.172",
    share="sambaShare",
    path="/folder/file.txt",
    original=r"\\192.168.10.172\sambaShare\folder\file.txt"
)
print(unc_path.to_string())  # "//192.168.10.172/sambaShare/folder/file.txt"
```

### PathMapper 类

#### `map_to_local(unc_path: UNCPath) -> str`
将UNC路径映射到本地路径。

**参数：**
- `unc_path` (UNCPath): 要映射的UNC路径对象

**返回：**
- `str`: 映射后的本地路径

**异常：**
- `MappingNotFoundError`: 当找不到映射关系时

**示例：**
```python
from uncpath import PathMapper, ConfigManager

config_manager = ConfigManager()
mapper = PathMapper(config_manager)
local_path = mapper.map_to_local(unc_path)
print(local_path)  # "/opt/samba/folder/file.txt"
```

#### `find_mapping(host: str, share: str) -> Optional[str]`
查找host/share的映射关系。

**参数：**
- `host` (str): 主机名或IP
- `share` (str): 共享名称

**返回：**
- `Optional[str]`: 映射的本地路径，如果未找到则返回None

**示例：**
```python
mapping = mapper.find_mapping("192.168.10.172", "sambaShare")
if mapping:
    print(f"映射到: {mapping}")
else:
    print("未找到映射关系")
```

### ConfigManager 类

#### `load_config() -> Dict`
加载配置文件。

**返回：**
- `Dict`: 配置字典

**异常：**
- `ConfigError`: 当配置文件格式错误时

**示例：**
```python
config_manager = ConfigManager()
config = config_manager.load_config()
print(config['mappings'])
```

#### `save_config(config: Dict) -> None`
保存配置到文件。

**参数：**
- `config` (Dict): 要保存的配置字典

**异常：**
- `ConfigError`: 当保存失败时

**示例：**
```python
config = {
    'mappings': {
        '192.168.10.172/sambaShare': '/opt/samba'
    }
}
config_manager.save_config(config)
```

#### `get_mappings() -> Dict[str, str]`
获取所有映射关系。

**返回：**
- `Dict[str, str]`: 映射关系字典

**示例：**
```python
mappings = config_manager.get_mappings()
for key, value in mappings.items():
    print(f"{key} -> {value}")
```

#### `add_mapping(key: str, value: str) -> None`
添加新的映射关系。

**参数：**
- `key` (str): UNC路径键 (格式: "host/share")
- `value` (str): 本地路径值

**示例：**
```python
config_manager.add_mapping("server1/shared", "/mnt/smb/server1")
```

## 命令行API

### uncd 命令

#### 基本用法
```bash
uncd <UNC_PATH>
```

**参数：**
- `UNC_PATH`: UNC路径（支持多种格式）

**选项：**
- `--path-only`: 只输出路径，不切换目录
- `--config PATH`: 指定配置文件路径
- `--help`: 显示帮助信息
- `--version`: 显示版本信息

**示例：**
```bash
# 切换到映射的目录
uncd \\192.168.10.172\sambaShare\

# 只获取路径
uncd --path-only \\192.168.10.172\sambaShare\

# 使用自定义配置文件
uncd --config /path/to/config.yaml \\server\share\
```

#### 返回值
- `0`: 成功
- `1`: 一般错误
- `2`: 配置错误
- `3`: 路径错误

## 异常类

### UncdError
基础异常类，所有uncpath相关异常的父类。

### InvalidUNCPathError
当UNC路径格式无效时抛出。

**示例：**
```python
try:
    resolver.parse_unc_path("invalid/path")
except InvalidUNCPathError as e:
    print(f"无效的UNC路径: {e}")
```

### MappingNotFoundError
当找不到映射关系时抛出。

**示例：**
```python
try:
    mapper.map_to_local(unc_path)
except MappingNotFoundError as e:
    print(f"未找到映射关系: {e}")
```

### ConfigError
当配置文件相关操作失败时抛出。

**示例：**
```python
try:
    config_manager.load_config()
except ConfigError as e:
    print(f"配置文件错误: {e}")
```

### DirectoryNotFoundError
当目标目录不存在时抛出。

**示例：**
```python
try:
    cli.change_directory(unc_path)
except DirectoryNotFoundError as e:
    print(f"目录不存在: {e}")
```

## Samba发现API（v0.2.0）

### SambaScanner 类

#### `discover_servers(network: str) -> List[SambaServer]`
发现网络中的Samba服务器。

**参数：**
- `network` (str): 网络地址（如 "192.168.1.0/24"）

**返回：**
- `List[SambaServer]`: 发现的Samba服务器列表

**异常：**
- `NetworkScanError`: 当网络扫描失败时

**示例：**
```python
from uncpath.discovery import SambaScanner

scanner = SambaScanner()
servers = scanner.discover_servers("192.168.1.0/24")
for server in servers:
    print(f"发现服务器: {server.host} ({server.version})")
```

#### `scan_network(network: str) -> List[str]`
扫描网络中的SMB服务。

**参数：**
- `network` (str): 网络地址

**返回：**
- `List[str]`: 提供SMB服务的主机IP列表

**示例：**
```python
hosts = scanner.scan_network("192.168.1.0/24")
print(f"发现 {len(hosts)} 个SMB服务")
```

### SambaClient 类

#### `list_shares() -> List[SambaShare]`
列出服务器上的共享目录。

**返回：**
- `List[SambaShare]`: 共享目录列表

**异常：**
- `ShareEnumerationError`: 当共享枚举失败时

**示例：**
```python
from uncpath.discovery import SambaClient, Credentials

credentials = Credentials(username="admin", password="secret")
client = SambaClient("192.168.10.172", credentials)
shares = client.list_shares()

for share in shares:
    print(f"共享: {share.name} ({share.type})")
```

#### `test_connection() -> bool`
测试与服务器的连接。

**返回：**
- `bool`: 连接是否成功

**示例：**
```python
if client.test_connection():
    print("连接成功")
else:
    print("连接失败")
```

### ShareEnumerator 类

#### `enumerate_all_shares(servers: List[SambaServer]) -> List[SambaShare]`
枚举所有服务器的共享目录。

**参数：**
- `servers` (List[SambaServer]): 服务器列表

**返回：**
- `List[SambaShare]`: 所有共享目录列表

**示例：**
```python
from uncpath.discovery import ShareEnumerator

enumerator = ShareEnumerator(scanner)
all_shares = enumerator.enumerate_all_shares(servers)
print(f"总共发现 {len(all_shares)} 个共享")
```

### AutoMapper 类

#### `generate_mappings(shares: List[SambaShare]) -> Dict[str, str]`
根据共享目录生成映射关系。

**参数：**
- `shares` (List[SambaShare]): 共享目录列表

**返回：**
- `Dict[str, str]`: 映射关系字典

**示例：**
```python
from uncpath.discovery import AutoMapper

mapper = AutoMapper(config_manager)
mappings = mapper.generate_mappings(shares)
for key, value in mappings.items():
    print(f"{key} -> {value}")
```

#### `update_config(mappings: Dict[str, str], preview: bool = False) -> bool`
更新配置文件。

**参数：**
- `mappings` (Dict[str, str]): 映射关系
- `preview` (bool): 是否只预览不更新

**返回：**
- `bool`: 更新是否成功

**示例：**
```python
success = mapper.update_config(mappings, preview=True)
if success:
    print("配置更新成功")
```

## 工具函数

### `resolve_unc_path(path: str) -> str`
便捷函数，直接解析UNC路径并返回本地路径。

**参数：**
- `path` (str): UNC路径

**返回：**
- `str`: 映射后的本地路径

**异常：**
- `InvalidUNCPathError`: 当路径格式无效时
- `MappingNotFoundError`: 当找不到映射时

**示例：**
```python
from uncpath import resolve_unc_path

local_path = resolve_unc_path(r"\\192.168.10.172\sambaShare\file.txt")
print(local_path)  # "/opt/samba/file.txt"
```

### `is_unc_path(path: str) -> bool`
检查路径是否为UNC路径（保持向后兼容）。

**参数：**
- `path` (str): 要检查的路径

**返回：**
- `bool`: 是否为UNC路径

**示例：**
```python
from uncpath import is_unc_path

print(is_unc_path(r"\\server\share\file.txt"))  # True
print(is_unc_path("C:\\Users\\file.txt"))       # False
```

### `normalize_unc_path(path: str) -> str`
标准化UNC路径（保持向后兼容）。

**参数：**
- `path` (str): 要标准化的路径

**返回：**
- `str`: 标准化后的路径

**示例：**
```python
from uncpath import normalize_unc_path

normalized = normalize_unc_path(r"\\server\share\file.txt")
print(normalized)  # "//server/share/file.txt"
```

## 配置API

### 配置文件格式

#### YAML格式
```yaml
version: "1.0"
mappings:
  "192.168.10.172/sambaShare": "/opt/samba"
  "server1/shared": "/mnt/smb/server1"
  
defaults:
  base_path: "/mnt/smb"
  auto_create: false
  
aliases:
  "samba": "192.168.10.172/sambaShare"
```

#### JSON格式
```json
{
  "version": "1.0",
  "mappings": {
    "192.168.10.172/sambaShare": "/opt/samba",
    "server1/shared": "/mnt/smb/server1"
  },
  "defaults": {
    "base_path": "/mnt/smb",
    "auto_create": false
  },
  "aliases": {
    "samba": "192.168.10.172/sambaShare"
  }
}
```

### 配置管理函数

#### `get_config_path() -> str`
获取默认配置文件路径。

**返回：**
- `str`: 配置文件路径

**示例：**
```python
from uncpath import get_config_path

config_path = get_config_path()
print(config_path)  # "~/.config/uncpath/config.yaml"
```

#### `create_default_config(path: str) -> None`
创建默认配置文件。

**参数：**
- `path` (str): 配置文件路径

**示例：**
```python
from uncpath import create_default_config

create_default_config("~/.config/uncpath/config.yaml")
```

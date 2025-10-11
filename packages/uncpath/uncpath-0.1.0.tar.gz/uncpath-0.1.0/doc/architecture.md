# 架构设计文档

## 系统架构概览

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   命令行接口     │    │   核心处理模块   │    │   配置管理模块   │
│   (CLI)         │    │   (Core)        │    │   (Config)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   路径解析模块   │
                    │   (Parser)      │
                    └─────────────────┘
```

## 模块设计

### 1. 命令行接口模块 (CLI)

#### 1.1 UncdCLI 类
```python
class UncdCLI:
    """命令行接口主类"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.path_resolver = UNCResolver()
        self.path_mapper = PathMapper()
    
    def run(self, args):
        """执行uncd命令"""
        pass
    
    def change_directory(self, unc_path):
        """切换到对应目录"""
        pass
    
    def get_local_path(self, unc_path):
        """获取本地路径（不切换）"""
        pass
```

#### 1.2 命令行参数
- `unc_path`: UNC路径（必需）
- `--path-only`: 只输出路径，不切换目录
- `--config`: 指定配置文件路径
- `--help`: 显示帮助信息
- `--version`: 显示版本信息

### 2. 核心处理模块 (Core)

#### 2.1 UNCResolver 类
```python
class UNCResolver:
    """UNC路径解析器"""
    
    def parse_unc_path(self, path: str) -> UNCPath:
        """解析UNC路径"""
        pass
    
    def normalize_unc_path(self, path: str) -> str:
        """标准化UNC路径"""
        pass
    
    def is_valid_unc_path(self, path: str) -> bool:
        """验证UNC路径格式"""
        pass
```

#### 2.2 UNCPath 数据类
```python
@dataclass
class UNCPath:
    """UNC路径数据结构"""
    protocol: str  # 'smb', 'unc', 'windows'
    host: str       # 主机名或IP
    share: str      # 共享名
    path: str       # 路径部分
    original: str   # 原始路径
```

#### 2.3 PathMapper 类
```python
class PathMapper:
    """路径映射器"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
    
    def map_to_local(self, unc_path: UNCPath) -> str:
        """将UNC路径映射到本地路径"""
        pass
    
    def find_mapping(self, host: str, share: str) -> Optional[str]:
        """查找映射关系"""
        pass
```

### 3. 配置管理模块 (Config)

#### 3.1 ConfigManager 类
```python
class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
    
    def load_config(self) -> Dict:
        """加载配置文件"""
        pass
    
    def save_config(self, config: Dict) -> None:
        """保存配置文件"""
        pass
    
    def get_mappings(self) -> Dict[str, str]:
        """获取映射关系"""
        pass
    
    def add_mapping(self, key: str, value: str) -> None:
        """添加映射关系"""
        pass
```

#### 3.2 配置文件结构
```yaml
# ~/.config/uncpath/config.yaml
version: "1.0"
mappings:
  # 精确映射
  "192.168.10.172/sambaShare": "/opt/samba"
  "server1/shared": "/mnt/smb/server1"
  
  # 通配符映射
  "192.168.*/samba*": "/mnt/smb/{host}/{share}"
  
# 默认设置
defaults:
  base_path: "/mnt/smb"
  auto_create: false
  create_mode: "0755"

# 别名设置
aliases:
  "samba": "192.168.10.172/sambaShare"
  "docs": "fileserver/docs"
```

### 4. 路径解析模块 (Parser)

#### 4.1 支持的路径格式
```python
class PathFormats:
    """支持的路径格式"""
    
    WINDOWS_UNC = r"^\\\\([^\\]+)\\([^\\]+)(.*)$"
    UNIX_UNC = r"^//([^/]+)/([^/]+)(.*)$"
    SMB_PROTOCOL = r"^smb://([^/]+)/([^/]+)(.*)$"
```

#### 4.2 路径解析流程
```
输入路径 → 格式识别 → 正则匹配 → 提取组件 → 标准化 → UNCPath对象
```

## 数据流设计

### 1. 基本流程
```
用户输入 → CLI解析 → UNC解析 → 配置查找 → 路径映射 → 目录切换
```

### 2. 详细流程
```
1. 用户执行: uncd \\192.168.10.172\sambaShare\
2. CLI接收参数并验证
3. UNCResolver解析路径，提取host/share/path
4. PathMapper查找配置中的映射关系
5. 如果找到映射，返回本地路径
6. 验证本地路径是否存在
7. 执行os.chdir()切换目录
8. 返回执行结果
```

## 错误处理设计

### 1. 错误类型
```python
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
```

### 2. 错误处理策略
- **输入验证**：在CLI层进行参数验证
- **路径解析**：在解析层进行格式验证
- **映射查找**：在映射层进行关系验证
- **目录切换**：在系统层进行权限验证

## 扩展性设计

### 1. 插件系统
```python
class MappingPlugin:
    """映射插件接口"""
    
    def can_handle(self, host: str, share: str) -> bool:
        """判断是否能处理该映射"""
        pass
    
    def map_path(self, host: str, share: str, path: str) -> str:
        """执行路径映射"""
        pass
```

### 2. 自定义映射器
```python
class DynamicMappingPlugin(MappingPlugin):
    """动态映射插件"""
    
    def __init__(self, mapping_function):
        self.mapping_function = mapping_function
    
    def map_path(self, host: str, share: str, path: str) -> str:
        return self.mapping_function(host, share, path)
```

## 性能优化

### 1. 缓存机制
- **配置缓存**：缓存已加载的配置文件
- **映射缓存**：缓存常用的映射关系
- **路径缓存**：缓存解析过的路径

### 2. 懒加载
- **配置懒加载**：只在需要时加载配置文件
- **插件懒加载**：只在需要时加载插件

## 安全考虑

### 1. 路径安全
- **路径遍历防护**：防止`../`等危险路径
- **权限检查**：检查目标目录的访问权限
- **路径验证**：验证路径的合法性

### 2. 配置安全
- **配置文件权限**：限制配置文件的访问权限
- **配置验证**：验证配置文件的格式和内容
- **敏感信息保护**：避免在配置中存储敏感信息

## 测试策略

### 1. 单元测试
- **路径解析测试**：测试各种UNC路径格式的解析
- **映射功能测试**：测试路径映射功能
- **配置管理测试**：测试配置文件的加载和保存

### 2. 集成测试
- **CLI集成测试**：测试完整的命令行流程
- **配置文件集成测试**：测试配置文件的各种场景
- **错误处理集成测试**：测试各种错误情况的处理

### 3. 端到端测试
- **用户场景测试**：测试典型的用户使用场景
- **跨平台测试**：测试在不同操作系统上的表现
- **性能测试**：测试工具的性能表现

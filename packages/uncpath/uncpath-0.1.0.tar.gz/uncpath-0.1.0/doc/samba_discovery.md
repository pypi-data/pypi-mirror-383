# Samba自动发现功能设计文档

## 功能概述

在v0.2.0版本中，我们将添加Samba自动发现功能，让工具能够自动扫描网络中的Samba服务器，枚举共享目录，并自动生成映射配置。这将大大简化用户的配置工作。

## 核心功能

### 1. Samba服务器发现
- **网络扫描**：自动扫描指定网段中的Samba服务器
- **端口检测**：检测SMB服务端口（445, 139）
- **服务识别**：识别Samba/SMB服务
- **服务器列表**：生成可用的Samba服务器列表

### 2. 共享目录枚举
- **共享列表**：枚举服务器上的所有共享目录
- **共享信息**：获取共享名称、类型、描述等信息
- **权限检测**：检测共享的访问权限
- **过滤规则**：过滤掉系统共享（IPC$, ADMIN$等）

### 3. 自动映射生成
- **映射策略**：根据发现的共享自动生成映射规则
- **命名规则**：智能生成本地路径名称
- **冲突处理**：处理映射冲突和重复
- **配置更新**：自动更新配置文件

## 技术架构

### 1. 模块设计

```
uncpath/
├── discovery/
│   ├── __init__.py
│   ├── scanner.py          # 网络扫描器
│   ├── samba_client.py     # Samba客户端
│   ├── share_enumerator.py # 共享枚举器
│   └── auto_mapper.py      # 自动映射器
├── cli.py                  # 更新CLI接口
└── config.py              # 更新配置管理
```

### 2. 核心类设计

#### SambaScanner 类
```python
class SambaScanner:
    """Samba服务器扫描器"""
    
    def __init__(self):
        self.scan_methods = ['nmap', 'smbclient', 'ping']
    
    def discover_servers(self, network: str) -> List[SambaServer]:
        """发现Samba服务器"""
        pass
    
    def scan_network(self, network: str) -> List[str]:
        """扫描网络中的SMB服务"""
        pass
    
    def check_smb_service(self, host: str) -> bool:
        """检查主机是否提供SMB服务"""
        pass
```

#### SambaClient 类
```python
class SambaClient:
    """Samba客户端"""
    
    def __init__(self, host: str, credentials: Optional[Credentials] = None):
        self.host = host
        self.credentials = credentials
    
    def list_shares(self) -> List[SambaShare]:
        """列出共享目录"""
        pass
    
    def test_connection(self) -> bool:
        """测试连接"""
        pass
    
    def get_share_info(self, share_name: str) -> SambaShare:
        """获取共享信息"""
        pass
```

#### ShareEnumerator 类
```python
class ShareEnumerator:
    """共享枚举器"""
    
    def __init__(self, scanner: SambaScanner):
        self.scanner = scanner
    
    def enumerate_all_shares(self, servers: List[SambaServer]) -> List[SambaShare]:
        """枚举所有服务器的共享"""
        pass
    
    def enumerate_server_shares(self, server: SambaServer) -> List[SambaShare]:
        """枚举单个服务器的共享"""
        pass
    
    def filter_shares(self, shares: List[SambaShare]) -> List[SambaShare]:
        """过滤共享（移除系统共享等）"""
        pass
```

#### AutoMapper 类
```python
class AutoMapper:
    """自动映射器"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
    
    def generate_mappings(self, shares: List[SambaShare]) -> Dict[str, str]:
        """根据共享生成映射关系"""
        pass
    
    def apply_mapping_strategy(self, shares: List[SambaShare], strategy: str) -> Dict[str, str]:
        """应用映射策略"""
        pass
    
    def update_config(self, mappings: Dict[str, str], preview: bool = False) -> bool:
        """更新配置文件"""
        pass
```

### 3. 数据结构

#### SambaServer 数据类
```python
@dataclass
class SambaServer:
    """Samba服务器信息"""
    host: str                    # 主机地址
    hostname: Optional[str]       # 主机名
    port: int                    # 端口号
    version: Optional[str]       # Samba版本
    os: Optional[str]            # 操作系统
    is_accessible: bool         # 是否可访问
    last_seen: datetime         # 最后发现时间
```

#### SambaShare 数据类
```python
@dataclass
class SambaShare:
    """Samba共享信息"""
    server: SambaServer          # 所属服务器
    name: str                   # 共享名称
    type: str                   # 共享类型 (disk, printer, etc.)
    comment: Optional[str]      # 共享描述
    is_readonly: bool           # 是否只读
    is_accessible: bool         # 是否可访问
    permissions: List[str]       # 权限列表
```

#### Credentials 数据类
```python
@dataclass
class Credentials:
    """认证信息"""
    username: Optional[str]      # 用户名
    password: Optional[str]      # 密码
    domain: Optional[str]        # 域
    use_anonymous: bool = False  # 是否使用匿名访问
```

## 实现细节

### 1. 网络扫描实现

#### 使用nmap扫描
```python
import subprocess
import re

def scan_with_nmap(self, network: str) -> List[str]:
    """使用nmap扫描SMB服务"""
    try:
        cmd = [
            'nmap', '-p', '445,139', '--open',
            '--script', 'smb-enum-shares,smb-os-discovery',
            network
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        hosts = []
        for line in result.stdout.split('\n'):
            if 'Nmap scan report for' in line:
                host = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if host:
                    hosts.append(host.group(1))
        
        return hosts
    except FileNotFoundError:
        raise SambaDiscoveryError("nmap未安装或不在PATH中")
```

#### 使用smbclient扫描
```python
def scan_with_smbclient(self, network: str) -> List[str]:
    """使用smbclient扫描SMB服务"""
    hosts = []
    # 生成IP地址列表
    ip_list = self._generate_ip_list(network)
    
    for ip in ip_list:
        if self._check_smb_with_smbclient(ip):
            hosts.append(ip)
    
    return hosts

def _check_smb_with_smbclient(self, host: str) -> bool:
    """使用smbclient检查SMB服务"""
    try:
        cmd = ['smbclient', '-L', host, '-N']  # -N表示匿名访问
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
```

### 2. 共享枚举实现

#### 使用smbclient枚举共享
```python
def list_shares_with_smbclient(self, host: str) -> List[SambaShare]:
    """使用smbclient枚举共享"""
    try:
        cmd = ['smbclient', '-L', host, '-N']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise SambaDiscoveryError(f"无法连接到 {host}: {result.stderr}")
        
        shares = []
        lines = result.stdout.split('\n')
        in_shares_section = False
        
        for line in lines:
            line = line.strip()
            if 'Sharename' in line and 'Type' in line:
                in_shares_section = True
                continue
            
            if in_shares_section and line and not line.startswith('-'):
                parts = line.split()
                if len(parts) >= 2:
                    share_name = parts[0]
                    share_type = parts[1]
                    
                    # 过滤系统共享
                    if share_name not in ['IPC$', 'ADMIN$', 'C$', 'D$']:
                        share = SambaShare(
                            server=SambaServer(host=host),
                            name=share_name,
                            type=share_type,
                            comment=None,
                            is_readonly=False,
                            is_accessible=True,
                            permissions=[]
                        )
                        shares.append(share)
        
        return shares
        
    except FileNotFoundError:
        raise SambaDiscoveryError("smbclient未安装或不在PATH中")
```

### 3. 自动映射生成

#### 映射策略实现
```python
class MappingStrategy:
    """映射策略基类"""
    
    def generate_mapping(self, share: SambaShare) -> Tuple[str, str]:
        """生成映射关系"""
        raise NotImplementedError

class DefaultMappingStrategy(MappingStrategy):
    """默认映射策略"""
    
    def __init__(self, base_path: str = "/mnt/smb"):
        self.base_path = base_path
    
    def generate_mapping(self, share: SambaShare) -> Tuple[str, str]:
        """生成默认映射"""
        key = f"{share.server.host}/{share.name}"
        value = f"{self.base_path}/{share.server.host}/{share.name}"
        return key, value

class HostBasedMappingStrategy(MappingStrategy):
    """基于主机的映射策略"""
    
    def __init__(self, base_path: str = "/mnt/smb"):
        self.base_path = base_path
    
    def generate_mapping(self, share: SambaShare) -> Tuple[str, str]:
        """生成基于主机的映射"""
        key = f"{share.server.host}/{share.name}"
        value = f"{self.base_path}/{share.server.hostname or share.server.host}/{share.name}"
        return key, value

class ShareBasedMappingStrategy(MappingStrategy):
    """基于共享的映射策略"""
    
    def __init__(self, base_path: str = "/mnt/smb"):
        self.base_path = base_path
    
    def generate_mapping(self, share: SambaShare) -> Tuple[str, str]:
        """生成基于共享的映射"""
        key = f"{share.server.host}/{share.name}"
        value = f"{self.base_path}/{share.name}"
        return key, value
```

## 命令行接口

### 1. 新增命令选项

```bash
# 自动发现Samba服务器和共享
uncd --discover-samba

# 扫描指定网段
uncd --discover-samba --network 192.168.1.0/24

# 扫描指定服务器
uncd --discover-samba --host 192.168.10.172

# 自动生成映射并更新配置
uncd --auto-map --discover-samba

# 预览发现的共享（不更新配置）
uncd --discover-samba --preview

# 使用指定认证信息
uncd --discover-samba --username admin --password secret

# 指定映射策略
uncd --discover-samba --mapping-strategy host-based

# 指定基础路径
uncd --discover-samba --base-path /opt/samba
```

### 2. 配置选项

```yaml
# ~/.config/uncpath/config.yaml
version: "1.0"

# 现有配置...
mappings: {}

# Samba发现配置
discovery:
  enabled: true
  scan_methods: ["nmap", "smbclient"]
  default_network: "192.168.1.0/24"
  scan_timeout: 30
  max_concurrent_scans: 10
  
  # 认证配置
  credentials:
    default_username: null
    default_password: null
    use_anonymous: true
  
  # 映射策略配置
  mapping_strategy: "default"  # default, host-based, share-based
  base_path: "/mnt/smb"
  auto_update_config: false
  
  # 过滤规则
  filters:
    exclude_system_shares: true
    exclude_readonly_shares: false
    min_share_size: 0  # MB
    
  # 扫描范围
  networks:
    - "192.168.1.0/24"
    - "192.168.10.0/24"
    - "10.0.0.0/8"
```

## 使用示例

### 1. 基本使用

```bash
# 发现本地网络中的Samba服务器
uncd --discover-samba

# 输出示例：
# 发现Samba服务器:
#   192.168.1.100 (Samba 4.15.0)
#   192.168.1.101 (Windows Server 2019)
# 
# 发现共享:
#   192.168.1.100/sambaShare -> /mnt/smb/192.168.1.100/sambaShare
#   192.168.1.100/docs -> /mnt/smb/192.168.1.100/docs
#   192.168.1.101/shared -> /mnt/smb/192.168.1.101/shared
```

### 2. 自动配置

```bash
# 自动发现并更新配置
uncd --auto-map --discover-samba --network 192.168.10.0/24

# 预览模式（不更新配置）
uncd --discover-samba --preview --network 192.168.10.0/24
```

### 3. 高级配置

```bash
# 使用自定义映射策略
uncd --discover-samba --mapping-strategy host-based --base-path /opt/samba

# 使用认证信息
uncd --discover-samba --username admin --password secret --host 192.168.10.172
```

## API使用示例

### 1. 基本API使用

```python
from uncpath.discovery import SambaScanner, ShareEnumerator, AutoMapper
from uncpath.config import ConfigManager

# 创建扫描器
scanner = SambaScanner()

# 发现服务器
servers = scanner.discover_servers("192.168.1.0/24")
print(f"发现 {len(servers)} 个Samba服务器")

# 枚举共享
enumerator = ShareEnumerator(scanner)
shares = enumerator.enumerate_all_shares(servers)
print(f"发现 {len(shares)} 个共享")

# 自动生成映射
config_manager = ConfigManager()
mapper = AutoMapper(config_manager)
mappings = mapper.generate_mappings(shares)

# 更新配置
mapper.update_config(mappings)
```

### 2. 高级API使用

```python
from uncpath.discovery import SambaClient, Credentials
from uncpath.discovery.mapping import HostBasedMappingStrategy

# 使用认证信息
credentials = Credentials(username="admin", password="secret")
client = SambaClient("192.168.10.172", credentials)

# 枚举共享
shares = client.list_shares()

# 使用自定义映射策略
strategy = HostBasedMappingStrategy("/opt/samba")
mappings = {}
for share in shares:
    key, value = strategy.generate_mapping(share)
    mappings[key] = value

print("生成的映射关系:")
for key, value in mappings.items():
    print(f"  {key} -> {value}")
```

## 错误处理

### 1. 常见错误类型

```python
class SambaDiscoveryError(Exception):
    """Samba发现基础异常"""
    pass

class NetworkScanError(SambaDiscoveryError):
    """网络扫描错误"""
    pass

class ShareEnumerationError(SambaDiscoveryError):
    """共享枚举错误"""
    pass

class MappingGenerationError(SambaDiscoveryError):
    """映射生成错误"""
    pass

class ConfigUpdateError(SambaDiscoveryError):
    """配置更新错误"""
    pass
```

### 2. 错误处理策略

```python
def discover_samba_with_error_handling(self, network: str) -> List[SambaServer]:
    """带错误处理的Samba发现"""
    try:
        return self.discover_servers(network)
    except NetworkScanError as e:
        logger.warning(f"网络扫描失败: {e}")
        return []
    except ShareEnumerationError as e:
        logger.warning(f"共享枚举失败: {e}")
        return []
    except Exception as e:
        logger.error(f"未知错误: {e}")
        raise SambaDiscoveryError(f"Samba发现失败: {e}")
```

## 性能优化

### 1. 并发扫描

```python
import asyncio
import aiofiles

async def discover_servers_async(self, network: str) -> List[SambaServer]:
    """异步并发扫描服务器"""
    ip_list = self._generate_ip_list(network)
    
    # 限制并发数
    semaphore = asyncio.Semaphore(self.max_concurrent_scans)
    
    async def check_host(ip: str) -> Optional[SambaServer]:
        async with semaphore:
            if await self._check_smb_async(ip):
                return SambaServer(host=ip)
            return None
    
    tasks = [check_host(ip) for ip in ip_list]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 过滤结果
    servers = [r for r in results if isinstance(r, SambaServer)]
    return servers
```

### 2. 缓存机制

```python
import json
from datetime import datetime, timedelta

class SambaDiscoveryCache:
    """Samba发现缓存"""
    
    def __init__(self, cache_file: str = "~/.cache/uncpath/discovery.json"):
        self.cache_file = Path(cache_file).expanduser()
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(hours=1)
    
    def get_cached_servers(self, network: str) -> Optional[List[SambaServer]]:
        """获取缓存的服务器列表"""
        if not self.cache_file.exists():
            return None
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            if network in cache_data:
                cached_time = datetime.fromisoformat(cache_data[network]['timestamp'])
                if datetime.now() - cached_time < self.cache_ttl:
                    return [SambaServer(**server) for server in cache_data[network]['servers']]
        except Exception:
            pass
        
        return None
    
    def cache_servers(self, network: str, servers: List[SambaServer]) -> None:
        """缓存服务器列表"""
        try:
            cache_data = {}
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
            
            cache_data[network] = {
                'timestamp': datetime.now().isoformat(),
                'servers': [server.__dict__ for server in servers]
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            logger.warning(f"缓存保存失败: {e}")
```

## 测试策略

### 1. 单元测试

```python
# tests/test_discovery.py
import pytest
from unittest.mock import Mock, patch
from uncpath.discovery import SambaScanner, ShareEnumerator

class TestSambaScanner:
    """测试Samba扫描器"""
    
    def setup_method(self):
        self.scanner = SambaScanner()
    
    @patch('subprocess.run')
    def test_scan_with_nmap(self, mock_run):
        """测试nmap扫描"""
        mock_run.return_value.stdout = """
        Nmap scan report for 192.168.1.100
        Host is up (0.001s latency).
        PORT    STATE SERVICE
        445/tcp open  microsoft-ds
        """
        
        hosts = self.scanner.scan_with_nmap("192.168.1.0/24")
        assert "192.168.1.100" in hosts
    
    @patch('subprocess.run')
    def test_scan_with_smbclient(self, mock_run):
        """测试smbclient扫描"""
        mock_run.return_value.returncode = 0
        
        result = self.scanner._check_smb_with_smbclient("192.168.1.100")
        assert result is True
```

### 2. 集成测试

```python
# tests/test_integration_discovery.py
import pytest
from uncpath.discovery import SambaDiscoveryManager

class TestSambaDiscoveryIntegration:
    """Samba发现集成测试"""
    
    def setup_method(self):
        self.discovery_manager = SambaDiscoveryManager()
    
    @pytest.mark.integration
    def test_full_discovery_workflow(self):
        """测试完整发现工作流程"""
        # 模拟发现过程
        with patch.object(self.discovery_manager, 'discover_servers') as mock_discover:
            mock_discover.return_value = [
                SambaServer(host="192.168.1.100"),
                SambaServer(host="192.168.1.101")
            ]
            
            result = self.discovery_manager.discover_and_map("192.168.1.0/24")
            assert len(result['servers']) == 2
            assert len(result['shares']) > 0
            assert len(result['mappings']) > 0
```

## 版本规划

### v0.2.0 - Samba自动发现功能
- [ ] 基础网络扫描功能
- [ ] Samba服务器发现
- [ ] 共享目录枚举
- [ ] 自动映射生成
- [ ] 配置文件自动更新

### v0.2.1 - 增强功能
- [ ] 认证支持
- [ ] 缓存机制
- [ ] 并发扫描优化
- [ ] 错误处理改进

### v0.2.2 - 高级功能
- [ ] 自定义映射策略
- [ ] 批量操作支持
- [ ] 定时扫描功能
- [ ] 监控和通知

这个Samba自动发现功能将大大提升工具的实用性，让用户无需手动配置就能使用网络中的Samba共享。

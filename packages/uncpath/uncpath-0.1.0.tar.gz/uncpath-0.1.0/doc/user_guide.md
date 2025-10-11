# 用户指南

## 快速开始

### 安装

```bash
pip install uncpath-py
```

### 基本使用

```bash
# 切换到UNC路径对应的本地目录
uncd \\192.168.10.172\sambaShare\

# 只获取路径，不切换目录
uncd --path-only \\192.168.10.172\sambaShare\
```

## 配置设置

### 创建配置文件

首次使用前，需要创建配置文件：

```bash
# 创建默认配置文件
uncd --init-config
```

配置文件位置：`~/.config/uncpath/config.yaml`

### 配置文件格式

```yaml
# ~/.config/uncpath/config.yaml
version: "1.0"

# 路径映射关系
mappings:
  # 精确映射
  "192.168.10.172/sambaShare": "/opt/samba"
  "server1/shared": "/mnt/smb/server1"
  "fileserver/docs": "/home/user/smb/docs"
  
  # 通配符映射（支持*和{}占位符）
  "192.168.*/samba*": "/mnt/smb/{host}/{share}"
  "*/shared": "/mnt/shared/{host}"

# 默认设置
defaults:
  base_path: "/mnt/smb"      # 默认基础路径
  auto_create: false         # 是否自动创建目录
  create_mode: "0755"        # 创建目录的权限

# 别名设置
aliases:
  "samba": "192.168.10.172/sambaShare"
  "docs": "fileserver/docs"
  "shared": "server1/shared"
```

### 添加映射关系

#### 方法1：编辑配置文件
直接编辑 `~/.config/uncpath/config.yaml` 文件，在 `mappings` 部分添加新的映射关系。

#### 方法2：使用命令行
```bash
# 添加映射关系
uncd --add-mapping "server2/shared" "/mnt/smb/server2"

# 查看所有映射关系
uncd --list-mappings
```

## 支持的路径格式

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

## 命令行选项

### 基本选项

#### `--path-only`
只输出映射后的本地路径，不切换目录。

```bash
uncd --path-only \\192.168.10.172\sambaShare\
# 输出: /opt/samba
```

#### `--config PATH`
指定自定义配置文件路径。

```bash
uncd --config /path/to/custom/config.yaml \\server\share\
```

#### `--help`
显示帮助信息。

```bash
uncd --help
```

#### `--version`
显示版本信息。

```bash
uncd --version
```

### 配置管理选项

#### `--init-config`
创建默认配置文件。

```bash
uncd --init-config
```

#### `--add-mapping KEY VALUE`
添加新的映射关系。

```bash
uncd --add-mapping "server3/shared" "/mnt/smb/server3"
```

#### `--list-mappings`
列出所有映射关系。

```bash
uncd --list-mappings
```

#### `--remove-mapping KEY`
删除映射关系。

```bash
uncd --remove-mapping "server3/shared"
```

## 使用场景

### 场景1：开发环境切换

```bash
# 从Windows SMB共享切换到Linux本地挂载
uncd \\192.168.10.172\sambaShare\
# 自动切换到 /opt/samba/

# 使用别名
uncd samba
# 自动切换到 /opt/samba/
```

### 场景2：多服务器环境

```bash
# 不同服务器的共享目录
uncd //server1/shared/
# 切换到 /mnt/smb/server1/

uncd smb://fileserver/docs/
# 切换到 /home/user/smb/docs/
```

### 场景3：脚本自动化

```bash
#!/bin/bash
# 在脚本中使用
LOCAL_PATH=$(uncd --path-only \\192.168.10.172\sambaShare\)
cd "$LOCAL_PATH"
echo "当前目录: $(pwd)"
```

### 场景4：Samba自动发现

```bash
# 自动发现并配置所有Samba共享
uncd --discover-samba --auto-map

# 发现特定网段的共享
uncd --discover-samba --network 192.168.10.0/24 --preview

# 使用认证信息发现共享
uncd --discover-samba --username admin --password secret --host 192.168.10.172
```

### 场景5：批量操作

```bash
# 批量处理多个路径
for path in "\\server1\shared" "\\server2\docs" "\\server3\files"; do
    echo "处理: $path"
    uncd "$path"
    # 执行操作...
done
```

## 高级功能

### Samba自动发现（v0.2.0）

#### 自动发现Samba服务器和共享

```bash
# 发现本地网络中的Samba服务器和共享
uncd --discover-samba

# 扫描指定网段
uncd --discover-samba --network 192.168.1.0/24

# 扫描指定服务器
uncd --discover-samba --host 192.168.10.172

# 自动生成映射并更新配置
uncd --auto-map --discover-samba

# 预览发现的共享（不更新配置）
uncd --discover-samba --preview
```

#### 使用认证信息

```bash
# 使用用户名和密码
uncd --discover-samba --username admin --password secret

# 使用域认证
uncd --discover-samba --username admin --password secret --domain WORKGROUP
```

#### 自定义映射策略

```bash
# 使用基于主机的映射策略
uncd --discover-samba --mapping-strategy host-based

# 使用基于共享的映射策略
uncd --discover-samba --mapping-strategy share-based

# 指定自定义基础路径
uncd --discover-samba --base-path /opt/samba
```

### 通配符映射

支持使用通配符进行灵活的路径映射：

```yaml
mappings:
  # 所有192.168.x.x网段的samba共享都映射到/mnt/smb/
  "192.168.*/samba*": "/mnt/smb/{host}/{share}"
  
  # 所有服务器的shared共享都映射到/mnt/shared/
  "*/shared": "/mnt/shared/{host}"
  
  # 使用占位符
  "{host}/docs": "/home/user/smb/{host}/docs"
```

### 别名功能

为常用的映射关系设置别名：

```yaml
aliases:
  "samba": "192.168.10.172/sambaShare"
  "docs": "fileserver/docs"
  "shared": "server1/shared"
```

使用别名：

```bash
uncd samba    # 等同于 uncd \\192.168.10.172\sambaShare\
uncd docs     # 等同于 uncd smb://fileserver/docs/
uncd shared   # 等同于 uncd //server1/shared/
```

### 自动目录创建

启用自动目录创建功能：

```yaml
defaults:
  auto_create: true
  create_mode: "0755"
```

当映射的本地目录不存在时，会自动创建：

```bash
uncd \\newserver\newshare\
# 如果 /mnt/smb/newserver/newshare 不存在，会自动创建
```

## 故障排除

### 常见问题

#### 1. 找不到映射关系
```
错误: MappingNotFoundError: 未找到映射关系 '192.168.10.172/sambaShare'
```

**解决方案：**
- 检查配置文件中的映射关系
- 使用 `uncd --list-mappings` 查看当前映射
- 使用 `uncd --add-mapping` 添加映射关系

#### 2. 配置文件格式错误
```
错误: ConfigError: 配置文件格式错误
```

**解决方案：**
- 检查YAML文件格式是否正确
- 使用 `uncd --init-config` 重新创建配置文件
- 验证缩进和语法

#### 3. 目录不存在
```
错误: DirectoryNotFoundError: 目录 '/opt/samba' 不存在
```

**解决方案：**
- 检查本地目录是否存在
- 启用自动创建功能
- 手动创建目录

#### 4. 权限问题
```
错误: PermissionError: 没有权限访问目录
```

**解决方案：**
- 检查目录权限
- 使用 `sudo` 运行命令
- 修改目录权限

### 调试模式

使用 `--verbose` 选项获取详细输出：

```bash
uncd --verbose \\192.168.10.172\sambaShare\
```

输出示例：
```
解析UNC路径: \\192.168.10.172\sambaShare\
主机: 192.168.10.172
共享: sambaShare
查找映射关系...
找到映射: /opt/samba
切换目录: /opt/samba
成功切换到目录: /opt/samba
```

### 配置文件验证

使用 `--validate-config` 选项验证配置文件：

```bash
uncd --validate-config
```

## 最佳实践

### 1. 配置文件管理
- 定期备份配置文件
- 使用版本控制管理配置文件
- 为不同环境创建不同的配置文件

### 2. 路径映射策略
- 使用有意义的映射路径
- 避免路径冲突
- 使用通配符简化配置

### 3. 安全考虑
- 限制配置文件的访问权限
- 避免在配置中存储敏感信息
- 定期检查映射关系的有效性

### 4. 性能优化
- 使用别名减少路径解析时间
- 避免过深的目录结构
- 定期清理无用的映射关系

## 集成指南

### Shell集成

#### Bash
在 `~/.bashrc` 中添加：

```bash
# uncd别名
alias uncd='uncd'
```

#### Zsh
在 `~/.zshrc` 中添加：

```bash
# uncd别名
alias uncd='uncd'
```

#### Fish
在 `~/.config/fish/config.fish` 中添加：

```fish
# uncd别名
alias uncd='uncd'
```

### IDE集成

#### VS Code
创建任务配置 `.vscode/tasks.json`：

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Switch to Samba",
            "type": "shell",
            "command": "uncd",
            "args": ["samba"],
            "group": "build"
        }
    ]
}
```

### 脚本集成

#### Python脚本
```python
import subprocess
import os

def switch_to_unc_path(unc_path):
    """切换到UNC路径对应的本地目录"""
    try:
        result = subprocess.run(['uncd', unc_path], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"成功切换到: {result.stdout.strip()}")
        else:
            print(f"错误: {result.stderr}")
    except Exception as e:
        print(f"执行失败: {e}")

# 使用示例
switch_to_unc_path(r"\\192.168.10.172\sambaShare\")
```

#### Shell脚本
```bash
#!/bin/bash

# 函数：切换到UNC路径
switch_to_unc() {
    local unc_path="$1"
    if uncd "$unc_path"; then
        echo "成功切换到: $(pwd)"
    else
        echo "切换失败"
        return 1
    fi
}

# 使用示例
switch_to_unc "\\192.168.10.172\\sambaShare\\"
```

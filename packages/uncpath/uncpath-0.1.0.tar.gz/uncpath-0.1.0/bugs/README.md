# Bug报告索引

本文件夹记录了uncpath-py项目开发过程中遇到的重要bug和问题。

## Bug列表

### 1. Python原始字符串反斜杠问题
- **文件**: [python_raw_string_backslash_issue.md](python_raw_string_backslash_issue.md)
- **日期**: 2025-10-11
- **状态**: ✅ 已修复
- **描述**: 在实现UNC路径解析器时，遇到Python原始字符串中反斜杠数量的问题，导致正则表达式无法正确匹配Windows UNC路径。
- **影响**: v0.1.0开发阶段
- **解决方案**: 使用字符串分割方法替代正则表达式

### 2. Windows Git换行符导致GitHub显示乱码
- **文件**: [github_readme_encoding_issue.md](github_readme_encoding_issue.md)
- **日期**: 2025-10-11
- **状态**: ✅ 已修复
- **描述**: Windows系统上推送README.md到GitHub后显示格式混乱，所有换行符被合并，导致Markdown格式无法正确渲染。
- **影响**: v0.1.0发布阶段
- **解决方案**: 设置core.autocrlf=false并添加.gitattributes文件

## Bug分类

### 按严重程度
- **高**: 影响核心功能的问题
- **中**: 影响用户体验的问题  
- **低**: 不影响功能的小问题

### 按状态
- **已修复** ✅: 问题已解决并测试通过
- **进行中** 🔄: 正在修复
- **待修复** ⏳: 已识别但未开始修复
- **无法修复** ❌: 由于技术限制无法修复

### 按模块
- **parser**: UNC路径解析相关
- **config**: 配置管理相关
- **mapper**: 路径映射相关
- **cli**: 命令行接口相关
- **general**: 通用问题

## 报告新Bug

如果发现新的bug，请按照以下格式创建新的bug报告：

1. 创建新的markdown文件，命名格式：`YYYY-MM-DD_bug_description.md`
2. 使用模板格式记录bug信息
3. 更新本索引文件

## Bug报告模板

```markdown
# Bug报告：[Bug标题]

## 问题描述
简要描述问题现象

## 问题详情
详细描述问题，包括：
- 问题现象
- 问题原因
- 复现步骤

## 解决方案
描述解决方案和修复过程

## 测试验证
验证修复效果的测试代码

## 经验教训
从这次bug中学到的经验

## 相关文件
涉及的文件列表

## 修复状态
- 影响版本：
- 修复版本：

## 日期
YYYY-MM-DD
```

## 统计信息

- 总bug数量: 2
- 已修复: 2
- 进行中: 0
- 待修复: 0

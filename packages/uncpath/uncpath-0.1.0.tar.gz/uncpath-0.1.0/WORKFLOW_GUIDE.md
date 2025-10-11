# CI/CD 工作流程指南 / Workflow Guide

## 概述 / Overview

本项目实现了完整的自动化 CI/CD 流程，用于 Python 包的测试、构建和发布。

This project implements a complete automated CI/CD pipeline for testing, building, and publishing Python packages.

## 工作流程触发条件 / Workflow Triggers

工作流程在以下情况下触发：

1. **标签推送** / **Tag Push**: 当推送符合 `v*.*.*` 格式的标签时（例如 `v1.0.0`）
2. **手动触发** / **Manual Trigger**: 可以在 GitHub Actions 界面手动触发

## 工作流程步骤 / Workflow Steps

### 1. 检出代码 / Checkout Code
- 使用 `actions/checkout@v4`
- 获取完整的 Git 历史记录（`fetch-depth: 0`）用于生成变更日志

### 2. 设置 Python 环境 / Setup Python
- 安装 Python 3.11
- 使用 `actions/setup-python@v5`

### 3. 安装 uv / Install uv
- 安装最新版本的 uv 包管理器
- 使用 `astral-sh/setup-uv@v5`

### 4. 提取版本号 / Extract Version
- 从 Git 标签中提取版本号
- 格式：`v1.2.3` → `1.2.3`
- 更新 `pyproject.toml` 中的版本号

### 5. 同步依赖 / Sync Dependencies
- 运行 `uv sync --no-dev` 或 `uv pip install -e .`
- 安装项目依赖

### 6. 运行测试 / Run Tests
- 执行 `uv run -m pytest -q`
- 如果测试失败，工作流程将停止

### 7. 构建包 / Build Package
- 运行 `uv build`
- 生成 wheel 包 (`.whl`) 和源码包 (`.tar.gz`)
- 产物位于 `dist/` 目录

### 8. 生成变更日志 / Generate Changelog
- 自动从 Git 提交历史生成变更日志
- 对于首次发布，包含所有提交
- 对于后续发布，包含自上一个标签以来的提交

### 9. 发布到 PyPI / Publish to PyPI
- **条件**：仅在推送版本标签时执行
- **要求**：需要配置 `PYPI_TOKEN` secret
- 运行 `uv publish --token $PYPI_TOKEN`
- 如果没有配置 token，会显示警告但不会失败

### 10. 创建 GitHub Release / Create GitHub Release
- **条件**：仅在推送版本标签时执行
- 创建 Release 页面，标题格式：`uncpath-py v1.2.3 发布`
- 附加构建产物（wheel 和 tar.gz 文件）
- 包含自动生成的变更日志

### 11. 输出摘要 / Output Summary
- 在 GitHub Actions 摘要页面显示发布信息
- 包含版本号、发布时间、PyPI 链接、GitHub Release 链接

## 配置要求 / Configuration Requirements

### 必需的 Secrets / Required Secrets

#### PYPI_TOKEN
用于发布包到 PyPI 的 API token。

**配置步骤：**

1. 访问 https://pypi.org/manage/account/token/
2. 创建一个新的 API token（选择项目范围或全局范围）
3. 在 GitHub 仓库设置中：
   - 导航到 Settings → Secrets and variables → Actions
   - 点击 "New repository secret"
   - 名称：`PYPI_TOKEN`
   - 值：粘贴从 PyPI 获取的 token

### 权限配置 / Permissions

工作流程需要以下权限：
- `contents: write` - 用于创建 GitHub Release
- `id-token: write` - 用于 PyPI 可信发布（如果配置）

## 发布新版本 / Release New Version

### 步骤 / Steps

1. **更新版本号** / **Update Version**
   ```bash
   # 编辑 pyproject.toml 中的 version 字段
   # 注意：工作流程会自动从 tag 更新版本号，但建议保持一致
   ```

2. **提交更改** / **Commit Changes**
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 1.0.0"
   git push
   ```

3. **创建并推送标签** / **Create and Push Tag**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. **等待工作流程完成** / **Wait for Workflow**
   - 访问 GitHub Actions 页面查看进度
   - 工作流程完成后，包将发布到 PyPI
   - GitHub Release 页面将自动创建

## 输出格式 / Output Format

工作流程完成后，在 GitHub Actions 摘要页面会显示：

```
## 发布成功 / Release Successful! 🎉

**版本号 / Version**: 1.0.0
**发布时间 / Release Time**: 2025-10-11 05:30:00 UTC
**PyPI 链接 / PyPI Link**: https://pypi.org/project/uncpath-py/1.0.0/
**GitHub Release 链接 / GitHub Release Link**: https://github.com/JiashuaiXu/uncpath-py/releases/tag/v1.0.0

### 构建产物 / Build Artifacts
```
uncpath_py-1.0.0-py3-none-any.whl
uncpath-py-1.0.0.tar.gz
```
```

## 故障排查 / Troubleshooting

### 测试失败 / Test Failures
如果测试失败，工作流程会停止。检查测试日志并修复问题后重新推送标签。

### PyPI 发布失败 / PyPI Publish Failures
- 确认 `PYPI_TOKEN` 已正确配置
- 确认版本号未在 PyPI 上使用过
- 检查包名是否已被其他人注册

### Release 创建失败 / Release Creation Failures
- 确认仓库有足够的权限
- 检查标签格式是否正确
- 确认 GITHUB_TOKEN 有 `contents: write` 权限

## 本地测试 / Local Testing

在推送标签前，可以本地测试：

```bash
# 运行测试
uv run -m pytest -q

# 构建包
uv build

# 检查构建产物
ls -lh dist/
```

## 手动触发 / Manual Trigger

如果需要手动触发工作流程（不推送标签）：

1. 访问仓库的 Actions 页面
2. 选择 "CI/CD Pipeline for uncpath-py" 工作流程
3. 点击 "Run workflow" 按钮
4. 选择分支并运行

注意：手动触发不会发布到 PyPI 或创建 Release。

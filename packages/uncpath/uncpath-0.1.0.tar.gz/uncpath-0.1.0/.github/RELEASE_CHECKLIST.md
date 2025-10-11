# Release Checklist / 发布检查清单

## 发布前准备 / Pre-Release Preparation

- [ ] 所有测试通过 / All tests pass
  ```bash
  uv run -m pytest -v
  ```

- [ ] 代码已合并到主分支 / Code merged to main branch

- [ ] 版本号已更新 / Version number updated
  - 位置 / Location: `pyproject.toml` 中的 `version` 字段
  - 遵循语义化版本 / Follow semantic versioning (MAJOR.MINOR.PATCH)

- [ ] 文档已更新 / Documentation updated
  - [ ] README.md
  - [ ] CHANGELOG.md (如果存在 / if exists)
  - [ ] API 文档 / API docs (如果有变更 / if changed)

- [ ] PYPI_TOKEN 已配置 / PYPI_TOKEN configured
  - 位置 / Location: Repository Settings → Secrets → Actions → PYPI_TOKEN

## 发布步骤 / Release Steps

### 1. 创建发布标签 / Create Release Tag

```bash
# 确保在主分支上 / Make sure you're on main branch
git checkout main
git pull origin main

# 创建标签 / Create tag (replace X.Y.Z with your version)
git tag vX.Y.Z

# 推送标签 / Push tag
git push origin vX.Y.Z
```

### 2. 监控工作流程 / Monitor Workflow

访问 / Visit: `https://github.com/JiashuaiXu/uncpath-py/actions`

观察工作流程执行情况：
- ✓ 测试通过 / Tests pass
- ✓ 构建成功 / Build succeeds  
- ✓ 发布到 PyPI / Published to PyPI
- ✓ GitHub Release 创建 / GitHub Release created

### 3. 验证发布 / Verify Release

- [ ] PyPI 页面检查 / Check PyPI page
  ```
  https://pypi.org/project/uncpath-py/X.Y.Z/
  ```

- [ ] GitHub Release 页面检查 / Check GitHub Release page
  ```
  https://github.com/JiashuaiXu/uncpath-py/releases/tag/vX.Y.Z
  ```

- [ ] 测试安装 / Test installation
  ```bash
  pip install uncpath-py==X.Y.Z
  python -c "import uncpath; print(uncpath.__version__)"
  ```

## 发布后任务 / Post-Release Tasks

- [ ] 在社交媒体或相关社区宣布发布 / Announce release on social media or relevant communities

- [ ] 更新依赖此包的其他项目 / Update other projects that depend on this package

- [ ] 监控问题报告和反馈 / Monitor issue reports and feedback

## 版本号指南 / Version Number Guide

根据语义化版本规范：

- **MAJOR (主版本)**: 不兼容的 API 变更 / Incompatible API changes
- **MINOR (次版本)**: 向后兼容的功能新增 / Backward-compatible new features  
- **PATCH (修订版本)**: 向后兼容的问题修复 / Backward-compatible bug fixes

示例 / Examples:
- `v0.1.0` - 初始开发版本 / Initial development version
- `v0.1.1` - 修复 bug / Bug fixes
- `v0.2.0` - 新增功能 / New features
- `v1.0.0` - 首个稳定版本 / First stable release
- `v2.0.0` - 重大变更 / Breaking changes

## 紧急回滚 / Emergency Rollback

如果发现严重问题需要回滚：

1. **从 PyPI 下架版本** / **Yank version from PyPI**
   - 访问 / Visit: https://pypi.org/manage/project/uncpath-py/releases/
   - 注意：此链接仅在首次发布后可用 / Note: This URL is only available after first publication
   - 选择有问题的版本并标记为 "yanked"
   
2. **在 GitHub 标记为 Pre-release** / **Mark as Pre-release on GitHub**
   - 编辑 Release 并勾选 "This is a pre-release"

3. **修复问题并发布新版本** / **Fix issues and release new version**

## 故障排查 / Troubleshooting

### 工作流程失败 / Workflow Fails

**测试失败 / Tests fail:**
- 删除标签 / Delete tag: `git push origin --delete vX.Y.Z`
- 修复问题并重新发布 / Fix issues and re-release

**PyPI 发布失败 / PyPI publish fails:**
- 检查 PYPI_TOKEN / Check PYPI_TOKEN
- 检查版本号是否已存在 / Check if version already exists
- 如需重新发布，增加版本号 / Increment version to re-publish

**GitHub Release 失败 / GitHub Release fails:**
- 检查仓库权限 / Check repository permissions
- 手动创建 Release / Manually create release

## 联系方式 / Contact

如有问题，请联系项目维护者或在 GitHub 上创建 issue。

For questions, contact project maintainers or create an issue on GitHub.

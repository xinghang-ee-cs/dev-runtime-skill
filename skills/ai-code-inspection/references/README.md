# 日常检查路线图

本文件只提供 `ai-code-inspection` 的轻量执行路线图。

## 启动

1. 读取 `../project-environment-profile.md`，确认当前项目稳定环境。
2. 明确检查边界：
   - `scope_target`
   - `code_selection_mode`
3. 如果开发者要求检查已修改代码，识别变更文件：
   - `git status --short`
   - `git diff --name-only`
   - `git ls-files --others --exclude-standard`
4. 根据检查边界选择需要执行的 Step。

## Step 顺序

1. `step1-naming-convention.md`：命名、文件放置、术语一致性。
2. `step2-code-quality.md`：常见 bug、死代码、错误处理、数据 shape、类型契约。
3. `step3-architecture-layer.md`：前后端分层、API 边界、repository/data access 边界。
4. `step4-test-coverage.md`：测试影响、边界用例、验证命令选择。
5. `step5-documentation.md`：docs/API/schema/README 与代码行为一致性。
6. `step6-comment-standard.md`：注释和本地文件头规范。
7. `step7-code-commit.md`：git 状态、验证摘要、提交准备和 CI/CD 配置轻量检查。

## 常用证据命令

```bash
git status --short
git diff --name-only
git ls-files --others --exclude-standard
git diff -- <scoped-files>
```

## 最终收口

最终报告应汇总：

- 执行过的 Step。
- 跳过的 Step。
- 发现的问题。
- 已完成的修复。
- 验证命令与结果。
- 相关时的 CI/CD 配置检查状态。
- 相关时的数据库迁移状态。

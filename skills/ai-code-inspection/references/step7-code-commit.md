# Step 7: 提交准备

本 Step 用于检查 git 状态、暂存范围、验证摘要和提交准备。除非开发者明确要求，不得 stage 或 commit。

## 安全规则

- 未经开发者明确要求，不得 stage、commit、push、创建分支、reset、checkout 或 stash。
- 保留无关改动。
- 如果存在无关 dirty 文件，保持不动；只在相关时单独报告。
- 优先使用非交互式 git 命令。
- 除非开发者明确要求且文件在范围内，否则不得 force-add 被忽略文件。

## 必查 Git 信息

运行或检查：

```bash
git status --short
git diff --name-only
git ls-files --others --exclude-standard
git diff -- <scoped-files>
git diff --cached --name-status
```

检查：

- changed files 是否符合声明检查边界。
- staged files 如存在，是否符合请求范围。
- untracked files 是有意纳入还是应保持不动。
- generated output、log、本地 env 文件和 cache 是否被意外纳入。
- 行为、API、schema 或 test command 变化时，docs 和 tests 是否同步。
- 验证命令是否执行；跳过时是否有明确理由。

## 验证摘要

使用 `../project-environment-profile.md` 中的命令。

广义 typed source 变化时，优先使用可用的 broad verify 命令。范围较窄时，运行与变更区域匹配的 package build/test/schema 命令。

跳过验证必须明确报告：

- 跳过的命令。
- 跳过原因。
- 剩余风险。

## CI/CD 检查

仅当 `ci_cd.ci_enabled: true` 时执行：

- 检查 workflow 文件是否覆盖相关变更区域。
- 确认 CI 是否包含 install、build、test、schema validation、migration deployment 和 deploy 步骤。
- 不得执行 release/deploy job。
- 检查结果应进入当前 Step 报告。

## 数据库迁移状态

如果 Prisma schema 或 migration 文件变化，最终 readiness 必须包含：

- 变化或新增的 migration 文件。
- schema validation 命令和结果，如已执行。
- runtime 数据库迁移应用状态：
  - `created_only`
  - `validated`
  - `applied`
  - `not_confirmed`
- 目标数据库，只有在开发者明确确认时才写。
- 应用 migration 的命令只能作为建议/人工命令列出，除非开发者批准执行。

schema/migration 发生变化但当前 runtime 数据库应用未确认时，不得声称 runtime readiness 通过。

## 提交信息建议

开发者要求 commit 时，使用简洁信息：

- `feat(frontend): ...`
- `fix(backend): ...`
- `test: ...`
- `docs: ...`
- `chore(skill): ...`

如果变更跨多个关注点，按关注点拆分 commit。只有小且内聚的变更才适合一个 commit。

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

typed source 或公共契约变化时，优先使用可用的 broad verify 命令。范围较窄时，运行环境档案中与相关组件匹配的 build、test、lint、typecheck、schema 或 contract validation 命令。

跳过验证必须明确报告：

- 跳过的命令。
- 跳过原因。
- 剩余风险。

## CI/CD 检查

仅当环境档案确认存在 CI/CD workflow 时执行：

- 检查 workflow 文件是否覆盖相关变更区域。
- 确认 CI 是否包含 install、build、test、schema validation、migration deployment 和 deploy 步骤。
- 不得执行 release/deploy job。
- 检查结果应进入当前 Step 报告。

## 数据库迁移状态

当 `persistence.schema_paths` 或 `migration_paths` 中的文件变化时，最终 readiness 必须包含：

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

- `feat(<scope>): ...`
- `fix(<scope>): ...`
- `test(<scope>): ...`
- `docs(<scope>): ...`
- `chore(<scope>): ...`

`<scope>` 来自当前项目组件或模块，不得写死为某类技术栈。

如果变更跨多个关注点，按关注点拆分 commit。只有小且内聚的变更才适合一个 commit。

## 授权范围与越界检查

本 Step 的问题统一使用 `../SKILL.md` 定义的六种分类。除原有提交准备检查外，还必须检查：

- 实际修改文件是否全部位于 `editable_scope`。
- 修正批次是否只处理了授权 `issue_id`、`allowed_files` 和 `allowed_actions`。
- 是否出现未授权业务行为、API/数据/错误语义、状态/权限或实现方式变化。
- 是否为处理一个问题顺手修改相邻规范问题。
- 是否出现未经确认的新增或替换依赖。
- 是否混入范围外文档、测试、配置或其他工作区改动。

归类规则：

- 已授权批次内、无行为或实现变化且验证充分的提交准备问题：可归为 `safe_standard_correction`。
- diff 证明存在明确 Bug：归为 `confirmed_bug` 并转入 `confirmed_bugfix`。
- 风险存在但缺少唯一修正方式：归为 `report_only_risk`。
- 需要确认业务、测试或验收预期：归为 `incremental_design_required`。
- 需要拆分职责、移动模块或改变技术路径：归为 `refactor_assessment_required`。
- 越过授权、数据库、权限、生产、发布、安全策略或 Breaking API 边界：归为 `blocked_out_of_boundary`。

发现越界修改时立即停止，标记 `validation_failed` 或 `blocked_out_of_boundary`，报告实际 diff；不得自行删除、回滚或扩大权限。

继续禁止未经授权执行 stage、commit、push、merge、reset、checkout、stash、deploy、release 或数据库迁移。

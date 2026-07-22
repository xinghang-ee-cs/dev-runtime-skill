# 项目环境档案

本文件记录 `ai-code-inspection` 使用的稳定项目环境事实，不保存临时运行状态、Step 输出、命令日志、检查发现或执行历史。

本文件是未初始化模板。首次在目标项目使用前，必须只读扫描当前仓库的真实文件、manifest、workspace 配置、源码入口、测试配置、持久化定义和 CI/CD workflow，再填写本档案。不得从 Skill 示例或其他项目复制环境事实；档案与仓库冲突时，以当前仓库事实为准并纠正档案。

```yaml
profile_status: uninitialized

workspace:
  structure: null
  root_path: .
  package_managers: []
  languages: []
  workspace_tools: []
  root_scripts:
    build: null
    test: null
    lint: null
    typecheck: null
    verify: null

components: []

persistence: []

contracts: []

ci_cd:
  enabled: null
  platforms: []
  workflow_paths: []
  capabilities: []

validation_commands:
  broad_verify: []
  build: []
  test: []
  lint: []
  typecheck: []
  coverage: []
  schema_validate: []
  contract_validate: []
```

## 条目结构

`components` 支持任意数量的前端、后端服务、worker、CLI、共享包或其他组件。每个条目按仓库事实使用以下字段；不存在或无法确认的字段保持 `null` 或空列表，不得猜测：

```yaml
- id: null
  type: null
  path: null
  language: null
  framework: null
  runtime: null
  build_tool: null
  router_or_entry: null
  state_management: null
  validation_tool: null
  test_runners: []
  scripts:
    build: null
    test: null
    lint: null
    typecheck: null
    coverage: null
```

`persistence` 支持多个组件、数据库或其他持久化方案：

```yaml
- id: null
  component_id: null
  database: null
  orm_or_client: null
  schema_paths: []
  migration_paths: []
  generated_paths: []
  validation_commands: []
  migration_commands: []
  execution_policy: explicit_confirmation_required
```

`contracts` 支持多个公共契约来源：

```yaml
- id: null
  component_ids: []
  type: null
  paths: []
  generation_commands: []
  validation_commands: []
```

`validation_commands` 的数组项使用 `{ component_id, cwd, command }` 记录真实命令；工作区级命令的 `component_id` 使用 `workspace`。只记录项目实际存在的命令，不记录单次运行结果。

## 初始化与维护规则

- 单项目、多组件、monorepo、多语言、多持久化、多测试框架和多 CI workflow 都使用同一结构，不再预设固定的前端或后端槽位。
- 初始化完成且关键事实已由仓库证据确认后，将 `profile_status` 改为 `initialized`；存在未确认字段时在执行报告中说明，不把推测写入档案。
- 只有稳定项目事实变化时才更新本文件；临时范围、当前模式、修改权限、Step 状态和验证结果写入 `inspection-runtime-state.md`。
- 数据库或持久化执行默认要求用户明确确认目标、环境和具体命令；本 Skill 不因档案中存在命令而自动执行。

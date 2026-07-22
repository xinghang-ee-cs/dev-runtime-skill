# 项目执行基线

本文件是 Runtime State Template。

实例化位置：

```text
<phase_runtime_directory>/project-execution-baseline.md
```

禁止在本文件保存某个项目或期次的执行基线。在落地清单前置准备 Step 2“查看项目环境”结束后，只更新当前 Phase Runtime Directory 中的实例；后续只有当执行、委派、验证或复盘需要反查环境事实时读取该实例。

本文件只保存当前运行可复用的稳定环境事实；不记录阶段日志、事故过程、subAgent 反馈流水或临时决策。

## 使用规则

- 当前期次新 Runtime 开始时，创建或覆盖当前 Phase Runtime Directory 中的 Baseline 实例；不得覆盖 Skill 静态模板，也不得跨期复用实例。
- 只记录会影响后续拆分、委派、验证和复盘的事实。
- 不在此文件定义验证通过标准；验证证据口径由 `validation-gates.md` 定义。
- 不在此文件定义执行顺序或状态机规则；执行闭环由 `task-state-machine.md` 和 `task-execution.md` 定义。
- 如果基线在任务期间过期，先更新当前 Baseline，再继续执行。
- 本实例必须由 `current-runtime-context.md.project_execution_baseline_file` 指向，并在 `checkpoint-runtime.md.project_execution_baseline_status` 中记录 `current | stale | missing | invalidated`。
- Runtime 恢复必须读取当前期次 Baseline 实例；不得从本 Skill 静态模板恢复项目环境事实。

## 恢复与失效规则

依赖新增/升级/降级/替换、lockfile、Runtime/框架版本、构建工具、测试框架、环境变量或外部工具依赖发生变化时，必须校验 Baseline。

```text
project_execution_baseline_missing_or_stale
-> STOP
-> refresh_environment_baseline
-> update_current_phase_runtime_baseline
-> rerun_recovery_consistency_gate
```

Baseline 未恢复为 `current` 前不得继续实现。依赖相关任务必须确保 Baseline 的 package manager、lockfile、版本与政策事实同 Runtime Context、Checkpoint 和 Active Task 依赖字段一致。

## Baseline: <date> <plan-name>

- baseline_status: <current | stale | missing | invalidated>
- last_confirmed:
- 源计划：
- 当前分支/状态：
- 开发工具：
- package_manager:
- lockfile:
- runtime_versions:
- framework_versions:
- dependency_policy:
- official_registry_sources:
- 前端测试框架/命令：
- 前端覆盖率命令：
- 后端测试框架/命令：
- 后端覆盖率命令：
- API 文档工具：
- 架构边界：
- 当前协议：
- 相关已有模块：
- 验证命令：
- 已知本地约束：
- known_environment_constraints:

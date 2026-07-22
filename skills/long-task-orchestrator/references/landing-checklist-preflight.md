# 落地清单前置检查

本文件只定义 Preflight Gate：检查、停止条件、输出。

## 1. Preflight 用途

```text
planning_handoff_intake
confirm_source_of_truth
confirm_plan_readiness
confirm_capability_handoff
confirm_implementation_contract
confirm_implementation_placement
confirm_environment_baseline
confirm_dependency_governance
confirm_task_generation_inputs
```

## 2. 固定逻辑阶段与启动顺序

现有 Preflight 只分为以下三个逻辑阶段，不创建第二套 Preflight：

```text
Planning Handoff Intake
-> Runtime Bootstrap
-> Remaining Preflight Gates
```

固定启动顺序：

```text
load_skill
-> read 00-runtime-priority-rules.md
-> read context-lifecycle.md
-> run Planning Handoff Intake Gate
-> confirm handoff_type = execution_ready
-> confirm requires_execution_handoff = true
-> confirm formal execution and acceptance record files exist
-> confirm Source of Truth
-> load execution_constraints
-> create Phase Runtime Directory
-> instantiate current-runtime-context.md
-> instantiate checkpoint-runtime.md
-> instantiate required Runtime State files
-> inspect project environment
-> confirm package manager / lockfile / runtime / framework / existing modules
-> write Phase Runtime Directory/project-execution-baseline.md
-> mark project_execution_baseline_status = current
-> write project_execution_baseline_file pointer into current-runtime-context.md
-> sync checkpoint-runtime.md
-> continue remaining Preflight Gates
-> run Capability Gate if applicable
-> run Implementation Placement Gate
-> run Implementation Contract Completeness Intake
-> run Dependency Governance Gate if applicable
-> confirm task generation inputs
-> generate task.md
-> validate Runtime Context
-> explicitly open execution_gate
-> enter task-execution.md
```

```text
Planning Handoff Intake passed != full Preflight passed
Runtime Bootstrap completed != execution_gate_open
```

## 3. Planning Handoff Intake Gate

该 Gate 是 Preflight 第一项，顺序不可调整：

```text
读取 Planning Handoff
-> 确认 handoff_type
-> 确认 requires_execution_handoff
-> 读取 assembled_documents
-> 读取 handoff_role_mapping
-> 读取 execution_constraints
-> 读取 Development Landing Checklist
-> 确认正式执行记录与正式验收记录文件存在
-> 确认 Source of Truth
-> 通过后进入 Runtime Bootstrap
```

必须同时满足：

- `handoff_type: execution_ready`。
- `requires_execution_handoff: true`。
- Handoff 状态有效且未失效。
- Development Landing Checklist 真实存在且已确认；13 或等价正式落地清单已确认。
- 14、15 或等价执行/验收框架路径真实存在。
- Planning Handoff 声明的正式执行记录与正式验收记录文件均真实存在。
- `assembled_documents` 只包含真实路径。
- `handoff_role_mapping` 可解析。
- `execution_constraints` 存在且语义完整。
- 不存在阻断执行的 P0 `blocking_open`。
- 当前任务可追溯到正式 Planning 文档。

任一失败：

```text
planning_only_or_execution_handoff_false -> STOP
execution_constraints_missing -> STOP
landing_checklist_missing_or_unconfirmed -> STOP
P0_parameter_blocking_open -> STOP
handoff_formal_path_mismatch -> STOP
formal_execution_record_file_missing -> STOP
formal_acceptance_record_file_missing -> STOP
formal_acceptance_record_file_missing -> REPORT_HANDOFF_INCOMPLETE
formal_acceptance_record_file_missing -> WRITE_BACK_UPSTREAM
STOP -> do_not_create_task.md
STOP -> do_not_implement
```

禁止根据文件编号、当前存在的 13 文件、聊天记忆、期次名称、`task.md` 或历史 Runtime 反向猜测 Handoff 类型。

Intake Gate 可以在 Phase Runtime Directory 创建前运行。Intake 通过只允许进入 Runtime Bootstrap，不代表完整 Preflight 已通过，也不得打开 `execution_gate`。

## 4. Runtime Bootstrap

Planning Handoff Intake Gate 通过后，按以下顺序启动当前期次 Runtime：

```text
create Phase Runtime Directory
-> instantiate current-runtime-context.md
-> instantiate checkpoint-runtime.md
-> instantiate required Runtime State files
-> inspect project environment
-> confirm package manager / lockfile / runtime / framework / existing modules
-> write current phase project-execution-baseline.md
-> mark project_execution_baseline_status = current
-> write project_execution_baseline_file pointer into current-runtime-context.md
-> sync checkpoint-runtime.md
```

环境检查必须覆盖：

- 项目结构、模块边界、路由、前后端拆分、legacy 边界。
- 本地外部工具、数据库与 schema/ORM 工具、测试命令、开发/测试共享库、云端生产环境信息。
- 当前工作区状态与不可回退的本地改动。
- 清单对应的代码区域、已有实现、明显缺口和风险。
- 外部能力适用时的环境变量、网络、回调、额度、限流和计费约束。
- 项目现有包管理器、lockfile、Runtime/框架版本、现有模块与依赖政策。

Baseline 状态只能在环境检查完成并写入当前期次实例后变为 `current`。首次启动时 Baseline 尚不存在是正常 Bootstrap 输入：

```text
first_runtime_bootstrap
+ Planning Handoff Intake passed
+ Phase Runtime Directory not yet created
+ Baseline not yet created
-> create Runtime Directory and Runtime State
-> inspect environment
-> create Baseline instance
-> mark baseline current
-> continue Remaining Preflight Gates
```

不得将首次 Baseline 缺失视为 `Runtime Recovery Failed`。

已有 Runtime 的恢复不属于首次 Bootstrap：

```text
existing_runtime_recovery
+ project_execution_baseline_file missing
or project_execution_baseline_status in stale|missing|invalidated
-> execution cannot resume
-> STOP
-> refresh_environment_baseline
-> update current phase Baseline
-> rerun Runtime Recovery Consistency Gate
```

## 5. Remaining Preflight Gates：计划与 Capability

Runtime Bootstrap 完成后，完整 Preflight 才继续执行以下门禁：

```text
Capability Gate if applicable
-> Implementation Placement Gate
-> Implementation Contract Completeness Intake
-> Dependency Governance Gate if applicable
-> confirm task generation inputs
```

检查落地文档：

- 用户指定的计划、落地清单或实现清单可读。
- Source of Truth 已由 planning handoff 或用户确认，且只有一个当前有效路径。
- Planning Handoff、`execution_constraints` 与正式文档路径一致。
- 默认 Source of Truth 为 planning handoff 指定的 `Development Landing Checklist`；不得通过文件编号猜测路径。
- 计划目录任务的上游文档存在、非占位、无阻塞待确认项。
- 清单包含用户旅程、验收步骤、端到端闭环、使用者视角验收、高风险流程和验证门禁。
- 清单中的任务必须可追溯到 Planning 文档 ID；Planning ID 只作追踪，不得成为任何实现资产命名来源。涉及外部能力时还必须包含 CAP-ID。
- 清单足以指导环境确认和任务生成。

检查 Capability Handoff：

- 若任务涉及外部能力、SDK、OpenAPI、MCP、AI Provider、基础设施依赖或第三方平台，必须存在并读取 planning handoff 指定的 `Capability Governance` 文档。
- Capability Registry 已登记相关 CAP-ID。
- 官方 SoT、SDK/API/OpenAPI/MCP 版本、鉴权、请求结构、响应结构、错误码来源已确认。
- Evidence Gate 已通过，或明确标注不适用。
- 最小真实调用验证已有证据，或在 planning 层标记为 BLOCKER 且不得执行 implementation。
- 降级策略和人工介入策略已定义。
- Mock 只能作为测试替身，不得作为生产真实能力验收证据。

## 6. Implementation Placement Gate

每个执行单元生成前必须在现有代码与正式架构依据中按顺序判断：

```text
extend_existing_domain
-> reuse_shared_capability
-> create_stable_business_domain
```

`create_stable_business_domain` 仅在以下条件全部成立时允许：

- 现有业务域无法合法承接，且不存在可复用共享能力。
- 新建原因不是期次、阶段、Sprint、版本、任务或 Planning ID。
- Planning 09 或等价正式架构文档提供明确依据。
- 业务概念跨期稳定。
- 数据、接口、权限、状态与模块职责边界清楚。
- 不形成重复能力，名称通过稳定业务命名检查。

缺少任何一项：`STOP -> WRITE_BACK_UPSTREAM`。

## 7. Implementation Contract Completeness Intake

对当前 TASK 实际涉及的业务参数逐项复核；状态只允许：

```text
confirmed
explicitly_delegated
not_applicable
blocking_open
```

动态检查文件/MIME/大小/数量/替换/删除/失败、重试/超时、分页/范围/默认值/精度/时区、空值/空结果/唯一性/排序、状态、权限、API 请求响应/错误码、用户可见异常及外部能力失败/降级等适用参数。

```text
all_affected_parameters in confirmed|explicitly_delegated|not_applicable
-> contract_intake_passed

any_affected_parameter = blocking_open
or missing_business_or_contract_parameter
-> CURRENT_TASK_BLOCKED
-> execution_gate_closed_for_task
-> WRITE_BACK_UPSTREAM
-> DO_NOT_IMPLEMENT
```

不得以“开发时再决定”“行业常见”或“先给默认值”继续。

## 8. Dependency Governance Gate

任何依赖新增、升级、降级或替换前必须按唯一顺序检查：

```text
确认项目现有 package manager
-> 检查 lockfile
-> 检查现有依赖能否满足
-> 检查是否存在重复能力
-> 从官方 Registry、Release 或文档确认稳定版本
-> 检查框架和 Runtime 兼容性
-> 检查安全或弃用状态
-> 记录版本选择依据
-> 明确 lockfile 影响
-> 明确验证命令
-> 才允许安装
```

必须沿用项目现有 npm/pnpm/yarn/bun，不得无依据使用 npm 或生成多个 lockfile；优先复用现有依赖，禁止重复功能包。不得凭模型记忆宣称“最新”；官方版本来源不可访问时，不得声称最新或安装，兼容性不可确认时必须阻断或取得明确授权。记录引入原因、版本、官方来源、替代方案、lockfile 影响和验证结果。lockfile 与安装继续作为 P0 串行边界。

Gate 状态语义：

```text
no_dependency_change -> not_applicable
dependency_change_and_gate_passed -> passed
dependency_version_source_compatibility_or_lockfile_unclear -> blocked

dependency_governance_status = blocked
-> execution_gate_closed_for_task
-> CURRENT_TASK_BLOCKED
-> DO_NOT_INSTALL
-> DO_NOT_IMPLEMENT
```

`dependency_governance_status` 必须同步到 Preflight Result、Runtime Context、Checkpoint、Project Execution Baseline 与 Active Task；`pending` 或 `blocked` 均不得打开 execution gate。

## 9. Task Generation 输入检查

检查 task generation 输入：

- `delegation-rules.md` 可读。
- `task-state-machine.md` 可读。
- `context-lifecycle.md` 可读。
- `system-topology.md` 可读。
- Source of Truth 可派生 `task.md`。
- 执行单元可追溯到 Source of Truth。
- 每个执行单元已有稳定业务概念、实现承接策略、禁止实现命名和参数合同状态。
- 执行顺序、依赖、所有权、共享边界、验证方式和完成证明具备生成依据。
- 涉及外部能力的执行单元必须带 CAP-ID、官方 SoT、SDK/API 版本、最小验证方式和降级策略。

## 10. 停止条件

```text
missing_source_of_truth -> STOP
invalid_planning_handoff_intake -> STOP
missing_execution_constraints -> STOP
upstream_plan_blocked -> STOP
plan_conflict -> STOP
implementation_placement_unconfirmed -> STOP
new_domain_without_architecture_basis -> STOP
missing_business_or_contract_parameter -> STOP
dependency_governance_failed -> STOP
formal_acceptance_record_file_missing -> STOP
missing_user_journey -> STOP
missing_acceptance_path -> STOP
missing_capability_registry -> STOP
capability_evidence_gate_blocked -> STOP
external_capability_version_unclear -> STOP
external_capability_auth_unclear -> STOP
external_capability_contract_unclear -> STOP
external_capability_real_validation_missing -> STOP
missing_environment_baseline -> STOP
unclear_ownership_boundary -> STOP
unclear_shared_boundary -> STOP
unreadable_required_reference -> STOP
```

## 11. 完成条件

```text
source_of_truth_confirmed
planning_handoff_intake_passed
execution_constraints_loaded
phase_runtime_directory_created
runtime_state_instantiated
project_execution_baseline_status_current
project_execution_baseline_pointer_written
checkpoint_runtime_synced
upstream_plan_ready
capability_handoff_passed_or_not_applicable
implementation_contract_inputs_complete
implementation_placement_inputs_complete
environment_baseline_confirmed
dependency_governance_passed_or_not_applicable
task_generation_inputs_ready
no_blocking_question
```

```text
preflight_not_passed -> execution_gate_closed
execution_gate_closed -> DO_NOT_IMPLEMENT
```

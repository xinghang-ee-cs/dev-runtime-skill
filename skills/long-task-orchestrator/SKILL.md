---
name: long-task-orchestrator
description: 当 Agent 必须接收已确认且 execution_ready 的 planning handoff，按其中的执行约束、稳定业务命名、实现合同和承接位置执行一个至少包含 4 个实现单元的完整功能或模块时使用。负责从开发开始到 ready_for_local_test，或在确认 testing/用户缺陷反馈后 patch 到 ready_for_local_retest：实现、重构、数据迁移、自动化测试代码编写与执行、结果记录及 Long Testing Handoff；不负责补写 Planning 业务合同、人工测试、真实设备测试、云端验证、最终验收或上线放行。
---

# 长任务编排器

## 用途

接收已确认的 `execution_ready` Planning Handoff，将正式开发任务转换为 Runtime Task，按既定架构、合同、参数和命名边界完成实现与开发期自动化验证，回写执行事实并形成 Long Testing Handoff。

不得重新访谈业务需求、自行补充用户可见业务规则、修改 Planning 正式需求、替 Planning 决定未确认业务参数，或接管最终验收、服务器/生产验证、发布批准及 Testing Skill 工作流。Planning Handoff 不完整或冲突时，停止当前实现并写回上游。

## Source of Truth

实现类长任务的 Source of Truth 必须是 planning handoff 明确确认的单一计划、落地清单或实现清单。

确认后的 SoT 路径只写入 Phase Runtime Directory 的 `current-runtime-context.md` 和 `checkpoint-runtime.md`。

`task.md` 只能作为 Phase Runtime Directory 的 Runtime control table。

`task.md` != Source of Truth。

`implementation` != `requirement_source`。

## Runtime Gate

进入 implementation 前必须完成：

```text
skill_loaded
runtime_kernel_loaded
source_of_truth_confirmed
planning_handoff_intake_passed
execution_constraints_loaded
phase_runtime_directory_created
runtime_state_instantiated
project_execution_baseline_status_current
preflight_passed
task_runtime_generated
runtime_context_valid
lifecycle_order_valid
implementation_contract_complete_for_task
implementation_placement_confirmed_for_task
dependency_governance_passed_or_not_applicable
execution_gate_open
```

任一条件不满足：

```text
execution_gate_closed
-> STOP
-> DO_NOT_IMPLEMENT
-> REPORT_BLOCKER
```

禁止：

```text
gate_failed_but_continue
missing_runtime_but_continue
missing_task_md_but_continue
preflight_failed_but_continue
source_of_truth_missing_but_continue
skill_reference_state_resume
```

```test
execution_gate_open must be explicitly declared after all gate conditions pass.
implicit_gate_open -> forbidden
```

## Runtime Ownership

```text
Skill references
=
Runtime Kernel
Runtime Procedure
Runtime State Template

Phase Runtime Directory
=
当前期次 Runtime State
当前期次 Runtime Log
当前期次 Runtime Recovery Data
```

Phase Runtime Directory 是当前期次 Runtime 目录：

```text
<phase_runtime_directory>/
```

Phase Runtime Directory 属于项目资产，属于当前期次资产，默认长期保留，直到项目交付。所有本期开发状态只能写入该期目录，不得写入项目根目录 `.runtime/`；`.runtime/` 只供各 Skill 维护跨期项目级状态。

### Phase Runtime Path Binding

`<phase_runtime_directory>` 由当前有效 Planning Handoff、目标项目的期次目录约定和已有 Runtime 事实共同解析，不是固定目录名。

```text
phase_runtime_directory
= 当前 planning handoff 对应的项目级 Runtime 目录
```

- 优先采用 Handoff 明确声明的 Runtime 位置；未声明时，从已确认的当前规划目录和项目约定派生。
- `<phase_runtime_directory>`、`<phase_planning_directory>`、`<planning_handoff_path>` 与 `<development_landing_checklist_path>` 仅为静态模板占位符，实例化前必须解析为目标项目真实路径。
- 不得沿用来源项目的目录、期次名称、绝对路径或历史 Runtime 位置。
- 目标位置无法唯一确认、Handoff 与项目事实冲突或写入权限不足时，关闭 execution gate 并报告阻断。
- 路径抽象只改变 Runtime 落点，不改变 Intake、Preflight、Task、Validation、Handoff、Completion 或 Patch 生命周期。

## Runtime 文件分层

Level 0（Skill Immutable）保留在 `skills/long-task-orchestrator/references/`。

Level 0 只允许 Runtime Kernel、Runtime Procedure 与 Runtime State Template，不允许 Runtime State。

Runtime Kernel 与 Runtime Procedure 例如：

- `00-runtime-priority-rules.md`
- `context-lifecycle.md`
- `task-state-machine.md`
- `system-topology.md`
- `task-execution.md`
- `validation-gates.md`
- `retrospective.md`
- `delegation-rules.md`
- `landing-checklist-preflight.md`

Skill references 不得保存某一期项目运行状态。

`skills/long-task-orchestrator/`、`references/` 与 `agents/` 只能保存静态 Skill 内容。不得保存项目/期次 Runtime Context、Checkpoint、task、事件、验证结果、Agent 决策、调试记录、基线实例、用户输入、项目路径实例或任何可恢复项目状态。Markdown Schema 与未填写占位示例允许存在。

Phase Runtime Directory 保存当前期次 Runtime State、Runtime Log 与 Runtime Recovery Data，例如：

```text
<phase_runtime_directory>/
```

Phase Runtime Directory 包含：

- `current-runtime-context.md`
- `checkpoint-runtime.md`
- `project-execution-baseline.md`
- `task.md`
- `execution-events.md`
- `validation-results.md`
- `testing-handoff.md` 或 `long-runtime-testing-summary.md`
- `agent-decisions.md`
- `temporary-execution-log.md`

`skills/long-task-orchestrator/references/` 中同名文件只能作为 Runtime State Template，不得作为恢复源。

## Runtime 启动

Skill Runtime 加载层：

```text
SKILL.md
-> 00-runtime-priority-rules.md
-> context-lifecycle.md
-> task-execution.md
```

## Runtime Instantiation Rule

执行开始：

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
-> generate Phase Runtime Directory/task.md
-> validate Phase Runtime Directory/current-runtime-context.md
-> explicitly open execution_gate
-> enter task-execution.md
```

```text
Planning Handoff Intake passed != full Preflight passed
Runtime Bootstrap completed != execution_gate_open
```

恢复执行：

```text
load_skill_runtime
-> locate current Phase Runtime Directory
-> read Phase Runtime Directory/current-runtime-context.md
-> read Phase Runtime Directory/checkpoint-runtime.md
-> read current valid Planning Handoff
-> read Phase Runtime Directory/project-execution-baseline.md
-> read current-stage Source of Truth
-> read Phase Runtime Directory/task.md
-> read Phase Runtime Directory/execution-events.md
-> run Runtime Recovery Consistency Gate
-> resume current step
```

首次 Runtime Bootstrap 与已有 Runtime 恢复必须区分：

```text
first_runtime_bootstrap
+ baseline file not yet created
-> create Runtime State
-> inspect environment
-> create current phase Baseline
-> mark baseline current
-> continue remaining Preflight Gates

existing_runtime_recovery
+ project_execution_baseline_file missing
or project_execution_baseline_status in stale|missing|invalidated
-> execution cannot resume
-> STOP
-> refresh_environment_baseline
-> update current phase Baseline
-> rerun Runtime Recovery Consistency Gate
```

首次启动时 Baseline 尚不存在不是 `Runtime Recovery Failed`；上述恢复阻断只适用于已有 Runtime。

禁止从 `skills/long-task-orchestrator/references/` 恢复某一期项目状态。

任何步骤失败，不得进入下一步。

任何步骤失败，不得执行 implementation。

## Planning Handoff

long-task-orchestrator 只能承接 Planning 已确认的 `execution_ready` Handoff。

### Planning Handoff Intake Gate

该 Gate 必须位于 Long Preflight 最前面，且顺序固定：

```text
读取 Planning Handoff
-> 确认 handoff_type
-> 确认 requires_execution_handoff
-> 读取 assembled_documents
-> 读取 handoff_role_mapping
-> 读取 execution_constraints
-> 读取 Development Landing Checklist
-> 读取 Capability Governance（适用时）
-> 检查关键参数状态
-> 检查实现命名和承接策略
-> 通过后才进入环境检查和 task.md 生成
```

合法入口必须同时满足 `requires_execution_handoff: true` 与 `handoff_type: execution_ready`，并确认 Handoff 有效、Development Landing Checklist 真实存在且已确认、14/15 或等价框架路径真实存在、`assembled_documents` 仅含真实路径、`handoff_role_mapping` 可解析、`execution_constraints` 存在、无 P0 `blocking_open`、任务可追溯且 Handoff 未失效。

以下任一条件必须停止，且不得生成 `task.md` 或开始 implementation：

```text
handoff_type = planning_only
requires_execution_handoff = false
execution_constraints = missing
Development Landing Checklist = missing_or_unconfirmed
P0 parameter_status = blocking_open
Handoff path != formal document path
```

不得根据文件编号、现存 13 文件、聊天记忆、期次名称、`task.md` 或历史 Runtime 反向猜测 Handoff 类型。

默认承接 `planning-layer-runtime` 的文档职责链路，而不是固定编号链路：

```text
Capability Governance
-> Test and Acceptance Plan
-> Risk, Dependency, and Open Questions
-> Development Landing Checklist
-> Execution and Integration Record
-> Acceptance and Retrospective Record
```

其中 `Development Landing Checklist` 是执行类任务的默认 handoff Source of Truth。实际文件路径必须由 planning handoff 或用户确认，不能由 long-task-orchestrator 通过编号猜测。

若任务涉及外部能力、SDK、OpenAPI、MCP、AI Provider、基础设施依赖或第三方平台，则必须同时读取 planning handoff 指定的 `Capability Governance` 文档，并确认 Capability Registry 与 Evidence Gate 已通过。

涉及设备 API、容器 SDK、定位、摄像头、麦克风、推送或其他外部平台能力时，Runtime 必须同时检查 Capability Evidence Gate 与 Capability Binding Gate。两者均通过后，才允许进入 implementation。

```text
planning_confirmed_development_landing_checklist
planning_capability_gate_passed_or_not_applicable
planning_capability_binding_gate_passed_or_not_applicable
-> allowed_to_start_runtime
```

禁止：

```text
unconfirmed_plan -> STOP
plan_document_incomplete -> STOP
plan_blocking_question_exists -> STOP
missing_capability_registry -> STOP
capability_evidence_gate_blocked -> STOP
capability_binding_gate_blocked -> STOP
external_capability_unverified_but_implemented -> DO_NOT_IMPLEMENT
implementation_before_planning_handoff -> DO_NOT_IMPLEMENT
```

执行承接：

```text
confirmed_source_of_truth -> Phase Runtime Directory/task.md
Phase Runtime Directory/task.md -> Phase Runtime Directory/execution-events.md / validation-results.md / agent-decisions.md
formal_execution_record -> planning handoff 指定的 Execution and Integration Record
formal_acceptance_record_reference -> planning handoff 指定的 Acceptance and Retrospective Record（read-only）
```

`task.md`、临时日志、聊天记录、subAgent 输出不得替代 planning 层正式执行记录和验收记录。

### Execution Constraints

必须读取 Planning Handoff 中的 `execution_constraints`，至少保留下列语义；等价字段可以映射，但不得丢失语义：

```yaml
planning_ids_are_trace_only:
stable_business_naming_required:
phase_based_implementation_names_forbidden:
existing_business_domain_preflight_required:
new_business_module_requires_architecture_basis:
data_domain_isolation_does_not_imply_phase_namespace:
```

在 `current-runtime-context.md` 中只保存 Handoff 路径、constraints 来源、Gate 状态和当前符合状态，不复制正文；Planning Handoff 始终是权威来源。

Planning 的 REQ/FLOW/SCN/DOMAIN/MODULE/ARCH/CAP/PAGE/UI-MOD/UX-SCN/STATE/API/PERM/TASK/TEST/RISK/DEP/OPEN/EXEC ID 只能用于文档、Runtime、验证、Handoff 与证据追踪，不得机械转换为目录、模块、代码符号、Schema、表/字段、API、权限、状态、配置、迁移、Seed、测试套件或 Feature Flag 名称。期次、阶段、Sprint、迭代、版本或 Planning 文档编号同样不得进入长期实现命名；实现必须采用跨期稳定的业务概念。

### Implementation Intake

每个执行单元生成前，按 `landing-checklist-preflight.md` 与 `task-state-machine.md` 完成：

```text
Implementation Placement Gate
-> Implementation Contract Completeness Intake
-> Dependency Governance Gate（涉及依赖变更时）
-> task.md Static Task Definition
```

承接策略只允许 `extend_existing_domain`、`reuse_shared_capability`、`create_stable_business_domain`，优先级依次如此。新建长期业务域必须具有正式架构依据和清晰、稳定、无重复的职责边界，否则停止并写回上游。

关键参数状态只允许 `confirmed`、`explicitly_delegated`、`not_applicable`、`blocking_open`。影响当前 TASK 的任一参数为 `blocking_open` 或缺失业务/合同参数时，当前 TASK 必须 `BLOCKED`，关闭该任务 execution gate，写回上游且不得实现。

Long 只能在 Planning 明确标记 `explicitly_delegated` 的私有、可逆、不影响用户可见行为/API/数据/权限/状态/验收且不创建公共语义的技术细节内决策，并写入 `agent-decisions.md`。

正式验收记录职责边界：

```text
formal_acceptance_record_path_defined
-> check_file_exists
-> if_exists: READ_AND_REFERENCE_ONLY
-> acceptance_status = not_started
-> acceptance_owner_runtime = testing-layer-runtime
```

Long 只允许在 Runtime Context 与 Long Testing Handoff 中保存正式验收记录路径及 Testing 所有权声明，不得修改正式验收文档正文。

若 Handoff 未声明正式验收记录路径，或声明路径对应文件不存在：

```text
formal_acceptance_record_path_missing
or formal_acceptance_record_file_missing
-> Planning Handoff Intake failed
-> STOP
-> REPORT_HANDOFF_INCOMPLETE
-> WRITE_BACK_UPSTREAM
-> DO_NOT_CREATE_TASK
-> DO_NOT_IMPLEMENT
```

Long 不得创建正式验收记录、创建占位文件、修改验收状态、填写人工/服务器/最终验收结果或标记 release ready。Execution and Integration Record 由 Plan 创建框架、Long 写入执行事实；Acceptance and Retrospective Record 由 Plan 创建框架、Testing 写入测试、验收和发布判断。

## Long Testing Handoff

long-task-orchestrator 在 `ready_for_local_test` 前必须写出 Long Testing Handoff：

```text
Phase Runtime Directory/testing-handoff.md
```

或：

```text
Phase Runtime Directory/long-runtime-testing-summary.md
```

该文件是 testing-layer-runtime 启动时继承自动化结果的事实源。

必须包含：

```yaml
automated_passed:
automated_failed:
automated_skipped:
manual_required:
coverage:
formal_acceptance_record_path:
acceptance_status: not_started
owner_runtime: testing-layer-runtime
```

字段规则：

- `automated_passed`：记录 long 已执行且通过的自动化验证，必须包含 evidence 引用。
- `automated_failed`：记录失败的自动化验证，必须包含失败摘要和 evidence 引用。
- `automated_skipped`：记录未执行或不可用的自动化验证，必须包含原因。
- `manual_required`：记录 testing-layer-runtime 后续负责的人工测试、真实设备测试、服务器/云端验证、外部能力验证、最终验收或上线前验证。
- `coverage`：记录自动化结果覆盖到的需求、任务、Capability、接口、权限、状态流或业务流程。
- `formal_acceptance_record_path`：只引用 Planning 已创建的正式验收记录路径。
- `acceptance_status` 固定为 `not_started`，`owner_runtime` 固定为 `testing-layer-runtime`；Long 不得据此写入正式验收记录。

以下自动化默认属于 long：

```text
vitest
jest
integration
api-test
playwright
```

禁止把 `manual_required` 中的项目标记为已通过。

## 生命周期顺序

```text
preflight -> execution -> retrospective
```

## 职责边界

long-task-orchestrator 负责：

- implementation
- refactor
- data migration
- code validation
- automated test code writing
- unit validation
- business automated validation
- integration/api-test/playwright automated execution
- automated validation result recording
- capability minimum validation
- Long Testing Handoff
- retrospective
- formal acceptance record path reference only

long-task-orchestrator 不负责：

- manual local testing
- real-device testing
- server/deployed environment verification
- final acceptance
- release gate
- create or write formal acceptance record

以上 testing / acceptance / release 工作由 testing skill 或 release gate skill 显式接管。

## Long Runtime Completion Boundary

long-task-orchestrator 的完成定义：

```text
implementation_done
+ code_quality_passed
+ function_unit_tests_passed
+ business_unit_tests_passed
+ contract_validation_passed
+ execution_constraint_validation_passed
+ minimum_capability_validation_passed_or_blocked
+ automated_validation_recorded
+ long_testing_handoff_written
+ no_unresolved_P0_validation_issue
```

`ready_for_local_test` 不是 Completion Boundary 前置条件，而是 Completion Rule 成功收敛后产生的 Runtime 输出状态。

```text
long_testing_handoff_written = false
-> completion_boundary_not_passed
-> do_not_produce ready_for_local_test
```

允许输出：

```text
ready_for_local_test
implementation_completed
unit_validation_passed
capability_minimum_validation_passed
testing-handoff.md
long-runtime-testing-summary.md
```

`ready_for_local_test` 只表示：

```text
implementation_done
+ automated_validation_completed_or_recorded
+ Long Testing Handoff written
```

不表示人工测试、真实设备测试、服务器/云端验证、最终验收或上线放行通过。

`ready_for_local_retest` 只表示 patch 实现和 patch 自动化验证完成，可交回 testing-layer-runtime 复测。

## Long Runtime Completion Rule

达到 Completion Boundary 后，long-task-orchestrator 必须按以下顺序收敛并结束：

```text
completion_boundary_passed
-> retrospective
-> execution_record_writeback
-> testing_handoff_writeback
-> runtime_checkpoint_writeback
-> runtime_archive
-> runtime_cleanup
-> implementation_completed
-> ready_for_local_test
-> record ready_for_local_test_since
-> runtime_closed
-> STOP
```

`runtime_cleanup` 负责：

- 清理当前进程中的临时上下文。
- 清理当前期次 Runtime 目录中明确标记为可清理的临时项。
- 保持 Skill 内始终只有静态内容。

不得删除：

- 当前期次 Runtime 目录。
- 当前期次 Runtime 日志。
- 当前期次 Validation 记录。
- 当前期次 Decision 记录。
- 当前期次 Recovery 数据。
- `current-runtime-context.md`、`checkpoint-runtime.md`、`project-execution-baseline.md`、`task.md`、`execution-events.md`、`validation-results.md`、`agent-decisions.md` 与 Testing Handoff。
- 正式执行记录、已记录的 P0/P1 决策，以及已填写的执行、验证或验收事实。

`ready_for_local_test` 之后不得继续选择下一执行单元。

禁止：

```text
auto_enter_acceptance_prep
auto_enter_human_environment_preparation
auto_wait_for_real_accounts
auto_wait_for_external_environment
auto_wait_for_local_test
```

禁止输出：

```text
final_acceptance_passed
release_ready
production_ready
local_test_passed
remote_integration_passed
final_test_passed
```

long-task-orchestrator 不负责执行或等待：

- 人工探索性测试
- 多端联调测试
- 真实业务终测
- UAT
- Release Gate
- 上线放行

## Testing Feedback Patch Runtime

当 testing-layer-runtime、人工本地测试或用户截图反馈确认存在开发缺陷时，long-task-orchestrator 可以重新进入 patch runtime。

触发条件：

```text
testing_feedback_defect
+ user_or_testing_runtime_confirmation
+ patch_scope_traceable_to_existing_SoT_or_confirmed_defect_source
+ no_new_unconfirmed_requirement
-> patch_runtime_allowed
```

Patch Runtime 必须复用主执行门禁，顺序固定：

```text
confirm_patch_source
-> confirm_patch_scope
-> confirm_existing_runtime_valid
-> reload_current_planning_handoff
-> recheck_execution_constraints
-> confirm_patch_traceable_to_existing_SoT_or_confirmed_defect
-> confirm_patch_does_not_require_full_replanning
-> run_Implementation_Placement_Gate
-> run_Implementation_Contract_Completeness_Intake
-> run_Dependency_Governance_Gate_if_applicable
-> run_Capability_Evidence_and_Binding_Gates_if_applicable
-> generate_patch_task
-> execute_patch
-> run_patch_automated_validation
-> run_patch_execution_constraint_validation
-> main_agent_review
-> update_validation_results
-> update_testing_handoff
-> update_checkpoint
-> ready_for_local_retest
-> STOP
```

Patch Task 必须使用 `task-state-machine.md` 定义的完整 Static Task Definition，包括与主任务相同的 Planning 追踪、稳定业务概念、execution constraints 来源、承接策略、现有业务域、新业务域依据、禁止命名、参数合同、明确委托参数及依赖变更字段；不得创建简化版 Patch Task Contract。

Patch 涉及依赖变化时必须针对当前 Patch 重新执行 Dependency Governance Gate，不得复用主 Runtime 的旧通过状态。

Patch Runtime 边界：

```text
patch_runtime != acceptance
patch_runtime != new_phase
patch_runtime != full_replanning
patch_runtime != release_gate
```

Patch Runtime 不得：

- 自动进入人工测试。
- 自动进入最终验收。
- 自动标记 release ready。
- 自动修改原始 Source of Truth。
- 扩大到未确认的新需求。
- 清空原 runtime 历史证据。
- 使用期次、阶段、Sprint、版本或 Planning ID 命名代码资产。
- 创建未规划的新业务模块。
- 修改未确认的 API、数据、权限、状态或租户边界。
- 自行补充业务参数或超出 `explicitly_delegated` 范围。
- 绕过 Dependency Governance Gate。

若缺陷证明上游 SoT 存在缺口，只能记录 `write-back_required` 并等待用户或上游流程确认。

## Patch Completion Rule

Patch Runtime 完成条件：

```text
patch_implementation_done
+ patch_automated_validation_recorded
+ patch_execution_constraint_validation_passed
+ patch_contract_consistency_passed
+ no_new_phase_based_implementation_name
+ no_unconfirmed_contract_change
+ testing_handoff_updated
+ checkpoint_updated
+ current_effective_status_updated
-> ready_for_local_retest
-> STOP
```

禁止：

```text
patch_completion must not reopen main runtime
patch_completion must not mark acceptance passed
patch_completion must not mark release ready
patch_completion must update current_effective_phase/current_effective_status
```

```text
patch_tests_passed but patch_execution_constraint_validation_failed
-> PATCH_NOT_DONE
-> CURRENT_PATCH_TASK_BLOCKED
```

测试通过不得覆盖 Patch 的命名、架构承接位置、参数或合同违规。

## 停止条件

```text
missing_source_of_truth
missing_runtime_kernel
missing_preflight
preflight_not_passed
missing_task_runtime
task_not_traceable_to_source_of_truth
invalid_runtime_context
invalid_lifecycle_order
missing_current_lifecycle_reference
execution_gate_closed
runtime_pollution_detected
```

STOP means:

- stop implementation
- report blocker
- do not self-resolve by assumption
- do not continue with partial runtime

## Runtime Pollution Detection

如果 `skills/long-task-orchestrator/references/` 存在某一期任务、执行记录、验证记录或决策记录，则：

```text
Runtime Pollution Detected
-> STOP
-> REPORT_BLOCKER
-> DO_NOT_RECOVER_FROM_SKILL
-> require explicit confirmed cleanup or relocation action
```

`runtime_cleanup` 不以 Skill 内项目实例为正常输入。若发现 Skill 实例态污染，必须停止并报告；清理仅覆盖当前进程临时上下文及当前期次 Runtime 中明确标记为可清理的临时项。

```text
runtime_cleanup != delete_phase_runtime_directory
runtime_cleanup != delete_runtime_logs
runtime_cleanup != delete_runtime_history
```

## 规则 Source of Truth

| 规则 | SoT |
| --- | --- |
| 不可变优先级 | `00-runtime-priority-rules.md` |
| Runtime 恢复 | `context-lifecycle.md` |
| 状态流转 | `task-state-machine.md` |
| 拓扑 | `system-topology.md` |
| 验证证据 | `validation-gates.md` |
| Planning Handoff Intake 与执行前门禁 | `landing-checklist-preflight.md` |

其他文件只能引用这些规则，不能重新定义。

## Checkpoint Runtime

长任务执行必须能只从文档恢复。

恢复执行前必须读取：

```text
Runtime Kernel
-> Phase Runtime Directory/current-runtime-context.md
-> Phase Runtime Directory/checkpoint-runtime.md
-> current valid Planning Handoff
-> Phase Runtime Directory/project-execution-baseline.md
-> current effective Source of Truth
-> Phase Runtime Directory/task.md
-> Phase Runtime Directory/execution-events.md
-> Runtime Recovery Consistency Gate
-> resume current step
```

禁止基于压缩前记忆直接继续。

checkpoint 只保存在 Phase Runtime Directory 中的当前有效恢复状态，可覆盖、可收敛，不做追加叙事日志。

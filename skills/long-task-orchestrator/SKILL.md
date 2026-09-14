---
name: long-task-orchestrator
description: 当 Agent 必须接收已确认且 execution_ready 的初始或增量 planning handoff，按其中的基线 revision、增量执行队列、执行约束、稳定业务命名、实现合同、UI/UX 精确绑定和承接位置执行一个至少包含 4 个实现单元的完整功能或模块时使用；也可接收 `bugfix-case/v1`，在不要求活动 Planning Runtime 或四个实现单元的情况下完成精确补丁。负责从开发开始到经必要验证矩阵证明真实构建/装载/启动及最小行为可用的 ready_for_local_test，或在确认缺陷后 patch 到 ready_for_local_retest / ready_for_bug_verification：实现、重构、数据迁移、前端合同落实、自动化测试代码编写与执行、结果记录及交接；不负责补写 Planning 业务合同、自行重设计、人工测试、真实设备测试、云端验证、最终验收或上线放行。
---

# 长任务编排器

## 用途

接收已确认的 `execution_ready` 初始或增量 Planning Handoff，只把其 `incremental_execution_contract` 明确允许的 TASK 转换为 Runtime Task，按既定架构、合同、参数和命名边界完成实现；从真实交付单元派生必要验证矩阵，证明适用的构建/装载/启动、配置、必需依赖和最小行为路径可用后，回写执行事实并形成 Long Testing Handoff。

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
planning_handoff_revision_consistency_passed
incremental_execution_contract_loaded
execution_constraints_loaded
execution_prerequisite_readiness_passed
frontend_contract_intake_passed_or_not_applicable
phase_runtime_directory_created
runtime_state_instantiated
project_execution_baseline_status_current
required_validation_matrix_complete
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

## Runtime Ownership and Bootstrap

Runtime 存储、路径绑定、首次 Bootstrap、已有 Runtime 恢复与失效传播的唯一详细规则在 `references/context-lifecycle.md`；启动顺序、Planning Handoff Intake 和 Remaining Preflight Gates 在 `references/landing-checklist-preflight.md`。进入实现前必须完整读取这两个文件，不得从本节摘要反向推测完整流程。

主文件只保留以下不可变边界：

- `skills/long-task-orchestrator/` 只保存静态 Kernel、Procedure、Schema 和未填写模板；禁止写入任何项目/期次 Runtime 事实。
- 当前期次状态、日志、证据和恢复数据只写入 Planning Handoff 与项目约定唯一解析的 `<phase_runtime_directory>`；项目根 `.runtime/` 只用于跨期项目级状态。
- 所有静态占位路径必须先解析为目标项目真实路径；冲突、不唯一或不可写时停止。
- Planning Handoff Intake 通过只允许 Runtime Bootstrap；Bootstrap 完成也不等于 `execution_gate_open`。
- 首次 Bootstrap 在环境扫描后创建 Baseline；已有 Runtime 缺失或过期 Baseline 时停止恢复。
- 恢复必须读取当前 Runtime Context、Checkpoint、Planning Handoff、Baseline、Task 和 Events，通过 Recovery Consistency Gate 后才继续；禁止依赖压缩前记忆或 Skill reference 中的实例状态。

## Planning Handoff

Planning Handoff Intake、revision/队列一致性、前置就绪、实现承接、依赖治理和正式记录权限的唯一详细规则在 `references/landing-checklist-preflight.md`、`references/task-state-machine.md` 和 `references/task-execution.md`。UI/UX 适用时还必须完整读取 `references/frontend-experience-execution.md`。

输入为 `bugfix-case/v1` 时改读 `references/bugfix-patch-runtime.md`，以 Case 的精确合同与原 Planning 引用替代活动期次 Handoff Intake；仍复用适用的实现、验证、依赖和 diff 门禁，但不套用“至少 4 个实现单元”或“必须恢复活动 Planning Runtime”的条件。

不可变 Intake 边界：

- 只接受当前有效且已确认的 `handoff_type: execution_ready` 与 `requires_execution_handoff: true`。
- 初始/增量 Handoff 必须按 canonical Gate 对账 `planning_baseline_revision`、可选 `active_change_revision`、六类互斥 TASK 队列、`prohibited_actions`、`execution_constraints` 和正式文档路径。
- `execution_prerequisite_readiness` 必须显式为 `before_long_status: passed`且 `unresolved_before_long: []`；Long 只消费引用与聚合结果，不复制配置正文、不读取秘密值，不把 `before_cloud_test | before_release` 误当当前阻断。
- 只有 `execute_only | resume_only | reexecute_affected_part` 可进入执行；`context_only | completed_locked | cancelled` 不得生成可执行任务。
- Planning ID 只作追踪，不得变成代码、Schema、API、权限、状态、配置、迁移或测试命名；实现使用稳定业务概念。
- 只能在 Planning 标记 `explicitly_delegated` 的私有、可逆、不改变外部合同的技术细节内自主决策，并写入 `agent-decisions.md`。
- Execution and Integration Record 可按 Handoff 写入执行事实；Acceptance and Retrospective Record 对 Long 始终是 `read_and_reference_only`。缺失任一正式记录文件时停止并回写 Planning，禁止 Long 创建占位验收文件。

## Long Testing Handoff

Long Testing Handoff 的唯一字段 schema、枚举与对账规则在 `references/validation-results.md#long-testing-handoff-summary`；Required Validation 通过语义在 `references/validation-gates.md`；UI/UX 汇总在 `references/frontend-experience-execution.md`。本文件不维护第二份 schema。

在任何 `ready_for_local_test | ready_for_local_retest` 之前，Long 必须在 Context 绑定的当前期次路径写入 Handoff，并确保：

- `runtime_epoch`、`planning_handoff_ref`、Planning/change revision、TASK contract revision、Matrix revision 和 effective validation ids 均可解析且彼此一致。
- 当前必需自动验证只能在最新有效证据全部通过时进入 `automated_passed`；失败、跳过、过期或缺失不得放行。
- `manual_required[].planning_test_refs` 与 Baseline `completeness_audit` 完全对账；人工、真机、云端、外部能力和最终验收仅移交 Testing，不得在 Long 写成通过。
- `acceptance_status: not_started`且 `owner_runtime: testing-layer-runtime`；Long 只引用正式验收记录路径。
- Handoff 写入后必须通过 `scripts/validate-long-readiness.sh`（Windows 使用同目录 `.ps1`；均调用唯一 Python 核心）的确定性对账；未通过时不得声明 ready。

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
- Required Validation Matrix 派生与完整性复核
- 自动化本地构建/打包、产物或装载、进程启动、运行配置绑定、必需依赖就绪及最小行为 smoke
- Local Runnable Gate
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

“manual local testing”不包含可自动执行的构建、产物/装载、进程启动、配置绑定、依赖就绪或最小行为 smoke；这些是 Long 的完成证明，禁止移交 Testing 后把当前 Runtime 标记为 ready。

## Long Runtime Completion Boundary

long-task-orchestrator 的完成定义：

```text
implementation_done
+ code_quality_passed
+ function_unit_tests_passed
+ business_unit_tests_passed
+ contract_validation_passed
+ frontend_contract_validation_passed_or_not_applicable
+ execution_constraint_validation_passed
+ minimum_capability_validation_passed_or_not_applicable
+ required_validation_matrix_current_and_complete
+ all_required_automated_validation_passed
+ local_runnable_gate_passed
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
+ current Required Validation Matrix complete
+ every required validation has current passed evidence
+ applicable build/package/artifact/load/config/dependency/boot/minimum-smoke postconditions passed
+ Local Runnable Gate passed
+ Long Testing Handoff written
```

不表示人工测试、真实设备测试、服务器/云端验证、最终验收或上线放行通过。

`ready_for_local_retest` 只表示 patch 实现完成、受影响的 Required Validation Matrix 已更新且全部必需项重新通过、Local Runnable Gate 恢复为 passed，可交回 testing-layer-runtime 复测。

## Long Runtime Completion Rule

计算完成状态前必须重新扫描当前交付单元，对照当前 Matrix revision 检查覆盖完整性，并按 `validation-gates.md` 重新计算 Local Runnable Gate。不得从 TASK 全部 `DONE`、主 Agent 复核、测试数量或“没有已记录失败”直接推导通过。手动核对后还必须运行确定性校验脚本；失败时人工判断不得覆盖。

达到 Completion Boundary 后，long-task-orchestrator 必须按以下顺序收敛并结束：

```text
completion_boundary_passed
-> completion_validation
-> ready_for_local_test
-> archive and close
-> write deterministic readiness receipt
-> STOP
```

只通过粗粒度前向状态机推进阶段；同一阶段内按既有依赖图并行，不为命令、图片或单项测试建立微状态。阻断停留在当前阶段，Planning revision 或 patch 形成新 cycle，不倒拨旧 cycle：

```bash
bash <long-skill-path>/scripts/validate-long-readiness.sh <runtime> --advance-workflow preflight
bash <long-skill-path>/scripts/validate-long-readiness.sh <runtime> --advance-workflow execution
bash <long-skill-path>/scripts/run-long-validation.sh <runtime> --requirement-id <REQ-ID> --validation-id <VALIDATION-ID> --attempt <N>
bash <long-skill-path>/scripts/validate-long-readiness.sh <runtime> --advance-workflow completion_validation
bash <long-skill-path>/scripts/validate-long-readiness.sh <runtime> --advance-workflow ready_for_local_test
bash <long-skill-path>/scripts/validate-long-readiness.sh <runtime> --expect-ready --write-receipt
```

Windows 用同参数调用 `.ps1`。所有 scope 内实现完成后，仍在 `execution` 阶段以“本期”为唯一正式闭环，为每个 required Matrix 项调用 runner，并把 execution receipt 绑定进 Validation Entry；TASK 局部检查不替代该验证，任一 probe 失败不得自写 `passed`。Patch 使用 `--advance-workflow patch_execution --cycle-kind patch --new-cycle` 开新 cycle，再依次进入 `patch_validation`、`ready_for_local_retest`；通常从 ready 开启，若进入 validation 后才发现必须修正，也从当前阶段新开 patch cycle，不回退旧 cycle。Receipt 是交给 Testing 前的最后一次写入；生成后任何 Runtime、合同、source 或证据变化都必须开启新的前向 patch cycle。阶段内任务可按既有规则并行，但同一 Runtime 的阶段迁移只由主 Runtime owner 串行调用。任一命令失败时保持当前阶段、记录 blocker；禁止手改 `long-workflow-state.json`、跳级、回退、归档或交接。

迁移命令表示“进入目标阶段”：进入 `execution / patch_execution` 时只要求执行合同和 Matrix 已可执行，允许交付文件仍为 `planned_in_confirmed_task`；实现完成后进入 `completion_validation / patch_validation` 才强制完整 source roots、机器计算 revision 和持久证据全部存在。不得用最终产物门禁阻止全新项目开始实现，也不得把 planned binding 直接带入 ready。

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

## Bugfix Fast Lane Patch Runtime

当输入是 ai-code-inspection 已确认并持久化的 `bugfix-case/v1` 时，完整读取 `references/bugfix-patch-runtime.md`。该模式独立于下方的期内 Testing Feedback Patch Runtime：它允许在来源期次已关闭或发布后直接消费 Bug 合同，产出 `01-long-patch-result.md` 与 `ready_for_bug_verification`，然后停止并交给 Testing。

Fast Lane 只豁免活动期次和最少四单元要求，不豁免精确 allowlist、回归、受影响验证矩阵、必要 build/typecheck/load、主 Agent diff 审查、GitHub Issue/分支/PR/CI/PR 合并以及合同变化退出门禁。

## Testing Feedback Patch Runtime

当 testing-layer-runtime、人工本地测试或用户截图反馈确认存在开发缺陷时，long-task-orchestrator 可以重新进入 patch runtime。

进入 Patch Runtime 前必须先消费上游的 Execution/Test Change Triage 结果，或按同一分类协议形成可审计判定：

```text
implementation_defect + current Planning contract remains valid -> fix_in_execution
test_defect -> return_to_testing
planning_gap -> reopen_current_planning
requirement_change -> reopen_current_planning
design_drift changing architecture/API/data/permission/state/UI/acceptance contract -> reopen_current_planning
deferred_improvement -> defer_or_reject_per_confirmed_disposition
```

只有 `fix_in_execution` 可以进入 Patch Runtime。需要 `reopen_current_planning` 时必须停止实现，交回 planning-layer-runtime 生成新的增量 Handoff；不得用 Patch 掩盖 Planning 缺口、需求变化或合同变化。

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
-> confirm_change_triage_disposition = fix_in_execution
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
-> rerun_affected_required_validation_matrix_items
-> recompute_Local_Runnable_Gate
-> run_patch_execution_constraint_validation
-> main_agent_review
-> update_validation_results
-> update_testing_handoff
-> deterministic_candidate_readiness_validation
-> ready_for_local_retest
-> record ready_for_local_retest_since
-> deterministic_ready_state_validation
-> update_checkpoint
-> STOP
```

Patch 使用与主 Runtime 相同的 `validate_long_readiness.py` 两段校验：写入 retest ready 前运行默认模式，写入状态和时间戳后运行 `--expect-ready`。任一失败都按主 Completion Rule 回写 `blocked`、保留证据并停止交接。

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

若缺陷证明上游 SoT 存在缺口、需求已变化或设计漂移改变正式合同，必须记录 Change Triage 证据并切回 planning-layer-runtime；只有新的增量 `execution_ready` Handoff 通过 revision 与队列校验后，Long 才能继续受影响范围。

## Patch Completion Rule

Patch Runtime 完成条件：

```text
patch_implementation_done
+ affected_required_validation_matrix_current
+ all_affected_required_validation_passed
+ local_runnable_gate_passed
+ patch_execution_constraint_validation_passed
+ patch_contract_consistency_passed
+ no_new_phase_based_implementation_name
+ no_unconfirmed_contract_change
+ testing_handoff_updated
+ deterministic_candidate_readiness_validation_passed
+ checkpoint_updated
+ current_effective_status_updated
+ deterministic_ready_state_validation_passed
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
| UI/UX 合同消费、偏差停止与验证 | `frontend-experience-execution.md` |

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

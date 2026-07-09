---
name: long-task-orchestrator
description: 当 Codex 必须根据已有 planning handoff、落地清单或实现清单执行一个完整功能或模块，并且该功能或模块包含至少 4 个实现单元时使用。负责从开发开始到 ready_for_local_test，或在确认 testing/用户缺陷反馈后 patch 到 ready_for_local_retest：实现、重构、数据迁移、自动化测试代码编写、单元测试、业务自动化测试、vitest/jest/integration/api-test/playwright 等自动化执行、自动化结果记录，以及 Long Testing Handoff；不负责人工测试、真实设备测试、云端验证、最终验收或上线放行。
---

# 长任务编排器

## 用途

基于已确认的 Source of Truth 执行长任务。

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
preflight_passed
phase_runtime_directory_created
runtime_state_instantiated
task_runtime_generated
runtime_context_valid
lifecycle_order_valid
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
docs/计划安排/<期次>/runtime/
```

Phase Runtime Directory 属于项目资产，属于当前期次资产，默认长期保留，直到项目交付。

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

Phase Runtime Directory 保存当前期次 Runtime State、Runtime Log 与 Runtime Recovery Data，例如：

```text
docs/计划安排/<期次>/runtime/
```

Phase Runtime Directory 包含：

- `current-runtime-context.md`
- `checkpoint-runtime.md`
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
-> confirm handoff Source of Truth
-> run landing-checklist-preflight.md
-> create Phase Runtime Directory
-> instantiate Runtime State from templates
-> generate_or_recover Phase Runtime Directory/task.md
-> validate Phase Runtime Directory/current-runtime-context.md
-> open execution_gate
-> enter task-execution.md
```

恢复执行：

```text
load_skill_runtime
-> locate current Phase Runtime Directory
-> read Phase Runtime Directory/current-runtime-context.md
-> read Phase Runtime Directory/checkpoint-runtime.md
-> read Phase Runtime Directory/task.md
-> read current-stage Source of Truth
-> resume
```

禁止从 `skills/long-task-orchestrator/references/` 恢复某一期项目状态。

任何步骤失败，不得进入下一步。

任何步骤失败，不得执行 implementation。

## Planning Handoff

long-task-orchestrator 只能承接 planning skill 已确认的开发落地清单。

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

涉及 JSAPI、RecorderManager、定位、摄像头、推送、小程序能力、企业协作平台能力、开放平台能力或其他平台能力时，Runtime 必须同时检查 Capability Evidence Gate 与 Capability Binding Gate。两者均通过后，才允许进入 implementation。

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
formal_acceptance_record -> planning handoff 指定的 Acceptance and Retrospective Record
```

`task.md`、临时日志、聊天记录、subAgent 输出不得替代 planning 层正式执行记录和验收记录。

正式验收记录门禁：

```text
formal_acceptance_record_path_defined
-> check_file_exists
-> if_missing_create_placeholder
-> status = not_accepted_waiting_testing_skill_or_manual_evidence
```

当 `formal_acceptance_record` 路径已由 planning handoff 或用户确认，但文件不存在时，long-task-orchestrator 必须在 Completion Boundary 后的 writeback 阶段创建占位正式验收记录。

创建占位正式验收记录不得触发 Acceptance Prep、人工环境准备或本地测试等待。

占位记录必须包含：

- 文档边界。
- 上游 SoT：Test and Acceptance Plan、Development Landing Checklist、Execution and Integration Record。
- 当前验收状态：未验收，等待 testing skill 显式接管。
- 已完成自动化验证索引。
- 待补证据：人工测试、真实设备、服务器/云端验证、外部能力最终验证、完整链路验收结果。
- 遗留事项与复盘占位。

禁止：

```text
missing_formal_acceptance_record_but_continue_to_acceptance_prep
placeholder_auto_enters_acceptance_prep
placeholder_auto_enters_human_environment_preparation
placeholder_marks_final_acceptance_passed
placeholder_marks_release_ready
placeholder_replaces_test_plan
placeholder_redefines_requirement_scope
```

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
```

字段规则：

- `automated_passed`：记录 long 已执行且通过的自动化验证，必须包含 evidence 引用。
- `automated_failed`：记录失败的自动化验证，必须包含失败摘要和 evidence 引用。
- `automated_skipped`：记录未执行或不可用的自动化验证，必须包含原因。
- `manual_required`：记录 testing-layer-runtime 后续负责的人工测试、真实设备测试、服务器/云端验证、外部能力验证、最终验收或上线前验证。
- `coverage`：记录自动化结果覆盖到的需求、任务、Capability、接口、权限、状态流或业务流程。

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

long-task-orchestrator 不负责：

- manual local testing
- real-device testing
- server/deployed environment verification
- final acceptance
- release gate

以上 testing / acceptance / release 工作由 testing skill 或 release gate skill 显式接管。

## Long Runtime Completion Boundary

long-task-orchestrator 的完成定义：

```text
implementation_done
+ code_quality_passed
+ function_unit_tests_passed
+ business_unit_tests_passed
+ contract_validation_passed
+ minimum_capability_validation_passed_or_blocked
+ automated_validation_recorded
+ long_testing_handoff_written
+ ready_for_local_test
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
retrospective
-> execution_record_writeback
-> testing_handoff_writeback
-> acceptance_placeholder_writeback
-> runtime_checkpoint_writeback
-> runtime_archive
-> runtime_cleanup
-> implementation_completed
-> ready_for_local_test
-> runtime_closed
-> STOP
```

`runtime_cleanup` 负责：

- 清除 Skill 内实例状态。
- 不在 Skill 内保留当前项目运行记录。
- 将 Skill 恢复到可复用状态。

不得删除：

- 当前期次 Runtime 目录。
- 当前期次 Runtime 日志。
- 当前期次 Validation 记录。
- 当前期次 Decision 记录。
- 当前期次 Recovery 数据。

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

Patch Runtime 顺序：

```text
confirm_patch_source
-> confirm_patch_scope
-> run_patch_preflight
-> generate_patch_task
-> execute_patch
-> validate_patch
-> update_validation_results
-> update_testing_handoff
-> update_checkpoint
-> ready_for_local_retest
-> STOP
```

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

若缺陷证明上游 SoT 存在缺口，只能记录 `write-back_required` 并等待用户或上游流程确认。

## Patch Completion Rule

Patch Runtime 完成条件：

```text
patch_implementation_done
+ patch_validation_recorded
+ testing_handoff_updated
+ checkpoint_updated
+ current_effective_status_updated
-> ready_for_local_retest
-> STOP
```

禁止：

```text
patch_completion must not reopen main runtime
patch_completion must not create final acceptance placeholder again unless missing
patch_completion must not mark acceptance passed
patch_completion must not mark release ready
patch_completion must update current_effective_phase/current_effective_status
```

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
-> migrate polluted state to current Phase Runtime Directory
-> convert Skill references back to Runtime State Template
-> recover only from Phase Runtime Directory
```

`runtime_cleanup` 只清理 `skills/long-task-orchestrator/references/` 中的实例态污染。

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

其他文件只能引用这些规则，不能重新定义。

## Checkpoint Runtime

长任务执行必须能只从文档恢复。

恢复执行前必须读取：

```text
Phase Runtime Directory/current-runtime-context.md
-> Phase Runtime Directory/checkpoint-runtime.md
-> 当前阶段 Source of Truth
```

禁止基于压缩前记忆直接继续。

checkpoint 只保存在 Phase Runtime Directory 中的当前有效恢复状态，可覆盖、可收敛，不做追加叙事日志。

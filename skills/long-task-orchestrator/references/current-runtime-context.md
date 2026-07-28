# 当前 Runtime 上下文模板

本文件是 Runtime State Template。

实例化位置：

```text
<phase_runtime_directory>/current-runtime-context.md
```

禁止在本文件保存某一期项目运行状态。

## Schema

```yaml
runtime_epoch:
context_version:
phase_runtime_directory:
runtime_mode:
based_on_plan:
recovery_source:
planning_handoff_source:
planning_baseline_revision:
active_change_revision:
incremental_execution_contract_snapshot:
execution_constraints_source:
execution_constraints_status:
implementation_contract_status:
dependency_governance_status:
capability_governance_source:
current_effective_phase:
current_effective_status:
active_patch_id:
patch_source:
last_patch_event:
last_validation_id:
ready_for_local_test_since:
ready_for_local_retest_since:
open_blockers:
open_manual_required:
invalidated_by:
recovery_required:
task_file:
checkpoint_file:
project_execution_baseline_file:
execution_events_file:
validation_results_file:
testing_handoff_file:
agent_decisions_file:
temporary_execution_log_file:
formal_execution_record:
formal_acceptance_record:
acceptance_status:
acceptance_owner_runtime:
active_task:
active_big_unit:
active_execution_unit:
last_completed_task:
last_updated:
```

## Template

```yaml
runtime_epoch: <project-phase-runtime-epoch>
context_version: 1
phase_runtime_directory: <phase_runtime_directory>
runtime_mode: main
based_on_plan: <confirmed Development Landing Checklist path>
recovery_source: <confirmed Development Landing Checklist path>
planning_handoff_source: <current valid Planning Handoff path>
planning_baseline_revision: <Planning Execution Baseline revision>
active_change_revision: <incremental Handoff revision; omit this key for initial Handoff>
incremental_execution_contract_snapshot:
  execute_only: []
  resume_only: []
  reexecute_affected_part: []
  context_only: []
  completed_locked: []
  cancelled: []
  prohibited_actions: []
execution_constraints_source: <field/path reference in Planning Handoff>
execution_constraints_status: <passed | failed | invalidated>
implementation_contract_status: <passed | blocked | pending>
dependency_governance_status: <passed | blocked | not_applicable | pending>
capability_governance_source: <confirmed Capability Governance path or null>
current_effective_phase: preflight.pending
current_effective_status: phase_runtime_directory_created
active_patch_id: null
patch_source: null
last_patch_event: null
last_validation_id: null
ready_for_local_test_since: null
ready_for_local_retest_since: null
open_blockers: []
open_manual_required: []
invalidated_by: null
recovery_required: false
task_file: <phase_runtime_directory>/task.md
checkpoint_file: <phase_runtime_directory>/checkpoint-runtime.md
project_execution_baseline_file: null
execution_events_file: <phase_runtime_directory>/execution-events.md
validation_results_file: <phase_runtime_directory>/validation-results.md
testing_handoff_file: <phase_runtime_directory>/testing-handoff.md
agent_decisions_file: <phase_runtime_directory>/agent-decisions.md
temporary_execution_log_file: <phase_runtime_directory>/temporary-execution-log.md
formal_execution_record: <planning handoff Execution and Integration Record path>
formal_acceptance_record: <planning handoff Acceptance and Retrospective Record path>
acceptance_status: not_started
acceptance_owner_runtime: testing-layer-runtime
active_task: null
active_big_unit: null
active_execution_unit: null
last_completed_task: null
last_updated: <ISO-8601 timestamp>
```

## Effective State Rule

字段语义：

```text
runtime_mode: main | patch
current_effective_phase: 当前唯一有效阶段
current_effective_status: 当前唯一有效状态
active_patch_id: 当前 patch id，没有则 null
patch_source: testing feedback / user confirmation / defect id，没有则 null
last_patch_event: 最近 patch event，没有则 null
last_validation_id: 最近有效验证 id
ready_for_local_test_since: 首次进入 ready_for_local_test 的时间
ready_for_local_retest_since: 最近一次进入 ready_for_local_retest 的时间
open_blockers: 当前仍有效阻塞项
open_manual_required: 交给 testing-layer-runtime 的人工/真实环境验证项
planning_baseline_revision: 当前实际消费的 Planning Execution Baseline revision
active_change_revision: 仅增量 Handoff 存在；初始 Handoff 必须省略字段而非写空值
incremental_execution_contract_snapshot: 当前 Handoff 六类 TASK 队列和 prohibited_actions 的恢复快照
formal_acceptance_record: 只读路径指针，不授权 Long 创建或写入正式验收记录
acceptance_status: Long 中固定为 not_started
acceptance_owner_runtime: 固定为 testing-layer-runtime
```

规则：

```text
checkpoint-runtime.md and current-runtime-context.md must agree on current_effective_phase
checkpoint-runtime.md and current-runtime-context.md must agree with Planning Handoff revisions and execution queue snapshot
dependency_governance_status must agree with Preflight Result, checkpoint, baseline, and active task
project_execution_baseline_file remains null during first bootstrap until the Baseline instance is written and marked current
once written, project_execution_baseline_file must point to current Phase Runtime Directory
patch segment must update current_effective_status
main runtime closed does not override active patch effective status
```

## Preflight Result Template

```text
skill_loaded = false
runtime_kernel_loaded = false
source_of_truth_confirmed = <path or false>
capability_governance_confirmed = <path or not_applicable>
planning_capability_gate_passed_or_not_applicable = false
planning_capability_binding_gate_passed_or_not_applicable = false
planning_handoff_intake_passed = false
planning_handoff_revision_consistency_passed = false
incremental_execution_contract_loaded = false
execution_constraints_loaded = false
phase_runtime_directory_created = false
runtime_state_instantiated = false
implementation_contract_complete_for_task = false
implementation_placement_confirmed_for_task = false
dependency_governance_passed_or_not_applicable = false
preflight_passed = false
task_runtime_generated = false
runtime_context_valid = false
lifecycle_order_valid = false
execution_gate_open = false
```

## Example

```yaml
runtime_epoch: <phase-name>-development-<date>
context_version: 1
phase_runtime_directory: <phase_runtime_directory>
project_execution_baseline_file: <phase_runtime_directory>/project-execution-baseline.md
based_on_plan: <development_landing_checklist_path>
recovery_source: <development_landing_checklist_path>
planning_handoff_source: <planning_handoff_path>
planning_baseline_revision: <planning-baseline-revision>
incremental_execution_contract_snapshot:
  execute_only: [<TASK-ID@contract-revision>]
  resume_only: []
  reexecute_affected_part: []
  context_only: []
  completed_locked: []
  cancelled: []
  prohibited_actions: []
execution_constraints_source: <Planning Handoff path>#execution_constraints
execution_constraints_status: passed
implementation_contract_status: passed
dependency_governance_status: not_applicable
acceptance_status: not_started
acceptance_owner_runtime: testing-layer-runtime
runtime_mode: main
current_effective_phase: execution.in_progress
current_effective_status: active
active_patch_id: null
active_task: <TASK-ID>
last_completed_task: <TASK-ID or null>
```

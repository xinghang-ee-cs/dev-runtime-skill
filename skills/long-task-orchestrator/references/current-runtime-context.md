# 当前 Runtime 上下文模板

本文件是 Runtime State Template。

实例化位置：

```text
docs/计划安排/<期次>/runtime/current-runtime-context.md
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
execution_events_file:
validation_results_file:
testing_handoff_file:
agent_decisions_file:
temporary_execution_log_file:
formal_execution_record:
formal_acceptance_record:
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
phase_runtime_directory: docs/计划安排/<期次>/runtime
runtime_mode: main
based_on_plan: <confirmed Development Landing Checklist path>
recovery_source: <confirmed Development Landing Checklist path>
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
task_file: docs/计划安排/<期次>/runtime/task.md
checkpoint_file: docs/计划安排/<期次>/runtime/checkpoint-runtime.md
execution_events_file: docs/计划安排/<期次>/runtime/execution-events.md
validation_results_file: docs/计划安排/<期次>/runtime/validation-results.md
testing_handoff_file: docs/计划安排/<期次>/runtime/testing-handoff.md
agent_decisions_file: docs/计划安排/<期次>/runtime/agent-decisions.md
temporary_execution_log_file: docs/计划安排/<期次>/runtime/temporary-execution-log.md
formal_execution_record: <planning handoff Execution and Integration Record path>
formal_acceptance_record: <planning handoff Acceptance and Retrospective Record path>
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
```

规则：

```text
checkpoint-runtime.md and current-runtime-context.md must agree on current_effective_phase
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
preflight_passed = false
phase_runtime_directory_created = false
runtime_state_instantiated = false
task_runtime_generated = false
runtime_context_valid = false
lifecycle_order_valid = false
execution_gate_open = false
```

## Example

```yaml
runtime_epoch: <phase-name>-development-<date>
context_version: 1
phase_runtime_directory: docs/计划安排/<期次>/runtime
based_on_plan: docs/计划安排/<期次>/<Development Landing Checklist>.md
recovery_source: docs/计划安排/<期次>/<Development Landing Checklist>.md
runtime_mode: main
current_effective_phase: execution.in_progress
current_effective_status: active
active_patch_id: null
active_task: <TASK-ID>
last_completed_task: <TASK-ID or null>
```

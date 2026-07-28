# Runtime Checkpoint 模板

本文件是 Runtime State Template。

实例化位置：

```text
<phase_runtime_directory>/checkpoint-runtime.md
```

禁止在本文件保存某一期项目恢复状态。

## Schema

```yaml
runtime_epoch:
context_version:
runtime_mode:
current_effective_phase:
current_effective_status:
active_patch_id:
current_sot:
planning_handoff_source:
planning_baseline_revision:
active_change_revision:
incremental_execution_contract_snapshot:
execution_constraints_status:
implementation_contract_status:
active_placement_decision:
dependency_governance_status:
project_execution_baseline_status:
completed:
pending:
validation_state:
runtime_risks:
open_blockers:
open_manual_required:
resume_entry:
last_updated:
```

## Template

## Current Effective State

```yaml
runtime_mode: <main | patch>
current_effective_phase: <preflight.pending | execution.in_progress | validation.in_progress | retrospective.in_progress | runtime.closed | patch.in_progress | patch.validation | patch.ready_for_local_retest>
current_effective_status: <current status>
active_patch_id: <patch id or null>
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
execution_constraints_status: <passed | failed | invalidated>
implementation_contract_status: <passed | blocked | pending>
active_placement_decision: <extend_existing_domain | reuse_shared_capability | create_stable_business_domain | null>
dependency_governance_status: <passed | blocked | not_applicable | pending>
project_execution_baseline_status: <current | stale | missing | invalidated>
```

首次 Runtime Bootstrap 中，Baseline 实例写入前允许暂时为 `missing`；环境检查并写入实例后必须同步为 `current`，才能继续 Remaining Preflight Gates。只有已有 Runtime 恢复时的 `missing | stale | invalidated` 才触发 `STOP -> refresh_environment_baseline -> rerun Runtime Recovery Consistency Gate`。

---

## Current SoT

- `<confirmed Development Landing Checklist path>`
- `<current valid Planning Handoff path>`
- `<confirmed Capability Governance path or not_applicable>`
- `<Phase Runtime Directory/project-execution-baseline.md>`
- `<Phase Runtime Directory/task.md>`

---

## Completed

- `<completed runtime fact>`

---

## Pending

- `<pending runtime fact>`

---

## Validation State

| item | status |
| --- | --- |
| source of truth | `<status>` |
| project execution baseline | `<current | stale | missing | invalidated>` |
| task runtime | `<status>` |
| execution gate | `<status>` |

---

## Runtime Risks

- `<risk or none>`

---

## Open Blockers

- `<current blocker or none>`

---

## Open Manual Required

- `<manual_required item or none>`

---

## Resume Entry

Next step:
`<single concrete recovery step>`

## Example

```yaml
runtime_epoch: <phase-name>-development-<date>
context_version: 1
runtime_mode: main
current_effective_phase: execution.in_progress
current_effective_status: active
active_patch_id: null
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
execution_constraints_status: passed
implementation_contract_status: passed
active_placement_decision: extend_existing_domain
dependency_governance_status: not_applicable
project_execution_baseline_status: current
current_sot:
  - <development_landing_checklist_path>
completed:
  - <TASK-ID> implementation completed
pending:
  - validate <TASK-ID>
open_blockers: []
open_manual_required: []
resume_entry: validate <TASK-ID> before selecting the next task
```

# Runtime Checkpoint 模板

本文件是 Runtime State Template。

实例化位置：

```text
docs/计划安排/<期次>/runtime/checkpoint-runtime.md
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
```

---

## Current SoT

- `<confirmed Development Landing Checklist path>`
- `<confirmed Capability Governance path or not_applicable>`
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
current_sot:
  - docs/计划安排/<期次>/<Development Landing Checklist>.md
completed:
  - <TASK-ID> implementation completed
pending:
  - validate <TASK-ID>
open_blockers: []
open_manual_required: []
resume_entry: validate <TASK-ID> before selecting the next task
```

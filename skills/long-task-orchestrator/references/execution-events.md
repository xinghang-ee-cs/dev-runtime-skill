# 执行事件模板

本文件是 Runtime State Template。

实例化位置：

```text
<phase_runtime_directory>/execution-events.md
```

禁止在本文件保存某一期项目执行事件。

## Runtime Session

```yaml
runtime_session_ref: <phase_runtime_directory>/current-runtime-context.md
```

## Schema

```yaml
event_id:
time:
lifecycle_event:
operation_type:
from_state:
to_state:
related_task:
status:
evidence_ref:
```

## Lifecycle Event

`lifecycle_event` 只允许：

```text
PRECHECK
TASK_STARTED
TASK_FINISHED
VALIDATION_ENTER
VALIDATION_EXIT
HANDOFF_WRITTEN
PATCH_STARTED
PATCH_FINISHED
RUNTIME_RECOVERED
RUNTIME_CLOSED
```

## Operation Type

`operation_type` 允许：

```text
preflight
implementation
validation
handoff
patch_intake
database_migration
test_runtime_cleanup
runtime_recovery
retrospective
```

规则：

```text
lifecycle_event controls runtime state transition
operation_type describes concrete execution operation
new operation_type requires agent decision if it touches P0/P1 boundary
```

## 禁止记录

- 测试命令
- Agent 讨论
- 验证细节
- HUMAN_GATE_ENTERED
- invent_unregistered_lifecycle_event
- use_operation_type_as_state_transition
- record_validation_detail_in_execution_events
- record_agent_decision_in_execution_events

## Template

```yaml
event_id: <EVENT-ID>
time: <ISO-8601 timestamp>
lifecycle_event: <allowed lifecycle event>
operation_type: <allowed operation type>
from_state: <runtime state>
to_state: <runtime state>
related_task: <TASK-ID or null>
status: <event status>
evidence_ref: <Phase Runtime Directory file or formal project record path>
```

## Example

```yaml
event_id: EVENT-001
time: <ISO-8601 timestamp>
lifecycle_event: TASK_FINISHED
operation_type: implementation
from_state: IN_PROGRESS
to_state: WAITING_VALIDATION
related_task: <TASK-ID>
status: implementation_completed
evidence_ref: <phase_runtime_directory>/task.md
```

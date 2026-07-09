# Runtime Decision Log

artifact_type: Project Runtime Evidence Template
governed_by: references/07-planning-conversation-runtime.md#113-decision-snapshot-runtime
append_only: true
default_loaded: false

not_sot: true
not_planning_context: true
not_handoff_package: true
not_capability_registry: true
not_acceptance: true
not_formal_document: true
not_long_term_memory: true

## Entries

Append Decision Snapshot entries below. Do not copy full chat, user input, AI output, CoT, or long analysis.

同一阶段同一结论禁止重复记录。

仅记录：

- 决策变化
- 风险变化
- 阻塞变化
- 恢复变化

```yaml
timestamp:
decision_id:
stage:
status:
current_understanding:
decision:
reason:
risk:
source:
impact:
supersedes:
next_action:
```

`status` 只允许：

```text
candidate
confirmed
superseded
rejected
```

# Runtime 优先级规则

本文件是 long-task-orchestrator 的 Runtime Immutable Kernel。

## 规则优先级

```text
Runtime Immutable
> Source of Truth
> Topology
> Lifecycle
> Task Runtime
> Temporary State
```

## Source of Truth

```text
formal_plan > task.md
task.md != formal_plan
implementation != requirement_source
temporary_log != execution_record
```

## Runtime 可恢复性

```text
long_running_execution -> recoverable_from_documents_only
resume_after_context_compression -> reconstruct_from_sot_and_checkpoint
memory_only_resume -> forbidden
```

## 完成规则

```text
missing_completion_proof -> NOT_DONE
missing_validation_evidence -> NOT_DONE
validation_unavailable_without_record -> NOT_DONE
unchecked_item -> NOT_PASSED
```

## 变更规则

```text
implicit_contract_change -> STOP
implicit_permission_change -> STOP
implicit_state_change -> STOP
implicit_data_model_change -> STOP
implicit_tenant_boundary_change -> STOP
plan_deviation -> WRITE_BACK_UPSTREAM_FIRST
low_risk_assumption -> MARK_AND_RECOVER_BEFORE_ACCEPTANCE
```

## 多 Agent 规则

```text
shared_boundary_parallel_write -> STOP
subagent_output -> REVIEW_BEFORE_ADOPT
P0_boundary -> MAIN_AGENT_SERIAL
```

## 停止条件

```text
unresolved_high_risk
plan_conflict
task_not_traceable_to_formal_plan
validation_unavailable_without_alternative_evidence
agent_ownership_conflict
```

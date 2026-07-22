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
planning_handoff_execution_constraints > runtime_derived_decision
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
missing_business_or_contract_parameter -> STOP
plan_deviation_affects_architecture_or_contract -> STOP_IMPLEMENTATION
plan_deviation_affects_architecture_or_contract -> CURRENT_TASK_BLOCKED
plan_deviation_affects_architecture_or_contract -> WRITE_BACK_UPSTREAM_FIRST
plan_deviation_affects_architecture_or_contract -> WAIT_FOR_CONFIRMED_HANDOFF
unconfirmed_public_semantic_assumption -> STOP
explicitly_delegated_private_technical_detail -> RECORD_AGENT_DECISION
```

`explicitly_delegated_private_technical_detail` 只有同时满足以下条件才成立：

- Planning 参数状态为 `explicitly_delegated`。
- 仅影响私有技术实现，不影响用户可见行为、API、数据、权限、状态或验收。
- 可逆、不创建公共语义且不突破任务边界。
- 决策写入当前期次 `agent-decisions.md`。

文件大小/数量、用户超时体验、API 默认值、权限结果、状态迁移、删除行为、唯一性、公开错误码、用户提示、业务重试次数和验收标准不得按低风险假设补齐。

正式计划发生变化时：

```text
formal_plan_changed
-> INVALIDATE Runtime Context
-> BUMP context_version
-> INVALIDATE affected task
-> reload Source of Truth and current Planning Handoff
-> regenerate Runtime Context
-> regenerate affected task
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

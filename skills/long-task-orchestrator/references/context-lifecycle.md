# 上下文生命周期

## Context Metadata

```yaml
runtime_epoch:
context_version:
based_on_plan:
last_confirmed:
invalidated_by:
recovery_source:
runtime_mode:
current_effective_phase:
current_effective_status:
active_patch_id:
```

## Runtime State Ownership

```text
skills/long-task-orchestrator/references/ -> Runtime Kernel / Runtime Procedure / Runtime State Template
Phase Runtime Directory -> Runtime State / Runtime Log / Runtime Recovery Data
```

Phase Runtime Directory 是当前期次 Runtime 目录，示例：

```text
docs/计划安排/<期次>/runtime/
```

Phase Runtime Directory 属于项目资产，属于当前期次资产，默认长期保留，直到项目交付。

```text
Phase Runtime Directory != Temporary Workspace
Phase Runtime Directory != Skill Cache
Phase Runtime Directory != Cleanup Target
```

恢复时必须从当前 Phase Runtime Directory 恢复。

禁止：

```text
recover_project_state_from_skill_references
store_project_execution_record_in_skill_references
store_project_validation_record_in_skill_references
store_project_decision_record_in_skill_references
delete_phase_runtime_directory_during_cleanup
```

## 失效条件

```text
formal_plan_changed -> INVALIDATE
api_contract_changed -> INVALIDATE
data_model_changed -> INVALIDATE
permission_rule_changed -> INVALIDATE
state_flow_changed -> INVALIDATE
runtime_recovery_failed -> INVALIDATE
agent_boundary_conflict -> INVALIDATE
high_risk_deviation_accepted -> INVALIDATE
task_source_changed -> INVALIDATE
base_dependency_changed -> INVALIDATE
```

失效后：

```text
STOP
-> 设置 invalidated_by
-> 升级 context_version
-> 重新加载 Source of Truth
-> 重新生成 Runtime Context
```

## 恢复

读取：

```text
00-runtime-priority-rules.md
-> Phase Runtime Directory/current-runtime-context.md
-> Phase Runtime Directory/checkpoint-runtime.md
-> current effective Source of Truth
-> Phase Runtime Directory/execution-events.md
-> Phase Runtime Directory/task.md
-> 当前生命周期 reference
```

校验：

```text
runtime_epoch_match
context_version_match
invalidated_by_empty
source_of_truth_current
task_current
checkpoint_current_effective_phase_match
shared_boundary_clear
```

失败：

```text
STOP
-> 标记 Runtime Recovery Failed
-> 将当前运行设为 BLOCKED
-> 要求重新确认
```

## 版本升级

```text
formal_plan_changed -> BUMP
task_structure_changed -> BUMP
state_machine_changed -> BUMP
system_topology_changed -> BUMP
runtime_kernel_changed -> BUMP
lifecycle_rule_changed -> BUMP
P0_or_P1_boundary_changed -> BUMP
```

## 快照压缩

```text
long_runtime -> SNAPSHOT_ALLOWED
checkpoint-runtime.md -> ACTIVE_STATE_ONLY
checkpoint-runtime.md -> REPLACE_MUTABLE_CONTEXT_ONLY
snapshot != formal_plan
snapshot != validation_evidence
snapshot != retrospective
```

## Checkpoint Runtime

触发：

```text
long_stage_completed
before_new_stage
before_context_compression
long_execution_over_30_to_45_min
```

规则：

```text
Phase Runtime Directory/checkpoint-runtime.md -> Level_2_Runtime_Mutable
Phase Runtime Directory/checkpoint-runtime.md -> overwrite_current_effective_state
checkpoint-runtime.md != execution_log
checkpoint-runtime.md != architecture_analysis
checkpoint-runtime.md != validation_detail
old_checkpoint -> retrospective
```

## 清理

```text
old_temporary_execution_log -> CLEANABLE
expired_validation_cache -> CLEANABLE
invalid_recovery_snapshot -> CLEANABLE
low_value_temporary_analysis -> CLEANABLE
skill_reference_project_state -> CLEANABLE
formal_plan -> NOT_CLEANABLE
formal_execution_record -> NOT_CLEANABLE
formal_acceptance_record -> NOT_CLEANABLE
phase_runtime_directory -> NOT_CLEANABLE
phase_runtime_log -> NOT_CLEANABLE
phase_runtime_recovery_data -> NOT_CLEANABLE
P0_or_P1_decision -> NOT_CLEANABLE
validation_evidence -> NOT_CLEANABLE
high_risk_deviation -> NOT_CLEANABLE
```

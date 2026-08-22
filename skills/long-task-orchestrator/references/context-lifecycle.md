# 上下文生命周期

## Context Metadata

```yaml
runtime_epoch:
context_version:
based_on_plan:
planning_handoff_source:
planning_baseline_revision:
active_change_revision:
incremental_execution_contract_snapshot:
execution_constraints_source:
execution_constraints_status:
frontend_experience_binding_source:
frontend_contract_intake_status:
frontend_execution_snapshot:
implementation_contract_status:
dependency_governance_status:
project_execution_baseline_file:
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
<phase_runtime_directory>/
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
formal_plan_changed_after_upstream_writeback -> INVALIDATE
task_source_changed -> INVALIDATE
base_dependency_changed -> INVALIDATE
planning_handoff_changed -> INVALIDATE
planning_baseline_revision_changed -> PRECISE_INVALIDATE
active_change_revision_changed -> PRECISE_INVALIDATE
incremental_execution_contract_changed -> PRECISE_INVALIDATE
execution_constraints_changed -> INVALIDATE
frontend_experience_binding_or_design_revision_changed -> PRECISE_INVALIDATE
```

失效后先区分全局恢复失败与合法增量 Handoff。合法增量 Handoff 必须精确传播：

```text
STOP
-> 设置 invalidated_by
-> 升级 context_version
-> 读取新 Handoff 的 revision 与六类执行队列
-> 只将 reexecute_affected_part 和确实被替代/取消的运行片段设为 INVALIDATED
-> 保持 execute_only 中 carried-forward pending TASK 的 TODO 与原合同
-> 保持 resume_only 中未受影响的可靠检查点
-> 保持 completed_locked 的 DONE、EXEC 与验证证据
-> 保持 context_only 不可执行
-> 保持 cancelled 历史且禁止执行
-> 重新加载当前有效 Planning Handoff 与 Source of Truth
-> 重新生成 Runtime Context
-> 只生成或修订允许队列中的受影响 task
```

`runtime_recovery_failed`、无法解析 revision 或队列冲突仍按保守全停处理；但不得因为存在新的 Change Set 就无条件失效整个期次。

## 首次 Runtime Bootstrap 与已有 Runtime 恢复

首次 Runtime Bootstrap 尚未创建 Baseline 时，不进入恢复判定：

```text
first_runtime_bootstrap
+ Planning Handoff Intake passed
+ Phase Runtime Directory not yet created
+ Baseline not yet created
-> create Runtime Directory and Runtime State
-> inspect environment
-> create current phase Baseline
-> mark project_execution_baseline_status = current
-> continue remaining Preflight Gates
```

首次 Bootstrap 中的 Baseline 缺失不是 `runtime_recovery_failed`。

只有恢复已有 Runtime 时才应用 Baseline 恢复阻断：

```text
existing_runtime_recovery
+ project_execution_baseline_file missing
or project_execution_baseline_status in stale|missing|invalidated
-> execution cannot resume
-> STOP
-> refresh_environment_baseline
-> update current phase Baseline
-> rerun Runtime Recovery Consistency Gate
```

## 恢复

读取：

```text
Runtime Kernel
-> Phase Runtime Directory/current-runtime-context.md
-> Phase Runtime Directory/checkpoint-runtime.md
-> current valid Planning Handoff
-> Phase Runtime Directory/project-execution-baseline.md
-> current effective Source of Truth
-> Phase Runtime Directory/task.md
-> Phase Runtime Directory/execution-events.md
-> Runtime Recovery Consistency Gate
-> resume current step
```

校验：

```text
runtime_epoch_match
context_version_match
runtime_mode_match
current_effective_phase_match
current_effective_status_compatible
active_patch_id_match
planning_handoff_source_match
planning_baseline_revision_match
active_change_revision_presence_and_value_match
incremental_execution_contract_snapshot_match
execution_constraints_source_current
execution_constraints_status_match
frontend_experience_binding_source_current
frontend_contract_intake_status_match
frontend_execution_snapshot_match
implementation_contract_status_match
dependency_governance_status_match
active_placement_decision_matches_active_task
source_of_truth_current
project_execution_baseline_current
task_current
invalidated_by_empty
shared_boundary_clear
```

四方一致性必须成立：

```text
current-runtime-context
= checkpoint-runtime
= current Planning Handoff
= active task static contract
```

其中 revision 与 execution disposition 也必须一致；初始 Handoff 的 `active_change_revision` 必须在四方同时不存在，增量 Handoff 必须在四方一致。

依赖相关任务还必须满足：

```text
current-runtime-context
= checkpoint-runtime
= project-execution-baseline
= active task dependency fields
```

失败：

```text
STOP
-> recovery_required: true
-> current task or patch task BLOCKED
-> record Runtime Recovery Failed
-> do_not_resume_implementation
```

不得任选冲突文件为新事实、根据聊天记忆或最后修改时间恢复、从代码反推合同，或自动覆盖冲突字段后继续。Planning Handoff 或 execution constraints 已变化时，按本文件失效流程提升 `context_version`，精确失效受影响任务并只重新生成允许队列对应的 Context 与任务。

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
skill_reference_project_state -> POLLUTION_STOP_AND_REPORT
process_temporary_context -> CLEANABLE
phase_runtime_explicitly_marked_temporary_item -> CLEANABLE
formal_plan -> NOT_CLEANABLE
formal_execution_record -> NOT_CLEANABLE
formal_acceptance_record -> NOT_CLEANABLE
phase_runtime_directory -> NOT_CLEANABLE
phase_runtime_log -> NOT_CLEANABLE
phase_runtime_recovery_data -> NOT_CLEANABLE
P0_or_P1_decision -> NOT_CLEANABLE
validation_evidence -> NOT_CLEANABLE
high_risk_deviation -> NOT_CLEANABLE
current-runtime-context.md -> NOT_CLEANABLE
checkpoint-runtime.md -> NOT_CLEANABLE
project-execution-baseline.md -> NOT_CLEANABLE
task.md -> NOT_CLEANABLE
execution-events.md -> NOT_CLEANABLE
validation-results.md -> NOT_CLEANABLE
agent-decisions.md -> NOT_CLEANABLE
testing_handoff -> NOT_CLEANABLE
filled_execution_validation_or_acceptance_fact -> NOT_CLEANABLE
```

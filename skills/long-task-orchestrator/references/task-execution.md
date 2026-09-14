# Task 执行生命周期

## 目录

- 前置条件、执行顺序与执行阶段
- 偏差停止与 Worker/SubAgent 编排
- Capability Binding Gate
- Runtime 回写与完成规则
- Cleanup、Checkpoint 与禁止项

本文件只定义 Execution Lifecycle。

## 前置条件

执行需要：

- preflight 已通过
- Planning Handoff Intake Gate 已通过
- Planning Handoff revision consistency 与 incremental execution selection 已通过
- `execution_constraints` 已从当前有效 Planning Handoff 读取
- `task.md` 已生成
- Runtime 上下文有效
- execution_gate_open
- task 状态有效
- 拓扑约束有效
- 验证证据定义有效
- 当前 Baseline 的 Required Validation Matrix 完整且 revision 有效
- 当前 TASK 的 Implementation Placement Gate 与 Implementation Contract Completeness Intake 已通过
- UI TASK 的 Frontend Contract Intake 与 Per-Task Frontend Binding Gate 已通过
- dependency_governance_passed_or_not_applicable
- 涉及外部能力时，Capability Evidence Gate 已通过
- 涉及 Platform Capability、SDK Capability、AI Capability、External Capability 时，Capability Binding Gate 已通过

## 执行顺序

```text
select_next_executable_unit
-> confirm_task_is_in_execute_resume_or_reexecute_queue
-> confirm_task_contract_revision_matches_handoff
-> confirm_dependencies
-> confirm_execution_constraints_current
-> confirm_implementation_contract_complete
-> confirm_frontend_contract_binding_if_applicable
-> confirm_implementation_placement
-> confirm_dependency_governance_if_applicable
-> confirm_capability_gate_if_applicable
-> confirm_capability_binding_if_applicable
-> confirm_delivery_unit_and_required_validation_refs
-> confirm_ownership_boundary
-> confirm_shared_boundary_clear
-> execute_unit
-> run_task_local_checks
-> request_review
-> write_back_WAITING_VALIDATION
-> continue_next_unit
```

`run_task_local_checks` 只用于尽早发现当前实现单元的明显错误，不是 Required Validation Matrix 的正式通过证据，也不把 TASK 单独闭环。当前期所有 scope 内实现均进入 `WAITING_VALIDATION` 后，才以“本期”为一个正式闭环，完整扫描交付单元并逐项调用 `scripts/run-long-validation.sh|ps1`；runner 生成 attempt receipt 后统一写入 `validation-results.md`，再把证据映射回有关 TASK。禁止把普通终端输出、Task 局部检查或 Agent 总结直接提升为 `passed`。

当不存在下一实现单元时，停止任务选择并进入本期正式验证；达到 `SKILL.md` 的 Long Runtime Completion Boundary 后不得再次执行 `continue_next_unit`。

任务选择不得扫描完整 Development Landing Checklist 后自行决定。选择语义固定为：

```text
execute_only -> 从 TODO 开始执行
resume_only -> 从已有可靠检查点继续未完成部分
reexecute_affected_part -> 只失效并重做明确受影响部分
context_only -> NEVER_EXECUTE
completed_locked -> NEVER_RERUN_OR_REGENERATE_EXEC
cancelled -> NEVER_EXECUTE
```

若当前 Runtime 中已有 TASK 与新 Handoff 队列不一致，先执行 `context-lifecycle.md` 的精确失效传播，不得把整个期次或全部 TASK 重置。

Patch 分支：

```text
if testing_feedback_patch_confirmed:
  enter_patch_runtime
  -> confirm_patch_source
  -> confirm_patch_scope
  -> confirm_change_triage_disposition_is_fix_in_execution
  -> confirm_existing_runtime_valid
  -> reload_current_planning_handoff
  -> recheck_execution_constraints
  -> confirm_patch_traceable_to_existing_SoT_or_confirmed_defect
  -> confirm_patch_does_not_require_full_replanning
  -> run_Implementation_Placement_Gate
  -> run_Implementation_Contract_Completeness_Intake
  -> run_Dependency_Governance_Gate_if_applicable
  -> run_Capability_Evidence_and_Binding_Gates_if_applicable
  -> generate_patch_task
  -> execute_patch_unit
  -> run_patch_automated_validation
  -> rerun_affected_required_validation_matrix_items
  -> recompute_local_runnable_gate
  -> run_patch_execution_constraint_validation
  -> main_agent_review
  -> update_validation_results
  -> update_testing_handoff
  -> deterministic_candidate_readiness_validation
  -> ready_for_local_retest
  -> record_ready_for_local_retest_since
  -> deterministic_ready_state_validation
  -> update_checkpoint
  -> STOP
```

Patch 的两次确定性校验分别使用 `validate_long_readiness.py` 默认模式和 `--expect-ready` 模式，与主 Completion Boundary 共用同一 Matrix、证据和 Handoff 口径。失败时回写 `blocked`，不得输出 `ready_for_local_retest`。

Patch Task 必须复用 `task-state-machine.md` 的完整 Static Task Definition，不得省略 Planning 追踪、稳定业务概念、execution constraints 来源、承接策略、现有业务域、新业务域依据、禁止命名、参数合同、明确委托参数或依赖变更字段。

Patch 涉及依赖变化时必须重新执行 Dependency Governance Gate，不得沿用主 Runtime 的旧状态。

Patch 停止条件：

```text
patch_scope_untraceable -> STOP
patch_change_triage_requires_planning_reentry -> STOP_AND_RETURN_TO_PLANNING
patch_introduces_new_requirement_without_user_confirmation -> STOP
patch_requires_SoT_change_without_writeback -> STOP
patch_crosses_P0_without_boundary_confirmation -> STOP
patch_validation_missing -> NOT_DONE
patch_required_validation_failed_blocked_not_run_or_missing -> PATCH_NOT_DONE
patch_local_runnable_gate_not_passed -> PATCH_NOT_DONE
patch_execution_constraint_validation_failed -> PATCH_NOT_DONE
patch_execution_constraint_validation_failed -> CURRENT_PATCH_TASK_BLOCKED
patch_contract_or_parameter_unconfirmed -> CURRENT_PATCH_TASK_BLOCKED
patch_dependency_governance_blocked -> DO_NOT_INSTALL
```

Patch 不得使用期次/阶段/Sprint/版本/Planning ID 命名实现资产，不得创建未规划业务模块或数据库合同外持久化单元，不得修改未确认 API/数据结构/权限/状态/租户边界、自行补业务参数、超出 `explicitly_delegated` 范围、绕过依赖治理、修改原始 SoT 或扩展未确认需求。

## 执行阶段

```text
prepare
execute
validate
review
writeback
continue_or_stop
```

## 偏差停止规则

以下任一偏差立即执行：

```text
STOP_IMPLEMENTATION
-> CURRENT_TASK_BLOCKED
-> WRITE_BACK_UPSTREAM_FIRST
-> WAIT_FOR_CONFIRMED_HANDOFF
```

适用于新增未规划模块、以期次或 Planning ID 命名实现资产、修改 API/权限/状态机/数据模型/租户边界/用户可见规则/关键参数、引入外部能力或正式业务域、改变验收口径，以及 PAGE/UI-MOD/UX-SCN/ASSET revision 与现有实现发生无法在已确认范围内解决的冲突。UI/UX 偏差按 `frontend-experience-execution.md` 分类并携带精确合同引用；禁止记录偏差后继续开发或自行重设计。

若上游正式计划更新，按 `context-lifecycle.md` 校验新的 baseline/change revision，精确失效受影响 TASK，提升 `context_version`，保留 `completed_locked` 与未受影响事实，重读 Handoff/SoT 后只重建允许队列对应的 Context 与 TASK。

## Worker/SubAgent 编排

```text
delegation_requires_delegation_rules
delegation_requires_topology_clearance
subagent_scope_must_be_bounded
subagent_result_requires_main_review
subagent_boundary_escalation -> stop_or_reassign
```

## Capability Binding Gate

适用范围：

- Platform Capability
- SDK Capability
- AI Capability
- External Capability

执行前必须确认：

- runtime binding
- adapter binding
- sdk api binding
- permission binding
- fallback binding

验证方式：

检查 Capability Binding Matrix 或等价 Runtime Evidence，确认：

- adapter 存在
- runtime 绑定存在
- sdk api 真实调用存在
- permission 绑定存在
- fallback 存在

以下情况必须 BLOCKED：

```text
adapter_missing
runtime_binding_missing
sdk_api_not_used
permission_binding_missing
```

以下情况标记 HIGH：

```text
fallback_missing
```

禁止仅凭以下内容判定 Capability Completed：

- OAuth 通过
- 容器识别通过
- UA 识别通过
- 页面打开
- JSSDK ready

## Runtime 回写时机

```text
phase_event -> after_phase_boundary
validation_result -> after_validation
agent_decision -> after_review
context_pointer -> after_active_unit_change
checkpoint_runtime -> after_long_stage_completed_or_before_stage_change
formal_execution_record -> after_unit_result
testing_handoff -> before_ready_for_local_test_or_ready_for_local_retest
formal_acceptance_record -> read_and_reference_only
```

## Execution Completion Rule

计算完成状态前必须重新扫描当前交付单元，确认 Matrix 未漏项、revision 未失效，并按 `validation-gates.md` 重新计算 Local Runnable Gate；不得直接从 TASK 数量、主 Agent 复核、测试数量或“无已记录失败”推导完成。完成边界必须按 `validation-gates.md` 运行 Long 确定性校验器，不得用人工判断覆盖失败。

执行完成后，若：

- implementation_done
- code_quality_passed
- function_unit_tests_passed
- business_unit_tests_passed
- contract_validation_passed
- execution_constraint_validation_passed
- minimum_capability_validation_passed_or_not_applicable
- required_validation_matrix_current_and_complete
- all_required_automated_validation_passed
- local_runnable_gate_passed
- long_testing_handoff_written
- no_unresolved_P0_validation_issue

则：

```text
completion_boundary_passed
-> retrospective
-> execution_record_writeback
-> testing_handoff_writeback
-> deterministic_candidate_readiness_validation
-> implementation_completed
-> ready_for_local_test
-> record ready_for_local_test_since
-> deterministic_ready_state_validation
-> runtime_checkpoint_writeback
-> runtime_archive
-> runtime_cleanup
-> runtime_closed
-> deterministic_readiness_receipt
-> STOP
```

`deterministic_candidate_readiness_validation` 运行校验器默认模式；进入 ready 的状态迁移执行 ready-state validation；归档、清理和关闭回写结束后，使用 `--expect-ready --write-receipt` 再次完整校验并写入最终 receipt。Receipt 成功后禁止继续修改 Runtime、合同、source 或证据；新增变化必须开启递增 patch cycle。任一步失败都必须回写 `blocked` 及错误证据，清空未成功生效的 ready 时间戳，并停止后续步骤和 Testing 交接声明。

`long_testing_handoff_written` 是 Completion Boundary 前置条件；`ready_for_local_test` 是 Completion Rule 的输出，不得反向作为完成前置条件。

```text
long_testing_handoff_written = false
-> completion_boundary_not_passed
-> do_not_produce ready_for_local_test
```

`ready_for_local_test` 表示：

```text
代码开发完成，当前 Required Validation Matrix 的全部必需项已通过，交付物的真实构建/装载/启动/配置/必需依赖/最小行为路径按适用性可在本地或受控测试环境运行，且 Long Testing Handoff 已完成；可进入 testing-layer-runtime 管理的人工/真实设备/服务器/最终验收阶段
```

不是：

```text
最终验收通过
人工测试通过
服务器验证通过
上线放行
```

## Runtime Cleanup

```text
runtime_cleanup
=
清理当前进程中的临时上下文
+ 清理当前期次 Runtime 目录中明确标记为可清理的临时项
```

不得删除：

- 当前期次 Runtime 目录
- 当前期次 Runtime 日志
- 当前期次 Validation 记录
- 当前期次 Decision 记录
- 当前期次 Recovery 数据
- current-runtime-context、checkpoint、project-execution-baseline、task、execution-events、validation-results、agent-decisions、Testing Handoff
- 正式执行记录、P0/P1 决策及已填写的执行、验证或验收事实

禁止：

```text
auto_enter_acceptance_prep
auto_enter_human_environment_preparation
auto_wait_for_real_accounts
auto_wait_for_external_environment
auto_wait_for_local_test
next_unit_after_ready_for_local_test
```

## Checkpoint 写入

仅在以下场景更新 `checkpoint-runtime.md`：

```text
long_stage_completed
before_new_stage
before_context_compression
long_execution_over_30_to_45_min
```

写入内容只保留当前恢复所需状态。

## 禁止

- 不得在此文件定义 task 状态流转。
- 不得在此文件定义 task 状态进入条件。
- 不得在此文件定义验证证据字段。
- 不得在此文件定义拓扑规则。
- 不得在此文件定义检查工作流。
- 前置条件失败后不得继续执行。
- execution_gate_closed 时不得执行 implementation。
- preflight 未通过时不得执行 implementation。
- task.md 未生成或不可追溯到 Source of Truth 时不得执行 implementation。
- 外部能力缺少 CAP-ID、官方 SoT、版本、鉴权、请求响应结构或最小真实调用验证时不得执行 implementation。
- Platform Capability、SDK Capability、AI Capability、External Capability 缺少 runtime binding、adapter binding、sdk api binding 或 permission binding 时不得执行 implementation。
- Long 不得创建或写入正式验收记录、验收占位文件、人工/服务器/最终验收结果或 release 判断。
- dependency governance 为 `blocked` 或 `pending` 时，关闭当前任务 execution gate，不得安装或实现。

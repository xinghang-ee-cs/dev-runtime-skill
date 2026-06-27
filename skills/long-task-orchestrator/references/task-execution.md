# Task 执行生命周期

本文件只定义 Execution Lifecycle。

## 前置条件

执行需要：

- preflight 已通过
- `task.md` 已生成
- Runtime 上下文有效
- execution_gate_open
- task 状态有效
- 拓扑约束有效
- 验证证据定义有效
- 涉及外部能力时，Capability Evidence Gate 已通过
- 涉及 Platform Capability、SDK Capability、AI Capability、External Capability 时，Capability Binding Gate 已通过

## 执行顺序

```text
select_next_executable_unit
-> confirm_dependencies
-> confirm_capability_gate_if_applicable
-> confirm_capability_binding_if_applicable
-> confirm_ownership_boundary
-> confirm_shared_boundary_clear
-> execute_unit
-> request_validation
-> request_review
-> write_back_runtime_state
-> continue_next_unit
```

当当前执行结果达到 `SKILL.md` 的 Long Runtime Completion Boundary 时，不得执行 `continue_next_unit`。

Patch 分支：

```text
if testing_feedback_patch_confirmed:
  enter_patch_runtime
  -> confirm_patch_scope
  -> confirm_existing_runtime_valid
  -> confirm_patch_does_not_require_full_replanning
  -> generate_patch_task
  -> execute_patch_unit
  -> validate_patch_unit
  -> write_back_patch_runtime_state
  -> update_testing_handoff
  -> ready_for_local_retest
  -> STOP
```

Patch 停止条件：

```text
patch_scope_untraceable -> STOP
patch_introduces_new_requirement_without_user_confirmation -> STOP
patch_requires_SoT_change_without_writeback -> STOP
patch_crosses_P0_without_boundary_confirmation -> STOP
patch_validation_missing -> NOT_DONE
```

## 执行阶段

```text
prepare
execute
validate
review
writeback
continue_or_stop
```

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
```

## Execution Completion Rule

执行完成后，若：

- implementation_done
- code_quality_passed
- function_unit_tests_passed
- business_unit_tests_passed
- contract_validation_passed
- minimum_capability_validation_passed_or_blocked
- automated_validation_recorded
- long_testing_handoff_written
- ready_for_local_test
- no unresolved P0 validation issue

则：

```text
retrospective
-> execution_record_writeback
-> testing_handoff_writeback
-> acceptance_placeholder_writeback
-> runtime_checkpoint_writeback
-> runtime_archive
-> runtime_cleanup
-> implementation_completed
-> ready_for_local_test
-> runtime_closed
-> STOP
```

`ready_for_local_test` 表示：

```text
代码开发、long 自动化验证记录、Long Testing Handoff 已完成，可进入 testing-layer-runtime 管理的人工/真实设备/服务器/最终验收阶段
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
仅清理 Skill 内实例状态
```

不得删除：

- 当前期次 Runtime 目录
- 当前期次 Runtime 日志
- 当前期次 Validation 记录
- 当前期次 Decision 记录
- 当前期次 Recovery 数据

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

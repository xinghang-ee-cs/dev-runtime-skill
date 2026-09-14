# 验证结果模板

## 目录

- Runtime Session
- Validation Entry 与 Capability Validation Schema
- 允许枚举与 Required Validation Binding
- 禁止记录
- Long Testing Handoff Summary
- Template 与 Example

本文件是 Runtime State Template。

实例化位置：

```text
<phase_runtime_directory>/validation-results.md
```

禁止在本文件保存某一期项目验证记录。

字段、枚举与结果语义必须引用 `validation-gates.md`；本文件不得成为第二份 Validation Contract。

## Runtime Session

```yaml
runtime_session_ref: <phase_runtime_directory>/current-runtime-context.md
```

## Validation Entry Schema

```yaml
validation_id:
time:
attempt:
related_task:
validation_type:
validation_focus:
command:
scope:
result:
matrix_revision:
code_config_revision:
requirement_id:
delivery_unit_id:
requirement_level:
execution_receipt_ref:
postcondition_results:
matrix_compatibility:
compatibility_evidence:
failures:
applied_fix:
rerun_result:
frontend_score:
backend_score:
why_not_automated:
manual_required:
execution_constraint_validation:
frontend_contract_validation:
capability_id:
capability_validation:
capability_evidence:
capability_binding:
runtime_binding:
adapter_binding:
sdk_api_binding:
permission_binding:
fallback_binding:
code_evidence:
evidence:
```

`manual_required` 为空时必须写：

```yaml
manual_required: []
```

## Capability Validation Schema

涉及外部能力、SDK、OpenAPI、MCP、AI Provider、基础设施依赖或第三方平台时使用：

```yaml
validation_id:
related_task:
capability_id:
official_sot:
sdk_version:
api_version:
auth_result:
minimum_real_call_result:
request_source:
response_evidence:
error_code_evidence:
timeout_handling:
rate_limit_handling:
fallback_result:
network_failure_recovery:
capability_binding:
runtime_binding:
adapter_binding:
sdk_api_binding:
permission_binding:
fallback_binding:
code_evidence:
result:
evidence:
```

Capability Validation 不允许只记录：

- SDK 初始化
- 鉴权
- 最小真实调用

还必须记录：

- Runtime 绑定证据
- Adapter 绑定证据
- SDK API 调用证据
- Permission 绑定证据
- Fallback 证据

若 `adapter_binding = false`，则 `result = not_passed`。

若 `sdk_api_binding = false`，则 `result = not_passed`。

若 `runtime_binding = false`，则 `result = not_passed`。

## 允许的枚举

`validation_type` 只允许：

```text
test
build
lint
smoke
openapi
typecheck
api-test
playwright
capability_real_call
capability_binding
execution_constraint_compliance
frontend_contract_compliance
```

`validation_focus` 只允许：

```text
unit
business_rule
contract
user_flow
state_transition
permission_boundary
capability_binding
implementation_naming
implementation_placement
delegated_parameter_boundary
dependency_governance
ui_contract
ux_contract
responsive_behavior
accessibility_behavior
visual_asset_consistency
artifact_readiness
runtime_configuration
dependency_readiness
process_readiness
schema_readiness
```

`sdk_init`、`auth_check`、`timeout`、`rate_limit`、`fallback`、`runtime_binding`、`adapter_binding`、`sdk_api_binding`、`permission_binding` 只能作为 validation focus、Capability 字段或 evidence，不得作为独立 `validation_type`。`rerun` 是 `rerun_result`，`code_evidence` 是字段，`long_testing_handoff` 是输出分类，均不是 `validation_type`。

## Required Validation Binding

- 当前期必要验证集合只从 `project-execution-baseline.md.required_validation_matrix` 读取；本文件不重新定义要求。
- Matrix 内的验证必须填写 `matrix_revision`、`requirement_id`、`delivery_unit_id`、`requirement_level` 和 `postcondition_results`。
- `attempt`、`time` 与 `code_config_revision` 按 `validation-gates.md` 的唯一结果新旧与当前代码/配置绑定规则记录；本模板不另行定义选择算法。
- `result: passed` 必须证明命令/探针真实执行且全部成功后置条件成立；类型检查不得替代构建，构建退出码不得替代产物/装载证明，代码存在不得替代进程启动、配置绑定或依赖就绪。
- `requirement_level: required` 的最新有效结果只允许 `passed` 才能通过 Completion Boundary；`failed | blocked | not_run`、缺失结果或仅记录未执行原因都必须阻断。
- 补充验证不属于 Matrix 时，将 Matrix 绑定字段写为 `not_applicable`；补充验证通过不得补偿任何必需项缺失。
- 修复重跑必须使用同一 `requirement_id` 追加新 validation entry；保留历史失败，完成门禁使用当前 Matrix revision 下的最新有效结果。
- Matrix revision 变化时，只有 requirement id、命令/探针、全部后置条件、安全边界及相关代码/配置均未变化的结果可标记 `matrix_compatibility: carried_forward_unchanged`，并填写逐项 `compatibility_evidence`；新增或变化项必须重跑。

## 禁止记录

- 架构讨论
- 生命周期事件
- subAgent 决策
- 仅 Mock 成功作为外部能力真实验证
- 仅代码可编译作为外部能力真实验证
- 仅 SDK 初始化、鉴权或最小真实调用作为 Capability Completed

## Long Testing Handoff Summary

实例化位置：

```text
<phase_runtime_directory>/testing-handoff.md
```

或：

```text
<phase_runtime_directory>/long-runtime-testing-summary.md
```

必须包含：

```yaml
runtime_epoch:
planning_handoff_ref:
planning_baseline_revision:
active_change_revision: # 初始 Handoff 省略
executed_task_contract_revisions: []
automated_passed:
  - id:
    source_validation_id:
    scope:
    command:
    evidence:
    coverage:
automated_failed:
  - id:
    source_validation_id:
    scope:
    command:
    failure:
    evidence:
automated_skipped:
  - id:
    scope:
    reason:
manual_required:
  - id:
    planning_test_refs: []
    scope:
    reason:
    owner_runtime: testing-layer-runtime
coverage:
  requirements:
  tasks:
  capabilities:
  apis:
  permissions:
  state_flows:
  business_flows:
required_validation_gate:
  matrix_ref:
  matrix_revision:
  effective_validation_ids: []
  result: <passed | blocked>
frontend_contract_validation_summary:
  applicable: <true | false>
  design_document_path:
  design_manifest_ref:
  validated_contract_refs: []
  validated_asset_refs: []
  automated_evidence_refs: []
  manual_required: []
  unresolved_mismatch: []
formal_acceptance_record_path:
acceptance_status: not_started
owner_runtime: testing-layer-runtime
validator_receipt_ref: long-readiness-receipt.json
```

规则：

- `runtime_epoch` 必须与 `current-runtime-context.md.runtime_epoch` 一致；`planning_handoff_ref` 必须与当前 Long Runtime 实际消费的 Planning Handoff 一致。两者均不得根据目录名或聊天记忆推断。
- `planning_baseline_revision`、可选 `active_change_revision` 和 `executed_task_contract_revisions` 必须与当前有效的 Planning Handoff 及 Long 执行事实一致；初始 Handoff 省略 `active_change_revision`。
- 每条 `automated_passed` 必须引用 `validation-results.md` 中的 `validation_id` 或等价 evidence。
- 每条 `automated_failed` 必须保留失败摘要，不得被 testing-layer-runtime 当作已通过继承。
- 每条 `automated_skipped` 必须保留未执行原因。
- `required_validation_gate` 只能引用 Baseline Matrix 和本文件中的有效 validation id，不得复制命令、后置条件或证据正文。
- `required_validation_gate.result: passed` 必须满足 `validation-gates.md` 的 Local Runnable Gate；任一 `required` 项处于 `failed | blocked | not_run`、缺失或 stale 时只能写 `blocked`，且不得进入 `ready_for_local_test`。
- `automated_failed`、`automated_skipped` 可以保存历史或非必需项，但当前有效的必需项失败/跳过不得以 Handoff 已写入为由放行。
- `manual_required` 只列 testing-layer-runtime 后续要管理的人工、真实设备、服务器/云端、外部能力最终验证、最终验收或上线前验证。
- `manual_required[].planning_test_refs` 必须与 Baseline Matrix `completeness_audit.manual_or_real_environment_planning_test_refs` 完全对账；没有 Planning TEST 引用的纯补充观察必须明确 `not_applicable`，不得用于填补 required 测试缺口。
- UI/UX 适用时 `frontend_contract_validation_summary` 必须按 `frontend-experience-execution.md` 记录；存在 `unresolved_mismatch` 时不得进入 `ready_for_local_test`。
- 不得在 handoff 中把 manual/server/final/release 项写成 passed。
- `formal_acceptance_record_path` 必须引用 Planning Handoff 已声明且真实存在的正式验收记录，只保存路径，不创建、修改或复制正文。
- `acceptance_status` 在 Long 中固定为 `not_started`，不得填写 `passed`、`failed`、`accepted`、`approved` 或 `release_ready`。
- `owner_runtime` 固定为 `testing-layer-runtime`。
- `validator_receipt_ref` 固定指向同一 Long Runtime 内由前向状态机在 ready 且归档/关闭回写完成后生成的 `long-readiness-receipt.json`；当前 schema 为 `long-readiness-receipt/v2`，冻结 workflow history digest、repository revision、Matrix revision、effective validation ids、全部 machine execution receipts、Runtime 文件及外部合同/source 摘要。Receipt 必须是移交前最后一次写入；Testing 必须重算摘要，缺失、篡改、遗漏新增文件或来源变化时拒绝继承。
- 每个 `required` Validation Entry 的 `execution_receipt_ref` 必须指向同一 Runtime 的 `machine-execution-receipts/<validation_id>.json`。该文件只能由 `run-long-validation.sh|ps1` 生成，必须同时出现在顶层 `evidence`，且每条 `postcondition_results[].evidence` 都引用它；Agent 不能仅凭终端文字自行填写 `passed`。
- 以上字段只表达验收文件位置、验收尚未开始及 Testing 接管，不授予 Long 写入正式验收记录的权限；`formal_acceptance_record -> read_and_reference_only`。

## Template

```yaml
validation_id: <VALIDATION-ID>
time: <ISO-8601 timestamp>
related_task: <TASK-ID>
validation_type: <test | build | lint | smoke | openapi | typecheck | api-test | playwright | capability_real_call | capability_binding | execution_constraint_compliance | frontend_contract_compliance>
validation_focus: <unit | business_rule | contract | user_flow | state_transition | permission_boundary | capability_binding | implementation_naming | implementation_placement | delegated_parameter_boundary | dependency_governance | ui_contract | ux_contract | responsive_behavior | accessibility_behavior | visual_asset_consistency | artifact_readiness | runtime_configuration | dependency_readiness | process_readiness | schema_readiness>
command:
  - <command or not_run_with_reason>
scope: <validated scope>
result: <passed | failed | blocked | not_run>
matrix_revision: <current matrix revision | not_applicable>
requirement_id: <required validation requirement id | not_applicable>
delivery_unit_id: <delivery unit id | not_applicable>
requirement_level: <required | optional | not_applicable>
execution_receipt_ref: <machine-execution-receipts/VALIDATION-ID.json；required 必填>
postcondition_results:
  - postcondition: <expected postcondition>
    result: <passed | failed | blocked | not_run>
    evidence: <同一 execution_receipt_ref>
matrix_compatibility: <current | carried_forward_unchanged | stale | not_applicable>
compatibility_evidence:
  - <field-level comparison evidence or not_applicable>
failures: <failure summary or none>
applied_fix: <fix summary or none>
rerun_result: <passed | failed | not_required>
frontend_score: <passed | failed | not_applicable>
backend_score: <passed | failed | not_applicable>
why_not_automated: <reason or not_applicable>
manual_required: []
capability_id: <capability id or not_applicable>
capability_validation: <status>
capability_evidence: <evidence status>
capability_binding: <status>
runtime_binding: <status>
adapter_binding: <status>
sdk_api_binding: <status>
permission_binding: <status>
fallback_binding: <status>
execution_constraint_validation:
  planning_ids_trace_only: <passed | failed | not_applicable>
  forbidden_phase_names_absent: <passed | failed | not_applicable>
  stable_business_naming_used: <passed | failed | not_applicable>
  implementation_placement_respected: <passed | failed | not_applicable>
  existing_domain_preflight_respected: <passed | failed | not_applicable>
  new_module_architecture_basis_valid: <passed | failed | not_applicable>
  delegated_parameter_boundary_respected: <passed | failed | not_applicable>
  dependency_governance_passed: <passed | failed | not_applicable>
  result: <passed | failed | not_applicable>
  evidence:
    - <evidence reference>
code_evidence:
  - path:
    task_ref:
    stable_business_concept:
    implementation_placement:
    constraint_check:
evidence:
  - <evidence summary>
```

## Example

以下局部示例只展示 `test` 与 `build` 必须拆分为独立 Validation Entry，不是完整 Validation Entry 示例。真实验证记录仍必须满足本文件完整 Schema，并填写所有适用字段；不得因为示例省略而省略字段。涉及代码的任务必须填写 `execution_constraint_validation`，代码改动必须填写 `code_evidence`，Capability 字段不适用时必须填写 `not_applicable`，`manual_required` 为空时必须填写 `[]`。

```yaml
- validation_id: VALIDATION-TEST-001
  time: <ISO-8601 timestamp>
  related_task: <TASK-ID>
  validation_type: test
  validation_focus: business_rule
  command:
    - <project package manager> test -- <target>
  scope: <implementation unit>
  result: passed
  failures: none
  applied_fix: none
  rerun_result: not_required
  why_not_automated: not_applicable
  manual_required: []
  evidence:
    - <test result summary>
- validation_id: VALIDATION-BUILD-001
  time: <ISO-8601 timestamp>
  related_task: <TASK-ID>
  validation_type: build
  validation_focus: contract
  command:
    - <project package manager> build
  scope: <touched workspace>
  result: passed
  failures: none
  applied_fix: none
  rerun_result: not_required
  why_not_automated: not_applicable
  manual_required: []
  evidence:
    - <build result summary>
```

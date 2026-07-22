# 验证结果模板

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
related_task:
validation_type:
validation_focus:
command:
scope:
result:
failures:
applied_fix:
rerun_result:
frontend_score:
backend_score:
why_not_automated:
manual_required:
execution_constraint_validation:
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
```

`sdk_init`、`auth_check`、`timeout`、`rate_limit`、`fallback`、`runtime_binding`、`adapter_binding`、`sdk_api_binding`、`permission_binding` 只能作为 validation focus、Capability 字段或 evidence，不得作为独立 `validation_type`。`rerun` 是 `rerun_result`，`code_evidence` 是字段，`long_testing_handoff` 是输出分类，均不是 `validation_type`。

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
formal_acceptance_record_path:
acceptance_status: not_started
owner_runtime: testing-layer-runtime
```

规则：

- 每条 `automated_passed` 必须引用 `validation-results.md` 中的 `validation_id` 或等价 evidence。
- 每条 `automated_failed` 必须保留失败摘要，不得被 testing-layer-runtime 当作已通过继承。
- 每条 `automated_skipped` 必须保留未执行原因。
- `manual_required` 只列 testing-layer-runtime 后续要管理的人工、真实设备、服务器/云端、外部能力最终验证、最终验收或上线前验证。
- 不得在 handoff 中把 manual/server/final/release 项写成 passed。
- `formal_acceptance_record_path` 必须引用 Planning Handoff 已声明且真实存在的正式验收记录，只保存路径，不创建、修改或复制正文。
- `acceptance_status` 在 Long 中固定为 `not_started`，不得填写 `passed`、`failed`、`accepted`、`approved` 或 `release_ready`。
- `owner_runtime` 固定为 `testing-layer-runtime`。
- 以上字段只表达验收文件位置、验收尚未开始及 Testing 接管，不授予 Long 写入正式验收记录的权限；`formal_acceptance_record -> read_and_reference_only`。

## Template

```yaml
validation_id: <VALIDATION-ID>
time: <ISO-8601 timestamp>
related_task: <TASK-ID>
validation_type: <test | build | lint | smoke | openapi | typecheck | api-test | playwright | capability_real_call | capability_binding | execution_constraint_compliance>
validation_focus: <unit | business_rule | contract | user_flow | state_transition | permission_boundary | capability_binding | implementation_naming | implementation_placement | delegated_parameter_boundary | dependency_governance>
command:
  - <command or not_run_with_reason>
scope: <validated scope>
result: <passed | failed | blocked | not_run>
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

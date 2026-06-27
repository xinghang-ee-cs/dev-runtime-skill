# 验证结果模板

本文件是 Runtime State Template。

实例化位置：

```text
docs/计划安排/<期次>/runtime/validation-results.md
```

禁止在本文件保存某一期项目验证记录。

## Runtime Session

```yaml
runtime_session_ref: docs/计划安排/<期次>/runtime/current-runtime-context.md
```

## Validation Entry Schema

```yaml
validation_id:
time:
related_task:
validation_type:
command:
scope:
result:
failures:
applied_fix:
rerun_result:
frontend_score:
backend_score:
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

## 允许记录

- test
- build
- lint
- smoke
- openapi
- typecheck
- rerun
- capability_real_call
- auth_check
- sdk_init
- timeout
- rate_limit
- fallback
- capability_binding
- runtime_binding
- adapter_binding
- sdk_api_binding
- permission_binding
- code_evidence
- long_testing_handoff

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
docs/计划安排/<期次>/runtime/testing-handoff.md
```

或：

```text
docs/计划安排/<期次>/runtime/long-runtime-testing-summary.md
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
```

规则：

- 每条 `automated_passed` 必须引用 `validation-results.md` 中的 `validation_id` 或等价 evidence。
- 每条 `automated_failed` 必须保留失败摘要，不得被 testing-layer-runtime 当作已通过继承。
- 每条 `automated_skipped` 必须保留未执行原因。
- `manual_required` 只列 testing-layer-runtime 后续要管理的人工、真实设备、服务器/云端、外部能力最终验证、最终验收或上线前验证。
- 不得在 handoff 中把 manual/server/final/release 项写成 passed。

## Template

```yaml
validation_id: <VALIDATION-ID>
time: <ISO-8601 timestamp>
related_task: <TASK-ID>
validation_type: <test | build | lint | smoke | openapi | typecheck | capability_real_call | capability_binding>
command:
  - <command or not_run_with_reason>
scope: <validated scope>
result: <passed | failed | blocked | not_run>
failures: <failure summary or none>
applied_fix: <fix summary or none>
rerun_result: <passed | failed | not_required>
frontend_score: <passed | failed | not_applicable>
backend_score: <passed | failed | not_applicable>
capability_id: <capability id or not_applicable>
capability_validation: <status>
capability_evidence: <evidence status>
capability_binding: <status>
runtime_binding: <status>
adapter_binding: <status>
sdk_api_binding: <status>
permission_binding: <status>
fallback_binding: <status>
code_evidence:
  - <file path>
evidence:
  - <evidence summary>
```

## Example

```yaml
validation_id: VALIDATION-001
time: <ISO-8601 timestamp>
related_task: <TASK-ID>
validation_type: test_and_build
command:
  - pnpm --dir <workspace> test -- <target>
scope: <implementation unit>
result: passed
failures: none
applied_fix: none
rerun_result: not_required
frontend_score: not_applicable
backend_score: passed
capability_id: not_applicable
capability_validation: not_applicable
capability_evidence: not_applicable
capability_binding: not_applicable
runtime_binding: passed
adapter_binding: not_applicable
sdk_api_binding: not_applicable
permission_binding: not_applicable
fallback_binding: not_applicable
code_evidence:
  - <changed file path>
evidence:
  - <test result summary>
```

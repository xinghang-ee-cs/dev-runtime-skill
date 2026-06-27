# 验证门禁

本文件只定义 Validation Evidence Definition。

## 1. 验证用途

```text
prove_implemented_scope
prove_contract_consistency
prove_capability_real_execution
prove_touched_scope_stability
prove_unavailable_validation_explicitly_recorded
```

## 1.1 Validation Layer Boundary

long Runtime 只负责开发期自动化验证：

```text
TEST-LAYER-AUTOMATED-UNIT
TEST-LAYER-AUTOMATED-BUSINESS
TEST-LAYER-AUTOMATED-INTEGRATION
TEST-LAYER-AUTOMATED-API
TEST-LAYER-AUTOMATED-UI
```

包括：

- unit test
- service test
- dto/schema test
- api contract test
- business flow automated test
- integration automated test
- api-test
- playwright automated test
- vitest
- jest
- state transition test
- permission basic validation
- capability minimum validation

禁止将以下内容作为 long Runtime Required Validation：

- local exploratory test
- multi-device test
- server/deployed environment acceptance
- real-device test
- final business acceptance
- release approval

Capability Validation 只要求：

```text
minimum_real_call_validation
```

不等于：

```text
final_acceptance
```

## 2. 证据字段

```yaml
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

`validation_type` 记录验证命令类型，允许：

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
```

`validation_focus` 记录验证覆盖重点，允许：

```text
unit
business_rule
contract
user_flow
state_transition
permission_boundary
capability_binding
```

字段定义：

- `capability_binding`: Capability Binding 是否完成。
- `runtime_binding`: Capability 是否已绑定对应 Runtime。
- `adapter_binding`: Capability Adapter 是否存在。
- `sdk_api_binding`: Capability 是否真实调用目标 SDK API。
- `permission_binding`: Capability 是否绑定权限处理。
- `fallback_binding`: Capability 是否定义并实现降级方案。
- `code_evidence`: Capability 对应代码证据。
- `evidence`: 自动化命令输出、报告路径、截图/trace 路径或失败记录；必须能进入 Long Testing Handoff。

Template:

```yaml
validation_type: test
validation_focus: business_rule
```

## 3. 阶段验证证据

For every user-facing task:

```text
must generate at least one automated user-flow validation when technically possible
```

If user-flow automation is not technically possible:

```text
record why_not_automated
and add manual_required with exact role, entry, action, expected visible state
```

阶段验证证据应覆盖：

- 当前阶段对应的 task 范围。
- user_flow validation 的 real entry、role、primary action、success visible state。
- 适用时覆盖 disabled/blocked state 和 error visible state。
- 项目基线中可用的最小相关验证命令。
- 前端与后端分开记录的覆盖率或不可用原因。
- 验证不可用原因。
- 涉及外部能力时，记录 CAP-ID、SDK 初始化、鉴权、最小真实调用、错误码、超时、限流、降级和网络失败恢复证据。
- 涉及 Platform Capability、SDK Capability、AI Capability、External Capability 时，必须记录 Capability Binding 字段。

## 4. 后端合同证据

后端合同证据应覆盖：

- endpoint path
- HTTP method
- auth/session expectation
- request shape
- response shape
- error shape
- important examples
- frontend-facing API document source
- related CAP-ID when the endpoint depends on external capability

## 5. 完成边界验证证据

完成边界验证证据应覆盖：

- touched scope checks
- frontend/backend contract consistency
- build/typecheck/test evidence
- vitest/jest/integration/api-test/playwright evidence when applicable
- external capability real-call evidence or explicit planning BLOCKER
- skipped or unavailable checks with reason
- frontend score
- backend score
- Long Testing Handoff classification: `automated_passed` / `automated_failed` / `automated_skipped` / `manual_required`

## 6. 验证报告要求

```text
validation_result -> validation-results.md
unavailable_validation -> explicit_record
unchecked_item -> not_passed
frontend_score != backend_score
unsupported_validation_claim -> forbidden
mock_only_capability_validation -> not_passed
missing_capability_real_call_evidence -> not_passed
missing_capability_binding_fields -> not_passed
platform_capability_without_binding_validation -> not_passed
sdk_capability_without_binding_validation -> not_passed
ai_capability_without_binding_validation -> not_passed
external_capability_without_binding_validation -> not_passed
```

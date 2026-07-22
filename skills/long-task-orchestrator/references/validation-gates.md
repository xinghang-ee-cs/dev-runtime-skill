# 验证门禁

本文件是 Validation Evidence Schema、字段要求和枚举的唯一事实来源。`validation-results.md` 只实例化结果并引用本文件，不得独立维护冲突枚举。

## 1. 验证用途

```text
prove_implemented_scope
prove_contract_consistency
prove_execution_constraint_compliance
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
execution_constraint_compliance
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
implementation_naming
implementation_placement
delegated_parameter_boundary
dependency_governance
```

字段定义：

- `capability_binding`: Capability Binding 是否完成。
- `runtime_binding`: Capability 是否已绑定对应 Runtime。
- `adapter_binding`: Capability Adapter 是否存在。
- `sdk_api_binding`: Capability 是否真实调用目标 SDK API。
- `permission_binding`: Capability 是否绑定权限处理。
- `fallback_binding`: Capability 是否定义并实现降级方案。
- `code_evidence`: Capability 对应代码证据。
- `why_not_automated`: 自动化不可执行时的具体原因；不得以此伪造 passed。
- `manual_required`: 交给 testing-layer-runtime 的人工/真实环境项；无项目时必须为 `[]`。
- `execution_constraint_validation`: Planning Handoff 执行约束合规结果。
- `evidence`: 自动化命令输出、报告路径、截图/trace 路径或失败记录；必须能进入 Long Testing Handoff。

`manual_required` 项格式：

```yaml
manual_required:
  - id:
    role:
    entry:
    action:
    expected_visible_state:
    reason:
    owner_runtime: testing-layer-runtime
```

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
- execution constraint compliance，覆盖命名、承接位置、参数委托边界与依赖治理。

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

## 7. Execution Constraint Compliance Validation

每个涉及代码的 TASK 在完成前必须记录：

```yaml
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
```

检查要求：

- Planning ID 只能出现在注释、文档引用、Runtime 追踪字段、验证与执行记录中。
- 扫描受影响代码、Schema、API、权限、配置和迁移，确认不存在期次、阶段、Sprint、迭代、版本或 Planning 编号命名。
- 实现必须使用稳定业务概念并位于 `task.md` 确认的承接位置。
- 创建新模块前必须检查现有业务域；新建长期业务域必须引用正式架构依据，否则失败，未新建则 `not_applicable`。
- Long 只能决定 Planning 标记为 `explicitly_delegated` 的私有技术参数。
- 依赖变更必须通过 Dependency Governance Gate；未变更则 `not_applicable`。

`code_evidence` 不只证明文件存在，必须证明合法承接位置、稳定业务命名、TASK 范围一致、无期次技术域、未越过 Handoff、新模块架构依据有效、依赖治理已通过且 Planning ID 只用于追踪：

```yaml
code_evidence:
  - path:
    task_ref:
    stable_business_concept:
    implementation_placement:
    constraint_check:
```

不得复制完整代码到验证结果。

```text
automated_tests_passed but execution_constraint_validation_failed -> TASK_NOT_DONE
build_passed but forbidden_phase_name_exists -> TASK_NOT_DONE
code_exists but implementation_placement_failed -> TASK_NOT_DONE
```

测试或构建通过不得覆盖架构、命名、承接位置或合同违规。

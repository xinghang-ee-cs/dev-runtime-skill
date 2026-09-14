# 验证门禁

本文件是 Validation Evidence Schema、字段要求和枚举的唯一事实来源。`validation-results.md` 只实例化结果并引用本文件，不得独立维护冲突枚举。

## 目录

- 1. 验证用途与边界
- Required Validation Matrix and Local Runnable Gate
- 2. 证据字段
- 3. 阶段验证证据
- 4. 后端合同证据
- 5. 完成边界验证证据
- 6. 验证报告要求
- 7. Execution Constraint Compliance Validation

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

自动化本地构建、产物/装载检查、进程启动、运行配置绑定、必需依赖就绪和最小行为探针属于开发期验证，不属于 `manual local testing`、服务器验收或最终验收，不得移交 Testing 代替 Long 完成。

## Required Validation Matrix and Local Runnable Gate

### 唯一事实源

```text
static rule -> this section
current phase required_validation_matrix -> Phase Runtime Directory/project-execution-baseline.md
executed evidence -> Phase Runtime Directory/validation-results.md
testing handoff -> references matrix revision and effective validation ids only
```

不得在 `task.md`、Checkpoint、Testing Handoff 或正式执行记录维护另一份平行的必要验证清单。上述文件只能引用 matrix revision、requirement id 和 validation id。

Testing 的 `business-journey-test-matrix.md` 不是本 Matrix 的副本：本 Matrix 只定义 Long 必须自动执行的交付单元/本地验证要求；Testing Matrix 只按 FLOW 汇总这些结果与后续人工、真机和部署后云端证据。两者通过 TEST/validation 引用连接，不复制命令、状态或规则正文。

### Matrix 派生

Preflight 必须从真实仓库、当前 Handoff 和已确认执行约束识别本次改变或被改变范围依赖的交付单元，包括但不限于 service、web client、worker、job、CLI、library/package、schema/migration 和其他可运行或可装载产物，并在当前期 `project-execution-baseline.md` 生成 `required_validation_matrix`。

Matrix 还必须消费 Planning Handoff 指定的 Test and Acceptance Plan：每项在本地可安全自动化且标记为 `mandatory_automated`，或经项目证据确认应由 Long 自动化的 P0/P1 业务/E2E TEST，都必须通过 `planning_test_refs` 映射为 `required` user-flow requirement。明确需要人工、真机或真实外部环境的 TEST 不伪装成自动化通过，而是精确进入 Long Handoff `manual_required`；同一 TEST 不得既遗漏于 Matrix，又遗漏于 `manual_required`。

每个交付单元必须按实际执行方式判断以下要求是否 `required | optional | not_applicable`：

- 静态/类型检查。
- 构建、打包或等价生成步骤。
- 预期产物存在且可由真实消费入口装载；没有产物的直接源码/解释执行模式必须提供仓库证据，并改为强制验证真实源码启动或装载入口。
- 运行配置绑定；只验证必需键是否进入目标进程及加载路径是否正确，不读取、输出或持久化秘密值。
- 本地或受控测试依赖就绪；数据库等依赖必须区分配置缺失、服务不可达、Schema/Migration 不就绪和业务探针失败。
- 可运行单元的进程启动与稳定就绪探针；可装载单元的 import/load/package smoke；migration-only 单元的非破坏性 schema/migration 检查。
- 至少一个从真实入口触发的最小行为 smoke；纯库或包以真实消费/装载入口替代服务探针。
- 启动了临时进程或资源时的受控清理。

Matrix 必须在同一 `requirements` 列表显式声明 `artifact_readiness`、`runtime_configuration`、`dependency_readiness` 与 `process_readiness` 的适用性；`not_applicable` 必须带具体原因，省略不代表不适用。`runnable` 必须具有 required `process_readiness` 和至少一项 `user_flow | business_rule | contract` 最小行为验证；`loadable` 必须具有 required `artifact_readiness` 与真实消费验证；`migration_only` 必须具有 required `schema_readiness`。这些约束只定义通用验证类别，不假设具体技术栈或命令。

Matrix 中每个 `required` 项必须具有唯一 `requirement_id`、适用的 `planning_test_refs`、项目派生的现有命令/探针或由已确认 TASK 明确创建的 planned binding、可验证成功后置条件、由 Agent 按当前授权与项目事实声明的安全执行边界，以及与每条后置条件一一对应的 `machine_execution.postcondition_probes`。`safe_execution_boundary` 是 Prompt/流程层的执行声明，runner 只校验枚举并记录，不证明目标环境、凭证或命令本身安全。`binding_status: planned_in_confirmed_task` 必须用 `planned_task_revision: TASK-ID@revision` 精确引用当前可执行队列中的明确任务，并须在该任务完成前更新为 `existing`；命令、入口、依赖或成功条件仍为 `unresolved` 时 Preflight 不得打开相关 TASK 的 execution gate。

以下规则保持通用：

- 不假设语言、框架、包管理器、输出目录、端口、健康检查路径、数据库或部署方式。
- 使用项目已有脚本、配置和正式合同；缺失且在已确认 TASK 范围内时登记 `planned_in_confirmed_task`，实现后更新 Matrix 再验证；超出范围或需要用户/外部方提供时转 `BLOCKED`。
- 只通过 `run-long-validation.sh|ps1` 执行 required 探针。`argv` 以参数数组、`shell=False` 和超时运行，stdout/stderr 以流式摘要和字节数处理，不在内存或 Runtime 保留正文；超时回收进程树。`path_exists` 直接观察项目根目录内的文件/目录。Receipt 先完整写入同目录临时文件，再原子创建且绝不覆盖，避免半写证据、无界输出和凭证或业务数据固化。
- `noEmit`、解释执行或无构建步骤本身不是失败，但必须证明真实消费路径不依赖编译产物，并通过对应启动/装载 smoke。
- Agent 在形成 Matrix 和执行前必须遵守当前授权：远程/生产资源不得作为默认探针目标，优先使用本地、隔离或明确批准的受控环境，禁止为了验证读取或打印秘密值、连接未知生产库或执行未授权迁移。Skill 与 runner 负责流程和输出稳定性，不承担代码级环境隔离、凭证扫描或命令安全证明。
- 外部能力的最终真实环境验收可以交给 Testing；若缺少它会使本地目标进程无法启动或最小业务 smoke 无法执行，则是 Long 的必需运行依赖阻断，不得转成 `manual_required` 后继续通过。
- 没有本地可运行服务的交付物可以将进程启动标记为 `not_applicable`，但仍必须通过适用于其真实消费方式的 build/package/load/schema 等必要验证。

### Evidence Gate

每条验证结果必须引用实际消费的 `matrix_revision`、`requirement_id` 和 `delivery_unit_id`。`required` 项只有同时满足以下条件才能为 `passed`：

```text
machine postcondition probes actually executed by the runner
+ exit/result successful
+ every success_postcondition evidenced
+ machine execution receipt binds runtime epoch, matrix, repository revision, requirement, attempt and exact probe specification
+ evidence belongs to current matrix revision, or has explicit unchanged carry-forward compatibility evidence
+ evidence belongs to current code/config state
```

以下任一情况都不得视为通过：

```text
typecheck used as build evidence
build exit zero without required artifact/loadability postcondition
process compiler/watch reports zero errors but target process never becomes ready
config helper exists but required keys are not proven bound to the target process
mock/unit test used as process boot or dependency readiness evidence
required result in failed|blocked|not_run
required result missing
required validation skipped with a reason
evidence belongs to stale matrix revision without explicit unchanged carry-forward compatibility evidence
passed written by an Agent without a valid machine execution receipt
```

验证修复后允许保留历史失败，但完成门禁只采用同一 `requirement_id` 的最新有效结果；最新结果必须为 `passed`，并引用 runner 生成的不可覆盖、摘要防篡改 execution receipt 及修复后的代码与配置状态。失败 receipt 作为历史保留；重跑必须递增 `attempt` 并使用新的 `validation_id`，不得覆盖或把失败 receipt 改成通过。Matrix revision 变化时只精确失效新增或语义变化的 requirement；未受影响项只有在 requirement id、机器探针、成功后置条件、安全边界及相关代码/配置均未变化，并在 `validation-results.md` 记录兼容依据时才可延用。

### Local Runnable Gate

完成边界前必须重新扫描当前交付单元与 Matrix 覆盖关系，并计算：

```text
matrix_covers_all_changed_or_required_delivery_units
+ every locally automatable required Planning TEST is mapped
+ every manual/real-environment Planning TEST is explicitly handed off
+ all_required_requirements_have_current_passed_evidence
+ no_required_requirement_failed_blocked_not_run_or_missing
+ runtime_required_dependencies_ready
+ runnable_or_loadable_entry_verified
= local_runnable_gate_passed
```

任何必需项失败、阻断、未运行、缺失或 Matrix 漏项都自动视为 P0 Completion Blocker：相关 TASK 不得 `DONE`，Runtime 不得输出 `ready_for_local_test` 或 `ready_for_local_retest`。用户可以决定暂停、补充环境或调整正式合同，但不能在保留 `ready_for_local_test` 语义的同时豁免该门禁。

### Deterministic Readiness Validation

Completion Boundary 不得只依赖自然语言复核。Long 必须在写入 ready 状态前与写入后分别运行唯一 Python 核心的跨平台薄入口：

```bash
bash <long-skill-path>/scripts/validate-long-readiness.sh <runtime> --advance-workflow preflight
bash <long-skill-path>/scripts/validate-long-readiness.sh <runtime> --advance-workflow execution
bash <long-skill-path>/scripts/run-long-validation.sh <runtime> --requirement-id <REQ-ID> --validation-id <VALIDATION-ID> --attempt <N>
bash <long-skill-path>/scripts/validate-long-readiness.sh <runtime> --advance-workflow completion_validation
bash <long-skill-path>/scripts/validate-long-readiness.sh <runtime> --advance-workflow ready_for_local_test
bash <long-skill-path>/scripts/validate-long-readiness.sh <runtime> --expect-ready --write-receipt
```

PowerShell 使用 `validate-long-readiness.ps1` 和相同参数；无法使用包装器时才直接调用 `validate_long_readiness.py`。

`long-workflow-state.json` 是脚本拥有的粗粒度前向账本：初始 cycle 只允许 `preflight -> execution -> completion_validation -> ready_for_local_test`；patch 以递增 cycle 执行 `patch_execution -> patch_validation -> ready_for_local_retest`，通常从既有 ready 开启；若已进入任一 validation 阶段才发现必须修正，也从该阶段开启新的 patch cycle，绝不倒拨或改写旧 cycle。同阶段任务仍按依赖图并行；普通 blocker 停留当前阶段，不创建回退边。校验器同时对账 Planning TEST 自动化等级、结构化 inventory 与真实 source refs、机器计算的 code/config revision、可解析非空证据、Matrix/任务/Handoff，并在 ready 后生成冻结这些事实的 `long-readiness-receipt.json`。任一错误返回非零，人工判断不得覆盖。

`--write-receipt` 只能在 ready stage 使用，并且必须放在本 cycle 的 checkpoint、archive、cleanup、close 回写全部完成之后；它是 Testing 接管前的最终密封动作。Receipt 生成后出现任何新增或变更文件都会使验证失败，必须用新的 patch cycle 重新收敛，不能在旧 receipt 后补写。

迁移是进入目标阶段，不是事后补记：`execution / patch_execution` 入口校验执行合同、Planning TEST 分类和 Matrix 计划，required binding 可为 `planned_in_confirmed_task | existing`，不要求尚待实现的 source 文件已经存在；`completion_validation / patch_validation` 才把 binding 收紧为 `existing`，并强制 inventory、真实 source、revision、验证结果和证据闭环。这样新项目可开始实现，但绝不能以 planned 状态越过完成边界。

Validation Results 中每个 `postcondition_results[].evidence`、`evidence[]` 和 carry-forward evidence 都必须是可解析、非空的持久化文件；外部 CI、平台或用户反馈先写入本期 Runtime 的脱敏证据记录，再引用该本地文件。只写路径字符串、命令文本或 `result: passed` 不构成证据。

Receipt 只保存摘要，不保存文件正文；即便如此，校验器仍拒绝 `.env`、credential/secret/key 等敏感路径和 Runtime symlink，防止为密封动作额外读取秘密或越出 Runtime。

## 2. 证据字段

```yaml
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

同一 `requirement_id` 的正式 Matrix 结果必须具有唯一正整数 `attempt`、ISO-8601 `time` 和当前 `code_config_revision`。当前结果按最大 attempt 选择；attempt 与时间顺序冲突、code/config revision 与 `completeness_audit.repository_scan_revision` 不一致时均阻断。

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
frontend_contract_compliance
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
- `manual_required[].planning_test_refs`：该人工/真机/真实环境项承接的 Planning TEST 引用；不得让同一 TEST 同时遗漏于 Matrix 和人工移交。
- `execution_constraint_validation`: Planning Handoff 执行约束合规结果。
- `frontend_contract_validation`: UI TASK 实际消费的 05 Manifest、Prompt/PAGE/UI-MOD/UX-SCN/ASSET revision 及结构、响应式、状态、交互、可访问性与视觉对照结果；唯一字段格式见 `frontend-experience-execution.md`。
- `evidence`: 自动化命令输出、报告路径、截图/trace 路径或失败记录；必须能进入 Long Testing Handoff。
- `matrix_revision`、`requirement_id`、`delivery_unit_id`、`requirement_level`：绑定当前期 Required Validation Matrix；不属于 Matrix 的补充验证可将后三者标记为 `not_applicable`，但不得替代任何 `required` 项。
- `postcondition_results`：逐项记录 Matrix 中 `success_postconditions` 的验证结果与证据引用；只记录命令退出码不足以证明产物、启动或依赖已就绪。
- `matrix_compatibility`、`compatibility_evidence`：记录结果属于当前 revision，或为何可从旧 revision 精确延用；不得用笼统的“未受影响”替代字段级比较。

`manual_required` 项格式：

```yaml
manual_required:
  - id:
    planning_test_refs: []
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
- UI TASK 按 `frontend-experience-execution.md` 覆盖精确合同 revision、default/loading/empty/error/success/blocked、trigger/pending/success/failure/retry/cancel/back、目标视口、键盘焦点与可访问名称；项目已有截图/视觉回归能力时绑定确认的 ASSET revision。
- 项目基线中可用的最小相关验证命令。
- 当前 `required_validation_matrix` 中所有 `required` 项；不得只选择容易通过的命令。
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
- Required Validation Matrix coverage 和 `local_runnable_gate_passed` 证据。
- vitest/jest/integration/api-test/playwright evidence when applicable
- external capability real-call evidence or explicit planning BLOCKER
- skipped or unavailable checks with reason
- frontend score
- backend score
- Long Testing Handoff classification: `automated_passed` / `automated_failed` / `automated_skipped` / `manual_required`
- execution constraint compliance，覆盖命名、承接位置、参数委托边界与依赖治理。
- frontend contract compliance，覆盖 Prompt/PAGE/UI-MOD/UX-SCN/ASSET revision 与自动化/人工边界。

## 6. 验证报告要求

```text
validation_result -> validation-results.md
unavailable_validation -> explicit_record
unchecked_item -> not_passed
missing_required_validation_matrix -> not_passed
incomplete_required_validation_matrix -> not_passed
missing_required_validation_result -> not_passed
required_validation_failed_blocked_or_not_run -> not_passed
required_validation_skipped -> not_passed
stale_matrix_evidence -> not_passed
local_runnable_gate_not_passed -> not_passed
frontend_score != backend_score
unsupported_validation_claim -> forbidden
mock_only_capability_validation -> not_passed
missing_capability_real_call_evidence -> not_passed
missing_capability_binding_fields -> not_passed
UI_TASK_without_frontend_contract_validation -> not_passed
frontend_contract_revision_mismatch -> not_passed
visual_comparison_unavailable_without_manual_required -> not_passed
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

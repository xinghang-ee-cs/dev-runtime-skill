# Test Writeback

## 目录

- 回写目标与必须维护的文件
- Long Handoff、执行顺序与业务旅程矩阵
- Change Triage 与人工队列
- 测试结果、Runtime 状态与事件
- 证据索引与 Deployment Revision Reconciliation Gate
- Release Handoff
- 回写时机、失败处理、确定性校验与 Test Progression Gate
- 禁止项

## 回写目标目录

`<phase_testing_runtime_directory>/`

`<phase_testing_runtime_directory>` 必须由当前 Planning/Long Handoff、项目期次目录约定和既有 Runtime 事实解析为唯一 `writeback_target`，不是固定目录名。

Testing Runtime 只写本期 Runtime 输出目录；不得修改 planning SoT 或业务产物。本期测试状态、事件、证据、队列、依赖、Change Triage 与恢复数据不得写入项目根目录 `.runtime/`；根 `.runtime/` 只允许该 Skill 明确定义的跨期项目级环境索引或稳定配置。

## 必须维护的文件

- `test-runtime-state.md`：当前阶段、当前环境、总状态、阻塞项、最后更新时间。
- `testing-workflow-state.json`：脚本原子维护的粗粒度前向阶段账本；不保存单项测试状态。
- `test-execution-events.md`：测试阶段事件，不写长日志。
- `test-validation-results.md`：所有正式 `item_type`（包括环境前置核验）的完整生命周期与最终执行状态唯一事实源。
- `test-evidence-index.md`：证据路径、截图路径、命令摘要、人工证据来源、long evidence 来源。
- `manual-test-queue.md`：待人工执行、待补证据、已确认/未确认的人工测试操作；不是 case 清单，而是用户实际操作队列。同一用户操作只能出现一次；多个 case 可以挂载到同一个操作项下。
- `test-execution-order.md`：测试顺序、依赖、阻塞关系。
- `business-journey-test-matrix.md`：Planning FLOW 到本地业务/E2E、部署后云端业务/E2E 和正式结果引用的覆盖索引；不保存测试项正式状态。
- `change-triage.md`：测试发现的分类、影响范围、当前合同是否仍有效和下游 disposition；不替代 Planning Change Set 或业务 SoT。
- `release-handoff.md`：仅在进入 Release Handoff Mode 时生成；保存发布前 DEP、测试结果和证据的只读移交快照，不承担发布后的持续状态。

## Long Testing Handoff 回写

读取 `testing-handoff.md` 或 `long-runtime-testing-summary.md` 后，必须把以下最小入口绑定记录到 `test-runtime-state.md.intake_binding`；不复制整个 Long Handoff：

```yaml
intake_binding:
  current_test_epoch:
  writeback_target:
  planning_handoff_ref:
  planning_baseline_revision:
  active_change_revision: # 初始 Handoff 省略
  long_testing_handoff_ref:
  long_runtime_epoch:
  required_validation_matrix_ref:
  required_validation_matrix_revision:
  required_validation_gate_result: <passed | blocked>
  intake_verified_at:
```

`required_validation_gate.result` 必须为 `passed`，且 Handoff 必须包含 `validator_receipt_ref: long-readiness-receipt.json`。Testing 只接受 `long-readiness-receipt/v2`，重算 receipt digest、Long workflow history digest、repository/Matrix revision、effective validation ids、每个 effective Validation Entry 的 `execution_receipt_ref` 及全部冻结文件摘要；机器 receipt 必须由 `long-machine-runner/v2` 生成并绑定同一 Runtime、Matrix、repository revision 和 validation id。任一缺失、变化或证据不完整时，Testing Runtime 为 `blocked`，不得通过重跑或人工测试改写。

Test Intake 必须重新打开真实 Planning Handoff、其 `Requirement and Scope` 与 `Test and Acceptance Plan` 路径，以及 Long Handoff 所在 Runtime 的 Matrix 和 Validation Results。`executed_task_contract_revisions` 必须与 Planning 的 `execute_only | resume_only | reexecute_affected_part` 精确相等；`automated_passed[].source_validation_id` 必须唯一且与 effective validation ids 精确相等。每个 effective validation id 必须解析到当前 Matrix revision 的 passed 证据，或解析到 Long 已用 `matrix_compatibility: carried_forward_unchanged` 和持久 compatibility evidence 明确批准的旧 Matrix passed 证据。只比较 Handoff 中几个同名字符串不构成通过。

每一个继承的自动化 case 必须写入 `test-validation-results.md`，使用完整字段集：

```yaml
item_id:
item_type: case
attempt:
environment:
environment_revision_ref: not_applicable
status: reused_from_long
source_validation_id: <Long effective validation id>
started_at:
completed_at:
depends_on_check:
expected_evidence:
frontend_contract_refs: []
result_summary:
evidence_refs:
evidence_missing_reason: null
blocker_or_failure_reason: null
covers: []
covered_by: []
evidence_reuse: true
writeback_status: updated
```

禁止在任何文件中继续使用 `result`、`evidence`、`rerun_required` 作为自动化继承结果字段。

## test-execution-order.md 格式

`test-execution-order.md` 只维护依赖、顺序及显式移出范围的依赖关系，不记录测试项的正式 `status`。是否可执行、是否阻塞、是否通过，必须由 `test-validation-results.md` 的状态和依赖计算得出。

```yaml
TEST-001:
  depends_on: []

TEST-002:
  depends_on:
    - TEST-001

TEST-003:
  depends_on:
    - TEST-002

TEST-004:
  depends_on:
    - TEST-003
  dependency_deferred_out_of_scope: []
```

规则：

- `depends_on` 全部通过后，当前测试才能执行。
- `reused_from_long` 视为依赖已通过。
- 前置失败时当前测试执行时被标记为 `blocked_by_dependency`（写入 `test-validation-results.md`），不得执行。
- 前置被用户移出当前范围时，当前测试可继续，但必须记录 `dependency_deferred_out_of_scope`。

## business-journey-test-matrix.md 格式

本文件只维护覆盖关系，不记录正式 `status`；所有测试项结果仍只来自 `test-validation-results.md`。

```yaml
matrix_revision:
planning_scope_refs: []
long_handoff_ref:
required_validation_gate_ref:
deployment_revision_ref: test-runtime-state.md#current_deployment_revision
journeys:
  - flow_ref:
    priority: <P0 | P1 | P2>
    success_journey_test_refs: []
    contract_defined_negative_test_refs: []
    local_business_e2e:
      requirement: <required | not_applicable>
      result_refs: []
    deployed_environment_e2e:
      requirement: <required | not_applicable>
      selection_reason: <p0_success_journey | deployment_sensitive | change_affected | no_deployment_in_scope | not_applicable>
      deployment_sensitivity: []
      result_refs: []
    open_coverage_gaps: []
coverage_summary:
  required_flow_count:
  locally_covered_flow_count:
  cloud_required_flow_count:
  cloud_covered_flow_count:
  open_required_gaps: []
```

规则：

- `flow_ref`、priority、TEST refs 和 required/not_applicable 来自 Planning Test and Acceptance Plan；Testing 不新增业务范围。本期部署适用时，P0 正向旅程必须为 `p0_success_journey / required`，P1 只有部署敏感或受当前变更影响时为 `required`；本期无部署目标时写 `no_deployment_in_scope / not_applicable`。
- `planning_scope_refs` 和 `journeys[].flow_ref` 必须与 Planning `Requirement and Scope` 的 FLOW 集合精确相等；priority、`success_journey_test_refs` 以及本地/云端 requirement 必须从真实 FLOW/TEST 合同派生。Testing 自己写出的矩阵和覆盖计数不能证明上游范围完整。
- `result_refs` 只引用 `test-validation-results.md` 项或其中已继承的 Long evidence，不复制结果正文。
- 每个 required result 必须使用正式 `item_type` 和完整结果字段，`covers` 至少包含当前 FLOW 对应的一个 Planning TEST；其每条证据必须按本文件唯一 schema 填齐本地或部署 revision、`flow_refs` 与来源，不允许任意探针或游离证据关闭业务旅程。
- `deployment_revision_ref` 必须引用 `test-runtime-state.md#current_deployment_revision`，不得在矩阵复制部署身份。每个 `deployed_environment_e2e.requirement: required` 的结果和证据都必须解析到该完整身份。
- 每次 Planning/Long revision、测试结果、证据有效性或 finding 状态变化后，精确更新受影响引用并重新计算 `coverage_summary`。部署身份变化只按本文件的 Deployment Revision Reconciliation Gate 处理；本规则不建立第二套失效顺序。
- required FLOW 缺少本地或适用的云端结果、结果为 failed/blocked/evidence_insufficient，引用证据为 stale/invalid/revision_mismatch，或存在未闭环 finding 时，必须写入 `open_required_gaps`；不得省略以获得通过结论。`stale` 是证据有效性，不是测试项 `status`。

## change-triage.md 闭环字段

每个发现必须保持唯一 `finding_id`，并至少记录：

```yaml
finding_id:
finding_status: <open | handed_to_long | waiting_planning | waiting_redeploy | retest_required | closed>
change_decision:
affected_flow_refs: []
affected_test_refs: []
affected_result_refs: []
superseded_evidence_refs: []
replacement_planning_handoff_ref:
replacement_long_handoff_ref:
replacement_required_validation_gate_ref:
redeployed_revision_ref:
retest_result_refs: []
closure_evidence_refs: []
```

规则：

- `implementation_defect` 交给 Long 后为 `handed_to_long`；收到 patch Handoff 且 `required_validation_gate: passed` 后转 `retest_required`，需要云端复验时先转 `waiting_redeploy`。
- `planning_gap | requirement_change | design_drift` 需要规划重入时为 `waiting_planning`；只有新的 Planning Handoff、Long Handoff 和受影响复测证据齐全后才能关闭。
- `closed` 必须有 `retest_result_refs` 和 `closure_evidence_refs`，并且业务旅程矩阵中受影响 required gap 已消失。只记录“代码已改”“已重新部署”或“用户说应该好了”不得关闭。
- 历史失败与被替代证据保留，通过 `superseded_evidence_refs` 精确失效；未受影响结果不得无条件失效。

## manual-test-queue.md 格式

`manual-test-queue.md` 只管理人工操作队列，不得记录 case 或 MANUAL-OP 的正式 `status`。

```yaml
MANUAL-OP-001:
  operation_signature: system_admin|admin-maintenance-config|project-exists|create-or-stop-region|test-domain
  user_facing_operation: 打开配置页，创建/停用区域并确认列表状态
  depends_on:
    - TEST-P7-CONFIG-001
  blocked_by: []
  queue_state: ready
  user_guidance:
    role_or_account: 系统管理员账号
    entry: 后台维护配置页
    precondition: 项目已存在，当前使用测试数据
    steps:
      - 打开维护配置页
      - 创建或停用一个区域
      - 返回列表查看区域状态和团队绑定状态
    observe:
      - 区域列表可见
      - 停用状态可见
      - 团队绑定可见
    feedback_hint: 可以自然反馈”列表状态正常””停用状态没显示”或直接发截图
  frontend_contract_refs:
    page_contract_refs: []
    module_contract_refs: []
    interaction_contract_refs: []
    asset_refs: []
    viewport_or_device: not_applicable
    allowed_visual_differences: []
  covers:
    - TEST-P7-REGION-001
    - TEST-P7-TEAM-001
    - TEST-P7-PERM-001
  evidence_need:
    - region list visible
    - stopped state visible
    - team binding visible
  covered_by_evidence: false
```

`queue_state` 取值及含义：

| `queue_state` | 含义 | 可执行 |
| --- | --- | --- |
| `ready` | 依赖已满足，可引导用户执行 | 是 |
| `waiting_dependency` | 依赖项尚未通过 | 否 |
| `blocked_by_environment` | 环境条件不满足 | 否 |
| `covered` | 已被已有证据完整覆盖 | 否 |
| `awaiting_user_feedback` | 已引导用户，等待反馈 | 否 |
| `not_actionable` | 当前不可操作，原因需在 `blocked_by` 中说明 | 否 |

字段含义：

- `depends_on`：当前人工操作执行前必须已经通过或完成的 case、manual operation 或环境前置项。
- `blocked_by`：当前人工操作无法执行时的阻塞项；无阻塞时为空数组。
- `queue_state`：操作调度状态，用于决定是否引导用户；不得使用 `verified`、`verified_by_user_report`、`failed`、`blocked`、`reused_from_long`、`pending_manual`、`pending_server` 等正式测试状态。
- 当 `queue_state` 为 `ready`、`depends_on` 全部通过、`blocked_by` 为空且未被 `covered_by_evidence` 覆盖时，AI 可以选择该操作作为下一个人工测试操作。
- `user_guidance` 只用于 AI 生成用户态引导，不要求用户填写。它必须帮助非专业用户知道下一步怎么做。
- `covered_by_evidence`：`true` 表示该操作已被已有证据覆盖，无需再次引导用户执行。
- `frontend_contract_refs`：仅 UI/UX 合同验证适用；必须来自 Planning Handoff 与 Long Testing Handoff 一致的精确 revision，并写明视口/设备和允许差异。非 UI 操作使用 `not_applicable`，不得填空引用。

## test-validation-results.md 格式

每个测试项必须拥有独立记录。这是每个测试项完整生命周期的唯一事实源。

```yaml
TEST-001:
  item_id: TEST-001
  item_type: case
  attempt: 1
  environment: local
  environment_revision_ref: not_applicable
  status: reused_from_long
  source_validation_id: VALIDATION-001
  started_at: “2026-06-30T10:00:00+08:00”
  completed_at: “2026-06-30T10:00:30+08:00”
  depends_on_check: passed
  expected_evidence: long evidence
  result_summary: 继承 long 自动化结果，所有断言通过
  evidence_refs:
    - EVIDENCE-LONG-001
  evidence_missing_reason: null
  blocker_or_failure_reason: null
  covers: []
  covered_by: []
  evidence_reuse: true
  writeback_status: updated

MANUAL-OP-001:
  item_id: MANUAL-OP-001
  item_type: manual_op
  attempt: 1
  environment: local
  environment_revision_ref: not_applicable
  status: verified_by_user_report
  started_at: “2026-06-30T10:05:00+08:00”
  completed_at: “2026-06-30T10:08:00+08:00”
  depends_on_check: passed
  expected_evidence: screenshot + user feedback
  result_summary: 用户确认区域列表和停用状态均正常
  evidence_refs:
    - manual-evidence/MANUAL-OP-001-screenshot.png
    - manual-evidence/MANUAL-OP-001-user-feedback.md
  evidence_missing_reason: null
  blocker_or_failure_reason: null
  covers:
    - TEST-P7-REGION-001
    - TEST-P7-TEAM-001
    - TEST-P7-PERM-001
  covered_by: []
  evidence_reuse: false
  writeback_status: updated

TEST-P7-PERM-001:
  item_id: TEST-P7-PERM-001
  item_type: case
  attempt: 1
  environment: local
  environment_revision_ref: not_applicable
  status: verified_by_user_report
  started_at: “2026-06-30T10:05:00+08:00”
  completed_at: “2026-06-30T10:08:00+08:00”
  depends_on_check: passed
  expected_evidence: user feedback on permission
  result_summary: 通过 MANUAL-OP-001 复用证据确认权限正常
  evidence_refs:
    - manual-evidence/MANUAL-OP-001-user-feedback.md
  evidence_missing_reason: null
  blocker_or_failure_reason: null
  covers: []
  covered_by:
    - MANUAL-OP-001
  evidence_reuse: true
  writeback_status: updated

DEP-CLOUD-001:
  item_id: DEP-CLOUD-001
  item_type: environment_prerequisite
  dependency_ref: <Planning Handoff 中的 DEP-ID 引用>
  required_stage: before_cloud_test
  planning_snapshot_status: <12 中 Planning 截止状态>
  owner: <来自 DEP>
  blocking_scope: <来自 DEP>
  attempt: 1
  environment: deployed
  environment_revision_ref: test-runtime-state.md#current_deployment_revision
  status: pending
  started_at: null
  completed_at: null
  depends_on_check: passed
  expected_evidence: <DEP safe_verification 指定的脱敏证据>
  result_summary: 等待在批准渠道完成并安全核验
  evidence_refs: []
  evidence_missing_reason: null
  blocker_or_failure_reason: null
  covers: []
  covered_by: []
  evidence_reuse: false
  writeback_status: updated
```

字段说明：

- `item_id`：测试项唯一标识。
- `item_type`：`case` / `manual_op` / `real_device` / `deployed_e2e` / `server_verification` / `environment_prerequisite`。
- `dependency_ref`、`required_stage`、`planning_snapshot_status`、`owner`、`blocking_scope`：仅 `environment_prerequisite` 必填；引用 Planning DEP 定义与截止快照，不复制配置秘密或建立第二个 DEP。
- `attempt`：第几次尝试；仅在实际重新执行时递增，恢复判断和修复游标不递增。
- `environment_revision_ref`：本地或不依赖部署的项写 `not_applicable`；部署后验证项必须引用 `test-runtime-state.md#current_deployment_revision`，不得复制 revision 值。
- `status`：测试项生命周期的唯一正式状态字段，使用完整状态枚举（见 `01-test-runtime-core.md` 状态枚举）。不得使用 `final_status`。
- `started_at`：本次执行开始时间。
- `completed_at`：本次执行完成时间；`in_progress` 项可为空。
- `depends_on_check`：依赖检查结果；`passed` / `failed` / `pending`。
- `expected_evidence`：预期证据类型描述。
- `frontend_contract_refs`：UI/UX 测试适用时记录 PAGE/UI-MOD/UX-SCN/ASSET 精确 revision；非 UI/UX 测试为 `[]`。
- `result_summary`：简短结果描述。
- `evidence_refs`：证据引用路径列表；正式证据字段名，不得使用 `evidence`。
- `evidence_missing_reason`：证据缺失原因；`evidence_insufficient` 或证据不完整时必填。
- `blocker_or_failure_reason`：失败或阻塞原因；正式字段名，不得使用 `failure_or_blocker_reason`。`failed` / `blocked` / `blocked_by_dependency` 时必填。
- `covers`：当前项覆盖的其他 case / assertion 列表。
- `covered_by`：当前项被哪个 MANUAL-OP 或证据覆盖。
- `evidence_reuse`：`true` / `false`。
- `writeback_status`：`pending` / `updated` / `blocked`。`updated` 表示该记录已成功写入。

## test-runtime-state.md 格式

```yaml
intake_binding:
  current_test_epoch: <resolved epoch>
  writeback_target: <phase_testing_runtime_directory>
  planning_handoff_ref: <current Planning Handoff path>
  planning_baseline_revision: <current revision>
  active_change_revision: <incremental revision; initial Handoff omits this key>
  long_testing_handoff_ref: <current Long Testing Handoff path>
  long_runtime_epoch: <Long runtime epoch>
  required_validation_matrix_ref: <Long Baseline matrix ref>
  required_validation_matrix_revision: <current matrix revision>
  required_validation_gate_result: passed
  intake_verified_at: “2026-06-30T09:59:00+08:00”
current_phase: manual_testing
current_environment: local
business_journey_matrix_ref: business-journey-test-matrix.md
business_journey_matrix_revision: <current matrix revision>
current_deployment_revision:
  status: not_applicable
  target_environment: not_applicable
  identity_mode: not_applicable
  revision_kind: not_applicable
  revision: not_applicable
  identity_digest: not_applicable
  evidence_ref: not_applicable
  component_revisions: []
  runtime_configuration_identity:
    status: not_applicable
    revision_kind: not_applicable
    revision: not_applicable
    evidence_ref: not_applicable
    secret_values_included: false
deployment_revision_reconciliation:
  status: not_required
  transition_id: not_applicable
  from_identity: not_applicable
  candidate_identity: not_applicable
  from_identity_digest: not_applicable
  candidate_identity_digest: not_applicable
  invalidated_evidence_refs: []
  removed_result_refs: []
  opened_gap_refs: []
  invalidated_release_handoff_ref: not_applicable
  started_at: null
  completed_at: null
active_release_handoff:
  status: not_generated
  snapshot_id: not_applicable
  snapshot_ref: not_applicable
  bound_deployment_identity_digest: not_applicable
  snapshot_digest: not_applicable
  invalidated_by: null
current_item: MANUAL-OP-002
current_item_status: in_progress
last_completed_item: MANUAL-OP-001
next_executable_item: MANUAL-OP-002
last_durable_checkpoint_at: “2026-06-30T10:08:00+08:00”
resume_required: false
overall_status: in_progress
blockers: []
last_updated_at: “2026-06-30T10:08:30+08:00”
```

字段说明：

- `intake_binding`：当前 Testing Runtime 的唯一入口身份与恢复绑定。`current_test_epoch`、`writeback_target`、Planning/Long Handoff、Long runtime epoch、Planning revision、Required Validation Matrix revision 与 Gate 结果必须同时可解析且一致；初始 Handoff 省略 `active_change_revision`，增量 Handoff 必须包含。不得只在会话内存中保存这些事实。
- `business_journey_matrix_ref / revision`：当前业务旅程矩阵的唯一恢复指针；矩阵变化时同步更新 revision，并先失效现有 Release Handoff。
- `current_item`：当前正在执行的测试项 ID。
- `current_deployment_revision`：部署后云端测试的唯一当前部署身份事实。进入云端测试前必须为 `status: known`，填写目标环境、`identity_mode`、精确 `revision_kind / revision` 和证据引用。本期无部署目标时整体使用 `not_applicable`；未知时使用 `status: unknown` 并阻断云端 required 项。
- `identity_digest`：把 `target_environment / identity_mode / revision_kind / revision`、按 `component_id` 排序的组件 `component_id / revision_kind / revision`、运行配置 `status / revision_kind / revision` 组成 JSON 对象，使用 UTF-8、递归 `sort_keys=true` 和紧凑分隔符 `(',', ':')` 序列化后计算 SHA-256，保存为 `sha256:<64 lowercase hex>`；证据路径、时间和秘密值不进入摘要。`status: known` 时必填，身份任一部分变化都必须产生新 digest。
- `identity_mode` 只允许 `single_revision | aggregate_deployment | component_set | not_applicable`。单体或单一镜像使用 `single_revision`；平台已有统一 deployment/build ID 时使用 `aggregate_deployment`；前端、后端、worker 等独立发布且没有统一 ID 时使用 `component_set`。
- `revision_kind` 只允许 `commit | build | image_digest | deployment_id | deployment_set_digest | not_applicable`。`component_set` 必须把按 `component_id` 排序后的非秘密组件 revision、目标环境和 `runtime_configuration_identity.revision` 共同生成稳定 `deployment_set_digest`，并在 `component_revisions` 逐项记录 `component_id`、组件 `revision_kind`、精确 `revision` 和证据引用；不得只选择其中一个服务冒充整套部署版本。
- mode/kind 必须一致：`single_revision` 只允许 `commit | build | image_digest` 且 `component_revisions: []`；`aggregate_deployment` 只允许 `deployment_id | build` 且 `component_revisions: []`；`component_set` 只允许 `deployment_set_digest` 且组件列表非空、`component_id` 唯一。`not_applicable` 只能与整体 `status: not_applicable` 同时使用。
- `runtime_configuration_identity`：覆盖部署产物之外会改变运行行为的公开配置、路由/代理、域名/CORS、基础设施绑定和秘密版本绑定。`status` 只允许 `known | not_applicable | unknown`；部署适用时只有经证明确实没有产物外配置才可使用 `not_applicable`，`unknown` 阻断 cloud-required 测试。`revision_kind` 只允许 `platform_configuration_revision | sanitized_manifest_digest | not_applicable`；摘要只能使用脱敏配置清单、键名、公开值和批准渠道提供的非秘密版本标识，禁止读取、包含或散列秘密值。
- `deployment_revision_reconciliation`：最近一次部署身份切换事务的恢复检查点；字段、顺序和通过条件只由下文 Deployment Revision Reconciliation Gate 定义。事务开始后 `from_identity_digest / candidate_identity_digest` 必须分别等于完整身份对象的 digest；`status: completed` 时 candidate digest 必须等于当前 `identity_digest`。`status: in_progress | blocked` 时禁止任何 cloud-required 测试、覆盖通过结论和 Release Handoff。
- `status: in_progress | blocked | completed` 时，`from_identity` 与 `candidate_identity` 必须展开为和 `current_deployment_revision` 相同的完整 schema，不能保留 `not_applicable`。`completed` 还必须能在 `test-execution-events.md` 解析到同一 `transition_id` 的 started/completed 事件；缺少身份或恢复事件时保持阻断。
- `active_release_handoff`：当前 Release Handoff 快照指针和有效性唯一来源。只允许 `not_generated | current | invalidated`；`current` 必须指向同一 epoch、revision、业务旅程矩阵、完整部署身份和 `snapshot_digest` 的快照，部署身份或覆盖合同变化时必须先转为 `invalidated`。
- `current_item_status`：当前项状态；`in_progress` 时必须有对应的前置检查点记录。
- `last_completed_item`：最近一个完成且 writeback_status = updated 的测试项。
- `next_executable_item`：下一个可执行的测试项；依赖未满足时为空。
- `last_durable_checkpoint_at`：最后一次成功写入检查点的时间。
- `resume_required`：`true` 表示存在 `interrupted_pending_reconcile` 项需要恢复。

## test-execution-events.md 格式

只追加简短事件，不写长日志，不作为最终状态事实源。

```yaml
- timestamp: “2026-06-30T10:05:00+08:00”
  event_type: test_started
  item_id: MANUAL-OP-001
  from_status: pending
  to_status: in_progress
  summary: 开始执行人工操作：打开配置页创建/停用区域

- timestamp: “2026-06-30T10:08:00+08:00”
  event_type: test_completed
  item_id: MANUAL-OP-001
  from_status: in_progress
  to_status: verified_by_user_report
  summary: 用户确认区域列表和停用状态正常
```

`event_type` 取值：

- `test_started`
- `test_completed`
- `test_blocked`
- `test_failed`
- `test_interrupted`
- `test_resumed`
- `test_deferred`
- `evidence_added`
- `evidence_reused`
- `dependency_changed`
- `environment_switched`
- `deployment_revision_reconciliation_started`
- `deployment_revision_reconciliation_completed`
- `deployment_revision_reconciliation_blocked`
- `release_handoff_generated`
- `release_handoff_invalidated`
- `writeback_success`
- `writeback_failed`
- `progression_gate_passed`
- `progression_gate_failed`

## test-evidence-index.md 格式

只维护证据索引和证据来源，不承担最终判断。必须能关联到具体 `item_id`。

```yaml
EVIDENCE-001:
  item_id: TEST-001
  evidence_type: long_automation
  source: long_readiness_receipt
  path: long-readiness-receipt.json
  content_sha256: <该文件实际内容的 sha256:...>
  target_environment: local
  revision_kind: git_commit
  revision: <Long Handoff 中的精确 revision>
  deployment_identity_ref: not_applicable
  component_revision_refs: []
  flow_refs: []
  description: long 自动化通过截图和断言
  added_at: “2026-06-30T10:00:00+08:00”
  valid: true
  invalidated_by: null

EVIDENCE-002:
  item_id: MANUAL-OP-001
  evidence_type: screenshot
  source: user
  path: manual-evidence/MANUAL-OP-001-screenshot.png
  content_sha256: <该文件实际内容的 sha256:...>
  target_environment: local
  revision_kind: <git_commit | git_worktree_snapshot | build_id | workspace_snapshot>
  revision: <当前本地代码与公开配置状态的精确标识>
  deployment_identity_ref: not_applicable
  component_revision_refs: []
  flow_refs: []
  description: 区域列表页面截图
  added_at: “2026-06-30T10:07:00+08:00”
  valid: true
  invalidated_by: null

EVIDENCE-003:
  item_id: MANUAL-OP-001
  evidence_type: user_report
  source: user
  path: manual-evidence/MANUAL-OP-001-user-feedback.md
  content_sha256: <该文件实际内容的 sha256:...>
  target_environment: local
  revision_kind: <git_commit | git_worktree_snapshot | build_id | workspace_snapshot>
  revision: <当前本地代码与公开配置状态的精确标识>
  deployment_identity_ref: not_applicable
  component_revision_refs: []
  flow_refs: []
  description: 用户自然语言反馈
  added_at: “2026-06-30T10:08:00+08:00”
  valid: true
  invalidated_by: null
```

证据索引规则：

- 每项必须填写 `content_sha256`、`target_environment`、`revision_kind`、`revision`、`deployment_identity_ref`、`component_revision_refs`、`flow_refs`、`valid` 和 `invalidated_by`；不适用字段显式写 `not_applicable` 或空数组。校验器重算持久文件摘要，不匹配即证据失效。
- 本地证据必须绑定可重建的代码与公开配置状态。Git 工作区干净时可用 `git_commit`；存在未提交改动时必须使用覆盖相关文件的 `git_worktree_snapshot`，不得只写 HEAD；非 Git 项目使用项目 build ID 或 `workspace_snapshot`。快照不得读取、包含或散列秘密值，优先复用 Long Handoff 已记录的代码/配置证据标识。
- Testing 未修改业务代码时，本地 required FLOW 证据的 `revision` 必须精确等于 Long readiness receipt 的 `repository_revision`；存在业务代码变化时先回 Long/Planning 形成新 receipt，不在 Testing 自造 revision。
- `path` 必须解析到 Testing Runtime 内真实、非空的持久化证据文件。外部平台链接、用户反馈或 CI 记录先写入脱敏本地证据记录，再引用该文件；仅填路径字符串不构成闭环。
- cloud-required 证据必须通过 `deployment_identity_ref` 引用 `test-runtime-state.md#current_deployment_revision`，其目标环境、revision kind、revision 和 `runtime_configuration_identity` 与当前完整部署身份一致；`component_set` 还必须列出该 FLOW 实际经过的组件 revision refs。CI/CD 证据只有针对同一完整部署身份时才可继承。
- 当前部署身份改变时，必须执行下文唯一的 Deployment Revision Reconciliation Gate；不得在其他文件另写切换顺序，或只改当前 revision 而保留旧 cloud-required 关闭关系。
- 本地证据和云端 `not_applicable` 项不会仅因部署身份改变而失效；Planning/Long 合同变化仍按实际影响精确失效。

## Deployment Revision Reconciliation Gate

本 Gate 是同一 Testing Runtime 内部署身份切换、证据失效、矩阵重算、Release Handoff 失效与中断恢复的唯一事务规则；其他文件只触发或引用本 Gate，不复制顺序。完整身份比较必须同时覆盖目标环境、部署/组件 revision 和 `runtime_configuration_identity`；候选身份与 `current_deployment_revision` 完全一致时不创建事务。

唯一持久化顺序：

1. **收敛当前项**：先完成当前测试项回写；若存在 `in_progress`，将其持久化为 `interrupted_pending_reconcile`。存在无法收敛的写入失败时停止，不得切换部署身份。
2. **写事务意图**：保持旧 `current_deployment_revision` 不变，将 `deployment_revision_reconciliation` 写为 `in_progress`，生成唯一 `transition_id`，完整记录与正式部署身份 schema 相同的 `from_identity` 和已核实 `candidate_identity`；同时将 `overall_status` 置为 `blocked`、`next_executable_item` 置空，并追加 `deployment_revision_reconciliation_started`。该检查点成功前不得失效证据。
3. **失效旧关闭关系**：把所有旧部署身份的 cloud-required 证据标记 `valid: false`，`invalidated_by` 指向 `transition_id`；从业务旅程矩阵移除对应 result refs，为每条 required FLOW 写入待复验 gap，并把实际变更引用分别记录到 `invalidated_evidence_refs`、`removed_result_refs`、`opened_gap_refs`。若 `active_release_handoff.status: current`，同时把 `release-handoff.md.snapshot_status` 与 `active_release_handoff.status` 写为 `invalidated`，两处 `invalidated_by` 均指向同一 `transition_id`，并记录 `invalidated_release_handoff_ref`。快照冻结载荷、历史证据与事件保留，旧结果不再作为当前关闭来源，也不得改写成当前通过。
4. **验证中间状态**：确认旧 cloud-required 证据已全部失效、旧 result refs 已全部移除、覆盖汇总为 `not_verified`；不存在 `active_release_handoff.status: current`，已有 `release-handoff.md` 时其 `snapshot_status` 必须为 `invalidated` 且 `invalidated_by` 与事务一致。任一检查失败时把事务写为 `blocked`，追加 `deployment_revision_reconciliation_blocked` 并停止。
5. **提交新身份**：只有第 4 步全部通过后，才在一次持久化写入中把 `current_deployment_revision` 替换为 `candidate_identity`，把事务写为 `completed` 并记录 `completed_at`，追加 `deployment_revision_reconciliation_completed`。随后把受影响 required 项的当前状态置为 `pending`，但此时不递增 `attempt`；只有真实开始复验时才按统一 attempt 规则递增。重新计算依赖与 `next_executable_item`，满足正常门禁后才解除 `overall_status: blocked`。

恢复规则：

- 会话恢复时若事务为 `in_progress | blocked`，必须从该事务检查点继续第 3–5 步；不得根据当前 revision、对话记忆或部分失效结果猜测事务已完成。
- `current_deployment_revision` 与已完成事务的 `candidate_identity` 不一致、失效引用数量无法对账、Release Handoff 失效引用无法对账，或事务完成事件缺失时，保持阻断并修复 Runtime 一致性。
- 同一目标环境重新部署也必须运行本 Gate；环境切换 Gate 不能替代部署身份事务。切换目标环境时两者都必须通过。

## release-handoff.md 格式

仅在完整上线进入 Release Handoff Mode 时生成：

```yaml
handoff_type: release_prerequisite_snapshot
snapshot_id:
snapshot_digest: <由校验脚本计算的 sha256:...>
snapshot_status: <current | invalidated>
generated_at:
invalidated_by: null
invalidated_at: null
current_test_epoch:
planning_handoff_ref:
planning_baseline_revision:
active_change_revision: <incremental revision; initial Handoff omits this key>
testing_runtime_ref:
long_testing_handoff_ref:
required_validation_gate_ref:
business_journey_matrix_ref:
business_journey_matrix_revision:
current_deployment_revision_ref: test-runtime-state.md#current_deployment_revision
deployment_identity_snapshot:
  status: <known | not_applicable>
  target_environment:
  identity_mode:
  revision_kind:
  revision:
  identity_digest:
  evidence_ref:
  component_revisions: []
  runtime_configuration_identity:
    status: <known | not_applicable>
    revision_kind:
    revision:
    evidence_ref:
    secret_values_included: false
business_journey_coverage_status: <verified | not_verified>
release_readiness_status: <ready | blocked>
required_result_refs: []
open_finding_refs: []
dependencies:
  - dependency_ref: <before_release DEP-ID 引用>
    planning_snapshot_status: <12 中 Planning 截止状态>
    testing_result_ref: <test-validation-results.md 中 environment_prerequisite 项>
    evidence_refs: []
    owner: <来自 DEP>
    blocking_scope: <来自 DEP>
    release_gate_owner: <项目发布/安全流程或责任主体>
unresolved_dependency_refs: []
```

规则：

- `snapshot_id` 必须唯一；`snapshot_status: current` 时，`test-runtime-state.md.active_release_handoff` 必须以同一 ID、路径、`snapshot_digest` 和完整部署身份摘要指向本文件。先运行 `--print-release-snapshot-digest` 获取冻结载荷摘要并同步写入快照与 active pointer；校验器会重算。只有 `snapshot_status: current` 且冻结载荷与当前 Testing Runtime 完全一致时，下游才可把它解释为当前移交。
- `deployment_identity_snapshot` 是生成时冻结的完整值，不是对可变指针的替代名称；它必须与当时 `current_deployment_revision` 完全一致并包含 `runtime_configuration_identity`。`current_deployment_revision_ref` 只用于回查来源，不能让旧快照自动继承后续部署身份。
- `planning_baseline_revision`、可选 `active_change_revision`、Long Handoff、Required Validation Gate、业务旅程矩阵 revision、`required_result_refs` 和 `open_finding_refs` 共同冻结本次测试结论。任一来源变化时必须通过对应失效流程把快照标为 `invalidated`，不得原地改写冻结载荷使旧结论看似仍然成立。
- `dependencies` 必须与 Planning Handoff `before_release_dependency_refs` 精确对账，并解析每个 `testing_result_ref` 和有效 evidence；`unresolved_dependency_refs` 必须等于机器计算出的未解除集合。集合为空时 `release_readiness_status: ready`，否则只能为 `blocked`；当前快照不等于发布通过。
- 每个 `before_release_dependency_refs` 都必须唯一出现；`testing_result_ref` 是 Testing 截止时的正式状态来源，Handoff 不复制新的状态枚举。
- `unresolved_dependency_refs` 必须包含 Testing 结果不是 `verified | verified_by_user_report`、证据失效、结果缺失或引用无法解析的全部项；也就是 `pending | in_progress | reused_from_long | failed | blocked | blocked_by_dependency | evidence_insufficient | interrupted_pending_reconcile | deferred | deferred_to_p2` 均不得遗漏。存在任何 unresolved 项时只能移交，不能输出发布通过。
- `snapshot_status`、`invalidated_by` 和 `invalidated_at` 是唯一允许在失效事务中更新的快照封套字段；其余冻结载荷不得修改。生成后由 `release_gate_owner` 在项目发布/安全流程中维护实际状态；不得反向修改 Planning 12，也不得把本快照当作发布后的持续状态源。
- 当前快照生成后，只要 Planning/Long revision、Required Validation Gate、业务旅程矩阵、required result、证据有效性、finding 或 DEP 结果发生变化，必须先把快照封套和 `active_release_handoff` 同时标为 `invalidated`，写入同一 `invalidated_by`，追加 `release_handoff_invalidated`，再更新其他当前状态。重新闭环后生成新的 `snapshot_id`；禁止复用旧 ID 或只更新可变指针。

## 回写时机

### 不可省略的回写时机

以下每个时机都必须完成持久化写入，校验成功后方可继续：

1. **每个测试项开始前**：在 `test-validation-results.md` 写入前置检查点（`status: in_progress`），更新 `test-runtime-state.md`，追加 `test-execution-events.md`；全部校验成功后方可执行或引导该测试项。
2. **每个测试项状态变化后**：状态从 `in_progress` 变为任何终态时，立即写入完成检查点。
3. **每个测试项结束后**：更新 `test-evidence-index.md`（或记录缺失原因），写入 `test-validation-results.md` 的最终 `status`、`evidence_refs`、`result_summary` 等，更新 `test-runtime-state.md` 游标，追加 `test-execution-events.md`。
4. **每次证据新增、复用、失效或不足后**：更新 `test-evidence-index.md` 和 `test-validation-results.md` 中对应项的 `evidence_refs`。
5. **每次依赖状态变化后**：重新计算 `test-validation-results.md` 中受影响项的可执行性，更新 `test-runtime-state.md` 的 `next_executable_item`。`test-execution-order.md` 不记录状态，无需因状态变化回写。
6. **每次部署身份变化时**：完整执行 Deployment Revision Reconciliation Gate；事务为 `in_progress | blocked` 时禁止推进。
7. **每次 Release Handoff 来源变化时**：先执行快照失效规则；当前快照未完成失效写回前禁止更新覆盖结论或生成新快照。
8. **每次中断恢复判断后**：写入恢复结果和 `interrupted_pending_reconcile` 或终态；同时恢复未完成的部署身份事务，并核对 `intake_binding` 与 `active_release_handoff`。
9. **每次选择下一条测试项前**：校验 Test Progression Gate，更新 `test-runtime-state.md` 的 `current_item`。
10. **最终报告前**：确保所有测试项的 `writeback_status = updated`，部署身份事务不为 `in_progress | blocked`，`business-journey-test-matrix.md` 已根据当前 revision 和结果重新计算，required FLOW 无未闭合 coverage gap 或 finding；存在 Release Handoff 时，其封套、冻结载荷和 `active_release_handoff` 必须一致。

### 禁止替代方案

以下情况不得视为回写完成：

- 只在自然语言回复中声明”已记录””已通过”。
- 只在对话中更新内部状态，不写入 Runtime 文档。
- “阶段结束时统一回写”替代逐项回写。
- 临时记忆、上下文推断或后续补充。

## 回写失败处理

### 情况 A：仍可持久化最小错误记录

若 `test-validation-results.md` 或 `test-runtime-state.md` 仍可写入：

1. 将当前项记录为 `writeback_status: blocked`。
2. 在 `test-runtime-state.md` 中记录 `overall_status: blocked`。
3. 向用户报告 Runtime writeback blocker。
4. 不得以口头总结、临时记忆或”之后补写”继续推进。
5. 最终结论必须为 `Blocked`。

### 情况 B：完全无法持久化

若连最小错误记录也无法写入文件：

1. 不得声称”已经将该项标记为 blocked”——该标记本身也无法持久化。
2. 不得伪造任何已写回状态。
3. 只能向用户报告 `runtime_writeback_unpersisted`。
4. 立即停止推进。
5. 下次恢复时，必须依据最后成功持久化的检查点处理。
6. 当前项若缺少可靠完成检查点，必须进入 `interrupted_pending_reconcile`。

## Testing Runtime Deterministic Gate

以下时机必须运行，不得用人工目视或自然语言总结替代：

```bash
bash <testing-skill-path>/scripts/validate-testing-runtime.sh <phase_testing_runtime_directory>
bash <testing-skill-path>/scripts/validate-testing-runtime.sh <phase_testing_runtime_directory> --expect-final
```

PowerShell 使用 `validate-testing-runtime.ps1` 和相同参数；无法使用包装器时才直接调用 `validate_testing_runtime.py`。

跨阶段只使用以下粗粒度前向迁移；单条命令、截图和人工动作不拆成 workflow stage。状态机不改变原有单项持久化和 Test Progression Gate：同一自动化测试项内部允许测试运行器安全并行，独立测试项之间不得因“可并行”跳过逐项检查点、证据和回写：

```bash
bash <testing-skill-path>/scripts/validate-testing-runtime.sh <runtime> --advance-workflow intake
bash <testing-skill-path>/scripts/validate-testing-runtime.sh <runtime> --advance-workflow local_testing
bash <testing-skill-path>/scripts/validate-testing-runtime.sh <runtime> --advance-workflow cloud_testing
bash <testing-skill-path>/scripts/validate-testing-runtime.sh <runtime> --advance-workflow release_handoff
```

本期无部署目标时停留在 `local_testing` 并可完成非发布测试报告；需要 Release Handoff 时允许 `local_testing -> release_handoff`。部署身份变化时先完成 Deployment Revision Reconciliation，再以 `--cycle-kind deployment_revision --new-cycle` 从 `release_handoff` 或当前 `cloud_testing` 开启递增 cycle；脚本把完整 deployment identity digest 写入 hash-chained event，直接改当前身份无法通过。已形成 Release Handoff 后需要本地复测时，必须先按失效规则把旧快照标记为 `invalidated`，再以 `--cycle-kind retest --new-cycle` 前向进入 `local_testing`，随后按适用范围进入 cloud/release，不倒拨旧 cycle。blocker 停留当前 stage；禁止回退、跳级、覆盖 history 或直接改 `testing-workflow-state.json`。`test-runtime-state.md.current_phase` 仍保留既有细分阶段，由校验器映射到上述粗粒度 stage，不改变原测试模式。

- 默认模式用于 Test Intake/恢复完成后、进入任何 cloud-required 测试前、Deployment Revision Reconciliation 完成或阻断后，以及 Release Handoff 失效后的运行时身份与事务校验。
- `--expect-final` 用于最终报告前，以及生成当前有效 Release Handoff 前与生成后；除基础校验外，还必须从 Planning FLOW/TEST 重新派生当前业务旅程范围，对账覆盖汇总、完整结果与 revision-bound evidence、云端完整部署身份、Release DEP 和 finding。`active_release_handoff.status: current` 时校验器自动执行同等最终闭环检查，即使调用方漏传参数也不放行。

校验失败时保持 `overall_status: blocked`，记录具体错误并修复当前 Runtime；不得修改 Planning/Long 来源文件来迎合校验，也不得跳过失败后继续。

校验器退出码 0 只表示 Runtime 合同内部一致，并同时输出 `release readiness: ready | blocked | not_generated | invalidated`；只有 `ready` 才能作为发布前置条件已闭环的证据，仍不等于项目发布/安全流程已经批准上线。

## Test Progression Gate

推进到下一条测试项前，当前项必须同时满足以下基础条件：

```text
不是 in_progress；
不是 interrupted_pending_reconcile；
writeback_status = updated；
依赖关系已重新计算；
下一项不是 blocked_by_dependency。
```

基础条件满足后，按当前项正式状态分别校验：

**`reused_from_long` / `verified` / `verified_by_user_report`**

- 必须存在有效 `evidence_refs`。
- `test-evidence-index.md` 必须存在对应有效证据。

**`evidence_insufficient`**

- 必须填写 `evidence_missing_reason`。
- 若已有证据，必须填写 `evidence_refs`。

**`failed` / `blocked` / `blocked_by_dependency` / `deferred` / `deferred_to_p2`**

- 必须填写 `blocker_or_failure_reason`。
- 不强制要求证据索引。

**`pending` / `in_progress` / `interrupted_pending_reconcile`**

- 禁止推进。

任一条件不满足时，不得推进。若条件不满足：

1. 报告具体不满足的条件。
2. 不得以口头总结替代回写。
3. 在 `test-execution-events.md` 中记录 `progression_gate_failed` 事件。
4. 在 `test-runtime-state.md` 中更新 `overall_status: blocked`。

## 禁止项

- 禁止只在对话中报告，不写 Runtime 文档。
- 禁止把测试结果写回规划 SoT。
- 禁止把截图或日志当成唯一通过证据。
- 禁止 append 巨长日志。
- 禁止多个文件重复定义同一测试状态。
- 禁止在 `business-journey-test-matrix.md` 复制测试项正式状态或另建第二套通过结论。
- 禁止重新执行 long 已通过且证据完整的自动化测试。
- 禁止把同一 operation_signature 拆成多个重复人工测试操作。
- 禁止因不同 case_id 而要求用户重复已经验证过的完整操作流程。
- 禁止人工测试引导只写测试任务名称，不写具体操作步骤。
- 禁止完成一个人工测试后，在仍存在可执行下一项时不主动引导。
- 禁止在 `manual-test-queue.md` 中生成无法判断依赖状态的人工操作项。
- 禁止当前项 `writeback_status != updated` 时推进到下一项。
- 禁止 `in_progress` 项没有前置检查点记录时执行或引导。
- 禁止 `interrupted_pending_reconcile` 项未恢复确认时跳过。

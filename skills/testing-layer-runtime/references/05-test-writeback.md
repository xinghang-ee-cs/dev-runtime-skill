# Test Writeback

## 回写目标目录

`<phase_testing_runtime_directory>/`

`<phase_testing_runtime_directory>` 必须由当前 Planning/Long Handoff、项目期次目录约定和既有 Runtime 事实解析为唯一 `writeback_target`，不是固定目录名。

Testing Runtime 只写本期 Runtime 输出目录；不得修改 planning SoT 或业务产物。本期测试状态、事件、证据、队列、依赖、Change Triage 与恢复数据不得写入项目根目录 `.runtime/`；根 `.runtime/` 只允许该 Skill 明确定义的跨期项目级环境索引或稳定配置。

## 必须维护的文件

- `test-runtime-state.md`：当前阶段、当前环境、总状态、阻塞项、最后更新时间。
- `test-execution-events.md`：测试阶段事件，不写长日志。
- `test-validation-results.md`：每个测试项（`case_id`、`MANUAL-OP`、真实设备验证项、服务器验证项）的最终执行状态唯一事实源。
- `test-evidence-index.md`：证据路径、截图路径、命令摘要、人工证据来源、long evidence 来源。
- `manual-test-queue.md`：待人工执行、待补证据、已确认/未确认的人工测试操作；不是 case 清单，而是用户实际操作队列。同一用户操作只能出现一次；多个 case 可以挂载到同一个操作项下。
- `test-execution-order.md`：测试顺序、依赖、阻塞关系。
- `change-triage.md`：测试发现的分类、影响范围、当前合同是否仍有效和下游 disposition；不替代 Planning Change Set 或业务 SoT。

## Long Testing Handoff 回写

读取 `testing-handoff.md` 或 `long-runtime-testing-summary.md` 后，必须记录：

```yaml
long_testing_handoff:
  source:
  verified:
  planning_baseline_revision:
  active_change_revision: # 初始 Handoff 省略
  executed_task_contract_revisions: []
  automated_passed:
  automated_failed:
  automated_skipped:
  manual_required:
  coverage:
```

每一个继承的自动化 case 必须写入 `test-validation-results.md`，使用完整字段集：

```yaml
item_id:
item_type: case
attempt:
environment:
status: reused_from_long
started_at:
completed_at:
depends_on_check:
expected_evidence:
result_summary:
evidence_refs:
evidence_missing_reason: null
blocker_or_failure_reason: null
covers: []
covered_by: []
evidence_reuse: false
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

## test-validation-results.md 格式

每个测试项必须拥有独立记录。这是每个测试项完整生命周期的唯一事实源。

```yaml
TEST-001:
  item_id: TEST-001
  item_type: case
  attempt: 1
  environment: local
  status: reused_from_long
  started_at: “2026-06-30T10:00:00+08:00”
  completed_at: “2026-06-30T10:00:30+08:00”
  depends_on_check: passed
  expected_evidence: long evidence
  result_summary: 继承 long 自动化结果，所有断言通过
  evidence_refs:
    - long-runtime-testing-summary.md#automated_passed.TEST-001
  evidence_missing_reason: null
  blocker_or_failure_reason: null
  covers: []
  covered_by: []
  evidence_reuse: false
  writeback_status: updated

MANUAL-OP-001:
  item_id: MANUAL-OP-001
  item_type: manual_op
  attempt: 1
  environment: local
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
```

字段说明：

- `item_id`：测试项唯一标识。
- `item_type`：`case` / `manual_op` / `real_device` / `server_verification`。
- `attempt`：第几次尝试；仅在实际重新执行时递增，恢复判断和修复游标不递增。
- `status`：测试项生命周期的唯一正式状态字段，使用完整状态枚举（见 `01-test-runtime-core.md` 状态枚举）。不得使用 `final_status`。
- `started_at`：本次执行开始时间。
- `completed_at`：本次执行完成时间；`in_progress` 项可为空。
- `depends_on_check`：依赖检查结果；`passed` / `failed` / `pending`。
- `expected_evidence`：预期证据类型描述。
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
current_phase: manual_testing
current_environment: local
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

- `current_item`：当前正在执行的测试项 ID。
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
  source: long-runtime-testing-summary.md
  path: testing-handoff.md
  description: long 自动化通过截图和断言
  added_at: “2026-06-30T10:00:00+08:00”
  valid: true

EVIDENCE-002:
  item_id: MANUAL-OP-001
  evidence_type: screenshot
  source: user
  path: manual-evidence/MANUAL-OP-001-screenshot.png
  description: 区域列表页面截图
  added_at: “2026-06-30T10:07:00+08:00”
  valid: true

EVIDENCE-003:
  item_id: MANUAL-OP-001
  evidence_type: user_report
  source: user
  path: manual-evidence/MANUAL-OP-001-user-feedback.md
  description: 用户自然语言反馈
  added_at: “2026-06-30T10:08:00+08:00”
  valid: true
```

## 回写时机

### 不可省略的回写时机

以下每个时机都必须完成持久化写入，校验成功后方可继续：

1. **每个测试项开始前**：在 `test-validation-results.md` 写入前置检查点（`status: in_progress`），更新 `test-runtime-state.md`，追加 `test-execution-events.md`；全部校验成功后方可执行或引导该测试项。
2. **每个测试项状态变化后**：状态从 `in_progress` 变为任何终态时，立即写入完成检查点。
3. **每个测试项结束后**：更新 `test-evidence-index.md`（或记录缺失原因），写入 `test-validation-results.md` 的最终 `status`、`evidence_refs`、`result_summary` 等，更新 `test-runtime-state.md` 游标，追加 `test-execution-events.md`。
4. **每次证据新增、复用、失效或不足后**：更新 `test-evidence-index.md` 和 `test-validation-results.md` 中对应项的 `evidence_refs`。
5. **每次依赖状态变化后**：重新计算 `test-validation-results.md` 中受影响项的可执行性，更新 `test-runtime-state.md` 的 `next_executable_item`。`test-execution-order.md` 不记录状态，无需因状态变化回写。
6. **每次中断恢复判断后**：写入恢复结果和 `interrupted_pending_reconcile` 或终态。
7. **每次选择下一条测试项前**：校验 Test Progression Gate，更新 `test-runtime-state.md` 的 `current_item`。
8. **最终报告前**：确保所有测试项的 `writeback_status = updated`。

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
- 禁止重新执行 long 已通过且证据完整的自动化测试。
- 禁止把同一 operation_signature 拆成多个重复人工测试操作。
- 禁止因不同 case_id 而要求用户重复已经验证过的完整操作流程。
- 禁止人工测试引导只写测试任务名称，不写具体操作步骤。
- 禁止完成一个人工测试后，在仍存在可执行下一项时不主动引导。
- 禁止在 `manual-test-queue.md` 中生成无法判断依赖状态的人工操作项。
- 禁止当前项 `writeback_status != updated` 时推进到下一项。
- 禁止 `in_progress` 项没有前置检查点记录时执行或引导。
- 禁止 `interrupted_pending_reconcile` 项未恢复确认时跳过。

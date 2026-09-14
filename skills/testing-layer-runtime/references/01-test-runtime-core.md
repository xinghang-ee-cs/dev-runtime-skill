# Test Runtime Core

## 目录

- 核心目标、边界与输入
- Long Handoff 与自动化结果复用
- Test Intake、Planning 与业务旅程覆盖
- 环境前置与 Change Triage
- 人工操作去重与引导
- 单一事实源、执行规则与停止条件
- Per-Test Durable Writeback
- 状态、attempt 与单项持久化顺序

## 核心目标

Testing Runtime 的目标是管理测试生命周期：

- 测试规划
- 自动化结果继承
- 人工测试
- 真实设备测试
- 云端验证
- 外部能力验证
- 验收管理
- Release Handoff

它不负责重新执行 long 已经完成并通过的自动化测试。

## Skill 边界

`planning-layer-runtime`：

- 负责冻结开发开始前的规划合同，并在 Execution/Test Change Triage 要求时受控重入。
- 负责需求、范围、数据模型、权限模型、UI、验收标准、风险、P0/P1/P2。
- 可产出 Planning Handoff 指定的 Test and Acceptance Plan，但只定义“测什么”。
- 禁止定义“怎么测、谁来测、测试顺序、测试执行状态、测试结果”。

`long-task-orchestrator`：

- 截止到 `ready_for_local_test`。
- 负责开发、重构、数据迁移、自动化测试代码编写、单元测试、业务测试、自动化执行和自动化测试结果记录。
- `vitest`、`jest`、`integration`、`api-test`、`playwright` 默认属于 long。

`testing-layer-runtime`：

- 截止到 release handoff。
- 负责汇总自动化结果、人工测试、真实设备测试、云端验证、外部能力验证、最终验收和上线前验证移交。
- 禁止重新执行 long 已完成并已通过的自动化测试。

## 输入来源

按优先级读取：

1. Planning/Long Handoff 指定的 `testing-handoff.md`
2. Planning/Long Handoff 指定的 `long-runtime-testing-summary.md`
3. Planning Handoff 指定的 Test and Acceptance Plan 真实路径
4. 用户指定的用例 ID、功能范围、变更范围或验收目标

Test and Acceptance Plan 只用于识别测试范围，不得从中继承执行顺序、测试状态或测试结果；不得依赖固定编号或固定目录猜测路径。

## Long Testing Handoff

Testing Runtime 启动时必须优先读取 long 测试交接文件。Long Runtime 必须提供：

```yaml
runtime_epoch:
planning_handoff_ref:
planning_baseline_revision:
active_change_revision: # 初始 Handoff 省略
executed_task_contract_revisions: []
required_validation_gate:
automated_passed:
automated_failed:
automated_skipped:
manual_required:
coverage:
frontend_contract_validation_summary:
```

启动时必须确认 Long Testing Handoff 的 `runtime_epoch` 与 Long Runtime 一致、`planning_handoff_ref` 指向实际消费的唯一 Planning Handoff，其 `planning_baseline_revision`、可选 `active_change_revision` 与该 Handoff 一致，并确认 `executed_task_contract_revisions` 只来自 `execute_only`、`resume_only` 或 `reexecute_affected_part`。epoch、引用或 revision 缺失、冲突、过期，或任务集合包含 `context_only`、`completed_locked`、`cancelled` 时，Test Intake Gate 不得通过。

字段含义：

| 字段 | testing 处理 |
| --- | --- |
| `runtime_epoch` | 必须与 Long Runtime 事实一致，并回写到 `intake_binding.long_runtime_epoch` |
| `planning_handoff_ref` | 必须指向 Long 实际消费且 Testing 本次核对的 Planning Handoff |
| `required_validation_gate` | 必须核对 `result: passed`、当前 matrix revision 与 effective validation ids；缺失、blocked、stale 或证据不可解析时 Test Intake Gate 阻断 |
| `automated_passed` | 继承为 `reused_from_long` |
| `automated_failed` | 对应自动化 case 的 `status: failed`，依赖该项的后续测试标记为 `blocked_by_dependency`；不得用人工测试覆盖 |
| `automated_skipped` | 判断是否需要人工、服务器或用户确认 |
| `manual_required` | 进入人工/真实设备/外部能力队列 |
| `coverage` | 用于识别未覆盖范围，不作为通过证明 |
| `frontend_contract_validation_summary` | UI/UX 适用时核对实际消费的设计文档、Manifest、PAGE/UX-SCN/ASSET revision；继承自动化证据，只将精确的未自动化项加入人工队列 |

缺失 handoff 或字段不完整时：

- 进入 Test Intake Mode。
- 报告 `long_testing_handoff_missing` 或 `long_testing_handoff_incomplete`。
- 不得通过重复执行自动化测试来替代 long handoff。
- 不得以 Testing 人工操作、云端 smoke 或重新运行部分测试补偿 `required_validation_gate` 未通过。

## Automated Result Reuse Rule

若同时满足：

- automated status = pass
- evidence exists
- long handoff verified

则：

- 每个继承的自动化 case 必须在 `test-validation-results.md` 中独立写入：

```yaml
status: reused_from_long
source_validation_id: <Long required_validation_gate.effective_validation_ids 中的唯一 ID>
evidence_refs:
  - <指向 long-readiness-receipt.json 的 Testing evidence id>
evidence_reuse: true
writeback_status: updated
```

- long testing handoff 只提供自动化来源事实和证据来源。
- `source_validation_id` 必须解析到 Long `automated_passed` 与 effective validation ids 的精确交集；证据索引必须绑定已冻结且摘要匹配的 Long readiness receipt，禁止只写 Handoff 标题锚点。
- 正式测试项状态只能写入 `test-validation-results.md`。
- 不得使用 `runtime result`、`evidence source` 作为独立结果字段。
- 禁止重新执行。

允许重新执行条件仅限：

- 用户明确要求。
- 环境发生变化。
- 自动化证据缺失。
- 自动化失败。
- 自动化结果过期。

重新执行必须记录 `rerun_reason`，并说明该行为是例外而不是 testing 默认职责。

## Test Intake Gate

在 Test Planning Phase 前，AI 必须在 Runtime 内部确认：

```text
current_test_epoch:
writeback_target:
planning_baseline_revision:
active_change_revision:
current_deployment_revision:
long_testing_handoff:
required_validation_gate:
planning_test_scope:
execution_prerequisite_readiness:
business_journey_scope:
frontend_experience_binding:
frontend_contract_validation_summary:
manual_required:
server_required:
release_required:
destructive_boundary:
evidence_requirements:
```

以上清单不得作为表单要求用户填写。缺少关键信息时，通过自然语言一次只追问一个当前阻塞事实。

## Test Planning Phase

Test Intake Gate 之后必须进入 Test Planning Phase。

输入：

- Planning Handoff 指定的 Test and Acceptance Plan
- Long Testing Handoff

输出：

- `business-journey-test-matrix.md`
- `test-execution-order.md`
- 自动化已完成
- 自动化失败
- 待人工验证
- 待服务器验证
- 待上线验证

规划规则：

- 从 planning 读取“测什么”。
- 从 long handoff 读取自动化事实。
- UI/UX 适用时从 Planning Handoff 读取精确设计合同与资产 revision，并与 Long `frontend_contract_validation_summary` 交叉校验；`unresolved_mismatch` 非空时阻断受影响测试。
- 对 `automated_passed` 直接写入 `reused_from_long`。
- 先按 Planning FLOW 生成业务旅程覆盖矩阵；每个适用 P0/P1 FLOW 都必须具有本地业务/E2E 证明要求。本期包含云端部署时，全部 P0 正向旅程以及部署敏感或受变更影响的 P1 FLOW 还必须具有云端业务/E2E 证明要求。
- 本地 required 证明优先映射 Long Handoff 的有效业务/E2E 证据；Long 应负责的本地 required 证据缺失时必须报告 coverage gap 并返回 Long，不得用人工、云端或单元测试补偿。
- 对 `manual_required` 建立人工测试卡。
- 对服务器和 release 事项只建立验证/移交项。
- 对 Planning Handoff 中每个 `before_cloud_test_dependency_refs` 和 `before_release_dependency_refs`，在 `test-validation-results.md` 建立引用同一 DEP-ID 的 `environment_prerequisite` 结果项；12 仍只是 Planning 截止快照，Testing 不回写 Planning SoT。
- 不生成脱离 Planning TEST 和合同 revision 的纯审美对照项；允许为 Long 明确移交且 Planning 已定义的视觉一致性、真机响应式、复杂 UX 或无障碍观察生成合同绑定人工项，但必须同时包含 PAGE/UX-SCN/ASSET revision、设备/视口、业务进入路径、操作、可见断言与通过条件。
- 不生成某一期的测试入口删除、测试快捷操作删除或测试专用接口删除测试项；这些只在最终上线门禁中移交。

## Business Journey Test Matrix And Coverage Gate

`<phase_testing_runtime_directory>/business-journey-test-matrix.md` 是本期业务旅程覆盖关系的唯一 Testing 实例。它从 Planning Test and Acceptance Plan 读取 FLOW/TEST 范围，从 Long Handoff 与 `test-validation-results.md` 读取证据引用；不重新定义业务规则，也不保存测试项正式状态。

它与 Long 的 `required_validation_matrix` 职责不同：Long Matrix 定义并门禁开发期自动化验证；本矩阵只按 FLOW 汇总 Long 结果与 Testing 后续人工、真机和部署后云端证据，不复制 Long 的命令、后置条件或正式结果状态。

唯一字段格式见 `05-test-writeback.md#business-journey-test-matrixmd-格式`；本文件只定义覆盖与完成规则，不复制 schema。

规则：

- 每个适用 P0/P1 FLOW 必须唯一映射，不得因已有大量单元、组件、接口或页面测试而省略完整旅程。
- `local_business_e2e.result_refs` 和 `deployed_environment_e2e.result_refs` 只能引用 `test-validation-results.md` 的正式结果或其已索引 Long evidence；矩阵不得另写 `passed/failed` 形成第二个状态源。
- 成功旅程必须从已确认合法入口开始，经过关键业务动作，到达可观察终态。反向覆盖只包含 Planning 已定义且实际适用的非法跳步、权限拒绝、错误输入、依赖失败、重试/恢复、幂等或旧流程隔离分支。
- 单元测试、组件测试、接口片段、构建/类型检查、截图和服务器 smoke 只能作为辅助证据，不能独立关闭 FLOW 的业务/E2E requirement。
- 本期包含云端部署时，每个 P0 FLOW 的正向旅程都要求云端 E2E；P1 仅在部署差异可能改变结果或受当前变更影响时要求，例如反向代理、域名/CORS、秘密注入、云数据库/对象存储、跨服务网络、真实回调、云端权限或外部能力。其余 P1 或本期无部署目标时明确 `not_applicable` 和原因，不得机械重跑。
- Matrix revision、Planning/Long revision 或受影响合同变化时，只失效真实命中的 journey/result refs，未受影响证据保持有效。部署身份变化是例外，必须完整执行 `05-test-writeback.md#deployment-revision-reconciliation-gate`；本文件不复制切换顺序。
- 部署身份比较必须覆盖目标环境、组件/部署 revision 与脱敏 `runtime_configuration_identity`；同一代码或镜像在公开配置、路由/代理、域名/CORS、基础设施绑定或秘密版本绑定变化后属于新部署身份，旧 cloud-required 证据不得沿用。

Business Journey Coverage Gate 只有同时满足以下条件才通过：

```text
every in-scope P0/P1 FLOW mapped exactly once
+ every required local business/E2E journey has valid evidence
+ when deployment is in scope, every P0 success journey and every deployment-sensitive or change-affected P1 journey has evidence for the exact deployed revision
+ all contract-defined required negative branches have valid evidence
+ no required coverage gap is failed, blocked, missing, evidence_insufficient, or backed by stale/invalid/revision-mismatched evidence
+ no unresolved finding affects a required journey
```

本 Gate 未通过时，Testing 最终结果不得为通过，也不得进入 release-ready handoff。

## Environment Prerequisite Result Lifecycle

Planning Handoff 中的 `before_cloud_test_dependency_refs` 与 `before_release_dependency_refs` 只是 DEP 引用和 Planning 截止快照，不代表 Testing 时已经就绪。Testing 必须按 `05-test-writeback.md#test-validation-resultsmd-格式` 为每个 DEP 创建唯一 `item_type: environment_prerequisite` 结果项：

- 初始为 `pending`；开始安全核验前写 `in_progress` 检查点。
- 工具通过不显示秘密值的探针核验时为 `verified`；工具不能安全读取但用户明确说明已在批准渠道完成时为 `verified_by_user_report`。
- 探针已实际执行但前提不满足时写 `failed`；无法开始写 `blocked`；已有信息不足以判断写 `evidence_insufficient`。不得把 Planning 的 `ready_verified` 等 DEP 状态值复制成 Testing `status`。
- 未就绪时只阻断 `blocking_scope` 命中的 FLOW/环境；其他本地结果和无关云端旅程继续有效。
- 需要用户操作时，一次只引导当前一个安全动作，说明业务用途、已核实的配置入口或责任主体、最短步骤、脱敏验证方式和完成后解锁范围；不得要求用户在聊天中发送秘密值、连接串、内网入口或生产数据。
- `before_release` 项可以在 Testing 中提前取得证据，但发布后的实际状态由 Release Handoff 指定的项目发布/安全流程拥有；Testing 不输出 release pass。

## Execution/Test Change Triage Gate

测试执行、人工反馈或证据核对出现偏差时，必须先形成 `change_decision`，再决定归属：

```yaml
change_decision:
  source_stage: testing
  finding_type:
  observed_result:
  expected_source:
  is_current_plan_still_valid:
  affected_ids: []
  planning_reentry_required:
  reentry_documents: []
  change_level:
  disposition:
```

| finding_type | 判定 | disposition |
| --- | --- | --- |
| `implementation_defect` | 当前 Planning 合同仍有效，实现结果偏离合同 | `fix_in_execution` |
| `test_defect` | 测试脚本、测试数据、环境、证据映射或 Testing Runtime 错误 | `fix_in_test` |
| `planning_gap` | 当前 Planning 缺少执行或验收所需合同 | `reopen_current_planning` |
| `requirement_change` | 用户接受的新需求、范围或验收变化 | `reopen_current_planning` |
| `design_drift` | 需要改变架构、API、数据、权限、状态、UI/体验或验收合同 | `reopen_current_planning` |
| `deferred_improvement` | 不改变本期当前有效合同的后续改善 | `defer_to_next_phase` 或 `reject_change` |

处理规则：

- `fix_in_execution`：写入 `<phase_testing_runtime_directory>/change-triage.md` 并形成 defect handoff，交由 long-task-orchestrator patch；Testing 不改业务代码。
- `fix_in_test`：只在 Testing 获准的测试资产和 Runtime 范围修正，按 attempt 与证据规则重测。
- `reopen_current_planning`：停止受影响测试，将 triage 证据交给 planning-layer-runtime；等待新的增量 Planning Handoff、Long 实现和 Long Testing Handoff。
- `defer_to_next_phase` / `reject_change`：记录确认依据和对当前验收的影响，不得静默忽略。
- 只失效 `affected_ids` 及依赖传播真实命中的测试；未受影响的测试、已完成证据和 Long 自动化继承结果保持有效，除非 revision 或依赖事实证明它们也受影响。
- `fix_in_execution` 恢复前必须读取 patch 后新的 Long Handoff，核对受影响 TASK revision、`required_validation_gate: passed` 和有效 evidence；随后更新业务旅程矩阵。需要云端证据的 FLOW 必须等待同一修复 revision 重新部署后复验。
- finding 只有在原观察结果不再复现、所有受影响断言已有新证据、依赖重新计算且业务旅程覆盖门禁重新通过后才能关闭；仅“代码已改”“Long 已完成”或“云端已重新部署”都不等于闭环。

## Manual Operation De-duplication Gate

在生成 `manual-test-queue.md` 前，Testing Runtime 必须先对人工测试候选项执行动作去重。

每个候选人工测试必须拆解为：

- `actor`：谁操作。
- `entry`：从哪个页面、入口或设备进入。
- `precondition`：执行前必须已经成立的状态。
- `operation`：用户实际要做的动作。
- `data_domain`：测试数据、正式数据、服务器数据或真实设备数据。
- `business_assertions`：该动作需要证明的业务断言。
- `evidence_need`：需要的截图、自然语言反馈、页面状态、接口状态或其他证据。

Testing Runtime 必须生成内部 `operation_signature`：

```text
actor + entry + precondition + operation + data_domain
```

规则：

- 相同 `operation_signature` 的人工测试不得生成多个独立用户操作。
- 一个 `operation_signature` 可以覆盖多个 `case_id` 和多个 `business_assertions`。
- 已验证过的 `operation_signature` 不得再次要求用户重复执行。
- 后续 case 若只缺少新的业务断言，只能复用已有证据并追问缺失观察点。
- 权限语义、错误语义、状态语义、图片边界和复用能力类 case，必须优先复用既有权限、申请、执行、图片、历史或配置证据。
- 若已有证据无法支撑新增断言，才允许创建补充人工测试；补充测试必须只验证缺失观察点，不得重复完整流程。

## test-execution-order.md

Test Planning Phase 必须生成：

```text
test-execution-order.md
```

职责：

- 管理测试顺序。
- 管理测试依赖。
- 管理阻塞关系。

格式：

```yaml
TEST-001:
  depends_on: []

TEST-002:
  depends_on:
    - TEST-001

TEST-003:
  depends_on:
    - TEST-002
```

执行规则：

- 只有 `depends_on` 全部通过，当前测试才能执行。
- 若前置失败，当前测试记录为 `blocked_by_dependency`，不得执行。
- `reused_from_long` 视为依赖已通过。
- `deferred` 不得作为当前依赖通过，除非用户明确把该范围移出当前验收边界。

## 单一事实源与文件职责

### test-validation-results.md

作为每个测试项最终执行状态的唯一事实源。每个 `case_id`、`MANUAL-OP`、真实设备验证项、部署后业务/E2E 验证项、服务器验证项都必须有独立记录。

至少包含：

```yaml
item_id:
item_type:
attempt:
environment:
status:
started_at:
completed_at:
depends_on_check:
expected_evidence:
result_summary:
evidence_refs:
evidence_missing_reason:
blocker_or_failure_reason:
covers:
covered_by:
evidence_reuse:
writeback_status:
```

规则：

- `status` 是测试项生命周期的唯一正式状态字段，不得使用 `final_status`。
- `evidence_refs` 是测试项证据的唯一正式字段，不得使用 `evidence`。
- `blocker_or_failure_reason` 是失败或阻塞原因的唯一正式字段，不得使用 `failure_or_blocker_reason`。
- `evidence_missing_reason` 在 `status` 为 `evidence_insufficient` 或证据不完整时必填。
- `test-validation-results.md` 不只是"最终结果文件"，而是"每个测试项完整生命周期的唯一事实源"，必须能记录 `in_progress`、中断和终态。
- `next_executable_item` 不得写入单项结果记录，只能写入 `test-runtime-state.md`。

### test-runtime-state.md

只负责 Runtime 游标和整体状态，不得承担每项完整结果。

完整唯一 schema 见 `05-test-writeback.md#test-runtime-statemd-格式`。本文件只约束职责：它必须持久化 `intake_binding`、当前完整部署身份、部署切换事务、当前 Release Handoff 指针、Runtime 游标和整体状态，不复制单项结果。`intake_binding` 缺失或与当前 Planning/Long Handoff、epoch、revision、Required Validation Gate 不一致时，Runtime 必须阻断。

若它与 `test-validation-results.md` 冲突，必须以 `test-validation-results.md` 为准，并立即修复 Runtime 游标。

### test-execution-events.md

只追加简短事件，不写长日志，不作为最终状态事实源。

事件至少记录：

```yaml
timestamp:
event_type:
item_id:
from_status:
to_status:
summary:
```

### test-evidence-index.md

只维护证据索引和证据来源，不承担最终判断。必须能关联到具体 `item_id`。

### manual-test-queue.md

只负责：

- 用户实际操作队列
- `operation_signature` 去重
- `depends_on`
- `blocked_by`
- `queue_state`
- 用户引导
- 覆盖关系
- 是否已被已有证据完整覆盖

`queue_state` 取值：`ready` / `waiting_dependency` / `blocked_by_environment` / `covered` / `awaiting_user_feedback` / `not_actionable`。

不得使用 `verified`、`verified_by_user_report`、`failed`、`blocked`、`reused_from_long`、`pending_manual`、`pending_server` 作为 `queue_state`。

不得在 `manual-test-queue.md` 中写任何 case 的最终结果。

## Manual Guidance Strategy

Manual Guidance Strategy 必须遵循 `references/03-evidence-format.md#manual-guidance-conversation-rule`。

原则：

- 用户负责操作系统并用自然语言反馈观察结果。
- AI 负责理解用户表达、提取测试结果、判断状态、结构化写回 Runtime、维护进度。
- 不得把 `case_id`、环境、证据类型、回写状态、`Pass`、`Fail`、`Unverified` 等内部字段交给用户填写。
- 一次只引导一个下一步操作。

## Guided Manual Operation Rule

Testing Runtime 必须优先使用 `manual-test-queue.md` 中 `MANUAL-OP` 的 `depends_on` 和 `blocked_by` 判断是否可执行。

可执行条件：

1. `manual-test-queue.md` 中该 MANUAL-OP 的 `queue_state = ready`。
2. `depends_on` 全部已通过、已完成、`reused_from_long`，或已被用户明确移出当前验收范围。
3. `blocked_by` 为空。
4. `covered_by_evidence = false`。
5. `test-validation-results.md` 中该 MANUAL-OP 不存在，或 `status = pending`。
6. 当前环境可执行。

禁止再次引导同一个 MANUAL-OP，当满足以下任一条件：

- `queue_state = awaiting_user_feedback`
- `queue_state = covered`
- `queue_state = waiting_dependency`
- `queue_state = blocked_by_environment`
- `queue_state = not_actionable`
- `test-validation-results.md` 中该 MANUAL-OP 的 `status = in_progress`
- `test-validation-results.md` 中该 MANUAL-OP 已是任意终态

队列状态迁移规则：

- 完成开始检查点并向用户发出操作引导：`queue_state = awaiting_user_feedback`
- MANUAL-OP 验证通过且证据闭环：`queue_state = covered`
- 依赖不满足：`queue_state = waiting_dependency`
- 环境不满足：`queue_state = blocked_by_environment`
- 无法继续、验证失败、已延期或无法补齐证据：`queue_state = not_actionable`

不得从 `manual-test-queue.md` 读取正式测试状态。`manual-test-queue.md` 只能使用 `queue_state`，不得出现正式 `status` 字段。

如果 `manual-test-queue.md` 缺失 `depends_on` 或 `blocked_by`，AI 必须回写补齐后再选择下一个人工操作，不得仅依赖跨文件推理。

用户态输出必须包含：

- 当前要测什么：用自然语言说明，不暴露内部 case 字段。
- 为什么要测：说明它要验证的业务结果。
- 操作前条件：用户需要处于哪个角色、账号、页面、数据状态。
- 具体操作步骤：用 2~6 个短步骤说明点击哪里、输入什么、提交什么、查看哪里。
- 需要观察什么：告诉用户重点看按钮、提示、列表、地图、图片、权限、状态或数据变化。
- 需要怎么反馈：允许自然语言、截图或简短反馈；不得要求用户按固定格式填写。
- 完成后的处理：AI 收到反馈后必须判断结果、回写 Runtime，并在无阻塞时主动给出下一个可执行操作。

禁止：

- 只输出 case_id 或测试标题。
- 一次要求用户执行多个独立测试操作。
- 让用户自己判断下一个该测什么。
- 让用户填写 Runtime 字段、状态枚举、Pass/Fail 表格或证据模板。

## 执行规则

- 先核验 Long `required_validation_gate`，再继承结果和生成业务旅程矩阵；Gate 缺失、blocked、stale 或证据不可解析时不得进入正式测试。
- 先继承 long 自动化结果，再决定人工/服务器/release 验证。
- 业务旅程覆盖优先于测试数量；每条适用 P0/P1 FLOW 的本地业务/E2E 证据必须先闭合，再进入需要部署后复验的云端 FLOW。
- 人工测试必须先做 operation_signature 去重，再进入 Manual Guidance Strategy。
- 已有证据可覆盖的 case，不得再次引导用户重复操作。
- 人工测试开始后，AI 必须主动选择并引导下一个可执行人工操作。
- 选择下一个人工测试操作时，必须优先读取 `MANUAL-OP.depends_on` 和 `MANUAL-OP.blocked_by`。
- 若人工操作依赖不清，必须先补齐 Runtime 回写，再引导用户操作。
- 用户完成一个人工操作并回写成功后，若存在下一个可执行人工操作，AI 必须继续给出下一步引导；不得只停留在”已记录”或”测试通过”。
- 若下一个操作被依赖、证据、环境、破坏性确认或服务器条件阻塞，AI 必须说明阻塞原因和当前只需要用户补充的一个事实。
- 不执行依赖未通过的测试。
- 自动化失败时报告阻塞，不用人工判断掩盖失败。
- 人工测试缺少截图或描述时，先按对话规则追问；最终仍无法形成证据时，在 Runtime 内部标记证据不足。
- 服务器部署状态未确认时，不进入 Server Verification Mode。
- release 测试请求必须切换到项目定义的发布/安全流程或可选 release/security skill。
- 测试发现回流 Long 或 Planning 后，必须等待新 Handoff，按合同影响精确失效本地证据并重算 `business-journey-test-matrix.md`；若产生新部署身份，只触发 `05-test-writeback.md#deployment-revision-reconciliation-gate`，不在本文件另建失效步骤。
- 每个测试项开始前，必须完成 Per-Test Durable Writeback Rule 的前置检查点回写；检查点写入成功后方可执行或引导该测试项。
- 每个测试项结束后，必须完成 Per-Test Durable Writeback Rule 的完成检查点回写；回写成功后方可推进到下一个测试项。
- 推进到下一个测试项前，必须通过 Test Progression Gate 的全部条件。
- 会话恢复、中断恢复时，必须执行 Runtime Resume/Recovery Rule；未恢复的 `interrupted_pending_reconcile` 项不得跳过。

## 停止条件

出现以下情况立即停止并报告：

- Long Testing Handoff 缺失且当前任务依赖 long 自动化事实。
- Long `required_validation_gate` 缺失、blocked、stale 或 effective validation evidence 不可解析。
- Planning `execution_prerequisite_readiness` 中当前阶段必需依赖未就绪。
- `deployment_revision_reconciliation.status` 为 `in_progress | blocked`，或完成事务与当前部署身份不一致。
- `intake_binding` 缺失，或其中 epoch、writeback target、Planning/Long Handoff、Planning revision、Matrix revision、Required Validation Gate 与当前来源不一致。
- `active_release_handoff.status: current` 但快照封套、冻结 revision、业务旅程矩阵或完整部署身份与当前 Runtime 不一致。
- long 自动化失败且用户没有明确要求处理失败。
- 依赖测试未通过。
- 证据缺失且经过自然语言追问后仍无法判断。
- 需要破坏性操作但没有用户二次确认。
- 服务器目标、账号、URL、部署版本或数据范围不清楚。
- 发现安全风险、越权、数据泄露、异常流量或可被蓄意破坏的行为。
- `writeback_target` 缺失。
- Planning/Long Handoff revision 缺失、冲突或过期。
- 测试发现尚未完成 Change Triage，或 disposition 要求 Planning 重入但尚无新增量 Handoff。
- required FLOW 未映射、本地或部署后业务/E2E 证据缺失，或影响 required FLOW 的 finding 尚未闭环。
- Runtime 回写失败。
- 存在 `interrupted_pending_reconcile` 项且无法通过已有证据恢复。
- 当前项的 Per-Test Durable Writeback 检查点写入失败。
- 尝试推进下一项时 Test Progression Gate 不满足。

## Per-Test Durable Writeback Rule

### 总则

`05-test-writeback.md#test-validation-resultsmd-格式` 唯一枚举的每个正式 `item_type` 都必须成为独立、可恢复、可审计的执行单元；自动化结果继承仍按具体 `case_id` 建立正式项。这里不复制另一份类型清单。

任何测试项不得只在对话中被认为完成。必须先完成 Runtime 持久化回写，才允许推进到下一个独立测试项。

此规则不可被弱化、简化或口头替代。

### 测试开始前检查点

在执行、引导或继承每一个测试项前，必须先写回当前项状态。

至少记录：

```yaml
item_id:
item_type:
attempt:
environment:
environment_revision_ref:
status: in_progress
started_at:
completed_at: null
depends_on_check:
expected_evidence:
result_summary: null
evidence_refs: []
evidence_missing_reason: null
blocker_or_failure_reason: null
covers: []
covered_by: []
evidence_reuse: false
writeback_status: updated
```

硬性要求：

- 只有该检查点成功写入 Runtime 后，AI 才能执行当前测试、引导用户操作、进入服务器验证或继承对应自动化结果。
- 若写回失败，必须停止，不得继续执行或引导下一项。
- 不得只在自然语言回复中声明"现在开始测试"而不写回。

### 测试完成后检查点

每一项测试出现以下任一结果时，必须立刻完成结果回写：

- `verified`
- `verified_by_user_report`
- `reused_from_long`
- `failed`
- `blocked`
- `blocked_by_dependency`
- `evidence_insufficient`
- `deferred`
- `deferred_to_p2`
- `interrupted_pending_reconcile`

至少记录：

```yaml
item_id:
attempt:
environment:
environment_revision_ref:
status:
completed_at:
result_summary:
evidence_refs:
evidence_missing_reason:
blocker_or_failure_reason:
covers:
covered_by:
evidence_reuse:
writeback_status:
```

注意：`status` 是测试项生命周期的唯一正式状态字段，不使用 `final_status`。`evidence_refs` 是测试项证据的唯一正式字段，不使用 `evidence`。`blocker_or_failure_reason` 是失败或阻塞原因的唯一正式字段，不使用 `failure_or_blocker_reason`。`next_executable_item` 只能写入 `test-runtime-state.md`，不得写入单项结果记录。

硬性要求：

- 当前项的结果回写成功前，禁止开始、执行、引导或继承下一个独立测试项。
- 当前项仍为 `in_progress` 时，禁止推进到下一项。
- 证据不足也必须形成明确状态，不允许静默跳过。
- 自动化继承结果也必须按可追溯测试项写入，而不是只写一个汇总结果。

### 推进门禁（Test Progression Gate）

只有同时满足以下条件，AI 才能推进到下一条测试：

```text
当前项已结束，不再处于 in_progress；
当前项最终状态已写入 test-validation-results.md；
当前项 writeback_status = updated；
当前依赖关系已重新计算；
下一项不是 blocked_by_dependency；
```

任一条件不满足时：

- 必须停止推进。
- 必须报告具体不满足的条件。
- 不得以口头总结、临时记忆或"之后补写"替代回写。
- 在 `test-execution-events.md` 中记录 `progression_gate_failed` 事件。
- 在 `test-runtime-state.md` 中更新 `overall_status: blocked`。

### 推进门禁终态分支规则

当当前项已是终态且门禁基础条件满足时，按当前项 `status` 分别校验：

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

### 中断恢复规则（Runtime Resume/Recovery Rule）

当出现以下情况时：

- AI 会话恢复；
- 用户说"继续测试"；
- 测试过程被中断；
- 工具调用失败；
- Runtime 文档存在未完成项；
- 当前状态不一致；

AI 必须优先读取：

```text
test-runtime-state.md
test-validation-results.md
test-execution-events.md
manual-test-queue.md
test-execution-order.md
business-journey-test-matrix.md
test-evidence-index.md
release-handoff.md（存在时）
```

恢复逻辑：

1. 先校验 `test-runtime-state.md.intake_binding` 与当前 Planning/Long Handoff、epoch、revision 和 Required Validation Gate 一致；缺失或冲突时保持阻断，不得继续恢复测试项。
2. 校验部署切换事务与 `active_release_handoff`；存在未完成事务、当前快照与冻结载荷不一致或旧快照尚未失效时，先按 `05-test-writeback.md` 恢复对应事务。
3. 只要 `test-validation-results.md` 中任一项 `status = in_progress`，无论 `writeback_status` 是否为 `updated`，恢复时都必须进入 `interrupted_pending_reconcile` 流程。
4. 将每个 `in_progress` 项改为 `interrupted_pending_reconcile`。
5. 更新 `test-runtime-state.md`：`resume_required: true`、`overall_status: blocked`。
6. 禁止选择任何新测试项。
7. 按 `started_at` 从早到晚逐条恢复。
8. 每项恢复后重新计算 `next_executable_item`。
9. 所有 `interrupted_pending_reconcile` 项处理完成前，不得恢复正常执行。

`writeback_status = updated` 仅表示当前检查点已成功持久化，不表示测试已完成。

### 文件不一致恢复裁决规则（Recovery Conflict Resolution Rule）

当恢复时各文件状态不一致，按以下优先级裁决：

**情况 A：结果文件是终态且已成功回写**

若 `test-validation-results.md` 中某项：

```yaml
status: <终态>
writeback_status: updated
```

即使 `test-runtime-state.md` 仍显示该项为 `in_progress`：

- 必须以结果文件为准。
- 修正 `test-runtime-state.md` 的游标。
- 不得错误标记为 `interrupted_pending_reconcile`。
- 再重新计算下一条可执行项。

**情况 B：结果文件是 in_progress 或结果记录缺失**

以下任一情况：

- 结果文件中该项仍为 `in_progress`；
- `test-runtime-state.md` 指向当前项，但结果文件中没有该项；
- 当前项存在开始事件，但没有完成检查点；

则标记为：

```yaml
status: interrupted_pending_reconcile
```

写回后再判断是否可基于已有证据恢复结果。

**情况 C：结果已通过，但证据索引不完整**

若结果文件写为：

```yaml
status: reused_from_long / verified / verified_by_user_report
writeback_status: updated
```

但 `evidence_refs` 缺失、引用无效，或 `test-evidence-index.md` 无法找到对应证据：

- 不得推进。
- 必须将该项调整为 `evidence_insufficient`。
- 写明 `evidence_missing_reason`。
- 重新计算依赖和下一项。

**情况 D：多个 in_progress 项**

若同时发现多个 `in_progress` 项：

- Runtime 总状态必须为 `blocked`。
- `resume_required: true`。
- 不得选择新的测试项。
- 按开始时间从早到晚逐条恢复、确认或标记阻塞。
- 所有冲突项解决前不得继续正常执行。

**情况 E：当前项无法判断**

无法通过已有证据判断结果时：

- 一次只向用户追问一个缺失事实。
- 不得假定通过、失败或未执行。
- 未恢复完成前，不得跳到后续项。

## 状态枚举

所有测试项（`case_id`、`MANUAL-OP`、真实设备验证项、部署后业务/E2E 验证项、服务器验证项、环境前置核验项）共享以下状态枚举：

| 状态 | 含义 | 使用约束 |
| --- | --- | --- |
| `pending` | 已规划但尚未开始；属于 test-validation-results.md 的测试项生命周期初始状态，不等同于 manual-test-queue.md 的 queue_state | — |
| `in_progress` | 已开始执行，尚未产生最终结果 | 必须写入检查点，不得只在对话中声明 |
| `reused_from_long` | 继承 long 自动化结果 | 需附带 evidence source 和 writeback_status |
| `verified` | 已验证通过 | 需附带证据引用 |
| `verified_by_user_report` | 由用户自然语言反馈确认通过 | 需附带用户反馈证据 |
| `failed` | 验证执行后结果不通过 | 需附带 `blocker_or_failure_reason` |
| `blocked` | 被阻塞（非依赖原因） | 需附带 `blocker_or_failure_reason` |
| `blocked_by_dependency` | 被前置依赖阻塞 | 需记录具体阻塞的依赖项 |
| `evidence_insufficient` | 证据不足，无法判定 | 需记录 evidence_missing_reason |
| `interrupted_pending_reconcile` | 曾开始但中断，需恢复确认 | 不得假设通过或失败 |
| `deferred` | 延期处理 | 需记录延期原因 |
| `deferred_to_p2` | 延期至 P2 | 需记录 P1/P2 变更原因 |

状态使用约束：

- `in_progress` 必须被定义为正式状态，不得只存在于自然语言描述。
- `interrupted_pending_reconcile` 必须专门表示"曾开始但没有可靠完成结果"的状态。
- `failed` 与 `blocked` 的区别：`failed` 表示验证执行后结果为不通过；`blocked` 表示无法开始验证。
- 不允许用 `pending_manual`、`pending_server` 等队列状态替代当前测试项的实际执行状态。
- 队列状态、环境分类、最终结果状态应保持语义分离，避免混用。

## MANUAL-OP 覆盖 Case 逐条回写规则

一个 `MANUAL-OP` 可以只要求用户完成一次操作，但它覆盖的每一个 case 必须在 `test-validation-results.md` 中拥有独立记录。

当 `MANUAL-OP-001` 覆盖多个 case 时：

1. `MANUAL-OP-001` 自身必须有独立结果记录。
2. 每个被覆盖 case 必须有独立结果记录。
3. 每个被覆盖 case 必须至少记录：

```yaml
item_id:
item_type: case
status:
covered_by:
evidence_refs:
evidence_reuse:
result_summary:
evidence_missing_reason:
writeback_status:
```

4. 只有该 case 的全部业务断言均被现有证据支撑时，才可写为 `verified` 或 `verified_by_user_report`。
5. 若同一操作已完成，但某个 case 缺少特定观察点，则该 case 必须写为：

```yaml
status: evidence_insufficient
evidence_reuse: true
covered_by:
  - MANUAL-OP-001
evidence_missing_reason: <缺失的观察点描述>
```

6. 不得因为 MANUAL-OP 通过，就默认其所有 `covers` 的 case 都通过。

同时保留原有原则：

- 不得要求用户重复完整操作。
- 只能基于已有操作补问一个缺失观察点。
- 用户不填写任何内部字段。

## attempt 递增规则

`attempt` 只在真正重新执行该测试项时递增。以下情况不增加 `attempt`：

- 单纯读取文件、恢复判断、修复游标、补写证据索引。
- 从 `interrupted_pending_reconcile` 恢复并确认原执行结果。
- 用户自然语言反馈后判断结果。
- 修复文件不一致或纠正状态冲突。

以下情况增加 `attempt`：

- 用户明确要求重新测试。
- 环境变化后重测。
- 自动化例外重跑。
- 测试项真正重新执行一次完整流程。


## 写回失败处理

### 情况 A：仍可持久化最小错误记录

若结果文件或状态文件仍可写入：

- 将当前项记录为 `writeback_status: blocked`。
- Runtime 整体状态写为 `overall_status: blocked`。
- 记录 Runtime writeback blocker。
- 停止推进。
- 最终结论必须为 `Blocked`。

### 情况 B：完全无法持久化

若连最小错误记录也无法写入：

- 不得声称"已经将该项标记为 blocked"。
- 不得伪造任何已写回状态。
- 只能向用户报告 `runtime_writeback_unpersisted`。
- 立即停止推进。
- 下次恢复时，必须依据最后成功持久化检查点处理。
- 当前项若缺少可靠完成检查点，必须进入 `interrupted_pending_reconcile`。

## 单测试项持久化顺序

### 开始一个测试项

每个 canonical `item_type` 以及自动化结果继承都必须按以下顺序：

1. 先在 `test-validation-results.md` 创建或更新该项，写入 `status: in_progress`、`writeback_status: updated`、`started_at`、`attempt`、`environment`、`environment_revision_ref`、`depends_on_check`、`expected_evidence`、`completed_at: null`、`result_summary: null`、`evidence_refs: []`、`evidence_missing_reason: null`、`blocker_or_failure_reason: null`、`covers: []`、`covered_by: []`、`evidence_reuse: false`。
2. 再更新 `test-runtime-state.md` 的 `current_item`、`current_item_status: in_progress`、`last_durable_checkpoint_at`。
3. 最后在 `test-execution-events.md` 追加 `test_started` 事件。

只有以上检查点全部成功持久化后，才允许执行、引导用户操作、进入服务器验证或继承 long 结果。

### 完成一个测试项

完成一个测试项时，必须按以下顺序：

1. 先更新 `test-evidence-index.md`，或明确记录证据缺失原因。
2. 再更新 `test-validation-results.md` 的正式 `status`、`evidence_refs`、`result_summary`、失败或阻塞原因等。
3. 若为 MANUAL-OP，逐条更新被覆盖 case 的独立结果记录。
4. 重新计算依赖关系和 `next_executable_item`。
5. 再更新 `test-runtime-state.md` 的游标。
6. 最后追加 `test_completed`、`test_failed`、`test_blocked`、`evidence_added` 等事件。

当前项的完成结果、证据索引和覆盖 case 都未成功回写前，禁止进入下一个独立测试项。

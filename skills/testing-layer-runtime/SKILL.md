---
name: testing-layer-runtime
description: 通用测试治理 Skill，用于在 long-task-orchestrator 完成 ready_for_local_test 后管理期次测试生命周期：读取 planning 测试范围与带 revision 的 long 自动化交接，继承已通过自动化结果，规划测试顺序，指导人工/真实设备/云端/外部能力/最终验收，对测试发现做 Execution/Test Change Triage，并在完整上线时整理项目发布/安全流程移交材料。Use when Codex needs to manage phase testing, manual acceptance, real-device validation, server verification, external capability validation, final acceptance, test evidence/writeback, change triage, or release handoff. Do not use it to re-run long-owned vitest/jest/integration/api-test/playwright automation unless an allowed reuse exception applies.
---

# Testing Layer Runtime

使用本 Skill 管理测试生命周期，而不是重复执行开发期自动化测试。它承接：

```text
planning-layer-runtime -> long-task-orchestrator -> testing-layer-runtime -> release/security gate（项目自带流程或可选 skill）
```

## Skill 边界

`planning-layer-runtime` 负责冻结执行前合同，并在执行/测试发现被分类为 planning gap、accepted requirement change 或改变正式合同的 design drift 时受控重入；它允许产出项目指定的 Test and Acceptance Plan，但只定义“测什么”，禁止定义“怎么测、谁来测、测试顺序、执行状态、测试结果”。

`long-task-orchestrator` 截止到 `ready_for_local_test`，负责开发、重构、迁移、自动化测试代码、单元测试、业务测试、自动化执行和自动化测试结果记录。`vitest`、`jest`、`integration`、`api-test`、`playwright` 默认属于 long。

`testing-layer-runtime` 截止到 release handoff，负责自动化结果汇总与继承、测试规划、人工测试、真实设备测试、云端验证、外部能力验证、最终验收和上线前验证移交。禁止重新执行 long 已完成且通过的自动化测试。

## 必读文件

每次执行前按需读取：

- 项目环境事实源（如 `docs/environment.md`、README、CI 配置或用户指定文档）：项目本地、云端、数据库、OpenAPI、Playwright、git 工具事实源。
- `testing-handoff.md` 或 `long-runtime-testing-summary.md`：long 自动化测试事实源，优先级高于重新执行。
- Planning Handoff 指定的 Test and Acceptance Plan：只读取测试范围与验收对象，不按固定编号或目录猜测路径。
- `references/01-test-runtime-core.md`：职责边界、Long Testing Handoff、Test Planning Phase、依赖顺序和停止条件。
- `references/02-test-environment-gates.md`：自动化结果继承、人工/真实设备、服务器、release handoff 环境规则。
- `references/03-evidence-format.md`：证据、截图、Manual Guidance 和最终报告格式。
- `references/04-destructive-boundaries.md`：破坏性测试、服务器测试、上线测试和安全告警边界。
- `references/05-test-writeback.md`：状态、阶段报告、证据索引、`test-execution-order.md` 和阻塞项回写规则。

## Project Path Binding

首次进入目标项目时，必须根据 Planning Handoff、Long Testing Handoff、项目现有规划目录约定和真实文件绑定以下占位符：

```text
<phase_test_plan_path>
<long_testing_handoff_path>
<phase_testing_runtime_directory>
<formal_acceptance_record_path>
```

- `<phase_testing_runtime_directory>` 是本期 `writeback_target`，不是固定目录名。
- 优先使用 Long Testing Handoff 或 Planning Handoff 明确声明的期次与写回位置；未声明时，才从已确认的当前规划目录和项目约定派生。
- 目标路径无法唯一确认、跨期冲突或写入权限不足时，进入 Test Intake Mode 并阻断写回。
- 本期测试状态、事件、证据索引、人工队列、依赖顺序和恢复数据只能写入 `<phase_testing_runtime_directory>`。
- 项目根目录 `.runtime/` 只允许保存该 Skill 明确定义的跨期项目级环境索引或稳定配置；不得保存某一期测试状态、证据、队列、游标或恢复快照。
- 不得沿用来源项目的项目名、期次名、绝对路径、固定文档编号或历史 Runtime 位置。

## Long Testing Handoff

启动时必须优先查找并读取：

```text
testing-handoff.md
long-runtime-testing-summary.md
```

Long Runtime 必须提供：

```yaml
planning_baseline_revision:
active_change_revision: # 初始 Handoff 省略
executed_task_contract_revisions: []
automated_passed:
automated_failed:
automated_skipped:
manual_required:
coverage:
```

Testing Runtime 必须继承 `automated_passed`，并把继承状态记录为：

```text
reused_from_long
```

Testing 必须核对 Long Handoff 的 baseline/change revision 与其所引用 Planning Handoff 一致，且 `executed_task_contract_revisions` 不包含 `context_only`、`completed_locked` 或 `cancelled`。若 long handoff 缺失、字段不完整、revision 冲突或证据不存在，进入 Test Intake Mode 并报告缺口；不得用测试层重复执行来掩盖 handoff 缺失或过期交接。

## Automated Result Reuse Rule

若同时满足：

- automated status = pass
- evidence exists
- long handoff verified

则 Testing Runtime 不得重新执行该自动化测试，直接继承结果并记录来源为 `long testing handoff`。

允许重新执行的条件仅限：

- 用户明确要求
- 环境发生变化
- 自动化证据缺失
- 自动化失败
- 自动化结果过期

重新执行时必须在 Runtime 里记录原因，且不得把 long-owned automation 当作 testing 的默认职责。

## Testing Runtime Writeback

规则：

- 进入任何测试模式前，必须解析 `current_test_epoch`。
- `current_test_epoch` 来源优先级：long handoff 的 `source_of_truth` / `runtime_epoch` / formal execution record；planning test plan 路径中的期次目录；用户明确指定的期次。
- `writeback_target` 必须绑定为 `<phase_testing_runtime_directory>`，并与当前期次 Handoff、项目目录约定和既有 Runtime 事实一致。

动作：

- Long Testing Handoff、Test Intake Gate、Test Planning Phase、依赖顺序生成、人工测试操作、用户自然反馈、服务器验证、release handoff 和最终报告前，按 `references/05-test-writeback.md` 回写。
- 每个测试项（`case_id`、`MANUAL-OP`、真实设备验证项、服务器验证项）开始前，必须完成 Per-Test Durable Writeback Rule 的前置检查点回写（`references/01-test-runtime-core.md`）；检查点写入成功后方可执行或引导该测试项。
- 每个测试项结束后，必须完成 Per-Test Durable Writeback Rule 的完成检查点回写；回写成功后方可推进到下一个测试项。
- Test Planning Phase 必须生成或更新 `test-execution-order.md`。
- 每次用户回传自然语言、截图或简短反馈后，AI 必须结构化判断并回写验证状态。
- 推进到下一个测试项前，必须通过 Test Progression Gate（`references/01-test-runtime-core.md`）。
- 最终报告输出前，必须先完成 Runtime 回写。

禁止项：

- 回写失败或 `writeback_target` 缺失时，最终结果只能是 `Blocked`。
- 禁止把测试执行结果写回 planning SoT。
- 禁止把 long 已通过自动化重新跑一遍再声称 testing 通过。
- 禁止在 `writeback_status != updated` 时推进到下一个测试项。

## Execution/Test Change Triage

测试发现不能直接等同于开发 Bug。任何会导致返工、改变测试依据或需要上游确认的发现，必须先在 `<phase_testing_runtime_directory>/change-triage.md` 记录：

```yaml
change_decision:
  source_stage: testing
  finding_type: <implementation_defect | test_defect | planning_gap | requirement_change | design_drift | deferred_improvement>
  observed_result:
  expected_source:
  is_current_plan_still_valid:
  affected_ids: []
  planning_reentry_required:
  reentry_documents: []
  change_level:
  disposition: <fix_in_execution | fix_in_test | reopen_current_planning | defer_to_next_phase | reject_change>
```

分流规则：

- 当前 Planning 合同仍有效、实现未满足合同：`implementation_defect -> fix_in_execution`，为 long-task-orchestrator 形成可追溯 defect handoff；只阻断受影响测试。
- 测试脚本、测试数据、环境准备、证据映射或 Testing Runtime 自身错误：`test_defect -> fix_in_test`；只能修改测试层获准资产和 Runtime，不得借此改业务代码或 Planning SoT。
- Planning 缺少必要合同：`planning_gap -> reopen_current_planning`。
- 用户接受的新需求或验收变化：`requirement_change -> reopen_current_planning`。
- 架构、API、数据、权限、状态、UI/体验或验收合同需要改变：`design_drift -> reopen_current_planning`。
- 不进入本期的改善项：按确认结果 `defer_to_next_phase` 或 `reject_change`。

`reopen_current_planning` 必须停止受影响测试并把 triage 证据交给 planning-layer-runtime；只有新的增量 Planning Handoff、Long 实现及对应 Long Testing Handoff 完成后，受影响测试才能恢复。未受影响且依赖仍成立的测试与已完成证据不得无条件失效或重跑。

## 执行模式与策略

执行模式：

- Test Intake Mode：测试来源、long handoff、环境或用例范围不清楚时使用。
- Test Planning Phase：根据 Planning Handoff 指定的 Test and Acceptance Plan 和 Long Testing Handoff 生成 `test-execution-order.md`，输出自动化已完成、自动化失败、待人工验证、待服务器验证、待上线验证。
- Test Governance Mode：管理人工测试、真实设备测试、外部能力验证和证据闭环。
- Server Verification Mode：部署完成后验证服务器独有事实。
- Release Handoff Mode：完整上线测试时整理发布/安全门禁移交信息；若项目提供专门 release/security skill 或流程，则切换过去。

执行策略：

- Automated Reuse Strategy：继承 long 自动化结果，不重复执行。
- Manual Operation De-duplication Strategy：人工测试拆解必须先按用户实际操作去重。同一 actor、entry、precondition、operation、data_domain 的人工动作只能引导用户执行一次。一个人工动作可以覆盖多个 case / assertion。后续 case 若依赖同一动作，必须复用既有证据，只补缺失观察点，不得要求用户重复完整流程。
- Guided Manual Operation Strategy：人工测试开始后，AI 必须从 `manual-test-queue.md` 中选择当前第一个 `queue_state = ready`、`depends_on` 全部通过、`blocked_by` 为空、`covered_by_evidence = false`、MANUAL-OP 在 `test-validation-results.md` 中不存在或 `status = pending`、当前环境可执行的操作，主动给出用户可照做的具体步骤。不得只输出 case 名称或任务名称。
- Manual Guidance Strategy：无法可靠自动化的交互操作使用；用户自然反馈，AI 负责追问、结构化、证据判断和 Runtime 回写。
- Server Verification Strategy：只验证本地和 long 无法证明的云端事实。
- Release Handoff Strategy：只整理上线门禁移交，不输出 release pass。

## 执行顺序

1. 定位当前期次和 `writeback_target`。
2. 读取 Long Testing Handoff，校验 baseline/change revision 与 TASK contract revision；缺失或冲突时进入 Test Intake Mode 并报告 handoff 缺口。
3. 读取 Planning Handoff 指定的 Test and Acceptance Plan，只提取”测什么”。
4. 进入 Test Planning Phase，先继承 `automated_passed`，标记 `reused_from_long`。
5. 对 `automated_failed`、`automated_skipped`、`manual_required`、服务器验证和上线验证建立分类与阻塞关系。
6. 基于已继承、失败、跳过、人工、服务器和上线验证范围，生成或更新 `test-execution-order.md`。
7. 对人工测试候选项执行 Manual Operation De-duplication Gate。
8. 生成或更新 `manual-test-queue.md`，确保它是用户实际操作队列，不是 case 清单。
9. 选择下一个可执行测试项时，必须完成 Per-Test Durable Writeback Rule 的前置检查点回写；检查点写入成功后方可执行或引导该测试项。
10. 每个测试项完成后，必须完成 Per-Test Durable Writeback Rule 的完成检查点回写；回写成功后方可推进到下一个测试项。
11. 推进到下一个测试项前，必须通过 Test Progression Gate。
12. 只执行依赖已通过的人工/真实设备/服务器验证。
13. 每次用户反馈并完成 Runtime 回写后，若仍存在下一个可执行人工操作，必须主动引导下一个操作；若存在阻塞、证据不足、破坏性确认、服务器信息缺失或测试完成，则说明当前状态和下一步。
14. 每个失败、偏差或新反馈先执行 Execution/Test Change Triage；按 disposition 在 Testing 修正、交回 Long、重入 Planning、延期或拒绝。
15. 完成非上线验证后输出验收结论；完整上线时进入 Release Handoff Mode。

## 硬边界

- 不修改业务产物。
- 不修改 planning SoT 或当前项目文档；只写 Runtime 输出目录。
- 不从 testing 反向定义需求、范围、P0/P1/P2、UI 或验收标准。
- 不把 `implementation_defect`、`test_defect`、`planning_gap`、`requirement_change` 与 `design_drift` 混为同一种 Bug，也不绕过 triage 直接返工。
- 不重新执行 long 已通过且有证据的 `vitest`、`jest`、`integration`、`api-test`、`playwright`。
- 不把纯 UI 图对照、页面截图差异或视觉验收生成独立人工测试用例；UI 状态只能作为业务用例附属证据，或由自动化快照/组件测试覆盖。
- 不把测试入口删除、测试快捷操作删除或测试专用接口删除生成到某一期的独立测试用例；这类事项只在完整上线/最终发布门禁中移交项目定义的发布/安全流程。
- 不把截图存在当作业务通过证据；必须同时有断言或人工内容。
- 不执行生产上线门禁；上线测试必须交给项目定义的发布/安全流程。
- 不执行未确认的数据库迁移、生产数据修改、压测、安全扫描或外部破坏性操作。
- 不读取、修改或输出真实密钥；环境配置只关注 `.env.example`、项目环境事实源或用户明确提供的脱敏配置。
- 保留无关工作区改动；未经用户明确要求，不 stage、commit、push。

## 阶段报告格式

每个阶段结束后向用户报告自然语言摘要，不默认暴露 Runtime 内部字段：

- 当前阶段和执行范围。
- 已继承的自动化结果。
- 待人工、待服务器、待上线验证项。
- 已获得的证据摘要。
- 结果：通过、未通过、阻塞、证据不足或 deferred。
- 问题、风险和下一步。
- 需要用户继续操作时，只提出当前一个下一步操作或一个确认问题。
- 需要用户继续操作时，必须输出“下一个测试操作”的具体引导，包括：使用哪个角色/账号、进入哪个页面/入口、前置状态、具体点击/输入/提交步骤、需要观察什么、需要反馈什么。不得只说“请测试某某功能”。

最终报告必须明确区分 `已继承自动化通过`、`已人工确认`、`服务器已验证`、`证据不足`、`上线门禁未执行/已移交`。

---
name: testing-layer-runtime
description: 本项目本地 Skill，用于在 long-task-orchestrator 完成 ready_for_local_test 后管理测试生命周期：读取 planning 的测试范围与 long 的自动化测试交接，继承已通过自动化结果，规划测试顺序，指导人工/真实设备/云端/外部能力/最终验收，并在完整上线时移交 ai-release-security-gate。Use when Codex needs to manage phase testing, manual acceptance, real-device validation, server verification, external capability validation, final acceptance, test evidence/writeback, or release handoff. Do not use it to re-run long-owned vitest/jest/integration/api-test/playwright automation unless an allowed reuse exception applies.
---

# Testing Layer Runtime

使用本 Skill 管理测试生命周期，而不是重复执行开发期自动化测试。它承接：

```text
planning-layer-runtime -> long-task-orchestrator -> testing-layer-runtime -> ai-release-security-gate
```

## Skill 边界

`planning-layer-runtime` 截止到开发开始前，负责需求、范围、数据模型、权限模型、UI、验收标准、风险和 P0/P1/P2。允许产出 `11-测试方案与验收用例.md`，但只定义“测什么”，禁止定义“怎么测、谁来测、测试顺序、执行状态、测试结果”。

`long-task-orchestrator` 截止到 `ready_for_local_test`，负责开发、重构、迁移、自动化测试代码、单元测试、业务测试、自动化执行和自动化测试结果记录。`vitest`、`jest`、`integration`、`api-test`、`playwright` 默认属于 long。

`testing-layer-runtime` 截止到 release handoff，负责自动化结果汇总与继承、测试规划、人工测试、真实设备测试、云端验证、外部能力验证、最终验收和上线前验证移交。禁止重新执行 long 已完成且通过的自动化测试。

## 必读文件

每次执行前按需读取：

- `docs/environment.md`：项目本地、云端、Prisma、OpenAPI、Playwright、git 工具事实源。
- `testing-handoff.md` 或 `long-runtime-testing-summary.md`：long 自动化测试事实源，优先级高于重新执行。
- `docs/计划安排/**/11-测试方案与验收用例.md`：只读取测试范围与验收对象。
- `references/01-test-runtime-core.md`：职责边界、Long Testing Handoff、Test Planning Phase、依赖顺序和停止条件。
- `references/02-test-environment-gates.md`：自动化结果继承、人工/真实设备、服务器、release handoff 环境规则。
- `references/03-evidence-format.md`：证据、截图、Manual Guidance 和最终报告格式。
- `references/04-destructive-boundaries.md`：破坏性测试、服务器测试、上线测试和安全告警边界。
- `references/05-test-writeback.md`：状态、阶段报告、证据索引、`test-execution-order.md` 和阻塞项回写规则。

## Long Testing Handoff

启动时必须优先查找并读取：

```text
testing-handoff.md
long-runtime-testing-summary.md
```

Long Runtime 必须提供：

```yaml
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

若 long handoff 缺失、字段不完整或证据不存在，进入 Test Intake Mode 并报告缺口；不得用测试层重复执行来掩盖 handoff 缺失。

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
- `writeback_target` 固定为 `docs/计划安排/<current_test_epoch>/testing-runtime/`。

动作：

- Long Testing Handoff、Test Intake Gate、Test Planning Phase、依赖顺序生成、人工测试操作、用户自然反馈、服务器验证、release handoff 和最终报告前，按 `references/05-test-writeback.md` 回写。
- Test Planning Phase 必须生成或更新 `test-execution-order.md`。
- 每次用户回传自然语言、截图或简短反馈后，AI 必须结构化判断并回写验证状态。
- 最终报告输出前，必须先完成 Runtime 回写。

禁止项：

- 回写失败或 `writeback_target` 缺失时，最终结果只能是 `Blocked`。
- 禁止把测试执行结果写回 planning SoT。
- 禁止把 long 已通过自动化重新跑一遍再声称 testing 通过。

## 执行模式与策略

执行模式：

- Test Intake Mode：测试来源、long handoff、环境或用例范围不清楚时使用。
- Test Planning Phase：根据 `11-测试方案与验收用例.md` 和 Long Testing Handoff 生成 `test-execution-order.md`，输出自动化已完成、自动化失败、待人工验证、待服务器验证、待上线验证。
- Test Governance Mode：管理人工测试、真实设备测试、外部能力验证和证据闭环。
- Server Verification Mode：部署完成后验证服务器独有事实。
- Release Handoff Mode：完整上线测试时整理移交信息并切换到 `ai-release-security-gate`。

执行策略：

- Automated Reuse Strategy：继承 long 自动化结果，不重复执行。
- Manual Operation De-duplication Strategy：人工测试拆解必须先按用户实际操作去重。同一 actor、entry、precondition、operation、data_domain 的人工动作只能引导用户执行一次。一个人工动作可以覆盖多个 case / assertion。后续 case 若依赖同一动作，必须复用既有证据，只补缺失观察点，不得要求用户重复完整流程。
- Guided Manual Operation Strategy：人工测试开始后，AI 必须从 `manual-test-queue.md` 中选择当前第一个依赖已通过、未验证、未阻塞、未被已有证据覆盖的操作，主动给出用户可照做的具体步骤。选择下一个人工操作时，优先使用 `manual-test-queue.md` 中 `MANUAL-OP.depends_on` 和 `MANUAL-OP.blocked_by` 判断是否可执行。不得只输出 case 名称或任务名称。
- Manual Guidance Strategy：无法可靠自动化的交互操作使用；用户自然反馈，AI 负责追问、结构化、证据判断和 Runtime 回写。
- Server Verification Strategy：只验证本地和 long 无法证明的云端事实。
- Release Handoff Strategy：只整理上线门禁移交，不输出 release pass。

## 执行顺序

1. 定位当前期次和 `writeback_target`。
2. 读取 Long Testing Handoff；缺失时进入 Test Intake Mode 并报告 handoff 缺口。
3. 读取 `11-测试方案与验收用例.md`，只提取“测什么”。
4. 进入 Test Planning Phase，先继承 `automated_passed`，标记 `reused_from_long`。
5. 对 `automated_failed`、`automated_skipped`、`manual_required`、服务器验证和上线验证建立分类与阻塞关系。
6. 基于已继承、失败、跳过、人工、服务器和上线验证范围，生成或更新 `test-execution-order.md`。
7. 对人工测试候选项执行 Manual Operation De-duplication Gate。
8. 生成或更新 `manual-test-queue.md`，确保它是用户实际操作队列，不是 case 清单。
9. 只执行依赖已通过的人工/真实设备/服务器验证。
10. 每次用户反馈并完成 Runtime 回写后，若仍存在下一个可执行人工操作，必须主动引导下一个操作；若存在阻塞、证据不足、破坏性确认、服务器信息缺失或测试完成，则说明当前状态和下一步。
11. 完成非上线验证后输出验收结论；完整上线时进入 Release Handoff Mode。

## 硬边界

- 不修改业务产物。
- 不修改 planning SoT 或当前项目文档；只写 Runtime 输出目录。
- 不从 testing 反向定义需求、范围、P0/P1/P2、UI 或验收标准。
- 不重新执行 long 已通过且有证据的 `vitest`、`jest`、`integration`、`api-test`、`playwright`。
- 不把纯 UI 图对照、页面截图差异或视觉验收生成独立人工测试用例；UI 状态只能作为业务用例附属证据，或由自动化快照/组件测试覆盖。
- 不把测试入口删除、测试快捷操作删除或测试专用接口删除生成到某一期的独立测试用例；这类事项只在完整上线/最终发布门禁中移交 `ai-release-security-gate`。
- 不把截图存在当作业务通过证据；必须同时有断言或人工内容。
- 不执行生产上线门禁；上线测试必须交给 `ai-release-security-gate`。
- 不执行未确认的数据库迁移、生产数据修改、压测、安全扫描或外部破坏性操作。
- 不读取、修改或输出真实密钥；环境配置只关注 `.env.example` 和 `docs/environment.md`。
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

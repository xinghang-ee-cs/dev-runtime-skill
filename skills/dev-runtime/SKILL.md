---
name: dev-runtime
description: 完整开发生命周期的统一路由入口。用户提出“开发某某应用”“做一个某某系统”“开始开发”“继续开发”或其他端到端开发请求时使用；即使请求模糊，也先进入 planning-layer-runtime。Planning Handoff Complete 后，至少 4 个实现单元的 execution_ready 工作交给 long-task-orchestrator，再按有效交接进入 testing-layer-runtime；少于 4 个实现单元时改由普通 Agent 按已确认范围实现和验证。需要代码检查、诊断、修复、审计或规范治理时，按 ai-code-inspection 当前 10 种场景路由。明确只要求单一阶段时直接使用对应 Skill。
---

# Dev Runtime

`dev-runtime` 负责完整开发请求的阶段选择与交接，不建立第二套 planning、implementation、testing 或 inspection Runtime。每个阶段开始前动态发现并完整读取对应 Skill；阶段内部状态、权限、产物和门禁只由该 Skill 定义。

## 使用范围

使用本 Skill：

- 用户要求从模糊想法开始完成一个应用、系统、功能或完整开发任务。
- 用户说“开始开发”“继续开发”“走完整流程”，但当前阶段或交接状态不清楚。
- 需要在 planning、implementation、testing 和代码检查之间按真实交接顺序推进。

不使用本 Skill：

- 用户明确只要求规划、实现、测试、代码检查、诊断、修复、审计或规范治理中的单一阶段；直接选择职责最匹配的 Skill。
- 只是无需正式规划和测试生命周期的零散小改；使用普通 Agent 指令。
- 发布批准、生产门禁或严格安全验收；交给目标项目自己的流程。

## 动态发现同级 Skill

不得假设 Skill 安装在仓库根目录 `skills/`，也不得写死 `.agents/skills/`、`.claude/skills/`、`.github/skills/` 或其他平台目录。

每次需要切换阶段时：

1. 读取当前项目有效的 `AGENTS.md`、平台 Skill 清单或等价发现信息。
2. 扫描项目实际安装的 Skill 目录，并读取候选 `SKILL.md` frontmatter。
3. 按 `name` 精确查找 `planning-layer-runtime`、`long-task-orchestrator`、`testing-layer-runtime` 或 `ai-code-inspection`。
4. 只完整读取当前阶段选中的 `SKILL.md`，再按它自己的路由加载必要 references、Profiles、模板和项目 Runtime。
5. Skill 缺失、重名、路径不确定或未安装时停止并报告；不得猜测路径、复制内嵌副本或假装已触发。

## 生命周期路由

```text
dev-runtime
-> planning-layer-runtime
-> Planning Handoff Complete
-> handoff_type / implementation-unit gate

planning_only
-> STOP: planning completed, no implementation handoff

execution_ready + implementation units < 4
-> normal Agent implementation and project validation
-> optional ai-code-inspection scene selected from the actual request
-> target project's own release/security process

execution_ready + implementation units >= 4
-> long-task-orchestrator
-> ready_for_local_test or ready_for_local_retest
-> testing-layer-runtime
-> release handoff
-> optional ai-code-inspection scene selected from the actual request
-> target project's own release/security process
```

“optional” 表示只有当前任务目标需要代码检查、诊断、修复、完整性核查、审计、重构评估、合并准备、hotfix 或规范治理时才进入 `ai-code-inspection`。不得为了让流程看起来完整而强制运行不匹配的场景。

## Planning 阶段

完整或模糊开发请求先使用 `planning-layer-runtime`：

- 需求不完整时停留在规划访谈和逐文档确认，不得直接实现。
- 只有 Planning Context、正式文档、最终人话总结和用户确认满足当前 planning Skill 的门禁后，才接受 `Planning Handoff Complete`。
- `handoff_type: planning_only` 时停止完整开发流程，不得交给实现 Skill。
- `handoff_type: execution_ready` 时读取已确认的 Development Landing Checklist、TASK 或等价实现清单，计算真实实现单元数量。

不得为了满足 long 的门禁而人为拆碎任务。实现单元数量必须来自 planning 已确认的真实任务边界。

## 实现分流

### 至少 4 个实现单元

只有同时满足以下条件，才进入 `long-task-orchestrator`：

- Handoff 已确认且未失效。
- `handoff_type: execution_ready` 且 `requires_execution_handoff: true`。
- 当前 long Skill 要求的正式职责、真实路径、`execution_constraints` 和 P0 门禁完整。
- 已确认工作至少包含 4 个真实实现单元。

进入后完全遵守 long 的 Intake Gate、Runtime Gate、自动化验证和 Long Testing Handoff。只有产生 `ready_for_local_test` 或 `ready_for_local_retest` 后，才允许切换到 testing。

### 少于 4 个实现单元

少于 4 个实现单元不属于 `long-task-orchestrator` 范围：

1. 保留 planning 已确认的范围、约束、验收标准和 Source of Truth。
2. 停止 long 路由，不创建 long Runtime，不产生或伪造 `ready_for_local_test`。
3. 由普通 Agent 按项目指令完成精确实现，并运行目标项目已有的适用 build、test、lint、typecheck、schema 或契约验证。
4. 明确报告未运行 long 和 testing 生命周期；没有有效 Long Testing Handoff 时不得触发 `testing-layer-runtime`。
5. 如用户还要求代码检查、合并准备或其他治理，按实际意图选择 `ai-code-inspection` 场景；否则移交目标项目自己的后续流程。

## Testing 阶段

只有存在有效 Long Testing Handoff，且 long 已达到 `ready_for_local_test` 或 `ready_for_local_retest` 时，才进入 `testing-layer-runtime`。

- testing 继承 long 已通过且证据有效的自动化结果，不为重复拿到“通过”而重跑。
- testing 负责人工、真实设备、服务器、云端、外部能力和最终验收，以及 release handoff。
- testing 不修改业务代码，也不批准生产发布。
- testing 发现开发缺陷时，按当前 testing 和 long Skill 的缺陷交接规则返回 long patch；不得由 dev-runtime 自创修复状态。

## AI Code Inspection 路由

使用 `ai-code-inspection` 前必须重新读取其当前 `SKILL.md` 并按完整语义选择场景。当前规则包含 10 个用户场景：

- 场景 1–9 使用 `single_run`，在各自范围与权限内一次完成，并只输出一次最终报告。
- 场景 6 虽内部完整执行 Step 1–7，仍是一次性只读审计，不是交互 gate。
- 只有场景 10 `standards_compliance_correction` 使用 `interactive_seven_step`。
- 普通“检查当前改动”进入 `changed_code_review`，不是七步交互治理。
- 明确 Bug 修复、需求完整性、全项目审计、合并准备或 hotfix 分别使用对应场景，不得统一压成一个“最终检查”。

`dev-runtime` 不复制十场景规则、不替场景授予修改权限，也不把普通 `继续` 解释为修复授权。场景执行完后，按 ai-code-inspection 的最终报告和建议后续场景决定是否结束、转入其他场景或返回前一阶段。

## 阶段切换门禁

1. 当前 Skill 未明确达到自己的交接条件时，不读取或执行下一阶段 Skill。
2. 用户态回复以问题、确认请求、范围纠偏或阻塞项收口时，本轮停止，不在同一轮越过用户确认。
3. 切换阶段前撤销上一阶段的临时权限；读取权限不自动成为修改权限。
4. 任一 Skill 缺失、输入不合法、Runtime 不一致、证据不足或环境条件缺失时，停止在当前阶段并报告唯一下一步。
5. 不得用普通待办、自然语言承诺、代码存在或自动化通过，替代正式 Skill 触发和 handoff。

## 最终报告

结束或阻塞时报告：

- `planning-layer-runtime`：未触发、进行中、已完成、`planning_only` 或阻塞原因。
- 实现分支：普通 Agent（少于 4 个实现单元）或 `long-task-orchestrator`（至少 4 个实现单元），以及真实验证状态。
- `testing-layer-runtime`：未适用、未触发、进行中、已完成或阻塞原因。
- `ai-code-inspection`：未适用，或实际选择的 `scene_id`、strategy、是否修改文件和结论。
- release/security：只说明移交状态，不宣称本仓库已经批准上线。

不得暗示未读取的 Skill、未执行的验证或未满足的门禁已经完成。

## 安全边界

- 保留与当前任务无关的工作区改动。
- 未经用户明确要求，不执行 stage、commit、push、reset、checkout、stash、部署、数据库迁移、真实数据修改、密钥修改或生产操作。
- 通用 Skill 源文件不得写入目标项目的身份、路径、账号、服务器、密钥或环境事实。

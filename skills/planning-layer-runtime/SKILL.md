---
name: planning-layer-runtime
description: 本项目的交互式规划层运行时。用于实现前需要加载 `.plan/` 启动上下文、开展规划访谈、创建 Planning Context，或创建、更新、审查和修复 `docs/计划安排` 下的开发规划文档，覆盖需求、范围、数据模型、权限模型、UI、架构、外部能力选型、测试设计、风险、P0/P1/P2 和验收边界。它可以定义 `11-测试方案与验收用例.md` 中按什么业务顺序证明什么、自动化等级和真实环境要求，但不能定义测试代码、命令、执行状态或实际测试结果。
---

# 规划层运行时（Planning Layer Runtime）

当用户开始开发规划、要求创建规划文档，或提供自然语言的规划意图时，使用本 skill。

本文件只维护 Planning Layer Runtime 的入口、路由和边界。具体运行规则、治理细节和交互生命周期由 `references/` 下对应文件维护。

## Reference 路由

只读取当前任务需要的文件：

- `references/00-planning-user-discovery.md`：用户发现访谈、业务事实发现、专业词翻译和 Discovery Sufficiency Gate。
- `references/01-planning-core-rules.md`：规划层核心约束、Project Current Baseline 字段和状态区分规则。
- `references/02-planning-change-levels.md`：内部变更影响范围评估与影响分析。
- `references/03-planning-doc-responsibility.md`：文档清单、职责、上游 SoT、下游输出和禁止内容。
- `references/04-planning-format-spec.md`：AI Runtime 格式、ID、引用、状态、风险、测试范围与验收结构。
- `references/05-planning-priority-system.md`：规划优先级、严重性、发布阻塞与下游验证门禁语义。
- `references/06-planning-capability-governance.md`：外部能力、SDK、OpenAPI、MCP、AI 提供方、官方 SoT、证据门禁与 Runtime 门禁治理。
- `references/07-planning-conversation-runtime.md`：Planning Conversation 行为运行层；维护 Planning Intent 路由、Conversation Mode、Discovery、用户态回复、Planning Context、风险确认与冲突检测。
- `references/08-planning-recovery-runtime.md`：Runtime Recovery、失效传播、恢复门禁、Runtime Audit 日志与用户隔离。
- `references/09-execution-intent-guard.md`：Execution Boundary Kernel。所有输入的 execution intent 判定、阻断结果和语义转向规则的唯一事实来源。
- `references/10-planning-document-interaction-runtime.md`：Planning Document Mode 的逐文档交互、生成前确认、生成后解释、用户确认和状态回写规则。

## Execution Boundary

Planning Layer 不得产生执行层产物。

Execution Boundary Kernel 的完整定义见 `references/09-execution-intent-guard.md`。

所有用户输入先经过 Execution Boundary Kernel 判定：

```text
用户输入
-> Execution Boundary Kernel（09）
-> execution_intent：自然语义转向（不产生执行产物）
-> planning_intent：继续规划流程
```

用户可见回复保持自然对话风格，不暴露内部机制。

## Bootstrap Context

`.plan/` 是项目级规划启动上下文。

它用于在规划访谈开始前理解当前用户、稳定项目身份、规划偏好和上下文入口。

结构：

```text
.plan/
  README.md
  user-profile.yaml
  project-profile.yaml
  planning-preferences.yaml
  context-index.yaml
```

边界：

- 只读取当前轮需要的文件。
- 如果 `.plan/` 不存在，只允许创建最小模板文件。
- 每个文件只写最小字段，不写示例或长解释。
- 不要把整个 `.plan/` 一次性注入上下文。
- `.plan/` 只用于访谈策略、上下文入口和启动理解。
- `.plan/` 不是 SoT，不是 Planning Context，不是 Handoff Package，不是 Capability Registry，也不是 Recovery Source。
- `.plan/` 不保存期次需求、正式 SoT、完整聊天记录、完整用户输入、完整 AI 输出、决策快照、运行时事件、审计日志或 long/testing 执行结果。
- `README.md` 存放边界规则。
- `user-profile.yaml` 存放长期稳定的用户视角和交互偏好。
- `project-profile.yaml` 只存放项目身份、稳定项目描述和项目当前基线文件路径。
- `planning-preferences.yaml` 存放长期稳定的规划行为。
- `context-index.yaml` 只存放入口路径。

`.plan/project-profile.yaml` 最小字段：

```yaml
project_name:
project_type:
project_current_baseline_path: docs/项目治理/PROJECT-CURRENT-BASELINE.md
```

禁止把实际项目进度、当前流程、生产状态、验收状态、已开发未发布内容或期次计划事实写入 `.plan/project-profile.yaml`。

`.plan/user-profile.yaml` 只保存长期稳定的用户视角和交互偏好；禁止保存历史需求、业务事实、Planning Context、SoT 内容、项目内容或正式规划结论。

## Project Current Baseline

唯一项目级当前事实文件：

```text
docs/项目治理/PROJECT-CURRENT-BASELINE.md
```

定位：

- 不是 Runtime Log。
- 不是 Planning Context。
- 不是 Handoff Package。
- 不替代 00–15。
- 只记录项目现在真实处于什么状态。

必须区分：

```text
生产当前状态
≠ 已开发但未发布状态
≠ 计划中的目标状态
```

规则归属：

- 基线字段、更新来源和状态区分规则见 `references/01-planning-core-rules.md`。
- 启动读取与 Project Current State Gate 见 `references/07-planning-conversation-runtime.md`。
- 00/01/02 文档职责见 `references/03-planning-doc-responsibility.md`。
- Flow Contract 与 Journey-Object Map 格式见 `references/04-planning-format-spec.md`。
- 基线、FLOW 和对象地图变化的失效传播见 `references/08-planning-recovery-runtime.md`。

## Runtime Lifecycle

高层生命周期：

```text
Execution Boundary Kernel（09）
-> Planning Intent routing（07）
-> Load .plan Bootstrap Context（按需）
-> Discovery / Planning Conversation（00 + 07）
-> Project Current State Gate（07）
-> Planning Context COMPLETE（07）
-> Planning Document Mode（07 + 10）
-> Planning Handoff
```

进入 Planning Document Mode 的最低条件：

- Planning Context 状态为 COMPLETE。
- Planning Completion Gate 已通过。
- Project Current State Gate 已通过。
- 高风险项已确认或已登记为待确认项。

Planning Conversation 行为、Discovery、用户态回复、Exploration Guard、Internal Complexity、User Context Gate 和 Conversation Continuity 的完整规则见 `references/07-planning-conversation-runtime.md`。

Planning Document Mode 的逐文档生成前确认、生成后解释、用户确认和状态回写规则见 `references/10-planning-document-interaction-runtime.md`。

## Document And Governance Boundaries

- 文档生成必须遵循 `references/03-planning-doc-responsibility.md`、`references/04-planning-format-spec.md`、`references/05-planning-priority-system.md` 和 `references/06-planning-capability-governance.md` 定义的责任边界、格式、优先级、能力治理和门禁。
- 使用 `references/02-planning-change-levels.md`，由 Planning Runtime 内部评估变更影响范围，用于决定 Planning Conversation 的探索深度。
- 涉及外部能力、SDK、OpenAPI、MCP、AI 提供方、基础设施依赖或人工能力时，按 `references/06-planning-capability-governance.md` 执行。
- 13 按 `references/10-planning-document-interaction-runtime.md` 完成确认后，14 和 15 作为执行记录框架与验收框架自动派生；它们只预置待填写事实位置，不填写任何实际执行、验证、验收、真实环境或发布结论。
- `11-测试方案与验收用例.md` 只定义测试设计：按什么业务顺序证明什么、测试类型、自动化等级、真实环境要求和预期证明结果。
- 规划文档不得定义测试代码、测试命令、fixture 脚本、测试执行调度、失败重试命令、实际执行状态、实际证据内容或实际测试结果。

## Runtime Evidence Boundary

Skill Runtime State 只用于当前状态、当前阶段、当前恢复点。

Project Runtime Evidence 只用于事件记录、决策记录和审计记录；默认不加载。

Planning Runtime Evidence 默认写入：

```text
docs/计划安排/<第X期>/planning-runtime/
```

边界：

- Project Runtime Evidence 不是 Runtime State。
- Project Runtime Evidence 不是 SoT。
- Project Runtime Evidence 不是 Planning Context。
- Project Runtime Evidence 不是 Handoff Package。
- Project Runtime Evidence 不是 Capability Registry。
- Project Runtime Evidence 不是 Acceptance。
- Project Runtime Evidence 不是 Runtime Recovery Source。
- 本 skill 只定义并写入 `planning-runtime/`。
- 本 skill 不定义其他 skill 的运行时目录、日志结构、证据保存位置或实际回写机制。

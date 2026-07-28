---
name: planning-layer-runtime
description: 交互式规划层运行时。用于读取目标项目当前基线、开展规划访谈、创建 Planning Context，创建、更新、审查和修复目标项目正式规划目录下的开发规划文档，以及在规划、执行、测试或验收阶段对新增需求、规划遗漏、设计漂移和变更回流进行范围准入、精确失效传播、增量任务合同与增量 Handoff。覆盖完整一期从当前事实、00–13、Planning Execution Baseline、14/15 框架、执行交接，到实际发布后项目基线更新和期次关闭的规划合同；不能填写测试代码、命令、执行状态、实际测试结果、验收或发布事实。
---

# 规划层运行时（Planning Layer Runtime）

当用户开始开发规划、要求创建规划文档，或提供自然语言的规划意图时，使用本 skill。

本文件只维护 Planning Layer Runtime 的入口、路由和边界。具体运行规则、治理细节和交互生命周期由 `references/` 下对应文件维护。

## Reference 路由

只读取当前任务需要的文件：

- `references/00-planning-user-discovery.md`：用户发现访谈、业务事实发现、专业词翻译和 Discovery Sufficiency Gate。
- `references/01-planning-core-rules.md`：规划层核心约束、完整一期事实链、Planning Execution Baseline 与 Change Set 唯一承载边界、项目当前基线与前端体验事实、期次关闭、Planning 追踪 ID 与实现命名隔离。
- `references/02-planning-change-levels.md`：变更影响分级、期内范围扩展准入、多 Change Set 生命周期、冻结基线后的增量执行选择与 carried-forward pending 任务保护。
- `references/03-planning-doc-responsibility.md`：文档清单、职责、上游 SoT、下游输出和禁止内容。
- `references/04-planning-format-spec.md`：AI Runtime 文件位置、ARCH 实现承接策略、TASK 命名与实现参数状态、`current-interaction.yaml`、ID、引用和验收结构。
- `references/05-planning-priority-system.md`：规划优先级、严重性、发布阻塞与下游验证门禁语义。
- `references/06-planning-capability-governance.md`：外部能力、SDK、OpenAPI、MCP、AI 提供方、官方 SoT、证据门禁与 Runtime 门禁治理。
- `references/07-planning-conversation-runtime.md`：Planning Conversation 行为运行层；维护完整一期生命周期、三个变更门禁编排、Planning Execution Baseline 冻结、Implementation Naming / Contract Completeness Gate、增量 Handoff 完整性、前端体验绑定和期次关闭。
- `references/08-planning-recovery-runtime.md`：上下文压缩与中断恢复、Change Triage 后的精确 Planning Recovery、失效传播、恢复门禁、Runtime Audit 日志与用户隔离。
- `references/09-execution-intent-guard.md`：Execution Boundary Kernel。所有输入的 execution intent 判定、阻断结果和语义转向规则的唯一事实来源。
- `references/10-planning-document-interaction-runtime.md`：Planning Document Mode 的用户反馈事务、逐文档交互、13 开发前准备总结、最终人话总结确认和状态回写规则。

## Project Path Binding

首次进入目标项目时，先根据仓库现有约定和正式文档位置绑定本项目路径，不得把本 Skill 中的占位符当作固定目录：

```yaml
planning_root: <项目正式规划根目录>
phase_planning_directory: <当前规划期次或工作包目录>
phase_planning_runtime_directory: <phase_planning_directory>/planning-runtime
project_current_baseline_path: <项目当前事实基线文件>
```

规则：

- 优先复用目标项目已有规划目录、期次组织方式和当前事实文件。
- 若项目尚无对应位置，只在本次职责确实需要时创建最小项目级路径，并将真实路径写入 `.runtime/planning-layer-runtime/project-profile.yaml` 或当前 Planning Context。
- 路径选择必须来自目标项目事实，不得默认使用本 Skill 来源项目的目录、期次名称或文档位置。
- `<planning_root>`、`<phase_planning_directory>`、`<phase_planning_runtime_directory>` 与 `<project_current_baseline_path>` 仅是静态规则中的语义占位符；写入项目前必须解析为真实路径。
- 目标位置唯一且可从仓库事实确认时直接绑定；存在多个候选、缺少写入权限或会改变已有 SoT 归属时，停止并请求用户确认。
- 路径绑定只改变产物落点，不改变 Planning Context、Document Assembly、Handoff、Gate、确认与恢复流程。

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

`.runtime/planning-layer-runtime/` 是项目级规划启动上下文。

它用于在规划访谈开始前理解当前用户、稳定项目身份、规划偏好和上下文入口。

结构：

```text
.runtime/planning-layer-runtime/
  user-profile.yaml
  environment-profile.yaml
  project-profile.yaml
  context-index.yaml（仅在存在多个稳定入口时按需创建）
```

边界：

- 只读取当前轮需要的文件。
- 如果 `.runtime/planning-layer-runtime/` 不存在，只在当前职责真实需要时直接创建对应项目文件；不得一次性创建完整目录树。
- 每个文件只写最小字段，不写示例或长解释。
- 不要把整个 `.runtime/planning-layer-runtime/` 一次性注入上下文。
- `.runtime/planning-layer-runtime/` 只用于访谈策略、上下文入口和启动理解。
- `.runtime/planning-layer-runtime/` 不是 SoT，不是 Planning Context，不是 Handoff Package，不是 Capability Registry，也不是 Recovery Source。
- `.runtime/planning-layer-runtime/` 不保存期次需求、正式 SoT、完整聊天记录、完整用户输入、完整 AI 输出、决策快照、运行时事件、审计日志或 long/testing 执行结果。
- `README.md` 不是必建文件；只有确实需要向人说明本地边界时才按需创建。
- `user-profile.yaml` 是长期稳定用户交互倾向和规划协作偏好的唯一来源。
- `environment-profile.yaml` 存放后续 Planning 需要复用的稳定项目与开发环境事实，不得保存任何凭证。
- `project-profile.yaml` 只存放项目身份、稳定项目描述和项目当前基线文件路径。
- `context-index.yaml` 只在确有多个稳定上下文入口时创建，并且只存放入口路径。

`.runtime/planning-layer-runtime/project-profile.yaml` 最小字段：

```yaml
project_name:
project_type:
project_current_baseline_path:
```

禁止把实际项目进度、当前流程、生产状态、验收状态、已开发未发布内容或期次计划事实写入 `.runtime/planning-layer-runtime/project-profile.yaml`。

`.runtime/planning-layer-runtime/user-profile.yaml` 只保存反复体现、对后续 Planning 有长期价值的交互和协作偏好；禁止保存完整聊天、原始消息、单次情绪、临时抱怨、本期需求、业务规则、文档内容、心理画像，或未经用户确认的身份、项目角色、职位与决策权推断。

`.runtime/planning-layer-runtime/` 中包含本地用户或电脑环境信息的文件默认视为本地启动上下文。创建或更新前必须检查项目已有忽略与版本管理策略；没有明确版本管理要求时应建议加入 `.gitignore`，但不得未经判断改变已有策略。

## Project Current Baseline

唯一项目级当前事实文件：

```text
<project_current_baseline_path>
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
-> Load .runtime/planning-layer-runtime Bootstrap Context（按需）
-> Discovery / Planning Conversation（00 + 07）
-> Project Current State Gate（07）
-> 确认目标、范围与成果用途
-> 形成 execution_handoff_decision 候选
-> 在本期 current-interaction.yaml 持久化最小恢复镜像与确认目标
-> 用户确认后在 Planning Context 与恢复镜像中同步 decision_status: confirmed
-> Planning Context COMPLETE（07）
-> 根据 execution_handoff_decision 生成 Document Assembly Plan
-> 在本期 current-interaction.yaml 同步最小 document_assembly 进度
-> Planning Document Mode（07 + 10）
-> 实际装配文档生成并确认

requires_execution_handoff: true
  -> 13 通过 Task Contract Gate
  -> 13 通过 Implementation Naming Gate
  -> 13 通过 Implementation Contract Completeness Gate
  -> 用户确认 13
  -> 在 13 中冻结 Planning Execution Baseline
  -> 自动派生 14/15 框架
  -> Execution and Acceptance Framework Derivation Gate

requires_execution_handoff: false
  -> 不生成 13/14/15

-> 汇总实际 assembled_documents
-> 基于真实路径生成 handoff_role_mapping
-> 校验 Handoff 分支与 Planning Context 一致

requires_execution_handoff: true
  -> 准备 execution_ready Handoff

requires_execution_handoff: false
  -> 准备 planning_only Handoff

-> planning_status: awaiting_final_summary_confirmation
-> 持久化 final_summary_confirmation 交互目标（10）
-> 本期最终人话总结（10）
-> 用户最后一次整体确认
-> Interaction Preference Consolidation
-> Planning Handoff Complete
-> PLANNING_COMPLETE

-> 后续执行 / 测试 / 验收发现问题时先做 Execution/Test Change Triage Gate（07）
-> 仅 planning_gap、requirement_change 或真正改变设计合同的 design_drift 进入 Planning Recovery（08）
-> 冻结基线后只通过 Change Set 修订受影响 SoT、TEST、TASK、14/15 空白框架与 Handoff
-> 未受影响和已完成事实保持不变
-> 实际验收与发布由后续承接方填写
-> 实际发布确认后才更新 PROJECT-CURRENT-BASELINE
-> 更新当前前端体验事实并关闭本期；关闭后的 00–15 历史只读
```

进入 Planning Document Mode 的最低条件：

- Planning Context 状态为 COMPLETE。
- Planning Completion Gate 已通过。
- Project Current State Gate 已通过。
- 高风险项已确认或已登记为待确认项。

Planning Conversation 行为、Discovery、用户态回复、Exploration Guard、Internal Complexity、User Context Gate 和 Conversation Continuity 的完整规则见 `references/07-planning-conversation-runtime.md`。

Planning Document Mode 的逐文档生成前确认、生成后解释、用户确认和状态回写规则见 `references/10-planning-document-interaction-runtime.md`。

`Planning Context COMPLETE`、正式文档生成完毕、13 已确认或 14/15 框架派生完成，都不等于 Planning 已真正结束。是否需要执行交接、两条条件式结束链路与最终整体确认以 `references/07-planning-conversation-runtime.md`、`references/10-planning-document-interaction-runtime.md` 和 `references/04-planning-format-spec.md` 为准。

## Document And Governance Boundaries

- 文档生成必须遵循 `references/03-planning-doc-responsibility.md`、`references/04-planning-format-spec.md`、`references/05-planning-priority-system.md` 和 `references/06-planning-capability-governance.md` 定义的责任边界、格式、优先级、能力治理和门禁。
- 使用 `references/02-planning-change-levels.md`，由 Planning Runtime 内部评估变更影响范围，用于决定 Planning Conversation 的探索深度。
- 涉及外部能力、SDK、OpenAPI、MCP、AI 提供方、基础设施依赖或人工能力时，按 `references/06-planning-capability-governance.md` 执行。
- 实际装配 13 时，13 按 `references/10-planning-document-interaction-runtime.md` 完成确认后，14 和 15 作为执行记录框架与验收框架自动派生；它们只预置待填写事实位置，不填写任何实际执行、验证、验收、真实环境或发布结论。
- 13 首次确认后冻结 `planning_execution_baseline`；Handoff 已生成、14/15 已派生或任一 TASK 已开始时同样视为已经冻结。冻结后的变更只能按 `references/02-planning-change-levels.md` 形成 Change Set，不得静默覆盖既有规划基线。
- Planning Execution Baseline 完整正文只由 13 承载；Change Set 完整历史只以 Decision Snapshot 追加到本期既有 `planning-runtime/decision-log.md`。`current-interaction.yaml`、14、15 和 Handoff 只保存或引用必要 revision。
- 执行、测试或验收发现的问题必须先按 `references/07-planning-conversation-runtime.md` 分类；只有需要规划回流的分类才调用 `references/08-planning-recovery-runtime.md`。
- 增量修订只重建 Recovery Output 和 Change Set 明确列出的受影响文档、TEST、TASK 与尚未填写真实事实的框架占位；完整 13 不等于全部待执行队列，但原基线中尚未完成且仍有效的 TASK 必须继续进入增量 Handoff。
- `11-测试方案与验收用例.md` 只定义测试设计：按什么业务顺序证明什么、测试类型、自动化等级、真实环境要求和预期证明结果。
- 规划文档不得定义测试代码、测试命令、fixture 脚本、测试执行调度、失败重试命令、实际执行状态、实际证据内容或实际测试结果。

## Static Skill And Project Runtime Boundary

`skills/planning-layer-runtime/` 只能保存 `SKILL.md`、`agents/openai.yaml`、静态路由、静态格式规范、静态职责说明和静态行为规则。

- 禁止保存运行时实例或运行时空文件。
- 禁止保存用户画像、环境档案、当前交互、Event、Decision、Audit、Summary 的复制源文件。
- 禁止保存任何 `runtime-*` 项目文件，以及项目、用户、电脑、环境、期次、反馈或进度数据。
- Skill 只在 references 的代码块中定义项目运行文件何时创建、写到哪里、包含哪些字段以及如何更新和恢复。
- 运行时必须读取静态字段规范，并在项目合法目录直接创建所需文件；禁止从 Skill 目录复制文件后填写。

期次级短期状态与证据按需写入：

```text
<phase_planning_runtime_directory>/
```

其中 `current-interaction.yaml` 保存当前阶段、`execution_handoff_decision` 的最小恢复镜像、最小文档装配进度、当前交互和最近一条反馈，是上下文压缩与工具中断后的短期恢复来源；Planning Context 仍是执行交接分支的权威语义来源。所有期次级运行数据只能写入当前项目对应的本期目录，不得写入 Skill、`.runtime/planning-layer-runtime/`、项目根目录或其他期次目录。

Project Runtime Evidence 只用于事件记录、决策记录和审计记录；默认不加载。

Planning Runtime Evidence 的唯一合法目录：

```text
<phase_planning_runtime_directory>/
```

边界：

- `current-interaction.yaml` 是短期 Runtime State，不是 Project Runtime Evidence。
- Project Runtime Evidence 不是 Runtime State。
- Project Runtime Evidence 不是 SoT。
- Project Runtime Evidence 不是 Planning Context。
- Project Runtime Evidence 不是 Handoff Package。
- Project Runtime Evidence 不是 Capability Registry。
- Project Runtime Evidence 不是 Acceptance。
- Project Runtime Evidence 不是 Runtime Recovery Source。
- 本 skill 只定义并写入 `planning-runtime/`。
- 本 skill 不定义其他 skill 的运行时目录、日志结构、证据保存位置或实际回写机制。

## Local Privacy And Packaging Boundary

- `.runtime/planning-layer-runtime/` 与 `<phase_planning_runtime_directory>/` 默认按项目本地私有数据处理。
- Skill 打包、分享或上传时，只包含 `skills/planning-layer-runtime/` 的静态文件；禁止携带项目 `.runtime/planning-layer-runtime/` 或任何期次 `planning-runtime/`。
- 首次创建本地运行文件前，检查项目已有版本控制和忽略策略。未得到用户明确要求时，用户倾向、电脑环境和原始反馈不得进入公开仓库。
- 优先遵守项目已有团队协作策略；确需共享时，只共享脱敏后的稳定项目信息。
- `environment-profile.yaml` 禁止保存 Token、密码、私钥、Cookie、主机账号、可识别个人的完整 Home 路径、内网 IP、机器序列号、完整敏感环境变量或可直接调用生产服务的配置。

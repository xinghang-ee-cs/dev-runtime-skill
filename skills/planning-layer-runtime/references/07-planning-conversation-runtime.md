# Planning Conversation Runtime

## 1. 运行模式（Runtime Modes）

Planning Layer Runtime 支持两种模式：

| 模式 | 输入 | 输出 | 禁止 |
| --- | --- | --- | --- |
| Planning Conversation Mode | 自然语言、模糊需求、阶段规划启动语句 | Planning Context | 直接生成最终文档 |
| Planning Document Mode | 完整 Planning Context | 单份正式 SoT 文档草案；13 确认后可派生 14/15 框架对 | 跳过文档职责边界、在 13 确认前一次生成多份文档 |

进入规则：

- 用户以自然语言启动规划时，默认进入 Planning Conversation Mode。
- Planning Context 完整后，才允许进入 Planning Document Mode。
- 用户直接要求生成文档但上下文不完整时，先进入 Planning Conversation Mode。

### 1.1 Planning Intent Subtype and Planning Exploration Guard

`references/09-execution-intent-guard.md` 只负责将输入判定为 `planning_intent` 或 `execution_intent`。当结果为 `planning_intent` 时，本运行时必须在 Planning Layer 内部使用以下子类路由；这不改变 Execution Boundary Kernel：

| 子类 | 适用情形 | 首要动作 |
| --- | --- | --- |
| `discovery_start` | 用户刚提出“创建计划”“开始规划”“梳理流程”“做一期规划”等自然语言方向 | 进入业务探索 |
| `context_reconstruction` | 需要恢复或核实已有项目、规划上下文或当前事实 | 重建并核实当前上下文 |
| `document_generation` | 用户要求生成文档，且完整 Planning Context 与既有 Gate 已实际满足 | 进入 Planning Document Mode |
| `document_review` | 用户要求审查或修订已有规划内容 | 读取并审查对应内容 |

规则：

- 自然语言“创建计划”“开始规划”“梳理流程”“做一期规划”默认是 `discovery_start`，不是 `document_generation`。
- 只有完整 Planning Context、Project Current State Gate、Discovery Sufficiency Gate 与 Planning Completion Gate 已实际满足时，才允许进入 `document_generation`。
- `context_reconstruction` 与 `document_review` 不得假设当前业务事实仍然有效；发现下列关键事实缺失或冲突时，必须回到 `discovery_start`。

Planning Exploration Guard 在每个 `discovery_start` 首轮，以及每次准备从探索转向收敛前建立完整不确定性地图；最低确认范围按 1.2 Exploration Scope Adaptation Rule 裁剪：

```text
当前业务流程
当前系统状态
当前用户角色/协作视角
当前痛点
本期真实目标
涉及角色
数据来源
现有流程是否已经运行
```

当前内部复杂度判断适用范围内的任一项仍未知时：

- 必须保持 Planning Conversation Mode，继续由 `00-planning-user-discovery.md` 进行发现。
- 允许复述当前理解、说明未知项、提出一个探索问题，或把推测明确标为“暂时假设”。
- 禁止生成正式规划文档、命名第 X 期、定义期次名称或本期目标标题、给出完整范围收口、列出模块/文档/功能范围，或创建看似正式的规划入口说明。
- 不得把用户提到的方向直接改写为已确认的期次主题；它只能是等待核实的业务线索。
- 必须同时遵守 User Context Gate Parallel Discovery Rule、Discovery Priority Rule 和 Solution Deferral Rule。

仅当当前内部复杂度判断适用范围内的事实均已通过用户确认、项目当前事实核实，或明确为“不涉及/不存在”的已确认事实时，才允许结束探索保护。探索保护通过后仍必须继续执行既有 Discovery Sufficiency Gate 与 Planning Completion Gate；它不新增 Runtime、日志、SoT、恢复来源或独立状态机。

### 1.2 Exploration Scope Adaptation Rule

Planning Exploration Guard 的最低确认范围必须根据变更规模调整。Guard 的目的不是收集所有信息，而是消除会改变规划方向的关键不确定性。

判断原则：

- 简单需求不应触发完整业务探索。
- 复杂业务变化不得因为已有部分上下文而跳过探索。
- 若内部复杂度尚未确认，先按当前输入做临时内部判断；一旦发现影响范围扩大，立即提升探索范围。
- 内部复杂度判断沿用 `references/02-planning-change-levels.md` 和 1.3 Internal Complexity Decision Rule，本规则只调整 Planning Conversation 的探索最低范围。

S 级变更目标是确认局部影响。至少确认：

```text
当前行为是什么
用户为什么需要调整
影响哪个范围
验收结果是什么
```

S 级不要求完整业务流程探索，不要求重新访谈全部角色、全部数据来源或整个系统状态；除非局部修改暴露出跨流程、跨角色、数据状态或验收口径风险。

M 级变更目标是确认业务链路影响。需要确认：

```text
当前流程
涉及角色
影响范围
数据变化
验收目标
```

M 级可以聚焦受影响链路，不要求无关业务域的完整探索；但不得跳过会改变流程、角色、数据或验收结论的未知项。

L 级变更目标是完整业务规划。执行完整探索：

```text
当前业务流程
当前系统状态
用户角色
痛点
真实目标
涉及角色
数据来源
已有流程运行状态
旧流程边界
```

L 级不得因用户先给出部分目标、候选模块或已有材料而直接进入范围收口或文档生成。

### 1.3 Internal Complexity Decision Rule

变更复杂度判断属于 Planning Runtime 内部决策。

判断依据：

- 是否影响业务流程。
- 是否新增或修改 FLOW。
- 是否影响角色权限。
- 是否影响数据对象。
- 是否影响状态迁移。
- 是否影响 API 契约。
- 是否影响 UI 主流程。
- 是否涉及外部能力。
- 是否影响测试与验收边界。

规则：

- S/M/L 不向用户展示。
- 不要求用户选择 S/M/L。
- 不要求用户判断需求规模。
- 用户只提供业务事实、当前问题和目标。
- Runtime 根据事实变化动态调整探索深度。
- 初始复杂度判断只是临时内部假设，不是最终结论。
- Discovery 过程中如果发现影响范围扩大，自动提升探索深度。
- 不得因为初始判断为 S 或 M，而跳过后续发现。

## 2. 规划启动上下文加载（Planning Bootstrap Context Load）

### 2.1 Execution Boundary Kernel

每轮用户输入的处理流程：

```text
用户输入
  │
  ▼
Execution Boundary Kernel（09）
  │
  ├── execution_intent → 自然语义转向
  └── planning_intent  → Planning Intent Subtype（本文件 1.1）→ 继续以下流程
```

详细规则见 `references/09-execution-intent-guard.md`。

Planning Conversation Mode 启动前，按需读取 `.runtime/planning-layer-runtime/`。

读取顺序：

```text
.runtime/planning-layer-runtime/user-profile.yaml
→ .runtime/planning-layer-runtime/environment-profile.yaml（当前轮需要时）
→ .runtime/planning-layer-runtime/project-profile.yaml
→ .runtime/planning-layer-runtime/context-index.yaml（存在多个稳定入口且当前轮需要时）
```

规则：

- 只读取当前任务需要的 `.runtime/planning-layer-runtime` 文件。
- 遵守最小上下文原则。
- 如果 `.runtime/planning-layer-runtime/` 不存在，只在当前职责真实需要时，根据 `04-planning-format-spec.md` 的字段规范直接创建对应项目文件；不得从 Skill 复制文件，也不得一次性创建完整目录树。
- `.runtime/planning-layer-runtime` 初始化是内部启动行为；在 Planning Conversation Mode 的首轮用户回复中，不得把已创建的文件、路径或初始化状态作为主体，除非用户明确要求查看它。
- 读取 `.runtime/planning-layer-runtime/` 后，不得跳过 User Discovery Sufficiency Gate。
- `.runtime/planning-layer-runtime` 只用于启动辅助，不是正式业务事实。
- `.runtime/planning-layer-runtime` 不替代 Planning Context。
- `.runtime/planning-layer-runtime/project-profile.yaml` 只允许保存 `project_name`、`project_type`、`project_current_baseline_path`。
- `.runtime/planning-layer-runtime/user-profile.yaml` 是长期交互倾向和规划协作偏好的唯一来源；禁止新增或读取第二个偏好来源。
- `context-index.yaml` 只在确有多个稳定上下文入口时创建；`README.md` 不属于必建文件。
- 首次创建 `.runtime/planning-layer-runtime/` 文件前检查项目版本控制与忽略策略；未获用户明确要求时，用户倾向与电脑环境不得进入公开仓库。
- 正式当前事实只来自 `<project_current_baseline_path>`、发布确认、验收记录、执行记录或用户明确确认。

### 2.2 User Context Gate Parallel Discovery Rule

任何期次启动都必须先检查 User Context Gate，但 User Context Gate 不得成为阻断业务探索的问卷入口。

适用：

- 第一期开启
- 第二期开启
- 后续任意期次开启
- 继续上一期规划
- 二次开发规划
- 新增阶段规划

规则：

- User Context Gate 用于辅助理解沟通方式，不是 Business Discovery 的前置阻塞。
- 不因用户说"开始开发"就直接问范围、角色、权限或验收。
- 不因用户说"第一期/第二期"就直接问完整规划字段。
- 先检查并复用当前使用者上下文。
- 已有高置信用户画像时复用。
- 未知或冲突时，用聊天方式识别；若当前输入已经包含明确业务目标或业务问题，识别过程必须与 Business Discovery 并行推进。
- 如果用户已经通过表达体现业务负责人视角、系统建设目标、当前问题背景或决策范围，不得为了补齐 user-profile 字段强制追问身份。
- 用户角色、职位、决策权允许通过后续对话自然归纳；只有缺失信息会改变规划方向、范围、授权边界或验收结果时，才主动追问。
- 不得首轮要求用户填写身份信息。
- 用户有明显不满、困惑、着急或强烈纠正时，先做情绪承接，再继续首轮推进。

### 2.3 Project Current State Gate

所有期次启动都必须执行 Project Current State Gate；它在进入正式 00 草案或 Planning Document Mode 前必须通过。

流程：

```text
User Context Gate（读取 / 复用 / 自然识别；不阻塞业务探索）
→ Project Current State Gate + Business Discovery（按当前最大不确定性并行推进）
→ Planning Conversation
→ Discovery Sufficiency Gate
→ Planning Completion Gate
→ Planning Document Mode
```

读取：

```text
<project_current_baseline_path>
```

第一期从 0 开始时允许创建该文件，但必须明确：

- 当前没有已发布版本。
- 当前没有既有正式流程。
- 当前没有可继承的生产业务事实。
- 当前初始事实来自用户确认。

后续期或已有项目首次使用本 skill 时必须确认：

- 当前生产中实际运行什么。
- 当前已开发但未发布什么。
- 当前已验收但未发布什么。
- 当前有哪些旧入口、旧对象、旧状态、旧审批或旧流程。
- 本期目标是新增、替换、阻断、迁移还是清理。

Gate 检查项：

```text
project_current_baseline_available
project_current_state_classified
production_state_distinguished_from_delivery_state
existing_legacy_assets_identified_or_explicitly_unknown
phase_change_target_reconciled_with_current_state
```

规则：

- 基线缺失、过期、来源冲突或无法确认时，不得进入 00 正式草案。
- 允许先通过自然对话重建基线，但必须区分已确认事实、待核实事实和未知事实。
- 不得把上一期 00–13 的计划内容当成当前已实现事实。
- 不得把已验收未发布写成生产已生效。
- 不得用已有旧代码绕过业务规划结论。

## 3. 对话生命周期（Conversation Lifecycle）

### 3.1 对话阶段（Layer 1 可见）

默认阶段：

```text
探索定位（自然理解、关键未知、一个推进问题）
→ 当前状态确认
→ 目标确认
→ 范围确认
→ 业务域确认
→ 当前视角确认
→ 权限确认
→ 数据可见性确认
→ 用户流程确认
→ 功能边界确认
→ 数据模型确认
→ UI确认
→ 接口契约确认
→ 架构确认
→ 外部能力确认
→ 测试方案确认
→ 风险确认
→ 开发任务合同确认
→ 执行与验收框架派生检查
```

规则：

- 允许跳过不涉及阶段。
- 跳过必须说明依据。
- 禁止无依据跳阶段。
- 当前状态、实际流程、用户视角、痛点、真实目标、涉及角色、数据来源或既有流程运行状态尚未确认时，不得推进到范围确认，也不得自行产出期次名称、主题或范围收口。
- 每轮只推进当前必要阶段。
- 每轮优先只问 1 个主问题；同一上下文且用户可轻松一次性回答时，才允许 2 到 3 个问题。
- 问题必须贴近操作、角色、流程和结果。
- 阶段不是问卷；不得要求用户按阶段字段回答。
- 不得为了补齐 Planning Context 模板而主动遍历所有阶段或字段。
- 问题优先级由 Discovery Priority Rule 决定。

### 3.2 用户发现访谈（User Discovery Interview）

当用户从自然语言需求开始时，Planning Conversation Mode 必须按需加载 `00-planning-user-discovery.md`。

规则：

- User Discovery 的访谈方法、业务事实发现、专业词翻译和 Discovery Sufficiency Gate 详细规则由 `00` 负责。
- `07` 只负责在正确阶段调用该 Runtime，并接收其输出。
- Discovery Sufficiency Gate 通过前，不得进入 Planning Document Mode。
- User Discovery Runtime 必须读取或检查 User Context Gate；若用户输入已包含明确业务目标或业务问题，不得等待 User Context Gate 字段补齐后才开始业务发现。

### 3.3 Discovery Priority Rule

Discovery 阶段的目标不是快速补齐 Planning Context 字段，而是优先理解用户当前表达中的最大业务不确定性。

问题必须来源于：

```text
当前用户提出的问题
当前业务目标
当前阻塞点
当前影响规划方向的不确定因素
```

规则：

- 不得为了填充 Planning Context 模板主动遍历所有字段。
- 不得连续询问角色、权限、数据、状态、模块、页面、接口等字段清单。
- 只有某个缺失信息会改变规划方向、范围、授权边界或验收结果时，才主动追问。
- 当用户已经给出业务问题时，首轮问题应围绕真实流程、当前卡点或结果影响，而不是身份标签或专业字段。
- 每轮只问当前最能改变下一步判断的一个自然问题。

示例：

```text
用户：想优化现有任务处理流程。

正确：现在一次完整任务通常怎么走？

错误：请描述角色、权限、数据模型、状态、接口。
```

### 3.4 Solution Deferral Rule

在 Planning Exploration Guard 生效期间，默认目标是理解问题，而不是设计解决方案。

禁止主动输出：

```text
产品方案列表
模块拆分
功能架构
页面设计
技术方案
系统改造方向
```

除非用户明确要求：

```text
你帮我设计方案
有哪些解决方式
帮我分析技术路线
```

规则：

- Discovery 阶段问题优先于方案。
- AI 可以提出澄清问题，但不得替用户提前决定未来系统形态。
- 用户未要求方案时，用户态回复只做当前理解、未知项和一个关键问题。
- 用户要求方案时，也只能输出候选方案，并明确其依赖哪些尚未确认的业务事实；不得把候选方案写成已确认范围、模块或任务。

## 发现复用规则（Discovery Reuse Rule）

Planning Conversation Runtime 开始前必须优先读取：

```yaml
user_profile
discovered_business_facts
```

若事实已确认，禁止重复提问。

仅允许：

- 补充缺失项
- 确认高风险项
- 解决冲突项
- 补齐 Completion Gate 所需信息

禁止：

- 已经确认"谁在使用"后，再次提问"用户角色是谁"。
- 已经确认"当前工作流程"后，再次提问"用户流程是什么"。

除非：

- 发现冲突
- 信息不足

## 4. 对话轮次输出（Conversation Round Output）

### 4.1 内部状态（不可见）

```text
当前阶段：
已确认：
缺失项：
风险或冲突：
下一步：
```

### 4.2 用户可见回复（Layer 1）

```text
自然理解：
当前未知：
一个推进问题：
```

### 4.3 输出规则

- 内部轮次状态仅用于日志、恢复、上下文管理。
- 用户可见回复才是给用户看的内容。
- 用户态回复必须像正常协作对话。
- Planning Exploration Guard 生效时，用户态回复必须按“自然理解 -> 当前未知 -> 一个推进问题”组织；不得把内部启动、候选范围或文档装配说明当作对话主体。
- 内部轮次状态的字段不能外显。
- 业务建模槽位不能原样外显。
- 情绪承接是用户态回复的一部分，不是可选项。
- 当用户还没有给出明确业务问题时，用户态问题优先确认协作方式，而不是要求用户选择身份分类。
- 当用户已经给出明确业务目标或业务问题时，用户态问题优先确认 Discovery Priority Rule 指向的最大业务不确定性。
- 角色、职位、决策权由 AI 从后续聊天中逐步归纳，不得首轮强行收集。
- 当前情绪只用于本轮承接，不进入 Planning Context，不进入 `.runtime/planning-layer-runtime`，不进入正式 SoT。
- 用户侧不要求按格式回复。
- 问题数量保持最少。
- 优先确认阻塞项。
- 默认只问一个自然问题。
- 只有同一上下文且用户可以轻松一次性回答时，才允许 2 到 3 个问题。
- 不得把 1 到 3 个问题执行成固定三问模板。
- 面向非专业用户时，不使用 RBAC、ABAC、状态机、接口契约、权限矩阵等专业术语。
- 仅在 Planning Conversation Mode 的用户态回复中，不输出 Formal SoT 正文；Planning Document Mode 按第 10 节生成正式文档。
- 不输出代码、shell 命令、文件树、工程搭建步骤或任何执行层内容。
- 在探索保护通过前，不输出期次编号、期次名称、本期目标标题、模块列表、文档列表、功能范围收口或“已补充规划上下文”等文档化结论。
- 在探索保护通过前，不主动输出产品方案列表、模块拆分、功能架构、页面设计、技术方案或系统改造方向，除非用户明确要求方案分析。
- 不得把 Discovery 做成字段补全问卷；不得为了补齐 Planning Context 模板而追问与当前规划方向无关的字段。
- S/M/L 是内部复杂度判断标签，不属于用户交互内容。
- 不得在用户态回复中说“你的需求属于 S 级”“这是一个 M 级变更”“我们按 L 级规划”“请选择 S/M/L”“确认一下本期规模等级”。
- 不得要求用户选择、理解或确认 S/M/L；用户只需要提供业务事实、当前问题和目标。
- 除非用户主动询问变更复杂度分析，否则不向用户展示 S/M/L 判断；即使用户询问，也必须解释为影响范围分析，不要求用户选择等级。

### 4.4 首轮示例

用户：

```text
开始第一期开发
```

如果用户画像未知，合格回复：

```text
我理解你现在是想启动一段新的规划，但还不急着把它写成开发材料。

目前我还不确定你希望我先帮你一起理清业务方向，还是你已经有一套可整理的现成材料。

我先确认一个问题：这次你更希望先从真实使用过程聊起，还是先把已有材料拿出来一起核对？
```

如果用户画像已知为项目负责人，合格回复：

```text
我理解你现在想从把控方向和交付的视角，把要解决的事情先聊清楚。

目前我还不确定现场已经在跑什么流程，以及这次最需要先解决的阻塞点。

我先确认一个问题：现在这件事通常是从谁发起、怎么一路处理到结束的？
```

用户提出模糊流程规划，合格回复：

```text
用户：可以先不急着出报告，优先解决现有任务处理流程。我们来创建一个最新的计划吧，本次计划主要梳理任务流转，包含数据导入、处理记录方式更新两个环节。

AI：我理解你现在不是急着做报告，而是想先把现有任务流程跑顺，并把数据导入和处理记录的结果沉淀下来。

目前我还不确定一次完整任务实际怎么走，数据现在从哪里来，以及处理记录卡在什么地方。

我先确认一个问题：现在一次完整任务，从发起到完成记录，使用人员通常是怎么走的？
```

用户提出检查记录问题，合格回复：

```text
用户：我想优化检查记录。

AI：我理解你想解决的是检查过程中的记录问题，先把现场记录这件事变得更顺。

目前我还不知道主要卡在哪里，也不知道是填写、查找、统计，还是后续整改跟踪最影响使用。

我先确认一个问题：现在现场人员记录检查结果时，最麻烦的是填写、查找、统计，还是后续整改跟踪？
```

用户提出局部优化，合格回复：

```text
用户：任务列表增加搜索条件。

AI：我理解这是已有任务列表里的局部体验优化，重点是把列表查找变得更准确，不需要重新梳理整条业务流程。

目前我还不确定现在列表有哪些搜索能力，以及新增搜索主要解决什么查找问题。

我先确认一个问题：现在使用人员最难找到的是哪类任务？
```

如果用户明显不满，合格回复：

```text
对，不能一上来就把方向写成计划标题或范围，那样会跳过实际情况。我先重新接住：你现在是想先把真实流程理清楚，再决定怎么规划。

目前我还不知道最影响你推进的是哪一段实际操作。

我先确认一个问题：你最希望先理顺的，是现场执行、数据导入，还是检查记录这一段为什么会卡住？
```

如果用户要求直接写代码，按 Execution Boundary Kernel（09）进行语义转向，不暴露系统机制。

## 5. 业务语言输入处理

用户可使用口语化描述。

规则：

- 业务事实发现和专业词翻译由 `00-planning-user-discovery.md` 负责。
- `07` 只接收已发现事实，并把可用事实补入 Planning Context。
- 正式 SoT 文档仍必须使用专业表达和来源引用。

### 5.1 UI/交互前置确认

当需求涉及用户界面、页面、表单、列表、地图、工作台、移动端、平台容器或桌面端操作时，必须确认 UI/交互高风险项。

UI 高风险项：

```text
核心页面布局
操作路径
跳转关系
状态反馈
异常态
空状态
加载态
移动/桌面适配
视觉风格
```

未确认时：

- 不允许生成依赖该 UI 的开发任务。
- 允许生成不依赖该 UI 的上游规划内容。
- 必须记录为待确认项和阻塞范围。

规则：

- UI 访谈方法沿用 `00-planning-user-discovery.md`。
- `07` 只记录 UI 高风险项、待确认项和阻塞范围。

### 5.2 03/04/05 逐文档确认重点

以下问题只作为内部确认方向，不得把完整 checklist 扔给用户；默认每轮只问一个最关键问题。

03 生成前使用业务语言确认：

- 用户从哪里进入？
- 什么条件下能做下一步？
- 用户遇到失败时会看到什么、能怎么办？
- 取消或失败后回哪里？
- 哪些旧入口用户仍可能访问？

04 生成前使用业务语言确认：

- 这条流程必须依赖哪些能力才能走通？
- 哪些能力只是协作，不应承担主责任？
- 哪些旧能力绝不能再参与？
- 缺少哪个能力时必须阻断？

05 生成前使用业务语言确认：

- 本期最优先要先看到哪些页面？
- 使用什么端、什么语言、什么视觉气质？
- 是否已有品牌、Figma、截图或参考图？
- 哪些页面或异常状态必须通过图明确表达？
- 哪些局部变化需要单独做模块图？
- 哪些交互现有页面图无法表达，需要后续补 UX 图？

05 设计确认记录复用既有 `UI_CONFIRMATION` 事件，不新增设计日志、出图日志或 UX Runtime。

### 5.3 06/07/08 逐文档确认重点

以下问题只作为内部确认方向，不得把完整 checklist 扔给用户；默认每轮只问一个最关键问题。

06 生成前使用业务语言确认：

- 哪些业务事实证明用户可以继续下一步？
- 什么事件会改变业务事实或状态？
- 哪些状态需要长期保存，哪些只是页面上的临时状态？
- 旧审批、旧申请或旧状态最多能做什么，绝不能变成什么新状态？
- 测试、预发布、生产等数据域是否必须隔离？

07 生成前使用业务语言确认：

- 前端需要读取什么，提交什么？
- 后端成功后必须返回什么，失败时必须拒绝什么？
- 哪些写操作可能重复点或多人同时提交？
- 哪些旧审批字段、旧状态或旧接口必须被挡在新流程外？
- 页面刷新后需要依赖哪个最新业务事实或决策视图？

08 生成前使用业务语言确认：

- 谁能对哪个资源做这个动作？
- 允许范围是自己的任务、负责区域、管理项目、当前租户还是历史只读？
- 哪些情况是未登录、无资格、越界、状态不满足、旧流程来源、数据域错误或外部能力失败？
- 工作人员只能协助诊断和恢复到哪一步，不能替谁完成业务动作？
- 历史记录最多允许谁以只读方式查看？

### 5.4 09/10/11 逐文档确认重点

以下问题只作为内部确认方向，不得把完整 checklist 扔给用户；默认每轮只问一个最关键问题。

09 生成前使用业务语言确认：

- 现有系统哪些能力可以保留？
- 哪些旧流程或旧逻辑绝不能再参与？
- 这次变化要从哪里切换到新流程？
- 出现问题时应该回退到什么可接受状态？

10 生成前使用业务语言确认：

- 这项能力是否真的必须依赖外部服务？
- 候选方案有哪些？
- 选择时最在意兼容性、成本、稳定性、国内可用性还是合规？
- 能力不可用会阻断哪件核心业务？

11 生成前使用业务语言确认：

- 用户必须按怎样的顺序完成这条业务？
- 哪些错误、越权、旧路径或异常绝不能通过？
- 哪些结果必须自动化证明？
- 哪些必须在真机或真实环境确认？

## 6. 风险确认模式

触发条件：

- 命中 `01-planning-core-rules.md#4-高风险不确定项`。
- 命中 `06-planning-capability-governance.md` 的 Capability Governance Runtime。
- 当前阶段存在权限、删除、数据归属、状态流、接口、UI/交互、审计、租户、外部能力、安全、合规或计费不确定项。

输出：

```text
当前理解：
缺失信息：
风险影响：
待确认问题：
处理状态：
```

规则：

- 高风险项不得静默假设。
- 必须追问至用户确认。
- 无法确认时，记录为待确认项。

## 7. 上下文完整性检查

每轮阶段结束时检查：

- 缺失实体
- 缺失角色
- 缺失权限
- 缺失状态
- 缺失 UI/交互确认
- 缺失测试
- 缺失验收

发现缺失时：

```text
缺失项：
影响范围：
建议补问：
```

## 8. 冲突检测

触发条件：

- 前后描述冲突
- 权限冲突
- 状态冲突
- 范围冲突
- Capability 冲突

触发后暂停，输出：

```text
当前理解：
冲突点：
影响范围：
建议确认项：
```

## 9. Planning Context

Conversation Mode 最终输出 Planning Context：

```text
当前项目状态：
目标：
范围：
角色：
权限：
数据：
流程：
FLOW：
旧流程/历史对象边界：
功能：
UI/交互：
能力：
测试：
风险：
验收：
待确认项：
涉及文档：
执行交接判断：
  execution_handoff_decision:
    requires_execution_handoff:
    handoff_type:
    decision_basis:
    decision_source:
    decision_status:
```

规则：

- Planning Context 是 Document Mode 的输入。
- Planning Context 不替代正式 SoT 文档。
- 待确认项必须保留来源和影响范围。
- 当前项目状态必须区分生产当前、已开发未发布、已验收未发布和计划目标。
- FLOW 只记录 Planning Conversation 已确认或待确认的业务旅程，不替代 01 的正式 Flow Contract。
- `execution_handoff_decision` 属于现有 Planning Context，不新增第二套 Planning Context、Runtime 文件、日志或状态机。
- `requires_execution_handoff` 只允许 `true` 或 `false`；`handoff_type` 必须分别对应 `execution_ready` 或 `planning_only`。
- `decision_source` 只记录实际来源：`user_confirmation`、`confirmed_planning_context`、`document_assembly_requirement`；可按实际情况记录一项或多项。
- `decision_status` 只允许 `candidate` 或 `confirmed`。进入 Planning Document Mode 前必须为 `confirmed`。
- `decision_basis` 必须说明为什么存在或不存在后续工程执行任务，不得只记录 S/M/L 或文档数量。
- 在向用户发出执行交接分支确认问题前，必须先按 `04` 在本期 `current-interaction.yaml` 写入候选镜像，并按 `10` 绑定 `execution_handoff_decision` 交互目标；用户反馈记录、校验和应用完成后，再同步写入 `decision_status: confirmed`。
- 如果本期目录尚未合法确定，保持 Planning Conversation，不得把候选或已确认分支暂存到 Skill、`.runtime/planning-layer-runtime/`、项目根目录或其他期次目录。
- 现有 Document Assembly Plan 必须同步保存同一份 `execution_handoff_decision` 字段和值；Planning Context 是权威来源，Document Assembly Plan 不得独立改写或形成第二个分支结论。
- 当前仍无法判断是否需要工程执行时，Planning Context 必须保持 `INCOMPLETE`，不得生成 Document Assembly Plan 或进入 Planning Document Mode。

### 9.1 Planning Handoff Package

Planning Context 状态为 `COMPLETE` 后，只能形成：

- 文档装配计划。
- 涉及文档范围。
- 尚待实际生成的职责清单。

此时不得生成正式 `assembled_documents`、正式路径或正式 `handoff_role_mapping`。

Planning Context 标记 `COMPLETE` 前，必须先完成以下唯一顺序：

```text
Planning Conversation 已确认目标、范围与成果用途
-> 形成 execution_handoff_decision 候选
-> 写入本期 current-interaction.yaml 最小恢复镜像
-> 持久化 execution_handoff_confirmation 交互目标
-> 向用户发问并按现有反馈事务记录、校验、应用
-> 在 Planning Context 与恢复镜像同步执行交接判断
-> decision_status: confirmed
-> Planning Context COMPLETE
-> 根据该结论生成 Document Assembly Plan
-> 同步本期 current-interaction.yaml 的最小 document_assembly 状态
-> 进入 Planning Document Mode
```

不得先进入 Planning Document Mode，再根据是否生成了 13、当前文件数量或压缩后的聊天摘要反向猜测分支。

正式 Handoff 的准备与完成链路：

`requires_execution_handoff` 不得只根据 S/M/L 判断。以下任一条件成立时必须为 `true`，且 `handoff_type` 必须为 `execution_ready`：

- 用户明确要求规划完成后执行开发。
- 本期需要新增或修改代码。
- 本期需要新增或修改接口。
- 本期需要新增或修改数据库。
- 本期需要新增或修改正式页面或交互实现。
- 本期需要接入外部能力。
- 本期需要执行数据迁移。
- 本期需要修改部署、配置或发布资产。
- 本期存在必须由后续执行方完成的其他工程任务。
- 本期需要生成 14、15 作为后续执行和验收承载。

只有以下条件全部满足时，才允许 `requires_execution_handoff: false` 且 `handoff_type: planning_only`：

- 本期成果只停留在规划、决策、评审或文档层。
- 当前不产生任何工程执行任务。
- 用户没有要求规划后直接开发。
- 不需要生成开发任务合同。
- 不需要 14、15 承载执行和验收。

禁止出现“需要开发，但因为任务简单所以 `requires_execution_handoff: false`”。

#### execution_handoff_decision 变更

后续用户修改目标或范围并导致分支变化时，必须先按 `10-planning-document-interaction-runtime.md` 记录并应用用户反馈，再回写 Planning Context；失效传播复用 `08-planning-recovery-runtime.md`，不得静默覆盖已确认结论。

`planning_only -> execution_ready`：

```text
记录并应用用户反馈
-> 回写 Planning Context
-> 同步本期 current-interaction.yaml 的 execution_handoff_decision
-> 使旧 Document Assembly Plan、Handoff 与最终总结失效
-> requires_execution_handoff: true
-> handoff_type: execution_ready
-> decision_status: confirmed
-> 重新评估 Document Assembly Plan
-> 装配 11、12、13 及 TASK 所需上游 SoT
-> 13 三个 Gate
-> 13 确认
-> 派生 14/15
-> 重建 assembled_documents、handoff_role_mapping 与 Handoff
```

不得直接把原 `planning_only` Handoff 交给开发执行。

`execution_ready -> planning_only` 只有用户明确取消本期全部工程执行任务时才允许。必须记录并应用反馈、回写 Planning Context、同步本期 `current-interaction.yaml`、使旧 Document Assembly Plan / Handoff / 最终总结失效、重新生成 Document Assembly Plan，并按 `08` 传播原 13/14/15 计划或文档失效；当前 Handoff 不得继续包含这些职责。

#### 分支 A：execution_ready

适用条件：Planning Context 中已确认 `requires_execution_handoff: true` 且 `handoff_type: execution_ready`。Document Assembly Plan 包含 `Development Landing Checklist` 是该结论的结果，不得反向作为猜测分支的依据。

```text
Planning Context COMPLETE
-> 进入 Planning Document Mode
-> 按动态装配规则生成并确认所有实际需要的正式文档
-> 所有被 13 引用的上游 SoT 已生成并确认
-> 12 已确认
-> 生成 13 草案
-> Task Contract Gate
-> Implementation Naming Gate
-> Implementation Contract Completeness Gate
-> 输出 13 人话总结
-> 用户确认 13
-> 回写 13 状态：已确认
-> 自动生成 14、15 框架
-> Execution and Acceptance Framework Derivation Gate 通过
-> 汇总实际已生成的 assembled_documents
-> 基于真实路径生成 handoff_role_mapping
-> 生成包含 execution_constraints 的 execution_ready Handoff Package（prepared）
-> planning_status: awaiting_final_summary_confirmation
-> 持久化 final_summary_confirmation active_interaction
-> 按 10 输出本期最终人话总结
-> 用户完成最后一次整体确认
-> 记录并应用 final_summary 确认反馈
-> Interaction Preference Consolidation 完成
-> 清理 current-interaction 中的待处理原文
-> Planning Handoff Complete
-> 追加 PLANNING_COMPLETE
```

本分支必须满足：13 已确认；14、15 已派生；三个 13 Gate 已通过；Handoff 包含 `execution_constraints`；P0 TASK 不存在 `blocking_open`。

#### 分支 B：planning_only

适用条件：Planning Context 中已确认 `requires_execution_handoff: false` 且 `handoff_type: planning_only`；本期只进行需求、流程、规则、UI、架构、能力选型、风险或其他规划确认，当前没有需要交给执行层的开发任务合同。

```text
Planning Context COMPLETE
-> 进入 Planning Document Mode
-> 按动态装配规则生成并确认所有实际需要的正式文档
-> 所有实际装配文档均已确认
-> 汇总实际 assembled_documents
-> 基于真实路径生成 handoff_role_mapping
-> Handoff 只包含本期真实存在且适用的职责
-> 生成 planning_only Handoff Package（prepared）
-> planning_status: awaiting_final_summary_confirmation
-> 持久化 final_summary_confirmation active_interaction
-> 按 10 输出本期最终人话总结
-> 用户完成最后一次整体确认
-> 记录并应用 final_summary 确认反馈
-> Interaction Preference Consolidation 完成
-> 清理 current-interaction 中的待处理原文
-> Planning Handoff Complete
-> 追加 PLANNING_COMPLETE
```

本分支：

- 不要求生成 12，除非本期实际存在风险、依赖或待确认事项需要 12 承载。
- 不生成 13、14、15。
- 不运行 Task Contract Gate、Implementation Naming Gate、Implementation Contract Completeness Gate 或 Execution and Acceptance Framework Derivation Gate。
- Handoff 不包含 `Development Landing Checklist`、`Execution and Integration Record`、`Acceptance and Retrospective Record`，也不包含针对代码执行的 `execution_constraints`。
- 如果本期结论需要交给开发执行，即使变更很小，也必须改走分支 A。

用途：

```text
execution_ready：Planning Runtime → 后续执行承接方 → 后续测试与验收承接方
planning_only：Planning Runtime → 本期规划结论的实际使用方
```

Handoff Package 格式：

```yaml
handoff_type: <planning_only | execution_ready>
requires_execution_handoff: <true | false>

# 仅 requires_execution_handoff: true 时生成
execution_constraints:
  planning_ids_are_trace_only: true
  stable_business_naming_required: true
  phase_based_implementation_names_forbidden: true
  existing_business_domain_preflight_required: true
  new_business_module_requires_architecture_basis: true
  data_domain_isolation_does_not_imply_phase_namespace: true

handoff_role_mapping:
  - role: Capability Governance
    path: <真实已生成路径>
  - role: Test and Acceptance Plan
    path: <真实已生成路径>
  - role: Risk, Dependency, and Open Questions
    path: <真实已生成路径>
  - role: Development Landing Checklist
    path: <真实已生成路径>
  - role: Execution and Integration Record
    path: <真实已生成路径>
    framework_status: planned_and_created
  - role: Acceptance and Retrospective Record
    path: <真实已生成路径>
    framework_status: planned_and_created
```

Handoff Branch Consistency Check 属于既有 Handoff 准备过程，不新增独立 Gate 文件、Runtime 或状态机。正式 Handoff 生成前必须检查：

```text
Planning Context.execution_handoff_decision.requires_execution_handoff
= current-interaction.yaml.execution_handoff_decision.requires_execution_handoff
= Document Assembly Plan.execution_handoff_decision.requires_execution_handoff
= Handoff.requires_execution_handoff

Planning Context.execution_handoff_decision.handoff_type
= current-interaction.yaml.execution_handoff_decision.handoff_type
= Document Assembly Plan.execution_handoff_decision.handoff_type
= Handoff.handoff_type

Planning Context.execution_handoff_decision.decision_status
= current-interaction.yaml.execution_handoff_decision.decision_status
= Document Assembly Plan.execution_handoff_decision.decision_status
= confirmed
```

`execution_ready` 必须同时满足：Planning Context 的决策状态为 `confirmed` 且分支为 `true / execution_ready`；13 已确认；14、15 已派生；三个 13 Gate 已通过；Handoff 包含 `execution_constraints`。

`planning_only` 必须同时满足：Planning Context 的决策状态为 `confirmed` 且分支为 `false / planning_only`；当前不生成或不承接 13、14、15；Handoff 不包含针对代码实现的 `execution_constraints`。

只强制逐项比较 `requires_execution_handoff`、`handoff_type`、`decision_status`；Handoff 不必完整复制 `decision_basis` 与 `decision_source`，但不得语义冲突。任一不一致时，不得生成或确认正式 Handoff，不得进入最终总结；必须回到 Planning Context 与本期恢复镜像修正，再重建 Document Assembly Plan。

规则：

- 使用职责名。
- 不使用固定编号。
- 必须使用实际路径。
- 必须来自本次 Planning Runtime 的正式输出。
- 上述 YAML 只表达允许的职责名；实际 Handoff 只能列出本期真实已生成且适用的 role。
- Handoff 不得包含尚未生成的文档、空占位路径、假设路径或未适用职责。
- `handoff_type: execution_ready` 必须具备 13、14、15、`execution_constraints`，且 Task Contract Gate、Implementation Naming Gate、Implementation Contract Completeness Gate 与 Execution and Acceptance Framework Derivation Gate 均已通过。
- `handoff_type: planning_only` 禁止包含 Development Landing Checklist、Execution and Integration Record、Acceptance and Retrospective Record 以及针对代码实现的 `execution_constraints`；允许包含本期实际生成的 Requirement and Scope、Business Domain、UI/UX Design、Architecture Decision、Capability Governance、Test and Acceptance Plan、Risk, Dependency, and Open Questions 等职责。
- 只有本期存在并已生成 13 时，Handoff 才可包含 `Development Landing Checklist`、`Execution and Integration Record`、`Acceptance and Retrospective Record`。
- 只有 14、15 自动派生完成且 Execution and Acceptance Framework Derivation Gate 通过后，才可以写入 `framework_status: planned_and_created`。
- `Execution and Integration Record.framework_status: planned_and_created` 只表示 14 已由 planning skill 创建执行记录框架和待填写位置，不代表实际执行事实。
- `Acceptance and Retrospective Record.framework_status: planned_and_created` 只表示 15 已由 planning skill 创建验收与复盘框架和待填写位置，不代表实际验收或发布事实。
- Handoff 只定义 planning skill 的输出事实，不定义或修改任何其他 skill 的内部职责、运行方式或文件维护逻辑。
- 后续承接方禁止通过编号猜测文件。
- 未生成 Handoff Package 时，不得进入最终人话总结确认。
- Handoff Package 已生成但最终人话总结尚未确认时，只能标记为 `prepared`，不得标记 Planning Handoff Complete。
- 最终整体确认与 Interaction Preference Consolidation 未完成时，不得将 planning 标记为完成交接。
- 最终总结输出前未持久化 `final_summary_confirmation` 目标时，不得询问用户确认。
- `.runtime/planning-layer-runtime/user-profile.yaml` 整理失败时保持 `awaiting_final_summary_confirmation`，不得静默完成交接。
- `execution_constraints` 仅在 `requires_execution_handoff: true` 时必须随正式 Handoff 输出，且不得复制整份 09 或 13。
- 执行承接方必须把 Planning ID 映射为稳定业务概念，不得把 TASK、FLOW、DOMAIN、API、PERM 等追踪 ID 机械转换为代码、数据库、API 或权限命名。
- 执行前必须优先核实现有稳定业务域能否承接；准备新建期次、Sprint、阶段或版本命名的实现资产时必须停止，并作为架构偏差回写 Planning。
- 新建长期业务模块必须具备 09 的架构依据；数据域隔离不得解释为期次物理命名空间。
- 上述内容只是 Planning 输出的实现边界，不定义或修改后续执行 Skill 的内部运行方式。
- `execution_ready` 只有在三个 13 Gate 均通过、`execution_constraints` 已写入 Handoff、P0 参数不存在 `blocking_open` 时，才允许持久化最终总结确认目标并进入最终总结确认；`planning_only` 按本期实际装配文档与真实路径检查，不要求实现类 Gate 或 `execution_constraints`。

正式文档真实生成后，才能加入：

```yaml
assembled_documents:

- role:
  path:
  reason:
```

示例：

```yaml
assembled_documents:

- role: Capability Governance
  path: <phase_planning_directory>/10-外部能力与集成治理.md
  reason: external_location_sdk

- role: Development Landing Checklist
  path: <phase_planning_directory>/13-开发任务拆分与落地清单.md
  reason: implementation_required
```

Document Assembly 原则：

- Document Assembly 必须按需求特征动态装配。
- 禁止默认生成全量文档。
- 内部影响评估为局部或业务链路影响时，只允许生成必要文档。
- 内部影响评估显示需要完整业务规划时，才允许完整文档链。
- Document Assembly 必须显式判断 `requires_execution_handoff`；该值不得只由 S/M/L 决定。
- Document Assembly Plan 必须直接读取 Planning Context 中 `decision_status: confirmed` 的 `execution_handoff_decision`；不得重新判断或覆盖该结论。
- Document Assembly Plan 中保存的 `execution_handoff_decision` 必须与 Planning Context 逐字段一致；不一致时不得进入 Planning Document Mode。
- Document Assembly Plan 生成后，必须把最小装配进度同步到本期 `current-interaction.yaml.document_assembly`；只记录职责、真实已生成文档、当前文档和装配状态，不复制正式装配结果或 Handoff。
- `requires_execution_handoff: true` 时必须装配 13 并执行 `execution_ready` 分支；`requires_execution_handoff: false` 时不装配 13/14/15 并执行 `planning_only` 分支。
- 只要装配 13，就必须同时装配并确认 11、12，以及所有被 TASK 引用的上游 SoT。
- 15 不得作为可独立装配的孤立文档；只能由已确认的 13 连同 14 一起自动派生。
- `assembled_documents` 只能包含已经真实生成的文档路径，不得伪造路径。
- `handoff_role_mapping` 只能在所有实际装配文档完成后生成，且必须只使用真实路径。
- Planning Context COMPLETE 阶段只能记录装配计划，不得写入正式 `assembled_documents` 或正式 `handoff_role_mapping`。
- 13 已确认、14/15 框架已生成、`assembled_documents` 与 `handoff_role_mapping` 已准备，都不等于 Planning 已真正结束。

低熵原则：

- Handoff 只是 Planning Runtime 的最终输出。
- Handoff 不是新的 Runtime 系统。
- 优先复用现有结构。
- 禁止为了 Runtime 交接新增长期 Runtime 结构。

## 10. Planning Document Mode

进入条件：

- Planning Context 状态为 COMPLETE。
- Planning Context 中 `execution_handoff_decision.decision_status: confirmed`。
- Document Assembly Plan 与已确认的 `requires_execution_handoff`、`handoff_type` 一致。
- Planning Completion Gate 已通过。
- Project Current State Gate 已通过。
- 高风险项已确认或已登记待确认项。

执行规则：

- 根据 `03-planning-doc-responsibility.md` 动态装配文档。
- 涉及 Capability 时，按 `06-planning-capability-governance.md` 执行。
- 涉及 Priority 时，按 `05-planning-priority-system.md` 执行。
- 涉及格式、ID、状态、测试范围或下游验证结果引用时，按 `04-planning-format-spec.md` 执行。
- 正式文档不得口语化。
- 每次只生成一份正式文档草案。例外：13 确认并回写后，14、15 作为框架对自动派生，不触发“每次只能生成一份正式文档”的限制。
- 逐文档生成、用户态总结、确认、状态回写、进入下一份文档的完整生命周期，以 `10-planning-document-interaction-runtime.md` 为唯一规则来源。
- 本文件只保留 Planning Conversation 到 Planning Document Mode 的入口条件和边界，不重复维护逐文档生命周期规则。
- `requires_execution_handoff: true` 时，13 确认并回写 `状态: 已确认` 后，Planning Document Mode 必须自动生成 14 和 15 的正式框架，并运行 Execution and Acceptance Framework Derivation Gate；14、15 只预置后续事实填写位置，不填写任何实际执行、验证、验收、真实环境或发布结论。
- `requires_execution_handoff: false` 时，不生成 13、14、15，不运行实现类 Gate；所有实际装配文档确认后直接准备 `planning_only` Handoff。
- 14、15 不需要分别进行生成前协作确认，也不需要把独立用户确认作为 Planning 完成前提。
- 对应分支的正式 Handoff 已基于真实路径准备后，进入 `planning_status: awaiting_final_summary_confirmation`，并按 `10-planning-document-interaction-runtime.md` 输出最终人话总结。此时只说明 Handoff 已准备及其事实边界，不得宣称 Planning 已完成。

### 10.1 Document Interaction Runtime Handoff

Planning Document Mode 每次只处理一份文档。

完整步骤、生成前协作确认、生成后人话总结、确认绑定、状态回写和进入下一文档规则，不在本文件重复定义。

使用本文件执行 Planning Conversation Runtime 时：

- 进入 Planning Document Mode 前，仍必须先满足本文件的 Planning Completion Gate。
- 进入 Planning Document Mode 后，逐文档生命周期立即切换到 `10-planning-document-interaction-runtime.md`。
- 本文件不维护逐文档生命周期；若出现重复或冲突，以 `10-planning-document-interaction-runtime.md` 为准，并删除重复规则。

### 10.2 Conversation Continuity Gate

每一轮用户态回复结束前，必须执行 Conversation Continuity Gate。

用户态回复必须自然说明：

- 当前已经完成什么。
- 当前还差什么或正在等什么。
- 用户现在最应该做的一件事。
- 用户可以怎么回复。
- 用户回复后 AI 会进入哪一步。

禁止：

- 只以"请确认"结尾。
- 只以"已完成"结尾。
- 只以"等待用户回复"结尾。
- 不说明下一步动作。
- 不说明用户应该确认什么。
- 不说明确认后进入哪里。

## 11. Planning Completion Gate

Planning Conversation Mode 结束前必须执行：

### Discovery Sufficiency Gate

规则：

- 详细检查项和补问规则由 `00-planning-user-discovery.md` 定义。
- `07` 必须在 Planning Completion Gate 前调用该 Gate。
- Gate 未通过时，不得进入 Planning Document Mode。

### Project Current State Check

检查：

```text
project_current_baseline_available
project_current_state_classified
production_state_distinguished_from_delivery_state
existing_legacy_assets_identified_or_explicitly_unknown
phase_change_target_reconciled_with_current_state
```

规则：

- 任一高风险项缺失时，Planning Context = INCOMPLETE。
- 不得进入 Planning Document Mode。
- 不得确认 00、01、02。

### Context Completeness Check

检查：

- 当前项目状态
- 目标
- 范围
- 角色
- 权限
- 数据
- 流程
- FLOW
- 旧流程/历史对象边界
- 功能
- UI/交互
- 能力
- 测试
- 验收
- execution_handoff_decision

是否已确认。

--------------------------------------------------

### High Risk Confirmation Check

检查：

以下高风险项是否已确认：

- 权限
- 删除规则
- 数据归属
- 状态流转
- 接口契约
- 审计规则
- 租户隔离
- 外部能力
- UI/交互高风险项
- 安全
- 合规
- 计费

规则：

必须满足以下条件之一：

- 已确认
- 已登记待确认项

--------------------------------------------------

### Conflict Check

检查：

- 权限冲突
- 状态冲突
- 范围冲突
- Capability 冲突
- 前后描述冲突

规则：

冲突数量必须为：

0

否则：

不得结束规划。

--------------------------------------------------

### Blocking Check

检查：

是否存在：

- 未解决阻塞项
- 未确认关键实体
- 未确认关键角色
- 未确认关键权限
- 未确认当前生产状态与交付状态边界
- 未确认旧入口、旧对象、旧状态、旧审批或旧流程处理方式
- 未确认 UI/交互高风险项且存在 UI 依赖开发任务

存在时：

不得结束规划。

--------------------------------------------------

### Flow Completeness Gate

检查：

- 每个 P0 REQ 已映射到 FLOW。
- 每条 FLOW 有合法入口。
- 每条 FLOW 有必要前置。
- 每条 FLOW 有成功终态。
- 每条 FLOW 有异常或阻断结果。
- 每条 FLOW 有禁止跳步 / 非法路径。
- 每个高风险流程已完成场景复述与用户确认。
- 每条 FLOW 已关联后续 TEST-ID 或明确待测试映射。

不满足时：

```text
Planning Context = INCOMPLETE
```

不得进入 Planning Document Mode。

--------------------------------------------------

### Journey-Object Consistency Gate

检查：

- 每条 FLOW 的前置对象存在。
- 每一步产生或改变的对象存在。
- 每个关键动作都有合法角色资格关系。
- 每个关键终态都有业务事实支撑。
- 每个旧流程或旧对象的处理状态明确。
- 每条反向验收都有对应禁止关系。
- 不存在旧对象驱动目标新流程的隐式关系。

规则：

- 不满足时，02 不得确认。
- 涉及 01 旅程定义缺失时，01 必须回退修正。
- 在 Planning Conversation Mode 中发现缺失时，Planning Context = INCOMPLETE。

--------------------------------------------------

### Scenario Consistency Gate

检查：

- 每个 P0 FLOW 至少有一个 SCN。
- 每个 SCN 只引用既有 FLOW。
- 每个 SCN 的进入条件不弱于 FLOW 前置。
- 每个关键异常有恢复、退出或人工协助路径。
- 03 未新增主业务旅程。
- 03 未改变 FLOW 的合法入口、终态或禁止路径。

规则：

- 不满足时，03 不得确认。
- 涉及 FLOW、对象关系、资格、前置、终态或禁止路径缺失时，必须标记上游 write-back required，并回到 01 或 02 修正。

--------------------------------------------------

### Module Coverage Gate

检查：

- 每个 P0 FLOW 有主模块。
- 每个关键 SCN 有承接模块。
- 每个模块有输入事实、输出能力、非责任和隔离边界。
- 旧流程隔离模块明确保护哪些 FLOW。
- 不存在模块循环依赖或模糊复用。

规则：

- 不满足时，04 不得确认。
- 旧审批、旧入口、旧状态、旧对象不得以“视情况复用”方式存在。

--------------------------------------------------

### UI/UX Design Readiness Gate

检查：

- 每个 P0 SCN 已映射 PAGE。
- 每个 PAGE 有合法进入条件和 UI STATE。
- 每个 UI STATE 有唯一主操作。
- 全局风格提示词已准备。
- P0 页面提示词已准备。
- 关键模块图需求已识别。
- UX 是否可由现有 UI 图覆盖已明确。
- 需要出图但尚未收到资产的项已标记，不得伪造已确认。

规则：

- 不满足时，05 的交互合同不得确认。
- 涉及该页面的 UI 依赖开发任务不得生成或进入可执行状态。
- 不依赖 UI 的后续规划文档不应被无故阻塞。

--------------------------------------------------

### State Integrity Gate

检查：

- 每个 P0 FLOW 都有前置业务事实、触发事件、成功事实与阻断事实。
- 每个关键状态均有唯一来源、分类、允许迁移、非法迁移与迁移守卫。
- 交互暂态、派生动作状态、持久业务状态、异常状态、旧流程边界状态、数据域状态已区分。
- 前端、路由、本地缓存、旧审批、旧入口不得成为业务状态来源。
- 旧对象与旧状态均有明确不可映射目标。

规则：

- 不满足时，06 不得确认。
- 涉及 FLOW、DOMAIN、SCN、MODULE 前置缺失时，必须标记上游 write-back required，并回到 01 或 02 修正。

--------------------------------------------------

### API Contract Gate

检查：

- 每个 P0 FLOW 至少有 QUERY、COMMAND、DECISION_VIEW 或 LEGACY_BOUNDARY 合同承接。
- 每个 COMMAND 都引用 06 的业务事件、前置事实和迁移守卫。
- 每个 COMMAND 都有幂等和并发语义。
- 每个 API 都声明访问上下文、业务资格和错误恢复方向。
- 旧审批字段、旧审批状态、旧审批接口无法进入新 COMMAND 的输入、判断或返回。
- 每个 API 都有正向与反向 TEST 映射。

规则：

- 不满足时，07 不得确认。
- 07 不得把 08 作为正式上游 SoT。

--------------------------------------------------

### Permission Decision Gate

检查：

- 每个关键 COMMAND 都有 PERM-ID。
- 每个 PERM 都明确动作、资源、允许主体、允许范围、资格、状态前置和数据域前置。
- 权限拒绝、范围拒绝、状态阻断、旧流程阻断、数据域阻断、外部能力阻断已区分。
- 工作人员协助能力没有越权。
- 历史对象只读边界已明确。
- 每个关键 PERM 均有自动化测试映射。

规则：

- 不满足时，08 不得确认。
- 前端隐藏、禁用或不展示按钮不得视为权限实现。

--------------------------------------------------

### Architecture Binding Gate

检查：

- 每条 P0 FLOW 都有逻辑架构承接位置。
- 每个关键逻辑模块已选择 `extend_existing_domain`、`reuse_shared_capability` 或 `create_stable_business_domain`，并关联稳定业务概念。
- 已优先核实现有稳定业务域；`create_stable_business_domain` 具备无法复用原因、长期职责边界和非期次命名依据。
- 每个 Canonical API Contract 都有 Architecture Binding。
- 每项旧资产都明确允许复用什么技术基础，以及禁止复用什么业务语义。
- 旧审批、旧入口、旧状态无法进入新 Command、新 State 或新 Decision View。
- 外部能力未完成 10 选型时，不得伪装为具体 Provider 已确认。
- 架构风险只移交 12，不在 09 重复定义正式 RISK。
- 09 未生成具体目录、类名、数据库表名或迁移名称，也未把数据域隔离解释为期次物理命名空间。

规则：

- 不满足时，09 不得确认。
- 09 启动前必须读取并引用 PROJECT-CURRENT-BASELINE。

--------------------------------------------------

### Capability Decision Gate

检查：

- 每项外部能力都有 CAP-ID。
- 每个 CAP 都关联 FLOW、MODULE、ARCH、TEST 和 RISK。
- 每个 CAP 都明确候选方案、选型状态、选择理由、官方事实和关键前提。
- 官方事实、权限、鉴权、版本、配额、计费、目标端兼容性未确认时，必须标记阻断范围。
- 页面可打开、JSSDK ready、Mock 成功、代码存在，均不得视为真实能力成功。
- 未完成 Capability Development-Entry Evidence Gate 的 CAP，不得进入相关开发任务。
- planning 阶段不得标记 `real_environment_verified` 或 `release_ready`。

规则：

- 不满足时，10 不得确认。
- 10 已确认不等于 Provider 已接入、已真机验证或已上线。

--------------------------------------------------

### Test Design Gate

检查：

- 每条 P0 FLOW 都有正向业务流程测试。
- 每条 P0 FLOW 都有前置阻断、状态、接口、权限、旧流程和回归测试。
- 涉及外部能力的 FLOW 都有真实环境能力测试。
- 涉及页面和交互的 FLOW 都有 UI 行为或 UX 测试。
- 每条测试都明确自动化等级。
- 11 中的测试顺序与 01 FLOW 顺序一致。
- 11 不记录实际测试结果。

规则：

- 不满足时，11 不得确认。
- 11 不得定义测试代码、命令、fixture 脚本、执行调度或实际证据内容。

--------------------------------------------------

### Risk / Dependency / Open Item Gate

检查：

- 每个正式 RISK 已归并为唯一风险。
- 每个 BLOCKER 有阻断阶段、处理策略与关闭条件。
- 每个 DEP 有验证来源和最晚解除阶段。
- 每个 OPEN 有回写目标和确认主体。
- 关键 OPEN 未关闭时，相关任务不得进入 13。
- 12 不重复定义已确认业务规则、状态、接口、权限或 UI 事实。

规则：

- 不满足时，12 不得确认。
- 01–11 只能移交风险信号、风险移交项、阻断提示或待确认问题，不得创建重复正式 RISK-ID。

--------------------------------------------------

### Task Contract Gate

仅当 `requires_execution_handoff: true`、本期实际装配 13 时运行本 Gate 及其后的 Implementation Naming Gate、Implementation Contract Completeness Gate；`planning_only` 不运行这些实现类 Gate。

检查：

- 每条 P0 FLOW 至少有一个主 TASK。
- 每个 TASK 可追溯到 FLOW / STATE / API / PERM / ARCH / TEST。
- 关键 OPEN 已关闭。
- 每个 CAP 任务只引用已确认的选型与门禁。
- 每个旧流程隔离要求均被至少一个 TASK 承接。
- 每个 TASK 有 Ready Gate、完成合同和回写目标。
- TASK 不引用不存在、未装配或未确认的 FLOW / STATE / API / PERM / ARCH / CAP / TEST 结论。

规则：

- 不满足时，13 不得确认。
- Task Contract Gate 只校验 13 自身及其上游 01–12；14、15 的预先存在不得作为 13 确认前置。
- 候选文件路径不等于已确认实现事实。
- TASK 不得使用“按实现时决定”“可选 A / B / C”“视情况复用”“后续再看”。

--------------------------------------------------

### Implementation Naming Gate

检查：

- 所有 TASK 的 Planning ID 仅用于 `trace_only`。
- 不存在期次、Sprint、阶段、版本或 Planning ID 被当作候选实现名称。
- 每个 P0 TASK 已关联稳定业务概念、实现承接策略和优先核实的现有业务域。
- `create_stable_business_domain` 具备 09 的架构依据。
- 数据域隔离没有被解释为期次物理命名空间。
- 候选实现位置优先指向已有稳定业务域。
- 不存在诱导执行方创建任何带期次、阶段、Sprint、迭代或版本命名空间的代码、模块、API、权限或数据资产。

规则：

- Gate 未通过时，13 不得确认，不得派生 14/15，不得准备正式 Handoff。
- 必须回到 09 或 13 修正；不得把命名决策推迟为执行层静默处理。

--------------------------------------------------

### Implementation Contract Completeness Gate

按任务实际内容检查；详细参数状态与事实归属以 `04-planning-format-spec.md#implementation-contract-parameter-status` 为唯一来源：

- 会改变业务合同、用户体验、API、数据、状态、权限、测试、验收或发布判断的参数已确认，或明确为 `blocking_open`。
- 文件/图片任务适用时，类型、大小、数量、必传、失败阻断、重试/恢复、替换/删除和对象绑定边界已闭合。
- 时间、输入、查询和外部能力参数只检查实际涉及项，不为格式完整追问无关值。
- 纯技术参数可以 `explicitly_delegated`，但已写明决策范围、既有规范、允许边界、验证方式和不可影响的业务结果。
- 不存在只写“实现时决定”的委托。
- P0 TASK 不存在未关闭的 `blocking_open`。
- 不存在会让开发执行到一半才必须向用户追问的 P0 业务参数。

规则：

- Gate 未通过时，13 不得确认；缺失参数回写真正拥有该事实的上游 SoT，并由 12 保留对应 OPEN。
- P0 主流程存在 `blocking_open` 时，不得派生 14/15，也不得准备正式 Handoff。
- 不得用 AI 猜测或行业默认值绕过确认。

--------------------------------------------------

### Execution and Acceptance Framework Derivation Gate

仅当 `requires_execution_handoff: true` 且 13 已确认、14/15 已派生时运行；`planning_only` 不运行本 Gate。

检查：

- 13 状态已确认。
- 14 已按 TASK 预置 `EXEC-<TASK-ID>` 空白执行项。
- 14 已继承 TASK 的目标、完成合同、预期 TEST、RISK / DEP / CAP 阻断与偏差回写位置。
- 14 只包含框架和待填写位置。
- 每条 P0 FLOW 都有预置验收项、风险关闭条件和发布影响。
- 15 已包含 TEST-ID、CAP 真实环境要求、RISK 关闭条件、DEP 解除条件、发布门禁和基线更新条件。
- 14、15 只使用已确认 01–13 的引用。
- 14、15 没有任何实际执行、测试、真实环境、验收、发布或基线更新事实。
- 14、15 的框架生成状态、框架完整性和实际事实状态符合统一状态模型：`generated` / `complete` / `not_required` / `not_started`。
- `assembled_documents` 只包含已经真实生成的路径。
- Handoff 尚未生成，或会在本 Gate 通过后基于实际路径重新生成。
- 所有 EXEC、TEST、CAP、发布与基线事实初始只能是 `not_started` 或空白待填。
- 14 未填写实际代码改动、实际文件修改、自动化测试通过、接口已联调、真实外部能力可用、真机验证完成、最终验收通过、可发布或已发布。
- 15 未填写通过、失败、已验收、真实环境已通过、可发布、已发布、生产已更新或 PROJECT-CURRENT-BASELINE 已更新。

规则：

- 14、15 不得反向定义业务、状态、接口、权限或测试标准。
- 14、15 不需要独立用户确认作为 Planning 完成前提。
- Gate 通过后的唯一允许动作是：生成实际 `assembled_documents`，基于真实路径生成唯一正式 Handoff Package 并标记为 `prepared`，然后进入最终人话总结确认。只有用户最后确认且 Interaction Preference Consolidation 完成后，才允许标记 Planning Handoff Complete。

--------------------------------------------------

### Completion Result

输出：

Planning Context 状态：

- INCOMPLETE
- COMPLETE

规则：

只有：

COMPLETE

才允许进入：

Planning Document Mode。

`execution_handoff_decision.decision_status` 不是 `confirmed`，或 `requires_execution_handoff` 与 `handoff_type` 不匹配时，Planning Context 必须保持 `INCOMPLETE`。

## 12. 运行时事件日志（Runtime Event Logging）

Runtime Event Log 属于 Project Runtime Evidence。

允许记录：

- 模式切换
- 阶段推进
- 风险发现
- 冲突发现
- Project Current State Gate 结果
- Completion Gate 结果
- Capability 识别
- Blocking Trigger
- 文档装配结果
- 文档确认结果
- UI/交互确认结果
- Context 状态变化

禁止记录：

- 完整 CoT
- 长篇推理
- 全量聊天记录
- 非结构化自然语言分析

Runtime Event 格式：

```yaml
event_seq:
timestamp:
runtime_mode:
event_type:
event_id:
related_ids:
decision:
reason:
blocking:
next_action:
```

允许事件类型：

```text
MODE_SWITCH
STAGE_ENTER
STAGE_COMPLETE
RISK_DETECTED
CONFLICT_DETECTED
CAPABILITY_DETECTED
BLOCKING_TRIGGERED
COMPLETION_GATE_CHECK
DOCUMENT_ASSEMBLY
DOCUMENT_CONFIRMATION
UI_CONFIRMATION
PLANNING_CONTEXT_UPDATED
PLANNING_COMPLETE
```

规则：

- 每个事件必须结构化。
- 每个事件必须最小化。
- `event_seq` 必须在同一个 `planning-runtime/event-log.md` 内单调递增。
- `event_seq` 是事件审计与恢复分析的主排序字段。
- `timestamp` 只表示发生时间，不作为唯一排序依据。
- 禁止重写历史 `event_seq`。
- 禁止插入旧 event 破坏已存在 `event_seq`。
- 如需补记事件，只能追加新 event，并在 `reason` 中标记 `backfill_event`。
- 不记录无意义状态。
- 不记录重复事件。
- 不记录完整用户输入。
- 不记录完整 AI 回复。
- 禁止生成自由事件名称。
- `reason` 仅允许简短结构化原因。

`reason` 示例：

```text
missing_permission_boundary
```

Runtime Event Log：

- 不属于正式 SoT。
- 不进入规划文档正文。
- 不参与业务事实定义。
- 不参与 Capability Registry。
- 不参与 Acceptance。
- 不作为 Runtime Recovery Source。

日志仅用于：

- 调试
- 执行留痕
- 模型对比
- 问题定位

Completion Gate Logging：

```yaml
event_seq:
event_type: COMPLETION_GATE_CHECK
decision:
context_status:
blocking_count:
conflict_count:
missing_sections:
```

Capability Logging：

```yaml
event_seq:
event_type: CAPABILITY_DETECTED
related_ids:
decision:
reason:
next_action:
```

示例：

```yaml
event_seq:
event_type: CAPABILITY_DETECTED
related_ids:
  - CAP-PLATFORM-001
decision: evidence_gate_required
reason: platform_capability_detected
next_action: capability_registry
```

Document Confirmation Logging：

```yaml
event_seq:
event_type: DOCUMENT_CONFIRMATION
related_ids:
decision:
reason:
blocking:
next_action:
```

UI Confirmation Logging：

```yaml
event_seq:
event_type: UI_CONFIRMATION
related_ids:
decision:
reason:
blocking:
next_action:
```

### 12.1 运行时状态与项目证据（Runtime State vs Project Evidence）

Runtime State：

负责：

- 当前状态
- 当前阶段
- 当前恢复点

用途：

- 中断恢复
- 继续执行

特点：

- 临时
- 可覆盖
- 可更新
- Planning 正式结束时清空待处理反馈并标记已结束

当前 Planning 的 Runtime State 实例固定为：

```text
<phase_planning_runtime_directory>/current-interaction.yaml
```

它是上下文压缩、会话恢复和工具中断后的短期恢复来源；其中 `execution_handoff_decision` 只是已确认 Planning Context 的最小镜像，`document_assembly` 只是当前装配进度的最小镜像。字段以 `04-planning-format-spec.md` 为准，处理顺序以 `10-planning-document-interaction-runtime.md` 为准，恢复校验以 `08-planning-recovery-runtime.md` 为准。

Project Runtime Evidence：

负责：

- 事件记录
- 决策记录
- 审计记录

用途：

- Skill 优化
- 模型评估
- 项目复盘
- 用户回传分析

特点：

- append-only
- 长期保留
- 项目资产

规则：

- Project Runtime Evidence 禁止作为 SoT。
- Project Runtime Evidence 禁止作为 Planning Context。
- Project Runtime Evidence 禁止作为 Handoff Package。
- Project Runtime Evidence 禁止作为 Runtime Recovery Source。

### 12.2 项目运行时证据目录（Project Runtime Evidence Directory）

Planning Runtime Evidence 的唯一合法目录：

```text
<phase_planning_runtime_directory>/
```

结构：

```text
planning-runtime/
current-interaction.yaml
event-log.md
event-summary.md
decision-log.md
decision-summary.md
audit-log.md
audit-summary.md
```

当前 Skill 仅实现：

```text
planning-runtime/
```

规则：

- 本 skill 不定义其他 skill 的运行时目录、日志结构、证据保存位置或实际回写机制。
- `execution_handoff_decision` 第一次需要在发问前持久化时按需创建 `current-interaction.yaml`；不得等到进入 Planning Document Mode 后才创建。
- `event-log.md` 在第一次实际写入 Runtime Event 时创建。
- `decision-log.md` 在第一次实际存在 Decision Snapshot 时创建。
- `audit-log.md` 只在真正触发 Runtime Audit 时创建；普通 Planning 不默认创建。
- Event、Decision、Audit Summary 只在达到压缩阈值、阶段收尾或确有复盘需要时创建。
- 无内容文件不得为了目录完整性创建；所有文件直接在期次目录创建，不得从 Skill 复制。
- 禁止提前实现其他 skill 的 evidence 目录。
- 禁止新增 `recovery-runtime/`。
- 禁止新增 `governance-runtime/`。
- 禁止新增 `entropy-runtime/`。
- 禁止新增 `analysis-runtime/`。
- 禁止新增 `debug-runtime/`。
- `current-interaction.yaml` 是可覆盖的短期 Runtime State，不属于 append-only Project Runtime Evidence。

### 12.3 决策快照运行时（Decision Snapshot Runtime）

Decision Snapshot Runtime 只记录关键决策快照，属于 Project Runtime Evidence，用于 Runtime Debugging、Model Comparison、Human Review 和项目复盘。

它回答：

- 为什么发生
- 为什么选择该方案
- 风险是什么
- 当时有哪些备选路径

它不是：

- 聊天记录
- 推理链
- 分析日志
- 长期记忆系统

首次存在需要保存的 Decision Snapshot 时创建并写入：

```text
<phase_planning_runtime_directory>/decision-log.md
```

`decision-summary.md` 只在达到压缩阈值、阶段收尾或确有复盘需要时创建。

Decision Snapshot 格式：

```yaml
timestamp:
decision_id:
stage:
status:
current_understanding:
decision:
reason:
risk:
source:
impact:
supersedes:
next_action:
```

Decision Status：

```text
candidate
confirmed
superseded
rejected
```

规则：

- 用户尚未完成场景级确认前，关键业务流只能记录为 `candidate`。
- 只有用户明确确认后，才能记录为 `confirmed`。
- 后续被用户纠正时，追加新 Snapshot，并把旧决策标记为 `superseded`。
- 明确讨论但不采用的方案记录为 `rejected`。
- 不得静默覆盖已有关键决策。

Decision ID Specification：

```text
Decision ID 格式：

DEC-<TYPE>-<SEQ>

示例：

DEC-SCOPE-001
DEC-ROLE-001
DEC-UI-001
DEC-CAPABILITY-001
DEC-BLOCKER-001
DEC-RECOVERY-001
```

规则：

- 全局唯一
- 稳定引用
- 不允许自然语言替代
- 不允许自由格式
- 不允许同义重复

目的：

```text
Decision Snapshot
可追踪
可检索
可引用
```

字段规则：

- `current_understanding` 仅允许结构化摘要；备选路径只能作为短列表写入其中。
- `decision` 仅允许写当前选择，不写长解释。
- `reason` 仅允许短枚举原因。
- `source` 仅允许来源类型、文档路径或 Runtime Gate 名称，不记录完整用户输入。
- `impact` 仅允许结构化影响摘要。

`reason` 示例：

```text
missing_permission_boundary
ui_confirmation_completed
capability_confirmed
blocking_detected
completion_gate_passed
```

仅允许记录以下决策场景：

```text
阶段推进：目标确认、范围确认、角色确认、UI确认、能力确认
风险确认：权限、数据归属、状态流、外部能力、UI高风险项
Blocking Trigger
Completion Gate
Document Confirmation
Capability Confirmation
Recovery Trigger
```

Decision Snapshot Deduplication：

同一阶段、同一结论，仅允许记录一次 Decision Snapshot。

允许新增 Snapshot：

- 结论发生变化
- 风险等级发生变化
- Blocking 状态发生变化
- Capability 状态发生变化
- Recovery Trigger 发生

禁止：

- 重复记录同一结论
- 每轮访谈重复记录
- 仅因措辞变化重复记录

Decision Snapshot 的目标：

```text
记录关键决策变化
```

而不是：

```text
记录访谈过程
```

禁止：

- 自由新增决策类型
- 保存完整聊天记录
- 保存完整用户输入
- 保存完整 AI 回复
- 保存 CoT
- 保存推理过程
- 将 Decision Snapshot 写入 Planning Context
- 将 Decision Snapshot 写入正式文档
- 将 Decision Snapshot 写入 Handoff Package
- 将 Decision Snapshot 写入 Capability Registry
- 将 Decision Snapshot 写入 Acceptance

Decision Summary 机制：

- `planning-runtime/decision-summary.md` 只保留关键决策、关键风险、关键阻塞、关键恢复事件。
- Summary 禁止完整复制 Log。
- Summary 禁止长篇解释。
- Summary 禁止用户原话。
- 历史决策进入 Summary 后，不默认进入 Runtime Context。

生命周期：

- Decision Log append-only。
- Decision Summary 周期性汇总。
- Decision Log 和 Decision Summary 默认不加载。
- Runtime 行为不得依赖历史 Decision Log。

## 13. 运行时事件持久化（Runtime Event Persistence）

第一次实际发生需记录的 Runtime Event 时创建并写入：

```text
<phase_planning_runtime_directory>/event-log.md
```

达到压缩阈值、阶段收尾或确有复盘需要时，才创建 Runtime Event Summary：

```text
<phase_planning_runtime_directory>/event-summary.md
```

规则：

- Runtime Event Log 属于 Project Runtime Evidence。
- 不属于正式 SoT。
- 不属于业务事实。
- 不参与文档职责定义。
- 不参与 Capability Governance。
- 不参与 Acceptance。
- 不作为 Runtime Recovery Source。

必须写入 Runtime Event Log 的事件：

```text
MODE_SWITCH
STAGE_ENTER
STAGE_COMPLETE
RISK_DETECTED
CONFLICT_DETECTED
CAPABILITY_DETECTED
BLOCKING_TRIGGERED
COMPLETION_GATE_CHECK
DOCUMENT_ASSEMBLY
DOCUMENT_CONFIRMATION
UI_CONFIRMATION
PLANNING_CONTEXT_UPDATED
PLANNING_COMPLETE
```

写入规则：

- 触发即追加写入。
- 不允许静默跳过。
- 不允许覆盖历史日志。
- 使用 append-only 模式。

Runtime Event Log 更新规则：

- 默认按 event_seq 追加。
- timestamp 仅作为事件发生时间参考。
- 不允许重写历史事件。
- 不允许重新生成旧日志。

日志格式：

```yaml
event_seq:
timestamp:
runtime_mode:
event_type:
event_id:
related_ids:
decision:
reason:
blocking:
next_action:
```

Summary 允许创建或更新的时机（且必须确有压缩或复盘需要）：

- Planning Completion Gate 通过后。
- Planning Document Mode 完成后。
- Planning Handoff Complete 后。

Summary 内容：

- 关键风险
- 关键冲突
- Capability 识别结果
- Blocking Trigger
- Completion Gate 结果
- Planning Result

Summary 禁止：

- 完整聊天记录
- 完整事件复制
- 长篇推理

日志增长控制：

- Runtime Event Log 作为 Project Runtime Evidence 长期保留。
- 历史事件通过 Summary 压缩复盘入口。
- 超过阈值的旧事件不默认进入上下文。
- Runtime Event Log 不作为长期记忆系统。

禁止：

- 无限增长
- 全量读取历史日志
- 将日志重新注入 Planning Context
- 将日志重新写入正式 SoT

日志读取规则：

- Runtime Event Log 不自动进入 Planning Context。
- Runtime Event Log 不自动进入正式文档。
- Runtime Event Log 不自动进入 Runtime SoT。
- Runtime Event Log 不作为 Runtime Recovery Source。

仅允许：

- Runtime Debugging
- 问题定位
- 模型行为分析
- 恢复问题复盘
- 用户主动回传日志

Completion Gate 必须追加：

```yaml
event_seq:
event_type: COMPLETION_GATE_CHECK
decision:
context_status:
blocking_count:
conflict_count:
missing_sections:
```

只有满足共同条件及当前 Handoff 分支的附加条件后，才允许标记 Planning Handoff Complete 并追加。

共同条件：

- 本期实际装配文档已生成并确认。
- `assembled_documents` 与 `handoff_role_mapping` 已基于真实路径生成。
- Handoff Branch Consistency Check 已通过；Planning Context、本期 `current-interaction.yaml` 恢复镜像、Document Assembly Plan 与 Handoff 的分支字段一致，前三者的 `decision_status` 均为 `confirmed`。
- 最终人话总结已输出并获得用户最后一次整体确认。
- Interaction Preference Consolidation 已完成，`.runtime/planning-layer-runtime/user-profile.yaml` 已按需更新或确认无需变更；写入失败不视为完成。
- `current-interaction.yaml` 的待处理反馈已清空，`planning_status` 已设为 `planning_handoff_complete`。

`execution_ready` 附加条件：

- 13 已确认，14/15 已派生且 Execution and Acceptance Framework Derivation Gate 已通过。
- Task Contract Gate、Implementation Naming Gate 与 Implementation Contract Completeness Gate 已通过。
- Handoff 已包含 `execution_constraints`，且不存在 P0 `blocking_open` 参数。

`planning_only` 附加条件：

- `requires_execution_handoff: false`。
- Handoff 不包含 13/14/15 职责或针对代码实现的 `execution_constraints`。
- 不存在阻断本期规划结论本身的 OPEN。

```yaml
event_seq:
event_type: PLANNING_COMPLETE
decision:
generated_documents:
handoff_status:
summary_generated:
final_summary_confirmed:
interaction_preference_consolidated:
planning_status:
blocking:
next_action:
```

事件语义：

- `Planning Context COMPLETE` 只表示访谈和上下文已完成。
- `Planning Document Assembly Complete` 表示实际装配文档已生成并确认。
- `Planning Handoff Prepared` 表示正式 Handoff Package 已按真实路径生成，但仍在等待最终人话总结确认。
- `Planning Handoff Complete` 表示最终人话总结已确认、用户偏好收尾已完成，Planning 正式结束。
- `PLANNING_COMPLETE` 只能在 Planning Handoff Complete 后追加。

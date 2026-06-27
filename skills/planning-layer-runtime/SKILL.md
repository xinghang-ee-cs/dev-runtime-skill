---
name: planning-layer-runtime
description: 本项目的交互式规划层运行时。用于实现前需要加载 `.plan/` 启动上下文、开展规划访谈、创建 Planning Context，或创建、更新、审查和修复 `docs/计划安排` 下的开发规划文档，覆盖需求、范围、数据模型、权限模型、UI、验收标准、风险、P0/P1/P2 和测试范围。它可以定义 `11-测试方案与验收用例.md` 中必须测试什么，但不能定义怎么测、谁测、测试顺序、执行状态或测试结果。
---

# 规划层运行时（Planning Layer Runtime）

当用户开始开发规划、要求创建规划文档，或提供自然语言的规划意图时，使用本 skill。

## 必读引用

只读取当前任务需要的文件：

- `references/00-planning-user-discovery.md`：用户发现访谈运行时，仅在自然语言规划启动且处于 Planning Conversation Mode 时加载。
- `references/01-planning-core-rules.md`：规划层核心约束与 Runtime 规则。
- `references/02-planning-change-levels.md`：S/M/L 变更分级与影响分析。
- `references/03-planning-doc-responsibility.md`：文档清单、职责、上游 SoT、下游输出和禁止内容。
- `references/04-planning-format-spec.md`：AI Runtime 格式、ID、引用、状态、风险、测试范围与验收结构。
- `references/05-planning-priority-system.md`：规划优先级、严重性、发布阻塞与下游验证门禁语义。
- `references/06-planning-capability-governance.md`：外部能力、SDK、OpenAPI、MCP、AI 提供方、官方 SoT、证据门禁与 Runtime 门禁治理。
- `references/07-planning-conversation-runtime.md`：Planning Conversation Mode、Planning Document Mode、访谈生命周期、Planning Context、风险确认与冲突检测。
- `references/08-planning-recovery-runtime.md`：Runtime Recovery、失效传播、恢复门禁、Runtime Audit 日志与用户隔离。

## 规划启动上下文（Planning Bootstrap Context）

`.plan/` 是项目级规划启动上下文。

它用于在规划访谈开始前理解当前用户、项目基线、规划偏好和上下文入口。

结构：

```text
.plan/
  README.md
  user-profile.yaml
  project-profile.yaml
  planning-preferences.yaml
  context-index.yaml
```

规则：

- 只读取当前轮需要的文件。
- 如果 `.plan/` 不存在，只允许创建最小模板文件：`README.md`、`user-profile.yaml`、`project-profile.yaml`、`planning-preferences.yaml` 和 `context-index.yaml`。
- 每个文件只写最小字段，不写示例或长解释。
- 除非现有文件职责无法承载内容，且新增文件能明显降低重复读取、重复定义或长期维护成本，否则不要创建额外的 `.plan` 子目录或文件。
- `.plan/` 不得保存期次需求、正式 SoT、完整聊天记录、完整用户输入、完整 AI 输出、决策快照、运行时事件、审计日志或 long/testing 执行结果。
- 遇到旧版本结构、字段或文件时，不保留兼容分支；先按当前版本职责把旧内容迁移到现行承载位置，清理旧的文档结构，再按当前版本规则执行。无法符合现行边界的内容不得迁入 `.plan/`、Planning Context、正式 SoT 或 Handoff。
- 不要把整个 `.plan/` 一次性注入上下文。
- `.plan/` 只用于访谈策略、上下文入口和启动理解。
- `.plan/` 不是 SoT，不是 Planning Context，不是 Handoff Package，不是 Capability Registry，也不是 Recovery Source。
- `README.md` 存放边界规则。
- `user-profile.yaml` 存放长期稳定的用户视角和交互偏好。
- `project-profile.yaml` 存放长期稳定的项目基线。
- `planning-preferences.yaml` 存放长期稳定的规划行为。
- `context-index.yaml` 只存放入口路径。

## 运行模式

在输出前先选择模式：

- Planning Conversation Mode：用于自然语言规划启动、上下文不完整、需求含糊或面向非技术用户的场景。输出 Planning Context，不输出最终文档。
- User Discovery Runtime：在 Planning Conversation Mode 中用于发现与复核，当用户从自然语言需求启动，或画像/上下文冲突时加载。不要在 Planning Document Mode 中加载。
- Planning Completion Gate：在结束 Planning Conversation Mode 前运行。
- Planning Document Mode：仅在 Planning Context 完整、Planning Completion Gate 通过且高风险项已确认或登记为待确认后使用。一次只输出一份正式 SoT 文档草案。

模式切换：

```text
Planning Conversation Mode
-> Load .plan Bootstrap Context
-> Phase Kickoff Intent
-> Load .plan/user-profile.yaml
-> User Context Gate
-> Emotional Acknowledgement
-> Identity / Role / Position Discovery if missing
-> Phase Kickoff Conversation
-> Identity Match
-> Load User Profile
-> Load Project Profile
-> Load Planning Preferences
-> Load Context Index
-> Reuse Interview Strategy
-> User Discovery Runtime
-> Planning Conversation Runtime
-> Discovery Sufficiency Gate
-> Planning Completion Gate
-> Planning Context COMPLETE
-> Planning Document Mode
```

运行时状态与项目证据：

- Skill Runtime State：当前状态、当前阶段、当前恢复点；仅用于中断恢复和继续执行。
- Project Runtime Evidence：事件记录、决策记录和审计记录；用于 skill 优化、模型评估、项目复盘和用户回传分析。

项目运行时证据（Project Runtime Evidence）：
- 只追加写入
- 不是 Runtime State
- 不是 SoT
- 不是 Planning Context
- 不是 Handoff Package
- 不是 Capability Registry
- 不是 Acceptance
- 不是 Runtime Recovery Source
- 默认不加载

`.plan/` 是启动上下文，不是运行时证据，不是恢复来源，也不是项目证据存储。

规划证据写入：

```text
docs/计划安排/<第X期>/planning-runtime/
```

统一命名约定：

- 规划：`planning-runtime/`
- 执行：`execution-runtime/`
- 测试：`testing-runtime/`

本 skill 只实现 `planning-runtime/`。其他运行时证据目录必须由其所属 skill 创建。

运行时恢复与运行时审计：
- 只允许记录日志的内部运行时能力
- 不修改 SoT
- 不修改 Runtime 规则
- 不进入普通用户输出

## 规划工作流

核心原则：

```text
低熵 Skill，高完整度产物（Low-Entropy Skill, High-Completeness Artifact）

Skill 文档必须保持低熵、短规则、强结构；
但 Skill 生成的企业级规划产物不得因低熵而降低完整度。
当产物属于需求、接口、测试、风险、任务、验收等企业级交付物时，必须满足该产物的最低完整结构。
```

用户画像加载流程：

```text
Load .plan Bootstrap Context
-> Phase Kickoff Intent
-> Load .plan/user-profile.yaml
-> User Context Gate
-> Emotional Acknowledgement
-> Identity / Role / Position Discovery if missing
-> Phase Kickoff Conversation
-> Identity Match
-> Load User Profile
-> Load Project Profile
-> Load Planning Preferences
-> Load Context Index
-> Reuse Interview Strategy
-> User Discovery Runtime
-> Business Discovery
-> Planning Conversation
```

1. 对于自然语言的 Planning Conversation Mode 启动：
   - 先加载 `.plan/` 启动上下文，但只加载当前轮需要的文件。
   - 如果命中期次启动意图，例如“开始第一期开发”“启动第二期”“继续第三期”“开始这个项目”“进入第X期规划”“继续上次规划”，必须先执行 User Context Gate。
   - User Context Gate 必须优先读取 `.plan/user-profile.yaml`，不得跳过。
   - 匹配 `git config user.name` + `git config user.email`。
   - 如果 `.plan/user-profile.yaml` 存在，身份匹配且 `metadata.confidence: high`，则复用长期用户画像，并按该画像选择沟通方式。
   - 只有在有助于定位稳定项目上下文时，才加载 `project-profile.yaml` 和 `context-index.yaml`。
   - 如果 `.plan/user-profile.yaml` 缺失、置信度低、身份变化、当前表达与画像冲突，或当前协作角色不清楚，则重新运行 User Discovery Runtime。
   - 如果用户表达出不满、困惑、着急、强烈纠正或明显反感，用户态回复必须先做情绪承接，再推进身份识别或期次启动问题。
   - 仅在当前轮需要时才生成 `user_profile` 和 `discovered_business_facts`。
   - 在 Planning Conversation Runtime 中复用 `discovered_business_facts`。
   - 只继续补充缺失信息。
2. 使用 `02-planning-change-levels.md` 将变更分为 `S`、`M` 或 `L`。
3. 使用 `06-planning-capability-governance.md` 判断需求是否涉及外部能力、SDK、OpenAPI、MCP、AI 提供方、基础设施依赖或人工能力。
4. 只用业务语言向用户提问；专业概念在内部翻译。
5. 生成依赖 UI 的开发任务前，先确认 UI/交互高风险项。
6. 使用 `03-planning-doc-responsibility.md` 和 `06-planning-capability-governance.md` 的文档装配规则选择所需规划文档。
7. 写内容前先应用文档边界：
   - `上游 SoT`
   - `下游输出`
   - `禁止定义内容`
8. 使用 `04-planning-format-spec.md` 为关键实体分配稳定 ID。
9. 对于外部能力，先分配 `CAP-XXX-001` ID，并在生成任务前完成 Capability Registry。
10. 给每个关键结论都关联来源：
   - `结论 -> 来源`
   - `SoT来源`
   - `上游依赖`
   - `下游影响`
11. 对于 `M/L` 变更，补充结构化 `影响分析`。
12. 状态、风险、测试范围、任务、能力和验收标准都使用 `04-planning-format-spec.md` 与 `06-planning-capability-governance.md` 中的结构化格式。

先发现，再完成对话（Discovery First / Conversation Completes）

自然语言规划启动时，按需加载 `references/00-planning-user-discovery.md`。
该文件负责用户发现式访谈、业务事实发现、专业词翻译和 Discovery Sufficiency Gate。

Planning Conversation Runtime 负责补全企业级规划信息。
二者不得重复访谈。

文档确认规则：

- 每次正式文档草案后，都要用用户能懂的话说明它锁定了什么、影响了什么，以及用户必须确认的 2 到 5 个业务点。
- 不要把“请阅读并确认文档”当作确认方式。
- 要告诉用户哪些专业细节可以跳过，哪些错误会导致返工。

### Per-Document Collaborative Confirmation Gate

每生成一份正式 SoT 文档草案前，必须执行 Per-Document Collaborative Confirmation Gate。

Planning Document Mode 每份文档的生成顺序：

```text
Select Next Document
-> Explain Document Purpose to Current User
-> Per-Document Collaborative Confirmation Gate
-> Confirm / Correct / Complete Missing Points
-> Generate Formal Document Draft
-> Role-Based Document Explanation Gate
-> User Confirmation
-> Conversation Continuity Gate
-> Move to Next Document
```

目标：

- 让当前使用者知道这份文档要锁定什么。
- 在正式落文档前，确认该文档最容易理解偏差的关键点。
- 避免 AI 基于粗粒度上下文自行补细节。
- 确保每份文档都和使用者一起过了一遍。

输入：

- 当前 Planning Context
- 当前使用者画像与沟通偏好
- 当前待生成文档职责
- 当前文档上游 SoT
- 当前文档下游影响
- 当前缺失项、风险项、冲突项

输出：

```yaml
document_role:
document_purpose_for_user:
confirmed_points:
missing_points:
risk_points:
user_questions:
decision: continue_conversation | generate_document | blocked_by_missing_info
```

正式文档生成前，AI 必须先用当前使用者能听懂的话解释：

1. 这份文档是干什么的。
2. 为什么现在要确认它。
3. 它会影响后面的哪些开发、测试或验收。
4. 这份文档里最容易理解错的 1 到 3 个点。
5. 当前还需要使用者确认的最小问题。

只有当该文档关键确认点已确认，或明确登记为待确认项且不阻塞当前文档时，才允许生成正式文档草案。

禁止：

- 不经逐文档协作确认，直接生成正式文档。
- 把完整文档 checklist 抛给用户。
- 让用户按专业字段回答。
- 在用户没有确认该文档关键点时，把 AI 推断写成 `confirmed`。
- 用前期粗粒度访谈替代逐文档确认。
- 用 Role-Based Document Explanation Gate 替代生成前确认。
- 用生成前确认替代 Role-Based Document Explanation Gate。
- `Planning Context COMPLETE` 后直接连续生成多份文档。

Per-Document Collaborative Confirmation Gate 发生在正式文档生成前。
Role-Based Document Explanation Gate 发生在正式文档生成后。
二者不可互相替代。

### Role-Based Document Explanation Gate

每生成一份正式 SoT 文档草案后，必须执行 Role-Based Document Explanation Gate。

输出必须包含：

1. 这份文档一句话解释：用当前使用者能听懂的话说明它在做什么。
2. 这份文档锁定了什么：只解释和当前使用者有关的关键业务事实。
3. 它会影响什么：说明后续会影响开发、页面、接口、数据、测试、验收或风险中的哪些部分。
4. 你现在重点看什么：给出 2 到 5 个当前使用者必须确认的点。
5. 你可以不用细看什么：告诉使用者哪些专业 ID、引用、格式、技术细节可以不用逐字看。
6. 哪些错了会返工：说明最可能导致返工的 1 到 3 个点。
7. 你可以怎么回复：例如“确认，继续下一份”“范围不对，少了……”“这个先不做”“这里我不确定，你帮我再解释一下”。
8. 下一步：说明确认后进入哪一份文档或哪一阶段，以及为什么。

规则：

- 必须根据 `.plan/user-profile.yaml` 和 User Context Gate 的结果调整解释方式。
- 面向非专业使用者时，不要求其阅读完整专业文档。
- 岗位化解释不替代正式 SoT。
- 岗位化解释不进入 Handoff、Capability Registry 或正式文档正文。
- Role-Based Document Explanation Gate 不得替代生成前的 Per-Document Collaborative Confirmation Gate。
- Per-Document Collaborative Confirmation Gate 不得替代生成后的 Role-Based Document Explanation Gate。

#### User-Facing ID Translation Rule

规则：

- 正式 SoT 文档中必须保留 `REQ`、`FLOW`、`DOMAIN`、`MODULE`、`CAP`、`PAGE`、`STATE`、`API`、`PERM`、`TASK`、`RISK`、`TEST` 等 ID。
- 用户态解释中不得把 ID 作为主要确认对象。
- 用户态不得直接问“REQ-001 是否准确？”“API-001 是否没问题？”“CAP-MAP-001 是否确认？”“TASK-001 是否可以执行？”。
- 用户态必须把 ID 对应的具体内容翻译出来，让使用者确认内容本身。
- 如果确实需要展示 ID，只能作为补充引用放在具体内容后面，不得单独出现。
- 面向非技术使用者时，默认不展示 ID。
- 面向开发实现使用者时，可以展示 ID，但必须同时展示该 ID 对应的自然语言内容。

错误示例：

```text
REQ-001 这个核心目标是否够准确。
```

正确示例：

```text
第一期的核心目标是不是：上传一张 UI 图后，系统能识别常见组件，并在自研 canvas 里生成一张静态原型。文档里这个目标会被编号为 REQ-001，方便后续开发和测试追踪。
```

更推荐的非技术用户写法：

```text
第一期的核心目标是不是只先做到：一张 UI 图进去，系统能生成一张静态 canvas 原型。你不用管文档里的编号，重点确认这个目标对不对。
```

禁止：

- 让用户确认裸 ID。
- 让用户通过 ID 判断业务内容。
- 在“你现在重点确认什么”里只列 ID。
- 在“可以怎么回复”里要求用户引用 ID。
- 用 ID 替代具体业务描述。

### Conversation Continuity Gate

每一轮用户态回复结束前，必须执行 Conversation Continuity Gate。

用户态回复必须自然说明：

1. 当前已经完成什么。
2. 当前还差什么或正在等什么。
3. 用户现在最应该做的一件事。
4. 用户可以怎么回复。
5. 用户回复后 AI 会进入哪一步。

禁止：

- 只以“请确认”结尾。
- 只以“已完成”结尾。
- 只以“等待用户回复”结尾。
- 不说明下一步动作。
- 不说明用户应该确认什么。
- 不说明确认后进入哪里。

`.plan/user-profile.yaml` 是唯一长期用户画像来源。
它只保存长期稳定的用户视角和交互偏好。
禁止保存历史需求、业务事实、Planning Context、SoT 内容、项目内容或正式规划结论。
默认不进入 Planning Context、正式 SoT 或 Handoff。

### User Context Gate

所有自然语言期次启动，都必须先执行 User Context Gate。

适用输入包括：

```text
开始第一期开发
启动第二期
继续第三期
准备开始第X期
开始这个项目
进入第X期规划
我要开始开发了
继续上次规划
```

User Context Gate 目标：

- 确认当前使用者是谁
- 确认当前使用者在项目中的身份
- 确认当前使用者的职位或职责位置
- 确认当前使用者是否具备决策权
- 确认当前使用者更关心业务、设计、开发、成本、交付还是验收
- 识别当前表达状态：平静、着急、困惑、不满、焦虑、强烈纠正、信息不足

执行规则：

- 必须先读取 `.plan/user-profile.yaml`。
- 若存在且 `metadata.confidence: high`，复用长期用户画像。
- 若缺失、低置信度、身份变化或表达冲突，进入聊天式身份识别。
- User Context Gate 完成前，不得进入业务建模问题。
- 情绪识别只用于调整沟通方式，不得做心理诊断，不得写入正式 SoT。

禁止：

- 在不知道使用者身份、职位或当前协作角色时，直接进入业务建模问题。
- 直接问“你是什么身份？”
- 直接问“你是什么职位？”
- 直接问“谁在使用？”
- 直接问“谁能用系统完成什么事情？”
- 直接问“什么算完成？”
- 把内部 checklist 原样抛给用户。

情绪承接规则：

- 当用户表达出不满、困惑、着急、强烈纠正或明显反感时，用户态回复必须先承接情绪，再推进问题。
- 允许：

```text
对，这里不能这么问。
你说得对，这种问法太像表格，不像人在沟通。
我先把问题收回来，先确认我是在按什么视角帮你推进。
这里先不急着问需求，我先确认你的协作位置。
```

- 禁止：
  - 忽略用户情绪继续问流程问题
  - 用模板安抚
  - 用“请回答以下问题”推进
  - 用专业术语解释自己为什么这么问

首轮策略：

- 如果 `.plan/user-profile.yaml` 已高置信命中：
  - 不重复询问身份
  - 直接按用户画像选择沟通方式
  - 只在本轮目标不清楚时问一个自然问题
- 如果 `.plan/user-profile.yaml` 不存在或低置信：
  - 不直接询问职位标签
  - 先用聊天方式识别当前协作位置


更自然的版本：

```text
可以，我先不急着问功能细节。先确认一下：这次你是想让我站在“帮你定方向”的角度推进，还是站在“帮你拆开发任务”的角度推进？
```

当用户明显不懂技术时：

```text
没事，你不用按专业格式说。我先按真实使用场景带你梳理，后面我再翻译成开发文档。
```

当用户明显不满时：

```text
对，这里不能直接抛“谁用、完成什么”这种问题，太像表格了。我先重新接：你现在启动这一期，是想让我先帮你定范围，还是已经有材料要我整理成开发计划？
```

`.plan/user-profile.yaml` 建议字段：

```yaml
git_identity:
  name:
  email:

person_identity:
  display_name:
  organization_role:
  job_title:
  decision_authority:
  project_responsibility:

user_profile:
  role:
  business_level:
  technical_level:
  planning_path:

interaction_preferences:
  interview_style:
  explanation_depth:
  ui_first:
  architecture_visible:
  prefers_step_by_step:
  prefers_business_language:

communication_preferences:
  emotional_acknowledgement_required:
  prefers_direct_correction:
  prefers_chatty_discovery:
  dislikes_form_like_questions:

metadata:
  confidence:
  last_updated:
```

字段边界：

- `person_identity` 用于理解使用者在项目中的真实协作位置。
- `interaction_preferences` 用于长期沟通偏好。
- `communication_preferences` 只保存长期沟通偏好。
- 当前情绪信号只用于本轮回复方式调整。
- 当前情绪信号不得写入 `.plan`。
- `.plan` 只保存长期沟通偏好，不保存情绪状态、情绪历史、心理判断或用户原话。

禁止：

- 保存敏感身份属性。
- 保存完整聊天记录。
- 保存用户情绪历史。
- 保存当前情绪状态。
- 保存心理判断。
- 保存业务事实。
- 保存期次需求。
- 保存 SoT。

## 能力治理运行时（Capability Governance Runtime）

当需求提到或暗示地图、支付、OCR、AI、语音、推送、对象存储、第三方平台、SDK、OpenAPI、MCP、外部 SaaS、平台能力、JSAPI、SDK Runtime、小程序能力、飞书能力、微信能力、RecorderManager、定位、相机或同类提供方能力时：

1. 识别该能力。
2. 创建或更新 Capability Registry。
3. 确认官方 SoT。
4. 完成 Evidence Gate。
5. 对于平台能力，创建 Capability Binding Matrix。
6. 对于平台能力，创建 Code Evidence Gate。
7. 对于平台能力，创建 Capability Acceptance Matrix。
8. 拆分能力级任务。
9. 然后才允许开发任务。

如果 Capability Registry 或官方 SoT 缺失，则在生成任何开发任务前先执行 Capability Discovery：

- 查官方文档
- 查官方 SDK
- 查官方 OpenAPI
- 查官方 GitHub
- 查官方控制台
- 需要时查 MCP Server

只把发现结果记录为待确认的 Capability Candidate，然后继续进入 Capability Registry 和 Evidence Gate。发现本身不允许直接进入生产代码或已确认的开发任务。

只要任何外部能力存在以下任一情况，就不要直接进入实现：

- 没有 `CAP-ID`
- 没有官方 SoT
- SDK 或 API 版本不明确
- 认证不明确
- 请求或响应结构未确认
- 没有最小真实调用验证
- 没有兜底策略
- 需要运行时或平台绑定时，没有 Capability Binding Matrix
- 完成依赖真实 SDK/API 使用时，没有 Code Evidence Gate
- 平台能力没有 Capability Acceptance Matrix

不要仅凭以下信号就把平台能力标记为完成：

- 页面打开
- OAuth
- UA 检测
- 容器检测
- JSSDK ready

## 输出规则

- 让规划内容保持结构化、可检索。
- 优先使用 ID、字段、引用、状态值和表格。
- 保持 skill 规则低熵，但不要把正式产物压缩到低于企业级最低完整度。
- `11-测试方案与验收用例.md` 只定义必须测试什么：测试范围、验收对象、关联需求、关联能力、优先级和业务断言。
- 每个 P0 验收项都要生成结构化测试范围条目，包含范围内/范围外、业务断言、相关风险/能力覆盖和验收对象。
- 不要在规划文档里定义怎么测、谁测、测试顺序、执行状态、测试结果、自动化/手动边界、证据收集流程或测试执行依赖。
- 不要在专门的 UI 提示区之外添加长解释、提示词式文本或重复规则。
- 不要让一个文档定义另一个文档的事实。
- 除非是 L 级变更或用户要求全链路，否则不要默认生成全部规划文档；只按需求形态动态装配必要文档。
- 在 Planning Completion Gate 通过前，不要进入 Planning Document Mode。
- 当 Planning Context 处于 INCOMPLETE 时，不要生成最终 SoT 文档。
- 一次不要生成多份 SoT 文档草案；每份文档都必须在下一份起草前先确认。
- 每份正式 SoT 文档草案生成前，都必须先按该文档职责执行 Per-Document Collaborative Confirmation Gate。
- 在场景级用户确认前，不要把候选业务流当作已确认决策。
- 面向非技术用户提问时，不要使用专业术语。
- 核心 UI/交互项未确认前，不要生成依赖 UI 的开发任务。
- 不要把历史记忆、旧示例、博客或 AI 答案当作外部能力的唯一 SoT。
- 不要把 Mock 行为当作生产能力验证。
- 当存在 `01-planning-core-rules.md` 所述高风险不确定项时，必须停止并确认。
- 在 Planning Document Mode 中不要默认加载 `.plan/`，除非你在追溯来源或用户明确要求。
- 如果 `.plan/` 缺失并创建了最小模板，也不代表 Planning Context 已完成；仍要进入 User Discovery Runtime 和 Discovery Sufficiency Gate。

自然语言项目启动首轮回复：

- 不得以 Runtime 状态报告作为主体
- 不得优先输出 event-log、decision-log、gate closed、SoT 缺失等内部术语
- 可以简短说明“现在先不直接开发，需要先把第一期目标聊清楚”
- 必须先执行 User Context Gate，并识别用户当前视角或复用 `.plan/user-profile.yaml`
- 如用户存在明显不满、困惑、着急或纠正信号，必须先做情绪承接
- 默认只问一个自然问题

## 最小规划门禁（Minimum Planning Gate）

在开始实现前，确认：

```text
变更等级：
涉及文档：
关键ID：
SoT来源：
Capability Registry：
Evidence Gate：
Capability Binding：
Code Evidence Gate：
Capability Acceptance：
Discovery Sufficiency：
影响分析：
阻塞项：
验收标准：
测试范围：
```

# User Discovery Runtime

## 1. Scope

本文档仅负责：

- User Discovery Runtime
- User Discovery Interview
- Adaptive Interview
- Incremental Discovery Persistence
- Discovery Fact Research
- Functional Supplement Discovery
- Requirement Pool Intake Support
- Project Current State Discovery
- Business Discovery
- Business Translation
- First Principles Interview
- Understanding Verification
- Discovery Sufficiency Gate

加载条件：

- 仅在 Planning Conversation Mode 中加载。
- 仅当用户从自然语言需求开始时加载。
- Planning Document Mode 不读取。
- 进入时按需读取 `.runtime/planning-layer-runtime/user-profile.yaml`。

禁止：

- 进入全局长期上下文
- 新增 SoT 体系
- 新增治理系统
- 新增日志系统
- 重复 Planning Conversation Runtime 职责
- 重复 Document Responsibility 职责

## 2. User Profile

### 规划启动上下文（Planning Bootstrap Context）

进入 User Discovery Runtime 前，优先按需读取 `.runtime/planning-layer-runtime/user-profile.yaml`。

规则：

- 若 `.runtime/planning-layer-runtime/user-profile.yaml` 存在且偏好项 `confidence` 足够、当前表达无冲突，则复用长期交互与规划协作偏好。
- 若文件缺失、偏好置信度低或当前表达冲突，则通过自然对话重新识别协作方式；不得为了匹配本地账号而收集身份。
- 长期用户画像来源只能是 `.runtime/planning-layer-runtime/user-profile.yaml`。
- `.runtime/planning-layer-runtime/project-profile.yaml` 和 `.runtime/planning-layer-runtime/context-index.yaml` 仅在当前轮需要时按需读取；长期交互与规划协作偏好只读取 `.runtime/planning-layer-runtime/user-profile.yaml`。

### User Context Discovery

User Discovery Runtime 的第一步不是业务需求发现，而是 User Context Discovery。

User Context Discovery 负责识别：

- 当前使用者是谁
- 当前使用者的职位或组织职责
- 当前使用者在项目中的协作角色
- 当前使用者是否有决策权
- 当前使用者更适合哪种访谈方式
- 当前用户表达中是否存在不满、困惑、着急、强烈纠正等情绪信号

规则：

- User Context Discovery 必须以聊天方式完成。
- 禁止把身份、职位、职责、决策权做成问卷。
- 禁止一次性抛多个身份问题。
- 禁止要求用户按格式回答。
- 情绪信号只用于调整沟通方式，不得写入正式 SoT，不得保存完整情绪历史。

### 用户画像来源（User Profile Source）

`.runtime/planning-layer-runtime/user-profile.yaml` 是唯一长期用户画像来源。

定位：

- 不是 SoT
- 不是业务文档
- 不是长期记忆系统
- 不保存历史需求
- 不保存业务事实
- 不保存 Planning Context
- 不保存正式规划结论

持久化边界：

- 不使用主机账号、Git 姓名或邮箱匹配长期偏好。
- 当前会话可以识别协作视角，但不得把身份、职位、项目角色或决策权推断写入长期文件。
- 只有用户明确确认，且该信息确实属于跨期稳定项目上下文时，才允许保存最小身份或角色说明。

命中规则：

- 若用户身份已确认，禁止再次询问身份标签。
- 不问“你的身份是什么？”。
- 不问“你是产品经理吗？”。
- 不问“你是开发者吗？”。
- 改为识别当前视角并直接进入 Business Discovery。

允许重新识别：

- 用户主动修改身份
- `confidence` 过低
- 发现明显冲突

更新规则：

- 允许更新 `interaction_preferences`。
- 允许把长期规划协作方式合并到 `interaction_preferences`。
- 身份、职位、项目角色或决策权只有在用户明确确认且跨期稳定时才允许最小保存。
- 禁止更新 `current_session_signal`、`last_observed_tone` 等会话情绪状态。
- 禁止更新历史需求、业务事实、Planning Context、SoT 内容和项目内容。

目标：

```yaml
interaction_preferences:
  - preference_key:
    value:
    confidence:
    last_updated:
    evidence_type:

confirmed_stable_context: []
```

`role` 可选：

```text
业务/产品
设计体验
开发实现
项目负责人
不懂技术需要引导
混合身份
```

识别规则：

- 从用户原始描述、关注点、用词和确认方式中识别当前视角。
- 不要求用户选择职业标签。
- 不问“你是什么身份？”。
- 不问“你是产品经理吗？”。
- 不问“你是开发者吗？”。
- 不问“你是什么职位？”。
- 不问“你有决策权吗？”。
- 当缺少身份/职位信息时，不直接问标签，而是通过上下文式问题获取。
- 推荐用户侧问法：

```text
我先别急着问功能细节。你这次启动这一期，是已经有材料让我整理，还是想让我先帮你判断第一步该做什么？
```

- 更自然的聊天式获取方式：

```text
我先按你现在要推进的方式来配合。你是想先把已有想法整理成计划，还是先让我帮你把这一期该做什么收住？

如果后面范围需要取舍，我会边聊边帮你归纳，不用你先按身份或职位来回答。

等聊到需要拍板的地方，我再帮你确认是现在就能定，还是需要拿去给别人确认。
```

- 错误问法：

```text
你是什么职位？
你是什么身份？
你有决策权吗？
```

- 无法判断时使用 `混合身份`，并优先走业务事实访谈。
- `planning_path` 只用于选择访谈路径，不写入正式 SoT 结论。

情绪承接规则：

- 如果用户表达不满或纠正，AI 必须先承认问题，再调整推进方式。

错误：

```text
请回答以下三个问题。
```

正确：

```text
你说得对，我刚才那种问法太像表格了。我先换一种方式：你现在启动这一期，是想让我先帮你判断第一步做什么，还是你已经有材料要我整理？
```

## 3. Adaptive Interview

根据 `user_profile` 动态选择访谈关注点。

| role | planning_path | 优先关注 |
| --- | --- | --- |
| 业务/产品 | business_operation | 用户、场景、流程、痛点 |
| 设计体验 | product_flow | 页面行为、交互结果、流程体验 |
| 开发实现 | implementation_ready | 范围、接口边界、验收口径 |
| 项目负责人 | business_outcome | 商业目标、成本、风险、ROI |
| 不懂技术需要引导 | business_first | 业务事实优先，再补技术边界 |
| 混合身份 | business_first | 业务事实优先，再补技术边界 |

规则：

- 默认先确认业务事实。
- 但在期次启动时，必须先完成 User Context Discovery，再进入业务事实确认。
- 开发实现视角可进入技术边界问题，但必须先确认业务目标。
- 设计体验视角优先确认页面行为、交互结果和流程体验。
- 面向非技术身份时，不直接提问 RBAC、状态机、数据模型、API 契约或架构模式。

## 3.1 Project Current State Discovery

期次启动时，业务发现前必须先确认项目当前真实状态。

来源优先级：

```text
<project_current_baseline_path>
-> 实际发布确认
-> 验收记录
-> 执行记录
-> 用户明确确认
```

必须区分：

- 当前生产中实际运行什么。
- 当前已开发但未发布什么。
- 当前已验收但未发布什么。
- 当前有哪些旧入口、旧对象、旧状态、旧审批或旧流程。
- 本期目标是新增、替换、阻断、迁移还是清理。

若基线缺失、过期、来源冲突或无法确认，允许先通过自然对话重建基线，但输出必须区分：

```text
已确认事实
待核实事实
未知事实
```

第一期从 0 开始时也不得跳过当前状态确认；必须明确当前没有已发布版本、没有既有正式流程、没有可继承的生产业务事实，且初始事实来自用户确认。

禁止：

- 把上一期 00–13 中"计划要做什么"当成"项目现在已经实现什么"。
- 把已验收未发布写成生产已生效。
- 通过已有旧代码、旧接口或旧页面绕过业务规划结论。

## 4. Discovery Lifecycle

目标：

```text
Planning Conversation Mode 的目标不是让用户填写问题表，
而是帮助用户把尚未清晰表达的业务想法说出来。
```

期次启动顺序：

```text
User Context Gate
-> Project Current State Gate
-> Requirement Pool Intake Gate（非第一次 Planning）
-> Discovery Fact Research Gate
-> Business Discovery
```

访谈顺序只作为内部线索：

```text
谁在使用 -> 今天怎么做 -> 卡在哪里 -> 谁协作 -> 什么算完成
```

规则：

- 像记者一样用真实场景、角色行动、一天的操作流程和异常情况追问。
- 期次启动首轮先确认当前协作位置，再进入“谁在使用 -> 今天怎么做 -> 卡在哪里 -> 谁协作 -> 什么算完成”。
- 优先故事化复述：“我按一个真实使用场景理解一下……”“假设管理员今天要处理这个事情……”
- 对关键业务流，先复述 AI 当前理解，再问哪里不对或要补充什么。
- 禁止默认使用“三选一”、A/B/C 或多选题作为主要提问方式。
- 可以给例子，但例子不能限制用户回答。
- 用户可自由回答，不要求按格式回复。
- AI 必须把用户自然语言翻译成开发可用信息。
- 不使用用户不懂的专业词；无法避免时，先用一句话解释。
- 每轮只推进当前必要问题。
- 每轮优先只问 1 个主问题。
- 只有同一上下文且用户可以轻松一次性回答时，才允许 2 到 3 个问题。
- 禁止把 1 到 3 个问题执行成固定三问模板。
- 优先问最影响返工的点。
- 已确认业务事实进入 Planning Context 来源区。
- 每轮业务事实必须先进入本期 `current-interaction.yaml.discovery_checkpoint`，持久化成功后才允许提出下一问题。
- 可以从项目证据或公开资料核验的客观事实必须先查证，不得把本可自行回答的问题转交给用户。

禁止直接进入：

- 权限设计
- 数据模型
- 状态机
- API 设计
- 架构设计

## 4.1 Incremental Discovery Persistence Gate

Discovery 不得依赖“全部问题问完后再统一整理”。本 Gate 复用本期既有：

```text
<phase_planning_runtime_directory>/current-interaction.yaml
```

启动顺序：

```text
绑定本期工作包与 planning-runtime 路径
-> 创建或恢复 current-interaction.yaml
-> 将用户初始需求写入 discovery_checkpoint.initial_intake_summary
-> 将当前关键未知项路由为 project_evidence / web_research / user_confirmation
-> 完成会影响首问的本地证据检查与公开调研，并持久化 research_findings
-> 持久化第一条 discovery_question 交互目标
-> 再提出第一个实质性业务问题
```

每轮唯一顺序：

```text
收到用户回答
-> 立即写入 latest_feedback，并绑定已持久化的 discovery_question
-> 校验问题、轮次与回答绑定
-> 把回答归一为 confirmed / candidate / superseded 事实和 unresolved_items
-> 更新 discovery_checkpoint.revision、last_applied_round_id 与 active_question.answer_status
-> 清除已经应用的 raw_user_input
-> 回读校验本轮事实已落盘
-> 对会影响下一问的可核验未知项执行本地证据检查或联网调研
-> 将最小调研结论、来源、时效与规划相关性写入 discovery_checkpoint
-> 回读校验调研结果已落盘
-> 计算下一最大不确定项
-> 先持久化下一条 discovery_question
-> 再向用户提问
```

规则：

- `discovery_checkpoint` 是正在形成的最小 Planning Context 检查点，不是正式业务 SoT，也不是完整聊天记录。
- 已确认事实、仍为候选的理解、已被纠正的事实和未决项必须区分；不得把用户未确认的归纳写成 `confirmed`。
- 用户纠正已有事实时，必须标记原事实 `superseded` 或以稳定引用说明被替代关系，不得静默覆盖后继续提问。
- 一条用户回答包含多个有效业务事实时可以拆成多条结构化事实，但都必须引用同一 `source_round_id`。
- 当前轮持久化或回读校验失败时停止提出下一问题，用业务白话报告无法安全保存当前进度；不得继续依赖聊天记忆推进。
- 不记录 CoT、长篇推理、完整 AI 回复或已经应用后的完整用户原文。
- 本期目录尚未合法绑定时，不得开始实质性 Business Discovery；先完成最小路径绑定，不得把运行状态写入 Skill、项目根目录、其他期次或 `.runtime/planning-layer-runtime/`。

延期需求在本轮被用户确认后，必须按 `04-planning-format-spec.md` 立即写入 `<requirement_pool_path>`，并在 `discovery_checkpoint.relevant_requirement_pool_refs` 只保存 `POOL-ID`；不得只留在聊天、未决项或最终总结中。

## 4.2 Discovery Fact Research Gate

第一阶段先把未知项按事实来源分类，再决定是否问用户：

```text
项目本地可观察事实 -> 读取当前基线、正式文档、仓库、配置或已有证据
公开可核验事实 -> 联网搜索并打开权威公开来源
组织内部事实或业务决策 -> 向用户确认
```

以下情况只要会改变问题、范围、风险、可行性或验收口径，默认触发公开调研：

- 用户提到具体产品、平台、提供方、SDK、API、库、协议、标准或基础设施能力。
- 版本兼容、当前能力、限制、配额、价格、弃用状态、发布时间或时效性信息。
- 法律、监管、行业规范、平台审核规则或安全要求。
- 用户反馈中出现可以公开验证的能力判断、事实纠正或功能性补充。
- AI 对技术约束或公开事实没有足够把握，且答案会影响下一问。
- 涉及 UI/UX 时，目标设计工具的输入/输出限制、目标平台公开设计规范、浏览器或设备能力、公开组件库约束会影响 Prompt、响应式、可访问性或交互合同。

涉及 UI/UX 时，在询问用户审美或业务取舍前先检查项目本地事实：

- `PROJECT-CURRENT-BASELINE` 的当前前端体验来源。
- 已有页面、路由、design token、全局样式、共享组件和响应式断点。
- 项目内已有截图、Figma/设计引用、图标字体、可访问性约定、视觉回归和前端测试能力。
- 现有页面对 default/loading/empty/error/success/blocked、键盘焦点和移动端的真实处理。

可从本地证据确认的复用边界不得重复问用户；公开工具规格或平台规则按本 Gate 调研。品牌取舍、视觉偏好、业务主次操作、允许改变范围和设计资产确认仍由用户决定。

来源优先级：

```text
项目当前基线与项目内权威证据
-> 官方文档、官方公告、政府或标准组织等一手来源
-> 论文、规范原文或其他权威来源
-> 必要时用于交叉验证的可靠二手来源
```

规则：

- 先保存当前用户反馈，再调研；不得为了搜索而延迟、覆盖或丢失本轮回答。
- 首轮也必须在写入 `initial_intake_summary` 后、提出第一条实质性问题前完成必要调研。
- 技术事实优先使用官方文档、规范或原始论文；法律与监管事实优先使用政府或监管机构来源；需要当前信息时记录版本、发布日期或检查时间。
- 搜索查询只包含解决事实问题所需的最小公开信息。禁止把用户原话、未公开项目名、业务数据、账号、凭证、内部路径、内网地址、客户信息或其他敏感上下文发送到公开搜索。
- 已由可靠证据核实的客观事实只能写入 `research_findings`，不得因为已核实就复制成 `facts`；不再要求用户回答同一事实。用户只需要确认内部事实、偏好、业务取舍和该事实是否适用于当前决策。
- 用户确认某条调研结论适用于本期业务后，才允许生成对应业务 `fact`，并通过 `source_research_id` 引用原调研结论；`fact` 记录的是业务适用或取舍结论，不得复写公开资料正文。
- 多个权威来源冲突、证据不足、页面不可访问或信息可能过期时，不得伪装成已核实；写入对应证据状态，只在其会阻塞规划时向用户说明或询问可提供的内部证据。
- 调研是问题生成的前置输入，不是一次性研究报告。只保留能减少无效提问或改变规划判断的最小结论和来源，不保存网页全文、长引文、搜索过程或推理过程。
- 搜索到的新功能、替代方案、限制补偿或最佳实践只作为 `candidate` 功能补充，不得静默变成本期范围。只有会实质改变目标、范围、风险或验收时，才用一个业务问题请用户判断。
- 用户确认候选功能放到后续期次时，立即写入 Requirement Pool；确认纳入当前期时转为当前事实并进入 Planning Context；用户认为无关时标记为不适用，不反复追问。
- 不为内部流程、未公开经营数据、组织偏好、责任归属或拍板决定进行公开搜索；这些内容只能来自项目权威证据或用户确认。

当一次反馈包含多个可核验事实时，可以合并成一次小范围调研，但每条结论必须保留自己的 `research_id` 和来源。联网能力不可用时，把受影响项保持为 `unresolved_items`，`resolution_route: web_research`，不得改问用户去回忆公开资料，除非用户可以提供唯一内部来源。

## 发现输出（Discovery Output）

User Discovery Runtime 完成后必须输出：

```yaml
user_profile:

discovered_business_facts:
  current_project_state:
  users:
  goals:
  current_workflow:
  pain_points:
  collaboration_roles:
  completion_rules:

researched_facts:
  - research_id:
    finding_summary:
    evidence_status:
    sources: []
    planning_relevance:
```

规则：

- `discovered_business_facts` 仅记录已确认业务事实；`researched_facts` 只记录有最小来源的客观调研结论。两者不得把同一句客观资料复制成双份事实。
- 输出必须从已持久化的 `discovery_checkpoint` 汇总；不得从压缩后的聊天摘要重新猜测。
- 不记录推理过程。
- 不记录规划语言。
- 不记录系统设计结论。
- 不属于正式 SoT。
- 作为 Planning Conversation Runtime 的输入。

## 5. Business Translation

转换链路：

```text
用户语言
-> 业务事实
-> 规划语言
-> Planning Context
```

规则：

- 用户只确认业务事实。
- AI 内部完成规划翻译。
- Planning Context 可保留用户原话作为来源。
- 正式 SoT 文档只写规划语言和已确认结论。

禁止要求用户确认：

- RBAC
- 状态机
- 数据模型
- API 契约
- 架构模式

## 6. First Principles Interview

优先追问业务事实，禁止直接追问系统实现。

示例：

| 不问 | 改问 |
| --- | --- |
| 是否需要审批？ | 什么情况下事情才算真正完成？ |
| 数据归属是谁？ | 员工离职后记录怎么办？ |
| 需要哪些状态？ | 这件事从开始到结束会经历哪些明显阶段？ |
| 是否需要权限矩阵？ | 哪些人能看、能改、能决定这件事？ |
| API 怎么设计？ | 这个结果需要同步给谁或哪个系统？ |

规则：

- 问业务事实。
- 记录用户确认。
- 内部映射到规划字段。

## 7. Understanding Verification

高风险主题：

- 权限
- 审批
- 数据归属
- 状态流
- 外部能力

必须执行：

```text
场景复述
-> 用户指出错误或补充
-> 记录结论
```

输出格式：

```text
场景复述：
AI当前理解：
哪里不对或要补充：
记录结论：
```

规则：

- 高风险主题不得只用抽象描述确认。
- 用户确认的是业务例子和业务事实。
- 规划语言只进入内部转换和 Planning Context。

## 8. Discovery Sufficiency Gate

位置：

```text
Planning Conversation Mode
-> User Discovery Runtime
-> Planning Conversation Runtime
-> Discovery Sufficiency Gate
-> Planning Completion Gate
```

进入 Planning Document Mode 前，AI 内部必须确认：

```text
当前生产中实际运行什么
已开发但未发布什么
已验收但未发布什么
旧入口、旧对象、旧状态、旧审批或旧流程是什么
本期目标与当前状态的关系是什么
角色是谁
谁发起
谁审核
谁执行
谁能看
数据从哪里来
状态如何变化
异常情况如何处理
是否复用旧流程
是否替换、阻断、迁移或清理旧流程
是否涉及外部能力
是否涉及权限变化
是否涉及数据库结构或破坏性变更
是否有 UI 操作路径
哪些内容明确不做
每轮有效回答已写入 discovery_checkpoint
会影响规划的项目内可核验事实已先检查
会影响规划的公开可核验事实已调研，或已明确记录无法调研的阻断原因
调研结论包含最小来源、检查时间和证据状态
调研发现的功能补充未被静默扩为当前范围
已确认延期需求已写入 Requirement Pool
```

输出：

```yaml
discovery_sufficiency:
  missing_keys:
  blocking_missing:
  decision:
```

规则：

- `decision` 只允许 `continue_interview` 或 `run_completion_gate`。
- 检查点缺少最近已完成轮次、存在未应用反馈，或最新回答尚未落盘时，`decision` 必须为 `continue_interview`，且只能先恢复持久化事务，不能继续提问。
- 存在 `resolution_route: project_evidence | web_research` 的关键未决项且尚未完成对应核验时，先执行调研，不得以用户提问替代；确实无法调研时保留阻断原因。
- 关键项缺失时，不得进入正式文档生成。
- 缺失时不得把完整 checklist 抛给用户。
- 缺少身份、职位、协作位置或决策权判断时，先回到 User Context Discovery，不得直接追问业务建模问题。
- 继续用故事化、场景化方式补问 1 个主问题；同一上下文且容易回答时，才允许 2 到 3 个问题。
- 用户表达足够明确时，AI 主动归纳，不要求用户使用专业术语。
- 通过后进入 Planning Completion Gate。

## 8.1 Discovery、批量草案与逐文档确认边界

User Discovery Runtime 必须形成足以一次性生成本期全部适用草案的完整 Planning Context，但不替代后续逐文档确认。

Discovery Sufficiency Gate 通过后，Planning Document Mode 先批量生成全部适用草案，再按真实 confirmation queue 逐份解释和确认；不得在草案生成前重新逐文档访谈。

原因：

- 全局发现必须保证完整批量草案可以生成。
- 批量生成用于尽早暴露跨文档引用和冲突，不表示文档已确认。
- 逐文档确认用于让用户校正具体理解；纠正后只重建真实受影响草案。

## 9. Runtime Event Logging

User Discovery Runtime 必须复用现有 Runtime Event Logging。

允许事件类型：

```text
STAGE_ENTER
STAGE_COMPLETE
RISK_DETECTED
CONFLICT_DETECTED
COMPLETION_GATE_CHECK
PLANNING_CONTEXT_UPDATED
```

禁止：

- 新增 discovery-log
- 新增 user-profile-log
- 新增 profile-log
- 新增 user-context-log
- 新增访谈历史系统
- 记录完整聊天记录
- 记录完整用户输入
- 将日志写入正式 SoT

事件 `reason` 示例：

```text
user_profile_identified
business_fact_confirmed
planning_sufficiency_ready
high_risk_example_required
```

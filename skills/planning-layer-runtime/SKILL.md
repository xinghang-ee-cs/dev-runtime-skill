---
name: planning-layer-runtime
description: 本项目的交互式规划层运行时。用于实现前需要加载 `.plan/` 启动上下文、开展规划访谈、创建 Planning Context，或创建、更新、审查和修复 `docs/计划安排` 下的开发规划文档，覆盖需求、范围、数据模型、权限模型、UI、架构、外部能力选型、测试设计、风险、P0/P1/P2 和验收边界。它可以定义 `11-测试方案与验收用例.md` 中按什么业务顺序证明什么、自动化等级和真实环境要求，但不能定义测试代码、命令、执行状态或实际测试结果。
---

# 规划层运行时（Planning Layer Runtime）

当用户开始开发规划、要求创建规划文档，或提供自然语言的规划意图时，使用本 skill。

## 规划启动上下文（Planning Bootstrap Context）

只读取当前任务需要的文件：

- `references/00-planning-user-discovery.md`：用户发现访谈运行时，仅在自然语言规划启动且需要补充用户/业务上下文时加载。
- `references/01-planning-core-rules.md`：规划层核心约束与 Runtime 规则。
- `references/02-planning-change-levels.md`：S/M/L 变更分级与影响分析。
- `references/03-planning-doc-responsibility.md`：文档清单、职责、上游 SoT、下游输出和禁止内容。
- `references/04-planning-format-spec.md`：AI Runtime 格式、ID、引用、状态、风险、测试范围与验收结构。
- `references/05-planning-priority-system.md`：规划优先级、严重性、发布阻塞与下游验证门禁语义。
- `references/06-planning-capability-governance.md`：外部能力、SDK、OpenAPI、MCP、AI 提供方、官方 SoT、证据门禁与 Runtime 门禁治理。
- `references/07-planning-conversation-runtime.md`：对话生命周期、Planning Context、风险确认与冲突检测。
- `references/08-planning-recovery-runtime.md`：Runtime Recovery、失效传播、恢复门禁、Runtime Audit 日志与用户隔离。
- `references/09-execution-intent-guard.md`：执行边界内核。所有输入的 execution intent 判定、阻断结果和语义转向规则的唯一事实来源。

## 执行边界（Execution Boundary）

Planning Layer 不得产生执行层产物。

Execution Boundary Kernel 的完整定义见 `references/09-execution-intent-guard.md`。

所有用户输入先经过 Execution Boundary Kernel 判定：

```text
用户输入
→ Execution Boundary Kernel（09）
→ execution_intent：自然语义转向（不产生执行产物）
→ planning_intent：继续既有规划流程
```

用户可见回复保持自然对话风格，不暴露任何内部机制。

详细规则见 `references/09-execution-intent-guard.md`。

## 规划启动上下文（Planning Bootstrap Context）

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

## 项目当前基线（Project Current Baseline）

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

## 运行时状态与项目证据

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

本 skill 只定义并写入 `planning-runtime/`。不定义其他 skill 的运行时目录、日志结构、证据保存位置或实际回写机制。

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
Load .plan Bootstrap Context（按需）
→ Load .plan/user-profile.yaml
→ User Context Gate
→ Emotional Acknowledgement（如需要）
→ Identity / Role / Position Discovery（如需要）
→ Project Current State Gate
→ Business Discovery（00-planning-user-discovery.md）
→ Planning Conversation（07-planning-conversation-runtime.md）
→ Discovery Sufficiency Gate
→ Planning Completion Gate
→ Planning Context COMPLETE
→ Planning Document Mode
```

1. 对于自然语言的 Planning Conversation Mode 启动：
   - 先加载 `.plan/` 启动上下文，但只加载当前轮需要的文件。
   - 如果命中期次启动意图，例如"开始第一期开发""启动第二期""继续第三期""开始这个项目""进入第X期规划""继续上次规划"，必须先执行 User Context Gate。
   - User Context Gate 必须优先读取 `.plan/user-profile.yaml`，不得跳过。
   - 匹配 `git config user.name` + `git config user.email`。
   - 如果 `.plan/user-profile.yaml` 存在，身份匹配且 `metadata.confidence: high`，则复用长期用户画像，并按该画像选择沟通方式。
   - 只有在有助于定位稳定项目上下文时，才加载 `project-profile.yaml` 和 `context-index.yaml`。
   - 如果 `.plan/user-profile.yaml` 缺失、置信度低、身份变化、当前表达与画像冲突，或当前协作角色不清楚，则重新运行 User Discovery Runtime。
   - 如果用户表达出不满、困惑、着急、强烈纠正或明显反感，用户态回复必须先做情绪承接，再推进身份识别或期次启动问题。
   - User Context Gate 完成后，必须执行 Project Current State Gate；不得只读上一期 00–13 或旧代码来推断当前生产事实。
   - Project Current State Gate 必须优先读取 `docs/项目治理/PROJECT-CURRENT-BASELINE.md`；缺失、过期、来源冲突或无法确认时，不得进入 00 正式草案。
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
9. 对于外部能力，先分配 `CAP-XXX` ID，并在生成相关开发任务前完成 10 的 Capability Decision Card、Capability Development-Entry Evidence Gate 和必要的选型前提标记。
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

逐文档生成、用户态总结、确认、状态回写、进入下一份文档的完整生命周期规则只维护在本文件。
其他 reference 文件只能引用本节，不得重复维护同一套完整生命周期逻辑。

文档确认规则：

- 每次正式文档草案生成后，必须先输出可独立确认的人话总结；总结要让用户不打开 Markdown 也能判断方向对不对。
- 人话总结必须覆盖该文件中所有需要用户拍板的业务结论：
  1. 这份文档当前草案实际确认了什么。
  2. 对哪些角色、流程、页面、数据、接口、测试、验收或业务结果会产生什么变化。
  3. 哪些内容仍未确认、只是候选、需要后续文档继续确认，或不属于当前文档确认范围。
  4. 用户确认后会锁定什么，并会进入哪份下一文档或哪一阶段。
- 用户可依据人话总结直接回复"对，就按这个理解执行"或指出哪里不对；这属于有效确认依据。
- "重点确认点"只能作为完整业务摘要后的辅助收口，不能替代人话总结。
- 不得默认要求用户"阅读文档后确认"，正式文档只作为追溯、开发、测试和复查依据。
- 草案未确认前，不得使用"已锁定"、"已确定"、"正式生效"等措辞；必须区分"当前草案理解/候选结论"和"确认后生效的结论"。
- 用户要求"用人话解释"、"总结一下这份文档"或类似说明时，必须保持当前文档仍为 `草案` 待确认；解释不改变文档状态。
- 解释结束后，必须重新给出确认对象和下一步：当前文档、当前草案版本、确认范围、用户可如何确认或指出偏差。
- 用户确认必须绑定当前文档、当前草案版本和确认范围；不得把一句"确认"错误理解为确认摘要本身、其他文档或其他范围。
- 草案版本优先使用文档头部版本、修订时间或本次草案明确标识；若文档无独立版本字段，则以当前文件路径和当前草案内容作为本次确认版本，不新增 runtime、日志体系、SoT、目录或状态机。
- **用户确认文档后，必须立即将该文档文件头部的 `状态` 字段从 `草案` 回写为 `已确认`。状态以文件内容为准，不得依赖对话记忆追踪。**
- **进入下一份文档前，必须先读取现有文档的状态字段，确认规划进度，不得凭记忆推断。**

### Per-Document Collaborative Confirmation Gate

每生成一份正式 SoT 文档草案前，必须执行 Per-Document Collaborative Confirmation Gate。

Planning Document Mode 每份文档的生成顺序：

```text
Select Next Document
→ Explain Document Purpose to Current User
→ Per-Document Collaborative Confirmation Gate
→ Confirm / Correct / Complete Missing Points
→ Generate Formal Document Draft
→ Role-Based Document Explanation Gate
→ User Confirmation
→ 回写文档状态：将文件头部 `状态` 从 `草案` 改为 `已确认`
→ 读取所有文档状态字段，确认规划进度
→ Conversation Continuity Gate
→ Move to Next Document
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

00、01、02 生成前的最少确认点：

- 00：当前项目真实状态、本期起点、本期目标变化、旧流程定位。
- 01：用户从哪里合法进入、每一步前置、不能跳过什么、成功结果、哪些旧路径禁止。
- 02：每一步依赖哪些业务事实、谁具备资格、哪些对象可产生什么结果、哪些旧对象绝不能影响新流程。
- 03：用户从哪里进入，什么条件下能做下一步，失败时看到什么、能怎么办，取消或失败后回哪里，哪些旧入口用户仍可能访问。
- 04：这条流程必须依赖哪些能力才能走通，哪些能力只是协作不应承担主责任，哪些旧能力绝不能再参与，缺少哪个能力时必须阻断。
- 05：本期最优先要先看到哪些页面，使用什么端、什么语言、什么视觉气质，是否已有品牌/Figma/截图/参考图，哪些页面或异常状态必须通过图明确表达，哪些局部变化需要单独做模块图，哪些交互现有页面图无法表达需要后续补 UX 图。
- 06：哪些业务事实证明流程可继续，什么事件会改变事实或状态，哪些状态必须持久化，哪些只是界面暂态，旧状态绝不能映射成什么新状态。
- 07：前端需要读什么、提交什么，后端必须返回什么、拒绝什么，哪些写操作需要幂等和并发处理，旧审批字段或旧接口是否必须封锁。
- 08：谁能对什么资源做什么动作，允许范围是什么，拒绝原因如何区分，工作人员只能协助到什么程度，历史对象只能在哪些范围只读。
- 09：现有系统哪些能力可以保留，哪些旧流程或旧逻辑绝不能再参与，这次变化要从哪里切换到新流程，出现问题时应该回退到什么可接受状态。
- 10：这项能力是否真的必须依赖外部服务，候选方案有哪些，选择时最在意兼容性/成本/稳定性/国内可用性/合规中的哪一项，能力不可用会阻断哪件核心业务。
- 11：用户必须按怎样的顺序完成这条业务，哪些错误/越权/旧路径/异常绝不能通过，哪些结果必须自动化证明，哪些必须在真机或真实环境确认。
- 12：哪些风险信号其实是同一个问题，哪些是必须先满足的依赖，哪些问题还没有拍板且会阻断任务。
- 13：哪些结论已经确认到可以执行，哪些 OPEN 还没关闭不能生成任务，哪些任务必须串行或可以并行，完成后要证明什么。
- 14 / 15：不单独进行生成前协作确认；13 确认后自动派生执行记录框架与验收框架，只预置待填写位置，不填写任何实际执行、验证、验收、发布或基线事实。

用户侧必须使用业务语言；不得要求用户直接回答"状态机"、"RBAC"、"对象关系"或"接口契约"。
不得把完整设计 checklist 扔给用户；默认每轮只问一个最关键问题。

03/04/05 文档确认门禁：

- Scenario Consistency Gate：每个 P0 FLOW 至少有一个 SCN；每个 SCN 只引用既有 FLOW；每个 SCN 的进入条件不弱于 FLOW 前置；每个关键异常有恢复、退出或人工协助路径；03 未新增主业务旅程；03 未改变 FLOW 的合法入口、终态或禁止路径。不满足时，03 不得确认。
- Module Coverage Gate：每个 P0 FLOW 有主模块；每个关键 SCN 有承接模块；每个模块有输入事实、输出能力、非责任和隔离边界；旧流程隔离模块明确保护哪些 FLOW；不存在模块循环依赖或模糊复用。不满足时，04 不得确认。
- UI/UX Design Readiness Gate：每个 P0 SCN 已映射 PAGE；每个 PAGE 有合法进入条件和 UI STATE；每个 UI STATE 有唯一主操作；全局风格提示词已准备；P0 页面提示词已准备；关键模块图需求已识别；UX 是否可由现有 UI 图覆盖已明确；需要出图但尚未收到资产的项已标记，不得伪造已确认。不满足时，05 的交互合同不得确认，涉及该页面的 UI 依赖开发任务不得生成或进入可执行状态。

05 设计确认记录复用既有 `UI_CONFIRMATION` 事件；不得新增设计日志、出图日志、UX Runtime 或独立资产数据库。

06/07/08 文档确认门禁：

- State Integrity Gate：每个 P0 FLOW 都有前置业务事实、触发事件、成功事实与阻断事实；每个关键状态均有唯一来源、分类、允许迁移、非法迁移与迁移守卫；交互暂态、派生动作状态、持久业务状态、异常状态、旧流程边界状态、数据域状态已区分；前端、路由、本地缓存、旧审批、旧入口不得成为业务状态来源；旧对象与旧状态均有明确不可映射目标。不满足时，06 不得确认。
- API Contract Gate：每个 P0 FLOW 至少有 QUERY、COMMAND、DECISION_VIEW 或 LEGACY_BOUNDARY 合同承接；每个 COMMAND 都引用 06 的业务事件、前置事实和迁移守卫；每个 COMMAND 都有幂等和并发语义；每个 API 都声明访问上下文、业务资格和错误恢复方向；旧审批字段、旧审批状态、旧审批接口无法进入新 COMMAND 的输入、判断或返回；每个 API 都有正向与反向 TEST 映射。不满足时，07 不得确认。
- Permission Decision Gate：每个关键 COMMAND 都有 PERM-ID；每个 PERM 都明确动作、资源、允许主体、允许范围、资格、状态前置和数据域前置；权限拒绝、范围拒绝、状态阻断、旧流程阻断、数据域阻断、外部能力阻断已区分；工作人员协助能力没有越权；历史对象只读边界已明确；每个关键 PERM 均有自动化测试映射。不满足时，08 不得确认。

09/10/11 文档确认门禁：

- Architecture Binding Gate：每条 P0 FLOW 都有逻辑架构承接位置；每个 Canonical API Contract 都有 Architecture Binding；每项旧资产都明确允许复用什么技术基础、禁止复用什么业务语义；旧审批、旧入口、旧状态无法进入新 Command、新 State 或新 Decision View；外部能力未完成 10 选型时，不得伪装为具体 Provider 已确认；架构风险只移交 12，不在 09 重复定义正式 RISK。不满足时，09 不得确认。
- Capability Decision Gate：每项外部能力都有 CAP-ID；每个 CAP 都关联 FLOW、MODULE、ARCH、TEST 和 RISK；每个 CAP 都明确候选方案、选型状态、选择理由、官方事实和关键前提；官方事实、权限、鉴权、版本、配额、计费、目标端兼容性未确认时，必须标记阻断范围；页面可打开、JSSDK ready、Mock 成功、代码存在，均不得视为真实能力成功；未完成 Capability Development-Entry Evidence Gate 的 CAP，不得进入相关开发任务；planning 阶段不得标记 `real_environment_verified` 或 `release_ready`。不满足时，10 不得确认。
- Test Design Gate：每条 P0 FLOW 都有正向业务流程测试；每条 P0 FLOW 都有前置阻断、状态、接口、权限、旧流程和回归测试；涉及外部能力的 FLOW 都有真实环境能力测试；涉及页面和交互的 FLOW 都有 UI 行为或 UX 测试；每条测试都明确自动化等级；11 中的测试顺序与 01 FLOW 顺序一致；11 不记录实际测试结果。不满足时，11 不得确认。

12/13/14/15 文档确认门禁：

- Risk / Dependency / Open Item Gate：每个正式 RISK 已归并为唯一风险；每个 BLOCKER 有阻断阶段、处理策略与关闭条件；每个 DEP 有验证来源和最晚解除阶段；每个 OPEN 有回写目标和确认主体；关键 OPEN 未关闭时，相关任务不得进入 13；12 不重复定义已确认业务规则、状态、接口、权限或 UI 事实。不满足时，12 不得确认。
- Task Contract Gate：只校验 13 自身及其上游 01–12；每条 P0 FLOW 至少有一个主 TASK；每个 TASK 可追溯到已装配且已确认的 FLOW / STATE / API / PERM / ARCH / TEST；关键 OPEN 已关闭；每个 CAP 任务只引用已确认的选型与门禁；每个旧流程隔离要求均被至少一个 TASK 承接；每个 TASK 有 Ready Gate、完成合同和回写目标。不满足时，13 不得确认。14、15 的预先存在不得作为 13 确认前置。
- Execution and Acceptance Framework Derivation Gate：13 已确认并回写后才运行；14 已按全部 TASK 预置 `EXEC-<TASK-ID>` 空白项；14 已继承 TASK 的目标、完成合同、预期 TEST、RISK / DEP / CAP 阻断与偏差回写位置；15 已按全部 P0 FLOW 和 TEST-ID 预置验收项，并包含 CAP 真实环境要求、RISK 关闭条件、DEP 解除条件、发布门禁和基线更新条件；14、15 只使用已确认 01–13 的引用；框架生成状态、框架完整性、用户独立确认和实际事实状态分别为 `generated` / `complete` / `not_required` / `not_started`；不得填写实际改动、验证通过、联调完成、通过、失败、已验收、可发布、已发布、生产已更新或基线已更新；Gate 通过后才允许生成实际 `assembled_documents`、唯一正式 Handoff Package 并标记 Planning Handoff Complete。

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

1. 确认对象：当前文档、当前草案版本、确认范围。
2. 这份文档用人话说是什么：用当前使用者能听懂的话说明当前草案在表达什么。
3. 当前草案理解：说明这份文档实际把哪些业务结论写成了草案。
4. 影响变化：说明它会让哪些角色、流程、页面、接口、数据、测试、验收或业务结果发生什么变化。
5. 仍未确认或候选内容：说明哪些只是候选、哪些需要后续文档再确认、哪些不在当前确认范围。
6. 确认后生效的内容：说明用户确认后会把哪些草案结论改为已确认，并进入哪一份文档或哪一阶段。
7. 重点确认点：在完整业务摘要之后，给出 2 到 5 个当前使用者最应该确认的业务点。
8. 可以不用细看什么：告诉使用者哪些专业 ID、引用、格式、技术细节可以不用逐字看。
9. 哪些错了会返工：说明最可能导致返工的 1 到 3 个点。
10. 可以怎么回复：例如"对，就按这个理解执行""范围不对，少了……""这个先不做""这里我不确定，你帮我再解释一下"。
11. 下一步：说明确认后进入哪一份文档或哪一阶段，以及为什么。

规则：

- 必须根据 `.plan/user-profile.yaml` 和 User Context Gate 的结果调整解释方式。
- 面向非专业使用者时，不要求其阅读完整专业文档。
- 岗位化解释不替代正式 SoT。
- 岗位化解释不进入 Handoff、Capability Registry 或正式文档正文。
- 人话总结本身不改变文档状态；只有用户确认了绑定的当前文档、当前草案版本和确认范围后，才允许回写 `状态: 已确认`。
- 禁止只输出"你重点看 X 点"、"可以不用细看 ID 和格式"这类收口内容。
- 禁止默认让用户打开 Markdown 后再确认。
- 在用户确认前，必须使用"当前草案理解"、"候选结论"、"确认后会锁定"等措辞，不得提前说已经锁定、已确定或正式生效。
- Role-Based Document Explanation Gate 不得替代生成前的 Per-Document Collaborative Confirmation Gate。
- Per-Document Collaborative Confirmation Gate 不得替代生成后的 Role-Based Document Explanation Gate。

错误示例：

```text
你重点看 3 点：范围、验收和风险。可以不用细看文档里的 ID、引用和格式。
```

正确示例：

```text
确认对象：00-需求背景与目标，当前草案版本，以本次生成后的文件内容为准；确认范围是本期为什么做、先解决什么问题、什么算方向正确。

这份文档用人话说是：当前草案认为第一期先解决"上传 UI 图后生成可查看的静态原型"这件事，不把复杂交互、多人协作和自动发布放进第一期。

它会让开发优先做上传入口、识别后的画布展示和基础验收；测试会重点证明一张图能稳定生成静态结果；暂时不会要求测试复杂交互或发布链路。

目前还没定的是后续是否做编辑、协作和发布，这些只是候选方向，不属于 00 这份文档的确认范围。

你只要确认这是不是你要的方向；确认后我会把 00 标记为已确认，并进入 01-需求范围与验收标准。
```

#### User-Facing ID Translation Rule

规则：

- 正式 SoT 文档中必须保留 `REQ`、`FLOW`、`SCN`、`DOMAIN`、`MODULE`、`CAP`、`PAGE`、`UI-MOD`、`UX-SCN`、`PROMPT-*`、`ASSET`、`STATE`、`API`、`PERM`、`TASK`、`RISK`、`DEP`、`OPEN`、`EXEC`、`TEST` 等 ID。
- 用户态解释中不得把 ID 作为主要确认对象。
- 用户态不得直接问"REQ-001 是否准确？""API-001 是否没问题？""CAP-MAP-001 是否确认？""TASK-001 是否可以执行？"。
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
- 在"你现在重点确认什么"里只列 ID。
- 在"可以怎么回复"里要求用户引用 ID。
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

- 只以"请确认"结尾。
- 只以"已完成"结尾。
- 只以"等待用户回复"结尾。
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
- 直接问"你是什么身份？"
- 直接问"你是什么职位？"
- 直接问"谁在使用？"
- 直接问"谁能用系统完成什么事情？"
- 直接问"什么算完成？"
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
  - 用"请回答以下问题"推进
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
可以，我先不急着问功能细节。先确认一下：这次你是想让我站在"帮你定方向"的角度推进，还是站在"帮你拆开发任务"的角度推进？
```

当用户明显不懂技术时：

```text
没事，你不用按专业格式说。我先按真实使用场景带你梳理，后面我再翻译成开发文档。
```

当用户明显不满时：

```text
对，这里不能直接抛"谁用、完成什么"这种问题，太像表格了。我先重新接：你现在启动这一期，是想让我先帮你定范围，还是已经有材料要我整理成开发计划？
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

当需求提到或暗示地图、支付、OCR、AI、语音、推送、对象存储、第三方平台、SDK、OpenAPI、MCP、外部 SaaS、平台能力、JSAPI、SDK Runtime、小程序能力、开放平台能力、企业协作平台能力、RecorderManager、定位、相机或同类提供方能力时：

1. 识别该能力。
2. 创建或更新 10 的 Capability Decision Card；已有 Capability Registry 只作为治理证据复用。
3. 确认官方 SoT。
4. 完成 Capability Development-Entry Evidence Gate。
5. 对于平台能力，识别 Capability Realization Requirement 与 Capability Acceptance Requirement 的后续证明要求。
6. 明确发布前真实验证要求，但不写成 planning 阶段已通过。
7. 然后才允许相关开发任务进入可执行状态。

如果 Capability Decision Card、Capability Registry 或官方 SoT 缺失，则在生成任何开发任务前先执行 Capability Discovery：

- 查官方文档
- 查官方 SDK
- 查官方 OpenAPI
- 查官方 GitHub
- 查官方控制台
- 需要时查 MCP Server

只把发现结果记录为待确认的 Capability Candidate，然后继续进入 Capability Decision Card、Capability Registry 和 Capability Development-Entry Evidence Gate。发现本身不允许直接进入生产代码或已确认的开发任务。

只要任何外部能力存在以下任一情况，就不要直接进入实现：

- 没有 `CAP-ID`
- 没有官方 SoT
- SDK 或 API 版本不明确
- 认证不明确
- 请求或响应结构未确认
- 没有兜底策略
- 没有架构承接边界
- 11 未设计真实环境验证要求
- 12 未收口关键 RISK / DEP / OPEN
- 存在阻断该 TASK 的关键 OPEN

不要仅凭以下信号就把平台能力标记为完成：

- 页面打开
- OAuth
- UA 检测
- 容器检测
- JSSDK ready
- Mock 成功
- 代码存在

## 输出规则

- 让规划内容保持结构化、可检索。
- 优先使用 ID、字段、引用、状态值和表格。
- 保持 skill 规则低熵，但不要把正式产物压缩到低于企业级最低完整度。
- `11-测试方案与验收用例.md` 只定义测试设计：按什么业务顺序证明什么、测试类型、自动化等级、真实环境要求和预期证明结果。
- 每条 P0 FLOW 都要生成结构化 TEST-ID 和 FLOW—测试覆盖矩阵，覆盖正向、状态、API、权限、旧流程、回归和必要的 CAP/UI/UX 测试。
- 不要在规划文档里定义测试代码、测试命令、fixture 脚本、测试执行调度、失败重试命令、实际执行状态、实际证据内容或实际测试结果。
- 不要在专门的 UI 提示区之外添加长解释、提示词式文本或重复规则。
- 不要让一个文档定义另一个文档的事实。
- 不要通过"已有旧代码"绕过业务规划结论；旧代码只能作为待核实来源，不是当前生产事实。
- 不要把计划、验收、已开发未发布和已上线生产状态混写。
- 不要把用户使用的 UI 出图工具当作产品运行时外部能力；不得仅因此强制创建 Capability Registry。
- 不要虚构 UI 图、设计资产路径或“已出图/已确认”结论。
- 不要把页面图、模块图或 UX 图标记为已开发、已测试、已验收或已上线。
- 不要让 06 定义物理数据库结构、表名、字段类型、索引、外键、SQL、ORM Schema 或迁移脚本。
- 不要让 07 定义完整页面交互、完整权限矩阵或数据库实现细节。
- 不要让 08 定义接口字段、接口响应结构、页面样式或业务状态枚举。
- 不要让旧接口、旧审批、旧状态以“兼容”名义参与新流程。
- 不要让 09 变成代码设计文档。
- 不要让 10 变成 SDK 实施文档。
- 不要让 11 变成测试执行日志或测试脚本。
- 不要让 12 重复定义已确认业务规则、状态、接口、权限或 UI 事实。
- 不要让 13 在关键 OPEN 未关闭、能力选型未确认、接口合同未确认或旧流程处理方式未确认时生成 TASK。
- 不要让 14 填写任何实际开发、联调、自动化验证、真实环境或发布事实。
- 不要让 15 填写任何实际验收、真实环境通过、发布、生产更新或 PROJECT-CURRENT-BASELINE 更新事实。
- 不要让 14/15 自动写入 `文档状态：已确认`，也不要把其框架生成解释为实际开发、验证、验收、发布或基线更新已完成。
- 不要把 Mock、页面打开、JSSDK ready 或代码存在误写为真实能力通过。
- 除非是 L 级变更或用户要求全链路，否则不要默认生成全部规划文档；只按需求形态动态装配必要文档。
- 在 Planning Completion Gate 通过前，不要进入 Planning Document Mode。
- 当 Planning Context 处于 INCOMPLETE 时，不要生成最终 SoT 文档。
- 一次不要生成多份 SoT 文档草案；每份文档都必须在下一份起草前先确认。
- 14、15 是 13 已确认后的派生框架对，不触发“每次只能生成一份正式文档”的限制，不需要分别进行生成前协作确认，也不需要把 14、15 的独立用户确认作为 Planning 完成前提。
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
- 可以简短说明"现在先不直接开发，需要先把第一期目标聊清楚"
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
Project Current Baseline：
Project Current State Gate：
Capability Registry：
Capability Development-Entry Evidence Gate：
Capability Realization Requirement：
Capability Acceptance Requirement：
Discovery Sufficiency：
Flow Completeness：
Journey-Object Consistency：
Scenario Consistency：
Module Coverage：
UI/UX Design Readiness：
State Integrity：
API Contract：
Permission Decision：
Architecture Binding：
Capability Decision：
Test Design：
Risk / Dependency / Open Item：
Task Contract：
Execution and Acceptance Framework Derivation：
影响分析：
阻塞项：
验收标准：
测试设计：
```

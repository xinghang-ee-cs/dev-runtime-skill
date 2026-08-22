# Planning Document Interaction Runtime

本文件是 Planning Document Mode 中批量草案装配、依次解释确认、定向修正和状态回写的唯一事实来源。

本文件不新增规划生命周期，不新增 Runtime 状态机，不替代 `03-planning-doc-responsibility.md`、`04-planning-format-spec.md`、`06-planning-capability-governance.md` 或 `07-planning-conversation-runtime.md`。

## 0. 交互目标与用户反馈事务

Planning Document Mode 必须复用 Discovery 首轮已经按 `04-planning-format-spec.md` 创建的：

```text
<phase_planning_runtime_directory>/current-interaction.yaml
```

不得从 Skill 目录复制文件。

如果进入 Planning Document Mode 时该文件不存在，说明逐轮 Discovery 持久化前置未完成，必须回到 `07-planning-conversation-runtime.md#321-discovery-round-transaction` 恢复；不得临时补造一个只含执行交接或文档状态的文件。不得再创建第二个 Planning Context、交接状态或文档装配状态文件。

Discovery 问答事务由 `07` 维护；本文件从执行交接分支确认与文档交互开始继续复用同一 `active_interaction / latest_feedback` 字段，不重复定义 Discovery 生命周期。

### 0.1 发问前持久化确认目标

生成或选择任何待确认内容后，必须先写 `active_interaction`，再向用户输出说明、问题或确认请求：

```text
生成或选择当前待确认内容
-> 持久化 target_type / target_id / stage / version / scope
-> 持久化 expected_user_action / next_step
-> 再向用户发问
-> 用户回复后立即记录 latest_feedback
-> 校验绑定
-> 应用反馈
```

适用于：

- 执行交接分支确认。
- 批量装配因事实不足而回流第一阶段时的阻断事实确认。
- 05 确认过程中的 UI/UX Prompt 交付、设计图接收与视觉确认。
- 文档草案生成后确认。
- 用户要求解释后的再次确认。
- 风险或冲突确认。
- 最终人话总结确认。

禁止等用户回复后再从对话记忆推断确认对象。文档交互使用真实文档路径作为 `target_id`；最终总结使用 `target_type: final_summary`，不得伪装成正式文档。

执行交接分支确认复用同一反馈事务，唯一顺序：

```text
生成 execution_handoff_decision 候选
-> 写入本期 current-interaction.yaml
-> active_interaction 绑定该确认目标
-> 再向用户说明是否会形成开发执行任务
-> 用户回复后先记录 latest_feedback
-> 校验绑定
-> 应用反馈
-> decision_status: confirmed
```

绑定格式：

```yaml
active_interaction:
  target_type: execution_handoff_decision
  target_id: current_phase_execution_handoff_decision
  stage: execution_handoff_confirmation
  version:
  scope: 本期是否形成开发执行任务
  expected_user_action: confirm_or_correct
  next_step: planning_context_complete
```

### 0.2 用户反馈处理顺序

任何可能影响文档状态、确认状态、当前阶段、待确认对象、文档内容、下一步动作、暂停/回退或 Planning 完成判断的用户输入，都必须先写入 `latest_feedback`。

唯一处理顺序：

```text
收到用户输入
-> 记录用户反馈
-> 绑定当前对象
-> 判断反馈类型
-> 校验是否允许应用
-> 若反馈包含会影响规划的可公开核验事实，执行由 07 编排的 Discovery Fact Research Gate，核验并持久化最小来源
-> 应用到对应文档或阶段
-> 标记反馈处理结果
-> 再决定是否进入下一步
```

禁止先改文档、推进阶段或回复确认结果，再依赖聊天上下文补记。字段和枚举以 `04-planning-format-spec.md#12-current-interactionyaml-最小格式` 为唯一来源。

绑定与幂等规则：

- 反馈到达时，立即复制当时已持久化的 `active_interaction` 目标类型、ID、阶段、版本与确认范围。
- 同一时间只允许一条未完成反馈；上一条仍为 `recorded` 或 `validated` 时，必须先恢复并处理，不得被新状态变更反馈覆盖。
- 不得进入下一文档或下一交互目标后重新解释、转移或重复消费这条反馈。
- 同一个 `feedback_id` 只能成功应用一次。
- 同一反馈不得同时确认当前文档并推进确认下一文档。
- 若目标文档已达到反馈预期状态，写入 `apply_status: already_effective`，不得重复修改或作用到下一文档。
- 无唯一合法待确认对象、目标版本不匹配或确认范围不明确时，写入 `needs_clarification`，不得猜测或改变任何文档状态。

自然语言分类：

- “确认”只在存在唯一合法待确认对象时记为 `confirm` 并允许改变该对象状态。
- “继续”记为 `continue`，只表示继续当前合法步骤，不自动等同于确认草案。
- “讲一下”“第 X 份说了什么”记为 `ask_explanation`；只解释目标文档，不改变草案状态。
- 用户补充事实记为 `supplement`；先判断事实归属的 SoT，再决定是否回写。
- 当前目标是 `design_asset_batch` 时，用户上传图片或提供图片引用记为 `supplement`：先绑定当前批次，再写回对应 `ASSET-ID@revision`；上传行为不得被分类为图片视觉确认或 05 文档确认。
- 用户纠正记为 `correct`；回写真正拥有该事实的上游 SoT，并按 `08-planning-recovery-runtime.md` 检查下游失效。
- `supplement` 或 `correct` 涉及产品当前能力、版本限制、公开规范、法律监管或其他可核验事实时，必须在反馈已记录后先按 `07` 调研；可靠公开证据可以消除事实提问，但不得未经用户确认改变业务适用性、当前范围或已确认 SoT。
- 调研发现的新功能或替代方案只作为候选；确认延期时写入 Requirement Pool，确认纳入时回到真正拥有该事实的上游 Planning Context / SoT 并执行失效传播。
- “先暂停”记为 `pause`；“回到上一份”记为 `return_to_previous`，均不得隐式确认当前草案。
- 无法可靠分类时记为 `unknown` 与 `needs_clarification`。

`raw_user_input` 只允许在 `recorded`、`validated`、`needs_clarification` 状态保留。反馈进入 `applied`、`already_effective` 或 `rejected` 后必须清空原文，只保留 `normalized_summary`、反馈类型、目标、处理结果和下一步。历史证据按需进入 `event-log.md`，不得复制完整聊天，也不得把反馈写入 Skill 目录或 `.runtime/planning-layer-runtime/user-profile.yaml`。

## 1. 文档确认规则

- 本期全部计划装配文档草案完成批量生成与跨文档校验后，才进入用户确认队列；不得在批量生成中途打断用户逐份确认。
- 轮到某份正式文档草案时，必须先输出可独立确认的人话总结；总结要让用户不打开 Markdown 也能判断方向对不对。
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
- 用户确认文档后，必须立即将该文档文件头部的 `状态` 字段从 `草案` 回写为 `已确认`。状态以文件内容为准，不得依赖对话记忆追踪。
- 进入下一份文档前，必须先读取现有文档状态和 `document_assembly.confirmation_queue`，确认规划进度，不得凭记忆推断。

## 2. Batch Draft Assembly And Sequential Confirmation Gate

Planning Document Mode 分为两个连续但不交错的阶段：先批量生成全部草案，再依次确认。

唯一顺序：

```text
Freeze Document Assembly Plan
-> Persist batch_revision and planned_roles
-> Generate all applicable 00–12 and optional 13 drafts in dependency order
-> After each file write, persist real path / draft revision / status in generated_documents
-> Run cross-document reference, responsibility and draft completeness checks
-> If missing Planning fact is found: stop batch, persist blocker, return to Discovery for one blocking fact
-> If batch succeeds: draft_generation_status = generated
-> Build confirmation_queue from real generated paths
-> Select first confirmation item
-> Persist draft_confirmation Target
-> If current item is 05 and required design assets are not visual_confirmed: run Design Asset Collection Interaction Gate
-> Role-Based Document Explanation Gate
-> Receive feedback and persist before processing
-> Validate Feedback Binding
-> Confirm or Correct
-> On confirm: write document 状态 = 已确认 and queue status = confirmed
-> On correction: update owning SoT and regenerate only affected downstream drafts
-> Re-run affected cross-document gates and refresh their draft revisions / queue status
-> Select next earliest unconfirmed or reopened item
-> Continue until all applicable 00–13 documents are confirmed
-> If 13 exists and is confirmed: derive 14/15 frameworks
```

批量生成规则：

- 草案仍按依赖拓扑生成，不按用户确认轮次决定生成顺序。
- 第二阶段不得重新逐文档访谈；生成所需事实必须来自已持久化 Discovery、Planning Context、项目证据、调研结果和已确认外部基线。
- 批量生成是一个用户不可见的完整装配步骤，但每写入一份文件都必须立即更新 `current-interaction.yaml.document_assembly`，避免中断或压缩后重复生成。
- 只有本期所有计划装配的 00–12 与可选 13 草案都真实存在、路径可回读且跨文档草案校验完成后，才向用户发出第一份文档确认。
- 13 草案可以随 00–12 一起批量生成，但此时只能是 `草案`；13 的 Task/Implementation/UI Execution Gate 仍在轮到 13 确认前基于已经确认的上游文档重新运行。
- 14、15 不参与初始批量草案生成；只在 13 已确认后自动派生。
- 批量生成中发现第一阶段事实不足时，停止装配并回到 Discovery，只问当前阻断的一个事实；不得边生成边向用户追加文档问题。
- 初始批量允许 05 以 `planned / prompt_ready` ASSET 和 `blocked` Manifest 形成完整草案；这不允许跳过第二阶段的 Design Asset Collection Interaction Gate，也不允许伪造实际图片路径或 `visual_confirmed` 状态。

依次确认规则：

- 默认按依赖顺序确认；可以合并纯框架说明，但不得把多个需要用户拍板的 SoT 文档合成一次模糊确认。
- 每轮只激活一个真实文档路径和 draft revision，继续复用现有反馈事务。
- 用户确认一份文档不自动确认其他草案。
- 用户纠正时先改真正拥有事实的文档；已生成但受影响的下游草案立即重建并提升 draft revision。
- 已确认文档若被上游纠正真实命中，状态改回 `草案` / queue status `reopened`；未受影响的已确认文档保持不变。
- 修正完成后从最早的 `reopened` 或 `pending_confirmation` 文档继续，不重新批量生成全部文档。
- 用户可以要求跳到某份文档解释，但不得绕过其未确认上游来确认下游。

`document_assembly` 必须形成可恢复队列：

```yaml
batch_revision:
draft_generation_status: <pending | generating | generated | blocked | invalidated>
generated_documents:
  - role:
    path:
    draft_revision:
    document_status: <draft | confirmed | reopened | invalidated>
confirmation_queue:
  - role:
    path:
    draft_revision:
    confirmation_status: <pending_confirmation | awaiting_feedback | confirmed | reopened | invalidated>
current_confirmation:
  role:
  path:
  draft_revision:
generation_blocker:
  owning_role:
  unresolved_item_ref:
  resume_condition:
assembly_status: <batch_assembling | awaiting_confirmation | confirming | rebuilding | blocked | complete>
```

## 3. Batch Assembly Input Completeness Check

以下内容必须在第一阶段 Discovery / Planning Context 中已经确认、由项目证据或公开调研核实，或明确登记为不阻断项。它们是批量草案装配的内部输入检查，不是在第二阶段逐文档重新询问用户的题单。

00、01、02 生成前的最少确认点：

- 00：当前项目真实状态、本期起点、本期目标变化、旧流程定位。
- 01：用户从哪里合法进入、每一步前置、不能跳过什么、成功结果、哪些旧路径禁止。
- 02：每一步依赖哪些业务事实、谁具备资格、哪些对象可产生什么结果、哪些旧对象绝不能影响新流程。
- 03：用户从哪里进入，什么条件下能做下一步，失败时看到什么、能怎么办，取消或失败后回哪里，哪些旧入口用户仍可能访问。
- 04：这条流程必须依赖哪些能力才能走通，哪些能力只是协作不应承担主责任，哪些旧能力绝不能再参与，缺少哪个能力时必须阻断。
- 05：本期最优先要先看到哪些页面，使用什么端、什么语言、什么视觉气质，是否已有品牌/Figma/截图/参考图，哪些页面或异常状态必须通过图明确表达，哪些局部变化需要单独做模块图，哪些交互现有页面图无法表达需要后续补 UX 图；准备交给开发时，还必须确认 Prompt 目标工具/输出规格、页面布局与响应式边界、状态反馈、内容长度、键盘焦点、可访问性、动效反馈、设计资产 revision 和允许/禁止偏离范围。能从项目设计体系、已确认资产或公开工具事实核实的内容先调研并写入，不把事实问题重复问用户。
- 06：哪些业务事实证明流程可继续，什么事件会改变事实或状态，哪些状态必须持久化，哪些只是界面暂态，旧状态绝不能映射成什么新状态。
- 07：前端需要读什么、提交什么，后端必须返回什么、拒绝什么，哪些写操作需要幂等和并发处理，旧审批字段或旧接口是否必须封锁。
- 08：谁能对什么资源做什么动作，允许范围是什么，拒绝原因如何区分，工作人员只能协助到什么程度，历史对象只能在哪些范围只读。
- 09：现有系统哪些能力可以保留，哪些旧流程或旧逻辑绝不能再参与，这次变化要从哪里切换到新流程，出现问题时应该回退到什么可接受状态。
- 10：这项能力是否真的必须依赖外部服务，候选方案有哪些，选择时最在意兼容性/成本/稳定性/国内可用性/合规中的哪一项，能力不可用会阻断哪件核心业务。
- 11：用户必须按怎样的顺序完成这条业务，哪些错误/越权/旧路径/异常绝不能通过，哪些结果必须自动化证明，哪些必须在真机或真实环境确认。
- 12：哪些风险信号其实是同一个问题，哪些是必须先满足的依赖，哪些问题还没有拍板且会阻断任务。
- 13：哪些结论已经确认到可以执行，哪些 OPEN 还没关闭不能生成任务，哪些任务必须串行或可以并行，完成后要证明什么。
- 14 / 15：不进入初始草案批次，也不进入独立确认队列；13 确认后自动派生执行记录框架与验收框架，只预置待填写位置，不填写任何实际执行、验证、验收、发布或基线事实。

若任一缺失项会阻断正确装配：停止批量生成，持久化 `draft_generation_status: blocked` 和 `generation_blocker`，回到第一阶段用业务语言只问一个当前阻断事实；回答持久化并重新达到 Planning Context COMPLETE 后，清空 blocker 并从未完成的批量装配检查点继续。不得把完整 checklist 扔给用户，也不得把第二阶段变成补访谈流程。

## 4. 文档确认门禁

03/04/05 文档确认门禁：

- Scenario Consistency Gate：每个 P0 FLOW 至少有一个 SCN；每个 SCN 只引用既有 FLOW；每个 SCN 的进入条件不弱于 FLOW 前置；每个关键异常有恢复、退出或人工协助路径；03 未新增主业务旅程；03 未改变 FLOW 的合法入口、终态或禁止路径。不满足时，03 不得确认。
- Module Coverage Gate：每个 P0 FLOW 有主模块；每个关键 SCN 有承接模块；每个模块有输入事实、输出能力、非责任和隔离边界；旧流程隔离模块明确保护哪些 FLOW；不存在模块循环依赖或模糊复用。不满足时，04 不得确认。
- UI/UX Design Readiness Gate：每个 P0 SCN 已映射 PAGE；每个 PAGE 有合法进入条件和 UI STATE；每个 UI STATE 有唯一主操作；全局风格提示词或继承基线已准备；P0 Prompt 具有可直接复制的完整 `prompt_body` 与输出规格；本期 PAGE/UI-MOD 已具备 UI Implementation Contract；关键 UX-SCN 已具备确定性状态迁移表；设计资产带 revision、真实路径和独立确认状态；05 Manifest 对内部引用完整，并以 `design_ready` 或带明确原因的 `blocked` 表示当前阶段；`scripts/validate_ui_ux_contract.py --allow-design-ready`、`--allow-blocked` 或同等结构校验通过。不要求此时尚未生成的 11、13 或 Handoff 引用；这些引用由后续 UI/UX Execution Readiness Gate 收口。存在必需 UI/UX 图时，必须先完成 5.1 的用户态 Prompt 交付、图片接收和视觉确认，且 `design_asset_collection.collection_status: complete`；需要出图但尚未收到或未确认的资产不得伪造，05 不得整体确认，相关 UI TASK 不得 Ready。

05 设计确认记录复用既有 `UI_CONFIRMATION` 事件；不得新增设计日志、出图日志、UX Runtime 或独立资产数据库。

06/07/08 文档确认门禁：

- State Integrity Gate：每个 P0 FLOW 都有前置业务事实、触发事件、成功事实与阻断事实；每个关键状态均有唯一来源、分类、允许迁移、非法迁移与迁移守卫；交互暂态、派生动作状态、持久业务状态、异常状态、旧流程边界状态、数据域状态已区分；前端、路由、本地缓存、旧审批、旧入口不得成为业务状态来源；旧对象与旧状态均有明确不可映射目标。不满足时，06 不得确认。
- API Contract Gate：每个 P0 FLOW 至少有 QUERY、COMMAND、DECISION_VIEW 或 LEGACY_BOUNDARY 合同承接；每个 COMMAND 都引用 06 的业务事件、前置事实和迁移守卫；每个 COMMAND 都有幂等和并发语义；每个 API 都声明访问上下文、业务资格和错误恢复方向；旧审批字段、旧审批状态、旧审批接口无法进入新 COMMAND 的输入、判断或返回；每个 API 都有正向与反向 TEST 映射。不满足时，07 不得确认。
- Permission Decision Gate：每个关键 COMMAND 都有 PERM-ID；每个 PERM 都明确动作、资源、允许主体、允许范围、资格、状态前置和数据域前置；权限拒绝、范围拒绝、状态阻断、旧流程阻断、外部能力阻断已区分；工作人员协助能力没有越权；历史对象只读边界已明确；每个关键 PERM 均有自动化测试映射。不满足时，08 不得确认。

09/10/11 文档确认门禁：

- Architecture Binding Gate：每条 P0 FLOW 都有逻辑架构承接位置；每个关键模块已选择实现承接策略并关联稳定业务概念；`create_stable_business_domain` 已说明现有域无法承接的原因和跨期独立意义；每个 Canonical API Contract 都有 Architecture Binding；每项旧资产都明确允许复用什么技术基础、禁止复用什么业务语义；旧审批、旧入口、旧状态无法进入新 Command、新 State 或新 Decision View；外部能力未完成 10 选型时，不得伪装为具体 Provider 已确认；架构风险只移交 12，不在 09 重复定义正式 RISK。不满足时，09 不得确认。
- Capability Decision Gate：每项外部能力都有 CAP-ID；每个 CAP 都关联 FLOW、MODULE、ARCH、TEST 和 RISK；每个 CAP 都明确候选方案、选型状态、选择理由、官方事实和关键前提；官方事实、权限、鉴权、版本、配额、计费、目标端兼容性未确认时，必须标记阻断范围；页面可打开、JSSDK ready、Mock 成功、代码存在，均不得视为真实能力成功；未完成 Capability Development-Entry Evidence Gate 的 CAP，不得进入相关开发任务；planning 阶段不得标记 `real_environment_verified` 或 `release_ready`。不满足时，10 不得确认。
- Test Design Gate：每条 P0 FLOW 都有正向业务流程测试；每条 P0 FLOW 都有前置阻断、状态、接口、权限、旧流程和回归测试；涉及外部能力的 FLOW 都有真实环境能力测试；涉及页面和交互的 FLOW 都有 UI 行为或 UX 测试；每条测试都明确自动化等级；11 中的测试顺序与 01 FLOW 顺序一致；11 不记录实际测试结果。不满足时，11 不得确认。

12/13/14/15 文档确认门禁：

- Risk / Dependency / Open Item Gate：每个正式 RISK 已归并为唯一风险；每个 BLOCKER 有阻断阶段、处理策略与关闭条件；每个 DEP 有验证来源和最晚解除阶段；每个 OPEN 有回写目标和确认主体；关键 OPEN 未关闭时，相关任务不得进入 13；12 不重复定义已确认业务规则、状态、接口、权限或 UI 事实。不满足时，12 不得确认。
- Task Contract Gate：只校验 13 自身及其上游 01–12；每条 P0 FLOW 至少有一个主 TASK；每个 TASK 可追溯到已装配且已确认的 FLOW / STATE / API / PERM / ARCH / TEST；关键 OPEN 已关闭；每个 CAP 任务只引用已确认的选型与门禁；每个旧流程隔离要求均被至少一个 TASK 承接；每个 TASK 有 Ready Gate、完成合同和回写目标；Implementation Naming Gate 与 Implementation Contract Completeness Gate 均通过。存在 UI TASK 时还必须通过 UI/UX Execution Readiness Gate，并以 execution-ready 默认校验验证 05、11、13 的精确绑定。不满足时，13 不得确认。14、15 的预先存在不得作为 13 确认前置；两道实现门禁的唯一检查项由 `07-planning-conversation-runtime.md` 维护。
- Execution and Acceptance Framework Derivation Gate：13 已确认并回写后才运行；14 已按全部 TASK 预置 `EXEC-<TASK-ID>` 空白项；14 已继承 TASK 的目标、完成合同、预期 TEST、RISK / DEP / CAP 阻断与偏差回写位置；15 已按全部 P0 FLOW 和 TEST-ID 预置验收项，并包含 CAP 真实环境要求、RISK 关闭条件、DEP 解除条件、发布门禁和基线更新条件；14、15 只使用已确认 01–13 的引用；框架生成状态、框架完整性、用户独立确认和实际事实状态分别为 `generated` / `complete` / `not_required` / `not_started`；不得填写实际改动、验证通过、联调完成、通过、失败、已验收、可发布、已发布、生产已更新或基线已更新；Gate 通过后只允许基于真实路径生成 `assembled_documents` 与交接信息并标记为 `prepared`，随后持久化最终总结确认目标，不得标记整个规划结束。

禁止：

- 在全部计划草案生成和批量校验完成前开始逐文档确认。
- 在批量生成过程中按每份文档打断用户补问或确认。
- 把完整文档 checklist 抛给用户。
- 让用户按专业字段回答。
- 在用户没有确认该文档关键点时，把 AI 推断写成 `confirmed`。
- 用批量生成替代后续逐文档确认。
- 用某一份确认替代其他文档确认。
- 用户纠正上游后全量重生成未受影响文档，或继续确认已失效下游草案。

Batch Draft Assembly 发生在任何文档确认前；Role-Based Document Explanation Gate 发生在批量生成完成后、当前文档确认前。两者不可交错。

## 5. Role-Based Document Explanation Gate

全部正式 SoT 草案批量生成完成后，对 confirmation queue 中当前这一份执行 Role-Based Document Explanation Gate。

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

- 必须根据 `.runtime/planning-layer-runtime/user-profile.yaml` 和 User Context Gate 的结果调整解释方式。
- 面向非专业使用者时，不要求其阅读完整专业文档。
- 岗位化解释不替代正式 SoT。
- 岗位化解释不进入 Handoff、Capability Registry 或正式文档正文。
- 人话总结本身不改变文档状态；只有用户确认了绑定的当前文档、当前草案版本和确认范围后，才允许回写 `状态: 已确认`。
- 禁止只输出"你重点看 X 点"、"可以不用细看 ID 和格式"这类收口内容。
- 禁止默认让用户打开 Markdown 后再确认。
- 在用户确认前，必须使用"当前草案理解"、"候选结论"、"确认后会锁定"等措辞，不得提前说已经锁定、已确定或正式生效。
- Role-Based Document Explanation Gate 只确认当前 queue item，不得替代完整批量草案装配或其他文档确认。
- 批量草案装配不产生用户确认，也不得省略后续 Role-Based Document Explanation Gate。
- 生成后收到的任何确认、纠正、补充、解释、继续、暂停或回退输入，都必须先按第 0 节写入 `current-interaction.yaml`。

### 5.1 05 Design Asset Collection Interaction Gate

当前 confirmation queue 项是 05，且本期需要 UI 图、局部模块图或 UX 图时，必须在 05 人话总结和正式文档确认前完成本 Gate。完整 Prompt 与资产格式以 `11-planning-ui-ux-execution-contract.md` 为准；本节只定义用户交互顺序。

唯一顺序：

```text
Read 05 asset plan and exact Prompt revisions
-> Assign or restore every required ASSET's stable image_sequence from 05
-> Build the next UI asset batch from at most 10 same-dependency required STYLE/PAGE/MODULE prompts
-> Persist design_asset_collection(prompt_ready) + design_asset_generation_request target
-> Output every prompt in this batch directly to the user with the fixed user-facing format
-> Persist collection_status = awaiting_assets
-> Ask the user to use any external image-generation tool or provide existing images, mapped by image_sequence
-> Receive files or external references and persist latest_feedback first
-> Bind each received image to ASSET-ID@revision and real path/reference
-> Mark received -> review_pending
-> If this batch is partial: keep awaiting_assets, request only missing ASSET refs and wait
-> When this batch is complete: persist collection_status = reviewing_assets
-> Persist design_asset_review_confirmation target
-> Explain visible coverage, known gaps and suspected contract mismatches
-> User confirms or requests correction
-> On confirm: mark exact UI ASSET revisions visual_confirmed
-> On correction: revise only affected Prompt/contract/ASSET revision, return to prompt_ready and resend it
-> If required UI prompts remain: build the next batch of at most 10 and repeat
-> Rebuild PROMPT-UX reference_inputs from visual_confirmed UI asset revisions
-> If an interaction image is required: repeat the same at-most-10 batch loop for UX prompts and UX images
-> If existing confirmed UI assets fully express the interaction: record covered_by_existing_ui_assets and skip UX image request
-> When every required UI/UX asset is visual_confirmed: collection_status = complete
-> Update 05 Manifest / contracts / coverage and affected downstream drafts
-> Run UI/UX Design Readiness Gate
-> Restore the current 05 draft_confirmation target
-> Continue to Role-Based Document Explanation Gate and 05 confirmation
```

用户态 Prompt 交付规则：

- 每个批次只能包含同一依赖层的 `1–10` 条 Prompt；即使剩余项超过 10 条也不得一次性全部输出。依赖边界或剩余数量不足 10 条时允许小批次，不得为了凑满而混入尚不具备依赖的 UX Prompt。
- 必须在聊天回复中直接按 11 §4.1 的唯一用户态格式交付本批次完整 Prompt，不得在本文件另定义或改写字段模板。不得只告诉用户“Prompt 已写入 05”、只给文件路径、只给锚点或要求用户自行打开 Markdown 复制。
- 批次开头说明当前批次、预计总批次、当前图片范围和可使用任意外部生图工具。没有内置生图工具不构成阻断，不得因此要求用户配置 API Key、CLI fallback 或特定厂商工具。
- UI Prompt 按依赖顺序分批提供 STYLE（适用时）、PAGE 和 UI-MOD Prompt；同层超过 10 条时继续下一批，不得无必要地一张图问一轮。UX Prompt 必须在其引用的 UI ASSET revision 已真实收到并完成视觉确认后提供，其 `参考的图片序号` 必须对应这些已确认 UI 图，避免引用不存在、旧版或仅存在于聊天描述中的图片。
- 用户已经有符合要求的 UI/UX 图时允许直接上传或提供真实外部引用，不强制重新生成；仍必须绑定 ASSET revision 并执行视觉确认。
- 必须明确告诉用户按稳定图片序号回传，并可同时给出建议文件名，避免多图无法归属。用户一次只提供部分图片时，已收到项立即持久化并保留；后续只列出和重发缺失或修订项，不要求重新上传未受影响图片。
- 一个批次完成视觉确认后，若仍有必需资产，必须主动交付下一批并重复“Prompt 交付 -> 外部生成/已有图回传 -> 审查 -> 用户确认”；直到全部必需 UI/UX 资产闭合。不得把“本批最多 10 张”误解为总共只处理 10 张，也不得在中途无故结束 05 设计资产收集。

视觉确认规则：

- 收到图片不等于确认。AI 先按 PAGE/UI-MOD/UX-SCN 合同检查覆盖状态、布局、主次操作、关键状态和明显冲突，再用人话说明差异并请求用户确认或重做。
- `visual_confirmed` 只能由绑定当前批次和当前 ASSET revision 的用户确认产生，并写回真实路径/引用、确认来源和时间；一句“确认”不得同时确认图片和 05 文档。
- 任一必需 UI/UX 图缺失、仍为 `review_pending` 或用户要求重做时，05 不得进入整体文档确认，`design_asset_collection` 保持未完成，相关 UI TASK 不得 Ready。
- 图片修订必须提升对应 ASSET revision；Prompt 或合同内容变化时同步提升其 revision，并只失效真实依赖旧 revision 的下游草案。
- 图片修订、批次切换和中断恢复不得重新编号。`design_asset_collection.active_prompt_refs` 与 `active_asset_refs` 按当次展示顺序保存，图片序号的唯一 SoT 仍是 05 ASSET 索引中的 `image_sequence`。
- 本 Gate 复用 `current-interaction.yaml`、05 ASSET 索引和既有 `UI_CONFIRMATION` 事件；不得新增出图日志、图片确认 Runtime 或第二份设计 SoT。

当前文档为 13 时，人话总结还必须说明：

- 规划文档里的追踪编号只用于前后关联，不会成为代码、数据库、接口或权限命名。
- 本期功能优先核实并承接哪些现有稳定业务域。
- 是否确实需要新建长期业务模块；需要时说明 09 的架构依据和长期业务概念。
- 数据域隔离不等于建立“第 X 期模块”或期次数据库命名空间。
- 哪些影响业务和验收的实现参数已经确认。
- 哪些纯技术参数已明确委托执行层，以及委托边界。
- 是否仍存在会让开发中途停止的关键参数缺口；存在时不得引导用户确认 13。

错误示例：

```text
你重点看 3 点：范围、验收和风险。可以不用细看文档里的 ID、引用和格式。
```

正确示例：

```text
确认对象：00-需求背景与目标，当前草案版本，以本次生成后的文件内容为准；确认范围是本期为什么做、先解决什么问题、什么算方向正确。

这份文档用人话说是：当前草案认为本阶段先解决“让已有任务列表支持可验证的多条件筛选”，暂不加入批量操作、跨组织协作和自动发布。

它会让开发优先完成筛选入口、查询条件和结果反馈；测试会重点证明筛选结果与业务规则一致；暂时不会要求验证批量操作或发布链路。

目前还没定的是后续是否做批量处理、协作和发布，这些只是候选方向，不属于 00 这份文档的确认范围。

你只要确认这是不是你要的方向；确认后我会把 00 标记为已确认，并进入 01-需求范围与验收标准。
```

## 6. User-Facing ID Translation Rule

规则：

- 正式 SoT 文档中必须保留 `REQ`、`FLOW`、`SCN`、`DOMAIN`、`MODULE`、`CAP`、`PAGE`、`UI-MOD`、`UX-SCN`、`PROMPT-*`、`ASSET`、`STATE`、`API`、`PERM`、`TASK`、`RISK`、`DEP`、`OPEN`、`EXEC`、`TEST` 等 ID；引用跨期需求时可以补充 `POOL-ID`，但不得把它当作本期 `REQ-ID`。
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
本阶段的核心目标是不是：让已有任务列表支持多条件筛选，并稳定返回符合业务规则的结果。文档里这个目标会被编号为 REQ-001，方便后续开发和测试追踪。
```

更推荐的非技术用户写法：

```text
本阶段的核心目标是不是只先做到：已有任务列表能够按确认的条件筛选并返回正确结果。你不用管文档里的编号，重点确认这个目标对不对。
```

禁止：

- 让用户确认裸 ID。
- 让用户通过 ID 判断业务内容。
- 在"你现在重点确认什么"里只列 ID。
- 在"可以怎么回复"里要求用户引用 ID。
- 用 ID 替代具体业务描述。

## 7. 本期最终人话总结确认

### 7.1 进入条件与状态

必须明确区分：

```text
Planning Context COMPLETE
!= 正式文档已经全部生成
!= 13 已确认
!= 14/15 框架已经生成
!= Planning 已真正结束
```

只有满足当前 Handoff 分支的进入条件后，才能输出最终人话总结。

共同条件：

- 本期所有实际装配文档已经生成并确认。
- `assembled_documents` 已基于真实路径生成。
- `handoff_role_mapping` 已基于真实路径生成，正式 Handoff 已准备但尚未标记 Complete。
- Handoff Branch Consistency Check 已通过；Planning Context、本期 `current-interaction.yaml` 恢复镜像、Document Assembly Plan 与 Handoff 的 `requires_execution_handoff / handoff_type` 一致，前三者的 `decision_status` 均为 `confirmed`。

当 `requires_execution_handoff: true`：

- Handoff 标记为 `execution_ready`。
- 13 已确认，14/15 已派生且 Execution and Acceptance Framework Derivation Gate 已通过。
- Task Contract Gate、Implementation Naming Gate、Implementation Contract Completeness Gate 已通过。
- Handoff 已包含 `execution_constraints`，且不存在 P0 `blocking_open` 参数。

当 `requires_execution_handoff: false`：

- Handoff 标记为 `planning_only`。
- Handoff 不包含 13、14、15 对应职责，也不包含针对代码实现的 `execution_constraints`。
- 不存在阻断本期规划结束的 OPEN。
- 不要求 13、14、15 或实现类 Gate。

输出总结前必须先写入：

```yaml
active_interaction:
  target_type: final_summary
  target_id: current_phase_final_summary
  stage: final_summary_confirmation
  version: <本次总结版本>
  scope: 本期最终业务理解与边界
  expected_user_action: confirm_or_correct
  next_step: planning_close

planning_status: awaiting_final_summary_confirmation
```

最后整体确认前，禁止把规划结束、完成交接或开始开发描述为已经发生的事实，例如“本期规划已结束”“规划已完成”“Plan 已完成”“已完成交接”或“现在已经可以直接开发”。允许明确的条件式未来表达：“确认后，本期规划正式结束。”所有分支都只能使用未来时或待确认状态。

### 7.2 汇总事实边界

最终总结只汇总已确认文档，不是新的 SoT，不得自行增加、改变或偷偷修正规则。根据本期实际内容动态装配，至少覆盖会影响本期成果使用方式或后续开发方向的内容：

- 本期为什么做、最终解决什么、用户实际怎么使用。
- 主要角色分别做什么，核心流程从哪里开始、到哪里结束。
- 关键业务判断、数据与权限边界、谁不能操作。
- 哪些数据只能由系统判断。
- 哪些旧入口、旧流程、旧审批、旧对象绝不能再影响新流程。
- 页面与交互的核心要求。
- 外部能力已确认到什么程度，哪些仍需真实环境验证。
- 测试必须重点证明什么，发布前必须满足什么。
- 当前仍存在但不阻断对应分支结束的依赖，以及本期明确不做什么。
- `execution_ready` 说明下一阶段由谁承接、开发过程在哪里记录实际改动，以及测试与验收过程在哪里记录真实环境、验收与发布判断；同时说明 14/15 框架生成不代表开发、测试、验收或发布完成。
- `planning_only` 说明本期成果如何使用、适用范围和后续何时需要重新进入开发规划；不得暗示已经形成开发执行任务。

用户态以业务白话为主，不以 Planning、FLOW、STATE、API、PERM、CAP、TASK、Gate、Handoff、SoT、Runtime、编号或矩阵作为主要表达。必要文件路径与编号只能放在末尾“相关文件”区域作为追溯信息。

### 7.3 最终回复结构

最终总结不得是一大段文字，至少包含：

```text
当前状态：等待你做最后一次整体确认

execution_ready：确认后，本期规划正式结束，并交给开发执行
planning_only：确认后，本期规划正式结束；当前不形成开发执行任务
```

只输出当前实际 Handoff 分支对应的一行，不同时向用户展示两种分支文案。

本期最终结论表：

| 主题 | 本期最终确认 | 明确边界 |
| --- | --- | --- |
| 本期目标 | 用业务白话说明 | 明确不包含什么 |
| 核心使用流程 | 用业务白话说明 | 明确不可跳过什么 |
| 角色分工 | 谁做什么 | 谁不能做什么 |
| 数据和权限 | 什么情况下允许 | 什么情况必须拒绝 |
| 旧流程处理 | 哪些彻底隔离 | 哪些最多只能只读 |
| 页面与交互 | 保留什么体验 | 前端不能代替什么判断 |
| 外部能力 | 已确认的接入方向 | 尚未真实验证的内容 |
| 测试与发布 | 必须证明什么 | 未满足时不能发布 |

表格行按实际涉及内容动态装配：不涉及外部能力时不生成空行，不涉及 UI 时不生成 UI 行；简单期次可缩短，复杂期次必须覆盖全部核心边界。

当 `requires_execution_handoff: true` 时，最终总结动态增加“开发前准备情况”：

| 检查项 | 当前结果 | 对开发的影响 |
| --- | --- | --- |
| 代码命名 | 使用长期业务名称 | 不使用期次或规划追踪编号 |
| 现有模块承接 | 已明确优先核实范围 | 执行前仍需核实现有代码 |
| 新模块 | 是否需要及架构原因 | 未经 09 确认不得新建 |
| 关键业务参数 | 已确认或尚缺失 | 仍有关键缺口时不能开始对应任务 |
| 技术参数 | 已明确委托范围 | 执行层只可在边界内决定 |

没有涉及的行不生成。用户态使用“追踪编号”“长期业务名称”“现有业务模块”“尚缺参数”等业务白话，不要求用户理解内部 Gate 或 ID 类型。

当 `requires_execution_handoff: false` 时，不生成“开发前准备情况”，改为动态生成“本期成果如何使用”：

| 检查项 | 当前结果 | 后续影响 |
| --- | --- | --- |
| 本期成果 | 规划或决策已经确认 | 当前不直接进入代码开发 |
| 适用范围 | 明确影响哪些后续工作 | 不代表已经实现 |
| 后续触发条件 | 什么时候需要重新进入开发规划 | 触发后再生成任务合同 |

用户态必须明确：

```text
当前规划内容已经整理完成，正在等待你做最后一次整体确认。

确认后，本期规划正式结束；当前不形成开发执行任务。
```

不得在最终总结确认阶段把“本期规划已结束”“本期规划正式结束”“规划已经完成”或“交接已经完成”作为已经发生的独立事实陈述，也不得说“下一步进入开发执行”。允许使用“确认后，本期规划正式结束”这类条件式未来表达。

随后必须包含：

- 5–10 条普通人能理解的重点边界，聚焦最容易在开发中被做错的业务逻辑。
- 当前未完成事实按分支动态输出：`execution_ready` 说明尚未开始开发或实际执行事实尚未写入、尚未证明自动化测试与真实外部能力、尚未完成最终验收、发布和生产基线更新；`planning_only` 说明当前没有形成开发执行任务，也不代表已经完成代码实现。
- 最后确认方式：用户可回复“确认，本期规划可以结束”，或“第 X 条不对，应该是……”。

### 7.4 最终总结纠正与确认

用户指出最终总结有误时：

```text
先记录本次反馈
-> 找到真正拥有该事实的上游文档
-> 回写并触发必要的下游重审
-> 重建 assembled_documents / handoff_role_mapping（如受影响）
-> 重新生成最终总结
```

不得只改总结文本。纠正后必须更新 `active_interaction.version` 并重新输出总结。用户完成最后确认后，先按第 0 节记录并应用绑定到 `final_summary` 的确认反馈，再执行第 8 节收尾。

## 8. Interaction Preference Consolidation 与正式结束回复

最后整体确认后、记录 `PLANNING_COMPLETE` 前，必须执行一次 Interaction Preference Consolidation：

- 检查本次对话中反复出现且对后续 Planning 有长期价值的交互倾向。
- 更新 `.runtime/planning-layer-runtime/user-profile.yaml`；每次 Planning 结束都要检查，而不是只在首次创建时写入。
- 新推断必须包含 `confidence`、`last_updated` 和简短证据类型，不保存原始聊天。
- 只保存稳定倾向，不保存完整聊天、本期业务事实、期次需求、一次性情绪、临时抱怨或单次措辞。
- 新旧倾向冲突时降低置信度，或以最新且反复确认的倾向更新。
- 证据不足时保持原值或低置信，不得把单次行为升级为高置信偏好。
- 该步骤不得要求用户填写画像字段，也不得向用户展示内部画像内容。
- 不得读取或更新第二个长期偏好来源。
- 偏好更新失败时不得静默跳过，也不得标记规划完成；保持 `awaiting_final_summary_confirmation`，并用业务白话说明本地偏好整理尚未完成。

完成偏好整理后：

```text
清空 current-interaction.yaml 中的待处理反馈
-> planning_status: planning_handoff_complete
-> 正式标记 Planning Handoff Complete
-> 追加 PLANNING_COMPLETE
```

最终用户态回复必须按 Handoff 分支明确写。

`execution_ready`：

```text
本期规划正式结束。

本期开发任务和后续验收承接关系已经准备好，下一步可以进入开发执行。
开发过程记录实际改动，测试和验收过程记录真实结果。
当前仍不代表开发、测试、验收或发布已经完成。
```

`planning_only`：

```text
本期规划正式结束。

本期需要确认的业务规则、范围或方案已经整理完成。
当前没有生成开发执行任务，也不代表已经完成代码实现。
后续决定进入开发时，需要基于本期结论生成开发任务合同和执行承接内容。
```

14、15 等专业文件名和编号只放在末尾“相关文件”区域。禁止只回复“已完成”，也禁止两种 Handoff 都统一回复“下一步进入开发执行”。

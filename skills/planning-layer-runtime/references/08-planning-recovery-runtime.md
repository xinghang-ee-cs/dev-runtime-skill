# 规划恢复运行时（Planning Recovery Runtime）

## 1. 范围（Scope）

本文档仅负责：

- Runtime Recovery
- Runtime Rollback
- SoT Invalid Propagation
- Validation Reopen
- Capability Revalidation Trigger
- Runtime Resume Path
- Recovery Event reuse
- Runtime Audit Logging
- Decision Snapshot Recovery Boundary
- 已通过 Execution/Test Change Triage 的精确 Planning Reentry

禁止：

- 修改业务 SoT
- 修改 Runtime Kernel
- 自动修正文档
- 自动生成最终修复方案
- Runtime 自动优化自身
- Runtime 自动修改规则
- Runtime 自动删除规则
- 对 implementation_defect 或 test_defect 触发 Planning Recovery
- 未经范围准入把新增需求吸收到当前期次

## 2. 恢复运行时（Recovery Runtime）

Recovery Runtime 只允许：

```text
发现失效
传播失效
记录恢复路径
恢复 Runtime 状态
```

禁止：

```text
自动修复系统
```

## 3. 恢复触发条件（Recovery Trigger）

以下情况只在当前 Planning 合同确实失效时触发 Recovery：

- PROJECT-CURRENT-BASELINE_CHANGED
- FLOW-CONTRACT_CHANGED
- JOURNEY-OBJECT-MAP_CHANGED
- SCENARIO-CONTRACT_CHANGED
- MODULE-BOUNDARY_CHANGED
- GLOBAL-STYLE_CHANGED
- DESIGN-ASSET_CHANGED
- STATE-DATA-FACT_CHANGED
- API-CONTRACT_CHANGED
- PERM-SCOPE-DATA-DOMAIN_CHANGED
- ARCH-DECISION_CHANGED
- CAPABILITY-DECISION_CHANGED
- TEST-DESIGN_CHANGED
- RISK-DEP-OPEN_CHANGED
- TASK-CONTRACT_CHANGED
- ACCEPTANCE-GATE_CHANGED
- 上游 SoT 修改
- 权限边界修改
- 状态机修改
- Capability Revalidation
- 接口契约修改
- 文档确认状态回退
- UI/交互确认状态回退
- CHANGE_TRIAGE_PLANNING_REENTRY_REQUIRED
- Validation Gate 失败
- Runtime Gate 失败
- Capability Binding 失效
- Acceptance Reopen
- 高风险冲突重新出现
- 上下文压缩
- 会话恢复
- 工具调用中断
- 长时间文件编辑后恢复
- 当前文档或确认对象无法确定
- 用户中途插入其他问题
- 同时存在多个草案

执行、联调、测试或验收发现的普通失败本身不是 Recovery Trigger。进入本 Runtime 前必须已经形成符合 `04-planning-format-spec.md` 的 `change_decision`；`implementation_defect`、`test_defect` 和规划仍有效的 `design_drift` 不进入本 Runtime。只有 `planning_gap`、已通过范围准入的 `requirement_change` 或真正改变设计合同的 `design_drift` 才允许触发。

### 3.1 当前交互恢复来源

上下文压缩、会话恢复、工具中断或当前确认对象不确定时，必须先读取：

```text
<phase_planning_runtime_directory>/current-interaction.yaml
```

只允许读取当前期次的该文件；不得到 Skill 目录寻找运行数据，不得把 Skill 中的示例代码块当成状态，不得读取其他期次的 `current-interaction.yaml`，也不得使用 `.runtime/planning-layer-runtime/user-profile.yaml` 或 `.runtime/planning-layer-runtime/project-profile.yaml` 恢复本期分支。

唯一恢复顺序：

```text
读取本期 current-interaction.yaml
-> 恢复 discovery_checkpoint revision / last_applied_round_id / active_question
-> 恢复 unresolved_items 的 resolution_route 与 research_findings
-> 恢复 active_interaction
-> 恢复未完成 latest_feedback
-> 校验反馈与 active_interaction 的目标绑定
-> discovery_question：核对问题 ID、回答状态、事实写入与下一未决项
-> document：检查目标正式文档当前状态
-> final_summary：检查总结版本与 planning_status
-> 恢复 execution_handoff_decision
-> 检查 decision_status
-> 与 Planning Context 中的 execution_handoff_decision 核对
-> 恢复 planning_execution_baseline_reference
-> 恢复 active_change 的 revision / change_status / decision_ref
-> 仅按 decision_ref 读取 decision-log 中对应 Change Set Decision Snapshot
-> 核对 Change Set 与 Recovery Output 受影响范围
-> 恢复 document_assembly 的 batch_revision / draft_generation_status
-> 核对 generated_documents 中每个真实路径、draft revision 与文档状态
-> 恢复 confirmation_queue / current_confirmation
-> 05 当前确认项适用时恢复 design_asset_collection 与 design_asset_batch 交互目标
-> 核对 Document Assembly Plan
-> 若批量装配中断，按已持久化检查点继续生成剩余草案并完成跨文档校验
-> 若处于确认或修正阶段，只恢复唯一 current_confirmation 或最早 reopened / pending_confirmation 项
-> 恢复 execution_ready 或 planning_only 分支
-> 判断 recorded / already_effective / invalid
-> 完成或阻止该反馈
-> 更新 apply_status 与 next_action
-> 再恢复当前 Planning 阶段
```

判断：

- 反馈已记录、目标与版本仍有效且尚未应用：继续校验并应用到原目标。
- `target_type: document` 时，目标文档已经达到反馈预期但反馈仍为 `recorded` 或 `validated`：标记 `already_effective`，不得重复应用。
- `target_type: final_summary`、`target_id: current_phase_final_summary`、`stage: final_summary_confirmation` 且版本匹配时，用户的“确认”只能消费最终总结目标，不得确认任何文档。
- 目标不存在、版本不匹配、确认范围不唯一或无法合法应用：标记 `needs_clarification` 或 `rejected`，不得猜测。
- 上一条反馈仍为 `recorded` 或 `validated` 时，必须先完成该反馈，不得用新反馈覆盖。

禁止根据压缩后的对话摘要、最近提到的文档编号、“下一步是第 X 份”、编号大小或模型记忆推断当前确认对象。

批量装配与确认队列恢复规则：

- `draft_generation_status: generating` 时，逐一回读 `generated_documents` 的真实文件；路径、revision 与内容匹配的草案直接复用，只从第一个缺失或无效项继续生成。不得覆盖有效草案，也不得在完整批次生成和跨文档校验完成前开始用户确认。
- `draft_generation_status: blocked` 时，只按 `generation_blocker` 恢复 owning role、`unresolved_item_ref` 与恢复条件，再从 Discovery checkpoint 定位问题；回答写入 checkpoint 后清空 blocker 并继续原 `batch_revision`，不得在 `document_assembly` 复制问题正文或重新访谈已确认事实。
- `draft_generation_status: generated` 时，`confirmation_queue` 必须覆盖本批次全部适用草案并与真实路径、draft revision 一致；不一致时先修复队列或标记草案 `invalidated`，不得凭文件编号补猜。
- 同时存在多个草案是正常批量状态，不构成全量回退理由。恢复时只允许一个 `current_confirmation`；其版本必须等于队列中的当前 draft revision。
- 用户纠正命中上游 SoT 时，按依赖关系把受影响项标记为 `reopened` 或 `invalidated`，只重建这些草案并刷新 revision；未受影响的草案、确认状态和真实文件保持不变。
- 修正完成后，从依赖顺序中最早的 `reopened` 或 `pending_confirmation` 项继续。不得重新生成完整批次，不得把确认流程退化为“生成一份再问一份”。
- `active_interaction`、`latest_feedback` 与 `current_confirmation` 任一绑定不一致时先停止并修复最小恢复镜像；不得将用户对一份文档的反馈消费到另一份草案。

05 设计资产收集恢复规则：

- 仅从 `design_asset_collection` 恢复当前 `asset_kind / collection_status / active_batch_id`，再读取 05 中对应 Prompt 与 ASSET 正文；不得从压缩摘要猜测用户正在生成 UI 图还是 UX 图。
- 按 `active_prompt_refs / active_asset_refs` 的持久化顺序恢复当前批次，再从 05 ASSET 的 `image_sequence` 恢复用户态图片序号；批次上限与重发顺序按 10 恢复，Prompt 用户态格式按 11 §4.1 渲染，图片确认展示格式按 11 §4.2 渲染。序号缺失、重复或与引用不一致时先阻断并修正 05，不得在恢复时临时重排。
- `collection_status: prompt_ready` 表示 Prompt 尚未可靠交付：先持久化 `design_asset_generation_request`，再从 05 回读并直接输出完整 `prompt_body`。
- `collection_status: awaiting_assets` 表示 Prompt 已交付、正在等待图片。恢复时保留已收到资产，只说明仍缺的 ASSET 映射；用户要求重发时从 05 输出同 revision Prompt，不另生成一份。
- `collection_status: reviewing_assets` 时，必须回读 05 中实际收到的路径、ASSET revision、覆盖状态和 known gaps，恢复 `design_asset_review_confirmation`，再按稳定 `image_sequence` 重新呈现本批全部 `review_pending` 图片后请求确认：当前工具支持图片展示时重新内联展示，不支持时依次恢复绑定当前 revision 的有效直接链接或自主定位信息。不得依赖压缩前的呈现、只恢复文字总结，或把“已上传”推断为 `visual_confirmed`。用户已经明确说明自行找到并确认当前 revisions 时优先应用该反馈并正常推进；只有真实位置或 revision 无法确定、用户无法找到或反馈无法绑定时才请求对应序号的最小补充，不要求用户重传其余有效图片。
- 收到尚未处理的图片反馈时，先把 `latest_feedback` 应用到原 `design_asset_batch`，再写 ASSET 路径与 `received / review_pending` 状态；不得错误应用到 05 文档确认目标。
- UI 资产全部确认后才恢复 UX Prompt 交付；PROMPT-UX 必须引用当前 `visual_confirmed` UI revision。若该 UX 已由现有 UI 图充分覆盖，按 05 的 `covered_by_existing_ui_assets` 恢复，不额外索要图片。
- Prompt、图片或确认 revision 不一致时只使受影响批次和下游草案失效；未受影响且已确认的 UI/UX 资产保持有效。

Discovery 恢复规则：

- `latest_feedback` 仍为 `recorded` 或 `validated` 时，先把该回答应用到原 `discovery_question`，更新事实、未决项和 checkpoint revision；不得重问或跳到下一问题。
- `active_question.answer_status: awaiting_answer` 且无未完成反馈时，向用户自然恢复该问题；不得根据压缩摘要另选问题。
- `last_applied_round_id` 已完成但 checkpoint revision 未更新，或事实写入与 feedback 结果不一致时，阻止推进并恢复该轮持久化事务。
- 下一问题必须来自已持久化 `unresolved_items` 与当前最大不确定项；已为 `confirmed` 的事实不得重复询问。
- `resolution_route: project_evidence | web_research` 的未决项先恢复对应核验事务，不得改成用户问题；已持久化且仍在时效范围内的 `verified` 结论直接复用。
- 调研结论为 `stale`、`conflicting`、`insufficient`，或所涉版本、价格、法规、平台能力可能已变化时，先重新核验并覆盖更新同一 `research_id`；不得根据压缩摘要或旧聊天结论猜测。
- 公开来源暂时不可访问时保留已有来源定位并标记需要重新核验；不得删除结论后要求用户回忆公开事实。用户补充唯一内部证据时按项目内来源重新校验。
- 调研发现的功能候选只有在用户已确认适用、延期或不适用后才能恢复为对应结论；延期项仍以 Requirement Pool 为唯一正文来源。
- 恢复到非第一次 Planning 的第一阶段时，只读取 `relevant_requirement_pool_refs` 命中的池条目；若尚未执行 Requirement Pool Intake Gate，则按 07 执行，不得扫描 00–15 猜测延期需求。
- `same` 条目已确认进入当前 Planning Context 后仍存在于池中时，完成消费删除再推进；`conflict` 条目尚未按用户最新确认更新时，恢复到冲突确认；`unrelated` 条目不加载正文。

Planning Context 中已确认的 `execution_handoff_decision` 是权威语义来源，本期 `current-interaction.yaml` 是短期恢复镜像。恢复时：

- `decision_status: confirmed` 且与 Planning Context 一致时，按该分支恢复，不得重新推断。
- `decision_status: candidate` 时，恢复到 `execution_handoff_confirmation` 交互。
- 镜像字段缺失时不得猜测，回到执行交接判断确认。
- 不得根据压缩后的聊天摘要重新推断分支。
- 不得根据当前已生成的文件数量反向推断分支。
- 不得因为 13 尚未生成而自动判断为 `planning_only`。
- 不得因为用户在压缩摘要中提到“开发”一词而覆盖已确认分支。
- Handoff 中的 `requires_execution_handoff`、`handoff_type` 必须与 Planning Context 一致。
- Document Assembly Plan 中的 `execution_handoff_decision` 必须与 Planning Context 逐字段一致；它只是恢复当前装配计划的同步字段，不是第二个决策来源。
- `current-interaction.yaml` 与 Planning Context 不一致，或 Document Assembly Plan 与恢复镜像不一致时，必须阻止恢复推进，回到 Planning Context 与本期恢复镜像修正。
- 增量恢复必须同时具备 `planning_execution_baseline_reference` 与 `active_change.decision_ref`。只读取 `decision_ref` 指向的当前 Change Set 快照，不扫描完整 decision-log 推导当前 revision。
- `active_change.change_status` 为 `closed` 或 `superseded` 时不得作为当前执行范围恢复；存在连续 Change Set 时只恢复当前 active revision，并通过快照中的 previous/supersedes 引用保留历史关系。
- `decision_ref` 必须使用 `<phase_planning_runtime_directory>/decision-log.md#decision_id=<DEC-ID>`，并唯一命中同时包含 Change Set 与 Recovery Output 的 Decision Snapshot。只命中文件、标题或时间戳时不得继续恢复。
- 当前 Snapshot 必须是相对冻结 Baseline 的累计有效增量；它已经包含仍有效前序 Change Set 的影响范围。Recovery 不读取 R2、R3 历史拼装当前状态，也不因 active 指针前移推断旧 revision 已 `closed` 或 `superseded`。
- 延期需求只从 `<requirement_pool_path>` 恢复；`current-interaction.yaml.discovery_checkpoint.relevant_requirement_pool_refs`、15 和 Handoff 只提供 `POOL-ID` 定位，不得包含第二份需求正文。Baseline 已冻结但 14/15 缺失时，仍恢复为框架派生阻断，不得恢复到 `handoff_prepared` 或执行入口。

`current-interaction.yaml` 是短期恢复来源，但不是正式 SoT、历史日志、长期聊天记录或研究报告。`discovery_checkpoint` 只保存结构化最小事实、未决项和调研结论，不得扩展为完整访谈历史或网页档案。不得新增 `recovery-state`、`feedback-runtime`、`confirmation-runtime` 或 `context-compression-runtime`。

## 4. 恢复输出（Recovery Output）

Recovery Runtime 必须输出：

```yaml
recovery_id:
trigger_source:
invalidated_items:
affected_documents:
affected_tasks:
affected_validation:
affected_capabilities:
recovery_stage:
recovery_action:
resume_condition:
blocking:
```

规则：

- 不允许自由格式。
- 不允许长篇解释。
- 不允许 AI 推理内容。
- 不允许自然语言总结。
- 与当前用户反馈有关的最小处理状态写回现有 `current-interaction.yaml` 字段；active Change Set 的完整 Recovery Output 必须与完整 Change Set 一起写入 `decision_ref` 指向的同一 Decision Snapshot。不得复制到 `current-interaction.yaml`，也不得为 Recovery Output 新增独立持久化文件。
- `affected_documents`、`affected_tasks`、`affected_validation` 是后续 Document Assembly、TASK 修订、14/15 框架修订和增量 Handoff 的硬约束；未列入者不得被重建、重置或重新执行。

## 5. SoT 失效传播（SoT Invalid Propagation）

当上游 SoT 修改时，必须传播：

- 下游文档失效
- Validation 失效
- Acceptance 失效
- 任务承接准备失效
- Capability Validation 失效

传播只作用于与 active Change Set 的 `added_ids / modified_ids / superseded_ids` 存在依赖关系的对象；`unaffected_ids` 必须保持有效。禁止把“存在上游变化”解释为整期全量失效。

示例：

```text
06 修改
-> 07 invalid
-> 08 invalid
-> 11 reopen
-> 13 reopen
-> 15 reopen
```

新增传播规则：

```text
PROJECT-CURRENT-BASELINE_CHANGED
-> 当前 Planning Context invalid
-> 00 invalid
-> 01 invalid
-> 02 invalid
-> 相关下游文档按依赖关系 invalid

FLOW-CONTRACT_CHANGED
-> 02 invalid
-> 03 invalid
-> 04 invalid
-> 05/06/07/08/11/13 按依赖关系 reopen

JOURNEY-OBJECT-MAP_CHANGED
-> 03 invalid
-> 06 invalid
-> 07 invalid
-> 08 invalid
-> 11 invalid
-> 13 invalid

FLOW changed
-> related SCN invalid
-> related MODULE coverage reopen
-> PAGE / UI-MOD / UX-SCN review reopen
-> related Prompt / UI Implementation / UX Interaction contracts reopen and raise revision when content changes
-> related assets marked review_pending or superseded
-> design_delivery_manifest and downstream bindings invalidated

SCN changed
-> related MODULE coverage reopen
-> related PAGE / UI-MOD / UX-SCN reopen

MODULE boundary changed
-> related PAGE / UI-MOD / UX-SCN reopen

global style changed（仅 replace_current 或受影响的 extend_current）
-> related PROMPT-PAGE / PROMPT-MODULE / PROMPT-UX reopen
-> only affected visual assets marked review_pending
-> affected PAGE / UI-MOD contracts and Manifest reopen

Prompt / PAGE / UI-MOD / UX-SCN / ASSET contract changed
-> changed item must receive a new revision; same-revision silent replacement forbidden
-> 05 design_delivery_manifest reopen
-> related 11 TEST reopen
-> related 13 frontend_contract_binding reopen
-> Handoff.frontend_experience_binding invalid
-> affected Long frontend_execution_snapshot invalid
-> affected UI TASK only enters resume/reexecute after a new valid Handoff

FLOW / DOMAIN 变化
-> 06 invalid
-> 07 invalid
-> 08 invalid
-> 11 reopen
-> 13 reopen

STATE / DATA FACT 变化
-> 07 invalid
-> 08 invalid
-> 11 reopen
-> 13 reopen

API Contract 变化
-> 08 invalid
-> 11 reopen
-> 13 reopen

PERM / Scope / Data Domain 变化
-> 07 contract review required
-> 11 reopen
-> 13 reopen

ARCH 决策变化
-> 关联 CAP review required
-> 关联 TEST reopen
-> 13 reopen

CAP 选型或关键前提变化
-> 关联 ARCH review required
-> 关联 TEST reopen
-> 12 风险 reopen
-> 13 reopen

TEST 设计变化
-> 13 测试任务 reopen
-> 后续测试与验收承接准备需要重新审查
-> 15 相关验收结果 reopen

FLOW / STATE / API / PERM 变化
-> 09 review required
-> 关联 CAP review required
-> 11 reopen
-> 13 reopen
-> 15 相关验收结果 reopen

RISK / DEP / OPEN 变化
-> 相关 TASK 需要重新审查
-> 相关 14 预置执行项需要重新审查
-> 相关 15 预置验收项需要重新审查

TASK 合同变化
-> 只使 active Change Set 对应的 14 预置执行项失效
-> 只使对应 15 预置验收项失效
-> 受影响且尚未填写真实事实的 14、15 占位标记 framework_rebuild_required
-> 未填写实际事实的受影响部分按新 TASK revision 重建或追加
-> 已由后续阶段写入的实际事实不得被 planning recovery 自动删除、覆盖或伪造
-> 未受影响 TASK / EXEC / TEST 保持原 ID、合同与状态
-> completed_locked TASK 不得重新进入执行队列
-> carried_forward pending TASK 保持 active，并继续进入新 Handoff.execute_only
-> 正在执行且未受影响 TASK 继续进入 resume_only
-> Handoff 需要在 Execution and Acceptance Framework Derivation Gate 通过后基于真实路径重新生成

验收标准、风险关闭条件或发布门禁变化
-> 15 对应预置验收项失效
-> 必须更新 15 框架后才能继续使用
```

禁止静默修复或全量重跑；必须记录 Change Set，并只处理明确受影响范围。

规则：

- 不得继续沿用已被 `superseded` 或 `invalid` 的受影响 task、测试映射或 handoff；未受影响和 `completed_locked` 内容必须继续保留。
- 旧 Handoff 被 `superseded` 只表示旧执行边界失效，不得因此丢失原 Baseline 中仍有效的未完成 TASK；新 Handoff 必须重新分类并完整承接 carried-forward pending 与未受影响 in-progress TASK。
- 必须重新读取当前有效 SoT，再继续后续文档。
- Recovery 必须复用已有 Runtime Event Log 与现有事件类型。
- 禁止新增日志目录、独立事件系统或独立 Recovery SoT。
- 视觉资产变化若不改变业务动作、场景入口、异常恢复、资格或流程终态，不得反向修改 01/02。
- 视觉资产变化若导致主操作、进入条件、异常处理、旧入口处理或用户路径变化，必须回到 03；若影响合法业务旅程，则继续回到 01/02。
- Prompt、PAGE/UI-MOD、UX-SCN 或 ASSET revision 变化必须同步更新 05 Manifest、11 TEST、13 TASK binding 与 Handoff；不得只替换图片文件或只改 Handoff。
- 不得继续沿用旧接口兼容结论。
- 06/07/08 恢复时必须先读取当前有效 SoT，再恢复后续文档。
- 不得继续沿用已失效的受影响测试映射、任务合同、能力结论或架构绑定；未受影响结论不得被无条件重审。
- 09/10/11 恢复时必须先读取当前有效 SoT，再继续下游文档或运行时。
- 12/13/14/15 恢复时只处理 planning skill 内部的框架失效与重审标记，不定义其他 skill 的恢复行为。
- 14、15 未填写实际事实的预置项可以标记为 `framework_rebuild_required` 并按新合同重建；已经由后续阶段填写的事实不得由 planning recovery 自动删除、覆盖、伪造或回退。
- Recovery 不得出现“先有 14、15 才能确认 13”的恢复路径；14、15 只在 13 已确认后派生或重建未填写的预置项。
- Recovery Output 与 active Change Set 不一致时不得继续；必须收窄到两者交集或先修正影响分析，禁止扩大到完整 00–15。
- 原 TASK 结论错误时保留历史并设置 `contract_status: superseded`、`execution_disposition: cancelled`，再创建 `relation_to_previous: replaces | supersedes` 的替代 TASK；局部扩展时创建增量 TASK；正在执行的 TASK 只允许 `resume` 或 `reexecute_affected_part`。
- TASK 保护必须分开：completed 未受影响项为 `completed_locked`；尚未开始且未受影响项为 carried-forward pending 并允许 `execute`；正在执行且未受影响项允许 `resume`；纯背景项才是 `context_only`。

### 5.1 执行交接分支变化传播

本节复用现有用户反馈事务、Planning Context、文档状态和失效传播规则，不新增 Recovery 类型、Runtime 文件、日志或状态体系。

`planning_only -> execution_ready`：

```text
记录并应用用户反馈
-> 回写 Planning Context 中的 execution_handoff_decision
-> 同步更新本期 current-interaction.yaml
-> requires_execution_handoff: true / handoff_type: execution_ready / decision_status: confirmed
-> 使旧 Document Assembly Plan 失效
-> 使原 planning_only Handoff 与最终总结失效
-> 重新生成 Document Assembly Plan
-> 同步 document_assembly
-> 按新计划批量生成全部新增或受影响草案并刷新 confirmation_queue
-> 依次确认新增或 reopened 草案；未受影响的已确认文档保持有效
-> 轮到 13 时运行三个 Gate 与适用的 UI/UX Execution Readiness Gate
-> 确认 13
-> 派生 14/15
-> 重建 assembled_documents、handoff_role_mapping 与 execution_ready Handoff
```

`execution_ready -> planning_only` 只有用户明确取消本期全部工程执行任务时才允许：

```text
记录并应用用户反馈
-> 回写 Planning Context 中的 execution_handoff_decision
-> 同步更新本期 current-interaction.yaml
-> requires_execution_handoff: false / handoff_type: planning_only / decision_status: confirmed
-> 使旧 Document Assembly Plan 失效
-> 重新评估实际适用文档
-> 使原 execution_ready Handoff 与最终总结失效
-> 重新生成 Document Assembly Plan
-> 同步 document_assembly
-> 按新计划只重建新增或受影响草案并刷新 confirmation_queue
-> 依次确认 reopened 草案；未受影响的已确认文档保持有效
-> 重新生成 planning_only Handoff
```

若 13、14、15 已经生成：

- 不得静默删除历史文件。
- 按既有失效传播规则标记为不再适用或 `superseded`。
- 不得继续放入当前 `assembled_documents`、`handoff_role_mapping` 或 Handoff。
- 已由后续阶段写入的实际事实不得由 Planning Recovery 删除、覆盖或回退。

## 6. 恢复恢复门禁（Recovery Resume Gate）

Recovery 不允许无限进行。

必须定义：

```yaml
resume_condition:
blocking_count:
conflict_count:
revalidation_required:
```

只有恢复完成后，才允许：

```text
重新进入 Planning Runtime
```

规则：

- Recovery Runtime 必须复用 Runtime Event Logging。
- Recovery Event 写入 `<phase_planning_runtime_directory>/event-log.md`。
- 禁止新增独立 Recovery Event System。
- Recovery Trigger 只允许追加一条 Decision Snapshot。
- Resume Gate 不得依赖历史 Decision Log。
- Resume Gate 必须确认 Planning Execution Baseline 未被覆盖、Change Set revision 唯一、受影响清单已闭合、未受影响与已有真实事实均受保护，且增量 Handoff 可以明确允许执行范围。

## 7. 运行时审计层（Runtime Audit Layer）

允许：

- Runtime 自检
- Runtime 风险检测
- Runtime 熵增检测

禁止：

- Runtime 自动优化自己
- Runtime 自动修改规则
- Runtime 自动修复 SoT
- Runtime 自动重写文档

规则：

- 只能写日志。
- 不能自动修改。
- 不影响普通用户使用。

## 8. 运行时审计日志（Runtime Audit Log）

真正触发 Runtime Audit 时，才创建并写入：

```text
<phase_planning_runtime_directory>/audit-log.md
```

`audit-summary.md` 只在达到压缩阈值、阶段收尾或确有复盘需要时创建。普通 Planning 不默认创建 Audit 文件，没有内容时不得为了目录完整性创建。

仅用于：

- Runtime Debug
- Runtime Governance
- Model Comparison
- Human Review

定位：

- Project Runtime Evidence
- 项目执行证据
- 不是 Runtime State

禁止：

- 业务事实定义
- Runtime SoT
- 用户流程
- 正式验收
- Runtime Recovery Source

以下内容只写入 `planning-runtime/audit-log.md`：

- 熵增检查
- Runtime 自检
- SoT 冲突
- 规则重复
- 文档职责漂移
- Runtime 膨胀
- 日志膨胀
- Capability 重复
- 长期 BLOCKER
- 长期 Pending
- Runtime 循环依赖

禁止：

- 注入用户对话
- 干扰 Planning Context
- 自动进入正式 SoT
- 自动阻塞普通用户任务

## 9. 审计事件格式（Audit Event Format）

统一格式：

```yaml
timestamp:
audit_id:
audit_type:
severity:
related_files:
related_ids:
detected_issue:
entropy_risk:
recommended_action:
human_review_required:
```

Audit 类型：

```text
RULE_DUPLICATION
SOT_CONFLICT
RESPONSIBILITY_DRIFT
RUNTIME_BLOAT
LOG_BLOAT
LONG_PENDING
LONG_BLOCKER
CAPABILITY_DUPLICATION
CIRCULAR_DEPENDENCY
INVALID_PROPAGATION_FAILURE
UNUSED_RUNTIME_FILE
```

新增 `audit_type` 必须满足：

- 单职责
- 不重复已有语义
- 不允许历史补丁命名
- 不允许模糊命名
- 必须经过 human review

若已有 `audit_type` 能表达问题，禁止新增新类型。

Audit 的目标是：

```text
发现 Runtime 风险
```

而不是：

```text
保存 Runtime 历史
```

禁止：

- 演变成问题数据库
- 演变成历史记忆系统
- 演变成 Runtime 分析系统
- 演变成长期状态存储

## 10. 审计日志生命周期（Audit Log Lifecycle）

Audit Log 必须：

- append-only
- 结构化
- 短字段
- 禁止长解释
- 禁止全量推理
- 禁止完整聊天记录
- 禁止重复事件

`audit-log.md` 作为 Project Runtime Evidence 长期保留。

历史问题必须 summary 化，进入：

```text
audit-summary.md
```

禁止：

- 无限增长
- 全量重新加载
- 历史日志重新注入 Runtime

## 11. 用户隔离（User Isolation）

普通用户不需要知道：

- Runtime Audit
- 熵增
- Runtime Governance
- Skill 自检

用户态原则：

```text
描述需求
-> 回答必要问题
-> 获取 Planning Context
-> 获取正式文档
-> 进入开发
```

规则：

- Runtime Audit 不进入用户态输出。
- Runtime Audit 不污染 Planning Context。
- Runtime Audit 不增加用户交互复杂度。
- Runtime Audit 不替代业务阻塞。

## 12. 决策快照恢复边界（Decision Snapshot Recovery Boundary）

Recovery Runtime 可以使用 Decision Snapshot，但只允许：

- 追加 Recovery Trigger 决策快照
- 在 Runtime Debugging 中读取 `planning-runtime/decision-summary.md`
- 在用户主动回传日志时读取相关片段
- 按本期 `current-interaction.yaml.active_change.decision_ref` 精确读取当前 Change Set Decision Snapshot

禁止：

- 默认读取完整 `planning-runtime/decision-log.md`
- 用历史 Decision Log 推导当前 Runtime 状态
- 将 Decision Snapshot 写入 Planning Context
- 将 Decision Snapshot 写入正式 SoT
- 将 Decision Snapshot 写入 Handoff Package
- 将 Decision Snapshot 写入 Capability Registry
- 将 Decision Snapshot 写入 Acceptance
- 新增 recovery 专用日志

规则：

- `.runtime/planning-layer-runtime/` 是 Bootstrap Context，不是 Runtime Recovery Source。
- 当前交互恢复先读取 `current-interaction.yaml`：文档目标再读取正式文档状态，最终总结目标读取总结版本与 `planning_status`；业务事实与失效传播仍以当前 SoT、当前 Gate 和当前 Recovery Output 为准。
- 不得用 `.runtime/planning-layer-runtime/` 中的历史信息恢复正式业务状态。
- 历史 Decision Snapshot 只能辅助复盘，不得成为恢复依据；唯一例外是 `active_change.decision_ref` 精确指向的当前 Change Set 快照，它与 Planning Execution Baseline revision 共同恢复当前有效增量范围，但仍不替代正式 SoT。

## 13. 低熵规则（Low Entropy Rule）

新增内容必须满足：

- 单职责
- 最小字段
- 不重复 SoT
- 不新增解释性规则
- 不新增历史补丁规则
- 不增加 Runtime 长上下文
- 不依赖历史日志
- 不自动读取全量 Audit
- 不允许 Runtime 自修改

Runtime Internal Layer 必须保持：

- 最小上下文
- 最小字段
- 最小状态
- 最小事件类型

禁止：

- Runtime Internal Layer 自增长
- Runtime Internal Layer 形成子 Runtime
- Runtime Internal Layer 相互依赖
- Runtime Internal Layer 长期持久化扩张

Project Runtime Evidence 文件：

```text
planning-runtime/event-log.md
planning-runtime/event-summary.md
planning-runtime/decision-log.md
planning-runtime/decision-summary.md
planning-runtime/audit-log.md
planning-runtime/audit-summary.md
```

短期 Runtime State 另为：

```text
planning-runtime/current-interaction.yaml
```

该文件可覆盖更新并作为当前交互恢复来源，不属于 append-only Project Runtime Evidence。

其中 `discovery_checkpoint` 是逐轮覆盖更新的结构化恢复检查点；不得把完整对话、逐字回答或每轮 AI 解释追加成新的日志体系。

规则：

- Project Runtime Evidence 必须优先复用既有文件。

禁止新增：

- recovery-runtime/
- governance-runtime/
- entropy-runtime/
- analysis-runtime/
- debug-runtime/

新增 Runtime 内容前必须先检查：

```text
是否已有现有结构可复用？
```

优先级：

```text
复用结构
>
合并职责
>
删规则
>
新增规则
```

禁止：

```text
为了修复局部问题
新增长期 Runtime 结构
```

若某规则无法降低熵：

```text
优先删规则
优先拆职责
优先调整结构
```

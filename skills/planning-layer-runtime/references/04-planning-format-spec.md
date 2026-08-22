# 流程梳理阶段：AI Runtime Format Specification

## 1. 文件位置

```text
<phase_planning_directory>/
```

### 1.1 运行数据位置

期次级 Planning 运行数据只允许保存到：

```text
<phase_planning_runtime_directory>/
├── current-interaction.yaml
├── event-log.md
├── event-summary.md
├── decision-log.md
├── decision-summary.md
├── audit-log.md
└── audit-summary.md
```

职责：

- `current-interaction.yaml`：当前短期交互状态；是上下文压缩、会话恢复和工具中断后的恢复来源。
- Event / Decision / Audit Log：本期追加式运行证据。
- Event / Decision / Audit Summary：对应 Log 的压缩复盘入口。
- 正式业务事实仍只进入 00–15 SoT；上述文件均不得替代 SoT。

创建方式：

```text
读取本文件中的字段规范
-> 在项目合法目录直接创建所需文件
-> 写入最小运行数据
```

禁止从 Skill 目录复制任何运行文件。禁止进入 Planning Document Mode 后一次性创建全部文件。

按需创建规则：

- `current-interaction.yaml`：进入 `discovery_start` 且本期路径合法绑定后，在第一条实质性业务问题前创建；不得等到访谈结束、执行交接判断或 Planning Document Mode 才创建，是唯一默认必需文件。
- `event-log.md`：第一次实际写入 Runtime Event 时创建。
- `decision-log.md`：第一次实际存在 Decision Snapshot 时创建。
- `audit-log.md`：真正触发 Runtime Audit 时创建；普通 Planning 不创建。
- `event-summary.md`、`decision-summary.md`、`audit-summary.md`：只在达到压缩阈值、阶段收尾或确有复盘需要时创建。
- 没有实际内容的文件不得为了目录完整性创建。

禁止为同一职责新增 `feedback-runtime`、`confirmation-runtime`、`handoff-runtime`、`recovery-state` 或 `context-compression-runtime`。

项目级跨期稳定信息保存到：

```text
.runtime/planning-layer-runtime/user-profile.yaml
.runtime/planning-layer-runtime/environment-profile.yaml
.runtime/planning-layer-runtime/project-profile.yaml
.runtime/planning-layer-runtime/context-index.yaml（仅在确有多个稳定上下文入口时）
```

跨期待处理需求单独保存到：

```text
<requirement_pool_path>
```

默认绑定为 `<planning_root>/REQUIREMENT-POOL.md`，但项目已有等价文件时优先复用。Requirement Pool 是规划输入资产，不属于 `.runtime/planning-layer-runtime/`、期次 `planning-runtime/`、00–15 正文或执行 Backlog。

其中：

- `user-profile.yaml` 是长期交互习惯和规划协作偏好的唯一来源，不保存完整聊天、原始消息、一次性情绪、临时抱怨、项目业务事实、期次内容、心理画像或未经确认的身份推断。
- `environment-profile.yaml` 只保存稳定项目与开发环境事实，不保存任何凭证或完整敏感配置。
- `project-profile.yaml` 只保存项目身份与当前基线入口。
- `context-index.yaml` 只在确有多个稳定上下文入口时创建。
- 新推断的用户倾向必须包含 `confidence` 与 `last_updated`；证据不足时不得把单次行为升级为高置信长期偏好。
- 长期交互与规划协作偏好只能由 `user-profile.yaml` 承载，禁止第二来源。
- `.runtime/planning-layer-runtime/` 不得默认一次性创建完整文件树；`README.md` 仅在确实需要向人说明边界时按需创建。
- 首次创建 `.runtime/planning-layer-runtime/` 或期次 `planning-runtime/` 文件前，检查项目现有版本控制与忽略策略。未获用户明确要求时，不得把用户倾向、电脑环境或原始反馈提交到公开仓库。
- `environment-profile.yaml` 禁止保存 Token、密码、私钥、Cookie、主机账号、可识别个人的完整 Home 路径、内网 IP、机器序列号、完整敏感环境变量或可直接调用生产服务的配置。

`.runtime/planning-layer-runtime/user-profile.yaml` 最小格式：

```yaml
interaction_preferences:
  - preference_key:
    value:
    confidence:
    last_updated:
    evidence_type:

confirmed_stable_context: []
```

`preference_key` 按实际需要使用，例如：人话总结或专业文档优先、单问题或集中确认、文档解释方式、阶段与结束条件可见性、表格/列表/流程图/段落偏好、技术术语接受程度、纠正响应方式、解释深度、文档和最终规划确认方式。单次行为只能记录为低置信候选；`evidence_type` 只写简短证据类型，不保存原始聊天。

`.runtime/planning-layer-runtime/environment-profile.yaml` 最小格式：

```yaml
operating_system:
shell:
language_runtimes: []
package_managers: []
common_tools: []
project_tech_stack: []
stable_project_paths: []
stable_startup_rules: []
environment_boundaries: []
last_updated:
```

仅写后续 Planning 确实需要复用的稳定环境事实；路径必须脱敏，不写个人 Home 全路径。

### 1.2 `current-interaction.yaml` 最小格式

只保留恢复当前交互所需字段，不扩展为业务状态机：

```yaml
current_phase:

discovery_checkpoint:
  status:
  revision:
  updated_at:
  initial_intake_summary:
  last_applied_round_id:
  active_question:
    question_id:
    topic:
    prompt_summary:
    asked_at:
    answer_status:
  facts:
    - fact_id:
      topic:
      summary:
      confirmation_status:
      source_round_id:
      source_research_id:
      supersedes_fact_id:
  unresolved_items:
    - item_id:
      summary:
      blocking:
      resolution_route:
      related_research_id:
      next_question:
  research_findings:
    - research_id:
      topic:
      finding_summary:
      evidence_scope:
      evidence_status:
      checked_at:
      sources:
        - source_type:
          source_ref:
          source_title:
          source_version_or_date:
      planning_relevance:
      related_fact_ids: []
      related_requirement_pool_refs: []
  relevant_requirement_pool_refs: []

execution_handoff_decision:
  requires_execution_handoff:
  handoff_type:
  decision_basis:
  decision_source:
  decision_status:

planning_execution_baseline_reference:
  phase_id:
  revision:

active_change:
  change_revision:
  admission_result:
  change_status:
  decision_ref:

document_assembly:
  batch_revision:
  planned_roles:
    - <本期计划装配的职责名>
  draft_generation_status:
  generated_documents:
    - role:
      path:
      draft_revision:
      document_status:
  confirmation_queue:
    - role:
      path:
      draft_revision:
      confirmation_status:
  current_confirmation:
    role:
    path:
    draft_revision:
  generation_blocker:
    owning_role:
    unresolved_item_ref:
    resume_condition:
  design_asset_collection:
    design_document_path:
    collection_revision:
    asset_kind:
    collection_status:
    active_batch_id:
    active_prompt_refs: []
    active_asset_refs: []
  assembly_status:

active_interaction:
  target_type:
  target_id:
  stage:
  version:
  scope:
  expected_user_action:
  next_step:

latest_feedback:
  feedback_id:
  received_at:
  raw_user_input:
  normalized_summary:
  feedback_type:
  target_type:
  target_id:
  target_stage:
  target_version:
  target_scope:
  apply_status:
  apply_result:
  next_action:

planning_status:
```

`target_type` 至少支持：

```text
document
discovery_question
design_asset_batch
execution_handoff_decision
final_summary
scope_change_decision
```

`stage` 至少支持：

```text
discovery_answer
design_asset_generation_request
design_asset_review_confirmation
draft_confirmation
execution_handoff_confirmation
final_summary_confirmation
scope_expansion_admission
```

`feedback_type` 只允许：

```text
confirm
correct
supplement
reject
ask_explanation
continue
pause
return_to_previous
unknown
```

`apply_status` 只允许：

```text
recorded
validated
applied
already_effective
rejected
needs_clarification
```

`planning_status` 至少区分：

```text
planning_in_progress
awaiting_final_summary_confirmation
planning_handoff_complete
```

规则：

- `discovery_checkpoint.status` 只允许 `in_progress`、`ready_for_completion_gate`、`compiled_into_planning_context`；`revision` 每成功应用一轮回答后单调递增。
- Discovery Runtime ID 在本期内唯一且单调递增：问题使用 `DQ-<SEQ>`，回答轮次使用 `DR-<SEQ>`，结构化事实使用 `DF-<SEQ>`，未决项使用 `DU-<SEQ>`，调研结论使用 `RF-<SEQ>`；这些 ID 只属于 `current-interaction.yaml`，不得进入正式实现命名。
- `active_question.answer_status` 只允许 `awaiting_answer`、`recorded`、`applied`、`superseded`；一条问题在 `awaiting_answer` 前必须已持久化 `question_id / topic / prompt_summary / asked_at`。
- `facts[].confirmation_status` 只允许 `candidate`、`confirmed`、`superseded`。用户纠正事实时不得静默覆盖；旧事实标记 `superseded`，新事实使用新 `fact_id` 并填写 `supersedes_fact_id`。
- `facts` 只保存用户表达、项目当前基线以及用户确认后的业务适用或取舍结论。公开或项目证据核实出的客观资料只进入 `research_findings`，不得直接复制进 `facts`。当用户确认某条调研结论适用于本期业务时，新业务事实填写 `source_research_id: <RF-ID>`；没有调研来源时省略该字段。
- `unresolved_items[].resolution_route` 只允许 `project_evidence`、`web_research`、`user_confirmation`；可自行核验的项不得错误路由成 `user_confirmation`。关联既有调研时填写 `related_research_id`，否则留空或省略。
- `research_findings[].evidence_scope` 只允许 `project_local`、`external_public`；`evidence_status` 只允许 `verified`、`conflicting`、`insufficient`、`stale`；`planning_relevance` 只允许 `evidence_only`、`candidate`、`confirmed_applicable`、`not_applicable`。
- 每条 `research_findings` 只保存影响当前规划判断的最小结论与来源定位。项目内来源使用真实文件路径或稳定证据 ID；公开来源使用可追溯 URL，并在可得时记录版本或发布日期。禁止保存网页全文、长引文、搜索结果页、搜索词历史、用户敏感信息或 AI 推理。
- `verified` 只表示来源足以支持客观结论，不等于用户已确认其业务适用性；会改变范围、取舍或验收的结论必须保持 `candidate`，直到用户确认后才转入对应业务事实或 Requirement Pool。
- 调研发现的延期功能正文只进入 Requirement Pool；`research_findings.related_requirement_pool_refs` 与 `relevant_requirement_pool_refs` 只保存 `POOL-ID`。调研结论不得成为第二份延期需求正文。
- 用户初始需求必须在第一条实质性业务问题前写入 `initial_intake_summary`；这里只保存结构化短摘要，不保存整段聊天。
- 收到 Discovery 回答后，必须先把 `latest_feedback` 绑定到当时已持久化的 `discovery_question` 并写为 `recorded`，再更新事实与未决项。完成应用后清除 `raw_user_input`，更新 `last_applied_round_id`，回读校验成功后才允许写入下一条问题。
- `discovery_checkpoint` 是当前期未完成 Planning Context 的最小恢复检查点，不是正式 SoT、Decision Log、完整 Planning Context 副本、访谈历史或研究报告。只保留会改变规划方向、范围、授权、流程或验收的事实、未决项与最小调研结论。
- 已确认延期需求的正文只进入 `<requirement_pool_path>`；`relevant_requirement_pool_refs` 只记录 `POOL-ID`，不得复制需求池正文。
- `execution_handoff_decision` 只保存恢复分支所需的最小镜像：`requires_execution_handoff` 只允许 `true | false`，`handoff_type` 只允许 `execution_ready | planning_only`，`decision_status` 只允许 `candidate | confirmed`；`decision_basis` 只写存在或不存在后续工程任务的原因，`decision_source` 只允许实际使用的 `user_confirmation`、`confirmed_planning_context`、`document_assembly_requirement`。
- Planning Conversation 中已确认的 Planning Context 是 `execution_handoff_decision` 的权威语义来源；本文件只是短期恢复镜像，不是第二套 Planning Context、业务 SoT、完整对话或推理记录。
- `document_assembly.planned_roles` 只记录本期计划装配的职责，不预造文件路径；`generated_documents` 只加入已经真实生成的本期草案及其 `role / path / draft_revision / document_status`，路径必须真实存在。每生成或重建一份草案后立即更新，不得等整批结束再补记。
- `batch_revision` 标识当前整批草案集合；`draft_generation_status` 只允许 `pending`、`generating`、`generated`、`blocked`、`invalidated`。
- `generated_documents[].document_status` 只允许 `draft`、`confirmed`、`reopened`、`invalidated`；`confirmation_queue[].confirmation_status` 只允许 `pending_confirmation`、`awaiting_feedback`、`confirmed`、`reopened`、`invalidated`。
- `confirmation_queue` 只能在当前批次所有计划草案真实生成且跨文档草案校验完成后激活；`current_confirmation` 每次只指向一个真实路径和 draft revision。批量生成中不得创建文档确认交互目标。
- `generation_blocker` 只在 `draft_generation_status: blocked` 时保存 owning role、指向 Discovery `unresolved_items` 的引用与恢复条件；解除后清空，不得复制问题正文或用户回答。
- `design_asset_collection` 仅在 05 当前确认项需要用户提供设计图时出现。`asset_kind` 只允许 `ui | ux`；`collection_status` 只允许 `prompt_ready | awaiting_assets | reviewing_assets | complete | blocked`；`active_prompt_refs` 与 `active_asset_refs` 只保存 05 中的精确 ID@revision，不复制 Prompt 正文或图片内容。
- 给用户输出 UI/UX Prompt 前，必须先把 `target_type: design_asset_batch`、当前 `active_batch_id`、`stage: design_asset_generation_request`、Prompt/ASSET revision 与预期动作持久化；收到图片后先记录 `latest_feedback`，再把实际文件或外部引用写回 05 ASSET。
- 请求用户确认已收到图片前，必须把同一批次切换为 `stage: design_asset_review_confirmation`；确认只作用于该批次实际收到的 ASSET revision，不得同时确认 05 文档或其他图片。
- `design_asset_collection` 是短期恢复指针；完整 Prompt、资产路径、状态、确认来源和覆盖范围仍只写在 05。UI/UX 图收集不得创建第二份设计资产清单、出图日志或独立 Runtime。
- `assembly_status` 只允许 `batch_assembling`、`awaiting_confirmation`、`confirming`、`rebuilding`、`blocked`、`complete`；它描述当前批次所处动作，不替代每份草案和队列项状态。
- 用户纠正上游事实后，只把真实受影响的草案标记 `reopened` 或 `invalidated` 并提升其 draft revision；未受影响的已确认项保持 `confirmed`。
- `document_assembly` 只保存批次、职责、草案真实路径与 revision、生成状态、确认队列、当前确认对象和装配状态，用于恢复当前进度；不得复制正式文档正文、完整 `assembled_documents`、Document Assembly Plan 或 Handoff Package。
- `planning_execution_baseline_reference` 只在执行基线冻结后保存 `phase_id / revision` 的最小恢复引用；完整 Baseline 正文只存在于 13。
- `active_change` 只保存当前 `change_revision / admission_result / change_status / decision_ref`；`decision_ref` 必须使用 `<phase_planning_runtime_directory>/decision-log.md#decision_id=<DEC-ID>` 精确指向本期既有 Change Set Decision Snapshot。该 Snapshot 同时承载完整 Change Set 与按 08 格式生成的 Recovery Output；不得在 `current-interaction.yaml` 复制它们、Baseline、TASK 或执行事实。
- `change_status` 只允许 `candidate`、`confirmed`、`applied_to_planning`、`handoff_prepared`、`closed`、`superseded`。新变化到达时不得直接覆盖尚未关闭的 `active_change`。
- 每一期只使用本期 `<phase_planning_runtime_directory>/current-interaction.yaml`；不得跨期共用或覆盖，不得把本期状态写入 Skill、`.runtime/planning-layer-runtime/`、项目根目录或其他期次目录。
- 第一期和后续任意期次都必须逐轮写 Discovery 检查点；“这是第一次执行”不得成为延迟持久化的理由。
- Discovery 发问前的唯一绑定格式为 `target_type: discovery_question`、`target_id: <DQ-ID>`、`stage: discovery_answer`、`version: <当前 checkpoint revision>`；`latest_feedback.target_id` 必须复制同一 `DQ-ID`。
- 向用户发出任何会影响流程状态的确认问题前，必须先写完整 `active_interaction`；不得等用户回复后再从聊天记忆推断确认对象。
- 文档确认时，`target_id` 使用真实文档路径。
- 设计资产生成请求使用 `target_type: design_asset_batch`、`target_id: <active_batch_id>`、`stage: design_asset_generation_request`；视觉确认使用同一 target 和 `stage: design_asset_review_confirmation`。用户提供图片不自动等于视觉确认。
- 执行交接分支确认固定使用 `target_type: execution_handoff_decision`、`target_id: current_phase_execution_handoff_decision`、`stage: execution_handoff_confirmation`；必须先写入候选镜像和该交互目标，再向用户发问。
- 最终总结确认固定使用 `target_type: final_summary`、`target_id: current_phase_final_summary`、`stage: final_summary_confirmation`；不得把最终总结伪装成正式文档，也不得新增最终总结 SoT 文件。
- `feedback_id` 在本期内唯一；同一 `feedback_id` 只能成功应用一次。
- `latest_feedback` 必须绑定当时已持久化的 `active_interaction`；不得事后转绑下一文档或其他交互目标。
- 同一时间只允许一条未完成反馈。上一条仍为 `recorded` 或 `validated` 时，必须先恢复并处理，不得被新状态变更反馈覆盖。
- `raw_user_input` 只允许在 `recorded`、`validated`、`needs_clarification` 状态保留；进入 `applied`、`already_effective` 或 `rejected` 后必须清空，只保留 `normalized_summary`、类型、目标、结果与下一步。
- 同一反馈不得同时确认当前目标并消费下一目标。
- Planning 真正完成后清空待处理反馈，并将 `planning_status` 设为 `planning_handoff_complete`。

### 1.3 Requirement Pool Format

跨期待处理需求的唯一文件：

```text
<requirement_pool_path>
```

文件存在时，每个条目使用：

```markdown
# Requirement Pool

本文档只保存用户已确认延期、尚待后续期次判断的需求。它不是项目当前事实、当前期范围、正式业务 SoT、TASK 或执行 Backlog。

### POOL-<DOMAIN>-<SEQ>：<需求短标题>

需求摘要：

预期业务价值：

语义比较键：
- 涉及角色：
- 涉及业务对象：
- 涉及流程或场景：
- 预期结果：
- 硬约束：

来源期次或工作包：

来源类型：
- discovery_deferred / scope_admission_deferred / acceptance_deferred

延期原因：

关联当前期 ID：

首次确认时间：

最近更新时间：

最近确认来源：
```

文件与条目规则：

- 文件不存在且没有真实延期需求时视为空池，不预建空文件；第一次确认延期后创建。
- Requirement Pool 只保留尚未被当前期正式消费的条目，因此不使用 `done`、`closed`、`consumed` 等历史状态堆积已完成项。
- `POOL-ID` 在项目规划根目录内稳定唯一。条目按需求语义去重；同一角色、业务对象、流程目标与硬约束指向同一件事时更新既有条目，不新增同义条目。
- 只有用户已确认延期的需求才能写入。候选想法、AI 推测、当前期未决问题、已纳入当前期范围的需求、TASK、Bug、执行状态和完整聊天不得进入。
- 延期决定确认后必须在继续下一轮提问、生成文档、准备 Handoff 或输出总结前写入并回读校验；不得等待本期结束时批量补记。
- 15“下一期输入”和 Handoff 只引用 `<requirement_pool_path>#POOL-ID`，不得复制需求正文或维护第二份状态。

非第一次 Planning 的语义比较只允许三种结果：

```text
same
conflict
unrelated
```

- `same`：主动提醒用户这是历史已确认延期需求，并把 `POOL-ID` 作为 Discovery 来源佐证；用户确认纳入当前期且对应事实已进入当前 Planning Context 后，删除该完整条目。
- `conflict`：在继续范围探索前向用户说明池中旧需求、当前新表达和冲突影响；用户确认最新方向后，先原位更新该 `POOL-ID` 的需求摘要、比较键、来源与最近更新时间，不创建重复条目。仅在更新后的需求随后被当前 Planning Context 正式纳入时删除。
- `unrelated`：不向用户展示，不影响当前探索，不更新、不删除，留待后续期次。

消费和修改规则：

- 正常消费必须删除整个已纳入条目，禁止保留“已完成需求墓地”。
- 冲突处理必须先更新为用户最新确认需求；不得保留旧需求正文作为并列候选，也不得静默以当前输入覆盖。
- 删除或更新前必须核对 `POOL-ID`、当前用户确认与当前 Planning Context 归属。未确认纳入时不得删除。
- 同一次写入只修改命中的条目；不得重排、重写或清理无关需求。
- 文件更新失败时停止消费、延期或下一轮 Planning 推进，不得只靠聊天记忆继续。

### 1.4 Planning Execution Baseline / Change Format

Planning Execution Baseline 完整正文的唯一承载是：

```text
<phase_planning_directory>/13-开发任务合同与落地清单.md
```

首次生成 13 只读取已确认且适用的 01–12；用户确认 13 后，才在同一文件中追加并冻结以下区块。Handoff 已生成、14/15 已派生或任一 TASK 已开始时，也必须引用同一冻结基线：

```yaml
planning_execution_baseline:
  phase_id:
  revision:
  frozen_at:
  source_documents: []
  active_task_contracts: []
  acceptance_scope: []
  frontend_baseline_binding:
```

冻结后不得静默覆盖。13 的当前有效 TASK 视图可以通过 Change Set 增量更新，但历史冻结快照只能保留或追加新 revision，不得覆盖旧 revision。`revision` 只用于 Planning 与证据追踪，不得进入代码、数据库、API、权限、配置、目录、类名或其他长期实现命名。

执行、联调、测试或验收发现问题时，先在现有 14 偏差/阻断/回写区或 15 测试结果/复盘区承载以下判定；不得创建独立 Change Log：

```yaml
change_decision:
  source_stage:
  finding_type:
  observed_result:
  expected_source:
  is_current_plan_still_valid:
  affected_ids: []
  planning_reentry_required:
  reentry_documents: []
  change_level:
  disposition:
```

`finding_type` 只允许 `implementation_defect`、`test_defect`、`planning_gap`、`requirement_change`、`design_drift`、`deferred_improvement`。`disposition` 只允许 `fix_in_execution`、`fix_in_test`、`reopen_current_planning`、`defer_to_next_phase`、`reject_change`。

冻结后准入本期的完整 Change Set 历史，只能作为追加式 Decision Snapshot 写入：

```text
<phase_planning_runtime_directory>/decision-log.md
```

Change Set 是范围准入、影响分析与增量执行选择的 Runtime 证据，不是业务 SoT，不代替受影响的 00–15，不复制其正文，也不保存 AI 私有推理。每个快照使用：

```yaml
change_set:
  base_revision:
  change_revision:
  previous_change_revision:
  supersedes_change_revision:
  admission_result:
  change_status:
  change_source:
  change_reason:
  added_ids: []
  modified_ids: []
  superseded_ids: []
  unaffected_ids: []
  affected_documents: []
  affected_tests: []
  affected_tasks: []
  execution_delta:
    executable_tasks: []
    reopened_tasks: []
    carried_forward_pending_tasks: []
    context_only_tasks: []
    completed_unchanged_tasks: []
    prohibited_rerun_tasks: []
```

保护范围：`unaffected_ids` 不得因为存在 Change Set 被无条件 reopen；`context_only_tasks` 不得执行；`completed_unchanged_tasks` 不得重新执行；`prohibited_rerun_tasks` 不得重新执行或重新生成 EXEC。

允许处理范围：`executable_tasks`、`reopened_tasks`、`carried_forward_pending_tasks` 可以按明确 TASK contract revision 与 Handoff 队列执行，不得扩大影响范围。禁止把整个 `execution_delta` 解释为保护或禁止执行范围。

`execution_delta` 的六个列表必须两两互斥，同一 TASK 只能出现一次。未受影响且已完成者进入 `completed_unchanged_tasks`；`prohibited_rerun_tasks` 只记录未被其他列表归类、但依据明确合同或既有事实禁止重跑的 TASK，不得与 `completed_unchanged_tasks` 重复。

`previous_change_revision` 用于连续 Change Set 链；只有新 Change Set 使旧 Change Set 失效时才填写 `supersedes_change_revision`，并把旧快照状态追加为 `superseded`。所有旧快照保留，不覆盖。

每个当前 active Change Set Snapshot 的 `added_ids / modified_ids / superseded_ids / unaffected_ids / affected_* / execution_delta` 都必须表达“相对冻结 Baseline 的累计有效增量”，包含仍有效的前序 revision 结果和当前 revision 变化。`previous_change_revision` 只保留链关系，Recovery 不得通过扫描旧快照补齐当前范围。

当新 revision 继续承接旧 revision 而非替代它时，旧 revision 保留其真实最后状态；active 指针前移不自动把旧 revision 推断为 `closed` 或 `superseded`。只有对应执行与验收真实完成时才追加 `closed`，只有被后续变化明确替代时才追加 `superseded`。

Change Set 与 `active_change.change_status` 共用同一状态枚举：`candidate`、`confirmed`、`applied_to_planning`、`handoff_prepared`、`closed`、`superseded`。

延期需求无论 15 是否存在，都立即进入唯一 `<requirement_pool_path>`。15 的“下一期输入”、planning_only Handoff 或 execution_ready Handoff 只记录本期产生或引用的 `POOL-ID` 与真实路径，不复制条目正文。不得为记录延期需求提前生成 13、14、15。

## 2. 一级标题

```markdown
# 第X期<文档主题>
```

## 3. 固定边界章节

```markdown
## 1. 文档边界
```

格式：

```markdown
本文档确认……

本文档正文进入……

相邻内容由 `xx` 文档承接。
```

## 4. 文档 ID 规范

统一 ID：

```text
REQ-xxx
POOL-xxx
FLOW-xxx
SCN-xxx
DOMAIN-xxx
MODULE-xxx
ARCH-xxx
CAP-xxx
PAGE-xxx
UI-MOD-xxx
UX-SCN-xxx
PROMPT-STYLE-xxx
PROMPT-PAGE-xxx
PROMPT-MODULE-xxx
PROMPT-UX-xxx
ASSET-xxx
STATE-xxx
API-xxx
PERM-xxx
TASK-xxx
RISK-xxx
DEP-xxx
OPEN-xxx
EXEC-xxx
TEST-xxx
```

规则：

- 全局唯一
- 稳定
- 不允许同义重复
- 不允许自然语言替代
- 本节 ID 全部是 `trace_only`，只用于 Planning 文档、执行/验收记录和变更证据追踪；不得转换为长期代码、数据库、API、权限、配置、迁移或测试套件命名。
- `POOL-ID` 只用于跨期待处理需求引用，不得直接成为 REQ、TASK 或实现命名；需求纳入当前期后仍须生成本期自己的 `REQ-ID`，再删除已消费池条目。
- ID 中的期次、阶段、Sprint 或版本标识不代表物理技术域；完整边界以 `01-planning-core-rules.md#32-planning-trace-id-boundary` 为唯一来源。
- PROMPT 必须关联适用的 PAGE、UI-MOD 或 UX-SCN；PROMPT-STYLE 必须关联适用页面、模块或 UX 范围。
- ASSET 在 `received`、`review_pending`、`visual_confirmed` 或 `superseded` 状态下必须关联实际收到的图或明确的外部引用。
- PAGE、UI-MOD、UX-SCN 均不得替代 FLOW、STATE、API、PERM 的事实定义。
- ARCH 必须关联已确认的 FLOW、MODULE、STATE、API 或 PERM，不得替代这些上游事实定义。
- RISK、DEP、OPEN 的正式 ID 只能由 12 创建；01–11 只能移交信号或待确认问题。
- EXEC 只能用于 14 的预置执行框架，不得表示实际执行已经发生。

## 4.1 决策状态规范

适用于关键业务流、权限、数据、状态、UI、外部能力和高风险结论。

```text
candidate
confirmed
superseded
rejected
```

规则：

- 场景级用户确认前，只能是 `candidate`。
- 用户明确确认后，才能是 `confirmed`。
- 后续被用户纠正时，旧结论标记 `superseded`，新结论重新记录。
- 明确不采用的方案标记 `rejected`。
- `candidate` 不得作为最终 SoT 结论，只能进入待确认项或风险。

Capability ID 使用：

```text
CAP-<DOMAIN>-<SEQ>
```

示例：

```text
CAP-MAP-001
CAP-VOICE-001
CAP-OCR-001
CAP-PAY-001
```

## 4.2 Flow Contract

`01-需求范围与验收标准.md` 的业务旅程必须使用：

```markdown
### FLOW-XXX：<业务旅程名称>

业务目标：

关联需求：
- REQ-XXX

参与角色：

合法入口：

起始状态：

必要前置：
- 身份：
- 会话：
- 组织/租户：
- 可见范围：
- 业务上下文：
- 前序业务事实：

允许步骤：
1.
2.
3.

每步预期可见结果：

成功终态：

异常与阻断：

禁止跳步 / 非法路径：
-
-

不做范围：

关联对象：
- DOMAIN-XXX

关联后续测试：
- TEST-XXX

Priority：
```

规则：

- 每个 P0 REQ 必须归属至少一条 FLOW。
- 每条 FLOW 必须有合法入口、起始状态、必要前置、成功终态和禁止跳步。
- 每个业务动作必须说明谁在什么条件下可以做。
- 01 必须同时定义正向验收和反向验收。

## 4.3 Journey-Object Map

`02-业务域模型.md` 必须按 01 的 FLOW 顺序生成：

```markdown
## 旅程—对象关系地图

| FLOW | 前置对象/事实 | 读取对象 | 新建/改变对象 | 成功事实 | 必须阻断条件 | 禁止对象关系 |
| --- | --- | --- | --- | --- | --- | --- |
```

规则：

- 01 每条 FLOW 都必须在 02 中有对应关系行。
- 01 的前置、动作或终态在 02 无对象或关系支撑时，02 不得确认。
- 02 新增会改变 01 旅程的对象关系时，必须回到 01 修正。

## 4.4 Access Context

有效访问上下文：

```text
用户主体
+ 有效会话
+ 组织/租户上下文
+ 角色分配
+ 项目/区域或业务可见范围
+ 当前动作所需资格
```

边界：

- 02 只定义业务资格与关系。
- 08 才定义权限矩阵、数据可见性、越权响应和接口级校验。

必须明确：

- 用户 ≠ 角色。
- 角色 ≠ 项目/区域操作资格。
- 管理员身份 ≠ 自动拥有区域组长业务资格。
- 历史审批人 ≠ 新流程生效权。

## 4.5 Current / Target / Legacy Object Treatment

`02-业务域模型.md` 必须包含：

```markdown
## 当前对象与目标对象处理矩阵

| 对象或旧流程 | 当前真实语义 | 本期目标关系 | 处理策略 | 是否可进入新流程 | 禁止关系 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
```

处理策略只允许：

```text
inherit
adapt
create
deprecate
block
readonly
cleanup
```

禁止使用：

```text
尽量兼容
视情况复用
后续再看
可能保留
```

## 4.6 负向对象关系

02 必须明确关键旧对象或旧流程对新流程的禁止关系。

格式：

```markdown
旧对象或旧流程：

禁止关系：
- 不得创建新流程记录
- 不得作为新流程前置
- 不得更新新流程状态
- 不得成为工作台下一步动作来源
- 不得映射为新流程有效状态
```

边界：

- 02 定义业务对象关系事实。
- 06 定义状态迁移禁止。
- 07 定义接口阻断。
- 08 定义权限阻断。
- 09 定义技术迁移与清理策略。

## 4.7 Scenario Contract

`03-用户场景与交互流程.md` 的核心 ID 使用：

```text
SCN-<DOMAIN>-<SEQ>
```

格式：

```markdown
### SCN-XXX：<用户场景名称>

关联业务旅程：
- FLOW-XXX

关联业务对象与资格：
- DOMAIN-XXX
- ACCESS-CONTEXT-XXX

参与角色：

合法进入条件：
-

用户起点：

交互步骤：

| 步骤 | 用户动作 | 系统处理 | 用户可见结果 |
| --- | --- | --- | --- |

分支：
- 正常完成：
- 前置缺失：
- 权限不足：
- 外部能力失败：
- 用户取消：

恢复或退出：
- 返回位置：
- 可重试条件：
- 人工协助条件：

禁止的用户路径：
-

需要的界面承接：
- PAGE-XXX
- UI-MOD-XXX
- UX-SCN-XXX（如需要）
```

规则：

- 每个 SCN 只引用既有 FLOW。
- SCN 的进入条件不得弱于 FLOW 前置。
- SCN 不得新增主业务旅程、合法入口、成功终态或禁止路径。
- 前置由既有系统承接时，必须写明“由既有体验承接”以及恢复成功后进入哪个 PAGE。

## 4.8 Module Boundary Format

`04-功能拆解与边界说明.md` 只定义系统能力模块，不定义用户页面或技术实现。

模块格式：

```markdown
### MODULE-XXX：<模块名称>

模块类型：
- 核心业务能力模块
- 横向边界模块
- 外部能力适配依赖

关联 FLOW：
- FLOW-XXX

关联 SCN：
- SCN-XXX

模块业务责任：

模块非责任：

模块输入业务事实：

模块输出业务能力：

上游模块依赖：

下游消费方：

模块隔离边界：

旧流程/旧语义隔离责任：

优先级：
```

覆盖矩阵：

```markdown
## 业务旅程—场景—模块覆盖矩阵

| FLOW | SCN | 必须模块 | 主模块 | 协作模块 | 缺失模块后的结果 | 旧模块隔离要求 |
| --- | --- | --- | --- | --- | --- | --- |
```

规则：

- 每一条 P0 FLOW 必须至少有一个主模块承接。
- 每一个关键 SCN 必须至少有一个模块负责。
- 每个模块必须有明确“负责 / 不负责”。
- 每个关键旧流程必须有明确隔离模块。
- 任何旧审批、旧入口、旧状态、旧对象不得以“视情况复用”方式存在。
- 外部能力适配依赖只表达依赖关系，不定义 SDK、版本、鉴权、真实调用或 Provider 细节；这些属于 10。

旧对象处理只允许：

```text
inherit
adapt
create
deprecate
block
readonly
cleanup
```

禁止使用：

```text
尽量兼容
视情况复用
可能保留
后续再看
```

旧流程隔离格式：

```markdown
旧模块：

隔离要求：
- 不得服务哪些 FLOW：
- 不得成为哪些 MODULE 的输入：
- 不得成为哪些 MODULE 的状态来源：
- 不得成为哪些 MODULE 的生效来源：
```

示例：

```text
旧审批模块
× 不得为第二天任务开始模块提供提交路径
× 不得提供生效前置
× 不得提供状态来源
× 不得成为工作台下一步动作来源
```

## 4.9 UI/UX Design Format

`05-前端页面与UI/UX交互设计.md` 可以兼容旧文件路径 `05-前端页面与UI交互设计.md`，但正文标题和职责必须使用“UI/UX交互设计”。

本节维护 Planning ID 与既有 05 基础格式；copy-ready Prompt、页面/模块实现合同、UX 状态迁移、版本化资产、Manifest、Handoff 精确绑定和执行门禁的完整唯一格式见 `11-planning-ui-ux-execution-contract.md`。涉及 UI TASK 时两者同时适用，发生格式简略与执行合同冲突时以 11 的更严格字段为准。

05 必须区分：

- 交互合同确认：页面承接的 SCN、页面状态、主次操作、禁用操作、异常恢复和旧入口处理。
- 视觉资产确认：风格图、完整页面图、局部模块图、UX 交互图是否收到、审阅、确认或需要重做。

05 开始前必须记录：

```yaml
style_inheritance_decision:
  mode:
  baseline_source:
  inherited_scope: []
  changed_scope: []
  change_reason:
  affected_assets: []
  user_confirmation:
```

`mode` 只允许 `inherit_current`、`extend_current`、`replace_current`，默认 `inherit_current`。`baseline_source` 必须指向 `PROJECT-CURRENT-BASELINE.md` 中已确认的当前前端体验事实或其权威来源。继承模式下不要求机械新建 PROMPT-STYLE。

Handoff 的前端体验绑定使用以下唯一子格式，不复制 05、09、11 或 13 正文：

```yaml
frontend_experience_binding:
  applicable:
  design_document_path:
  design_contract_version:
  design_manifest_ref:
  baseline_source:
  style_mode:
  reference_pages: []
  required_existing_components: []
  allowed_extensions: []
  prohibited_redefinitions: []
  prompt_refs: []
  page_contract_refs: []
  module_contract_refs: []
  interaction_contract_refs: []
  confirmed_design_assets:
    - id:
      revision:
      path_or_url:
      status: visual_confirmed
  consistency_tests: []
```

- 存在 UI TASK 或前端体验变化时 `applicable: true` 且所有适用字段必填；否则为 `false`，其余字段为空或省略。
- `style_mode` 必须等于 05 的 `style_inheritance_decision.mode`；`baseline_source` 引用当前前端体验基线或已确认替换目标。
- `design_document_path` 必须是 05 的真实路径；`design_contract_version` 固定为 `ui-ux-execution/v1`；`design_manifest_ref` 必须解析到 05 的唯一 Manifest。
- `prompt_refs`、`page_contract_refs`、`module_contract_refs` 与 `interaction_contract_refs` 必须同时携带 ID、revision 和 05 内锚点；不得只给编号或聊天上下文。
- `confirmed_design_assets` 只能引用真实存在且已 `visual_confirmed` 的同 revision 资产，并携带真实路径或外部引用；`consistency_tests` 只引用 11 中相关 TEST-ID。
- `required_existing_components` 要求优先复用现有组件；`allowed_extensions` 只列允许新增部分；`prohibited_redefinitions` 禁止重写全局导航、主题、公共组件和未受影响页面。
- `frontend_experience_binding` 与 05 `design_delivery_manifest`、13 `frontend_contract_binding` 的路径、ID 和 revision 必须一致；任何不一致都阻断 UI TASK Ready。

### PROMPT-STYLE-XXX：<全局风格统一性提示词>

所有 PROMPT 必须先按 `11-planning-ui-ux-execution-contract.md` 填写 `prompt_revision`、`prompt_type`、`target_tool`、`language`、`reference_inputs`、`output_spec`、`required_constraints`、`negative_constraints` 与 fenced `prompt_body`。以下各节只补充不同 Prompt 类型的语义要求。

必须覆盖：

- 产品类型
- 目标用户
- 使用端与设备尺寸
- 品牌与业务气质
- 色彩与层级
- 字体与信息密度
- 卡片、表单、按钮、导航、反馈组件语言
- 图标与插图风格
- 异常、空、加载、禁用状态风格
- 中文界面要求
- 一致性约束
- 禁止出现的风格或旧业务语义
- 适用 PAGE / UI-MOD / UX-SCN 范围

规则：

- PROMPT-STYLE 不生成某个具体业务页面。
- PROMPT-STYLE 是 PROMPT-PAGE、PROMPT-MODULE、PROMPT-UX 的共同风格前缀。
- 只有 `replace_current`，或 `extend_current` 确实需要新增跨页面风格规则时，才生成或修订 PROMPT-STYLE；`inherit_current` 直接使用已确认的 inherited frontend baseline reference。
- `replace_current` 必须列出受影响 PAGE / UI-MOD / UX-SCN / PROMPT / ASSET，并使相关资产进入重新审查；不得伪装成普通新增页面。

### PAGE-XXX：<页面名称>

页面提示词 ID：

```text
PROMPT-PAGE-<DOMAIN>-<SEQ>
```

页面提示词必须包含：

- 关联 FLOW / SCN / MODULE
- 页面目标
- 目标角色
- 合法进入条件
- 页面完整信息结构
- 当前 UI 状态
- 唯一主操作
- 次级操作
- 必须隐藏或禁用的操作
- 空、错、加载、阻断状态
- 成功后可见变化
- 失败后的恢复或退出
- 继承的全局风格要求
- 完整页面生成要求
- 目标工具或 `tool_agnostic`、参考资产 revision、视口、画幅、分辨率与帧数
- 可直接复制且无需依赖聊天上下文的完整 `prompt_body`
- 明确的 required constraints 与 negative constraints

规则：

- 页面提示词必须生成完整页面，不得只生成局部卡片。
- 每个 PAGE 必须定义合法进入条件。
- 每个 UI STATE 只能有 0 或 1 个主操作。
- 05 不得借页面设计改变 FLOW、资格、状态语义或权限规则。
- 每个进入 UI TASK 的 PAGE 还必须提供 `11-planning-ui-ux-execution-contract.md` 定义的 UI Implementation Contract，覆盖 design token、布局、响应式、组件、全部适用状态、内容边界、无障碍、动效反馈和实现验收断言。

### UI-MOD-XXX：<局部模块名称>

模块提示词 ID：

```text
PROMPT-MODULE-<DOMAIN>-<SEQ>
```

模块化设计只用于：

- 局部按钮状态变化
- 弹窗
- 抽屉
- 提示条
- 表单块
- 卡片局部变化
- 空状态模块
- 异常提示模块
- 上传重试模块
- 图标或状态反馈变化

模块提示词必须包含：

- 所属 PAGE
- 关联 SCN
- 基准页面或基准资产
- 局部模块范围
- 触发条件
- 变化前状态
- 变化后状态
- 用户可见结果
- 必须保留的周围 UI
- 必须保持的全局风格
- 禁止重画整页
- 禁止新增未确认业务动作
- 目标工具或 `tool_agnostic`、参考资产 revision、局部输出画幅与完整 `prompt_body`

规则：

- 不是每个技术 MODULE 都必须生成 UI 图。
- 只有用户可见的页面或局部交互模块才需要 UI 设计资产。
- 先有页面整体设计，再补局部模块设计。
- 进入 UI TASK 的 UI-MOD 必须使用与 PAGE 相同的 UI Implementation Contract 字段集，并将布局、状态、资产和验收范围限定到所属 PAGE 的指定局部区域。

### UX-SCN-XXX：<UX交互场景名称>

UX 提示词 ID：

```text
PROMPT-UX-<DOMAIN>-<SEQ>
```

UX 必须优先复用已收到的页面图和模块图。

每个 UX 场景必须记录：

- 关联 FLOW
- 关联 SCN
- 起始 PAGE
- 经过的 PAGE / UI-MOD
- 用户动作
- 页面可见变化
- 成功结果
- 失败、重试、取消、返回与人工协助路径
- 已有 UI 图是否足以表达
- `contract_revision`
- From UI state、Trigger、Preconditions、Domain/API intent、Pending feedback、Success/Failure UI state、Recovery/Retry、Cancel/Back、Forbidden actions 与 Visible evidence 的逐步状态迁移表

UX 图状态只允许：

```text
covered_by_existing_ui_assets
ux_asset_required
ux_asset_received
ux_asset_confirmed
superseded
```

只有以下情况生成 PROMPT-UX：

- 现有静态页面图无法说明多步交互。
- 同一页面多状态切换无法说明。
- 异常恢复、取消、回退或人工协助路径不清楚。
- 弹窗、抽屉、多页面跳转关系不清楚。
- 旧入口迁移后的用户路径不清楚。

PROMPT-UX 必须生成多帧交互设计图，或带页面缩略图、箭头、状态说明的交互流程图。PROMPT-UX 不得重新设计页面视觉风格，不得重写 FLOW、资格、状态语义或权限规则。

PROMPT-UX 还必须按 11 提供目标工具、参考资产 revision、帧数、画幅、分辨率、negative constraints 与完整 `prompt_body`。叙事性流程说明不能替代 UX Interaction Contract。

### ASSET-XXX

```markdown
### ASSET-XXX

资产类型：
- global_style
- page_ui
- module_ui
- ux_interaction

关联：
- FLOW：
- SCN：
- MODULE：
- PAGE：
- UI-MOD：
- UX-SCN：
- PROMPT：

来源：
- user_provided
- user_generated
- external_reference

资产路径或引用：

资产 revision：

内容指纹（可获得时）：

资产状态：
- planned
- prompt_ready
- received
- review_pending
- visual_confirmed
- superseded

覆盖说明：

未覆盖项：

确认结论：

用户确认引用（`visual_confirmed` 必填）：

确认时间（`visual_confirmed` 必填）：
```

规则：

- 不得虚构图片、路径、设计资产或“已出图”结论。
- 用户未提供图时，只能是 `planned` 或 `prompt_ready`。
- 设计资产已生成不等于页面已开发、页面已测试、页面已验收或已上线。
- UI 依赖开发任务只能在所需页面或模块资产达到 `visual_confirmed` 后生成或进入可执行状态。
- 不依赖 UI 的后续规划文档不应被无故阻塞。
- 同一资产内容变化必须提升 `asset_revision`；不得在原 revision 下静默替换。
- `visual_confirmed` 必须携带真实路径或外部引用、revision、用户确认来源和确认时间。
- Long 只能消费 Handoff 明确列出的 `ASSET-ID@revision`，不得自行选择目录中的最新文件。

覆盖矩阵：

```markdown
## FLOW—SCN—MODULE—PAGE—合同—资产—TEST 覆盖矩阵

| FLOW | SCN | MODULE | PAGE / UI-MOD | Prompt ref | UI contract revision | UX-SCN revision | Confirmed asset ref | TEST ref | Execution readiness |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

规则：

- 每个 P0 SCN 必须有 PAGE 和 UI STATE 承接。
- 每个关键异常 SCN 必须定义恢复、退出或人工协助界面。
- 每个 PAGE 必须定义合法进入条件。
- 每个 UI STATE 只能有 0 或 1 个主操作。
- 旧入口必须逐项定义唯一的页面处理方式：`redirect`、`block` 或 `readonly`。
- 不得同时把“跳转、阻断、只读”写成同一旧入口的并列候选。
- 每个进入 UI TASK 的行必须有 Prompt revision、UI contract revision、UX contract revision（适用时）、`visual_confirmed` ASSET revision 与 TEST-ID；`Execution readiness` 只允许 `design_ready`、`execution_ready` 或 `blocked:<reason>`。05 首次确认可为 `design_ready`，UI TASK Ready 前必须为 `execution_ready`。

## 4.10 Data / State Contract Format

`06-数据模型与状态流转.md` 是业务事实与状态合法性的唯一 SoT。

状态分类只允许：

```text
domain_state
derived_action_state
interaction_state
exception_state
legacy_boundary_state
data_domain_state
```

定义：

- `domain_state`：持久业务状态，例如已提交、已生效、已关闭。
- `derived_action_state`：由业务状态、资格、上下文和异常事实推导出的当前可做什么状态，例如当前可提交、当前需补资料。
- `interaction_state`：UI 暂态，例如确认弹窗打开、提交中、上传中、重试中；默认由 03 / 05 管理，只有确实需要持久化、断点恢复或审计时，才可升为 06 状态。
- `exception_state`：业务或外部能力失败后需要恢复、补充或人工协助的状态。
- `legacy_boundary_state`：旧入口、旧对象、旧审批、旧状态的只读、阻断、迁移或清理边界。
- `data_domain_state`：测试、预发布、生产等数据域及其隔离状态。

06 必须包含：

```markdown
## FLOW—事实—事件—状态映射

| FLOW | 前置业务事实 | 触发事件 | 允许状态变化 | 成功事实 | 阻断事实 | 关联 MODULE | 关联 API | 关联 TEST |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

每一个 P0 FLOW 必须具备：

- 前置业务事实
- 明确触发事件
- 允许状态变化
- 成功后的新业务事实
- 阻断事实
- 非法来源

状态分类表：

```markdown
| 状态 ID | 状态类别 | 是否持久化 | 唯一来源 | 触发事件 | 可读取方 | 可触发变化者 | 下游用途 |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

规则：

- 派生动作状态不得成为业务写入的唯一放行依据。
- 前端、路由、本地缓存、旧审批记录、旧入口来源不得自行生成或伪造状态。
- 派生动作状态必须由后端根据真实业务状态、资格、上下文和异常事实稳定推导。
- 禁止把“没有任务”直接迁移为“可打卡”或其他可写状态。
- 可执行状态必须通过任务已分配、项目/区域上下文完整、当前用户具备资格等明确业务事实重新计算。
- “字段”只能表示业务逻辑所需事实，不得定义表名、字段类型、长度、索引、外键、SQL、ORM Schema 或迁移脚本。
- `data_domain_state` 和“独立数据域”只定义数据来源、访问范围、状态来源、写入边界以及生产/测试隔离，不得推导以期次、Sprint、阶段或版本命名的数据库表、代码模块、API 命名空间或权限体系。
- 是否新增物理模型或模块由执行前真实架构检查决定，且必须采用 09 确认的稳定业务概念与实现承接策略。

状态迁移守卫格式：

```markdown
状态迁移：

触发事件：

前置事实：

允许角色资格：

允许数据范围：

禁止来源：

成功后的新事实：

失败后的阻断状态：

是否可重试：

是否可回滚：

关联 API：

关联 PERM：

关联 TEST：
```

不得只写：

```text
A -> B
```

旧对象与旧状态隔离映射：

```markdown
## 旧对象与旧状态隔离映射

| 旧对象 / 旧状态 | 当前允许用途 | 不可映射目标 | 是否可读取 | 是否可写入 | 是否可作为状态来源 | 处理策略 |
| --- | --- | --- | --- | --- | --- | --- |
```

处理策略只允许：

```text
inherit
adapt
create
deprecate
block
readonly
cleanup
```

旧审批、旧申请、旧状态若只能用于历史只读，必须明确：

- 不得成为新流程写入前置。
- 不得成为新流程生效来源。
- 不得成为新工作台下一步动作来源。
- 不得映射为任何新流程有效状态。

## 4.11 Canonical API Contract Format

`07-接口设计与前后端契约.md` 定义前后端读写、拒绝和恢复语义的 Canonical API Contract。

接口类型：

```text
QUERY
COMMAND
DECISION_VIEW
LEGACY_BOUNDARY
```

定义：

- `QUERY`：只读取业务事实，不改变状态。
- `COMMAND`：触发业务事件，可能改变业务事实或状态。
- `DECISION_VIEW`：返回由 06 推导出的当前可操作状态或下一步动作，只读。
- `LEGACY_BOUNDARY`：定义旧对象、旧接口、旧入口的只读、阻断、迁移或解析边界。

规则：

- DECISION_VIEW 不得成为业务状态唯一来源。
- DECISION_VIEW 不得绕过 COMMAND 的状态守卫。
- 前端不得使用本地缓存、旧接口、旧审批状态或来源参数自行推导主操作。
- 07 不得把 08 作为正式上游 SoT。
- 07 可以引用 02 的业务资格关系，以及 06 的状态前置、触发事件和迁移守卫。
- 07 只声明接口所需的访问上下文、业务资格、状态与事实前置，不重写完整权限矩阵、数据可见范围策略或越权展示策略。

Canonical Contract 与 Architecture Binding 分离：

```text
07 Canonical API Contract：
- 业务意图
- 请求语义
- 响应语义
- 错误语义
- 状态守卫
- 禁止字段
- 幂等与并发语义

09 Architecture Binding / Implementation Boundary：
- 目标逻辑承接层
- 依赖方向
- 可复用技术基础
- 禁止复用旧语义
- 旧流程切断位置
```

规则：

- 09 不得擅自改变 07 的方法、路径、请求语义、响应语义、状态前置或错误语义。
- 09 不定义具体文件路径、目录、代码、SDK 初始化、环境变量名称、任务拆分或实际实施结果。
- 若 Canonical API Contract 发生改变，必须回写 07，并触发 08、11、13 等下游失效传播。

单接口格式：

```markdown
API-ID：

Contract Type：
- QUERY / COMMAND / DECISION_VIEW / LEGACY_BOUNDARY

关联 FLOW：
关联 SCN：
关联 MODULE：
关联 PAGE / UI-MOD：

业务意图：

触发业务事件：
- COMMAND 必填
- QUERY / DECISION_VIEW 不适用时显式标记

合法访问上下文：

所需业务资格：

状态与事实前置：
- 只引用 06，不重新定义

请求：
- 允许字段
- 禁止字段
- 字段业务语义

成功结果：
- 返回的新业务事实
- 返回的状态引用
- 是否返回最新决策视图

拒绝结果：
- errorCode
- errorClass
- retryable
- safeRecovery
- nextUserIntent

幂等与并发：
- 幂等要求
- 重复提交结果
- 并发冲突结果

旧流程边界：
- 禁止读取的旧状态
- 禁止写入的旧对象
- 历史兼容唯一允许范围

Canonical Physical Binding：
- 方法
- 路径
- 稳定性说明

关联 TEST：
- 正向合同测试
- 输入非法测试
- 状态守卫测试
- 权限 / 范围测试
- 幂等与并发测试
- 旧流程隔离测试
```

所有会改变业务状态的 `COMMAND` 必须明确：

- 幂等策略：必须使用幂等键，或明确等价的服务端去重策略。
- 重复提交：不得重复创建业务事实或重复改变状态；必须返回稳定的同一业务结果或最新业务摘要。
- 并发冲突：必须返回稳定错误码、冲突结果或最新状态摘要。
- 成功响应：必须返回足以刷新页面与决策视图的最新业务事实。

具体并发一致性架构边界由 09 决定；数据库锁、事务、缓存等代码实现方式由 13/14 和执行层承接。

旧审批与旧接口的接口级封锁：

若业务明确“新流程直接生效，不经过旧审批”，对应 COMMAND 必须显式定义：

```text
禁止输入字段：
- taskRequestId
- approvalStatus
- approvedBy
- approvalAction
- pendingApproval
- approved
- rejected
- 以及任何等价审批字段

禁止状态来源：
- 旧审批记录
- 旧申请记录
- 管理员审批结果
- 旧任务申请上下文

禁止返回语义：
- PENDING_APPROVAL
- APPROVED
- REJECTED
- 待管理员审核
- 管理员审批完成
```

历史旧对象若允许读取，必须明确：

```text
只读展示
≠ 新流程判断依据
≠ 新流程写入依据
≠ 新流程生效依据
≠ 新工作台下一步动作来源
```

`source` 参数语义：

```text
source = 客户端来源、兼容判断或审计辅助信息

source ≠ 身份
source ≠ 角色
source ≠ 项目 / 区域范围
source ≠ 提交资格
source ≠ 状态放行条件
```

## 4.12 Permission / Scope / Deny Strategy Format

`08-权限、数据可见性与异常处置边界说明.md` 定义后端不可绕过的访问决策、数据范围、拒绝分类、异常协助与历史访问策略。

访问决策模型：

```text
已认证用户
+ 目标动作
+ 目标资源
+ 租户 / 项目 / 区域范围
+ 业务资格
+ 当前业务状态
+ 当前数据域
```

拒绝类型只允许：

```text
authentication_denied
authorization_denied
scope_denied
state_guard_denied
legacy_source_denied
data_domain_denied
external_capability_blocked
```

定义：

- `authentication_denied`：未认证或会话无效。
- `authorization_denied`：无角色或业务资格。
- `scope_denied`：不在租户、项目、区域、任务等可访问范围。
- `state_guard_denied`：业务前置、业务状态或迁移守卫不满足。
- `legacy_source_denied`：旧对象、旧状态、旧审批、旧入口试图影响新流程。
- `data_domain_denied`：测试、预发布、生产等数据域隔离违规。
- `external_capability_blocked`：定位、图片、外部平台等能力失败，需恢复或人工协助。

不得把这些全部笼统写成“权限不足”或“异常”。

范围词典：

```text
SELF_TASK
ASSIGNED_REGION
MANAGED_PROJECT
CURRENT_TENANT
TEST_DOMAIN
PRODUCTION_DOMAIN
HISTORICAL_READONLY
```

如项目有其他稳定范围，使用同样结构扩展；禁止自然语言模糊表达。

权限策略格式：

```markdown
PERM-ID：

关联 FLOW：
关联 API：
关联 DOMAIN：
关联 STATE：

动作：

资源：

允许主体：

允许范围：

业务资格：

业务状态前置：

数据域前置：

允许结果：

拒绝类型：

拒绝原因码：

是否允许只读：

是否允许人工协助：

旧流程禁止来源：

关联 TEST：
```

规则：

- 前端隐藏、禁用或不展示按钮，只是体验。
- 08 定义的 PERM 决策，必须由后端或服务端边界实际执行。
- 任何前端、接口参数、来源参数、旧审批记录、旧入口、管理员身份都不得绕过 PERM 决策。

工作人员协助边界：

```text
工作人员协助 = 诊断、技术恢复、引导用户回到正常路径

工作人员协助 ≠ 代替用户提交业务动作
工作人员协助 ≠ 直接修改正常业务状态
工作人员协助 ≠ 代替业务资格主体生效
工作人员协助 ≠ 代替区域负责人或其他业务角色完成关键动作
```

每一项工作人员协助必须定义：

- 能读取什么诊断信息。
- 可执行什么技术动作。
- 不能修改什么业务事实。
- 协助完成后用户回到哪个合法场景。

若确实需要人工改变业务事实，必须回到 01、02、06 定义新的合法业务事件，不得由 08 默认放行。

旧流程与历史访问边界：

- 旧对象没有任何新流程 COMMAND 权限。
- 历史记录只有在满足 HISTORICAL_READONLY 范围时允许读取。
- 旧对象、旧审批、旧状态不得作为新流程状态、资格、前置或生效来源。
- 具体用户跳转、阻断页面、只读页面由 03 / 05 定义。
- 具体接口实现、旧路由删除、旧服务迁移由 09 定义逻辑切断位置，并由 13/14 和执行层承接。

## 4.13 06/07/08 Test Mapping Format

06、07、08 都必须成为 11 自动化测试设计的上游依据，但不得把 11 重写为测试执行文档。

每条关键 `STATE`、`API`、`PERM` 必须明确关联 TEST-ID，并至少覆盖：

- 正向业务规则测试
- 非法输入测试
- 非法状态迁移测试
- 资格拒绝测试
- 范围拒绝测试
- 数据域隔离测试
- 幂等测试
- 并发冲突测试
- 旧流程来源拒绝测试
- 历史只读测试
- 工作人员协助越界测试

自动化等级只允许：

```text
mandatory_automated
automated_preferred
manual_or_real_environment_required
```

原则：

- API 合同、状态迁移、权限、范围、幂等、并发、旧流程隔离默认必须自动化。
- 视觉一致性、复杂体验、真机硬件能力、外部真实环境可标记为人工或真实环境验证。

## 4.14 Architecture Decision / Binding Format

`09-架构设计与关键决策.md` 将已确认的业务语义、状态、接口和权限绑定到项目内部逻辑架构、边界和切换策略中。

09 启动前必须读取并引用：

```text
PROJECT-CURRENT-BASELINE.md
```

09 必须明确区分：

- 当前生产中真实生效的模块、入口、调用链。
- 已开发但未发布的模块。
- 仓库中存在但已废弃的模块。
- 仅用于历史追溯的模块。
- 本期允许复用的技术基础。
- 本期禁止复用的旧业务语义。

ARCH 决策记录最小格式：

```markdown
### ARCH-XXX：<架构决策名称>

关联 FLOW：
关联 MODULE：
关联 STATE / EVENT：
关联 API：
关联 PERM：
关联 CAP：

架构当前基线：

目标逻辑架构：

逻辑承接位置：

实现承接策略：
- extend_existing_domain / reuse_shared_capability / create_stable_business_domain

稳定业务概念：

优先承接的现有逻辑域：

新建长期业务域的必要性：
- 不适用时明确写不适用

禁止的临时命名：
- 期次、Sprint、阶段、版本或 Planning ID 命名

执行前架构核实要求：

允许复用的技术基础：

禁止复用的旧语义：

旧流程切断位置：

数据域、部署与发布架构边界：

切换策略：

回退策略：

对 10 / 11 / 13 的输入：

架构风险移交项：
```

09 必须包含：

```markdown
## Canonical Contract—Architecture Binding

| FLOW | MODULE | STATE / EVENT | Canonical API | 目标逻辑承接层 | 可复用技术基础 | 禁止复用旧语义 | 旧流程切断位置 | 关联 CAP | 下游 TASK |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

规则：

- 每条 P0 FLOW 最终必须有逻辑层承接。
- 每个 Canonical API Contract 必须有 Architecture Binding。
- 可复用技术基础必须写清楚“复用什么”。
- 禁止复用旧语义必须写清楚“绝不复用什么”。
- 实现承接策略只允许 `extend_existing_domain`、`reuse_shared_capability`、`create_stable_business_domain`。
- 默认优先核实并扩展已有稳定业务域，或复用共享能力。
- `create_stable_business_domain` 必须说明现有域无法承接的原因、长期业务概念、职责边界、跨期独立意义和非临时命名依据。
- 稳定业务概念必须来自目标项目真实存在且可跨期复用的业务对象、业务任务、处理记录或证据资产，不得使用期次、阶段或版本表达。
- 09 不定义具体目录、类名、表名、ORM Model 或迁移名称；这些必须在执行前基于真实代码架构核实。
- 不得使用“按实现时决定”“视情况复用”“后续再看”。

09 必须包含：

```markdown
## Legacy Semantic Firewall

| 旧模块 / 旧对象 / 旧状态 | 是否可读取 | 是否可写入 | 是否可进入新 Command | 是否可影响新 State | 是否可影响 Decision View | 是否可作为生效来源 | 处理策略 |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

处理策略只允许：

```text
inherit
adapt
create
deprecate
block
readonly
cleanup
```

规则：

- 旧审批、旧申请、旧入口、旧状态不得通过“技术复用”重新进入新流程。
- 旧对象若允许历史读取，只允许 `readonly`。
- 历史只读旧对象不得成为新流程前置、状态来源、下一步动作来源或生效来源。
- 09 只定义内部是否需要某类能力端口、依赖方向和隔离边界。
- 具体外部 Provider、SDK、版本或鉴权方式由 10 决定。
- 外部能力未完成 10 选型确认时，09 只能定义 `CAPABILITY PORT`、`ARCHITECTURE REQUIREMENT`、`ADAPTER BOUNDARY`，不得把具体 Provider 绑定标记为 `confirmed`。
- 架构风险只移交 12；09 不创建正式 `RISK-ID`、风险等级或风险闭环。

## 4.15 Capability Decision Card

`10-外部能力选型与接入决策.md` 是外部能力的选型与接入决策合同。若项目保留旧文件路径 `10-外部能力与集成治理.md`，正文标题和职责必须使用“外部能力选型与接入决策”。

文档确认状态与能力就绪状态必须分开：

```text
文档确认状态：
草案 / 已确认

CAP 选型状态：
identified
candidate
confirmed
rejected
superseded
deprecated

CAP 真实就绪状态：
not_ready
official_sot_verified
preconditions_ready
real_environment_verified
release_ready
blocked
```

规则：

- 10 已确认不等于能力已接入。
- 10 已确认不等于能力已真实验证。
- 10 已确认不等于能力可上线。
- 未完成 Capability Development-Entry Evidence Gate 的 CAP，不得进入相关开发任务。
- planning 阶段允许写入 `identified`、`candidate`、`confirmed`、`official_sot_verified`、`preconditions_ready`、`blocked`。
- planning 阶段禁止写入 `real_environment_verified` 或 `release_ready`。
- Adapter、真实调用、代码证据、真实设备和真实环境验证只属于后续执行 / 测试 / 验收要求。
- 页面可打开、JSSDK ready、Mock 成功、代码存在，均不得视为真实能力成功。

能力格式：

```markdown
### CAP-XXX：<能力名称>

关联 FLOW：
关联 MODULE：
关联 SCN：
关联 ARCH：

业务需要：

能力边界：
- 必须支持：
- 明确不支持：

候选方案：
- Candidate A：
- Candidate B：

当前选型：
- 状态：
- 选择结果：

选择理由：

官方事实：
- 官方来源：
- SDK / API / Provider 版本：
- 官方更新时间或访问日期：

适用端与运行前提：
- 运行环境：
- 鉴权：
- 权限 / Scope：
- 网络：
- 额度 / 限流：
- 计费：
- 合规：

能力失败影响：
- 影响 FLOW：
- 影响范围：
- 上游业务处理引用：

Capability Development-Entry Evidence Gate：

Capability Realization Requirement：

Capability Acceptance Requirement：

关联 TEST：
关联 RISK：
关联下游 TASK：
```

边界：

- 10 可以定义能力失败类型、技术前提、真实可用验证要求，以及能力失败影响哪个 FLOW 或 SCN。
- 10 不得自行决定用户进入哪个页面、用户补什么资料、用户是否完成业务闭环、谁代替谁提交业务动作或某个业务状态是否迁移。
- `source`、容器来源、JSSDK ready、页面打开、Mock 返回、历史代码存在，不得成为身份、资格、权限、业务状态或真实能力成功依据。
- 10 不定义 Adapter 代码、SDK 调用代码、接口字段映射、具体实现文件、开发任务、实际接入结果或最终验收结果。

## 4.16 Test Design Format

`11-测试设计与验收用例.md` 以 01 的 FLOW 为主线，将业务、状态、接口、权限、旧流程隔离、外部能力和 UI/UX 结论转化为可执行、可自动化、可验收的测试设计合同。

测试类型：

```text
business_flow
state_transition
api_contract
permission_scope
legacy_boundary
capability_real_environment
ui_behavior
ux_interaction
visual_review
regression
release_gate
```

自动化等级：

```text
mandatory_automated
automated_preferred
manual_or_real_environment_required
```

单条测试设计格式：

```markdown
### TEST-XXX：<测试名称>

测试类型：

关联 REQ：
关联 FLOW：
关联 SCN：
关联 DOMAIN：
关联 STATE：
关联 API：
关联 PERM：
关联 CAP：
关联 PAGE / UI-MOD / UX-SCN：
关联 Prompt / UI Contract / ASSET revision：

测试目标：

业务前置：
- 身份 / 会话：
- 组织 / 租户：
- 角色与资格：
- 项目 / 区域范围：
- 任务与业务事实：
- 数据域：

逻辑测试步骤：
1.
2.
3.

预期业务结果：

预期状态结果：

预期接口结果：

预期用户可见结果：

前端合同断言（UI/UX 适用）：
- 结构与组件层级：
- 响应式与内容边界：
- default / loading / empty / error / success / blocked 状态：
- trigger / pending / success / failure / retry / cancel / back：
- 键盘、焦点、可访问名称与非颜色提示：
- 视觉对照 ASSET-ID@revision：

反向 / 禁止路径：

自动化等级：
- mandatory_automated
- automated_preferred
- manual_or_real_environment_required

真实环境要求：

预期证据要求：

关联 RISK：
```

11 必须包含：

```markdown
## FLOW—测试覆盖矩阵

| FLOW | 正向流程 | 状态测试 | API 测试 | 权限测试 | 旧流程测试 | CAP 测试 | UI/UX 测试 | 自动化等级 | 最终验收来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

业务测试顺序必须继承 01 的 FLOW：

```text
身份 / 会话 / 访问上下文
-> 进入工作台或业务入口
-> 核心业务动作
-> 异常与恢复
-> 当前周期闭环
-> 后续周期动作
-> 旧流程和历史对象隔离
-> 外部能力与发布门禁
```

每条 P0 FLOW 至少必须覆盖：

- 正向业务流程。
- 状态与前置阻断。
- API 合同。
- 权限与范围。
- 旧流程隔离。
- 回归测试。

涉及外部能力时，增加：

- `capability_real_environment`

涉及页面和 UX 时，增加：

- `ui_behavior`
- `ux_interaction`
- `visual_review`

默认必须标记为 `mandatory_automated`：

- 状态迁移。
- 业务前置阻断。
- API 合同。
- 输入非法。
- 权限与范围。
- 幂等。
- 并发冲突。
- 旧流程隔离。
- 历史只读边界。
- 测试与生产数据域隔离。

允许标记为 `manual_or_real_environment_required`：

- 真实设备定位、相机、麦克风或其他平台容器能力。
- 视觉一致性与信息层级。
- 复杂 UX 使用体验。
- 真实网络、权限、配额、限流和 Provider 行为。

规则：

- 每一条 P0 FLOW 必须有完整测试覆盖。
- 若某个 FLOW 的关键测试缺失，11 不得确认。
- 若某项测试无法自动化，必须明确原因、真实环境要求和最终验收方式。
- 自动化测试通过不等于真实环境能力已验收。
- 视觉评审通过不等于接口、权限、状态与旧流程隔离已证明。
- UI/UX TEST 必须引用 05 中精确的 PAGE/UI-MOD/UX-SCN/ASSET revision；不得只写“与设计一致”或依赖聊天截图。
- 能自动化的结构、状态、响应式和交互行为必须标记相应自动化等级；纯视觉差异、真机布局或复杂体验确实不能自动化时，必须写清人工观察步骤、视口/设备、对照 revision 和通过条件。
- 11 不记录测试命令、测试代码、fixture 脚本、执行调度、重试命令、实际执行状态或实际测试结果。

## 4.17 Risk / Task / Execution / Acceptance Framework Format

### 12 RISK / DEP / OPEN Format

`12-风险、依赖与待决策事项.md` 是正式 RISK / DEP / OPEN 的唯一 SoT。若项目保留旧路径 `12-风险、依赖与待确认项.md`，正文标题和职责必须使用“风险、依赖与待决策事项”。

01–11 只能输出：

- 风险信号。
- 风险移交项。
- 阻断提示。
- 待确认问题。

12 必须归并信号，并为每个独立风险生成唯一正式 `RISK-ID`。同一外部能力未验证问题、同一旧流程重新进入新主流程问题，不得在多个文档中拥有多个正式 `RISK-ID`。

类型定义：

| 类型 | 定义 | 是否允许进入 13 |
| --- | --- | --- |
| `RISK` | 某个不确定条件可能造成业务、数据、安全、交付或上线损害 | 可以，但必须有治理策略 |
| `DEP` | 某任务或目标成立前必须满足的外部、环境、顺序、事实或跨团队前提 | 可以，但必须明确阻断范围 |
| `OPEN` | 尚未拍板，且会影响业务语义、交互路径、架构边界、能力选型或验收标准的问题 | 不可以直接进入任务 |

RISK 格式：

```markdown
### RISK-XXX

风险类别：
风险等级：
Priority：

来源信号：
关联 FLOW：
关联 DOMAIN / STATE / API / PERM / ARCH / CAP / TEST：

风险描述：

触发条件：

影响范围：

阻断阶段：
- planning_confirmation
- task_generation
- execution_start
- acceptance
- release
- baseline_update

处理策略：
- avoid
- mitigate
- transfer
- accept_deferred

关联 DEP：
关联 OPEN：
关联 TASK：
关联 TEST：

关闭条件：

关闭证据类型：

风险状态：
- identified
- planned
- mitigating
- verification_pending
- closed
- accepted_deferred
- reopened
```

DEP 格式：

```markdown
### DEP-XXX

依赖对象：

依赖类型：
- external_provider
- external_decision
- project_baseline
- environment
- sequencing
- cross_team
- release

必须满足的事实：

阻断范围：

验证来源：

最晚解除阶段：

关联 RISK：

状态：
- unknown
- pending
- verified
- unavailable
- superseded
```

OPEN 格式：

```markdown
### OPEN-XXX

待决问题：

为什么不能默认：

影响的 SoT：

候选方案：

推荐方案：

需要确认的主体：

最晚确认阶段：

未确认时阻断什么：

确认后回写目标：

状态：
- open
- awaiting_user
- confirmed
- rejected
- superseded
```

规则：

- 已确认且已有正式 SoT 承接的业务规则，不得再次作为 RISK 或 OPEN 进入 12。
- 关键 OPEN 未关闭，不得生成对应 TASK。
- OPEN 的关闭必须先回写真正拥有该事实的上游 SoT；上游结论确认后，12 才能记录 resolved / confirmed 及其来源。
- 12 不重复定义已确认业务规则、状态、接口、权限或 UI 事实。

### Implementation Contract Parameter Status

实现所需参数按任务实际内容动态检查，每项只允许：

```text
confirmed
explicitly_delegated
blocking_open
not_applicable
```

- `confirmed`：用户、已确认 SoT、官方事实或项目稳定规范已有明确值。
- `explicitly_delegated`：只适用于不会改变业务流程、用户权利、数据含义、权限、状态、用户体验或验收结果的技术参数；必须写明执行层决策范围、项目既有规范、允许边界、验证方式和不得影响的业务结果。
- `blocking_open`：缺失值会改变 API、数据结构、页面交互、权限、状态、业务结果、测试、验收或发布判断；必须由 12 保留 OPEN 并阻断对应 TASK Ready。
- `not_applicable`：当前任务不涉及。

禁止为了格式完整询问无关参数，也禁止用行业默认值或 AI 猜测填充文件大小、数量、次数、超时或重试等业务边界。

按任务实际内容检查：

- 表单和普通输入：必填性、合法值、默认值、长度、最小/最大值、数量、单位、精度、重复、修改、删除和空值处理。
- 文件和图片：文件类型/MIME、单文件与总大小、最大数量、是否必传、失败是否阻断提交、用户重试、业务要求中的重试次数、替换/删除、业务对象绑定、修改后旧文件处理和跨租户/跨任务访问边界。
- 时间和日期：时区、日切、截止时间、操作窗口、跨天、过期处理和时间事实来源。
- 列表和查询：默认排序、核心筛选、可见范围、空结果、分页及会影响业务或验收的分页边界。
- 外部能力：失败是否阻断、用户可见结果、降级、降级后保留能力、真实环境验证，以及属于业务要求的超时/重试/次数边界。

适用时至少覆盖以下验收样例：

- 合同文档：允许格式、最大大小、上传失败行为。
- 作为业务必需证据的检查图片：是否必传、允许格式、单张大小、最大数量、失败时能否提交、重试/恢复、替换和删除规则。

纯技术参数如数据库连接池大小、内部缓存容量或 SDK 内部算法允许 `explicitly_delegated`，但必须满足已确认的业务结果与验证边界。

参数事实的文档归属以 `03-planning-doc-responsibility.md#实现合同参数的文档归属` 为唯一来源。13 只汇总 Task Ready 所需参数是否闭合，不重复定义上游事实；下游发现缺失时必须回写真正拥有该事实的上游 SoT。

### 13 Task Contract Format

`13-开发任务合同与落地清单.md` 将已确认、可执行、可验证的规划结论整理为任务合同、依赖关系、并行边界、完成证明要求与后续执行记录框架的输入。若项目保留旧路径 `13-开发任务拆分与落地清单.md`，正文标题和职责必须使用“开发任务合同与落地清单”。

13 只能接收：

- 已确认 FLOW / DOMAIN / SCN / MODULE / PAGE。
- 已确认 STATE / API / PERM。
- 已确认 ARCH / CAP。
- 已定义 TEST。
- 已定义 RISK / DEP。
- 已关闭或不影响本任务的 OPEN。

13 输入闭包：

- 只要本期需要生成 13 TASK，就必须同时具备 11 测试设计与验收用例、12 风险/依赖/待决策事项，以及所有被 TASK 引用且已确认的上游 SoT。
- TASK 不得引用不存在、未装配或未确认的 FLOW / STATE / API / PERM / ARCH / CAP / TEST 结论。
- 15 不得作为可独立装配的孤立文档；只能由已确认的 13 连同 14 一起自动派生。

禁止：

- 关键 OPEN 未关闭时生成 TASK。
- 能力选型未确认时生成 `capability_integration` TASK。
- 接口合同未确认时生成接口实现 TASK。
- 旧流程处理方式未确认时生成 `legacy_cutover` TASK。

TASK 格式：

```markdown
### TASK-XXX：<任务名称>

task_revision:
  contract_revision:
  introduced_in_revision:
  contract_status:
  relation_to_previous:
  previous_task_id:
  previous_contract_revision:
  execution_disposition:

任务类型：
- implementation
- legacy_cutover
- capability_integration
- test_enablement
- release_readiness_automation
- verification_handoff

Priority：

承接业务目标：
- FLOW：
- SCN：
- MODULE：

执行输入：
- DOMAIN：
- STATE / EVENT：
- API：
- PERM：
- ARCH：
- CAP：
- TEST：
- RISK：
- DEP：

任务目标：

实现命名与承接边界：

- Planning ID 用途：
  - trace_only
- 稳定业务概念：
- 预期实现承接策略：
  - extend_existing_domain / reuse_shared_capability / create_stable_business_domain
- 优先核实的现有业务域：
- 禁止使用的实现命名：
  - 期次编号
  - TASK / FLOW / DOMAIN / API / PERM 等 Planning ID
  - Sprint、阶段或临时版本名称
- 新建物理模块允许条件：
- 执行前架构核实：

允许复用的技术基础：

禁止复用的旧语义：

逻辑影响面：
- backend:
- frontend:
- platform:
- operations:

候选影响文件：
- 路径：
- 可信度：
- 是否必须在执行前核实：

任务前置：
- 已确认 SoT：
- 已解除 DEP：
- 不允许存在的 OPEN：
- 上游 TASK：

并行边界：
- 可并行：
- 不可并行：
- 共享资源：

Task Ready Gate：

实现合同完整性：
- 会影响业务、接口、数据、状态、权限、页面或验收的参数是否完整：
- 已确认参数：
- 明确委托执行层的技术参数：
- 委托边界：
- 阻断 OPEN：
- 是否允许进入开发：

完成合同：
- 应实现的能力：
- 应保持的禁止关系：
- 必须覆盖的 TEST：
- 应进入 14 的预期验证项：
- 发现偏差时的回写目标：

前端体验绑定（UI TASK 适用）：

frontend_contract_binding:
  design_document_path:
  design_manifest_ref:
  baseline_source:
  reference_pages: []
  prompt_refs: []
  page_contract_refs: []
  module_contract_refs: []
  interaction_contract_refs: []
  confirmed_asset_refs: []
  consistency_test_refs: []
  allowed_extensions: []
  prohibited_redefinitions: []
```

`contract_status` 只允许 `active`、`completed`、`superseded`、`cancelled`；`relation_to_previous` 只允许 `new`、`unchanged`、`extends`、`replaces`、`supersedes`；`execution_disposition` 只允许 `execute`、`resume`、`reexecute_affected_part`、`context_only`、`completed_locked`、`cancelled`。

增量规则：

- 新增 TASK：`active + new + execute`。
- 未受影响且尚未完成：`active + unchanged + execute`；未开始者进入 `carried_forward_pending_tasks`，正在执行者由 Handoff `resume_only` 承接。
- 未受影响且已完成：`completed + unchanged + completed_locked`。
- 原能力局部扩展时，新建 `active + extends + execute` 的增量 TASK，并以 `previous_task_id` 指向原 TASK；原 TASK 保持历史状态，不重置。
- 原合同错误时，旧 TASK 使用 `contract_status: superseded` 与 `execution_disposition: cancelled`；新 TASK 使用 `active + replaces + execute` 或 `active + supersedes + execute` 并指向旧 TASK。不得使用 `relation_to_previous: superseded` 表示旧 TASK 状态。
- 已取消 TASK 使用 `cancelled + cancelled`；旧 EXEC 和实际事实仍保留。
- `previous_contract_revision` 在 `relation_to_previous: new` 时为空；同一 TASK ID 修订合同时必须指向该 TASK 的上一 `contract_revision`。此时只扩充尚未完成范围使用 `extends`，事实核实后继续未受影响部分用 `resume`，已完成部分失效时用 `reexecute_affected_part`；不得用 `unchanged` 掩盖受影响修订。
- 新 TASK 指向其他 TASK 时，`previous_task_id` 填被关联 TASK，`previous_contract_revision` 填其被关联合同 revision；同一 TASK 修订时 `previous_task_id` 填自身 TASK-ID。两者不得悬空或指向不存在的合同。
- 正在执行的 TASK 必须区分已完成、保留、取消和受影响部分，只允许 `resume` 或 `reexecute_affected_part`，且只能进入一个 Handoff 队列。

Task Ready Gate 必须明确：

- 上游 SoT 已确认。
- 不存在阻断本任务的 OPEN。
- 必要 DEP 已验证，或阻断机制已明确。
- 必要 CAP 已完成开发前门禁。
- 上游 TASK 已满足，或并行边界已明确。
- Implementation Naming Gate 已通过。
- 每个 P0 TASK 已关联稳定业务概念、实现承接策略和优先核实的现有业务域。
- Implementation Contract Completeness Gate 已通过。
- 会影响业务合同、用户体验、接口语义、数据、状态、权限或验收结果的参数均为 `confirmed` 或 `not_applicable`。
- 纯技术参数若为 `explicitly_delegated`，已写明决策范围、既有规范、允许边界、验证方式和不可影响的业务结果。
- 不存在阻断本任务的 `blocking_open`。
- UI TASK 的 05、Design Manifest、Prompt、PAGE/UI-MOD、UX-SCN、ASSET 和 TEST 精确引用均可解析，且与 Handoff `frontend_experience_binding` 的路径、ID、revision 一致。
- UI TASK 所需设计资产均为 Handoff 指定的 `visual_confirmed` revision；不得使用未确认或目录中自动发现的更新版本。
- `scripts/validate_ui_ux_contract.py` 已通过，或脚本不可用时已经完成并记录同等结构与引用校验。

Task Completion Contract 必须明确：

- 应实现的目标能力。
- 应保持的禁止关系。
- 必须具备执行条件的 TEST。
- 必须预留的验证与交接信息。
- 发现规划偏差时的回写目标。

规则：

- 候选文件路径不等于已确认实现事实。
- 规划阶段只确认逻辑影响面。
- 文件、目录、代码位置和具体实现方式只能作为候选影响面，必须在后续执行前核实。
- 带有期次或版本标识的 TASK-ID 只用于追踪，不得推导实现名称。
- 13 不生成具体表名、类名、模块目录、权限点、API 物理命名空间或迁移名称。
- 若 09 未确认 `create_stable_business_domain`，13 不得暗示需要创建新物理模块。
- “独立数据域”不得作为创建任何期次、阶段或版本物理命名空间的依据。
- 执行前若发现必须新建长期业务模块而 09 无对应决策，必须作为架构偏差回写 Planning。
- 任一 `blocking_open` 未关闭时，对应 TASK 不得 Ready；P0 主流程存在 `blocking_open` 时不得完成正式 Handoff。
- `explicitly_delegated` 不得只写“实现时决定”。
- 不得在 TASK 中使用“按实现时决定”“可选 A / B / C”“视情况复用”“后续再看”。
- Task Completion 不等于最终验收、真实环境能力通过、已发布或 PROJECT-CURRENT-BASELINE 已更新。
- UI TASK 的 Task Completion Contract 必须要求实现结构、响应式、状态、交互、可访问性和视觉资产一致性验证；合同或确认资产与现有代码冲突时，回写 `design_drift` 或 `planning_gap`，不得由执行层自行重设计。

13 必须显式识别并写明：

- 共享 STATE。
- 共享 API Contract。
- 共享权限边界。
- 共享路由入口。
- 共享旧流程切断点。
- 共享数据域。
- 共享发布配置。
- 哪些 TASK 可并行。
- 哪些 TASK 必须串行。
- 哪些 TASK 完成前下游不可开始。
- 哪些 TASK 完成前其他 TASK 不得声明完成。

13 确认规则：

- Task Contract Gate 只校验 13 自身及其上游 01–12。
- 14、15 的预先存在不得作为 13 确认前置。
- 13 被用户确认并回写 `状态: 已确认` 后，才触发 14、15 框架派生。
- 首次确认同时在 13 中冻结 `planning_execution_baseline`；后续完整 13 是当前有效合同目录与历史快照承载，不等于全部待执行队列，实际执行范围以 Handoff 的增量执行合同为准。

### 13 to 14 / 15 Framework Derivation Rule

唯一顺序：

```text
初始批次已生成 13 草案
-> 13 引用的 01–12 均已依次确认
-> 轮到 13 confirmation queue 项
-> 存在 UI TASK 时运行 UI/UX Execution Readiness Gate
-> Task Contract Gate
-> Implementation Naming Gate
-> Implementation Contract Completeness Gate
-> 输出 13 人话总结
-> 用户确认 13
-> 回写 13：已确认
-> 冻结 Planning Execution Baseline
-> 自动触发 14、15 框架派生
-> 自动生成 14 与 15 的正式框架
-> 对 14、15 运行 Execution and Acceptance Framework Derivation Gate
-> 汇总实际已生成的 assembled_documents
-> 基于实际路径生成 handoff_role_mapping
-> 准备 execution_ready Handoff
```

14、15 是从已确认 13 自动派生的框架对：

- 三个 13 Gate 必须发生在用户确认 13 前；Gate 未通过时不得要求用户确认 13。
- Gate 失败时必须修正 09、13 或对应上游 SoT；不得先让用户确认 13，再补做 Gate。
- 本顺序只适用于实际装配 13、即 `requires_execution_handoff: true` 的 Planning。

- 不触发“每次只能生成一份正式文档”的限制。
- 不进入初始草案批次或独立确认队列。
- 不需要把 14、15 的独立用户确认作为 Planning 完成前提。
- 自动生成后只向用户输出简洁说明：已生成执行记录框架与验收框架，当前只预置待填事实位置，不代表开发完成、测试通过、可发布或已发布。
- 框架状态必须和实际事实状态分离。
- 14、15 自动派生后不得写入 `文档状态：已确认`。
- 已有冻结基线时，派生只处理 active Change Set 的新增或受影响 TASK / TEST / 空白占位；不得全量重建 14/15。

### 14 Execution Record Framework Format

`14-开发执行与联调变更记录.md` 是后续执行事实的承载框架。planning skill 在 13 被确认后必须自动创建 14 的正式框架，但不得填写任何实际发生的事实。

固定结构：

```text
1. 文档边界
2. 执行基线
3. TASK 执行状态矩阵
4. 预期执行合同
5. 实际执行记录区
6. 自动化验证索引区
7. 偏差、阻断与回写请求区
8. 外部能力、环境与真实验证待补项
9. 测试交接区
```

执行基线必须引用：Planning Execution Baseline revision、TASK contract revision、active Change Set 和当前允许执行范围。

文档必须包含：

```text
框架生成状态：generated
框架完整性：complete
用户独立确认：not_required
实际事实状态：not_started
```

解释必须写入：

```text
框架生成状态：generated
框架完整性：complete
用户独立确认：not_required
实际事实状态：not_started
= 执行框架和预期合同已经由已确认 13 自动派生且预置完整

不代表
= 实际开发已经开始或完成
```

首次派生为本期允许执行的每个 TASK 预置；增量派生只为新增、替代或受影响 TASK 追加：

```markdown
### EXEC-<TASK-ID>

关联 TASK：
关联 FLOW：
关联 STATE / API / PERM / ARCH / CAP / TEST：

执行基线：
- 任务版本：
- Planning Execution Baseline revision：
- TASK contract revision：
- active Change Set：
- 当前允许执行范围：
- 上游 SoT：

预期实现目标：

预期验证范围：

实际改动：
- 待填写

实际结果：
- not_started

验证覆盖：
- 待填写

联调等级：
- 待填写

与计划差异：
- 待填写

回写要求：
- 待填写

交接：
- 待填写
```

不得把“待填写”替换成推测性的实际结果。
所有 EXEC、TEST、CAP、发布与基线事实初始只能是 `not_started` 或空白待填；不得因框架生成而使用“通过、失败、已验收、可发布、已发布、生产已更新、基线已更新”等状态。

追加式规则：

- 新增 TASK 只追加新的 EXEC；局部扩展保留旧 EXEC 并追加增量 EXEC；替代 TASK 保留旧 EXEC 并追加 replacement EXEC。
- 未受影响 TASK 不修改、不重建、不重置状态。
- 已填写的实际执行、验证、联调和偏差事实不得删除、覆盖、回退为 `not_started` 或绑定到不同 task revision。
- Planning Recovery 只能重建受影响且尚未填写真实事实的预置框架。

### 15 Acceptance and Retrospective Framework Format

`15-验收结果与复盘.md` 是后续验收、真实环境验证、发布判定与复盘事实的承载框架。planning skill 在 13 被确认后必须自动创建 15 的正式框架，但不得填写任何实际验收或发布结论。

固定结构：

```text
1. 文档边界
2. 验收基线
3. FLOW 验收矩阵
4. TEST 实际结果区
5. CAP 真实环境验证区
6. RISK / DEP 关闭判定区
7. P0 / P1 / P2 发布门禁区
8. 发布判定与发布事实区
9. PROJECT-CURRENT-BASELINE 更新条件与结果区
10. 复盘
11. 下一期输入（只引用 Requirement Pool）
```

文档必须包含：

```text
框架生成状态：generated
框架完整性：complete
用户独立确认：not_required
实际事实状态：not_started
```

解释必须写入：

```text
框架生成状态：generated
框架完整性：complete
用户独立确认：not_required
实际事实状态：not_started
= 验收框架与预期验收对象已经由已确认 13 自动派生且预置完整

不代表
= 本期已经验收、发布或完成基线更新
```

FLOW 验收矩阵：

```markdown
| FLOW | 关联 TEST | 自动化证据 | 人工 / 真实环境证据 | RISK 关闭条件 | 验收状态 | 发布影响 |
| --- | --- | --- | --- | --- | --- | --- |
```

planning skill 只允许预填：

- FLOW。
- 关联 TEST。
- 预期证据类型。
- 风险关闭条件。
- 发布影响。
- 验收状态初始值。

禁止预填：

- 通过。
- 失败。
- 已验收。
- 真实环境已通过。
- 可发布。
- 已发布。
- 生产已更新。
- PROJECT-CURRENT-BASELINE 已更新。

规则：

- 15 不得独立装配或提前生成。
- 15 只能在 13 已确认后与 14 一起自动派生。
- 15 初始验收状态只能是 `not_started` 或空白待填。
- 15 不得因框架生成写入通过、失败、已验收、真实环境已通过、可发布、已发布、生产已更新或 PROJECT-CURRENT-BASELINE 已更新。
- 已有实际 TEST、CAP、验收、发布或基线更新事实时不得覆盖、删除或回退；Change Set 只允许追加受影响验收项或修订尚未填写的占位。
- 实际发布确认后，15 才记录 PROJECT-CURRENT-BASELINE 更新结果；Planning 框架生成不能执行该更新。
- 下一期输入只允许列出 `<requirement_pool_path>#POOL-ID` 和一句引用目的；需求正文、延期状态和消费状态只在 Requirement Pool 维护。

### 12/13/14/15 State Separation Rule

必须始终区分：

```text
框架已生成且完整
≠ 实际开发完成
≠ 自动化验证通过
≠ 真实环境通过
≠ 最终验收通过
≠ 已发布
≠ 项目当前基线已更新
```

## 5. 引用规范

关键结论必须使用显式引用。

```markdown
## 关联需求

- REQ-USER-001
- REQ-ORDER-002

## 上游依赖

- 02-业务域模型.md#DOMAIN-USER-001

## 下游影响

- 07-接口设计与前后端契约.md#API-ORDER-001

## SoT来源

- 01-需求范围与验收标准.md#REQ-ORDER-001
```

规则：

- 所有关键结论必须可追踪
- 禁止隐式依赖
- 禁止自然语言模糊引用

## 6. 状态机格式规范

```markdown
## 状态定义

状态：STATE-ORDER-REVIEWING
状态值：REVIEWING

允许来源：
- CREATED

允许去向：
- APPROVED
- REJECTED

非法迁移：
- ARCHIVED -> REVIEWING

回滚规则：
- APPROVED 可回滚至 REVIEWING
```

规则：

- 所有状态必须显式定义
- 所有迁移必须可验证
- 禁止隐式状态流

## 7. 风险等级规范

风险等级：

```text
LOW
MEDIUM
HIGH
BLOCKER
```

说明：

- 正式 `RISK-ID` 只能由 12 创建。
- 12 的正式 RISK / DEP / OPEN 格式见 `## 4.17 Risk / Task / Execution / Acceptance Framework Format`。
- 下列格式仅用于非正式风险信号或历史兼容读取，不得替代 12 的正式格式。

风险信号格式：

```markdown
风险ID：
风险等级：
影响范围：
触发条件：
应对策略：
确认状态：
```

规则：

- 风险必须带等级
- 风险必须带影响范围
- 风险必须带触发条件

## 8. 下游验证结果引用规范

本规范只用于 14/15 等下游执行/验收文档引用结果结构。
planning-layer-runtime 不生成、填写或推断执行结果。

```markdown
验证项：
验证来源：
预期结果：
实际结果：
验证状态：
证据：
```

规则：

- 验收必须结构化
- 禁止仅写“已完成”
- 禁止无证据验收

## 9. 流程格式

使用：

```text
步骤A
-> 步骤B
-> 步骤C
```

## 10. 接口格式

使用：

```http
GET /api/example
```

## 11. JSON 格式

使用：

```json
{
  "success": true
}
```

## 12. 命令格式

使用：

```powershell
<project-test-command>
```

## 13. 企业级 SaaS 固定检查项

仅补充字段，不写实现方案。

### 02-业务域模型.md

```markdown
## 业务域权限关系

业务域：
角色：
权限：
数据可见范围：
越权策略：
```

检查：

- RBAC扩展
- ABAC扩展
- 多租户扩展
- 权限与业务域绑定
- 角色与权限动态绑定
- 禁止数据库实现、代码逻辑、前端行为

### 05-前端页面与UI/UX交互设计.md

```markdown
## 交互合同确认

关联 SCN：
关联 MODULE：
PAGE / UI-MOD / UX-SCN：
合法进入条件：
主操作：
禁用或隐藏操作：
异常恢复：
旧入口处理：

## UI/UX 执行交付清单

design_delivery_manifest：

## 可复制设计提示词

PROMPT-ID@revision：
target_tool / output_spec / negative_constraints：
prompt_body：

## 页面实现合同

PAGE / UI-MOD@revision：
design token / layout / responsive / component / state / content / accessibility / motion / acceptance：

## UX 交互合同

UX-SCN@revision：
From state / Trigger / Pending / Success / Failure / Retry / Cancel / Back / Forbidden / Evidence：

## 设计资产索引

ASSET@revision：
PROMPT：
资产状态：
真实路径或引用：
用户确认引用：

## 覆盖矩阵

FLOW—SCN—MODULE—PAGE—合同—资产—TEST 覆盖矩阵
```

检查：

- UI进入SoT链路
- 交互合同与视觉资产分开确认
- 设计提示词和资产索引可追踪
- UI TASK 的 Prompt、PAGE/UI-MOD、UX-SCN、ASSET 和 TEST 具备精确 revision 绑定
- Prompt 有可直接复制的完整 `prompt_body`，页面和 UX 有可执行合同
- 用户未提供图时，资产只能是 `planned` 或 `prompt_ready`
- 05 内容与资产闭合时 Manifest 可为 `design_ready`；只有提升为 `execution_ready`、所需资产 `visual_confirmed` 且执行级结构/引用校验通过时 UI TASK 才可 Ready
- 不得把设计资产状态写成已开发、已测试、已验收或已上线

### 06-数据模型与状态流转.md

```markdown
## 业务事实与状态合法性

核心业务数据事实：

业务事件：

状态分类：

状态唯一来源：

迁移守卫：

旧对象 / 旧状态隔离映射：

数据域治理边界：

下游 API / PERM / TEST 映射：
```

检查：

- 状态分类清晰
- 状态唯一来源可追踪
- 迁移守卫完整
- 旧状态隔离明确
- 数据域边界明确
- 禁止生成表名、字段类型、索引、外键、SQL、ORM Schema 或迁移脚本

### 08-权限、数据可见性与异常处置边界说明.md

```markdown
## 访问决策与拒绝边界

PERM-ID：
动作：
资源：
允许主体：
允许范围：
业务资格：
业务状态前置：
数据域前置：
拒绝类型：
拒绝原因码：
工作人员协助边界：
旧流程禁止来源：
```

检查：

- 测试数据也是权限
- 权限决策可追踪
- 数据范围结构化
- 拒绝类型不得混写
- 后端必须执行 PERM 决策
- 历史对象只读边界明确

### 09-架构设计与关键决策.md

```markdown
## Canonical Contract—Architecture Binding

| FLOW | MODULE | STATE / EVENT | Canonical API | 目标逻辑承接层 | 可复用技术基础 | 禁止复用旧语义 | 旧流程切断位置 | 关联 CAP | 下游 TASK |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Legacy Semantic Firewall

| 旧模块 / 旧对象 / 旧状态 | 是否可读取 | 是否可写入 | 是否可进入新 Command | 是否可影响新 State | 是否可影响 Decision View | 是否可作为生效来源 | 处理策略 |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

检查：

- 必须读取并引用 PROJECT-CURRENT-BASELINE。
- 每条 P0 FLOW 都有逻辑架构承接位置。
- 每个 Canonical API Contract 都有 Architecture Binding。
- 允许复用的技术基础与禁止复用的旧业务语义必须分开写。
- 旧审批、旧入口、旧状态无法进入新 Command、新 State 或新 Decision View。
- 外部能力未完成 10 选型时，只能定义能力端口和边界，不得确认具体 Provider。
- 09 只移交架构风险给 12，不重复定义正式 RISK。

### 10-外部能力选型与接入决策.md

旧文件路径可继续使用 `10-外部能力与集成治理.md`，但正文标题和职责必须使用“外部能力选型与接入决策”。

```markdown
### CAP-XXX：<能力名称>

关联 FLOW：
关联 MODULE：
关联 SCN：
关联 ARCH：
业务需要：
能力边界：
候选方案：
当前选型：
选择理由：
官方事实：
适用端与运行前提：
能力失败影响：
Capability Development-Entry Evidence Gate：
Capability Realization Requirement：
Capability Acceptance Requirement：
关联 TEST：
关联 RISK：
关联下游 TASK：
```

检查：

- CAP-ID 全局唯一
- CAP 选型状态与 CAP 真实就绪状态分开
- 官方 SoT 可追踪
- SDK/API/OpenAPI/MCP 版本明确
- 鉴权方式明确
- 权限、Scope、网络、额度、限流、计费、合规和目标端兼容性明确
- Capability Development-Entry Evidence Gate、Capability Realization Requirement 和 Capability Acceptance Requirement 明确
- 能力失败影响的 FLOW / SCN 可追踪
- 10 已确认不等于能力已接入、已真实验证或已上线
- 禁止用 Mock 替代生产真实能力验证

### 11-测试设计与验收用例.md

11 的正式格式见 `## 4.16 Test Design Format`。

规则：

- 11 定义业务逻辑测试顺序、测试依赖关系、测试前置业务事实、测试类型、自动化等级、真实环境要求和预期证明结果。
- 11 不定义测试命令、测试代码、fixture 脚本、测试执行调度、失败重试命令、实际执行状态、实际证据内容或测试通过/失败结果。
- P0 FLOW 必须覆盖正向流程、状态测试、API 测试、权限测试、旧流程测试和回归测试。
- 涉及外部能力时，必须包含真实环境能力测试。
- 涉及页面和交互时，必须包含 UI 行为或 UX 测试。
- API 合同、状态迁移、权限、范围、幂等、并发和旧流程隔离默认必须自动化。
- 真机、外部 Provider、视觉和复杂 UX 可标记为真实环境或人工验证，但不能省略业务与接口自动化。
- Planning 不得输出最终验收通过、测试已执行、测试通过或测试失败结论。

## 测试方案完整性门禁

生成 `11-测试方案与验收用例.md` 时必须检查：

- 每条 P0 FLOW 是否都有正向业务流程测试。
- 每条 P0 FLOW 是否都有前置阻断、状态、接口、权限、旧流程和回归测试。
- 涉及外部能力的 FLOW 是否有真实环境能力测试。
- 涉及页面和交互的 FLOW 是否有 UI 行为或 UX 测试。
- 每条 TEST 是否明确自动化等级。
- 11 中的测试顺序是否与 01 FLOW 顺序一致。
- 是否未记录实际测试结果、实际证据、测试命令或测试代码。

任一缺失时，`11` 不得视为完成。

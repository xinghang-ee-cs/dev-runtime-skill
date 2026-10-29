# Discovery 首轮入口

本文件定义首次提出业务问题前的最小阶段合同，是 07 的逐轮 Discovery 事务与 04 的 current-interaction 格式在首轮的必要投影；后续反馈、文档生成和交接仍按对应完整章节执行。启动只读本文件、SKILL.md 以及 09 的意图边界，不预读 00/01/04/07 的完整内容。已存在的项目状态和指令优先核对，不假设这是空白项目。

## 1. 判断当前入口

先应用 `09-execution-intent-guard.md`。若是实现请求、已有待继续的 Case、文档确认或恢复，则退出本首轮入口，按该模式加载。用户明确开始需求规划且没有当前待恢复交互时才继续。

先执行 SKILL.md 的 doctor、sync/pin 顺序。安装任务本身不能进入本流程。不要把创建文件和内部门禁作为用户答复主体。

## 2. 复用最少事实并绑定位置

检查项目已有指令、README 的项目说明，以及已存在的 `.runtime/planning-layer-runtime/project-profile.yaml`、user-profile、environment-profile 和当前 Planning Context/检查点；文件不存在就不读取，也不批量新建。只读与首问直接有关的事实，不扫描全部源码、框架、数据库、部署或监控。

优先复用项目真实规划根、当前工作包和基线路径。位置能唯一确定时直接绑定；没有现成位置时根据当前项目结构选择本次必要的最小路径，不把示例目录当固定要求；多个候选或会改变既有 SoT 归属时先处理路径，不开始业务访谈。只在当前职责需要时把真实绑定写入 project-profile 或当前 Context。

已有项目先读取紧凑当前基线；后续期次还须读取唯一需求池中与本次请求相关的条目，解决明确冲突，不让用户重复已有记录。已有部署身份直接复用。没有历史运行数据时标记 unavailable，不采集原始日志，不制造业务问题。不推断用户身份、职位或决策权；缺少画像时使用业务白话。

## 3. 在首问前持久化最小检查点

只创建当前工作包的 planning-runtime/current-interaction.yaml，不创建正式 00–15、完整 Planning Context、Handoff、Baseline 或其他三个 Skill 的 Runtime。04 的字段合同仍有效；当前阶段无值的文档装配、设计资产、增量变更和交接字段可以暂不实例化，不复制整份 YAML 示例。

首轮必须有以下恢复信息，名称沿用 04：

- `current_phase`、`planning_status`：当前实际 Discovery 阶段，不声明完成。
- `discovery_checkpoint.status/revision/updated_at/initial_intake_summary/last_applied_round_id`：初始意图摘要、有效 revision 和真实时间；尚无用户回答时 round 不伪造。
- `discovery_checkpoint.active_question`：question_id、topic、prompt_summary、asked_at、answer_status，等待当前首问的回答。
- `discovery_checkpoint.facts/unresolved_items/research_findings/relevant_requirement_pool_refs`：只保存用户明确输入的简短事实和当前未知项。空集合写空列表；项目/公开核验结论不冒充用户确认事实。
- `active_interaction`：target_type=discovery_question、target_id、stage、version、scope、expected_user_action、next_step，绑定同一个 question_id/revision。
- `explanation_adaptation`：无可靠画像时 mode=plain_language、terminology_policy=explain_first_use、source=safe_default；已有偏好优先复用。没有反馈时不伪造 latest_feedback。

用户事实的 fact_id/topic/summary/confirmation_status/source_round_id 只表达真实来源；首问未知项使用 item_id/summary/blocking/resolution_route/next_question。只有实际需要核验的项才增加研究字段。涉及后续复杂格式再读取 04 的对应节及子节。

04 的枚举与 ID 约束不可推测或简写：首轮 `planning_status=planning_in_progress`、`discovery_checkpoint.status=in_progress`、`active_question.answer_status=awaiting_answer`、`active_interaction.stage=discovery_answer`；问题 DQ-<SEQ>、事实 DF-<SEQ>、未决项 DU-<SEQ>、调研 RF-<SEQ>，回答轮次 DR-<SEQ> 尚未发生则为 null。`resolution_route` 仅 project_evidence/web_research/user_confirmation；事实状态仅 candidate/confirmed/superseded。`explanation_adaptation` 还包含 source_refs 列表与带时区的 last_reconciled_at。所有时间使用真实带时区时间，interaction.version 必须等于 checkpoint.revision。

新首轮检查点可以使用 JSON 语法写入 current-interaction.yaml（JSON 是合法 YAML，字段合同不变），用标准库校验，不为启动安装依赖。写入后执行已安装 Skill 中的 `scripts/validate_discovery_entry.py <检查点真实路径>`，再回读。该 validator 只校验新首问，既有 YAML Runtime 走普通恢复，不为了本检查重写历史。校验失败不得提问，按具体错误修正后重验；通过不代表其他阶段门禁通过。

写入后回读，确认初始意图、当前未知、question_id 和 revision 一致。写入或回读失败就报告阻塞，不先提下一问题再补写。

## 4. 最少事件与一条业务问题

实际发生 MODE_SWITCH、STAGE_ENTER 或状态门禁事件时，追加当前 planning-runtime/event-log.md；不重读历史全文。每条沿用 07 的字段：event_seq、timestamp、runtime_mode、event_type、event_id、related_ids、decision、reason、blocking、next_action。记录最短事实与结果，不写完整推理或聊天；只在压缩/阶段收尾真正需要时生成 event-summary.md。事件不是恢复事实源，当前检查点才是。

选择会改变下一步判断的最大业务不确定项。先复用本地可查事实；公开事实确实影响首问时才核验官方来源，并保存 research_id、finding_summary、evidence_scope/status、checked_at、sources 和 planning_relevance，不把可查事实交给用户回答。没有此类依赖时不为了流程形式联网调研。

答复以自然理解、当前未知和一个业务问题组成；同一上下文必要时最多 2–3 个问题。不先定模块、需求边界或技术方案，不把提问变成身份/技术配置问卷，不生成正式规划文档。首问之后等待用户回答，不自行模拟多轮。

收到真实回答后，进入 07 的 `Discovery Round Transaction`：先保存反馈，更新事实和未决项、延期则即时维护需求池，清除原始输入，revision 前进并回读，再持久化下一问题；不得先问后记。若出现业务/资料冲突、外部能力、数据库或 UI/UX 等新依赖，按当前事实精确加载 00/01/04/06/07 或专题的适用章节，不能把本入口当作完整一期规则的替代。

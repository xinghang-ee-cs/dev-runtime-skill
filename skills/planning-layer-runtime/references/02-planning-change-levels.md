# 流程梳理阶段：变更分级

## 1. 变更等级

| 等级 | 类型 | 示例 | 流程要求 |
| --- | --- | --- | --- |
| S | 轻量变更 | 文案、样式、小 Bug、低风险 UI 调整 | 轻量记录 + 验收口径 |
| M | 单模块变更 | 单页面功能、单模块接口调整、局部状态变化 | 按影响动态装配；进入 TASK 时闭合 11、12、13，并在 13 确认后派生 14、15 |
| L | 跨模块变更 | 跨模块流程、权限、数据模型、状态机、架构调整、关键外部能力接入 | 完整走 00-13；13 确认后派生 14、15 |

## 2. S 级变更

适用条件：

- 不改权限
- 不改数据模型
- 不改接口契约
- 不改状态流
- 不影响旧逻辑
- 不影响租户隔离

最小记录：

```text
变更类型：S
变更内容：……
影响范围：……
验收口径：……
后续验证承接：按验收口径由后续承接方记录
```

规则：

- S 级不需要 13 时，不要求 11、12、14、15。
- S 级只保留轻量规划记录与验收口径，不得为了“看起来完整”伪造装配文档。

## 3. M 级变更

必须确认：

- 范围
- 涉及模块
- 涉及状态
- 涉及权限
- 涉及接口
- 涉及数据
- 验收口径
- 涉及外部能力时，必须确认 Capability Registry 与 Evidence Gate

动态装配：

- 必须有 `01-需求范围与验收标准.md`。
- 按实际影响选择 02–10。
- 不进入 TASK 合同时，不强制生成 11、12、13、14、15。
- 只要进入 TASK 合同，最小闭环必须是：

```text
01
+ 按实际影响选择的 02–10
+ 11-测试设计与验收用例
+ 12-风险、依赖与待决策事项
+ 13-开发任务合同与落地清单
-> 13 确认后自动生成 14、15
```

禁止：

- 有 13 和 15，但没有 11、12、14。
- 15 被提前独立生成。
- TASK 引用不存在、未装配或未确认的 FLOW / STATE / API / PERM / ARCH / CAP / TEST 结论。

影响分析：

```markdown
## 影响分析

影响文档：
影响接口：
影响状态：
影响权限：
影响测试范围：
影响外部能力：
影响租户隔离：
影响缓存：
影响历史兼容：
```

## 4. L 级变更

适用：

- 跨模块业务流程
- 权限体系调整
- 数据模型调整
- 状态机调整
- 架构调整
- 多租户规则调整
- 审批、删除、审计、计费相关调整
- 关键外部能力、SDK、OpenAPI、MCP、AI Provider 接入或替换

必须完整走：

```text
00 -> 13
-> 13 确认后自动生成 14、15
```

影响分析：

```markdown
## 影响分析

影响文档：
影响接口：
影响状态：
影响权限：
影响测试范围：
影响外部能力：
影响租户隔离：
影响缓存：
影响历史兼容：
```

规则：

- 禁止只改代码不分析影响
- 禁止跨模块隐式变更
- 所有 L 级变更必须可追踪

## 5. 任务与验收闭包规则

动态装配可以省略“不适用”的文档，但不得省略已被 TASK、TEST、RISK、DEP、OPEN 或验收门禁实际引用的 SoT。

只要本期需要生成 13 TASK，就必须同时具备：

- 11 测试设计与验收用例。
- 12 风险、依赖与待决策事项。
- 所有被 TASK 引用的上游 SoT，且相关结论已确认。

13 被确认后，必须自动生成：

- 14 执行记录框架。
- 15 验收结果与复盘框架。

规则：

- 15 不得作为可独立装配的孤立文档。
- 15 只能由已确认的 13 连同 14 一起自动派生。
- `assembled_documents` 与 `handoff_role_mapping` 只能包含实际已生成的文档和角色，不得为了“看起来完整”伪造路径或角色。

## 6. 期内范围扩展准入

用户在本期规划、执行、测试或验收过程中提出新增或修改时，先做范围准入，不得直接改规划、改代码或把完整 13 重新入队。准入结果只允许：

```text
absorb_as_current_phase_scope
absorb_as_current_phase_delta
defer_to_next_phase
replace_current_phase_scope
```

至少判断：是否为本期验收目标必要补全、是否为原规划遗漏、是否阻断当前 P0 FLOW、是否为独立新增功能、执行是否已开始、是否使已完成 TASK 失效、是否改变 FLOW / STATE / API / PERM / ARCH / UI / 发布范围，以及是否造成大范围返工。

规则：

- 执行尚未开始且基线未冻结时，可以按影响范围修正规划，只重审受影响部分。
- 执行已开始后，独立新增能力默认 `defer_to_next_phase`；用户确认延期后必须立即写入唯一 `<requirement_pool_path>`，不得等待 15、Handoff 或本期结束。
- `defer_to_next_phase` 不改变当前执行基线，不创建本期 Change Set、不修改本期 TASK，也不重建当前 Handoff。
- 后续实际派生 15 时，只在其“下一期输入”中引用 `<requirement_pool_path>#POOL-ID`；最终为 `planning_only` 时 Handoff 同样只引用池条目，不得复制需求正文，也不得为了记录延期需求提前生成 13、14、15。
- 若 Planning Execution Baseline 已冻结而 14/15 尚未真实派生，该状态只能视为框架派生未完成的阻断中间态；可以写入 Requirement Pool，但不得把 Change Set 推进到 `handoff_prepared`，也不得生成 `execution_ready` Handoff 或开始执行。
- Requirement Pool 写入成功不等于需求已进入下一期范围。下一期仍须按 `07-planning-conversation-runtime.md` 与用户当前输入比较并重新确认。
- 新增内容确实阻断当前 P0 FLOW 且不纳入就无法达到本期验收目标时，优先评估 `absorb_as_current_phase_delta`；仍必须完成影响分析，不得因此扩大为整期重跑。
- 必须留在本期且基线已冻结时，只能 `absorb_as_current_phase_delta` 并形成 Change Set。
- 本期方向根本改变时才使用 `replace_current_phase_scope`，必须明确原任务保留、取消、替换和重新执行范围。
- 已关闭期次不得作为普通追加容器；独立新增需求进入下一期。

## 7. Change Set 与增量执行选择

`planning_execution_baseline` 冻结后，允许留在本期的变更必须相对冻结版本计算增量。格式由 `04-planning-format-spec.md` 维护。

强规则：

```text
affected_tasks != 本期全部 TASK
```

- `affected_documents`、`affected_tests`、`affected_tasks` 只包含因依赖传播真实受影响的对象。
- 未受影响文档、FLOW、TEST 和 EXEC 不得因为存在 Change Set 被无条件 reopen；TASK 必须再按完成状态与原执行基线处置分类。
- Recovery Output 的 `affected_documents`、`affected_tasks`、`affected_validation` 是后续装配与执行选择的硬约束，不是说明字段。
- 新增 TASK 使用新 ID；局部扩展已完成 TASK 时创建增量 TASK，不重置原 TASK；错误合同用替代 TASK 保留历史；正在执行的 TASK 只允许继续未受影响部分或重做受影响部分。
- `execution_delta` 必须把任务分为 `executable_tasks`、`reopened_tasks`、`carried_forward_pending_tasks`、`context_only_tasks`、`completed_unchanged_tasks`、`prohibited_rerun_tasks`；完整 13 只提供当前有效合同视图，不自动成为执行队列。
- `execution_delta` 六个列表必须两两互斥；同一 TASK 只能进入一个列表。未受影响且已完成者优先进入 `completed_unchanged_tasks`；`prohibited_rerun_tasks` 只承载尚未被其他五类归类、且因明确合同或事实禁止重跑的 TASK。
- `carried_forward_pending_tasks` 只包含未受当前变更影响、尚未开始、仍属于原 Planning Execution Baseline 的 active TASK；它们必须继续执行，并映射到 Handoff `execute_only`，不得降为 `context_only`。
- 正在执行且未受影响的原基线 TASK 映射到 `resume_only`；已完成且未受影响的 TASK 映射到 `completed_locked`；只作为背景或依赖参考的任务才进入 `context_only`。

保护范围：`unaffected_ids` 不得无条件 reopen；`context_only_tasks` 不得执行；`completed_unchanged_tasks` 与 `prohibited_rerun_tasks` 不得重新执行或重新生成 EXEC。

允许处理范围：`executable_tasks`、`reopened_tasks`、`carried_forward_pending_tasks` 可以按对应 TASK contract revision 和 Handoff 队列继续执行，但不得扩大到未列入的影响范围。禁止把整个 `execution_delta` 解释为禁止执行范围。

多 Change Set 规则：

- 每个 Change Set 使用唯一 `change_revision` 并引用 `base_revision`；完整历史追加到既有 `decision-log.md`，不得覆盖旧快照。
- 新变化到达时先检查当前 active Change Set 状态，不得直接覆盖 `active_change`。
- 旧 Change Set 可继续时，新 Change Set 基于当前有效规划视图和上一 revision；新变化使旧 Change Set 失效时，将旧 revision 标记为 `superseded`，新 revision 明确引用被替代 revision。
- `active_change` 只指向当前 revision；状态依次为 `candidate -> confirmed -> applied_to_planning -> handoff_prepared -> closed`，被替代时为 `superseded`。
- 当前 active Change Set Decision Snapshot 必须是相对冻结 Planning Execution Baseline 的“累计有效增量快照”：其 ID、影响范围、TASK 分类与 `execution_delta` 必须包含所有仍有效的前序 Change Set 结果和本次新增变化。不得只记录当前 revision 的局部差量后再要求 Recovery 扫描 R2、R3 历史拼装当前范围。
- 新 revision 继续承接旧 revision 时，旧快照保留其实际最后状态，不因 active 指针前移而推断为 `closed` 或 `superseded`；`active_change` 表示唯一恢复头，不表示其他历史 revision 的执行或验收事实已经完成。只有真实状态迁移或被替代证据才能追加旧 revision 的新状态快照。

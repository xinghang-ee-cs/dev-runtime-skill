# Bugfix Case Planning Governance

Bugfix Fast Lane 是正式期次之外的追加式缺陷闭环，不是新一期 Planning，也不是冻结基线的 Change Set。只有已确认 `implementation_defect` 且当前 Planning 合同仍有效时适用。

## Planning 的职责

- 不为 Fast Lane 重启 Discovery、重建 Planning Context 或重新装配 00–13。
- 不把 Bug 的执行、测试、发布事实写入原 14/15，也不改变原 baseline hash。
- 保持原 00–15 历史只读；即使期次已经关闭，也只允许在其 `bugfixes/` 下追加 Case。
- 在预期行为、合同有效性或来源期次不明确时执行 gate 和路由。
- `planning_gap`、`requirement_change` 或改变合同的 `design_drift` 必须退出 Fast Lane，按现有 Change Set / Planning Recovery 处理。
- 只有修复已经部署、原 Bug 生产复验完成、同类型问题验证完成且 Case 关闭后，才把新的生产事实更新到 `PROJECT-CURRENT-BASELINE.md`。

## 路径与索引

```text
<phase_planning_directory>/bugfixes/index.md
<phase_planning_directory>/bugfixes/<BUG-ID>/
```

来源无法确认时使用 `<planning_root>/bugfixes/unassigned/<BUG-ID>/`。`index.md` 每行至少记录 Bug ID、Issue、来源期次、当前 `bugfix_status`、owner、`next_required_action`、Case 路径和更新时间；它只是检索索引，状态仍以 Case 内 `bugfix-case.json` 为准。

## 基线更新门禁

Planning 只有在下列条件全部成立后才能消费 Case 的最终事实：

```text
release_status = deployed
+ original_bug_status = production_verified
+ bugfix_status = closed
+ workflow_completed = true
+ 04-similar-bug-review.md proves similar_defect_reviewed
-> update PROJECT-CURRENT-BASELINE.md
```

基线只记录“现在生产中真实成立什么”以及必要的 Case 引用，不复制整个 Bug 历史。发现新的同类型缺陷时，为它创建新 Bug ID、Issue 和 Case；不得扩写已完成补丁的范围。

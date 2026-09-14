# Bugfix Fast Lane 与 Bugfix Case

本规则只用于已经确认的 `implementation_defect`。它把问题诊断、最小补丁、定向测试、上线复验和同类型问题检查串成一个可恢复的短闭环，但不创建新 Planning 期次，也不修改原期次 00–15。

## 准入与退出

进入 Fast Lane 必须同时满足：

- 观察现象、可靠预期来源、根因和具体根因文件已经确认。
- 当前 Planning 合同仍然有效；修复不改变需求、API、数据、权限、状态、UI/UX 或验收合同。
- 修复范围可列成精确文件 allowlist，并能定义原 Bug 回归与相邻风险范围。
- 已创建或关联一个保持到最终闭环才关闭的 Issue。

分流固定为：

```text
implementation_defect + current contract valid -> Bugfix Fast Lane
test_defect -> testing-layer-runtime
planning_gap | requirement_change | contract-changing design_drift
  -> planning-layer-runtime Change Set
```

任一准入条件后来失效，立即停止 Fast Lane；保存已有证据并转 Planning Change Triage，不得用补丁扩大或重写合同。

## 持久目录

优先把 Case 放到问题来源期次内：

```text
<phase_planning_directory>/bugfixes/
  index.md
  BUG-YYYYMMDD-NNN/
    bugfix-case.json
    00-bug-contract.md
    01-long-patch-result.md
    02-test-verification.md
    03-release-verification.md
    04-similar-bug-review.md
```

来源期次无法唯一确认时，暂存于 `<planning_root>/bugfixes/unassigned/<BUG-ID>/`。确认来源后移动整个 Case 并更新索引；不得把内容复制成两个有效 Case。

`bugfixes/` 是追加式事实区，不属于 Planning Execution Baseline，不参与原 00–15 的 baseline hash。已关闭期次的 00–15 继续历史只读；允许追加新的 Case，不允许借 Case 回写或覆盖那些文档。

`bugfix-case.json` 是跨 Skill 的机器状态源，schema 固定为 `bugfix-case/v1`。五份 Markdown 保存事实、证据和给人的解释，不得与 JSON 状态冲突。Testing 在接管、发布返回和关闭前运行自己的 `validate_bugfix_case.py`。

## `00-bug-contract.md`

诊断层创建并填写：

- Bug ID、Issue URL/编号、来源期次或 `unassigned`、发现环境与已部署 revision。
- observed、expected、`expected_behavior_source`、稳定复现步骤与证据。
- severity、用户/业务影响、直接原因、根本原因和具体根因文件。
- 唯一或高度确定的修复策略、精确 allowed paths、禁止范围。
- 原 Bug 回归目标、相邻高风险路径、回滚/止血策略。
- Change Triage：`implementation_defect`、`fix_in_execution`、当前合同仍有效。

初始化后：

```yaml
schema_version: bugfix-case/v1
bugfix_status: diagnosed
workflow_completed: false
next_required_action:
  action: long_bugfix_patch
  primary_owner: long-task-orchestrator
  supporting_skill: ai-code-inspection
  target_record: 01-long-patch-result.md
  status: pending
```

## GitHub 与版本

Bug 修复同样遵守项目 GitHub 治理：Issue → 最新默认分支 → `fix/<BUG-ID>-short` → commits → PR/CI → 仅通过 PR 合并 → 部署。禁止因紧急而直写默认分支。

产品 Bug PR 使用 `Refs #N`，不要使用会在合并时自动关单的 `Closes #N`。Issue 必须保持 open，直到生产复验与同类型问题验证都完成。无合同变化的兼容修复通常提升 PATCH；一旦需要合同/API/数据变化就退出 Fast Lane，由正式 Planning 决定版本。

## 恢复与交接

每次进入相关项目或收到上线返回时，先扫描所有 `bugfix-case.json`。发现 `workflow_completed: false` 必须按 `next_required_action` 恢复，不依赖聊天记忆。

若用户暂缓，写入 `paused_at`、`paused_reason` 和 `resume_action`，仍保持 `workflow_completed: false`。若状态为 `awaiting_similar_defect_verification`，唯一下一步是交给 Testing 执行 `04-similar-bug-review.md`，不得先宣告流程完成。

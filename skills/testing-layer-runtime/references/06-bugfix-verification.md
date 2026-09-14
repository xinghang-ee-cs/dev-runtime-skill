# Bugfix Verification 与上线后同类型问题验证

本模式只消费 `bugfix-case/v1`，不建立完整期次 Test Plan，也不默认重跑全部 FLOW。Testing 是原 Bug 定向验证和上线后同类型问题验证的主 owner；ai-code-inspection 支持根因模式、调用链和数据映射扫描，Long 只接收新建 Case 的实现缺陷。

## Intake 与定向测试

读取 `bugfix-case.json`、`00-bug-contract.md` 和 `01-long-patch-result.md`。只有 `bugfix_status: ready_for_bug_verification`、Long 证据可复用且实际 revision 一致时进入。

定向范围固定为：

1. 原 Bug 的稳定复现路径。
2. 补丁直接影响路径。
3. Bug 合同列出的相邻高风险路径。
4. 仅在适用时执行人工、真机、云端或外部能力验证。

Long 已完成且仍有效的自动化标为 `reused_from_long`，不得为形式完整重复执行。把步骤、环境、revision、结果、证据、失败与残余风险写入 `02-test-verification.md`。通过后进入项目发布流程；Testing 不替代 release/security gate。

## 发布与生产复验

`03-release-verification.md` 记录分支、PR、Issue 引用方式、CI、合并 commit、部署 revision、版本、回滚点和生产复验。产品 Bug PR 必须使用 `Refs #N`；Issue 保持 open。

部署不等于完成。状态顺序至少包含：

```text
merged
-> deployed
-> original_bug_production_verified
-> awaiting_similar_defect_verification
-> similar_defect_verifying
-> similar_defect_reviewed
-> closed
```

原 Bug 完成生产复验后必须立即持久化：

```yaml
release_status: deployed
original_bug_status: production_verified
bugfix_status: awaiting_similar_defect_verification
workflow_completed: false
next_required_action:
  action: post_release_similar_defect_verification
  primary_owner: testing-layer-runtime
  supporting_skill: ai-code-inspection
  target_record: 04-similar-bug-review.md
  status: pending
```

随后向用户突出输出唯一下一步：

> 修复已上线，原 Bug 已完成生产复验，但流程尚未结束。当前停在等待同类型问题验证。下一步必须继续 Testing，扫描并定向验证潜在的其他同类型问题。

不得把这条提醒埋在普通总结或可选建议中，也不得先说“修复流程已完成”。

## 同类型问题验证

`04-similar-bug-review.md` 必须覆盖：

- 与根因相同的代码模式和错误条件。
- 相似模块、调用者、数据映射、状态与异常路径。
- 已有自动化能否覆盖该类失败，以及新增的定向验证证据。
- 每个发现的结论、证据和后续 Bug ID/Issue。

发现另一个同类型问题时创建新的 Bug ID、GitHub Issue 和 Case；不要静默扩大原补丁。新 Case 按自己的优先级进入 Fast Lane，原 Case 可在其扫描范围与新 Issue 引用完整后继续关闭。

只有 `similar_defect_reviewed` 且 `04-similar-bug-review.md` 证据完整时，才设置 `bugfix_status: closed`、`workflow_completed: true` 并关闭原 Issue。

## 跨会话恢复

每次进入项目、收到部署返回或恢复 Testing 时扫描未完成 `bugfix-case.json`。若状态为 `awaiting_similar_defect_verification`，立即提醒并恢复本模式。用户延期时持久化：

```yaml
paused_at: <timestamp>
paused_reason: <user-confirmed reason>
resume_action: post_release_similar_defect_verification
```

延期不改变 `workflow_completed: false`，也不允许关闭 Issue。

## Issue 关闭清单

```text
- [x] 根因确认
- [x] 修复完成
- [x] 自动化验证
- [x] PR 合并
- [x] 部署
- [x] 原 Bug 生产复验
- [ ] 同类型问题扫描
- [ ] 同类型问题定向测试
- [ ] Bugfix Case 关闭
```

最后三项完成后才能关闭 Issue。

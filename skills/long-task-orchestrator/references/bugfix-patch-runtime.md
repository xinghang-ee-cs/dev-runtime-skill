# Bugfix Patch Runtime

本模式用于 `bugfix-case/v1` 已完成诊断且 Change Triage 为 `implementation_defect -> fix_in_execution` 的快速补丁。它可以处理已发布或已关闭期次，不要求恢复一个活动 Planning Runtime，也不要求至少四个实现单元。

## Intake

必须读取 Case 的 `bugfix-case.json` 和 `00-bug-contract.md`，并确认：

- Issue 存在且仍为 open。
- 来源 Planning 合同引用可读，或 Case 提供了可靠 `expected_behavior_source`。
- `current_planning_contract_valid: true`。
- allowed paths、根因文件、修复策略、回归目标和回滚策略具体且一致。
- 不涉及新需求、公共合同、数据模型、权限/状态语义或架构路径变化。

若缺少其中任何一项，停止实现并返回 ai-code-inspection 补证；若合同不再有效，转 planning-layer-runtime，不得自行扩充 Case。

## 执行与门禁

```text
bugfix_patch intake
-> set bugfix_status = patching
-> implement exact allowed scope
-> add a regression that fails before and passes after when feasible
-> run affected validation matrix
-> run necessary broader build/typecheck/load checks
-> inspect actual diff against allowed paths
-> write 01-long-patch-result.md
-> set bugfix_status = ready_for_bug_verification
-> hand off to testing-layer-runtime
```

补丁可以只有一个实现单元。验证范围必须与风险相称：不因“快”而跳过已有 required gate，也不把与补丁无关的完整期次重新实现或重跑。Long 已经产出的当前、可验证自动化证据应由 Testing 继承。

`01-long-patch-result.md` 至少记录：提交前 revision、实际修改文件、diff 与 allowlist 对账、回归测试、受影响验证矩阵、必要广义验证、失败/跳过项、残余风险、回滚条件和 Long 结论。

交接状态：

```yaml
bugfix_status: ready_for_bug_verification
workflow_completed: false
next_required_action:
  action: bugfix_verification
  primary_owner: testing-layer-runtime
  supporting_skill: long-task-orchestrator
  target_record: 02-test-verification.md
  status: pending
```

## 边界

- 不修改原 00–15、Planning Baseline 或 Bug 合同中的预期行为。
- 不扩大 allowed paths；新根因或新缺陷创建独立 Bug ID/Issue/Case。
- 不执行人工验收、生产部署或 Case 关闭。
- 产品 Bug PR 必须引用 Issue，使用 `Refs #N`，并在适用 CI 通过后才由 PR 合并。

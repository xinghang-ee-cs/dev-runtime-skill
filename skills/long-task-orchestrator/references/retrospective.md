# 执行复盘闭环

本文件只定义 Runtime Evidence Consolidation Protocol。

## 前置条件

```text
task-execution_final_check_done
task.md_readable
execution-events.md_readable
validation-results.md_readable
agent-decisions.md_readable
```

## 证据来源

证据必须追溯到：

- `task.md`
- `execution-events.md`
- `validation-results.md`
- `testing-handoff.md` 或 `long-runtime-testing-summary.md`
- `agent-decisions.md`

可选正式来源：

- 正式执行记录
- 正式验收记录
- 源计划

缺少必需证据 -> STOP。

## 复盘规则

复盘输出必须：

- 区分 `DONE` / `SKIPPED` / `PARTIAL` / `BLOCKED`
- 包含验证证据
- 确认 Long Testing Handoff 已写出
- 包含剩余风险
- 将不支持或不可用的验证写成不可用，而不是通过
- 排除无证据支撑的结论

证据归并必须满足：

```text
task_state -> task.md
lifecycle_event -> execution-events.md
validation_result -> validation-results.md
testing_handoff -> testing-handoff.md or long-runtime-testing-summary.md
agent_decision -> agent-decisions.md
remaining_risk -> agent-decisions.md
```

## Runtime 生命周期摘要

复盘必须记录：

- runtime-epoch
- context-version
- 是否发生 `INVALIDATED`
- 是否发生 Runtime Recovery Failed
- 是否重新生成 Runtime Context
- 是否存在长期失效上下文

## Retrospective Boundary

复盘只能总结：

- implementation result
- unit validation result
- automated business/integration/api/ui validation result
- capability minimum validation
- Long Testing Handoff summary
- remaining risks before testing-layer-runtime takeover

禁止输出：

- release approved
- final acceptance passed
- production ready

如果以下测试未执行：

- manual local test
- real-device test
- server/deployed environment verification
- final acceptance

必须明确写为：

```text
NOT_EXECUTED
```

并写入 Long Testing Handoff 的 `manual_required`，不得隐式通过，也不得作为 long 未完成项阻塞 `ready_for_local_test`。

## 禁止

- 不得在最终检查完成前复盘。
- 不得把未执行的检查写成通过。
- 不得把 `SKIPPED`、`PARTIAL` 或 `BLOCKED` 写成完成。
- 不得新增无证据支撑的结论。
- 不得定义 artifact 文件名。
- 不得定义输出模板。
- 不得定义清理流程。
- 不得把 `temporary-execution-log.md` 作为核心证据来源。

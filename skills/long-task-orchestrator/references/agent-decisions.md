# Agent 决策模板

本文件是 Runtime State Template。

实例化位置：

```text
<phase_runtime_directory>/agent-decisions.md
```

禁止在本文件保存某一期项目决策记录。

## Runtime Session

```yaml
runtime_session_ref: <phase_runtime_directory>/current-runtime-context.md
```

## Schema

```yaml
decision_id:
time:
decision_type:
related_task:
decision:
reason:
impact:
evidence_ref:
delegation_source:
boundary_check:
```

## 允许记录

- 接受建议
- 拒绝建议
- 延期
- subAgent使用
- subAgent拒绝
- 风险接受
- 明确委托范围内的私有技术实现决策

## 禁止记录

- 测试结果
- 生命周期事件
- 正式执行记录
- 正式验收记录

## Template

```yaml
decision_id: <DECISION-ID>
time: <ISO-8601 timestamp>
decision_type: <accepted | rejected | deferred | subagent_used | subagent_rejected | risk_accepted | delegated_technical_detail>
related_task: <TASK-ID or null>
decision: <decision summary>
reason: <reason>
impact: <runtime impact>
evidence_ref: <Phase Runtime Directory file or formal project record path>
delegation_source: <Planning Handoff explicitly_delegated field reference or not_applicable>
boundary_check: <private, reversible, no public semantic impact, within task boundary>
```

## Example

```yaml
decision_id: DECISION-001
time: <ISO-8601 timestamp>
decision_type: deferred
related_task: <TASK-ID>
decision: defer server or external capability final verification
reason: manual/server/final verification is outside long-task-orchestrator boundary
impact: record manual_required item for testing-layer-runtime handoff
evidence_ref: <phase_runtime_directory>/testing-handoff.md
```

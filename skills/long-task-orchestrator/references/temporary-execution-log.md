# 临时执行日志模板

本文件是 Runtime State Template。

实例化位置：

```text
<phase_runtime_directory>/temporary-execution-log.md
```

本文件不承担核心 Runtime State，仅用于短期、可清理的信息。

禁止在本文件保存某一期长期项目执行记录。

## Schema

```yaml
entry_id:
time:
category:
related_task:
summary:
expires_when:
promote_to:
```

## 允许记录

- 无法分类的临时事实
- 短期调试记录
- 临时恢复信息

## 禁止记录

- Runtime Kernel
- Runtime Procedure
- 正式执行记录
- 正式验收记录
- 不可清理的 P0/P1 决策

## Template

```yaml
entry_id: <TEMP-ENTRY-ID>
time: <ISO-8601 timestamp>
category: <scratch | debug | recovery_hint>
related_task: <TASK-ID or null>
summary: <temporary fact>
expires_when: <condition>
promote_to: <none | execution-events.md | validation-results.md | agent-decisions.md | formal project record>
```

## Example

```yaml
entry_id: TEMP-001
time: <ISO-8601 timestamp>
category: recovery_hint
related_task: <TASK-ID>
summary: rerun validation after dependency cache refresh
expires_when: validation result is recorded
promote_to: validation-results.md
```

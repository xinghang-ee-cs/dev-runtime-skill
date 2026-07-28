# Task 状态机

本文件定义 `task.md` 的运行态状态机。

`task.md` 是运行期执行控制表，不是正式计划来源。
正式计划仍以源落地清单和计划文档为准。

## 1. 状态枚举

| 状态 | 含义 |
| --- | --- |
| TODO | 尚未开始 |
| IN_PROGRESS | 正在执行 |
| WAITING_VALIDATION | 实现完成，等待验证 |
| IN_REVIEW | 验证完成，等待主 Agent 复核 |
| DONE | 已完成，且完成证明与验证证据成立 |
| PARTIAL | 部分完成，但仍有未完成范围 |
| BLOCKED | 被阻塞，无法安全继续 |
| SKIPPED | 明确跳过或延期 |
| INVALIDATED | 当前运行态已失效，必须重新确认 |

状态枚举只能由 Skill Kernel 正式定义。本文件不得临时新增 Human Gate 或 Acceptance Gate 状态。

禁止新增：

```text
WAITING_HUMAN_ENVIRONMENT_PREPARATION
WAITING_ACCEPTANCE_ENVIRONMENT_CONFIRMATION
HUMAN_GATE_ENTERED
```

除非该状态已经在 Skill Kernel 中正式定义。

## 2. 状态流转

```text
TODO
-> IN_PROGRESS
-> WAITING_VALIDATION
-> IN_REVIEW
-> DONE
```

异常流转：

```text
TODO -> BLOCKED
IN_PROGRESS -> BLOCKED
WAITING_VALIDATION -> BLOCKED
IN_REVIEW -> PARTIAL
IN_REVIEW -> BLOCKED
IN_REVIEW -> SKIPPED
PARTIAL -> IN_PROGRESS
BLOCKED -> IN_PROGRESS
SKIPPED -> TODO
TODO -> INVALIDATED
IN_PROGRESS -> INVALIDATED
WAITING_VALIDATION -> INVALIDATED
IN_REVIEW -> INVALIDATED
PARTIAL -> INVALIDATED
BLOCKED -> INVALIDATED
```

禁止流转：

```text
TODO -> DONE
IN_PROGRESS -> DONE
WAITING_VALIDATION -> DONE
BLOCKED -> DONE
SKIPPED -> DONE
INVALIDATED -> DONE
```

## 3. 状态进入条件

### TODO

进入条件：

- 任务来自正式源落地清单。
- 已写明目标、来源、所有权、依赖、验证方式和完成证明。
- 尚未开始执行。

### IN_PROGRESS

进入条件：

- 前置依赖已完成，或被明确跳过且记录原因和影响。
- 所有权边界清楚。
- 不与其他并行任务冲突。
- 不存在高风险未确认项。
- Planning Handoff Intake 与 execution constraints 有效。
- 当前 TASK 位于 `execute_only`、`resume_only` 或 `reexecute_affected_part`，且 contract revision 与 Handoff 一致。
- 实现承接策略已确认，稳定业务命名与禁止命名已记录。
- 当前 TASK 的实现合同完整，参数状态无 `blocking_open`。
- 涉及依赖变更时 Dependency Governance Gate 已通过。

### WAITING_VALIDATION

进入条件：

- 实现动作已完成。
- 已记录实际改动文件。
- 已确认不存在架构/合同偏差；存在时必须转入 `BLOCKED`。
- 准备执行验证门禁。

### IN_REVIEW

进入条件：

- 已执行验证，或已记录验证不可用原因。
- 验证结果已写入 `Phase Runtime Directory/validation-results.md`。
- 如使用 subAgent，subAgent 输出已返回。
- 等待主 Agent 复核是否可采纳。

### DONE

进入条件：

- 完成证明成立。
- 验证证据成立，或验证不可用原因已记录。
- 主 Agent 已复核。
- 无未处理高风险偏差。
- `execution_constraint_validation.result = passed`。
- 已同步正式执行记录。

### PARTIAL

进入条件：

- 任务只完成部分范围。
- 剩余范围明确。
- 风险和影响已记录。
- 后续处理路径明确。

### BLOCKED

进入条件：

- 高风险不确定项未确认。
- 上游计划冲突。
- 依赖缺失。
- 验证命令不可确认且无替代证据。
- 所有权边界冲突。
- 继续执行可能破坏接口、权限、状态、数据或共享环境。
- 业务/合同参数缺失或为 `blocking_open`。
- 实现承接位置不成立，或新业务域缺少正式架构依据。
- 架构/合同偏差等待上游确认。
- 依赖版本、官方来源或兼容性无法确认。

### SKIPPED

进入条件：

- 明确不做或延期。
- 已写明跳过原因。
- 已写明影响范围。
- 已写明后续处理方式。
- 已同步执行记录和决策记录。

### INVALIDATED

进入条件：

- 正式计划变化。
- Planning Handoff 或 execution constraints 变化。
- Planning baseline/change revision 或 execution selection 变化且当前 TASK 确实受影响。
- 接口/状态/权限/数据模型变化。
- Runtime 恢复失败。
- context-version 冲突。
- 上游确认后正式计划、Planning Handoff 或 execution constraints 发生变化。
- Runtime Kernel 变化。

进入 `INVALIDATED` 后：

```text
停止执行
-> 重新读取 Source of Truth
-> 重新生成 Runtime Context
-> 按新 Handoff 队列只重新确认受影响 task
```

不得把 `completed_locked`、未受影响的 `resume_only` 或 carried-forward pending `execute_only` 无条件标记为 `INVALIDATED`。

## 4. task.md 结构

```text
task.md = Static Task Definition + Current Task State Table
```

### Static Task Definition

Static Task Definition 只包含静态字段。

每个执行单元使用以下格式：

```md
1.1 执行单元名称

- 任务ID：
- 目标：
- 来源：
- 所有权：
- 依赖：
- 影响范围：
- 共享边界：
- 拓扑等级：P0/P1/P2/P3
- 是否允许并行：是/否
- 是否允许委派：是/否
- 验证方式：
- 完成证明：
- Planning 追踪来源：
- Planning Baseline Revision：
- Active Change Revision：
- TASK Contract Revision：
- Execution Disposition：
- 稳定业务概念：
- execution_constraints 来源：
- 实现承接策略：
- 优先承接的现有业务域：
- 是否需要新建长期业务域：
- 新业务域架构依据：
- 禁止实现命名：
- 参数合同状态：
- 明确委托的技术参数：
- 是否涉及依赖变更：
```

字段规则：

- Planning 追踪来源只引用 Planning ID 与路径，不作为实现命名来源。
- Active Change Revision 在初始 Handoff 中必须省略；增量 Handoff 中必须与 Planning Handoff 一致。
- Execution Disposition 只允许 `execute_only`、`resume_only`、`reexecute_affected_part`；`context_only`、`completed_locked`、`cancelled` 不得生成可执行 Static Task Definition。
- 稳定业务概念不得使用期次、阶段、Sprint、版本或 Planning ID。
- 实现承接策略只允许 `extend_existing_domain`、`reuse_shared_capability`、`create_stable_business_domain`。
- `create_stable_business_domain` 时“新业务域架构依据”必填，且必须引用正式架构依据。
- 禁止实现命名必须列出本任务不可出现的期次/阶段/Sprint/版本/追踪 ID 命名模式。
- 参数合同状态记录适用参数是否均为 `confirmed`、`explicitly_delegated` 或 `not_applicable`。
- 明确委托的技术参数只记录 Planning 明确委托给执行层的参数。

### Current Task State Table

```md
## Current Task State Table

| task_id | status | execution_ref | validation_ref | review_status | blocker | last_updated |
| --- | --- | --- | --- | --- | --- | --- |
```

规则：

```text
task current status must be updated only in Current Task State Table
static task definition must not contain mutable status
old status snapshot must be overwritten, not duplicated
patch task must also use Current Task State Table
```

## 5. 状态更新规则

- 状态变更必须按状态机流转。
- 每次状态变更必须记录原因。
- 当前状态只能更新在 `Current Task State Table`。
- Static Task Definition 不得写入 mutable status。
- 旧状态快照必须覆盖，不得追加复制。
- 进入 `WAITING_VALIDATION` 必须已有实际改动记录。
- 进入 `IN_REVIEW` 必须已有验证记录。
- 进入 `DONE` 必须已有完成证明和主 Agent 复核。
- 进入 `BLOCKED` 必须写明阻塞项和解除条件。
- 进入 `SKIPPED` 必须写明原因、影响和后续处理。
- 进入 `INVALIDATED` 必须写明失效原因、invalidated-by 和重新确认路径。
- `PARTIAL` 不能作为最终成功状态。

## 6. 状态证据写入位置

| 状态行为 | 写入位置 |
| --- | --- |
| 阶段开始/结束 | `Phase Runtime Directory/execution-events.md` |
| 验证结果 | `Phase Runtime Directory/validation-results.md` |
| Long Testing Handoff | `Phase Runtime Directory/testing-handoff.md` 或 `Phase Runtime Directory/long-runtime-testing-summary.md` |
| subAgent 采纳/拒绝 | `Phase Runtime Directory/agent-decisions.md` |
| 明确委托范围内的私有技术实现决策 | `Phase Runtime Directory/agent-decisions.md` |
| 无法分类临时事实 | `Phase Runtime Directory/temporary-execution-log.md` |
| 当前任务状态索引 | `Phase Runtime Directory/task.md` 的 `Current Task State Table` |
| 当前快照 | `Phase Runtime Directory/current-runtime-context.md` |
| 可恢复运行态 | `Phase Runtime Directory/checkpoint-runtime.md` |

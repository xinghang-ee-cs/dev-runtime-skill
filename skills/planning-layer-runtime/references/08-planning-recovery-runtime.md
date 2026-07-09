# 规划恢复运行时（Planning Recovery Runtime）

## 1. 范围（Scope）

本文档仅负责：

- Runtime Recovery
- Runtime Rollback
- SoT Invalid Propagation
- Validation Reopen
- Capability Revalidation Trigger
- Runtime Resume Path
- Recovery Event reuse
- Runtime Audit Logging
- Decision Snapshot Recovery Boundary

禁止：

- 修改业务 SoT
- 修改 Runtime Kernel
- 自动修正文档
- 自动生成最终修复方案
- Runtime 自动优化自身
- Runtime 自动修改规则
- Runtime 自动删除规则

## 2. 恢复运行时（Recovery Runtime）

Recovery Runtime 只允许：

```text
发现失效
传播失效
记录恢复路径
恢复 Runtime 状态
```

禁止：

```text
自动修复系统
```

## 3. 恢复触发条件（Recovery Trigger）

以下情况触发 Recovery：

- PROJECT-CURRENT-BASELINE_CHANGED
- FLOW-CONTRACT_CHANGED
- JOURNEY-OBJECT-MAP_CHANGED
- SCENARIO-CONTRACT_CHANGED
- MODULE-BOUNDARY_CHANGED
- GLOBAL-STYLE_CHANGED
- DESIGN-ASSET_CHANGED
- STATE-DATA-FACT_CHANGED
- API-CONTRACT_CHANGED
- PERM-SCOPE-DATA-DOMAIN_CHANGED
- ARCH-DECISION_CHANGED
- CAPABILITY-DECISION_CHANGED
- TEST-DESIGN_CHANGED
- RISK-DEP-OPEN_CHANGED
- TASK-CONTRACT_CHANGED
- ACCEPTANCE-GATE_CHANGED
- 上游 SoT 修改
- 权限边界修改
- 状态机修改
- Capability Revalidation
- 接口契约修改
- 文档确认状态回退
- UI/交互确认状态回退
- 测试失败
- Validation Gate 失败
- Runtime Gate 失败
- Capability Binding 失效
- Acceptance Reopen
- 高风险冲突重新出现

## 4. 恢复输出（Recovery Output）

Recovery Runtime 必须输出：

```yaml
recovery_id:
trigger_source:
invalidated_items:
affected_documents:
affected_tasks:
affected_validation:
affected_capabilities:
recovery_stage:
recovery_action:
resume_condition:
blocking:
```

规则：

- 不允许自由格式。
- 不允许长篇解释。
- 不允许 AI 推理内容。
- 不允许自然语言总结。

## 5. SoT 失效传播（SoT Invalid Propagation）

当上游 SoT 修改时，必须传播：

- 下游文档失效
- Validation 失效
- Acceptance 失效
- 任务承接准备失效
- Capability Validation 失效

示例：

```text
06 修改
-> 07 invalid
-> 08 invalid
-> 11 reopen
-> 13 reopen
-> 15 reopen
```

新增传播规则：

```text
PROJECT-CURRENT-BASELINE_CHANGED
-> 当前 Planning Context invalid
-> 00 invalid
-> 01 invalid
-> 02 invalid
-> 相关下游文档按依赖关系 invalid

FLOW-CONTRACT_CHANGED
-> 02 invalid
-> 03 invalid
-> 04 invalid
-> 05/06/07/08/11/13 按依赖关系 reopen

JOURNEY-OBJECT-MAP_CHANGED
-> 03 invalid
-> 06 invalid
-> 07 invalid
-> 08 invalid
-> 11 invalid
-> 13 invalid

FLOW changed
-> related SCN invalid
-> related MODULE coverage reopen
-> PAGE / UI-MOD / UX-SCN review reopen
-> related prompts and assets marked review_pending or superseded

SCN changed
-> related MODULE coverage reopen
-> related PAGE / UI-MOD / UX-SCN reopen

MODULE boundary changed
-> related PAGE / UI-MOD / UX-SCN reopen

global style changed
-> related PROMPT-PAGE / PROMPT-MODULE / PROMPT-UX reopen
-> visual assets marked review_pending

FLOW / DOMAIN 变化
-> 06 invalid
-> 07 invalid
-> 08 invalid
-> 11 reopen
-> 13 reopen

STATE / DATA FACT 变化
-> 07 invalid
-> 08 invalid
-> 11 reopen
-> 13 reopen

API Contract 变化
-> 08 invalid
-> 11 reopen
-> 13 reopen

PERM / Scope / Data Domain 变化
-> 07 contract review required
-> 11 reopen
-> 13 reopen

ARCH 决策变化
-> 关联 CAP review required
-> 关联 TEST reopen
-> 13 reopen

CAP 选型或关键前提变化
-> 关联 ARCH review required
-> 关联 TEST reopen
-> 12 风险 reopen
-> 13 reopen

TEST 设计变化
-> 13 测试任务 reopen
-> 后续测试与验收承接准备需要重新审查
-> 15 相关验收结果 reopen

FLOW / STATE / API / PERM 变化
-> 09 review required
-> 关联 CAP review required
-> 11 reopen
-> 13 reopen
-> 15 相关验收结果 reopen

RISK / DEP / OPEN 变化
-> 相关 TASK 需要重新审查
-> 相关 14 预置执行项需要重新审查
-> 相关 15 预置验收项需要重新审查

TASK 合同变化
-> 14 对应预置执行项失效
-> 15 对应预置验收项失效
-> 尚未填写真实事实的 14、15 标记 framework_rebuild_required
-> 未填写实际事实的部分按新 TASK 合同重建
-> 已由后续阶段写入的实际事实不得被 planning recovery 自动删除、覆盖或伪造
-> Handoff 需要在 Execution and Acceptance Framework Derivation Gate 通过后基于真实路径重新生成

验收标准、风险关闭条件或发布门禁变化
-> 15 对应预置验收项失效
-> 必须更新 15 框架后才能继续使用
```

禁止：

```text
局部偷偷修复
```

规则：

- 不得继续沿用旧 task、旧测试映射或旧 handoff。
- 必须重新读取当前有效 SoT，再继续后续文档。
- Recovery 必须复用已有 Runtime Event Log 与现有事件类型。
- 禁止新增日志目录、独立事件系统或独立 Recovery SoT。
- 视觉资产变化若不改变业务动作、场景入口、异常恢复、资格或流程终态，不得反向修改 01/02。
- 视觉资产变化若导致主操作、进入条件、异常处理、旧入口处理或用户路径变化，必须回到 03；若影响合法业务旅程，则继续回到 01/02。
- 不得继续沿用旧接口兼容结论。
- 06/07/08 恢复时必须先读取当前有效 SoT，再恢复后续文档。
- 不得继续沿用旧测试映射、旧任务拆分、旧能力结论或旧架构绑定。
- 09/10/11 恢复时必须先读取当前有效 SoT，再继续下游文档或运行时。
- 12/13/14/15 恢复时只处理 planning skill 内部的框架失效与重审标记，不定义其他 skill 的恢复行为。
- 14、15 未填写实际事实的预置项可以标记为 `framework_rebuild_required` 并按新合同重建；已经由后续阶段填写的事实不得由 planning recovery 自动删除、覆盖、伪造或回退。
- Recovery 不得出现“先有 14、15 才能确认 13”的恢复路径；14、15 只在 13 已确认后派生或重建未填写的预置项。

## 6. 恢复恢复门禁（Recovery Resume Gate）

Recovery 不允许无限进行。

必须定义：

```yaml
resume_condition:
blocking_count:
conflict_count:
revalidation_required:
```

只有恢复完成后，才允许：

```text
重新进入 Planning Runtime
```

规则：

- Recovery Runtime 必须复用 Runtime Event Logging。
- Recovery Event 写入 `docs/计划安排/<第X期>/planning-runtime/event-log.md`。
- 禁止新增独立 Recovery Event System。
- Recovery Trigger 只允许追加一条 Decision Snapshot。
- Resume Gate 不得依赖历史 Decision Log。

## 7. 运行时审计层（Runtime Audit Layer）

允许：

- Runtime 自检
- Runtime 风险检测
- Runtime 熵增检测

禁止：

- Runtime 自动优化自己
- Runtime 自动修改规则
- Runtime 自动修复 SoT
- Runtime 自动重写文档

规则：

- 只能写日志。
- 不能自动修改。
- 不影响普通用户使用。

## 8. 运行时审计日志（Runtime Audit Log）

Audit 输出默认写入：

```text
docs/计划安排/<第X期>/planning-runtime/audit-log.md
docs/计划安排/<第X期>/planning-runtime/audit-summary.md
```

仅用于：

- Runtime Debug
- Runtime Governance
- Model Comparison
- Human Review

定位：

- Project Runtime Evidence
- 项目执行证据
- 不是 Runtime State

禁止：

- 业务事实定义
- Runtime SoT
- 用户流程
- 正式验收
- Runtime Recovery Source

以下内容只写入 `planning-runtime/audit-log.md`：

- 熵增检查
- Runtime 自检
- SoT 冲突
- 规则重复
- 文档职责漂移
- Runtime 膨胀
- 日志膨胀
- Capability 重复
- 长期 BLOCKER
- 长期 Pending
- Runtime 循环依赖

禁止：

- 注入用户对话
- 干扰 Planning Context
- 自动进入正式 SoT
- 自动阻塞普通用户任务

## 9. 审计事件格式（Audit Event Format）

统一格式：

```yaml
timestamp:
audit_id:
audit_type:
severity:
related_files:
related_ids:
detected_issue:
entropy_risk:
recommended_action:
human_review_required:
```

Audit 类型：

```text
RULE_DUPLICATION
SOT_CONFLICT
RESPONSIBILITY_DRIFT
RUNTIME_BLOAT
LOG_BLOAT
LONG_PENDING
LONG_BLOCKER
CAPABILITY_DUPLICATION
CIRCULAR_DEPENDENCY
INVALID_PROPAGATION_FAILURE
UNUSED_RUNTIME_FILE
```

新增 `audit_type` 必须满足：

- 单职责
- 不重复已有语义
- 不允许历史补丁命名
- 不允许模糊命名
- 必须经过 human review

若已有 `audit_type` 能表达问题，禁止新增新类型。

Audit 的目标是：

```text
发现 Runtime 风险
```

而不是：

```text
保存 Runtime 历史
```

禁止：

- 演变成问题数据库
- 演变成历史记忆系统
- 演变成 Runtime 分析系统
- 演变成长期状态存储

## 10. 审计日志生命周期（Audit Log Lifecycle）

Audit Log 必须：

- append-only
- 结构化
- 短字段
- 禁止长解释
- 禁止全量推理
- 禁止完整聊天记录
- 禁止重复事件

`audit-log.md` 作为 Project Runtime Evidence 长期保留。

历史问题必须 summary 化，进入：

```text
audit-summary.md
```

禁止：

- 无限增长
- 全量重新加载
- 历史日志重新注入 Runtime

## 11. 用户隔离（User Isolation）

普通用户不需要知道：

- Runtime Audit
- 熵增
- Runtime Governance
- Skill 自检

用户态原则：

```text
描述需求
-> 回答必要问题
-> 获取 Planning Context
-> 获取正式文档
-> 进入开发
```

规则：

- Runtime Audit 不进入用户态输出。
- Runtime Audit 不污染 Planning Context。
- Runtime Audit 不增加用户交互复杂度。
- Runtime Audit 不替代业务阻塞。

## 12. 决策快照恢复边界（Decision Snapshot Recovery Boundary）

Recovery Runtime 可以使用 Decision Snapshot，但只允许：

- 追加 Recovery Trigger 决策快照
- 在 Runtime Debugging 中读取 `planning-runtime/decision-summary.md`
- 在用户主动回传日志时读取相关片段

禁止：

- 默认读取完整 `planning-runtime/decision-log.md`
- 用历史 Decision Log 推导当前 Runtime 状态
- 将 Decision Snapshot 写入 Planning Context
- 将 Decision Snapshot 写入正式 SoT
- 将 Decision Snapshot 写入 Handoff Package
- 将 Decision Snapshot 写入 Capability Registry
- 将 Decision Snapshot 写入 Acceptance
- 新增 recovery 专用日志

规则：

- `.plan/` 是 Bootstrap Context，不是 Runtime Recovery Source。
- Recovery 判断必须来自当前 SoT、当前 Gate、当前 Recovery Output。
- 不得用 `.plan/` 中的历史信息恢复正式业务状态。
- Decision Snapshot 只能辅助复盘，不得成为恢复依据。

## 13. 低熵规则（Low Entropy Rule）

新增内容必须满足：

- 单职责
- 最小字段
- 不重复 SoT
- 不新增解释性规则
- 不新增历史补丁规则
- 不增加 Runtime 长上下文
- 不依赖历史日志
- 不自动读取全量 Audit
- 不允许 Runtime 自修改

Runtime Internal Layer 必须保持：

- 最小上下文
- 最小字段
- 最小状态
- 最小事件类型

禁止：

- Runtime Internal Layer 自增长
- Runtime Internal Layer 形成子 Runtime
- Runtime Internal Layer 相互依赖
- Runtime Internal Layer 长期持久化扩张

Project Runtime Evidence 文件：

```text
planning-runtime/event-log.md
planning-runtime/event-summary.md
planning-runtime/decision-log.md
planning-runtime/decision-summary.md
planning-runtime/audit-log.md
planning-runtime/audit-summary.md
```

规则：

- Project Runtime Evidence 必须优先复用既有文件。

禁止新增：

- recovery-runtime/
- governance-runtime/
- entropy-runtime/
- analysis-runtime/
- debug-runtime/

新增 Runtime 内容前必须先检查：

```text
是否已有现有结构可复用？
```

优先级：

```text
复用结构
>
合并职责
>
删规则
>
新增规则
```

禁止：

```text
为了修复局部问题
新增长期 Runtime 结构
```

若某规则无法降低熵：

```text
优先删规则
优先拆职责
优先调整结构
```

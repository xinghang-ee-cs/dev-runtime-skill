# Test Runtime Core

## 核心目标

Testing Runtime 的目标是管理测试生命周期：

- 测试规划
- 自动化结果继承
- 人工测试
- 真实设备测试
- 云端验证
- 外部能力验证
- 验收管理
- Release Handoff

它不负责重新执行 long 已经完成并通过的自动化测试。

## Skill 边界

`planning-layer-runtime`：

- 截止到开发开始前。
- 负责需求、范围、数据模型、权限模型、UI、验收标准、风险、P0/P1/P2。
- 可产出 `11-测试方案与验收用例.md`，但只定义“测什么”。
- 禁止定义“怎么测、谁来测、测试顺序、测试执行状态、测试结果”。

`long-task-orchestrator`：

- 截止到 `ready_for_local_test`。
- 负责开发、重构、数据迁移、自动化测试代码编写、单元测试、业务测试、自动化执行和自动化测试结果记录。
- `vitest`、`jest`、`integration`、`api-test`、`playwright` 默认属于 long。

`testing-layer-runtime`：

- 截止到 release handoff。
- 负责汇总自动化结果、人工测试、真实设备测试、云端验证、外部能力验证、最终验收和上线前验证移交。
- 禁止重新执行 long 已完成并已通过的自动化测试。

## 输入来源

按优先级读取：

1. `testing-handoff.md`
2. `long-runtime-testing-summary.md`
3. `docs/计划安排/**/11-测试方案与验收用例.md`
4. 用户指定的用例 ID、功能范围、变更范围或验收目标

`11-测试方案与验收用例.md` 只用于识别测试范围，不得从中继承执行顺序、测试状态或测试结果。

## Long Testing Handoff

Testing Runtime 启动时必须优先读取 long 测试交接文件。Long Runtime 必须提供：

```yaml
automated_passed:
automated_failed:
automated_skipped:
manual_required:
coverage:
```

字段含义：

| 字段 | testing 处理 |
| --- | --- |
| `automated_passed` | 继承为 `reused_from_long` |
| `automated_failed` | 标记为待处理阻塞，不得用人工绕过 |
| `automated_skipped` | 判断是否需要人工、服务器或用户确认 |
| `manual_required` | 进入人工/真实设备/外部能力队列 |
| `coverage` | 用于识别未覆盖范围，不作为通过证明 |

缺失 handoff 或字段不完整时：

- 进入 Test Intake Mode。
- 报告 `long_testing_handoff_missing` 或 `long_testing_handoff_incomplete`。
- 不得通过重复执行自动化测试来替代 long handoff。

## Automated Result Reuse Rule

若同时满足：

- automated status = pass
- evidence exists
- long handoff verified

则：

- 直接继承结果。
- Runtime result 记录为 `reused_from_long`。
- evidence source 记录为 `long testing handoff`。
- 禁止重新执行。

允许重新执行条件仅限：

- 用户明确要求。
- 环境发生变化。
- 自动化证据缺失。
- 自动化失败。
- 自动化结果过期。

重新执行必须记录 `rerun_reason`，并说明该行为是例外而不是 testing 默认职责。

## Test Intake Gate

在 Test Planning Phase 前，AI 必须在 Runtime 内部确认：

```text
current_test_epoch:
writeback_target:
long_testing_handoff:
planning_test_scope:
manual_required:
server_required:
release_required:
destructive_boundary:
evidence_requirements:
```

以上清单不得作为表单要求用户填写。缺少关键信息时，通过自然语言一次只追问一个当前阻塞事实。

## Test Planning Phase

Test Intake Gate 之后必须进入 Test Planning Phase。

输入：

- `11-测试方案与验收用例.md`
- Long Testing Handoff

输出：

- `test-execution-order.md`
- 自动化已完成
- 自动化失败
- 待人工验证
- 待服务器验证
- 待上线验证

规划规则：

- 从 planning 读取“测什么”。
- 从 long handoff 读取自动化事实。
- 对 `automated_passed` 直接写入 `reused_from_long`。
- 对 `manual_required` 建立人工测试卡。
- 对服务器和 release 事项只建立验证/移交项。
- 不生成纯 UI 对照、页面截图差异或视觉验收的独立人工测试项。
- 不生成某一期的测试入口删除、测试快捷操作删除或测试专用接口删除测试项；这些只在最终上线门禁中移交。

## Manual Operation De-duplication Gate

在生成 `manual-test-queue.md` 前，Testing Runtime 必须先对人工测试候选项执行动作去重。

每个候选人工测试必须拆解为：

- `actor`：谁操作。
- `entry`：从哪个页面、入口或设备进入。
- `precondition`：执行前必须已经成立的状态。
- `operation`：用户实际要做的动作。
- `data_domain`：测试数据、正式数据、服务器数据或真实设备数据。
- `business_assertions`：该动作需要证明的业务断言。
- `evidence_need`：需要的截图、自然语言反馈、页面状态、接口状态或其他证据。

Testing Runtime 必须生成内部 `operation_signature`：

```text
actor + entry + precondition + operation + data_domain
```

规则：

- 相同 `operation_signature` 的人工测试不得生成多个独立用户操作。
- 一个 `operation_signature` 可以覆盖多个 `case_id` 和多个 `business_assertions`。
- 已验证过的 `operation_signature` 不得再次要求用户重复执行。
- 后续 case 若只缺少新的业务断言，只能复用已有证据并追问缺失观察点。
- 权限语义、错误语义、状态语义、图片边界和复用能力类 case，必须优先复用既有权限、申请、执行、图片、历史或配置证据。
- 若已有证据无法支撑新增断言，才允许创建补充人工测试；补充测试必须只验证缺失观察点，不得重复完整流程。

## test-execution-order.md

Test Planning Phase 必须生成：

```text
test-execution-order.md
```

职责：

- 管理测试顺序。
- 管理测试依赖。
- 管理阻塞关系。

格式：

```yaml
TEST-001:
  depends_on: []

TEST-002:
  depends_on:
    - TEST-001

TEST-003:
  depends_on:
    - TEST-002
```

执行规则：

- 只有 `depends_on` 全部通过，当前测试才能执行。
- 若前置失败，当前测试记录为 `blocked_by_dependency`，不得执行。
- `reused_from_long` 视为依赖已通过。
- `deferred` 不得作为当前依赖通过，除非用户明确把该范围移出当前验收边界。

## 执行矩阵

将测试范围整理为 Runtime 内部执行矩阵：

| 字段 | 要求 |
| --- | --- |
| `case_id` | 使用 planning 稳定 ID；缺失时生成临时 ID 并标记需回补 |
| `source` | planning path、long handoff 或用户请求 |
| `classification` | `reused_automation` / `manual` / `real_device` / `server` / `release_handoff` |
| `priority` | `P0` / `P1` / `P2` / `unknown` |
| `long_status` | `passed` / `failed` / `skipped` / `missing` / `not_applicable` |
| `runtime_status` | `reused_from_long` / `pending_manual` / `pending_server` / `blocked_by_dependency` / `deferred` / `verified` |
| `evidence` | long evidence、截图、人工内容、服务器验证摘要或 release handoff |
| `depends_on` | 来自 `test-execution-order.md` |
| `operation_signature` | 人工测试动作去重签名；非人工测试可为空 |
| `covers` | 当前人工动作覆盖的 case_id / assertion 列表 |
| `covered_by` | 当前 case 复用哪个人工动作或证据 |
| `evidence_reuse` | `true` / `false` |
| `writeback_status` | `pending` / `updated` / `blocked` |

执行矩阵是内部管理结构，不得要求用户填写或理解其中字段。

## Manual Guidance Strategy

Manual Guidance Strategy 必须遵循 `references/03-evidence-format.md#manual-guidance-conversation-rule`。

原则：

- 用户负责操作系统并用自然语言反馈观察结果。
- AI 负责理解用户表达、提取测试结果、判断状态、结构化写回 Runtime、维护进度。
- 不得把 `case_id`、环境、证据类型、回写状态、`Pass`、`Fail`、`Unverified` 等内部字段交给用户填写。
- 一次只引导一个下一步操作。

## Guided Manual Operation Rule

Manual Guidance Strategy 不只是说明测试任务，还必须主动引导用户完成当前下一个可执行人工操作。

Testing Runtime 必须优先使用 `manual-test-queue.md` 中 `MANUAL-OP` 的 `depends_on` 和 `blocked_by` 判断是否可执行。

可执行条件：

1. `depends_on` 全部已通过、已完成、`reused_from_long`，或已被用户明确移出当前验收范围。
2. `blocked_by` 为空。
3. `status` 未验证。
4. 未被 `covered_by` 或 `evidence_reuse` 完整覆盖。
5. 当前环境可以执行。

如果 `manual-test-queue.md` 缺失 `depends_on` 或 `blocked_by`，AI 必须回写补齐后再选择下一个人工操作，不得仅依赖跨文件推理。

用户态输出必须包含：

- 当前要测什么：用自然语言说明，不暴露内部 case 字段。
- 为什么要测：说明它要验证的业务结果。
- 操作前条件：用户需要处于哪个角色、账号、页面、数据状态。
- 具体操作步骤：用 2~6 个短步骤说明点击哪里、输入什么、提交什么、查看哪里。
- 需要观察什么：告诉用户重点看按钮、提示、列表、地图、图片、权限、状态或数据变化。
- 需要怎么反馈：允许自然语言、截图或简短反馈；不得要求用户按固定格式填写。
- 完成后的处理：AI 收到反馈后必须判断结果、回写 Runtime，并在无阻塞时主动给出下一个可执行操作。

禁止：

- 只输出 case_id 或测试标题。
- 一次要求用户执行多个独立测试操作。
- 让用户自己判断下一个该测什么。
- 让用户填写 Runtime 字段、状态枚举、Pass/Fail 表格或证据模板。

## 执行规则

- 先继承 long 自动化结果，再决定人工/服务器/release 验证。
- 人工测试必须先做 operation_signature 去重，再进入 Manual Guidance Strategy。
- 已有证据可覆盖的 case，不得再次引导用户重复操作。
- 人工测试开始后，AI 必须主动选择并引导下一个可执行人工操作。
- 选择下一个人工测试操作时，必须优先读取 `MANUAL-OP.depends_on` 和 `MANUAL-OP.blocked_by`。
- 若人工操作依赖不清，必须先补齐 Runtime 回写，再引导用户操作。
- 用户完成一个人工操作并回写成功后，若存在下一个可执行人工操作，AI 必须继续给出下一步引导；不得只停留在“已记录”或“测试通过”。
- 若下一个操作被依赖、证据、环境、破坏性确认或服务器条件阻塞，AI 必须说明阻塞原因和当前只需要用户补充的一个事实。
- 不执行依赖未通过的测试。
- 自动化失败时报告阻塞，不用人工判断掩盖失败。
- 人工测试缺少截图或描述时，先按对话规则追问；最终仍无法形成证据时，在 Runtime 内部标记证据不足。
- 服务器部署状态未确认时，不进入 Server Verification Mode。
- release 测试请求必须切换到 `ai-release-security-gate`。

## 停止条件

出现以下情况立即停止并报告：

- Long Testing Handoff 缺失且当前任务依赖 long 自动化事实。
- long 自动化失败且用户没有明确要求处理失败。
- 依赖测试未通过。
- 证据缺失且经过自然语言追问后仍无法判断。
- 需要破坏性操作但没有用户二次确认。
- 服务器目标、账号、URL、部署版本或数据范围不清楚。
- 发现安全风险、越权、数据泄露、异常流量或可被蓄意破坏的行为。
- `writeback_target` 缺失。
- Runtime 回写失败。

# Evidence Format

## 目录

- 自动化证据
- 截图与页面分析
- 业务旅程与端到端证据
- 测试项证据绑定
- Manual Guidance 与证据复用
- 阶段报告与最终报告

## 自动化证据

Testing Runtime 默认不重新执行 long-owned 自动化测试。继承 long 自动化结果时必须包含：

```text
功能/用例：
自动化验证：已继承
来源：long testing handoff
status：reused_from_long
evidence_refs：
writeback_status：updated
无需重复执行：是
```

只有满足允许重新执行条件时，自动化重跑报告才必须包含：

```text
命令：
工作目录：
开始时间：
目标用例：
关键输出摘要：
退出码：
结果：
证据文件：
跳过项：
```

不要粘贴超长日志；保留失败断言、错误栈关键行、截图路径、trace 路径或测试报告路径。继承 long 结果时只引用 long evidence，不复制完整日志。

## 截图与页面分析

本地或服务器页面测试必须说明：

```text
页面/URL：
视口/设备：
PAGE / UI-MOD contract revision：
UX-SCN revision：
对照 ASSET-ID@revision：
登录状态：
操作路径：
截图路径：
可见内容：
交互反馈：
业务断言：
布局与遮挡：
异常提示：
结论：
```

截图只能证明可见状态，不能单独证明业务流程通过。必须结合数据、接口响应、状态变化或人工内容。

截图证据必须服务业务、交互或已确认的前端合同断言。不得生成脱离 Planning TEST、PAGE/UX-SCN/ASSET revision 的模糊“对照 UI 图”卡；Long 明确移交且 Planning 已定义的视觉一致性、真机响应式、复杂 UX 或可访问性观察项可以生成独立人工项，但必须写明设备/视口、进入路径、操作、预期可见状态、对照 revision、允许差异与通过条件。

## 业务旅程与端到端证据

每条关闭 FLOW requirement 的证据必须说明：

```text
FLOW / TEST 引用：
环境：local | deployed
environment_revision_ref：
合法业务入口：
角色 / 账号 / 租户：
前置业务事实：
真实业务动作：
关键中间断言：
可观察终态：
反向或恢复分支（适用时）：
结果记录引用：
证据索引引用：
```

规则：

- 本地证据优先引用 Long Handoff 中与同一 FLOW/TEST 对应的有效业务或 E2E validation id；单元、组件、接口片段、类型检查或构建证据只能补充，不能单独关闭旅程。
- 本地 required FLOW 的 evidence revision 必须匹配当前 Long readiness receipt 冻结的 repository revision，且 `path` 解析到真实非空持久化文件；只写 `passed`、虚构 revision 或不存在的路径不得关闭旅程。
- 云端结果必须通过 `environment_revision_ref` 引用 `test-runtime-state.md#current_deployment_revision`；证据索引中的目标环境、部署/组件 revision 与 `runtime_configuration_identity` 必须精确匹配。代码或镜像不变但运行配置身份变化时，旧证据仍然失效。只有 URL 可访问、进程健康或单接口成功不能替代从业务入口到终态的证明。
- 同一证据可以覆盖多个明确断言，但 `business-journey-test-matrix.md` 中每个 FLOW 仍须分别引用；不得用“整体测试通过”覆盖未映射旅程。
- Planning/Long 合同或本地代码 revision 变化后，按真实影响标记本地证据失效。部署身份变化必须执行 `05-test-writeback.md#deployment-revision-reconciliation-gate`；历史证据保留用于闭环追踪，但只有当前完整部署身份的 new attempt/new evidence 才能关闭 required 云端旅程。

## 证据与测试项绑定规则

`05-test-writeback.md` 唯一枚举的每个正式 `item_type` 都必须独立关联证据或明确的证据缺失原因；本文件不复制另一份类型清单。

### 证据最低要求

根据测试项类型和状态，证据最低要求如下：

| 状态 | 证据最低要求 |
| --- | --- |
| `reused_from_long` | `source_validation_id` + Long readiness receipt 证据索引 |
| `verified` | 至少一个证据引用 |
| `verified_by_user_report` | 用户自然语言反馈或截图 |
| `failed` | 失败描述 + 相关截图或日志 |
| `blocked` | 阻塞原因描述 |
| `blocked_by_dependency` | 具体阻塞的依赖项 ID |
| `evidence_insufficient` | 缺失证据描述 + 已具备证据引用 |
| `interrupted_pending_reconcile` | 中断时已有证据引用（如有） |
| `deferred` | 延期原因描述 |

### 证据索引关联

`test-evidence-index.md` 中的每个证据必须关联到具体 `item_id`，并采用 `05-test-writeback.md#test-evidence-indexmd-格式` 的唯一 schema。每个持久文件必须记录 `content_sha256`，由校验器重算后完全匹配。业务旅程 result 的 `covers` 必须包含对应 Planning TEST，证据 `flow_refs` 必须包含被关闭 FLOW。云端证据必须包含目标环境、revision kind、精确 revision、FLOW 引用、有效性和失效来源；本地证据必须绑定可重建的本地代码/公开配置 revision。

不允许存在无法关联到 `item_id` 的游离证据条目。

### 证据缺失处理

若测试项缺少必要证据：

1. AI 必须追问缺失观察点，只问一个当前缺失事实。
2. 用户提供后，立即更新 `test-evidence-index.md` 和 `test-validation-results.md`。
3. 若用户无法提供，则将该测试项标记为 `evidence_insufficient`。
4. `evidence_insufficient` 不得静默跳过，必须在 `test-validation-results.md` 中记录 `evidence_missing_reason`。
5. 最终报告中必须明确列出 `evidence_insufficient` 项。

### 证据复用记录

复用已有证据覆盖多个测试项时，每个被覆盖的测试项必须独立记录：

```yaml
# test-validation-results.md 中 TEST-P7-PERM-001 的记录
item_id: TEST-P7-PERM-001
status: verified_by_user_report
evidence_reuse: true
covered_by:
  - MANUAL-OP-001
evidence_missing_reason: null
```

若复用证据但缺少某个特定断言，只补记录缺失观察点：

```yaml
item_id: TEST-P7-PERM-001
status: evidence_insufficient
evidence_reuse: true
covered_by:
  - MANUAL-OP-001
evidence_missing_reason: 非组长页面是否没有提交入口
```

## Manual Guidance Conversation Rule

Manual Guidance Strategy 默认采用 Conversation Driven Testing，禁止采用 Form Driven Testing。

原则：

- 一次只验证一个下一步操作。
- 用户允许自然表达。
- AI 负责理解、追问、结构化和回写。
- Runtime 状态默认隐藏。
- 优先截图，缺失时柔性补证。

## User-Facing Manual Operation Format

当需要用户执行人工测试时，输出必须使用自然语言引导，并包含以下内容：

```text
现在测试：
目的：
操作前确认：
请这样做：
1.
2.
3.
重点观察：
完成后你可以这样反馈：
```

规则：

- `现在测试` 只写用户能理解的业务名称，不写内部 case_id。
- `目的` 只说明本次操作要证明的业务结果。
- `操作前确认` 只写必要条件，例如账号角色、页面入口、是否已有测试数据。
- `请这样做` 必须是可执行步骤，不得只写”测试某功能”。
- `重点观察` 必须告诉用户看什么现象。
- `完成后你可以这样反馈` 必须允许自然语言，例如”这里OK了””按钮还是能点””截图如下”。
- 如果用户已经提供截图或反馈，AI 必须先判断是否足够；足够则回写并主动给出下一个测试操作，不足则只追问一个缺失观察点。

## Manual Evidence Reuse Rule

人工证据可以被多个 case 复用。

若用户已经完成过同一 `operation_signature` 对应的操作，Testing Runtime 不得再次要求用户重复该操作。

若新 case 只缺少某个业务断言，AI 只能基于已有证据追问缺失观察点，例如：

- “刚才提交后按钮是否已经不可点击？”
- “刚才非组长页面是否没有提交入口？”
- “刚才图片详情是否只对本人可见？”
- “刚才错误提示是否表达为权限不足，而不是系统异常？”

不得要求用户重新走完整申请、审批、执行、上传、查看或配置流程。

当复用证据时，Runtime 内部必须记录：

```yaml
evidence_reuse: true
covered_by:
evidence_missing_reason:
```

用户态报告中只说明”这个点复用前面已确认的流程，只补一个观察点”，不要暴露内部字段。

## 阶段报告

每个测试环境结束后向用户输出自然语言摘要：

```text
当前测试环境：
测试来源：
执行范围：
自动化覆盖：
人工引导：
破坏性边界：
已执行：
证据：
结果：通过 / 未通过 / 阻塞 / 证据不足
问题与风险：
下一步：
等待确认：
```

默认不得在用户态报告中暴露 Runtime 内部字段。它们只写回 Runtime 文档；用户主动要求查看时才输出。

## 最终报告

最终报告面向用户必须包含：

```text
测试范围：
规划来源：
Long Testing Handoff：
Long Required Validation Gate：
最终结果：
本地业务/E2E 覆盖：
部署后云端业务/E2E 覆盖：
已继承自动化通过：
已自动化通过：
已人工确认：
服务器已验证：
上线门禁状态：
未覆盖项：
证据不足项：
失败项：
未闭环 finding：
破坏性操作记录：
reused_from_long：
剩余风险：
建议下一步：
```

Runtime 内部必须继续判断 `Long Runtime Completion Verified`，取值只能是：

- `verified`
- `not_verified`

只有 Long Handoff 的 `required_validation_gate.result: passed`、matrix revision 与 effective validation ids 均可解析且有效时，才允许 `Long Runtime Completion Verified: verified`。

Runtime 还必须判断 `Business Journey Coverage Verified`，取值只能是：

- `verified`
- `not_verified`

只有 `business-journey-test-matrix.md` 中每个 required P0/P1 FLOW 的本地业务/E2E、合同定义的必需反向分支和 finding 闭环都满足，并且本期部署适用时全部 P0 正向旅程、部署敏感或受变更影响的 P1 FLOW 已在 `test-runtime-state.md#current_deployment_revision` 指向的完整部署身份上闭合，才允许为 `verified`。

若 `Long Runtime Completion Verified` 为 `not_verified`：

- 最终结果：`Blocked`
- 不得进入 `Server Verification`
- 不得进入 `Release Handoff`

若 `Business Journey Coverage Verified` 为 `not_verified`：

- 最终结果：`Blocked`
- 必须列出精确 FLOW、缺失环境证据或未闭环 finding
- 不得以测试数量、服务器 smoke 或部分用例通过替代

若 `writeback_status` != `updated`：

- 最终结果：`Blocked`

以上 gate 和 writeback 字段默认不暴露给用户，只影响最终结论和 Runtime 回写。

`上线门禁状态` 只能是：

- `not_requested`
- `handoff_required`
- `handoff_ready`
- `handled_by_release_security_gate`

不得在本 Skill 中写 `release_pass`。

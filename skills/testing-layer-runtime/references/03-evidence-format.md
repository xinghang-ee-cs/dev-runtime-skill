# Evidence Format

## 自动化证据

Testing Runtime 默认不重新执行 long-owned 自动化测试。继承 long 自动化结果时必须包含：

```text
功能/用例：
自动化验证：已继承
来源：long testing handoff
long evidence：
runtime result：reused_from_long
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

截图证据只能服务业务断言；不得为了“对照 UI 图”或“页面差异记录”单独生成一张人工测试卡。

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
- `请这样做` 必须是可执行步骤，不得只写“测试某功能”。
- `重点观察` 必须告诉用户看什么现象。
- `完成后你可以这样反馈` 必须允许自然语言，例如“这里OK了”“按钮还是能点”“截图如下”。
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
reuse_reason:
missing_observation:
```

用户态报告中只说明“这个点复用前面已确认的流程，只补一个观察点”，不要暴露内部字段。

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
最终结果：
已继承自动化通过：
已自动化通过：
已人工确认：
服务器已验证：
上线门禁状态：
未覆盖项：
证据不足项：
失败项：
破坏性操作记录：
reused_from_long：
剩余风险：
建议下一步：
```

Runtime 内部必须继续判断 `Long Runtime Completion Verified`，取值只能是：

- `verified`
- `not_verified`

若 `Long Runtime Completion Verified` 为 `not_verified`：

- 最终结果：`Blocked`
- 不得进入 `Server Verification`
- 不得进入 `Release Handoff`

若 `writeback_status` != `updated`：

- 最终结果：`Blocked`

以上 gate 和 writeback 字段默认不暴露给用户，只影响最终结论和 Runtime 回写。

`上线门禁状态` 只能是：

- `not_requested`
- `handoff_required`
- `handoff_ready`
- `handled_by_ai-release-security-gate`

不得在本 Skill 中写 `release_pass`。

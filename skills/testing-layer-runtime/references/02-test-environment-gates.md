# Test Environment Gates

## 环境切换 Writeback Gate

在不同测试环境之间切换时（如从本地人工测试切换到服务器验证），必须满足以下条件后方可切换：

1. 当前环境中所有测试项的 `writeback_status = updated`。
2. 当前环境中无 `in_progress` 或 `interrupted_pending_reconcile` 的测试项。
3. `test-runtime-state.md` 已更新 `current_phase`、`current_environment`、`current_item`、`next_executable_item`。
4. `test-execution-events.md` 已记录环境切换事件。

不允许在仍有未回写完成的测试项时切换环境。

## 1. 自动化结果继承

目标：

- 从 Long Testing Handoff 汇总自动化结果。
- 继承 long 已通过且有证据的结果。
- 标记失败、跳过、缺证据和需人工验证的范围。

默认归属 long 的测试：

```text
vitest
jest
integration
api-test
playwright
```

Testing Runtime 禁止默认重新执行上述测试。

继承要求：

- `automated_passed` + evidence exists + handoff verified -> `reused_from_long`。
- `automated_failed` -> 对应自动化 case 的 `status: failed`，依赖该项的后续测试标记为 `blocked_by_dependency`；不得以人工测试覆盖。
- `automated_skipped` -> 判断为 `manual_required`、`server_required`、`release_required` 或 `coverage_gap`。
- `coverage` 只能证明覆盖范围，不能单独证明验收通过。

允许重新执行条件：

- 用户明确要求。
- 环境发生变化。
- 自动化证据缺失。
- 自动化失败。
- 自动化结果过期。

重新执行时必须记录：

```yaml
rerun_reason:
requested_by:
scope:
command:
result_summary:
evidence_refs:
```

## 2. 本地人工与真实设备测试

目标：

- 验证 long 无法证明的真实设备、真实外部能力、现场授权弹窗、麦克风、定位、扫码、拍照、用户实际操作和业务可见状态。
- 完成最终验收中的人工证据闭环。

执行要求：

- 只执行 `manual_required` 或 Test Planning Phase 判定必须人工确认的范围。
- 不把人工测试变成自动化回归重跑。
- 不生成纯 UI 图对照、页面截图差异或视觉验收的独立人工测试项。
- 页面状态只作为业务断言的附属证据。
- 启动本地服务前说明端口和命令；结束前关闭由本流程启动的服务。
- 如果服务由用户启动，结束时提醒用户自行关闭。

人工流程：

- Manual Guidance Strategy 必须采用 Conversation Driven Testing。
- 一次只引导一个下一步操作。
- 禁止一次输出多项验证要求或强格式回传模板。
- 用户可以用自然语言、截图、简短反馈或非专业描述表达结果。
- AI 必须把用户反馈结构化为 Runtime 证据和验证状态。

## 3. 服务器环境测试

目标：

- 在部署完成后验证 long 和本地人工测试无法证明的真实运行条件。
- 包括服务器构建产物、nginx 代理、systemd 服务、生产环境变量、真实外部能力、真实回调、云端资源和数据库链路。

前置条件：

以下为 AI 内部确认清单，不得作为表单要求用户一次性填写。缺失项通过自然语言逐项确认。

```text
提交已完成：
部署已完成：
部署分支/提交：
目标 URL：
登录/测试账号：
服务器数据范围：
外部能力账号或开关：
允许的破坏性范围：
```

执行要求：

- 必要部署事实未确认前，不进入服务器测试。
- 先检查部署工作流和 long handoff，判断哪些已经被 long 或 CI/CD 覆盖。
- 不把本地单测、集成测试、api-test、Playwright 或普通本地交互测试重复搬到服务器阶段。
- 服务器阶段只验证云端独有事实。
- 人工验证为主；能通过安全、只读、低侵入命令验证的事项再自动化。

## 4. 上线测试与 Release Handoff

目标：

- 为完整上线、发布放行、压力测试、安全测试和鲁棒性验证提供移交。
- 本 Skill 不执行上线门禁，只进入 Release Handoff Mode。

移交要求：

- 汇总 `reused_from_long` 自动化结果。
- 汇总人工、真实设备、外部能力和服务器验证结果。
- 标出 P0/P1 未覆盖项、证据不足项、服务器待确认项和已知风险。
- 明确要求切换到项目定义的发布/安全流程或可选 release/security skill。
- 测试入口、测试快捷操作、测试专用接口删除只在最终上线/发布门禁中处理，不进入某一期独立测试矩阵。

禁止：

- 禁止任何破坏性上线测试。
- 禁止未经授权的压测、安全扫描、漏洞利用、数据篡改、账号枚举或绕过权限尝试。
- 禁止把上线测试结论建立在本地测试或服务器冒烟测试之上。

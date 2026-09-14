# Test Environment Gates

## 目录

- 环境切换 Writeback Gate
- 1. 自动化结果继承
- 2. 本地人工与真实设备测试
- 3. 部署后云端业务与端到端测试
- 4. 上线测试与 Release Handoff

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

- Long Handoff `required_validation_gate.result: passed`，matrix revision 与 effective validation ids 可解析且未过期；否则 Test Intake 阻断，不进入继承。
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

## 3. 部署后云端业务与端到端测试

目标：

- 在部署完成后，对精确部署 revision 验证本地无法证明或可能因部署差异改变结果的完整业务旅程。
- 覆盖反向代理、域名/CORS、云端秘密注入、进程/容器运行方式、云数据库/对象存储、跨服务网络、真实回调、外部能力和权限边界对 FLOW 的实际影响。
- 服务器、容器或云资源 smoke 只作为前置证据；最终仍必须从真实业务入口走到 Planning 定义的可观察终态。

前置条件：

以下为 AI 内部确认清单，不得作为表单要求用户一次性填写。缺失项通过自然语言逐项确认。

```text
提交已完成：
部署已完成：
部署分支/提交：
构建或部署 revision：
目标 URL：
登录/测试账号：
服务器数据范围：
外部能力账号或开关：
before_cloud_test 依赖状态：
允许的破坏性范围：
```

执行要求：

- 必要部署事实未确认前，不进入服务器测试。
- `current_deployment_revision` 必须表达当前完整部署身份；多服务独立发布时使用 component set，不得只绑定其中一个服务。完整身份还必须包含 `runtime_configuration_identity`，覆盖脱敏公开配置、路由/代理、域名/CORS、基础设施绑定和秘密版本绑定；不得以代码或镜像未变化为由复用配置变化前的证据。`deployment_revision_reconciliation.status` 必须不为 `in_progress | blocked`。
- Planning Handoff `execution_prerequisite_readiness.before_cloud_test_dependency_refs` 指向的每个 DEP 都必须在 `test-validation-results.md` 拥有 `item_type: environment_prerequisite` 的正式结果；只有该结果为 `verified | verified_by_user_report` 且证据对当前环境有效时才算就绪。未就绪时只阻断 DEP `blocking_scope` 命中的 FLOW，不猜测配置成功，也不回写 Planning 12。
- 需要用户补配置时，按 `01-test-runtime-core.md#environment-prerequisite-result-lifecycle` 一次引导一个安全动作并立即回写结果；只说明用途、已核实入口、短步骤和脱敏验证，不接收秘密值。
- 先检查部署工作流和 long handoff，判断哪些已经被 long 或 CI/CD 覆盖。
- 先执行安全、只读、低侵入的入口与依赖 smoke；smoke 失败时停止依赖它的业务旅程并记录明确阻断。
- 本期包含云端部署时，执行 `business-journey-test-matrix.md` 中全部 P0 正向业务旅程，以及标记为部署敏感、受当前 revision 影响或本地证据无法证明的 P1 云端业务/E2E；不把整套本地单测、集成测试、api-test、Playwright 或普通交互测试机械搬到云端。
- CI/CD 已针对同一精确部署 revision 产生完整业务/E2E 证据时可以继承；只有 smoke、零散接口结果或其他 revision 的结果时不能冒充业务旅程通过。
- 优先使用隔离测试租户、测试账号和可清理测试数据。人工验证与安全自动化都必须遵守相同 FLOW、前置、断言和证据要求。
- 云端发现失败后先执行 Change Triage；implementation defect 回 Long patch，test/environment defect 在 Testing 获准范围修正，planning gap/requirement change/design drift 回 Planning。修复版本重新部署后，本地证据按真实影响精确失效；云端 required 旅程按下一条规则处理。
- 部署身份改变时必须完整执行 `05-test-writeback.md#deployment-revision-reconciliation-gate`；本文件只触发该 Gate，不复制证据失效、矩阵重算或恢复顺序。

## 4. 上线测试与 Release Handoff

目标：

- 为完整上线、发布放行、压力测试、安全测试和鲁棒性验证提供移交。
- 本 Skill 不执行上线门禁，只进入 Release Handoff Mode。

移交要求：

- 汇总 `reused_from_long` 自动化结果。
- 汇总人工、真实设备、外部能力和服务器验证结果。
- 标出 P0/P1 未覆盖项、证据不足项、服务器待确认项和已知风险。
- 读取 Planning Handoff 的每个 `before_release_dependency_refs`，确保其在 `test-validation-results.md` 有 `environment_prerequisite` 结果项，并按 `05-test-writeback.md#release-handoffmd-格式` 将 DEP 引用、Planning 快照、Testing 结果引用、证据、owner、阻断范围和 `release_gate_owner` 写入 `release-handoff.md`。
- 未就绪或证据无效的发布前 DEP 必须进入 `unresolved_dependency_refs`；Testing 只移交快照，后续实际状态由项目发布/安全流程维护，不反向覆盖 Planning 12。
- 明确要求切换到项目定义的发布/安全流程或可选 release/security skill。
- 测试入口、测试快捷操作、测试专用接口删除只在最终上线/发布门禁中处理，不进入某一期独立测试矩阵。

禁止：

- 禁止任何破坏性上线测试。
- 禁止未经授权的压测、安全扫描、漏洞利用、数据篡改、账号枚举或绕过权限尝试。
- 禁止把上线测试结论建立在本地测试或服务器冒烟测试之上。

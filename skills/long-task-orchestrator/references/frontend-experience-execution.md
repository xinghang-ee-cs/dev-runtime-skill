# Frontend Experience Execution

本文件是 Long 对 Planning UI/UX 执行合同的消费与合规规则。任一允许执行 TASK 涉及正式页面、用户可见交互、响应式行为、视觉资产或前端体验变化时必须读取。

## 目录

- 1–3：权威链、Frontend Contract Intake 与 Runtime Snapshot
- 4–6：TASK 绑定、实现规则与 Design Drift 停止条件
- 7–8：前端合同验证与 Testing Handoff

## 1. Authority Chain

```text
Planning Handoff.frontend_experience_binding
-> UI/UX Design 真实路径
-> design_delivery_manifest
-> PAGE / UI-MOD / UX-SCN contract revision
-> visual_confirmed ASSET revision
-> 13 frontend_contract_binding
-> TEST refs
```

Handoff 是允许消费范围入口；05 是 Prompt、页面/模块实现合同、UX 状态迁移和资产索引正文；13 是 TASK 级绑定；11 是验证目标。聊天记录、目录中的最新图片、未确认 Figma frame、代码现状或模型偏好不能覆盖该链路。

## 2. Frontend Contract Intake Gate

Long Planning Handoff Intake 中存在 UI TASK 时必须按顺序执行：

```text
confirm frontend_experience_binding.applicable = true
-> resolve design_document_path and UI/UX Design role path
-> confirm both paths are identical and readable
-> resolve design_manifest_ref
-> confirm design_contract_version = ui-ux-execution/v1
-> confirm design_delivery_manifest.execution_readiness = execution_ready
-> resolve all Prompt / PAGE / UI-MOD / UX-SCN IDs and revisions
-> resolve every ASSET-ID@revision and real path or external reference
-> confirm every required asset status = visual_confirmed
-> resolve consistency TEST refs
-> compare 05 Manifest, 13 TASK binding and Handoff
-> run planning validator or equivalent structural checks
-> mark frontend_contract_intake_status = passed
```

任一失败：

```text
frontend_contract_intake_status = blocked
-> STOP
-> DO_NOT_CREATE_UI_RUNTIME_TASK
-> REPORT_HANDOFF_INCOMPLETE_OR_DESIGN_DRIFT
-> WRITE_BACK_TO_PLANNING
```

不得自动选择更高 revision。发现目录中存在新图但 Handoff 未绑定时，只报告存在未准入 revision，不得使用。

## 3. Runtime Snapshot

`current-runtime-context.md` 只保存消费指针和校验状态：

```yaml
frontend_experience_binding_source: <Planning Handoff path>#frontend_experience_binding
frontend_contract_intake_status: <passed | blocked | not_applicable | invalidated>
frontend_execution_snapshot:
  design_document_path: <05 真实路径>
  design_contract_version: ui-ux-execution/v1
  design_manifest_ref: <05 path>#design-delivery-manifest
  prompt_refs: [<PROMPT-ID@revision>]
  page_contract_refs: [<PAGE-ID@revision>]
  module_contract_refs: [<UI-MOD-ID@revision>]
  interaction_contract_refs: [<UX-SCN-ID@revision>]
  confirmed_asset_refs: [<ASSET-ID@revision>]
  consistency_test_refs: [<TEST-ID>]
```

Runtime 不复制 Prompt 正文、页面合同、状态迁移表或图片内容。任一上游 revision 变化时 snapshot 失效，并按 Planning 新 Handoff 精确失效受影响 TASK。

## 4. Per-Task Frontend Binding Gate

每个 UI Runtime Task 的 Static Task Definition 必须包含：

```yaml
frontend_contract_binding_source: <13 TASK anchor>
design_document_path: <05 真实路径>
prompt_refs: [<PROMPT-ID@revision>]
page_contract_refs: [<PAGE-ID@revision>]
module_contract_refs: [<UI-MOD-ID@revision>]
interaction_contract_refs: [<UX-SCN-ID@revision>]
confirmed_asset_refs: [<ASSET-ID@revision>]
consistency_test_refs: [<TEST-ID>]
frontend_contract_status: <passed | blocked | not_applicable>
```

开始实现前逐项确认：

- TASK 引用只来自 Handoff 允许范围。
- Prompt、PAGE/UI-MOD、UX-SCN 与 ASSET revision 能在 05 解析。
- PAGE/UI-MOD 合同覆盖 design token、布局、响应式、组件、状态、内容、无障碍、动效反馈和实现断言。
- UX-SCN 状态表覆盖 trigger、pending、success、failure、retry、cancel、back 和 forbidden actions。
- 当前现有组件和技术约束能在禁止重定义与允许扩展范围内实现。

缺少任一项时当前 TASK `BLOCKED`；不得以“按设计实现”或复制 Handoff 顶层字段替代 TASK 级绑定。

## 5. Implementation Rules

Long 必须：

- 优先复用 `required_existing_components` 和项目已有 design token。
- 按 UI Implementation Contract 实现区域顺序、布局、尺寸、响应式适配、组件 variant、状态、内容长度、校验提示、焦点、键盘顺序、可访问名称和动效反馈。
- 按 UX Interaction Contract 实现每个 trigger 与状态迁移，并使 pending、失败恢复、取消、返回和禁止动作可观察、可测试。
- 只在 `allowed_extensions` 内增加用户可见内容；严格遵守 `prohibited_redefinitions`。
- 把 Planning ID 仅用于追踪，继续使用稳定业务命名。

Long 可以自主决定不改变可见行为、合同、资产匹配或验收结果的私有实现细节；必须遵守既有架构和显式委托边界。

Long 不得：

- 凭审美偏好重排页面、改色、改字号、替换组件或省略状态。
- 看到新资产后自动升级 revision。
- 因技术实现困难删减 error、empty、blocked、retry、cancel、back 或 accessibility 行为。
- 用截图近似匹配掩盖结构、状态、权限或交互合同偏差。

## 6. Design Drift Stop Rule

以下任一情况立即停止当前 UI TASK：

- 05 合同与确认资产互相矛盾。
- 现有组件无法在禁止重定义范围内实现合同。
- 页面布局、内容长度、响应式、状态或交互存在阻断性缺口。
- 实现需要新增未经确认的用户动作、权限、状态、API 或视觉体系。
- 已确认资产不可读取、revision 不匹配或被 superseded。
- 自动化验证证明实现偏离合同且无法在当前范围内修复。

按现有 Change Triage 分类为 `design_drift` 或 `planning_gap`，写明冲突的 PAGE/UX-SCN/ASSET revision 和受影响 TASK，等待新的有效 Handoff。禁止本地修改 05、13 或 Handoff。

## 7. Frontend Contract Validation

每个 UI TASK 完成前必须记录：

```yaml
frontend_contract_validation:
  design_document_path:
  design_manifest_ref:
  validated_prompt_refs: []
  validated_page_contract_refs: []
  validated_module_contract_refs: []
  validated_interaction_contract_refs: []
  validated_asset_refs: []
  structural_assertions: <passed | failed | not_applicable>
  responsive_assertions: <passed | failed | not_applicable>
  state_assertions: <passed | failed | not_applicable>
  interaction_assertions: <passed | failed | not_applicable>
  accessibility_assertions: <passed | failed | not_applicable>
  visual_comparison: <passed | failed | manual_required | not_applicable>
  evidence: []
  manual_required: []
  result: <passed | failed>
```

自动化优先级：

1. 结构、组件、主操作数量和隐藏/禁用规则。
2. default/loading/empty/error/success/blocked 状态。
3. trigger/pending/success/failure/retry/cancel/back 与重复提交保护。
4. 目标视口和 breakpoint 的布局、溢出与内容长度。
5. 键盘、焦点、accessible name 与非颜色提示。
6. 项目已有截图/视觉回归能力下的 `ASSET-ID@revision` 对照。

技术上无法自动化的纯视觉、真机布局或复杂体验必须进入 `manual_required`，包含 PAGE/UX-SCN/ASSET revision、设备/视口、进入路径、操作、预期可见状态和通过条件。`manual_required` 不等于 Long 已验证通过。

```text
tests_passed_but_frontend_contract_validation_failed -> TASK_NOT_DONE
asset_revision_mismatch -> TASK_NOT_DONE
visual_comparison_unavailable_without_manual_required -> TASK_NOT_DONE
```

## 8. Testing Handoff

Long Testing Handoff 必须增加：

```yaml
frontend_contract_validation_summary:
  applicable: true
  design_document_path: <05 真实路径>
  design_manifest_ref: <精确引用>
  validated_contract_refs: []
  validated_asset_refs: []
  automated_evidence_refs: []
  manual_required: []
  unresolved_mismatch: []
```

存在 `unresolved_mismatch` 时不得进入 `ready_for_local_test`；不可自动化但范围明确的项目进入 Testing 人工队列，不得标记自动化通过。

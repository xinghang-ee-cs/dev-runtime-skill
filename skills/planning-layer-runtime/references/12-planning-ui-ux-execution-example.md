# UI/UX Execution Contract 完整结构示例

本文件只演示 execution-ready 05 的完整结构和引用关系，不代表真实项目事实。示例中的项目路径、设计资产和确认记录是教学值；实际 Planning 必须替换为目标项目中可回读的真实路径、revision 与证据。

## 目录

- 文档边界、前端体验继承判断与执行交付清单
- 可复制的 PAGE / UX Prompt
- PAGE UI Implementation Contract
- UX 确定性状态迁移表
- 版本化设计资产、覆盖矩阵与 Handoff 绑定

## 文档边界

- 示例场景：用户检查个人资料并确认提交。
- 上游事实：只演示引用，不在本文件重新定义。
- 目标：展示 Prompt、页面合同、UX 状态表、资产、TEST 与 Handoff 的精确绑定。

## 前端体验继承判断

```yaml
style_inheritance_decision:
  mode: inherit_current
  baseline_source: docs/product/PROJECT-CURRENT-BASELINE.md#frontend-experience
  inherited_scope:
    - global-navigation
    - neutral-color-tokens
    - form-components
  changed_scope:
    - profile-review-page
  change_reason: 新增资料确认页面，不改变全局视觉体系
  affected_assets:
    - ASSET-PROFILE-PAGE-001@asset-r3
    - ASSET-PROFILE-UX-001@asset-r2
  user_confirmation: CONFIRM-UI-20260822-01
```

## UI/UX 执行交付清单

```yaml
design_delivery_manifest:
  contract_version: ui-ux-execution/v1
  design_document_path: docs/planning/phase-profile/05-前端页面与UI-UX交互设计.md
  style_mode: inherit_current
  baseline_source: docs/product/PROJECT-CURRENT-BASELINE.md#frontend-experience
  prompt_refs:
    - id: PROMPT-PAGE-PROFILE-001
      revision: prompt-r2
      anchor: '#prompt-page-profile-001资料确认页'
    - id: PROMPT-UX-PROFILE-001
      revision: prompt-r1
      anchor: '#prompt-ux-profile-001提交与失败恢复'
  page_contract_refs:
    - id: PAGE-PROFILE-001
      revision: page-r4
      anchor: '#page-profile-001资料确认页'
  module_contract_refs: []
  interaction_contract_refs:
    - id: UX-SCN-PROFILE-001
      revision: ux-r3
      anchor: '#ux-scn-profile-001提交与失败恢复'
  confirmed_asset_refs:
    - id: ASSET-PROFILE-PAGE-001
      revision: asset-r3
      path_or_url: docs/planning/phase-profile/assets/profile-review-page-r3.png
    - id: ASSET-PROFILE-UX-001
      revision: asset-r2
      path_or_url: docs/planning/phase-profile/assets/profile-submit-flow-r2.png
  consistency_test_refs:
    - TEST-PROFILE-UI-001
    - TEST-PROFILE-UX-001
  unresolved_design_refs: []
  execution_readiness: execution_ready
```

## 可复制设计提示词

### PROMPT-PAGE-PROFILE-001：资料确认页

```yaml
prompt_revision: prompt-r2
prompt_type: page
target_tool: tool_agnostic
language: 简体中文
reference_inputs:
  - id: FRONTEND-BASELINE
    revision: baseline-r7
    path_or_url: docs/product/PROJECT-CURRENT-BASELINE.md#frontend-experience
output_spec:
  device: responsive
  viewport: 1440x900 and 390x844
  frame_count: 2
  aspect_ratio: 16:10 and 390:844
  resolution: 1440x900 and 1170x2532
required_constraints:
  - 复用现有顶部导航、表单行、主按钮和提示条组件
  - 桌面端内容区最大宽度 960px，移动端左右边距 16px
  - 默认状态只有“确认提交”一个主操作
  - 展示默认、提交中、失败和成功后的可见反馈
negative_constraints:
  - 不新增侧边导航
  - 不改变品牌色、全局圆角或字体体系
  - 不新增编辑、审批、代提交或跳过确认动作
  - 不使用旧资料审批语义
```

prompt_body:

```prompt
为一个简体中文的响应式业务系统生成“资料确认页”完整页面设计，分别输出 1440×900 桌面帧和 390×844 移动帧。严格继承所给 FRONTEND-BASELINE 的顶部导航、字体、灰阶、品牌主色、表单行、按钮、提示条、间距和圆角；不要重新设计全局导航或主题。

页面从上到下包含：返回入口、标题“确认个人资料”、一句说明、只读资料分组（姓名、证件类型、联系方式、常用地址）、信息使用说明、确认勾选项、操作区。桌面端内容区最大宽度 960px 并居中，移动端左右边距 16px；资料分组保持清晰标签和值层级，长地址允许换行，不截断关键信息。

默认状态只有“确认提交”一个主按钮，“返回修改”为次级文本操作；未勾选确认项时主按钮禁用并提供非颜色提示。提交中保持页面结构不跳动，主按钮显示进度并禁止重复提交；失败时在操作区上方显示可聚焦的错误提示，保留输入状态，提供“重新提交”和“返回修改”；成功后显示明确成功反馈并只提供“返回工作台”。同时表现键盘焦点顺序、可访问名称和非颜色状态提示。

禁止新增编辑表单、审批、代提交、跳过确认、旧资料流程入口、侧边导航或额外业务动作。输出完整页面，不要只输出卡片或组件集合。
```

### PROMPT-UX-PROFILE-001：提交与失败恢复

```yaml
prompt_revision: prompt-r1
prompt_type: ux
target_tool: tool_agnostic
language: 简体中文
reference_inputs:
  - id: ASSET-PROFILE-PAGE-001
    revision: asset-r3
    path_or_url: docs/planning/phase-profile/assets/profile-review-page-r3.png
output_spec:
  device: responsive
  viewport: 1440x900
  frame_count: 4
  aspect_ratio: 16:10
  resolution: 1440x900 per frame
required_constraints:
  - 依次展示默认、提交中、失败、重试成功四帧
  - 每帧标注触发动作、可见变化和当前可用动作
  - 所有帧复用确认页面 asset-r3
negative_constraints:
  - 不重新设计页面布局和视觉风格
  - 不增加确认弹窗、审批或代提交路径
  - 不省略失败后的重试和返回修改
```

prompt_body:

```prompt
基于 ASSET-PROFILE-PAGE-001 asset-r3 生成四帧交互设计图，不重新设计页面。帧 1 为默认状态：确认项已勾选，“确认提交”可用；帧 2 为点击后的提交中状态：按钮显示进度，重复提交、返回修改和返回入口暂时禁用，页面结构不位移；帧 3 为网络失败状态：焦点进入操作区上方错误提示，资料与确认项保持，显示“重新提交”和“返回修改”；帧 4 为重新提交成功状态：显示成功反馈，只保留“返回工作台”。使用箭头连接四帧，并在每帧旁标注 Trigger、Visible change、Allowed actions、Forbidden actions。输出 1440×900 四帧画板。
```

## 页面实现合同

### PAGE-PROFILE-001：资料确认页

```yaml
contract_revision: page-r4
source_prompt_refs:
  - id: PROMPT-PAGE-PROFILE-001
    revision: prompt-r2
source_asset_refs:
  - id: ASSET-PROFILE-PAGE-001
    revision: asset-r3
    path_or_url: docs/planning/phase-profile/assets/profile-review-page-r3.png
design_tokens:
  color: 复用 FRONTEND-BASELINE 的 color.surface、color.text、color.primary、color.danger
  typography: 复用 heading-lg、body-md、label-sm；正文行高不低于现有 body-md
  spacing: 复用 4/8/12/16/24/32 token scale
  radius: 复用 radius-md；禁止创建页面专属全局 token
  shadow: 内容容器使用现有 surface shadow；移动端为 none
  iconography: 复用现有 outline icon，16px 或 20px
layout_contract:
  viewport: desktop 1440x900; mobile 390x844
  grid: desktop 12 columns / 24px gutter / 32px margin; mobile 4 columns / 16px gutter / 16px margin
  regions:
    - existing global header
    - centered review content
    - sticky mobile action area
  alignment:
    - labels and values align to existing read-only form rows
    - desktop action area right aligned
  sizing:
    - content max-width 960px
    - primary action min-width 144px desktop and full-width mobile
  overflow: page scroll; mobile action area remains visible without covering focused content
responsive_contract:
  breakpoints:
    - project desktop breakpoint
    - project mobile breakpoint
  adaptations:
    - desktop two-column label/value rows become stacked rows on mobile
    - actions become full-width vertical order on mobile
  prohibited_changes:
    - no content reordering that changes reading or focus order
    - no hidden required fields on mobile
component_contract:
  required_existing_components:
    - GlobalHeader
    - ReadOnlyFieldRow
    - PrimaryButton
    - InlineAlert
    - Checkbox
  component_order:
    - BackLink
    - PageHeading
    - ReviewSections
    - UsageNotice
    - ConfirmationCheckbox
    - InlineAlert
    - ActionArea
  variants:
    - PrimaryButton default/loading/disabled
    - InlineAlert danger/success
  enabled_disabled_hidden_rules:
    - Confirm unchecked disables submit
    - Submitting disables submit, back link and modify action
    - Success hides all prior actions and shows only return-to-workspace
state_contract:
  default: review data visible; one primary submit action; modify is secondary
  loading: structure stable; button progress visible; repeat submit and navigation disabled
  empty: not_applicable because entry requires complete review data; invalid entry is blocked upstream
  error: focused inline error; data and confirmation preserved; retry and modify available
  success: success message visible; only return-to-workspace available
  blocked: explain invalid entry and provide return-to-workspace; no submit action
content_contract:
  required_copy:
    - 确认个人资料
    - 请确认以下信息准确无误
    - 确认提交
    - 返回修改
  variable_content_limits:
    - address may wrap to three lines desktop and unrestricted lines mobile
    - phone number never truncates
  truncation_wrapping_rules:
    - identifiers use middle truncation only when existing baseline requires it
    - labels never truncate
  localization_rules:
    - simplified Chinese only in this phase
    - no mixed English action labels
  validation_messages:
    - 未勾选确认项：请先确认以上资料准确无误
    - 提交失败：资料提交失败，请重新提交或返回修改
accessibility_contract:
  semantic_structure:
    - one h1
    - review sections use labelled groups
    - status changes use an appropriate live region
  keyboard_order:
    - back link, confirmation checkbox, modify, submit
  focus_management:
    - failure focuses inline alert
    - success focuses success heading
  accessible_names:
    - icon-only status indicators include text alternatives
  contrast_and_non_color_cues:
    - disabled, error and success states include text or icon cues in addition to color
motion_feedback_contract:
  transitions:
    - button loading indicator only; no page entrance animation
  durations_or_project_tokens:
    - use existing feedback motion token
  reduced_motion_behavior:
    - replace animated spinner with non-motion progress state when project preference is enabled
  pending_feedback_timing:
    - show pending feedback immediately after accepted submit trigger
implementation_acceptance:
  structural_assertions:
    - required component order is preserved
    - default state has exactly one primary action
  responsive_assertions:
    - no horizontal scroll at 390px
    - sticky action area does not cover focused elements
  state_assertions:
    - repeat submit is impossible while pending
    - error preserves data and confirmation
    - success removes prior actions
  visual_comparison_refs:
    - ASSET-PROFILE-PAGE-001@asset-r3
```

## UX 交互合同

### UX-SCN-PROFILE-001：提交与失败恢复

```yaml
contract_revision: ux-r3
flow_ref: FLOW-PROFILE-001
scenario_ref: SCN-PROFILE-REVIEW-001
start_page_ref: PAGE-PROFILE-001@page-r4
covered_by_asset_ref: ASSET-PROFILE-UX-001@asset-r2
```

| Step | From UI state | Trigger | Preconditions | Domain/API intent ref | Pending feedback | Success UI state | Failure UI state | Recovery / retry | Cancel / back | Forbidden actions | Visible evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PAGE-PROFILE-001.default | 勾选确认项 | 已合法进入且资料完整 | STATE-PROFILE-REVIEWABLE | none | PAGE-PROFILE-001.default with submit enabled | same state with inline guidance | 修正确认项 | 返回修改 | 未确认时提交 | 按钮启用且勾选项有可访问名称 |
| 2 | PAGE-PROFILE-001.default | 点击确认提交 | 确认项已勾选且 PERM-PROFILE-SUBMIT 允许 | API-PROFILE-SUBMIT | 立即进入 loading；禁用重复提交和导航 | PAGE-PROFILE-001.success | PAGE-PROFILE-001.error | 错误态允许重新提交 | pending 时禁止取消；失败后可返回修改 | 重复提交、返回、修改 | loading、成功或错误提示可被断言 |
| 3 | PAGE-PROFILE-001.error | 点击重新提交 | 原资料和确认项保留 | API-PROFILE-SUBMIT | 再次进入 loading | PAGE-PROFILE-001.success | PAGE-PROFILE-001.error | 可继续重试或返回修改 | 返回修改 | pending 时重复提交 | 焦点先到错误提示，重试后状态可见 |
| 4 | PAGE-PROFILE-001.success | 点击返回工作台 | 提交成功事实已确认 | FLOW-PROFILE-001 terminal | none | PAGE-WORKSPACE-001.default | PAGE-PROFILE-001.success with navigation error | 保留成功状态并允许再次返回 | not_applicable | 再次提交、返回修改 | 工作台入口可见或导航错误提示可见 |

## 设计资产索引

### ASSET-PROFILE-PAGE-001

```yaml
asset_revision: asset-r3
asset_type: page_ui
asset_status: visual_confirmed
source: user_generated
asset_path_or_url: docs/planning/phase-profile/assets/profile-review-page-r3.png
content_fingerprint: sha256:example-profile-review-r3
applies_to:
  prompt_refs:
    - PROMPT-PAGE-PROFILE-001@prompt-r2
  page_refs:
    - PAGE-PROFILE-001@page-r4
  module_refs: []
  interaction_refs:
    - UX-SCN-PROFILE-001@ux-r3
covered_states:
  - default
  - loading
  - error
  - success
known_gaps: []
user_confirmation_ref: CONFIRM-UI-20260822-01
confirmed_at: '2026-08-22T10:00:00+09:00'
```

### ASSET-PROFILE-UX-001

```yaml
asset_revision: asset-r2
asset_type: ux_interaction
asset_status: visual_confirmed
source: user_generated
asset_path_or_url: docs/planning/phase-profile/assets/profile-submit-flow-r2.png
content_fingerprint: sha256:example-profile-submit-flow-r2
applies_to:
  prompt_refs:
    - PROMPT-UX-PROFILE-001@prompt-r1
  page_refs:
    - PAGE-PROFILE-001@page-r4
  module_refs: []
  interaction_refs:
    - UX-SCN-PROFILE-001@ux-r3
covered_states:
  - default
  - loading
  - error
  - success
known_gaps: []
user_confirmation_ref: CONFIRM-UI-20260822-02
confirmed_at: '2026-08-22T10:05:00+09:00'
```

## FLOW—SCN—MODULE—PAGE—合同—资产—TEST 覆盖矩阵

| FLOW | SCN | MODULE | PAGE / UI-MOD | Prompt ref | UI contract revision | UX-SCN revision | Confirmed asset ref | TEST ref | Execution readiness |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FLOW-PROFILE-001 | SCN-PROFILE-REVIEW-001 | MODULE-PROFILE-REVIEW | PAGE-PROFILE-001 | PROMPT-PAGE-PROFILE-001@prompt-r2; PROMPT-UX-PROFILE-001@prompt-r1 | page-r4 | UX-SCN-PROFILE-001@ux-r3 | ASSET-PROFILE-PAGE-001@asset-r3; ASSET-PROFILE-UX-001@asset-r2 | TEST-PROFILE-UI-001; TEST-PROFILE-UX-001 | execution_ready |

## 13 UI TASK 绑定示例

```yaml
frontend_contract_binding:
  design_document_path: docs/planning/phase-profile/05-前端页面与UI-UX交互设计.md
  design_manifest_ref: docs/planning/phase-profile/05-前端页面与UI-UX交互设计.md#design-delivery-manifest
  baseline_source: docs/product/PROJECT-CURRENT-BASELINE.md#frontend-experience
  reference_pages:
    - PAGE-PROFILE-001@page-r4
  prompt_refs:
    - PROMPT-PAGE-PROFILE-001@prompt-r2
    - PROMPT-UX-PROFILE-001@prompt-r1
  page_contract_refs:
    - PAGE-PROFILE-001@page-r4
  module_contract_refs: []
  interaction_contract_refs:
    - UX-SCN-PROFILE-001@ux-r3
  confirmed_asset_refs:
    - ASSET-PROFILE-PAGE-001@asset-r3
    - ASSET-PROFILE-UX-001@asset-r2
  consistency_test_refs:
    - TEST-PROFILE-UI-001
    - TEST-PROFILE-UX-001
  allowed_extensions:
    - profile review page composition
  prohibited_redefinitions:
    - global navigation
    - theme tokens
    - shared form component semantics
```

## Handoff 绑定示例

```yaml
frontend_experience_binding:
  applicable: true
  design_document_path: docs/planning/phase-profile/05-前端页面与UI-UX交互设计.md
  design_contract_version: ui-ux-execution/v1
  design_manifest_ref: docs/planning/phase-profile/05-前端页面与UI-UX交互设计.md#design-delivery-manifest
  baseline_source: docs/product/PROJECT-CURRENT-BASELINE.md#frontend-experience
  style_mode: inherit_current
  reference_pages:
    - PAGE-PROFILE-001@page-r4
  required_existing_components:
    - GlobalHeader
    - ReadOnlyFieldRow
    - PrimaryButton
    - InlineAlert
    - Checkbox
  allowed_extensions:
    - profile review page composition
  prohibited_redefinitions:
    - global navigation
    - theme tokens
    - shared form component semantics
  prompt_refs:
    - id: PROMPT-PAGE-PROFILE-001
      revision: prompt-r2
      anchor: '#prompt-page-profile-001资料确认页'
    - id: PROMPT-UX-PROFILE-001
      revision: prompt-r1
      anchor: '#prompt-ux-profile-001提交与失败恢复'
  page_contract_refs:
    - id: PAGE-PROFILE-001
      revision: page-r4
      anchor: '#page-profile-001资料确认页'
  module_contract_refs: []
  interaction_contract_refs:
    - id: UX-SCN-PROFILE-001
      revision: ux-r3
      anchor: '#ux-scn-profile-001提交与失败恢复'
  confirmed_design_assets:
    - id: ASSET-PROFILE-PAGE-001
      revision: asset-r3
      path_or_url: docs/planning/phase-profile/assets/profile-review-page-r3.png
      status: visual_confirmed
    - id: ASSET-PROFILE-UX-001
      revision: asset-r2
      path_or_url: docs/planning/phase-profile/assets/profile-submit-flow-r2.png
      status: visual_confirmed
  consistency_tests:
    - TEST-PROFILE-UI-001
    - TEST-PROFILE-UX-001

handoff_role_mapping:
  - role: UI/UX Design
    path: docs/planning/phase-profile/05-前端页面与UI-UX交互设计.md
```

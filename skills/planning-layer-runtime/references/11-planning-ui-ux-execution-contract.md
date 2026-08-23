# UI/UX Execution Contract

本文件定义 `05-前端页面与UI/UX交互设计.md` 面向设计生成、开发实现和测试验收的可执行交付合同。涉及正式页面、用户可见交互或前端体验变化时必须读取；纯后端、纯数据或纯规划任务不适用。

## 目录

- 1–3：目标、交付组成与 Design Delivery Manifest
- 4–7：Copy-Ready Prompt、UI Implementation、UX Interaction 与版本化资产合同
- 8–10：覆盖矩阵、Planning Handoff 与 UI TASK 绑定
- 11–12：执行/验收规则与 UI/UX Execution Readiness Gate

## 1. 目标与边界

执行级 05 必须让下游无需依赖聊天记录即可回答：

- 设计工具应收到什么可直接复制的 Prompt。
- 每个页面、局部模块和交互状态应呈现什么。
- 哪些视觉资产已被用户确认，以及确认的是哪个版本。
- 开发必须复用什么、允许扩展什么、禁止重新定义什么。
- 每个用户动作从哪个状态出发，成功、失败、取消和返回后进入什么状态。
- Long 与 Testing 应读取哪些精确路径、ID、revision 和 TEST。

05 不定义业务事实、权限、持久状态、API 或架构；它只能引用 01–10 中已经确认的事实。发现上游冲突时停止 05 确认并回写真正的 SoT。

## 2. 执行级交付组成

涉及 UI 的 execution-ready 规划必须在同一 05 文档中包含：

1. `style_inheritance_decision`。
2. `design_delivery_manifest`。
3. 可复制设计提示词。
4. 页面实现合同。
5. 适用时的局部模块实现合同。
6. UX 交互合同与确定性状态迁移表。
7. 带 revision 的设计资产索引。
8. FLOW—SCN—MODULE—PAGE—合同—资产—TEST 覆盖矩阵。

第二阶段轮到 05 时，必须按 `10-planning-document-interaction-runtime.md#51-05-design-asset-collection-interaction-gate` 直接向用户提供完整 UI Prompt、接收并确认 UI 图，再为确有需要的交互提供基于已确认 UI revision 的 UX Prompt 并接收 UX 图。设计内容和全部必需资产闭合后可标记 `design_ready`；11 TEST 与 13 TASK 精确绑定完成后才可标记 `execution_ready` 并准备 Handoff。本期只形成讨论或仍缺设计事实/资产时使用 `blocked`。只要存在 UI TASK，进入 Handoff 前必须为 `execution_ready`，且对应资产必须为 `visual_confirmed`。

## 3. Design Delivery Manifest

05 必须包含唯一清单：

```yaml
design_delivery_manifest:
  contract_version: ui-ux-execution/v1
  design_document_path: <05 的真实项目路径>
  style_mode: <inherit_current | extend_current | replace_current>
  baseline_source: <当前前端体验基线的真实路径与锚点>
  prompt_refs:
    - id: <PROMPT-ID>
      revision: <prompt revision>
      anchor: <05 内稳定锚点>
  page_contract_refs:
    - id: <PAGE-ID>
      revision: <page contract revision>
      anchor: <05 内稳定锚点>
  module_contract_refs: []
  interaction_contract_refs:
    - id: <UX-SCN-ID>
      revision: <interaction contract revision>
      anchor: <05 内稳定锚点>
  confirmed_asset_refs:
    - id: <ASSET-ID>
      revision: <asset revision>
      path_or_url: <真实路径或外部引用>
  consistency_test_refs: [<TEST-ID>]
  unresolved_design_refs: []
  execution_readiness: <design_ready | execution_ready | blocked>
  blocked_reason: <blocked 时必填；其他状态省略>
```

规则：

- `design_document_path` 必须是真实路径，不得使用编号猜测或占位符。
- 所有引用必须能在当前 05 或已确认 11 中解析；ID 与 revision 必须同时匹配。
- `design_ready` 表示 Prompt、PAGE/UI-MOD、UX-SCN 与必需资产本身已经闭合；允许 11/13/Handoff 尚未生成，此时 `consistency_test_refs` 可暂为空。
- `execution_ready` 表示 11 TEST 与 13 TASK 绑定已完成一致性校验，可以准备 Handoff；此时 `unresolved_design_refs` 必须为空，且 `consistency_test_refs` 不得缺少适用 UI/UX TEST。
- `blocked` 必须写明设计事实、资产或下游绑定的具体阻断原因；不得用来掩盖缺失内容。
- `confirmed_asset_refs` 只能引用 `asset_status: visual_confirmed` 的同 revision 资产。
- 任一 Prompt、合同、资产或 TEST revision 变化都会使旧 Manifest 与下游绑定失效；必须更新 05、13、Handoff，并按 Change Set 精确传播。

## 4. Copy-Ready Prompt Contract

每条 `PROMPT-STYLE`、`PROMPT-PAGE`、`PROMPT-MODULE` 或 `PROMPT-UX` 都必须是可直接复制的交付项，而不是关键词清单。

固定字段：

```yaml
prompt_revision: <稳定 revision>
prompt_type: <style | page | module | ux>
target_tool: <真实工具名 | tool_agnostic>
language: <输出界面与提示词语言>
reference_inputs:
  - id: <ASSET / baseline reference>
    revision: <适用时填写>
    path_or_url: <真实路径或引用>
output_spec:
  device: <desktop | mobile | tablet | responsive | other>
  viewport: <宽×高或明确范围>
  frame_count: <整数>
  aspect_ratio: <比例>
  resolution: <像素或工具可识别要求>
required_constraints: []
negative_constraints: []
```

紧随字段后必须提供：

````markdown
prompt_body:

```prompt
<无需补充上下文即可复制到 target_tool 的完整提示词正文>
```
````

Prompt 正文必须明确：

- 产品、用户、设备、页面或交互目标。
- 参考资产及必须继承的视觉语言。
- 完整信息结构、组件层级、主次操作和全部适用状态。
- 输出画幅、帧数、分辨率或可验证的输出约束。
- 禁止出现的风格、业务动作、旧语义、额外页面或未经确认内容。
- 页面 Prompt 输出完整页面；模块 Prompt 只改指定区域；UX Prompt 输出明确帧序和状态变化。

禁止：

- 把“参考上文”“按之前风格”“自行补充”“视情况处理”作为必要上下文。
- 省略 `prompt_body`，只列提示词要点。
- 使用不存在或未确认的参考图。
- 用 Prompt 新增 FLOW、资格、权限、状态或 API 语义。

### 4.1 User-Facing Prompt Delivery And Asset Intake

Prompt 写入 05 只是持久化，不等于已经交付给用户。批次选择、每批上限、UI/UX 依赖顺序、图片接收、视觉确认和继续条件只按 10 执行，中断恢复只按 08 执行；本节是每条 Prompt 用户态格式与图片序号映射的唯一事实来源。

- 主展示必须固定为“序号、`title`、尺寸建议、参考的图片序号、单独 Prompt 文本”，用户无需理解内部 ID 即可复制和回传：

````markdown
序号：图 01
title：资料审核页—默认与提交状态
尺寸建议：桌面端；1440×1024；16:10；2x；4 帧
参考的图片序号：无

```prompt
<独立、完整、无需引用聊天上文的 prompt_body>
```
````

- `序号` 来自对应 ASSET 的稳定 `image_sequence`，跨批次、恢复与 revision 变化均不得重排；`参考的图片序号` 只引用已真实提供的 ASSET 序号，没有时明确写 `无`。内部 `PROMPT-ID@revision -> ASSET-ID@revision`、目标工具和对应合同继续持久化，并可作为每项末尾的一行追踪信息，但不得取代主展示字段。
- 批次开头按 10 说明进度，并明确用户可把 Prompt 复制到任意外部生图工具；本格式不得依赖内置 ImageGen、CLI、API Key 或指定供应商。
- UX Prompt 的“参考的图片序号”必须逐一映射其 `reference_inputs` 中已达到 `visual_confirmed` 的 UI ASSET revision；需要多帧交互图时，Prompt 正文明示帧序、画幅和每帧状态，已有确认 UI 图足以表达时不机械增加 UX 图。
- 用户可上传自行制作、其他工具生成或既有的 UI/UX 图；Prompt 是方便生成的直接交付，不是接受资产的唯一入口。
- 用户按图片序号回传；部分回传、修订与继续行为按 10 处理，且不得改变未受影响 ASSET 的 `image_sequence`。

本节不新增交互 Runtime 或第二份资产状态。

存在必需 UI/UX 图时，只有 `design_asset_collection.collection_status: complete` 且全部对应 ASSET revision 均为 `visual_confirmed`，05 才能通过整体确认；没有必需设计图时必须在 05 明确记录判定依据，不创建空批次。

### 4.2 User-Facing Visual Confirmation Display

图片路径写入 05、AI 能够读取图片或用户已经上传文件，都不等于用户完成了视觉确认。视觉确认请求应让用户在当前对话中直接看到自己正在确认的实际画面；当前交互工具不支持图片展示时，优先回退为可直接打开并绑定同一资产 revision 的图片链接；链接也不可用时，必须提供精确定位信息，允许用户自行找到图片并以明确反馈确认。交互顺序只按 10 执行，恢复重显只按 08 执行，本节是用户态图片确认呈现格式的唯一事实来源。

批次开头必须说明当前确认批次、资产类型和图片数量。当前工具支持图片展示时，随后按 `image_sequence` 逐张使用以下主格式；`实际图片` 位置必须调用当前交互表面支持的原生图片/附件预览或可实际渲染的内联图片能力，不能输出占位文字：

````markdown
当前确认批次：UI 第 1 批，共 3 张

图 01｜资料审核页—默认与提交状态

<直接内联展示 ASSET-ID@revision 对应的实际图片>

资产版本：v2
覆盖：默认、提交中、成功、失败
发现：失败态缺少返回修改入口
状态：review_pending
````

当前工具确认不支持图片展示时，改用以下回退格式；链接必须能直接打开当前 `ASSET-ID@revision` 对应图片，普通文件路径或不可访问地址不算有效链接：

```markdown
图 01｜资料审核页—默认与提交状态

查看图片：[打开图 01 当前版本](<当前 ASSET revision 的可访问链接>)

资产版本：v2
覆盖：默认、提交中、成功、失败
发现：失败态缺少返回修改入口
状态：review_pending
```

当前工具既不能展示图片、也不能提供有效直接链接时，改用以下自主定位格式。真实位置必须来自当前 ASSET，内容指纹只在已有时提供，不得临时伪造：

```text
图 01｜资料审核页—默认与提交状态

资产版本：v2
图片位置：<当前 ASSET revision 的真实路径或外部位置>
内容指纹：<已有 hash、文件版本或等价指纹；没有时写“未记录”>
覆盖：默认、提交中、成功、失败
发现：失败态缺少返回修改入口
状态：review_pending

当前工具无法直接展示或打开这张图。你可以按以上位置自行找到并查看；
确认后可回复“已找到并确认图 01 当前版本”，也可以直接指出需要修改的地方。
```

规则：

- 实际图片始终是主确认对象；图片序号和标题用于用户识别，资产版本用于精确追溯。内部 `ASSET-ID@revision` 可作为次要追踪信息，但不得要求用户依靠裸 ID 判断画面。
- 展示必须读取 05 当前 ASSET revision 的真实 `asset_path_or_url`，并与当前批次 `active_asset_refs` 逐项匹配；不得展示旧版、目录中自动发现的“最新图”、Prompt 参考图或仅存在于聊天历史中的图片。
- 每张图片后只展示本次确认必要的覆盖、差异和状态；没有 known gaps 时明确写“未发现已知缺口”。不得用长篇技术审查挤开实际图片。
- UX 资产包含多帧或多个画面时，按 UX Interaction Contract 的帧序连续展示并标明帧号；链接或自主定位回退时也必须逐帧映射，不得只提供首帧后确认整个交互。
- 工具支持图片展示时必须使用主格式，不得为了省事降级。工具不支持时依次使用直接链接和自主定位，不要求用户切换页面能力或更换工具。
- 整批图片均已按当前可用方式呈现后，再给出“确认本批图片”“已自行找到并确认本批图片”或“图 02 的……需要调整”等自然语言回复方式。该确认只绑定本次 `design_asset_review_confirmation` 中的准确 ASSET revisions，不确认 05 文档。
- 用户明确说明已按定位信息找到并查看当前图片后，其确认或纠正是视觉接受结果的优先依据；不得因 AI 无法展示、无法生成链接或审美判断不同而拒绝推进。AI 发现的合同缺口继续如实列出，若会改变已确认业务或交互合同则按既有 SoT 规则处理，不得静默忽略。
- 只有实际资产缺少可定位的真实位置、revision 无法唯一确定、用户表示无法找到，或反馈无法绑定当前确认批次时，才保持 `review_pending` 并请求最小补充。普通文件名、失效链接或 AI 的审图结论本身不能证明用户查看，但用户对准确定位对象的明确反馈可以完成确认。
- 图片内容或 revision 变化后，必须按当前工具能力重新展示新版本、重新提供其直接链接或更新自主定位信息，并重新确认；旧展示、旧链接、旧定位信息和旧确认不得继承。
- 三种呈现方式都只是现有 ASSET 的用户态呈现，不复制图片、不修改 `asset_path_or_url`，也不新增工具能力状态、preview 状态、展示日志、确认文件或第二份资产 SoT。

## 5. UI Implementation Contract

每个进入 UI TASK 的 `PAGE` 必须包含以下实现合同；用户可见的 `UI-MOD` 使用同一字段集并将布局范围限定到所属 PAGE。

```yaml
contract_revision: <稳定 revision>
source_prompt_refs:
  - id: <PROMPT-ID>
    revision: <prompt revision>
source_asset_refs:
  - id: <ASSET-ID>
    revision: <asset revision>
    path_or_url: <真实路径或引用>
design_tokens:
  color: <token/现有来源/精确值>
  typography: <token/字号/字重/行高>
  spacing: <token/间距刻度>
  radius: <token/精确值>
  shadow: <token/精确值或 none>
  iconography: <来源、尺寸和风格>
layout_contract:
  viewport: <目标视口>
  grid: <列、gutter、margin>
  regions: []
  alignment: []
  sizing: []
  overflow: <滚动、固定、截断规则>
responsive_contract:
  breakpoints: []
  adaptations: []
  prohibited_changes: []
component_contract:
  required_existing_components: []
  component_order: []
  variants: []
  enabled_disabled_hidden_rules: []
state_contract:
  default: <可见内容与唯一主操作>
  loading: <骨架/进度/禁用规则>
  empty: <信息、动作、退出>
  error: <错误信息、重试、退出>
  success: <可见变化与后续动作>
  blocked: <阻断原因与合法动作>
content_contract:
  required_copy: []
  variable_content_limits: []
  truncation_wrapping_rules: []
  localization_rules: []
  validation_messages: []
accessibility_contract:
  semantic_structure: []
  keyboard_order: []
  focus_management: []
  accessible_names: []
  contrast_and_non_color_cues: []
motion_feedback_contract:
  transitions: []
  durations_or_project_tokens: []
  reduced_motion_behavior: []
  pending_feedback_timing: []
implementation_acceptance:
  structural_assertions: []
  responsive_assertions: []
  state_assertions: []
  visual_comparison_refs: []
```

字段不适用时写明确的 `not_applicable` 与原因；不得省略后让执行层猜测。精确数值优先引用项目现有 design token；若项目没有 token 且数值会影响视觉匹配，必须由用户确认或从 `visual_confirmed` 资产量取并记录来源。

## 6. UX Interaction Contract

每个关键 `UX-SCN` 必须定义起点、终点、参与页面/模块、业务与 API 意图引用，并提供确定性状态迁移表：

```markdown
| Step | From UI state | Trigger | Preconditions | Domain/API intent ref | Pending feedback | Success UI state | Failure UI state | Recovery / retry | Cancel / back | Forbidden actions | Visible evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

每行必须满足：

- `From UI state` 与目标状态能在 PAGE/UI-MOD 的 `state_contract` 中解析。
- `Preconditions` 只引用已确认的 FLOW/STATE/PERM/API 事实。
- `Pending feedback` 明确出现时机、可重复提交策略和当前可用动作。
- 成功、失败、重试、取消、返回和人工协助路径按实际场景闭合。
- `Forbidden actions` 明确 pending、blocked、permission denied 或 legacy entry 下不可执行的动作。
- `Visible evidence` 可被自动化断言、截图或人工观察证明。

无法用已有静态资产说明多步或多状态交互时，必须生成 `PROMPT-UX` 和对应 `ASSET`；否则记录 `covered_by_existing_ui_assets` 并列出覆盖资产。

## 7. Versioned Asset Contract

每个 `ASSET` 使用以下字段：

```yaml
image_sequence: <本期 05 内唯一且稳定的正整数；用户态显示为图 01>
asset_revision: <稳定 revision>
asset_type: <global_style | page_ui | module_ui | ux_interaction>
asset_status: <planned | prompt_ready | received | review_pending | visual_confirmed | superseded>
source: <user_provided | user_generated | external_reference>
asset_path_or_url: <received 及以后状态必填>
content_fingerprint: <可获得时记录 hash、Figma version、file version 或等价指纹>
applies_to:
  prompt_refs: []
  page_refs: []
  module_refs: []
  interaction_refs: []
covered_states: []
known_gaps: []
user_confirmation_ref: <visual_confirmed 时必填>
confirmed_at: <visual_confirmed 时必填>
supersedes: <旧 ASSET-ID@revision；不适用时省略>
```

规则：

- `image_sequence` 是用户态图片映射的唯一序号：同一 ASSET 的所有 revision 保持不变，批次切换、中断恢复、替换或确认顺序变化都不得重编号；新 ASSET 使用本期下一个未占用正整数，已废弃序号不回收。
- Prompt 展示中的“序号”和“参考的图片序号”必须由 `image_sequence` 渲染。引用图片时仍在内部绑定确切 `ASSET-ID@revision`，不得只保存数字而丢失版本关系。
- `received` 及以后状态必须有真实路径或外部引用。
- `source: user_generated` 表示用户使用 Planning 提供的 Prompt 生成后回传；`user_provided` 表示用户直接提供已有图。两者进入执行前都必须经过同一视觉确认。
- `visual_confirmed` 必须绑定 revision、用户确认来源与确认时间。
- 同一资产内容变化必须提升 `asset_revision`；不得在原 revision 下静默替换。
- 新 revision 未确认前，旧 revision 仍是执行绑定；如果旧版已被明确废弃，则 UI TASK 必须阻断。
- Long 只能消费 Handoff 明确列出的 `ASSET-ID@revision`，不得自动选择“最新图”。

## 8. Coverage Matrix

05 必须包含：

```markdown
| FLOW | SCN | MODULE | PAGE / UI-MOD | Prompt ref | UI contract revision | UX-SCN revision | Confirmed asset ref | TEST ref | Execution readiness |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

每个 P0 SCN、关键异常状态和旧入口处理都必须有唯一覆盖结论。`Execution readiness` 只允许 `design_ready`、`execution_ready` 或 `blocked:<reason>`；05 首次确认时允许 `design_ready`，生成 UI TASK 和 execution-ready Handoff 前必须提升为 `execution_ready`。

## 9. Planning Handoff Binding

UI 适用时 Handoff 必须传递精确消费指针：

```yaml
frontend_experience_binding:
  applicable: true
  design_document_path: <05 的真实路径>
  design_contract_version: ui-ux-execution/v1
  design_manifest_ref: <05 路径>#design-delivery-manifest
  baseline_source: <真实路径与锚点>
  style_mode: <inherit_current | extend_current | replace_current>
  reference_pages: [<PAGE-ID@contract-revision>]
  required_existing_components: []
  allowed_extensions: []
  prohibited_redefinitions: []
  prompt_refs:
    - id: <PROMPT-ID>
      revision: <prompt revision>
      anchor: <05 内锚点>
  page_contract_refs:
    - id: <PAGE-ID>
      revision: <contract revision>
      anchor: <05 内锚点>
  module_contract_refs: []
  interaction_contract_refs:
    - id: <UX-SCN-ID>
      revision: <contract revision>
      anchor: <05 内锚点>
  confirmed_design_assets:
    - id: <ASSET-ID>
      revision: <asset revision>
      path_or_url: <真实路径或引用>
      status: visual_confirmed
  consistency_tests: [<TEST-ID>]
```

Handoff 只传递绑定，不复制 Prompt、UI 合同或交互表正文。正式 `handoff_role_mapping` 在 05 已实际生成时必须加入：

```yaml
- role: UI/UX Design
  path: <05 的真实路径>
```

## 10. UI TASK Binding

13 中每个 UI TASK 必须引用同一绑定：

```yaml
frontend_contract_binding:
  design_document_path: <05 的真实路径>
  design_manifest_ref: <05 路径>#design-delivery-manifest
  baseline_source: <真实路径与锚点>
  reference_pages: [<PAGE-ID@contract-revision>]
  prompt_refs: [<PROMPT-ID@revision>]
  page_contract_refs: [<PAGE-ID@contract-revision>]
  module_contract_refs: []
  interaction_contract_refs: [<UX-SCN-ID@contract-revision>]
  confirmed_asset_refs: [<ASSET-ID@asset-revision>]
  consistency_test_refs: [<TEST-ID>]
  allowed_extensions: []
  prohibited_redefinitions: []
```

05 与 13 的路径、ID、revision 必须一致；正式 Handoff 准备时再与两者逐项比较。任一引用无法解析、资产不是 `visual_confirmed`、合同仍有未决项或 TEST 缺失时，UI TASK 的 Task Ready Gate 失败。

## 11. Execution and Acceptance Rules

Long 必须：

- 在生成 UI Runtime Task 前解析 `frontend_experience_binding` 的全部路径、ID、revision 和资产。
- 将当前消费绑定写入 Runtime snapshot，只保存引用和校验状态，不复制正文。
- 按 PAGE/UI-MOD 合同实现结构、状态、响应式、文案、无障碍和动效反馈。
- 按 UX 状态迁移表实现 trigger、pending、success、failure、retry、cancel、back 和 forbidden actions。
- 对可自动化部分建立结构、状态、响应式与交互断言；项目支持截图或视觉回归时绑定确认资产。
- 遇到合同与现有代码、资产或技术限制冲突时停止，并以 `design_drift` 或 `planning_gap` 写回 Planning；不得自行重设计。

Testing 必须继承 Long 的自动化证据，并针对 `manual_required` 中未自动化的视觉一致性、真实设备布局、复杂 UX 和无障碍观察项，按同一 PAGE/UX-SCN/ASSET revision 进行人工验证。最终结论不得引用不同 revision 的资产。

## 12. UI/UX Execution Readiness Gate

UI TASK 进入 Ready 前必须全部满足：

- Design Delivery Manifest 已从 05 确认阶段的 `design_ready` 提升为 `execution_ready`，且无 unresolved design refs。
- 每个关联 Prompt 有完整 copy-ready `prompt_body`。
- 每个关联 PAGE/UI-MOD 有完整 UI Implementation Contract。
- 每个关联 UX-SCN 有确定性状态迁移表。
- 每个必需资产真实存在且为 Handoff 指定的 `visual_confirmed` revision。
- 13 确认前，05 Manifest、11 TEST 与 13 UI TASK binding 的 TEST 和合同引用一致。
- 准备 Handoff 时，`frontend_experience_binding` 还必须与 05、11、13 的路径、ID、revision 和 TEST 一致。
- 05 轮到确认前运行设计就绪校验：`python3 scripts/validate_ui_ux_contract.py --design-doc <05-path> --allow-design-ready`；若设计仍合法阻断，使用 `--allow-blocked` 并保留明确 blocker。
- 13 轮到确认前运行执行就绪校验：`python3 scripts/validate_ui_ux_contract.py --design-doc <05-path> --task-doc <13-path>`。
- 正式 Handoff 准备后运行完整绑定校验：`python3 scripts/validate_ui_ux_contract.py --design-doc <05-path> --task-doc <13-path> --handoff <handoff-path>`；需要验证项目内真实路径时再提供 `--project-root <project-root>`。
- 脚本不可用时必须逐项完成同等检查并记录原因与证据。

任一失败：

```text
UI_TASK_NOT_READY
-> STOP_HANDOFF_OR_EXECUTION
-> WRITE_BACK_TO_05_OR_OWNING_SOT
-> DO_NOT_INFER_OR_REDESIGN
```

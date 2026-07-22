---
name: ai-code-inspection
description: 通用前后端代码检查与规范矫正 Skill，依据项目环境档案和按需加载的技术栈 Profile 执行命名与放置、代码质量、架构边界、测试、文档、注释以及 Git/验证/CI/CD/提交准备检查。支持 11 种模式：前 10 种单次完成，第 11 种交互式执行完整七步。已确认 Bug 只有在预期行为、根因证据和具体根因文件均明确时才允许单次最小修复。不要用于上线、发布、生产验收、严格安全验收或大规模重构。
---

# AI Code Inspection

使用本 Skill 完成日常代码检查、专项检查，以及受控的规范合规矫正。`standards_compliance_correction` 以 `interactive_seven_step` 完整执行 Step 1–7；`full_readonly_audit` 也完整执行 Step 1–7，但以 `single_run` 连续只读完成并一次性反馈；其余 9 种模式按任务目标加载并连续执行适用 Step。

本 Skill 不承担上线、部署、生产门禁或严格安全验收，也不得把规范矫正扩张为业务修改、方案替换或大规模重构。

## 事实源与文件职责

正式执行前必须读取：

1. `project-environment-profile.md`
   - 稳定环境信息的单一事实源（SoT）。
   - 只记录从当前仓库确认的工作区、组件、语言、框架、运行时、持久化、契约、测试、验证命令和 CI/CD 稳定事实。
   - 不得写入临时运行状态、Step 记录、命令输出或每次执行日志。
   - 只有稳定环境事实变化时才允许修改。
2. `inspection-runtime-state.md`
   - 当前运行的临时状态与权限快照。
   - 记录运行模式、检查范围、修改范围、处置权限、Step/phase、问题、修正、验证和风险。
   - 最终报告输出后必须重置为初始模板，不得积累跨运行上下文。

文件职责必须保持低熵：

- `SKILL.md`：唯一 Runtime Governance Source。
- `references/README.md`：轻量执行路线图。
- `references/step1-*.md` 到 `step7-*.md`：完整且不可降级的检查规范，不得在其中重复 Runtime 状态、权限或 gate 规则。
- `references/profiles/`：只保存技术栈附加规则；不得重新定义模式、范围、权限、问题分类或 Runtime 生命周期。

环境档案为 `uninitialized`、缺失或与仓库事实冲突时，先只读扫描当前目标仓库并初始化或纠正稳定事实，再运行检查。不得从示例、其他项目或通用 Skill 源文件复制环境事实；无法可靠确认的字段保持为空并报告。

## 启动与模式选择

每次新运行：

1. 读取环境事实源；未初始化时先依据当前仓库事实完成初始化。
2. 将 Runtime 状态重置为初始模板，清除上一运行的模式和全部修改权限。
3. 根据用户目标确定 `mode`；记录 `mode_source: explicit_user` 或 `inferred_default`。
4. 分别解析并记录 `scope`、`editable_scope` 和 `remediation_policy`。
5. 根据 `mode` 计算并记录 `execution_strategy`；模式切换时必须重新计算，不得继承旧策略。
6. 记录 `modifier`、`modifier_source` 和系统时间生成的 `run_started_at`。
7. 只有边界、权限和执行策略无歧义后，才开始执行。

默认选择规则：

- 普通“检查代码”“review 改动”默认为 `changed_code_review`，只读检查当前 Git 变更。
- 指定文件、模块或问题时，只检查明确目标及必要的只读上下文；不得扩成全项目。
- “全量检查项目”固定为 `full_readonly_audit`。
- 只有用户明确要求“按规范修正、矫正、整改”时，才选择 `standards_compliance_correction`。
- 模糊请求不得默认解释为“全项目 + 全量代码”，也不得默认获得修改权限。

## 11 种运行模式

| mode | execution_strategy | 定位 | 默认处置权限 | Step 路由 |
| --- | --- | --- | --- | --- |
| `changed_code_review` | `single_run` | 当前 Git 变更检查 | `report_only` | 按变更影响选择适用 Step |
| `targeted_diagnosis` | `single_run` | 指定问题诊断与根因定位 | `report_only` | Step 2 为主，按证据补充相关 Step |
| `confirmed_bugfix` | `single_run` | 修复已有明确预期和复现证据的 Bug | `confirmed_bugfix_only` | Step 2、4 及受影响的 5、6、7 |
| `regression_verification` | `single_run` | 验证既有修改是否回归 | `report_only` | Step 4 为主，补充相关质量和提交证据 |
| `implementation_completeness_review` | `single_run` | 对照明确需求或验收依据检查完整性 | `report_only` | Step 2–5 及必要的 1、6、7 |
| `incremental_design` | `single_run` | 补充业务边界、测试场景、验收标准和待确认项 | `design_only` | Step 3–5，不修改生产实现 |
| `full_readonly_audit` | `single_run` | 全项目完整只读审计 | `report_only` | 一次性完整执行 Step 1–7，只读 |
| `refactor_risk_assessment` | `single_run` | 评估调用链、兼容性、测试保护和回滚点 | `report_only` | Step 2–4、7 及相关上下文 |
| `merge_readiness_review` | `single_run` | 检查 Git、构建、测试、文档和合并准备 | `report_only` | Step 7 为主，按变更补充适用 Step |
| `hotfix_patch_review` | `single_run` | 检查补丁范围、回归风险、验证和可回滚性 | `report_only` | Step 2、4、7 及受影响的 5、6 |
| `standards_compliance_correction` | `interactive_seven_step` | 对明确范围执行完整七步规范检查；确认具体问题后才允许安全矫正 | `report_only` | 强制按 Step 1–7 顺序交互执行 |

前 10 种任务模式必须遵守所有已加载 Step 的完整规范。其中 `full_readonly_audit` 必须完整执行 Step 1–7；其余 9 种模式按任务加载适用 Step。跳过非适用 Step 时必须记录理由；不得以“按需执行”为由删减已选 Step 内的规范。

前 10 种模式不使用逐 Step 的 `继续` gate。用户发起任务的请求本身，即授权 Skill 在该模式、声明范围和既定权限内直接完成全部适用检查或执行、必要修复、验证和最终报告。内部经过多个 Step 时也不得暂停等待 `继续`，不得读取或消费 `current_authorized_batch` 驱动普通流程。

- `changed_code_review` 默认只读，一次性输出问题、风险和建议。
- `targeted_diagnosis` 一次完成现象分析、调用链定位和根因判断。
- `confirmed_bugfix` 只有满足下方准入条件后，其请求本身才授权在精确 Bug 文件范围内完成最小修复和验证；不再次确认同一 Bug，不处理无关问题。
- `regression_verification`、`implementation_completeness_review`、`refactor_risk_assessment`、`merge_readiness_review` 和 `hotfix_patch_review` 一次完成各自检查、验证和报告。
- `incremental_design` 一次完成设计输出，不修改生产代码。
- `full_readonly_audit` 在单次运行中连续完成完整 Step 1–7，只输出一次最终问题清单，绝不进入修复。

前 10 种模式只有在需要扩大范围、切换模式、缺少无法合理推断的关键业务事实、触发硬边界、需要大规模重构或替换实现方式、验证失败且继续会扩大边界，或请求与模式权限冲突时才停止。停止时报告阻塞原因和建议路由，不得要求用户用 `继续` 模糊授权。

## confirmed_bugfix 准入与初始化

只有问题现象、预期行为来源、根因证据和具体根因文件均明确，并能证明修复不会越过当前 Bug 边界时，才允许进入实际修复并初始化为：

```yaml
mode: confirmed_bugfix
execution_strategy: single_run
remediation_policy: confirmed_bugfix_only
production_code_editable: true

scope:
  target: confirmed_bug_path
  selection_source: bug_call_chain
  specified_files: []
  related_paths: []

editable_scope:
  type: files
  files:
    - 已确认根因文件
  paths: []
```

`editable_scope.files` 必须逐项写入具体文件，禁止使用“相关文件”“Bug 模块”等模糊范围。用户提出明确 Bug 修复请求且上述条件均满足后，不需要用 `继续` 再次确认同一 Bug；在一次 `single_run` 中完成最小修复、必要测试、全部适用验证和最终反馈。

`confirmed_bugfix` 不使用 `current_authorized_batch`、`authorization`、`继续` gate 或 Step 间暂停；这些交互机制只属于 `standards_compliance_correction`。

### confirmed_bugfix 行为变化边界

`confirmed_bugfix` 允许将已经证明错误的行为修正为有明确依据的预期行为。只有以下条件全部满足时才允许修改：

- 问题现象明确。
- 预期行为来源明确。
- 根因证据充分。
- 具体根因文件明确，且逐项写入 `editable_scope.files`。
- 修改直接对应当前 Bug，不越过该 Bug 边界。
- 可以通过测试、类型检查、构建或其他证据验证。
- 不触发数据库、Git、发布、安全等其他硬边界。

允许的修改仅包括：修正错误条件判断、错误字段或数据映射、已确认的状态处理错误、已确认的异常处理错误、导致当前 Bug 的局部调用或实现，以及为当前 Bug 增加具有明确预期依据的必要测试。

本模式只允许将错误行为修正为已确认的正确行为，并在明确根因文件内进行最小实现调整。

即使处于 `confirmed_bugfix`，仍然禁止：

- 新增未经确认的业务规则，或修改与当前 Bug 无关的正常行为。
- 扩大到相邻模块、历史问题或规范清理。
- 批量重命名、移动文件、重构整个模块，或替换框架、依赖、技术方案。
- 改变公共 API；当前 Bug 的明确证据要求修复该契约错误时除外。
- 修改数据库结构、执行 migration、修改权限或安全策略、生产环境或真实数据。
- 在多个互斥修复方案中自行选择，或在预期行为不明确时边猜边改。
- 改变未被当前 Bug 证据支持的业务规则或技术路径。

预期行为不明确、根因仍是推测、修改文件无法确定、存在多个互斥修复方案、需要新增业务规则，或需要架构重构/替换实现方式时，不得边猜边改，必须保持：

```yaml
production_code_editable: false
editable_scope:
  type: none
  files: []
  paths: []
```

根因或预期仍不明确时切换到 `targeted_diagnosis`；修复需要新增业务规则或决定新的状态流转时切换到 `incremental_design`；修复需要改变整体技术路径、拆分架构职责或大规模重构时切换到 `refactor_risk_assessment`。不得继续停留在可修改的 `confirmed_bugfix` 状态。

## 检查范围、修改范围与处置权限

每次运行必须使用以下独立结构：

```yaml
mode: null

scope:
  target: null
  selection_source: null
  specified_files: []
  related_paths: []

editable_scope:
  type: none
  files: []
  paths: []

remediation_policy: report_only
```

- `scope` 决定检查哪些代码和上下文。
- `editable_scope` 决定允许修改哪些文件或路径。
- `scope` 大于 `editable_scope` 合法；读取上下文不代表获得修改权限。
- `editable_scope.type` 至少支持 `none`、`files`、`paths`；必须把最终解析出的文件或路径写入对应列表。
- Git 当前变更只能用于确定检查范围；除非用户明确要求修正且权限字段已记录，否则不能自动成为修改范围。

支持的 `remediation_policy`：

- `report_only`：只检查和报告。
- `safe_fix_only`：仅处理机械性、可验证且无行为变化的问题。
- `confirmed_bugfix_only`：仅修复具有明确预期和证据的已确认 Bug。
- `design_only`：只补充设计、测试和验收场景，不修改生产实现。
- `standards_safe_correction`：按完整 Step 1–7 对已授权范围执行受控规范矫正。

进入 `standards_compliance_correction` 时必须统一初始化为：

```yaml
mode: standards_compliance_correction
remediation_policy: report_only
production_code_editable: false
editable_scope:
  type: none
  files: []
  paths: []
```

用户说“按规范修正、矫正、整改”只授权进入该模式，不授权立即修改任何问题。第一阶段只执行当前 Step 检查、分类并报告。只有用户明确确认具体 `issue_id` 或明确问题批次后，才能为该批次记录 `standards_safe_correction`、`production_code_editable: true` 和精确到文件的 `editable_scope`。

用户确认批次的当轮只记录授权并停止，不得同轮执行；必须等待下一次 `继续` 消费该批次。

`production_code_editable` 是生产代码修改的独立总开关。只有用户明确要求修改、当前 mode/policy 允许且 `editable_scope` 已落到具体文件或路径时才能设为 `true`；`report_only`、`design_only` 和所有全量只读阶段必须保持 `false`。`cleanup_forbidden` 与 `refactor_forbidden` 是附加否决项：任一为 `true` 时，对应清理或重构即使落在修改范围内也不得执行。

任何修改必须同时满足：

```text
当前 mode 允许
AND remediation_policy 允许
AND 文件位于 editable_scope
AND 修改生产代码时 production_code_editable 为 true
AND cleanup_forbidden / refactor_forbidden 未否决该操作
AND 修改符合当前 mode 对业务行为、外部语义和实现变化的明确限制
AND 符合该模式的行为边界
AND 不触发数据库、Git、发布、安全等硬边界
```

检查到问题不代表自动获得修改权限。任一条件不满足时，只能记录和报告。

### 模式行为边界对照

- `standards_compliance_correction`：不得改变业务逻辑、外部行为或实现方式，只做无行为变化的安全规范矫正。
- `confirmed_bugfix`：允许将已证明错误的行为改为有明确依据的预期行为，只允许在具体根因文件内做最小实现调整。
- 其他模式：按照各自 `mode`、`editable_scope` 和 `remediation_policy` 的边界执行。

模式切换必须先清空 `editable_scope`，将 `remediation_policy` 重置为 `report_only`，并将 `production_code_editable` 设为 `false`；`cleanup_forbidden` 和 `refactor_forbidden` 也必须按新模式重新计算。不得继承上一模式的文件权限、处置权限、限制标记或待修正批次。随后按新请求重新授权。

## 统一问题分类与记录

所有模式、所有 Step 必须使用同一组分类；Step reference 只能补充本 Step 的归类例子和安全边界，不得重新定义分类含义：

```yaml
issue_classification:
  - safe_standard_correction
  - confirmed_bug
  - report_only_risk
  - incremental_design_required
  - refactor_assessment_required
  - blocked_out_of_boundary
```

- `safe_standard_correction`：同时具备明确规范依据、唯一或高度确定的修正结果、当前检查与授权范围、无业务/外部行为/API/数据/错误/状态/权限/默认值/查询/排序/过滤变化、无实现路径/架构/依赖变化，并可用静态检查、构建或测试验证。
- `confirmed_bug`：存在明确运行错误、失败测试、公共契约冲突或可证明错误行为；只能在 `confirmed_bugfix` 模式处理。
- `report_only_risk`：存在风险或不规范，但缺少唯一、安全的修正方式；只能报告。
- `incremental_design_required`：需要补充业务规则、异常路径、状态转换、测试预期、验收标准或兼容要求；转入 `incremental_design`。
- `refactor_assessment_required`：需要拆分职责、移动模块、引入抽象、替换技术方案或调整调用路径；转入 `refactor_risk_assessment`。
- `blocked_out_of_boundary`：涉及权限、数据库执行、生产环境、发布、安全策略、Breaking API 或其他硬边界；不得处理。

每个问题至少记录：

```yaml
- issue_id: null
  step: null
  classification: null
  evidence: null
  affected_files: []
  expected_behavior_source: null
  behavior_change_risk: none
  implementation_change_risk: none
  allowed_in_current_mode: false
  suggested_mode: null
  remediation_status: not_needed
```

所有策略都先执行：

```text
发现问题
→ 判断问题分类
→ 判断当前模式是否允许处理
→ 判断是否有明确修改授权
```

- `single_run`：在当前请求已经授予的 mode、scope、editable_scope 和 remediation_policy 内直接处理允许事项，完成验证后一次性报告；不等待问题批次确认。检查到的越权问题只报告并给出建议路由。
- `interactive_seven_step`：当前 Step 只读检查后报告问题；可处理问题也必须等待用户明确确认具体 `issue_id` 或批次，普通 `继续` 不构成确认。

禁止发现问题后越权修正；禁止把不同性质的问题合并成模糊批次；禁止为修正一个问题顺手处理相邻问题；禁止为通过规范检查改变业务行为或实现方式。

## 全量检查与全量规范矫正

用户要求“全量检查项目”时固定使用：

```yaml
mode: full_readonly_audit
editable_scope:
  type: none
  files: []
  paths: []
remediation_policy: report_only
production_code_editable: false
```

该模式强制只读，并以 `single_run` 连续完成完整 Step 1–7；内部 Step 不是交互 gate，只在结束时一次性输出问题清单、证据、风险和建议路由。

用户要求“全量按规范整改”时仍使用 `standards_compliance_correction + interactive_seven_step`：从 Step 1 开始逐步只读检查、报告和确认，不得退化成一次性全项目自动整改。普通 `继续` 不构成问题或批次确认，也不能让 `full_readonly_audit` 进入修复。

## 规范合规矫正

`standards_compliance_correction` 必须逐步完整执行：

```text
Step 1 命名与放置
→ Step 2 代码质量
→ Step 3 架构与分层
→ Step 4 测试覆盖
→ Step 5 文档一致性
→ Step 6 注释规范
→ Step 7 Git、验证、CI/CD 和提交准备
```

每个 Step 都必须加载对应 reference、完成检查、记录问题和处置结果。环境不适用的具体检查项可以按条件标记 `skipped` 并说明原因，但不得跳过整个七步阶段或删减 reference 中的规范。

每个 Step 都必须从 `report_only + production_code_editable: false + editable_scope.type: none` 开始。检查报告生成稳定 `issue_id` 后，等待用户明确确认具体问题或批次；普通 `继续` 不构成确认。获得确认后，只允许创建一个精确授权批次：

```yaml
remediation_policy: standards_safe_correction
production_code_editable: true
editable_scope:
  type: files
  files:
    - 明确授权文件
  paths: []

remediation:
  pending:
    - batch_id: null
      issue_ids: []
      allowed_files: []
      allowed_actions: []
```

修正完成或失败后立即撤销修改授权，将 `production_code_editable` 设为 `false`、`remediation_policy` 恢复为 `report_only`、`editable_scope` 恢复为 `none`，并把授权标记为已消费。进入下一 Step 时不得继承当前 Step 的授权、批次、文件或动作。

本模式只允许处理机械性规范问题、明确且唯一的安全矫正、不影响业务行为和实现方式的问题，以及用户已经明确授权的具体问题批次。

只允许矫正同时满足以下条件的问题：

- 有明确的 Step 规范或项目既有约定作为依据。
- 位于已声明的 `editable_scope`。
- 不改变业务逻辑、外部可观察行为、API、数据或错误语义。
- 不改变状态流转、权限规则、业务条件、默认值、查询、排序、过滤或异常行为。
- 不替换技术方案、依赖、框架、状态管理、数据访问方式或实现路径。
- 不改变事务边界、事务顺序或业务编排顺序。
- 不进行大规模重构、历史文件批量移动或重命名。
- 能通过 build、typecheck、test、lint 或 schema validation 等证据验证。

可安全矫正的典型问题：当前改动中的未使用 import、明确类型错误、明确错别字、与实际行为矛盾的注释、本次新增代码的命名违规、有明确预期依据的测试缺口、本次改动导致的文档不一致，以及本次新增代码引入的简单分层违规。

以下内容只能报告，不得在本模式修改：

- 业务逻辑、状态流转、权限规则、API 或数据语义变化。
- 默认值、查询、排序、过滤、异常或错误语义变化。
- 架构重构，历史文件的大量移动或重命名。
- 替换依赖、框架、状态管理或数据访问方式。
- 缺少明确业务依据的测试预期。
- 文档与实现冲突但无法判断哪一方正确。

根据问题性质，建议转入 `confirmed_bugfix`、`incremental_design` 或 `refactor_risk_assessment`。普通 `继续` 不得越过此路由。

## Runtime 执行策略

`execution_strategy` 只允许：

- `single_run`：前 10 种任务模式。
- `interactive_seven_step`：仅 `standards_compliance_correction`。

### 单次运行模式规则

`single_run` 固定执行：

```text
进入模式
→ 完成全部适用检查或执行
→ 完成必要修复和验证
→ 一次性最终报告
```

内部 Step 只用于加载检查规范，不是用户交互 gate。不得创建 Step 间等待状态，不得读取、等待或消费 `继续`，也不得使用 `current_authorized_batch`、`authorization` 或 `remediation.pending` 驱动普通流程。

### 七步交互模式规则

`interactive_seven_step` 才使用 Step 间暂停、稳定 `issue_id`、用户确认批次、`current_authorized_batch`、`authorization` 和 `继续` gate。每个检查或修正阶段开始前重新读取 Runtime；已经在本次运行标记为 `done` 的检查不得重复执行。阶段结束后记录执行项、跳过项、问题、修正、验证、风险和阻塞。

`steps` 中的阶段状态保留 `done`、`failed`、`skipped`；修正状态保留 `not_needed`、`pending_user_continue`、`completed`、`validation_failed`、`blocked_out_of_boundary`。其中 `pending_user_continue` 只能表示“明确授权批次正在等待消费下一 Runtime gate”，不能表示仅凭 `继续` 新增修改权限。越过模式、范围、处置权限或硬边界的问题必须标记 `blocked_out_of_boundary`。验证失败必须标记 `validation_failed` 并停止。

用户确认问题或批次时，把授权写成不可扩张的快照：

```yaml
current_authorized_batch: null
authorization:
  issue_ids: []
  allowed_files: []
  allowed_actions: []
  granted_by: null
  consumed: false
```

`issue_ids`、`allowed_files` 和 `allowed_actions` 必须逐项明确，且与 `remediation.pending` 中的单个批次一致。禁止用“修复本 Step”“处理类似问题”“相关文件”等模糊表述创建授权。

一个授权批次只能包含当前同一 Step、同一问题分类和同一类安全动作；不得跨 Step、跨分类或把行为敏感问题与安全规范问题合并。需要处理多个批次时，必须分别确认并逐次消费。

在 `standards_compliance_correction` 中，每次 `继续` 只允许一个分支：

1. 存在与 `current_authorized_batch` 一致且 `authorization.consumed: false` 的授权批次：只执行该批次、验证、撤销权限、输出修正结果并停止。
2. 不存在待执行授权批次，且当前 Step 只读检查已经完成并报告：只进入下一个 Step 的只读检查、输出该 Step 报告并停止；不得顺带修正问题。

Step 1 检查由进入规范矫正模式的请求触发。后续 `继续` 必须优先消费已经存在的授权批次；只有不存在待执行批次时才能进入下一 Step。Step 7 完成后输出最终汇总并重置 Runtime。

`继续` 只能推进当前状态，不能：

- 扩大 `scope` 或 `editable_scope`。
- 改变 `remediation_policy`、`production_code_editable` 或其他处置权限。
- 切换 `mode`，或把只读模式变成修复模式。
- 确认问题编号、确认问题批次或自动创建修改授权。
- 默认授权修复当前 Step 的全部问题。
- 同时完成检查和修正、多个修正批次或多个 Step。
- 让全量审计进入修复。
- 授权修改规范矫正中的行为敏感问题。

问题只有已明确纳入当前 `editable_scope`、符合当前 `remediation_policy`，并已作为确定批次写入 `remediation.pending` 时，`继续` 才能消费其修正阶段。普通 `继续` 永远不等于问题确认；未确认问题保持报告状态并允许进入下一 Step。

修正阶段开始时把该批次从 `pending` 移到 `active`。验证通过后移入 `remediation.completed`；验证失败时记录失败命令、关键输出和风险。无论完成或失败，都必须将 `authorization.consumed` 设为 `true`，清空 `current_authorized_batch` 和 `remediation.active`，撤销生产代码修改权限并停止；不得用新的 `继续` 自动创建授权、扩大边界或绕过失败。

当前 Step 顺带发现但属于下一 Step 的问题只能记录到 `next_step_candidate`；不得据此提前修改或推进下一 Step。

## 环境适配与 Profile 条件加载

每次检查按以下顺序加载规则：

1. 读取 `project-environment-profile.md`，根据当前 `scope` 识别涉及的 `components`、`persistence`、`contracts` 和 CI workflow。
2. 加载当前模式需要的通用 Step reference；通用规则始终执行，不依赖 Profile。
3. 根据涉及组件的 `language`、`framework`、`test_runners`，以及相关持久化项的 `orm_or_client` 和契约项的 `type`，只加载 `references/profiles/` 中匹配的 Profile。
4. 同一范围涉及多个组件或多种工具时，分别加载匹配 Profile，并按组件记录适用性；不得一次加载与当前范围无关的全部 Profile。
5. 没有匹配 Profile 时，继续完整执行通用命名、质量、边界、测试、文档、注释和 Git 检查，以当前代码、配置、测试和环境档案为事实来源，不猜测框架规则；在报告中记录专用 Profile 未覆盖，并可建议新增 Profile。

`persistence.schema_paths` 或 `migration_paths` 指向的内容变化时，执行环境档案声明的状态检查和 validation command，并报告数据库迁移状态。只有环境档案确认存在 CI/CD 时才检查对应 workflow。与当前环境或范围无关的附加 Profile 规则标记为 `skipped` 并写明原因；不得因此跳过整个 Step。

## 修改后的强制验证

任何模式只要修改了文件，必须按顺序完成：

1. 依据实际 diff 确认修改文件，不依赖预期列表。
2. 将实际修改文件与 `editable_scope` 比对；发现越界修改立即停止并报告，不自行清理或扩权。
3. 对全部修改文件执行所有适用的 Step 规范检查，不得只复查触发修改的单一问题。
4. 根据环境事实执行必要的 build、typecheck、test、lint 或 schema validation。
5. 检查 diff 与验证证据，确认未改变该模式禁止改变的业务行为、外部语义或实现方式。
6. 输出修改摘要、验证结果、跳过理由、剩余风险和未处理问题。

单个针对性测试不能代表全部通过。typed source 或公共契约变化时，必须执行环境档案中适用的 typecheck、build 或契约验证；单元测试不能替代类型或契约检查。持久化 schema 或 migration 路径变化时，必须执行环境档案声明的可用 schema validation。

## 数据库迁移、Git 与 CI/CD 边界

- 环境档案中任一 `persistence.schema_paths` 或 `migration_paths` 发生变化时，必须报告 runtime 数据库迁移状态：`not_applicable`、`created_only`、`validated`、`applied` 或 `not_confirmed`。
- 不执行数据库迁移、不直接连接或修改 runtime 数据库。只有开发者明确目标数据库和具体命令并单独确认后，才能转入对应流程；数据库命令报错时必须抛出错误并停止。
- CI/CD 只做条件性轻量检查：检查 workflow 是否具备 clean install、build、test、migration 等适用步骤；不得执行 release 或 deploy job。
- 未经开发者明确要求，不执行 stage、commit、push、创建分支、reset、checkout 或 stash。
- 任何提交准备前都检查并报告 `git status --short`、`git diff --cached --name-status` 和 `git ls-files --others --exclude-standard`。
- 不使用 `git add -f` 添加被忽略路径，除非用户明确要求提交具体被忽略文件。
- 不混入与当前任务无关的工作区改动。若发现意外暂存、误提交或提交范围异常，停止并按项目规则请求确认。

## Step 1–7 规范路由

Step reference 中的现有规范全部保留并保持强制性；本轮运行治理不得覆盖、降级或把其中规则改成可选项。

1. `references/step1-naming-convention.md`：命名、文件放置、路由/模块命名、术语一致性。
2. `references/step2-code-quality.md`：常见 Bug、死代码、错误处理、数据 shape、类型契约质量。
3. `references/step3-architecture-layer.md`：项目既有入口、传输、业务编排、数据访问、外部能力与共享契约边界。
4. `references/step4-test-coverage.md`：测试影响、缺失边界用例、合适的 package 命令。
5. `references/step5-documentation.md`：docs/API/schema/README 与代码行为一致性。
6. `references/step6-comment-standard.md`：有效注释和项目本地文件头规范。
7. `references/step7-code-commit.md`：Git 状态、变更/未跟踪文件、暂存范围、验证摘要、CI/CD 和提交准备。

每次只加载当前需要执行的 Step reference，并按当前范围加载匹配 Profile。前 10 种模式依据路由在单次运行中连续完成适用 Step；`full_readonly_audit` 在单次运行中连续加载全部七个 Step，不在 Step 间暂停。只有规范矫正按七步交互策略逐 Step 加载、报告和暂停。

## 报告格式

`single_run` 在内部累计各 Step 证据，只在全部适用任务和验证完成后输出一次最终报告，不向用户逐 Step 停顿。`interactive_seven_step` 在当前 Step 检查或单个修正批次结束后输出阶段报告并停止。

报告至少包含：

- `运行模式`：`mode` 与 `mode_source`。
- `当前阶段`：Step、reference 和 inspection/remediation phase。
- `检查范围`：`scope`。
- `修改范围`：`editable_scope`。
- `处置权限`：`remediation_policy` 与 `production_code_editable`。
- `问题清单`：证据、风险、是否可在当前模式处理、建议路由。
- `修改摘要`：实际修改文件和内容；无则写 `无`。
- `验证结果`：命令与 pass/fail/skipped；跳过必须说明原因。
- `剩余风险与阻塞`。
- `下一阶段`：仅 `interactive_seven_step` 描述当前模式、范围和权限内可推进的一个阶段；`single_run` 不输出等待 `继续` 的下一阶段。

最终报告必须汇总执行/跳过/失败的 Step、问题与处置结果、修改文件、验证证据、CI/CD 状态、相关时的数据库迁移状态和剩余风险。最终报告输出后，将 Runtime 状态重置为初始模板。

## 硬边界

- 不执行上线、发布、发布就绪检查（Release readiness）、生产门禁（production gate）或严格企业级安全验收；切换到专门的 release/security gate Skill。
- 不写业务规划产物或业务产品内容；需要设计决策时转入相应规划流程。
- 不在规范矫正中改变业务逻辑、外部行为、API/数据/错误语义、状态流转、权限或技术实现路径。
- 不自动执行大规模重构、数据库迁移、真实数据修改、安全策略修改、Breaking API contract 变更或真实环境变量/密钥修改；`.env.example` 的文档性检查仍受明确范围约束。
- 除稳定环境事实变化外，不修改 `project-environment-profile.md`。
- 不在 `inspection-runtime-state.md` 中积累跨运行上下文。
- 保留与当前任务无关的所有工作区改动。

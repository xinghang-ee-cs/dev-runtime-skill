---
name: ai-code-inspection
description: 通用代码检查、诊断与受控修复 Skill，按 10 种真实工作场景路由当前改动检查、具体问题诊断、已确认 Bug 修复与回归、需求完整性核查、业务规则补全、全项目审计、重构风险评估、合并就绪检查、紧急修复和七步规范治理。适用于 review 当前变更、定位异常、修复证据充分的 Bug、对照需求验收、补齐行为规则、摸清项目现状、评估重构、检查 PR/MR/合并准备、处理阻断故障或按工程规范检查代码。回归验证只作为修复后的内部阶段；只有规范性检查使用交互式 Step 1–7。不要用于上线、发布、生产门禁、严格安全验收或无边界的大规模重构。
---

# AI Code Inspection

按用户所处的真实工作阶段选择场景，再确定范围、权限、执行流程和后续路由。不得用单个宽泛词机械决定场景，也不得把读取范围当作修改授权。

本 Skill 不承担上线、部署、生产门禁或严格安全验收。目标项目存在专门的 release/security 流程时，在检查结束后移交；不存在时只报告边界，不虚构对应 Skill。

## 事实源与文件职责

项目级可变状态统一保存在目标项目根目录 `.runtime/ai-code-inspection/`。Skill 目录只保存静态规则、references、Profiles、agents 配置和 Runtime 初始模板，不保存目标项目的运行实例。

正式执行前读取：

1. `.runtime/ai-code-inspection/project-environment-profile.md`：稳定环境事实 SoT，只记录从目标仓库确认的工作区、组件、语言、框架、运行时、持久化、契约、测试、验证命令和 CI/CD 事实。
2. `.runtime/ai-code-inspection/inspection-runtime-state.md`：本次运行状态与权限快照；最终报告后重置为空闲模板，不积累跨运行上下文。

文件职责保持低熵：

- `SKILL.md`：唯一 Runtime Governance Source，独占场景、路由、权限、状态切换、gate 和报告规则。
- `references/README.md`：只提供场景概览、轻量路由和执行路线。
- `references/step1-*.md` 到 `step7-*.md`：只提供检查标准和本 Step 安全边界，不定义场景或 Runtime 生命周期。
- `references/profiles/`：只补充技术栈特有规则，不重新定义场景、范围、权限、问题分类或生命周期。
- `assets/runtime-templates/`：只提供未初始化环境档案和空闲 Runtime 模板，用于首次初始化目标项目。

Runtime 目录或文件不存在时，只按当前任务需要从 `assets/runtime-templates/` 初始化目标项目的 `.runtime/ai-code-inspection/`：环境档案必须根据目标仓库的 manifest、workspace 配置、源码入口、测试配置、持久化定义、公共契约、CI/CD workflow 和已有环境文档填写。不得从 Skill 示例或其他项目复制稳定事实；无法可靠确认的字段保持未确认并报告。

## 启动与场景路由

每次新运行：

1. 读取或按需初始化环境事实源，并将 Runtime 重置为初始模板，撤销上一运行的修改权限和授权批次。
2. 判断用户工作阶段、处理对象、期望结果，以及问题、需求、紧急、Git 和规范上下文。
3. 记录 `requested_scene`、`effective_scene`、`scene_source`、`matched_signals`、必要的 `preserved_intent` 和 `fallback_reason`；内部阶段及其来源只写入 `execution`。
4. 分别解析 `scope`、`editable_scope` 和 `remediation_policy`，再计算 `execution.strategy`。
5. 记录 `modifier`、`modifier_source` 和系统时间生成的 `run_started_at`。
6. 只有场景、范围、权限和执行策略无歧义后才开始执行。

路由时先判断完整语义：工作阶段、处理对象、期望检查/诊断/修改/设计/评估/审计/交付结论、具体问题与根因、需求或验收依据、真实紧急性、Git 合并上下文，以及核心判断依据是否为工程规范。

`scene_source` 只记录用户场景的进入来源，使用 `explicit_scene`、`contextual_scene` 或 `inferred_default`。`automatic_internal_phase` 只允许写入 `execution.internal_phase_source`，不得覆盖用户场景来源。

## 10 个用户场景

| scene_id | 中文场景 | strategy | 默认范围 | 默认权限 | Step 路由 |
| --- | --- | --- | --- | --- | --- |
| `changed_code_review` | 当前改动日常检查 | `single_run` | 当前 Git 变更及必要只读上下文 | `report_only`，不可修改 | 按影响加载适用 Step |
| `targeted_diagnosis` | 具体问题根因诊断 | `single_run` | 问题调用链及必要只读上下文 | `report_only`，不可修改 | Step 2 为主，按证据补充 |
| `confirmed_bugfix` | 已确认问题的修复与回归闭环 | `single_run` | 已确认 Bug 调用链 | 准入后仅精确文件 | Step 2、4 及受影响 Step |
| `implementation_completeness_review` | 需求实现完整性核查 | `single_run` | 完成对象及需求/验收依据 | `report_only`，不可补开发 | Step 2–5 及必要 Step |
| `incremental_design` | 业务规则与验收边界补全 | `single_run` | 规则缺口及必要业务上下文 | `design_only`，不可改生产代码 | Step 3–5 |
| `full_readonly_audit` | 全项目现状审计 | `single_run` | 全项目 | `report_only`，全程只读 | 一次性完整 Step 1–7 |
| `refactor_risk_assessment` | 重构前的影响与风险评估 | `single_run` | 结构对象及影响链 | `report_only`，不可重构 | Step 2–4、7 及相关上下文 |
| `merge_readiness_review` | 代码合并前的交付就绪检查 | `single_run` | 交付单元、工作区及暂存区 | `report_only`，无 Git 写权限 | Step 7 为主，补适用 Step |
| `hotfix_patch_review` | 关键阻断问题的紧急修复闭环 | `single_run` | 故障链、最小补丁及相邻高风险路径 | 初始只读；准入后仅精确文件 | Step 2、4、7 及受影响 Step |
| `standards_compliance_correction` | 规范性检查与受控矫正 | `interactive_seven_step` | 按规范检查范围解析；无可靠范围时为 `unresolved` | 初始只读；逐批确认后精确矫正 | 强制顺序 Step 1–7 |

用户可主动进入的场景只能是以上 10 个。`regression_verification` 只属于场景 3 的内部阶段，不是独立用户场景。

### 场景 1：当前改动日常检查

用于一轮修改后快速发现本轮变更中的明显 Bug、类型/data shape/错误处理问题、契约问题、局部架构越界、必要测试和文档遗漏，以及无关文件。

普通“检查这次改动”“看看刚才改的代码”“Review 当前变更”进入本场景。“检查修改的代码”中的“修改”描述检查对象，不授予修改权限。不得扩成全项目扫描、七步交互治理、需求完整性核查、直接修复或合并就绪判断。

### 场景 2：具体问题根因诊断

用于用户已观察到报错、失败、异常或不符合预期的行为，但根因未知的情况。一次完成并输出：实际现象、预期行为来源、调用链与关键证据、直接原因、根本原因、具体根因文件、修复准入是否满足和建议后续场景。

不得顺手修改、扫描全项目、自行创造业务规则或把历史架构问题直接重构。

### 场景 3：已确认问题的修复与回归闭环

只有以下条件全部满足才允许实际修改：

- 问题现象明确，预期行为有可靠来源，根因证据和具体根因文件明确。
- 修复范围可逐文件记录，修复方案唯一或高度确定，不需创造业务规则或大规模重构。
- 修改可验证，且不触发数据库、生产、权限、发布、安全或其他硬边界。

准入不足时保留原始修复意图并先完成只读诊断：

```yaml
routing:
  requested_scene: confirmed_bugfix
  effective_scene: targeted_diagnosis
  preserved_intent: repair
  fallback_reason: confirmed_bugfix_prerequisites_not_met
```

用户已明确要求修复时，不得仅因初始根因未知就要求用户重新提出修复。诊断在同一次 `single_run` 中补齐现象、预期来源、根因证据、具体文件、确定修复方案和精确范围，且没有触发其他边界时，必须重新计算 `effective_scene` 并自动返回 `confirmed_bugfix`：

```text
准入诊断 → 返回 confirmed_bugfix → 建立精确 editable_scope
→ 最小修复 → 基础验证 → 撤销修改权限
→ 自动进入 regression_verification → 回归 → 一次最终报告
```

返回修复时清空 `fallback_reason`，将 `remediation_policy` 设为 `confirmed_bugfix_only`、`production_code_editable` 设为 `true`，只把已确认根因文件和必要测试文件写入 `editable_scope.files`；不得把诊断读取范围继承为修改权限。

预期不明确、根因仍为推测、存在互斥方案、需要业务选择/新规则、公共契约或数据库结构变化、大规模重构、技术路径替换、任何硬边界或无法确定精确文件时，必须停止修改。规则不明确转场景 5，结构调整转场景 7，其他硬边界标记 `blocked_out_of_boundary`。

只允许修正导致当前问题的错误条件、字段/映射、状态/异常处理或局部调用，增加必要测试，以及更新因本次修复明确失效的局部文档或注释。禁止无关清理、顺手重构、修改其他业务规则、扩大文件范围或替换依赖/框架。

只有实际完成代码修复且基础验证通过后，自动进入内部 `regression_verification`；进入前撤销全部代码与数据库临时权限。内部回归必须确认原问题消失、预期行为成立、原有正常路径未破坏、关键失败/边界路径正确、实际 diff 未越界，并有自动化测试或可重复验证依据。回归失败时建立新的只读诊断或路由到场景 5/7，不继承旧授权。

### 场景 4：需求实现完整性核查

必须同时存在明确完成对象和需求/验收依据。事实源可为 PRD、已确认规划、用户故事、验收标准、公共契约、UI 设计、任务清单或用户明确确认。

建立矩阵：`需求项 → 预期业务流程 → 客户端/入口实现 → 服务/核心实现 → 数据与状态变化 → 异常/边界路径 → 测试证据 → 完成状态`。完成状态至少包含 `已完成`、`部分完成`、`未实现`、`无法确认`、`已取消或不适用`。

不得自动补开发。明确漏实现则输出开发任务；规则不明转场景 5；已实现但行为错误转场景 2 或 3；需结构调整转场景 7。

### 场景 5：业务规则与验收边界补全

用于多个合理但互斥方案并存，状态流转、异常/取消/重试/权限/兼容规则缺失，或文档、代码、测试冲突而无法判断正确行为的情况。

输出规则缺口、已知事实、冲突/不确定项、可选方案、推荐规则及依据、待确认事项、正常/失败/取消/重试路径、状态转换与非法跳转、可测试验收标准和后续实现范围建议。

“补充”不是绝对入口。补测试、README 或注释不自动进入本场景；只有补充对象是业务规则、流程边界、行为预期或验收依据时才进入。

### 场景 6：全项目现状审计

用于项目接手、阶段收口、下一期准备、重构准备、移交或系统治理前建立全项目真实基线。以 `single_run` 全程只读完整执行 Step 1–7；内部 Step 不是交互 gate，只输出一次最终报告。

报告包含总体判断、真实现状基线、风险分级、问题分类、问题领域地图、持久化迁移状态、CI/CD 状态、治理顺序及每个问题的建议后续场景。禁止修复任何问题。“审计代码是否符合规范”的核心依据是规范，固定进入场景 10。

### 场景 7：重构前的影响与风险评估

必须同时存在明确结构调整对象，对模块、职责、调用链、事务边界或实现路径的调整意图，且当前目标是评估而非立即修改。

确认真实调用链、职责分布、公共契约、数据/事务边界、依赖、测试保护、发布和回滚条件；输出结构事实、问题与成因、重构目标、不变约束、影响范围、行为/契约/数据/依赖风险、方案对比、分阶段实施建议、每阶段验证与回滚点，以及是否建议现在执行。

“评估”不是绝对入口：评估功能完整性进场景 4；评估规范进场景 10；评估 Bug 是否修好属于场景 3 内部回归。

### 场景 8：代码合并前的交付就绪检查

必须存在 commit、PR/MR、分支、合并、工作区或代码提交等明确交付上下文；业务表单的“提交前检查”不属于本场景。

检查任务与变更一致性、无关文件、临时代码、测试/build/typecheck、文档/契约、schema/migration、工作区/暂存区、CI/CD、commit 拆分和合并条件。结论固定为 `ready`、`conditionally_ready` 或 `not_ready`。

未经明确授权不得 stage、commit、push、创建分支、reset、checkout、stash 或删除/清理文件；本场景自身不执行任何 Git 写操作。

### 场景 9：关键阻断问题的紧急修复闭环

必须同时具备具体问题、明确修复/恢复意图，以及真实紧急性、阻断性或生产影响。“线上故障”“核心功能不可用”“hotfix”“紧急补丁”“立即恢复”是强信号；“快速检查代码”不是。

固定执行：

```text
紧急程度和影响确认 → 回滚/止血/向前修复判断 → 快速根因诊断
→ 锁定最小补丁范围 → 补丁修改 → 核心回归
→ 高风险相邻路径检查 → 补丁交付就绪
```

初始只读。用户已明确要求紧急修复但仍需诊断时，记录 `requested_scene: hotfix_patch_review`、`effective_scene: targeted_diagnosis`、`preserved_intent: hotfix` 和 `fallback_reason: hotfix_prerequisites_not_met`。诊断补齐根因、预期、确定补丁方案、精确文件和硬边界准入后，在同一次 `single_run` 中将 `effective_scene` 自动恢复为 `hotfix_patch_review` 并清空 `fallback_reason`，不要求用户再次提出 hotfix。准入后临时使用 `hotfix_patch_only` 和精确 `editable_scope`；不得继承诊断读取范围。

紧急性不得成为猜测修改、扩权、顺手重构、跳过验证、操作生产、部署、migration 或 Git 写操作的理由。补丁完成、失败或进入回归/交付检查前先撤销全部临时权限。

报告故障与影响、紧急程度、回滚/止血/修复判断、根因证据、实际补丁文件、核心验证、未完成验证与风险、回滚方式、部署前人工事项、永久治理任务及固定 `hotfix_readiness`：`ready`、`conditionally_ready`、`not_ready` 或 `blocked`。`conditionally_ready` 必须列出 `conditions`；不得生成其他状态名。

### 场景 10：规范性检查与受控矫正

用户以“规范、规范性检查、按规范检查、代码规范、规范整改/矫正、七步规范检查、是否符合规范”为核心判断依据时固定进入本场景；即使同时出现“修改”“代码”“审计”也不得改路由。

进入 Step 1 前按以下顺序解析范围：

1. 用户明确文件或模块：范围为指定对象及必要只读上下文。
2. 用户明确“修改代码、当前改动、本轮代码”：范围为当前 Git 变更及必要只读上下文，不得扩大为全项目。
3. 用户明确全项目/整个仓库规范检查：范围为全项目，仍按 Step 1–7 交互执行、从只读开始，不转场景 6 或一次性自动整改。
4. 用户只说“做规范检查”：优先复用当前对话中可可靠确定的最近代码范围；没有可靠范围时记录 `scope.target: unresolved`，停止并请求明确文件、模块、当前 Git 变更或全项目。不得先扫描全项目，也不得创建修改权限。

固定以 `interactive_seven_step` 顺序执行 Step 1–7。每个 Step 从 `report_only + production_code_editable: false + editable_scope.type: none` 开始：加载对应 reference、完成检查、生成稳定 `issue_id`、分类、输出阶段报告并停止。

只有用户明确确认具体 `issue_id`，或同一 Step、同一分类、同一安全动作的问题批次后，才记录一个精确授权批次。确认当轮只记录授权并停止；下一次 `继续` 只消费该批次、验证、撤销权限、报告并停止。无待执行批次时，`继续` 只进入下一个 Step 的只读检查。普通 `继续` 永远不能确认问题、创建权限、扩范围、切场景或让全量审计进入修复。

规范检查发现的明确 Bug 转场景 3；规则缺口转场景 5；架构重构转场景 7；其他硬边界阻塞。不得在本场景处理这些问题。

## 场景语义、冲突与默认路由

完整语义优先于宽泛动词：

- “对修改的代码做规范性检查” → 场景 10；“检查修改的代码” → 场景 1。
- “修改已经定位的问题” → 请求场景 3；准入不足时实际执行场景 2。
- “评估功能是否完整” → 场景 4；“评估拆分模块的风险” → 场景 7。
- “快速检查当前代码” → 场景 1；“线上问题快速修复” → 场景 9。
- “准备提 PR，检查工作区” → 场景 8；“提交表单前检查字段”不进入场景 8。
- “全量审计后自动修复” → 场景 6 且只读，修复意图因场景边界被拒绝。
- “修复完成后验证”不创建新场景；属于本次场景 3 的已执行修复时自动完成，否则先确认现有修复上下文。

仅在没有明确场景语义时使用默认推断。不得把普通检查扩成全项目审计，不得用“修改、补充、完整、评估、检查”等单词单独决定场景，也不得把“修改”自动解释为生产代码授权。

## 场景切换与阻塞路由

场景切换先保存原始请求、必要证据和切换原因，再撤销临时权限并恢复安全默认状态：

```yaml
remediation_policy: report_only
production_code_editable: false
database_operation_authorized: false
editable_scope:
  type: none
  files: []
  paths: []
current_authorized_batch: null
authorization: null
cleanup_forbidden: true
refactor_forbidden: true
```

随后重新计算新场景的 strategy、scope、editable_scope、remediation_policy、独立权限、适用 Step 和当前阶段。可以保留现象、预期来源和根因证据，但不得继承旧修改范围、允许动作、数据库/Git 授权、修正批次或临时例外。

自动路由只允许：

- 场景 3 准入不足 → 保留 `repair` 意图进入只读诊断；同次运行内补齐准入 → 自动返回场景 3；修复和基础验证通过 → 内部回归。
- 场景 3 回归发现预期缺失 → 场景 5；需要结构调整 → 场景 7；新 Bug → 新建场景 2 范围。
- 场景 4 发现规则缺口 → 场景 5；错误实现 → 场景 2/3；结构问题 → 场景 7。
- 场景 10 发现 Bug/规则缺口/重构需求 → 分别建议场景 3/5/7，不继承规范矫正授权。
- 任一场景触发未经独立明确授权的真实数据库动作、生产、发布、安全、权限或 Breaking API 硬边界 → `blocked_out_of_boundary` 并停止。

## Runtime 与执行策略

首次初始化和每次重置使用 `assets/runtime-templates/inspection-runtime-state.md`。`cleanup_forbidden` 与 `refactor_forbidden` 始终恢复为 `true`，不得重置为 `false`、`null` 或删除。

`routing.effective_scene` 使用场景表中的 `scene_id`；不得把 `regression_verification` 写入 `requested_scene`。`preserved_intent` 只使用 `repair`、`hotfix` 或 `null`，且只在用户已明确要求修复、当前需要先完成准入诊断时使用。

场景 1–9 使用 `single_run`：在既定范围与权限内连续完成全部适用检查、允许的修改、验证和最终报告；内部 Step 不是用户 gate，不等待或消费 `继续`。

场景 10 独占 `interactive_seven_step`。一个授权批次只能包含当前同一 Step、同一分类和同一类安全动作，并逐项记录 `issue_ids`、`allowed_files`、`allowed_actions`、`granted_by` 和 `consumed: false`。执行后无论成功或失败，都消费并清空批次、撤销权限、恢复安全默认状态后停止。

场景 10 只允许无业务行为、外部语义、API/数据/错误/状态/权限、默认值、查询/排序/过滤、事务、依赖、架构和实现路径变化的机械性安全矫正。不能证明等价的问题只能报告或转场景。

## 范围、权限与问题分类

`scope` 决定可读取和检查的对象；`editable_scope` 决定可修改对象。`scope` 大于 `editable_scope` 合法，反向不合法。任何修改必须同时满足：场景允许、策略允许、目标位于精确修改范围、生产代码开关为 `true`、附加否决项未阻止、符合场景行为边界且未触发硬边界。

`production_code_editable` 与 `database_operation_authorized` 是相互独立的权限，任一字段不得推导、覆盖或撤销另一个字段。每个 `true` 都必须分别满足自身准入；相关动作完成、失败、切换场景或最终报告后撤销对应临时权限。

支持的 `remediation_policy`：`report_only`、`confirmed_bugfix_only`、`design_only`、`standards_safe_correction` 和紧急补丁临时使用的 `hotfix_patch_only`。检查到问题不等于获得修改权限。

所有场景统一使用：

```yaml
issue_classification:
  - safe_standard_correction
  - confirmed_bug
  - report_only_risk
  - incremental_design_required
  - refactor_assessment_required
  - blocked_out_of_boundary
```

每个问题至少记录 `issue_id`、Step/phase、classification、evidence、affected_files、expected_behavior_source、行为/实现风险、当前场景是否允许处理、建议场景和处置状态。禁止越权修正、模糊批次、顺手处理相邻问题，或为通过检查改变未授权业务行为/实现方式。

## 环境适配与 Profile 条件加载

1. 读取项目级环境档案，根据当前 `scope` 识别涉及的组件、持久化、公共契约和 CI workflow。
2. 加载当前场景需要的通用 Step reference；通用规则始终执行，不依赖 Profile。
3. 根据相关组件的语言、框架、测试工具、持久化工具和契约类型，只加载 `references/profiles/` 中匹配的 Profile。
4. 同一范围涉及多组件或多工具时分别记录适用性；不得无差别加载全部 Profile。
5. 没有匹配 Profile 时继续执行通用规则，以目标代码、配置、测试和环境档案为事实源，不猜测框架规则；报告专用 Profile 未覆盖，并可建议新增通用 Profile。

## 条件执行与强制验证

根据环境档案和实际范围加载 Step reference；与环境无关的检查标记 `skipped` 并说明原因。场景 6 完整加载 Step 1–7；场景 10 按顺序逐 Step 加载；其余场景只加载适用 Step，但不得删减已加载 Step 内的规范。

任何场景只要修改文件，必须按顺序：核对实际 diff；与 `editable_scope` 比对；对修改文件执行全部适用 Step 规范；运行环境档案中适用的 build/typecheck/test/lint/schema/contract validation；确认未越过当前场景行为边界；报告修改、验证、跳过项和风险。单个针对性测试不能替代可用的构建、类型检查或必要广义验证。

## 数据库验证与操作边界

来自环境档案或项目既有脚本、确定不连接真实/目标数据库、不读写业务数据、不应用 migration 且不部署的本地 schema validation、format、code generation 或纯本地 build/typecheck/lint/test，可以作为当前场景验证执行，不需要数据库操作授权。具体工具命令只从环境档案和匹配 Profile 取得，不在通用核心中预设。

任何连接目标数据库、查询/修改业务数据、应用或生成会写入目标数据库的 migration、schema push、回填、seed、reset、truncate、删除数据或修改表/列/索引/约束的命令，都必须由用户单独明确目标环境、目标数据库、具体命令和允许动作。获准命令一旦报错，原样报告关键错误并停止。

数据库状态分别记录 `created_only`、`validated`、`applied` 或 `not_confirmed`。静态 schema validation 通过最多证明 `validated`；build/test 通过和 migration 文件存在都不能证明目标数据库已经 `applied`。

## Step 1–7 规范路由

1. `references/step1-naming-convention.md`：命名、放置和术语一致性。
2. `references/step2-code-quality.md`：Bug、死代码、错误处理、数据 shape 和类型契约。
3. `references/step3-architecture-layer.md`：入口、业务编排、数据访问、公共契约和外部能力边界。
4. `references/step4-test-coverage.md`：测试影响、边界用例和验证命令。
5. `references/step5-documentation.md`：docs/API/schema/README 与行为一致性。
6. `references/step6-comment-standard.md`：注释和项目本地文件头规范。
7. `references/step7-code-commit.md`：Git 状态、验证、CI/CD 和提交准备。

## 报告格式

所有最终报告展示：用户请求场景、实际执行场景、场景来源、命中信号、执行策略、检查范围、修改范围、处置权限、是否修改代码、当前阶段、问题与证据、验证结果、剩余风险和建议后续场景。涉及内部阶段时额外展示内部阶段及其来源，不得复用 `scene_source` 表示内部阶段来源。

场景 3 和 9 额外展示 `preserved_intent` 与 `fallback_reason`。场景 3 分别展示准入诊断、是否自动返回修复、修复、基础验证、内部回归和最终结果；场景 9 展示紧急诊断、回滚/止血/向前修复判断、补丁、核心回归、交付就绪和固定 readiness。场景 10 保留逐 Step 阶段报告和授权批次。

数据库相关报告分别展示：本地静态验证命令、是否连接目标数据库、migration 文件状态、schema validation 状态、目标数据库应用状态和 `database_operation_authorized`。

`single_run` 在全部适用任务和验证完成后只输出一次最终报告；场景 10 在当前 Step 或单个修正批次结束后输出阶段报告并停止。最终报告后将 Runtime 重置为初始模板。

## 硬边界

- 不执行上线、发布、Release readiness、production gate 或严格企业级安全验收。
- 不在诊断、完整性核查、规则补全、全项目审计、重构评估或合并检查中修改生产代码。
- 不自动执行大规模重构、真实数据库操作、生产操作、权限/安全策略修改、Breaking API、真实环境变量/密钥修改或依赖/框架替换。
- 未经用户明确要求，不执行 stage、commit、push、创建分支、reset、checkout、stash、deploy、release 或清理删除。
- 提交准备前检查并报告 `git status --short`、`git diff --cached --name-status` 和 `git ls-files --others --exclude-standard`；不得默认强制添加被忽略文件。
- 只检查 CI/CD 配置覆盖，不执行 release 或 deploy job。
- 不修改当前任务无关改动；发现越界 diff、意外暂存或提交范围异常时停止，不自行回滚、删除或扩权。
- 除稳定环境事实变化外，不修改项目环境档案；不在 Runtime 中积累跨运行上下文。

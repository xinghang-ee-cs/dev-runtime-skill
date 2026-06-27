# Planning Conversation Runtime

## 1. 运行模式（Runtime Modes）

Planning Layer Runtime 支持两种模式：

| 模式 | 输入 | 输出 | 禁止 |
| --- | --- | --- | --- |
| Planning Conversation Mode | 自然语言、模糊需求、阶段规划启动语句 | Planning Context | 直接生成最终文档 |
| Planning Document Mode | 完整 Planning Context | 单份正式 SoT 文档草案 | 跳过文档职责边界、一次生成多份文档 |

进入规则：

- 用户以自然语言启动规划时，默认进入 Planning Conversation Mode。
- Planning Context 完整后，才允许进入 Planning Document Mode。
- 用户直接要求生成文档但上下文不完整时，先进入 Planning Conversation Mode。

## 2. 规划启动上下文加载（Planning Bootstrap Context Load）

Planning Conversation Mode 启动前，按需读取 `.plan/`。

读取顺序：

```text
.plan/planning-preferences.yaml
-> .plan/user-profile.yaml
-> .plan/project-profile.yaml
-> .plan/context-index.yaml
```

规则：

- 只读取当前任务需要的 `.plan` 文件。
- 遵守最小上下文原则。
- 如果 `.plan/` 不存在，允许创建最小模板，但这不代表 Planning Context 已完成。
- 读取 `.plan/` 后，不得跳过 User Discovery Sufficiency Gate。
- `.plan` 只用于启动辅助，不是正式业务事实。
- `.plan` 不替代 Planning Context。

### All-Phase User Context First Rule

任何期次启动都必须先执行 User Context Gate。

适用：

- 第一期开启
- 第二期开启
- 后续任意期次开启
- 继续上一期规划
- 二次开发规划
- 新增阶段规划

规则：

- 不因用户说“开始开发”就直接问业务建模问题。
- 不因用户说“第一期/第二期”就直接问范围、用户、验收。
- 先确认当前使用者上下文。
- 已有高置信用户画像时复用。
- 未知或冲突时，用聊天方式识别。
- 用户有明显不满、困惑、着急或强烈纠正时，先做情绪承接，再继续首轮推进。

## 3. 对话生命周期（Conversation Lifecycle）

默认阶段：

```text
目标确认
-> 范围确认
-> 业务域确认
-> 当前视角确认
-> 权限确认
-> 数据可见性确认
-> 用户流程确认
-> 功能边界确认
-> 数据模型确认
-> UI确认
-> 接口契约确认
-> 架构确认
-> 外部能力确认
-> 测试方案确认
-> 风险确认
-> 开发任务确认
```

规则：

- 允许跳过不涉及阶段。
- 跳过必须说明依据。
- 禁止无依据跳阶段。
- 每轮只推进当前必要阶段。
- 每轮优先只问 1 个主问题；同一上下文且用户可轻松一次性回答时，才允许 2 到 3 个问题。
- 问题必须贴近操作、角色、流程和结果。
- 阶段不是问卷；不得要求用户按阶段字段回答。

## 3.1 用户发现访谈（User Discovery Interview）

当用户从自然语言需求开始时，Planning Conversation Mode 必须按需加载 `00-planning-user-discovery.md`。

规则：

- User Discovery 的访谈方法、业务事实发现、专业词翻译和 Discovery Sufficiency Gate 详细规则由 `00` 负责。
- `07` 只负责在正确阶段调用该 Runtime，并接收其输出。
- Discovery Sufficiency Gate 通过前，不得进入 Planning Document Mode。
- User Discovery Runtime 的入口必须先完成 User Context Gate，不得跳过到业务发现。

## 发现复用规则（Discovery Reuse Rule）

Planning Conversation Runtime 开始前必须优先读取：

```yaml
user_profile
discovered_business_facts
```

若事实已确认，禁止重复提问。

仅允许：

- 补充缺失项
- 确认高风险项
- 解决冲突项
- 补齐 Completion Gate 所需信息

禁止：

- 已经确认“谁在使用”后，再次提问“用户角色是谁”。
- 已经确认“当前工作流程”后，再次提问“用户流程是什么”。

除非：

- 发现冲突
- 信息不足

## 4. 对话轮次输出（Conversation Round Output）

内部状态与用户态分离。

内部轮次状态（Internal Round State）：

```text
当前阶段：
已确认：
缺失项：
风险或冲突：
下一步：
```

用户可见回复（User-facing Reply）：

```text
自然复述：
当前判断：
一个推进问题：
```

规则：

- Internal Round State 仅用于日志、恢复、上下文管理。
- User-facing Reply 才是给用户看的内容。
- 用户态回复必须像正常协作对话。
- Internal Round State 的字段不能外显。
- 业务建模槽位不能原样外显。
- 情绪承接是用户态回复的一部分，不是可选项。
- 用户态问题优先确认“协作方式”，而不是要求用户选择身份分类。
- 角色、职位、决策权由 AI 从后续聊天中逐步归纳，不得首轮强行收集。
- 当前情绪只用于本轮承接，不进入 Planning Context，不进入 `.plan`，不进入正式 SoT。
- 用户侧不要求按格式回复。
- 问题数量保持最少。
- 优先确认阻塞项。
- 默认只问一个自然问题。
- 只有同一上下文且用户可以轻松一次性回答时，才允许 2 到 3 个问题。
- 不得把 1 到 3 个问题执行成固定三问模板。
- 面向非专业用户时，不使用 RBAC、ABAC、状态机、接口契约、权限矩阵等专业术语。
- 不输出最终 SoT 正文。

首轮示例：

用户：

```text
开始第一期开发
```

如果用户画像未知，合格回复：

```text
可以。我先不急着问功能细节，先确认我该按什么方式配合你。

这次你是想让我偏“帮你定第一期范围”，还是偏“把已有材料整理成开发任务”？
```

如果用户画像已知为项目负责人，合格回复：

```text
可以。我先按你负责把控范围和交付的视角来推进，不直接开写代码。

这次第一期是已经有材料要我整理，还是先帮你判断最小可交付范围？
```

如果用户明显不满，合格回复：

```text
对，不能一上来就问“谁用、完成什么”，那不是正常对话。我先重新接住：你现在是要我帮你把这一期范围收住，还是已经有材料让我整理成开发计划？
```

## 5. 业务语言输入处理

用户可使用口语化描述。

规则：

- 业务事实发现和专业词翻译由 `00-planning-user-discovery.md` 负责。
- `07` 只接收已发现事实，并把可用事实补入 Planning Context。
- 正式 SoT 文档仍必须使用专业表达和来源引用。

## 5.1 UI/交互前置确认

当需求涉及用户界面、页面、表单、列表、地图、工作台、移动端、小程序、飞书或 PC 操作时，必须确认 UI/交互高风险项。

UI 高风险项：

```text
核心页面布局
操作路径
跳转关系
状态反馈
异常态
空状态
加载态
移动/桌面适配
视觉风格
```

未确认时：

- 不允许生成依赖该 UI 的开发任务。
- 允许生成不依赖该 UI 的上游规划内容。
- 必须记录为待确认项和阻塞范围。

规则：

- UI 访谈方法沿用 `00-planning-user-discovery.md`。
- `07` 只记录 UI 高风险项、待确认项和阻塞范围。

## 6. 风险确认模式

触发条件：

- 命中 `01-planning-core-rules.md#4-高风险不确定项`。
- 命中 `06-planning-capability-governance.md` 的 Capability Governance Runtime。
- 当前阶段存在权限、删除、数据归属、状态流、接口、UI/交互、审计、租户、外部能力、安全、合规或计费不确定项。

输出：

```text
当前理解：
缺失信息：
风险影响：
待确认问题：
处理状态：
```

规则：

- 高风险项不得静默假设。
- 必须追问至用户确认。
- 无法确认时，记录为待确认项。

## 7. 上下文完整性检查

每轮阶段结束时检查：

- 缺失实体
- 缺失角色
- 缺失权限
- 缺失状态
- 缺失 UI/交互确认
- 缺失测试
- 缺失验收

发现缺失时：

```text
缺失项：
影响范围：
建议补问：
```

## 8. 冲突检测

触发条件：

- 前后描述冲突
- 权限冲突
- 状态冲突
- 范围冲突
- Capability 冲突

触发后暂停，输出：

```text
当前理解：
冲突点：
影响范围：
建议确认项：
```

## 9. Planning Context

Conversation Mode 最终输出 Planning Context：

```text
目标：
范围：
角色：
权限：
数据：
流程：
功能：
UI/交互：
能力：
测试：
风险：
验收：
待确认项：
涉及文档：
```

规则：

- Planning Context 是 Document Mode 的输入。
- Planning Context 不替代正式 SoT 文档。
- 待确认项必须保留来源和影响范围。

## 9.1 Planning Handoff Package

Planning Context 状态为 `COMPLETE` 后，Planning Runtime 必须生成 Handoff Package。

用途：

```text
Planning Runtime
-> Long Runtime
-> Execution Runtime
-> Acceptance Runtime
```

Handoff Package 格式：

```yaml
handoff_role_mapping:

Capability Governance:
  path:

Test and Acceptance Plan:
  path:

Risk, Dependency, and Open Questions:
  path:

Development Landing Checklist:
  path:

Execution and Integration Record:
  path:

Acceptance and Retrospective Record:
  path:
```

规则：

- 使用职责名。
- 不使用固定编号。
- 必须使用实际路径。
- 必须来自本次 Planning Runtime 的正式输出。
- Long Runtime 禁止通过编号猜测文件。
- 未生成 Handoff Package 时，不允许进入 Long Runtime。

Document Assembly 完成后，必须输出：

```yaml
assembled_documents:

- role:
  path:
  reason:
```

示例：

```yaml
assembled_documents:

- role: Capability Governance
  path: docs/计划安排/第四期/10-外部能力与集成治理.md
  reason: feishu_location_sdk

- role: Development Landing Checklist
  path: docs/计划安排/第四期/13-开发任务拆分与落地清单.md
  reason: implementation_required
```

Document Assembly 原则：

- Document Assembly 必须按需求特征动态装配。
- 禁止默认生成全量文档。
- S/M 级需求只允许生成必要文档。
- L 级需求允许完整文档链。
- `assembled_documents` 必须进入 Planning Context。
- `handoff_role_mapping` 必须基于 `assembled_documents` 生成。

低熵原则：

- Handoff 只是 Planning Runtime 的最终输出。
- Handoff 不是新的 Runtime 系统。
- 优先复用现有结构。
- 禁止为了 Runtime 交接新增长期 Runtime 结构。

## 10. Planning Document Mode

进入条件：

- Planning Context 状态为 COMPLETE。
- Planning Completion Gate 已通过。
- 高风险项已确认或已登记待确认项。

执行规则：

- 根据 `03-planning-doc-responsibility.md` 动态装配文档。
- 涉及 Capability 时，按 `06-planning-capability-governance.md` 执行。
- 涉及 Priority 时，按 `05-planning-priority-system.md` 执行。
- 涉及格式、ID、状态、测试范围或下游验证结果引用时，按 `04-planning-format-spec.md` 执行。
- 正式文档不得口语化。
- 每次只生成一份正式文档草案。
- 当前文档未确认前，不允许生成下一份文档。
- 用户确认后，才允许进入下一份文档。
- 每份正式文档草案生成前，必须先执行 Per-Document Collaborative Confirmation Gate。
- 禁止用全局 Discovery 替代逐文档确认。
- 禁止用生成后解释替代生成前确认。
- 禁止用生成前确认替代生成后解释。

### 10.1 Per-Document Draft Lifecycle

Planning Document Mode 每次只处理一份文档。

每份文档必须按以下顺序执行：

1. Select Document
   根据 `assembled_documents` 选择下一份待生成文档。
2. Pre-Draft Explanation
   用当前使用者能理解的话说明这份文档要解决什么问题、为什么现在要确认、它会影响后续什么。
3. Per-Document Collaborative Confirmation
   只确认该文档最关键、最容易偏差、最影响返工的点。默认只问 1 个主问题；同一上下文且容易回答时，才允许 2 到 3 个问题。
4. Formal Document Draft
   生成正式 SoT 文档草案。使用专业结构，不口语化，不把用户态解释写进正文。
5. Role-Based Document Explanation
   按当前使用者岗位/身份解释文档内容。
6. User Confirmation
   用户确认、修改或要求解释。
7. Conversation Continuity Gate
   明确告诉用户当前完成了什么、还差什么、现在该确认什么、可以怎么回复，以及回复后进入哪份文档或阶段。

Per-Document Collaborative Confirmation 的 decision 只允许：

```text
continue_conversation
generate_document
blocked_by_missing_info
```

决策规则：

- `continue_conversation`：还有该文档必须确认的信息，继续聊天补齐。
- `generate_document`：该文档关键点已确认，可以生成正式草案。
- `blocked_by_missing_info`：缺少关键事实，不能生成当前文档，必须说明最小阻塞问题。

禁止：

- `Planning Context COMPLETE` 后直接连续生成多份正式文档。
- 只靠前期总访谈直接生成所有细节文档。
- 不经逐文档协作确认，直接生成正式文档。
- 把逐文档确认问题做成完整问卷。
- 让用户按专业字段回答。
- 把 AI 推断直接写成 `confirmed`。
- 用生成前确认替代 Role-Based Document Explanation Gate。
- 没有用户确认就进入下一份文档。

Per-Document Collaborative Confirmation Gate 发生在正式文档生成前。
Role-Based Document Explanation Gate 发生在正式文档生成后。
二者不可互相替代。

前者解决：

- 生成前有没有聊清楚。
- AI 是否在自行补细节。

后者解决：

- 生成后使用者能不能听懂。
- 使用者是否知道确认什么和下一步怎么做。

### 10.2 Role-Based Document Explanation Gate

每生成一份正式 SoT 文档草案后，必须执行 Role-Based Document Explanation Gate。

输出结构：

```text
一句话解释：
锁定了什么：
会影响什么：
现在重点看什么：
可以不用细看什么：
错了会返工的点：
可以怎么回复：
下一步：
```

字段规则：

- `一句话解释`：用当前使用者能听懂的话说明这份文档在做什么。
- `锁定了什么`：只解释和当前使用者有关的关键业务事实。
- `会影响什么`：说明后续会影响开发、页面、接口、数据、测试、验收或风险中的哪些部分。
- `现在重点看什么`：给出 2 到 5 个当前使用者必须确认的点。
- `可以不用细看什么`：告诉使用者哪些专业 ID、引用、格式、技术细节可以不用逐字看。
- `错了会返工的点`：说明最可能导致返工的 1 到 3 个点。
- `可以怎么回复`：给出自然回复方式，例如“确认，继续下一份”“范围不对，少了……”“这个先不做”“这里我不确定，你帮我再解释一下”。
- `下一步`：说明确认后进入哪一份文档或哪一阶段，以及为什么。

规则：

- 必须根据 `.plan/user-profile.yaml` 和 User Context Gate 的结果调整解释方式。
- 面向非专业使用者时，不要求其阅读完整专业文档。
- 岗位化解释不替代正式 SoT。
- 岗位化解释不进入 Handoff、Capability Registry 或正式文档正文。
- Role-Based Document Explanation Gate 不得替代生成前的 Per-Document Collaborative Confirmation Gate。
- Per-Document Collaborative Confirmation Gate 不得替代生成后的 Role-Based Document Explanation Gate。

#### User-Facing ID Translation Rule

规则：

- 正式 SoT 文档中必须保留 `REQ`、`FLOW`、`DOMAIN`、`MODULE`、`CAP`、`PAGE`、`STATE`、`API`、`PERM`、`TASK`、`RISK`、`TEST` 等 ID。
- 用户态解释中不得把 ID 作为主要确认对象。
- 用户态不得直接问“REQ-001 是否准确？”“API-001 是否没问题？”“CAP-MAP-001 是否确认？”“TASK-001 是否可以执行？”。
- 用户态必须把 ID 对应的具体内容翻译出来，让使用者确认内容本身。
- 如果确实需要展示 ID，只能作为补充引用放在具体内容后面，不得单独出现。
- 面向非技术使用者时，默认不展示 ID。
- 面向开发实现使用者时，可以展示 ID，但必须同时展示该 ID 对应的自然语言内容。

错误示例：

```text
REQ-001 这个核心目标是否够准确。
```

正确示例：

```text
第一期的核心目标是不是：上传一张 UI 图后，系统能识别常见组件，并在自研 canvas 里生成一张静态原型。文档里这个目标会被编号为 REQ-001，方便后续开发和测试追踪。
```

更推荐的非技术用户写法：

```text
第一期的核心目标是不是只先做到：一张 UI 图进去，系统能生成一张静态 canvas 原型。你不用管文档里的编号，重点确认这个目标对不对。
```

禁止：

- 让用户确认裸 ID。
- 让用户通过 ID 判断业务内容。
- 在“你现在重点确认什么”里只列 ID。
- 在“可以怎么回复”里要求用户引用 ID。
- 用 ID 替代具体业务描述。

### 10.3 Conversation Continuity Gate

每一轮用户态回复结束前，必须执行 Conversation Continuity Gate。

用户态回复必须自然说明：

- 当前已经完成什么。
- 当前还差什么或正在等什么。
- 用户现在最应该做的一件事。
- 用户可以怎么回复。
- 用户回复后 AI 会进入哪一步。

禁止：

- 只以“请确认”结尾。
- 只以“已完成”结尾。
- 只以“等待用户回复”结尾。
- 不说明下一步动作。
- 不说明用户应该确认什么。
- 不说明确认后进入哪里。

### 10.4 逐文档协作确认重点

以下内容只作为内部引导方向，不得原样全部抛给用户。每次只选择当前文档最关键的 1 到 3 个点自然提问。

| 文档 | 确认方向 | 面向非专业用户的问法方向 |
| --- | --- | --- |
| 00-需求背景与目标 | 为什么做、解决什么问题、成功是什么样子 | 这件事最想改变什么 |
| 01-需求范围与验收标准 | 本期做什么、不做什么、什么算完成 | 这一期最希望先看到哪一块能跑起来 |
| 02-业务域模型 | 核心业务对象、对象关系、归属和生命周期 | 系统里最重要的东西有哪些，它们之间是什么关系 |
| 03-用户场景与交互流程 | 谁在什么场景下做什么、异常时怎么办 | 真实一天里，用户会从哪一步开始，到哪一步结束 |
| 04-功能拆解与边界说明 | 模块边界、负责什么、不负责什么、依赖什么 | 哪些功能是一组，哪些先不管 |
| 05-前端页面与 UI 交互设计 | 页面、入口、按钮、跳转、空/错/加载状态、视觉方向 | 用户打开后先看到什么，点哪里，下一步发生什么 |
| 06-数据模型与状态流转 | 关键数据、状态变化、历史兼容、测试数据治理 | 这件事从开始到结束会经历哪些明显阶段，哪些记录不能丢 |
| 07-接口设计与前后端契约 | 页面/模块之间需要传什么、错误怎么反馈、权限怎么校验 | 这个结果需要同步给谁或哪个页面 |
| 08-权限与异常边界说明 | 谁能看、谁能改、谁能决定、越权怎么办 | 哪些人只能看，哪些人可以改，哪些事情必须有人拍板 |
| 09-架构设计与关键决策 | 复用策略、模块边界、关键技术取舍和例外 | 只解释影响成本、稳定性、未来扩展的取舍，不要求确认技术细节 |
| 10-外部能力与集成治理 | 外部平台/SDK/API/AI 服务、官方来源和真实验证要求 | 哪些能力必须接真实平台，哪些可以先做演示替代 |
| 11-测试方案与验收用例 | 只确认测什么，不确认怎么测 | 哪些结果必须证明是对的，哪些出错不能上线 |
| 12-风险、依赖与待确认项 | 最大风险、谁来确认、确认不了会影响什么 | 哪些地方如果不确定，后面最容易返工或卡住 |
| 13-开发任务拆分与落地清单 | 任务顺序、依赖、P0/P1/P2、能否交给执行 skill | 先做哪几件最关键，哪些可以后面做 |

### 10.5 正式文档生成后的用户确认输出

```text
当前文档草案
用户能理解的确认解释
最需要确认的 2 到 5 个业务点
可不用细看的专业细节
错误会导致返工的点
风险/冲突
用户确认状态
是否允许进入下一文档：否
```

确认状态：

```text
待确认
已确认
需修改
```

规则：

- 不得只说“请阅读文档并确认”。
- 必须说明：这份文档做了什么、锁定了哪些业务事实、会影响后续哪些开发。
- `00`、`01`、`03`、`04`、`05`：用业务语言解释较完整。
- `06`、`07`、`08`、`09`：说明它对数据库、接口、权限、页面或架构开发意味着什么。
- `10`、`11`、`12`、`13`：重点解释风险、测试、落地任务、阻塞项和后续执行边界。
- 专业细节不要求用户逐字确认，业务事实和返工风险必须确认。
- `用户确认状态` 为 `已确认` 后，下一轮才可进入下一文档。
- 用户要求修改时，只修正当前文档，不生成后续文档。
- 逐文档确认不得替代 Planning Completion Gate。

## 11. Planning Completion Gate

Planning Conversation Mode 结束前必须执行：

### Discovery Sufficiency Gate

规则：

- 详细检查项和补问规则由 `00-planning-user-discovery.md` 定义。
- `07` 必须在 Planning Completion Gate 前调用该 Gate。
- Gate 未通过时，不得进入 Planning Document Mode。

### Context Completeness Check

检查：

- 目标
- 范围
- 角色
- 权限
- 数据
- 流程
- 功能
- UI/交互
- 能力
- 测试
- 验收

是否已确认。

--------------------------------------------------

### High Risk Confirmation Check

检查：

以下高风险项是否已确认：

- 权限
- 删除规则
- 数据归属
- 状态流转
- 接口契约
- 审计规则
- 租户隔离
- 外部能力
- UI/交互高风险项
- 安全
- 合规
- 计费

规则：

必须满足以下条件之一：

- 已确认
- 已登记待确认项

--------------------------------------------------

### Conflict Check

检查：

- 权限冲突
- 状态冲突
- 范围冲突
- Capability 冲突
- 前后描述冲突

规则：

冲突数量必须为：

0

否则：

不得结束规划。

--------------------------------------------------

### Blocking Check

检查：

是否存在：

- 未解决阻塞项
- 未确认关键实体
- 未确认关键角色
- 未确认关键权限
- 未确认 UI/交互高风险项且存在 UI 依赖开发任务

存在时：

不得结束规划。

--------------------------------------------------

### Completion Result

输出：

Planning Context 状态：

- INCOMPLETE
- COMPLETE

规则：

只有：

COMPLETE

才允许进入：

Planning Document Mode。

## 12. 运行时事件日志（Runtime Event Logging）

Runtime Event Log 属于 Project Runtime Evidence。

允许记录：

- 模式切换
- 阶段推进
- 风险发现
- 冲突发现
- Completion Gate 结果
- Capability 识别
- Blocking Trigger
- 文档装配结果
- 文档确认结果
- UI/交互确认结果
- Context 状态变化

禁止记录：

- 完整 CoT
- 长篇推理
- 全量聊天记录
- 非结构化自然语言分析

Runtime Event 格式：

```yaml
event_seq:
timestamp:
runtime_mode:
event_type:
event_id:
related_ids:
decision:
reason:
blocking:
next_action:
```

允许事件类型：

```text
MODE_SWITCH
STAGE_ENTER
STAGE_COMPLETE
RISK_DETECTED
CONFLICT_DETECTED
CAPABILITY_DETECTED
BLOCKING_TRIGGERED
COMPLETION_GATE_CHECK
DOCUMENT_ASSEMBLY
DOCUMENT_CONFIRMATION
UI_CONFIRMATION
PLANNING_CONTEXT_UPDATED
PLANNING_COMPLETE
```

规则：

- 每个事件必须结构化。
- 每个事件必须最小化。
- `event_seq` 必须在同一个 `planning-runtime/event-log.md` 内单调递增。
- `event_seq` 是事件审计与恢复分析的主排序字段。
- `timestamp` 只表示发生时间，不作为唯一排序依据。
- 禁止重写历史 `event_seq`。
- 禁止插入旧 event 破坏已存在 `event_seq`。
- 如需补记事件，只能追加新 event，并在 `reason` 中标记 `backfill_event`。
- 不记录无意义状态。
- 不记录重复事件。
- 不记录完整用户输入。
- 不记录完整 AI 回复。
- 禁止生成自由事件名称。
- `reason` 仅允许简短结构化原因。

`reason` 示例：

```text
missing_permission_boundary
```

Runtime Event Log：

- 不属于正式 SoT。
- 不进入规划文档正文。
- 不参与业务事实定义。
- 不参与 Capability Registry。
- 不参与 Acceptance。
- 不作为 Runtime Recovery Source。

日志仅用于：

- 调试
- 执行留痕
- 模型对比
- 问题定位

Completion Gate Logging：

```yaml
event_seq:
event_type: COMPLETION_GATE_CHECK
decision:
context_status:
blocking_count:
conflict_count:
missing_sections:
```

Capability Logging：

```yaml
event_seq:
event_type: CAPABILITY_DETECTED
related_ids:
decision:
reason:
next_action:
```

示例：

```yaml
event_seq:
event_type: CAPABILITY_DETECTED
related_ids:
  - CAP-FEISHU-001
decision: evidence_gate_required
reason: platform_capability_detected
next_action: capability_registry
```

Document Confirmation Logging：

```yaml
event_seq:
event_type: DOCUMENT_CONFIRMATION
related_ids:
decision:
reason:
blocking:
next_action:
```

UI Confirmation Logging：

```yaml
event_seq:
event_type: UI_CONFIRMATION
related_ids:
decision:
reason:
blocking:
next_action:
```

### 12.1 运行时状态与项目证据（Runtime State vs Project Evidence）

Runtime State：

负责：

- 当前状态
- 当前阶段
- 当前恢复点

用途：

- 中断恢复
- 继续执行

特点：

- 临时
- 可覆盖
- 可更新
- 项目结束可删除

Project Runtime Evidence：

负责：

- 事件记录
- 决策记录
- 审计记录

用途：

- Skill 优化
- 模型评估
- 项目复盘
- 用户回传分析

特点：

- append-only
- 长期保留
- 项目资产

规则：

- Project Runtime Evidence 禁止作为 SoT。
- Project Runtime Evidence 禁止作为 Planning Context。
- Project Runtime Evidence 禁止作为 Handoff Package。
- Project Runtime Evidence 禁止作为 Runtime Recovery Source。

### 12.2 项目运行时证据目录（Project Runtime Evidence Directory）

Planning Runtime Evidence 默认写入：

```text
docs/计划安排/<第X期>/planning-runtime/
```

结构：

```text
planning-runtime/
event-log.md
event-summary.md
decision-log.md
decision-summary.md
audit-log.md
audit-summary.md
```

统一命名约定：

```text
Planning: planning-runtime/
Execution: execution-runtime/
Testing: testing-runtime/
```

当前 Skill 仅实现：

```text
planning-runtime/
```

规则：

- `execution-runtime/` 由 Execution Skill 创建。
- `testing-runtime/` 由 Testing Skill 创建。
- 禁止提前实现其他 Skill 的 evidence 目录。
- 禁止新增 `recovery-runtime/`。
- 禁止新增 `governance-runtime/`。
- 禁止新增 `entropy-runtime/`。
- 禁止新增 `analysis-runtime/`。
- 禁止新增 `debug-runtime/`。

### 12.3 决策快照运行时（Decision Snapshot Runtime）

Decision Snapshot Runtime 只记录关键决策快照，属于 Project Runtime Evidence，用于 Runtime Debugging、Model Comparison、Human Review 和项目复盘。

它回答：

- 为什么发生
- 为什么选择该方案
- 风险是什么
- 当时有哪些备选路径

它不是：

- 聊天记录
- 推理链
- 分析日志
- 长期记忆系统

默认写入：

```text
docs/计划安排/<第X期>/planning-runtime/decision-log.md
docs/计划安排/<第X期>/planning-runtime/decision-summary.md
```

Decision Snapshot 格式：

```yaml
timestamp:
decision_id:
stage:
status:
current_understanding:
decision:
reason:
risk:
source:
impact:
supersedes:
next_action:
```

Decision Status：

```text
candidate
confirmed
superseded
rejected
```

规则：

- 用户尚未完成场景级确认前，关键业务流只能记录为 `candidate`。
- 只有用户明确确认后，才能记录为 `confirmed`。
- 后续被用户纠正时，追加新 Snapshot，并把旧决策标记为 `superseded`。
- 明确讨论但不采用的方案记录为 `rejected`。
- 不得静默覆盖已有关键决策。

Decision ID Specification：

```text
Decision ID 格式：

DEC-<TYPE>-<SEQ>

示例：

DEC-SCOPE-001
DEC-ROLE-001
DEC-UI-001
DEC-CAPABILITY-001
DEC-BLOCKER-001
DEC-RECOVERY-001
```

规则：

- 全局唯一
- 稳定引用
- 不允许自然语言替代
- 不允许自由格式
- 不允许同义重复

目的：

```text
Decision Snapshot
可追踪
可检索
可引用
```

字段规则：

- `current_understanding` 仅允许结构化摘要；备选路径只能作为短列表写入其中。
- `decision` 仅允许写当前选择，不写长解释。
- `reason` 仅允许短枚举原因。
- `source` 仅允许来源类型、文档路径或 Runtime Gate 名称，不记录完整用户输入。
- `impact` 仅允许结构化影响摘要。

`reason` 示例：

```text
missing_permission_boundary
ui_confirmation_completed
capability_confirmed
blocking_detected
completion_gate_passed
```

仅允许记录以下决策场景：

```text
阶段推进：目标确认、范围确认、角色确认、UI确认、能力确认
风险确认：权限、数据归属、状态流、外部能力、UI高风险项
Blocking Trigger
Completion Gate
Document Confirmation
Capability Confirmation
Recovery Trigger
```

Decision Snapshot Deduplication：

同一阶段、同一结论，仅允许记录一次 Decision Snapshot。

允许新增 Snapshot：

- 结论发生变化
- 风险等级发生变化
- Blocking 状态发生变化
- Capability 状态发生变化
- Recovery Trigger 发生

禁止：

- 重复记录同一结论
- 每轮访谈重复记录
- 仅因措辞变化重复记录

Decision Snapshot 的目标：

```text
记录关键决策变化
```

而不是：

```text
记录访谈过程
```

禁止：

- 自由新增决策类型
- 保存完整聊天记录
- 保存完整用户输入
- 保存完整 AI 回复
- 保存 CoT
- 保存推理过程
- 将 Decision Snapshot 写入 Planning Context
- 将 Decision Snapshot 写入正式文档
- 将 Decision Snapshot 写入 Handoff Package
- 将 Decision Snapshot 写入 Capability Registry
- 将 Decision Snapshot 写入 Acceptance

Decision Summary 机制：

- `planning-runtime/decision-summary.md` 只保留关键决策、关键风险、关键阻塞、关键恢复事件。
- Summary 禁止完整复制 Log。
- Summary 禁止长篇解释。
- Summary 禁止用户原话。
- 历史决策进入 Summary 后，不默认进入 Runtime Context。

生命周期：

- Decision Log append-only。
- Decision Summary 周期性汇总。
- Decision Log 和 Decision Summary 默认不加载。
- Runtime 行为不得依赖历史 Decision Log。

## 13. 运行时事件持久化（Runtime Event Persistence）

Runtime Event Log 默认写入：

```text
docs/计划安排/<第X期>/planning-runtime/event-log.md
```

Runtime Event Summary 默认写入：

```text
docs/计划安排/<第X期>/planning-runtime/event-summary.md
```

规则：

- Runtime Event Log 属于 Project Runtime Evidence。
- 不属于正式 SoT。
- 不属于业务事实。
- 不参与文档职责定义。
- 不参与 Capability Governance。
- 不参与 Acceptance。
- 不作为 Runtime Recovery Source。

必须写入 Runtime Event Log 的事件：

```text
MODE_SWITCH
STAGE_ENTER
STAGE_COMPLETE
RISK_DETECTED
CONFLICT_DETECTED
CAPABILITY_DETECTED
BLOCKING_TRIGGERED
COMPLETION_GATE_CHECK
DOCUMENT_ASSEMBLY
DOCUMENT_CONFIRMATION
UI_CONFIRMATION
PLANNING_CONTEXT_UPDATED
PLANNING_COMPLETE
```

写入规则：

- 触发即追加写入。
- 不允许静默跳过。
- 不允许覆盖历史日志。
- 使用 append-only 模式。

Runtime Event Log 更新规则：

- 默认按 event_seq 追加。
- timestamp 仅作为事件发生时间参考。
- 不允许重写历史事件。
- 不允许重新生成旧日志。

日志格式：

```yaml
event_seq:
timestamp:
runtime_mode:
event_type:
event_id:
related_ids:
decision:
reason:
blocking:
next_action:
```

Summary 生成时机：

- Planning Completion Gate 通过后。
- Planning Document Mode 完成后。
- Planning Complete 后。

Summary 内容：

- 关键风险
- 关键冲突
- Capability 识别结果
- Blocking Trigger
- Completion Gate 结果
- Planning Result

Summary 禁止：

- 完整聊天记录
- 完整事件复制
- 长篇推理

日志增长控制：

- Runtime Event Log 作为 Project Runtime Evidence 长期保留。
- 历史事件通过 Summary 压缩复盘入口。
- 超过阈值的旧事件不默认进入上下文。
- Runtime Event Log 不作为长期记忆系统。

禁止：

- 无限增长
- 全量读取历史日志
- 将日志重新注入 Planning Context
- 将日志重新写入正式 SoT

日志读取规则：

- Runtime Event Log 不自动进入 Planning Context。
- Runtime Event Log 不自动进入正式文档。
- Runtime Event Log 不自动进入 Runtime SoT。
- Runtime Event Log 不作为 Runtime Recovery Source。

仅允许：

- Runtime Debugging
- 问题定位
- 模型行为分析
- 恢复问题复盘
- 用户主动回传日志

Completion Gate 必须追加：

```yaml
event_seq:
event_type: COMPLETION_GATE_CHECK
decision:
context_status:
blocking_count:
conflict_count:
missing_sections:
```

Planning 完成后必须追加：

```yaml
event_seq:
event_type: PLANNING_COMPLETE
decision:
generated_documents:
summary_generated:
blocking:
next_action:
```

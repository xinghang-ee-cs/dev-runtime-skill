# 流程梳理阶段：AI Runtime Format Specification

## 1. 文件位置

```text
docs/计划安排/<第X期>/
```

## 2. 一级标题

```markdown
# 第X期<文档主题>
```

## 3. 固定边界章节

```markdown
## 1. 文档边界
```

格式：

```markdown
本文档确认……

本文档正文进入……

相邻内容由 `xx` 文档承接。
```

## 4. 文档 ID 规范

统一 ID：

```text
REQ-xxx
FLOW-xxx
SCN-xxx
DOMAIN-xxx
MODULE-xxx
ARCH-xxx
CAP-xxx
PAGE-xxx
UI-MOD-xxx
UX-SCN-xxx
PROMPT-STYLE-xxx
PROMPT-PAGE-xxx
PROMPT-MODULE-xxx
PROMPT-UX-xxx
ASSET-xxx
STATE-xxx
API-xxx
PERM-xxx
TASK-xxx
RISK-xxx
DEP-xxx
OPEN-xxx
EXEC-xxx
TEST-xxx
```

规则：

- 全局唯一
- 稳定
- 不允许同义重复
- 不允许自然语言替代
- PROMPT 必须关联适用的 PAGE、UI-MOD 或 UX-SCN；PROMPT-STYLE 必须关联适用页面、模块或 UX 范围。
- ASSET 在 `received`、`review_pending`、`visual_confirmed` 或 `superseded` 状态下必须关联实际收到的图或明确的外部引用。
- PAGE、UI-MOD、UX-SCN 均不得替代 FLOW、STATE、API、PERM 的事实定义。
- ARCH 必须关联已确认的 FLOW、MODULE、STATE、API 或 PERM，不得替代这些上游事实定义。
- RISK、DEP、OPEN 的正式 ID 只能由 12 创建；01–11 只能移交信号或待确认问题。
- EXEC 只能用于 14 的预置执行框架，不得表示实际执行已经发生。

## 4.1 决策状态规范

适用于关键业务流、权限、数据、状态、UI、外部能力和高风险结论。

```text
candidate
confirmed
superseded
rejected
```

规则：

- 场景级用户确认前，只能是 `candidate`。
- 用户明确确认后，才能是 `confirmed`。
- 后续被用户纠正时，旧结论标记 `superseded`，新结论重新记录。
- 明确不采用的方案标记 `rejected`。
- `candidate` 不得作为最终 SoT 结论，只能进入待确认项或风险。

Capability ID 使用：

```text
CAP-<DOMAIN>-<SEQ>
```

示例：

```text
CAP-MAP-001
CAP-VOICE-001
CAP-OCR-001
CAP-PAY-001
```

## 4.2 Flow Contract

`01-需求范围与验收标准.md` 的业务旅程必须使用：

```markdown
### FLOW-XXX：<业务旅程名称>

业务目标：

关联需求：
- REQ-XXX

参与角色：

合法入口：

起始状态：

必要前置：
- 身份：
- 会话：
- 组织/租户：
- 可见范围：
- 业务上下文：
- 前序业务事实：

允许步骤：
1.
2.
3.

每步预期可见结果：

成功终态：

异常与阻断：

禁止跳步 / 非法路径：
-
-

不做范围：

关联对象：
- DOMAIN-XXX

关联后续测试：
- TEST-XXX

Priority：
```

规则：

- 每个 P0 REQ 必须归属至少一条 FLOW。
- 每条 FLOW 必须有合法入口、起始状态、必要前置、成功终态和禁止跳步。
- 每个业务动作必须说明谁在什么条件下可以做。
- 01 必须同时定义正向验收和反向验收。

## 4.3 Journey-Object Map

`02-业务域模型.md` 必须按 01 的 FLOW 顺序生成：

```markdown
## 旅程—对象关系地图

| FLOW | 前置对象/事实 | 读取对象 | 新建/改变对象 | 成功事实 | 必须阻断条件 | 禁止对象关系 |
| --- | --- | --- | --- | --- | --- | --- |
```

规则：

- 01 每条 FLOW 都必须在 02 中有对应关系行。
- 01 的前置、动作或终态在 02 无对象或关系支撑时，02 不得确认。
- 02 新增会改变 01 旅程的对象关系时，必须回到 01 修正。

## 4.4 Access Context

有效访问上下文：

```text
用户主体
+ 有效会话
+ 组织/租户上下文
+ 角色分配
+ 项目、资源或业务可见范围
+ 当前动作所需资格
```

边界：

- 02 只定义业务资格与关系。
- 08 才定义权限矩阵、数据可见性、越权响应和接口级校验。

必须明确：

- 用户 ≠ 角色。
- 角色 ≠ 项目、资源或业务范围操作资格。
- 管理员身份 ≠ 自动拥有资源负责人或业务负责人资格。
- 历史审批人 ≠ 新流程生效权。

## 4.5 Current / Target / Legacy Object Treatment

`02-业务域模型.md` 必须包含：

```markdown
## 当前对象与目标对象处理矩阵

| 对象或旧流程 | 当前真实语义 | 本期目标关系 | 处理策略 | 是否可进入新流程 | 禁止关系 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
```

处理策略只允许：

```text
inherit
adapt
create
deprecate
block
readonly
cleanup
```

禁止使用：

```text
尽量兼容
视情况复用
后续再看
可能保留
```

## 4.6 负向对象关系

02 必须明确关键旧对象或旧流程对新流程的禁止关系。

格式：

```markdown
旧对象或旧流程：

禁止关系：
- 不得创建新流程记录
- 不得作为新流程前置
- 不得更新新流程状态
- 不得成为工作台下一步动作来源
- 不得映射为新流程有效状态
```

边界：

- 02 定义业务对象关系事实。
- 06 定义状态迁移禁止。
- 07 定义接口阻断。
- 08 定义权限阻断。
- 09 定义技术迁移与清理策略。

## 4.7 Scenario Contract

`03-用户场景与交互流程.md` 的核心 ID 使用：

```text
SCN-<DOMAIN>-<SEQ>
```

格式：

```markdown
### SCN-XXX：<用户场景名称>

关联业务旅程：
- FLOW-XXX

关联业务对象与资格：
- DOMAIN-XXX
- ACCESS-CONTEXT-XXX

参与角色：

合法进入条件：
-

用户起点：

交互步骤：

| 步骤 | 用户动作 | 系统处理 | 用户可见结果 |
| --- | --- | --- | --- |

分支：
- 正常完成：
- 前置缺失：
- 权限不足：
- 外部能力失败：
- 用户取消：

恢复或退出：
- 返回位置：
- 可重试条件：
- 人工协助条件：

禁止的用户路径：
-

需要的界面承接：
- PAGE-XXX
- UI-MOD-XXX
- UX-SCN-XXX（如需要）
```

规则：

- 每个 SCN 只引用既有 FLOW。
- SCN 的进入条件不得弱于 FLOW 前置。
- SCN 不得新增主业务旅程、合法入口、成功终态或禁止路径。
- 前置由既有系统承接时，必须写明“由既有体验承接”以及恢复成功后进入哪个 PAGE。

## 4.8 Module Boundary Format

`04-功能拆解与边界说明.md` 只定义系统能力模块，不定义用户页面或技术实现。

模块格式：

```markdown
### MODULE-XXX：<模块名称>

模块类型：
- 核心业务能力模块
- 横向边界模块
- 外部能力适配依赖

关联 FLOW：
- FLOW-XXX

关联 SCN：
- SCN-XXX

模块业务责任：

模块非责任：

模块输入业务事实：

模块输出业务能力：

上游模块依赖：

下游消费方：

模块隔离边界：

旧流程/旧语义隔离责任：

优先级：
```

覆盖矩阵：

```markdown
## 业务旅程—场景—模块覆盖矩阵

| FLOW | SCN | 必须模块 | 主模块 | 协作模块 | 缺失模块后的结果 | 旧模块隔离要求 |
| --- | --- | --- | --- | --- | --- | --- |
```

规则：

- 每一条 P0 FLOW 必须至少有一个主模块承接。
- 每一个关键 SCN 必须至少有一个模块负责。
- 每个模块必须有明确“负责 / 不负责”。
- 每个关键旧流程必须有明确隔离模块。
- 任何旧审批、旧入口、旧状态、旧对象不得以“视情况复用”方式存在。
- 外部能力适配依赖只表达依赖关系，不定义 SDK、版本、鉴权、真实调用或 Provider 细节；这些属于 10。

旧对象处理只允许：

```text
inherit
adapt
create
deprecate
block
readonly
cleanup
```

禁止使用：

```text
尽量兼容
视情况复用
可能保留
后续再看
```

旧流程隔离格式：

```markdown
旧模块：

隔离要求：
- 不得服务哪些 FLOW：
- 不得成为哪些 MODULE 的输入：
- 不得成为哪些 MODULE 的状态来源：
- 不得成为哪些 MODULE 的生效来源：
```

示例：

```text
旧审批模块
× 不得为第二天任务开始模块提供提交路径
× 不得提供生效前置
× 不得提供状态来源
× 不得成为工作台下一步动作来源
```

## 4.9 UI/UX Design Format

`05-前端页面与UI/UX交互设计.md` 可以兼容旧文件路径 `05-前端页面与UI交互设计.md`，但正文标题和职责必须使用“UI/UX交互设计”。

05 必须区分：

- 交互合同确认：页面承接的 SCN、页面状态、主次操作、禁用操作、异常恢复和旧入口处理。
- 视觉资产确认：风格图、完整页面图、局部模块图、UX 交互图是否收到、审阅、确认或需要重做。

### PROMPT-STYLE-XXX：<全局风格统一性提示词>

必须覆盖：

- 产品类型
- 目标用户
- 使用端与设备尺寸
- 品牌与业务气质
- 色彩与层级
- 字体与信息密度
- 卡片、表单、按钮、导航、反馈组件语言
- 图标与插图风格
- 异常、空、加载、禁用状态风格
- 中文界面要求
- 一致性约束
- 禁止出现的风格或旧业务语义
- 适用 PAGE / UI-MOD / UX-SCN 范围

规则：

- PROMPT-STYLE 不生成某个具体业务页面。
- PROMPT-STYLE 是 PROMPT-PAGE、PROMPT-MODULE、PROMPT-UX 的共同风格前缀。

### PAGE-XXX：<页面名称>

页面提示词 ID：

```text
PROMPT-PAGE-<DOMAIN>-<SEQ>
```

页面提示词必须包含：

- 关联 FLOW / SCN / MODULE
- 页面目标
- 目标角色
- 合法进入条件
- 页面完整信息结构
- 当前 UI 状态
- 唯一主操作
- 次级操作
- 必须隐藏或禁用的操作
- 空、错、加载、阻断状态
- 成功后可见变化
- 失败后的恢复或退出
- 继承的全局风格要求
- 完整页面生成要求

规则：

- 页面提示词必须生成完整页面，不得只生成局部卡片。
- 每个 PAGE 必须定义合法进入条件。
- 每个 UI STATE 只能有 0 或 1 个主操作。
- 05 不得借页面设计改变 FLOW、资格、状态语义或权限规则。

### UI-MOD-XXX：<局部模块名称>

模块提示词 ID：

```text
PROMPT-MODULE-<DOMAIN>-<SEQ>
```

模块化设计只用于：

- 局部按钮状态变化
- 弹窗
- 抽屉
- 提示条
- 表单块
- 卡片局部变化
- 空状态模块
- 异常提示模块
- 上传重试模块
- 图标或状态反馈变化

模块提示词必须包含：

- 所属 PAGE
- 关联 SCN
- 基准页面或基准资产
- 局部模块范围
- 触发条件
- 变化前状态
- 变化后状态
- 用户可见结果
- 必须保留的周围 UI
- 必须保持的全局风格
- 禁止重画整页
- 禁止新增未确认业务动作

规则：

- 不是每个技术 MODULE 都必须生成 UI 图。
- 只有用户可见的页面或局部交互模块才需要 UI 设计资产。
- 先有页面整体设计，再补局部模块设计。

### UX-SCN-XXX：<UX交互场景名称>

UX 提示词 ID：

```text
PROMPT-UX-<DOMAIN>-<SEQ>
```

UX 必须优先复用已收到的页面图和模块图。

每个 UX 场景必须记录：

- 关联 FLOW
- 关联 SCN
- 起始 PAGE
- 经过的 PAGE / UI-MOD
- 用户动作
- 页面可见变化
- 成功结果
- 失败、重试、取消、返回与人工协助路径
- 已有 UI 图是否足以表达

UX 图状态只允许：

```text
covered_by_existing_ui_assets
ux_asset_required
ux_asset_received
ux_asset_confirmed
superseded
```

只有以下情况生成 PROMPT-UX：

- 现有静态页面图无法说明多步交互。
- 同一页面多状态切换无法说明。
- 异常恢复、取消、回退或人工协助路径不清楚。
- 弹窗、抽屉、多页面跳转关系不清楚。
- 旧入口迁移后的用户路径不清楚。

PROMPT-UX 必须生成多帧交互设计图，或带页面缩略图、箭头、状态说明的交互流程图。PROMPT-UX 不得重新设计页面视觉风格，不得重写 FLOW、资格、状态语义或权限规则。

### ASSET-XXX

```markdown
### ASSET-XXX

资产类型：
- global_style
- page_ui
- module_ui
- ux_interaction

关联：
- FLOW：
- SCN：
- MODULE：
- PAGE：
- UI-MOD：
- UX-SCN：
- PROMPT：

来源：
- user_provided
- user_generated
- external_reference

资产路径或引用：

资产状态：
- planned
- prompt_ready
- received
- review_pending
- visual_confirmed
- superseded

覆盖说明：

未覆盖项：

确认结论：
```

规则：

- 不得虚构图片、路径、设计资产或“已出图”结论。
- 用户未提供图时，只能是 `planned` 或 `prompt_ready`。
- 设计资产已生成不等于页面已开发、页面已测试、页面已验收或已上线。
- UI 依赖开发任务只能在所需页面或模块资产达到 `visual_confirmed` 后生成或进入可执行状态。
- 不依赖 UI 的后续规划文档不应被无故阻塞。

覆盖矩阵：

```markdown
## FLOW—SCN—MODULE—PAGE—设计资产覆盖矩阵

| FLOW | SCN | MODULE | PAGE | UI-MOD | UX-SCN | 页面图状态 | 模块图状态 | UX覆盖状态 | 开发前置状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

规则：

- 每个 P0 SCN 必须有 PAGE 和 UI STATE 承接。
- 每个关键异常 SCN 必须定义恢复、退出或人工协助界面。
- 每个 PAGE 必须定义合法进入条件。
- 每个 UI STATE 只能有 0 或 1 个主操作。
- 旧入口必须逐项定义唯一的页面处理方式：`redirect`、`block` 或 `readonly`。
- 不得同时把“跳转、阻断、只读”写成同一旧入口的并列候选。

## 4.10 Data / State Contract Format

`06-数据模型与状态流转.md` 是业务事实与状态合法性的唯一 SoT。

状态分类只允许：

```text
domain_state
derived_action_state
interaction_state
exception_state
legacy_boundary_state
data_domain_state
```

定义：

- `domain_state`：持久业务状态，例如已提交、已生效、已关闭。
- `derived_action_state`：由业务状态、资格、上下文和异常事实推导出的当前可做什么状态，例如当前可提交、当前需补资料。
- `interaction_state`：UI 暂态，例如确认弹窗打开、提交中、上传中、重试中；默认由 03 / 05 管理，只有确实需要持久化、断点恢复或审计时，才可升为 06 状态。
- `exception_state`：业务或外部能力失败后需要恢复、补充或人工协助的状态。
- `legacy_boundary_state`：旧入口、旧对象、旧审批、旧状态的只读、阻断、迁移或清理边界。
- `data_domain_state`：测试、预发布、生产等数据域及其隔离状态。

06 必须包含：

```markdown
## FLOW—事实—事件—状态映射

| FLOW | 前置业务事实 | 触发事件 | 允许状态变化 | 成功事实 | 阻断事实 | 关联 MODULE | 关联 API | 关联 TEST |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

每一个 P0 FLOW 必须具备：

- 前置业务事实
- 明确触发事件
- 允许状态变化
- 成功后的新业务事实
- 阻断事实
- 非法来源

状态分类表：

```markdown
| 状态 ID | 状态类别 | 是否持久化 | 唯一来源 | 触发事件 | 可读取方 | 可触发变化者 | 下游用途 |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

规则：

- 派生动作状态不得成为业务写入的唯一放行依据。
- 前端、路由、本地缓存、旧审批记录、旧入口来源不得自行生成或伪造状态。
- 派生动作状态必须由后端根据真实业务状态、资格、上下文和异常事实稳定推导。
- 禁止把“没有任务”直接迁移为“可打卡”或其他可写状态。
- 可执行状态必须通过任务已分配、项目/资源/业务范围上下文完整、当前用户具备资格等明确业务事实重新计算。
- “字段”只能表示业务逻辑所需事实，不得定义表名、字段类型、长度、索引、外键、SQL、ORM Schema 或迁移脚本。

状态迁移守卫格式：

```markdown
状态迁移：

触发事件：

前置事实：

允许角色资格：

允许数据范围：

禁止来源：

成功后的新事实：

失败后的阻断状态：

是否可重试：

是否可回滚：

关联 API：

关联 PERM：

关联 TEST：
```

不得只写：

```text
A -> B
```

旧对象与旧状态隔离映射：

```markdown
## 旧对象与旧状态隔离映射

| 旧对象 / 旧状态 | 当前允许用途 | 不可映射目标 | 是否可读取 | 是否可写入 | 是否可作为状态来源 | 处理策略 |
| --- | --- | --- | --- | --- | --- | --- |
```

处理策略只允许：

```text
inherit
adapt
create
deprecate
block
readonly
cleanup
```

旧审批、旧申请、旧状态若只能用于历史只读，必须明确：

- 不得成为新流程写入前置。
- 不得成为新流程生效来源。
- 不得成为新工作台下一步动作来源。
- 不得映射为任何新流程有效状态。

## 4.11 Canonical API Contract Format

`07-接口设计与前后端契约.md` 定义前后端读写、拒绝和恢复语义的 Canonical API Contract。

接口类型：

```text
QUERY
COMMAND
DECISION_VIEW
LEGACY_BOUNDARY
```

定义：

- `QUERY`：只读取业务事实，不改变状态。
- `COMMAND`：触发业务事件，可能改变业务事实或状态。
- `DECISION_VIEW`：返回由 06 推导出的当前可操作状态或下一步动作，只读。
- `LEGACY_BOUNDARY`：定义旧对象、旧接口、旧入口的只读、阻断、迁移或解析边界。

规则：

- DECISION_VIEW 不得成为业务状态唯一来源。
- DECISION_VIEW 不得绕过 COMMAND 的状态守卫。
- 前端不得使用本地缓存、旧接口、旧审批状态或来源参数自行推导主操作。
- 07 不得把 08 作为正式上游 SoT。
- 07 可以引用 02 的业务资格关系，以及 06 的状态前置、触发事件和迁移守卫。
- 07 只声明接口所需的访问上下文、业务资格、状态与事实前置，不重写完整权限矩阵、数据可见范围策略或越权展示策略。

Canonical Contract 与 Architecture Binding 分离：

```text
07 Canonical API Contract：
- 业务意图
- 请求语义
- 响应语义
- 错误语义
- 状态守卫
- 禁止字段
- 幂等与并发语义

09 Architecture Binding / Implementation Boundary：
- 目标逻辑承接层
- 依赖方向
- 可复用技术基础
- 禁止复用旧语义
- 旧流程切断位置
```

规则：

- 09 不得擅自改变 07 的方法、路径、请求语义、响应语义、状态前置或错误语义。
- 09 不定义具体文件路径、目录、代码、SDK 初始化、环境变量名称、任务拆分或实际实施结果。
- 若 Canonical API Contract 发生改变，必须回写 07，并触发 08、11、13 等下游失效传播。

单接口格式：

```markdown
API-ID：

Contract Type：
- QUERY / COMMAND / DECISION_VIEW / LEGACY_BOUNDARY

关联 FLOW：
关联 SCN：
关联 MODULE：
关联 PAGE / UI-MOD：

业务意图：

触发业务事件：
- COMMAND 必填
- QUERY / DECISION_VIEW 不适用时显式标记

合法访问上下文：

所需业务资格：

状态与事实前置：
- 只引用 06，不重新定义

请求：
- 允许字段
- 禁止字段
- 字段业务语义

成功结果：
- 返回的新业务事实
- 返回的状态引用
- 是否返回最新决策视图

拒绝结果：
- errorCode
- errorClass
- retryable
- safeRecovery
- nextUserIntent

幂等与并发：
- 幂等要求
- 重复提交结果
- 并发冲突结果

旧流程边界：
- 禁止读取的旧状态
- 禁止写入的旧对象
- 历史兼容唯一允许范围

Canonical Physical Binding：
- 方法
- 路径
- 稳定性说明

关联 TEST：
- 正向合同测试
- 输入非法测试
- 状态守卫测试
- 权限 / 范围测试
- 幂等与并发测试
- 旧流程隔离测试
```

所有会改变业务状态的 `COMMAND` 必须明确：

- 幂等策略：必须使用幂等键，或明确等价的服务端去重策略。
- 重复提交：不得重复创建业务事实或重复改变状态；必须返回稳定的同一业务结果或最新业务摘要。
- 并发冲突：必须返回稳定错误码、冲突结果或最新状态摘要。
- 成功响应：必须返回足以刷新页面与决策视图的最新业务事实。

具体并发一致性架构边界由 09 决定；数据库锁、事务、缓存等代码实现方式由 13/14 和执行层承接。

旧审批与旧接口的接口级封锁：

若业务明确“新流程直接生效，不经过旧审批”，对应 COMMAND 必须显式定义：

```text
禁止输入字段：
- taskRequestId
- approvalStatus
- approvedBy
- approvalAction
- pendingApproval
- approved
- rejected
- 以及任何等价审批字段

禁止状态来源：
- 旧审批记录
- 旧申请记录
- 管理员审批结果
- 旧任务申请上下文

禁止返回语义：
- PENDING_APPROVAL
- APPROVED
- REJECTED
- 待管理员审核
- 管理员审批完成
```

历史旧对象若允许读取，必须明确：

```text
只读展示
≠ 新流程判断依据
≠ 新流程写入依据
≠ 新流程生效依据
≠ 新工作台下一步动作来源
```

`source` 参数语义：

```text
source = 客户端来源、兼容判断或审计辅助信息

source ≠ 身份
source ≠ 角色
source ≠ 项目 / 资源 / 业务范围
source ≠ 提交资格
source ≠ 状态放行条件
```

## 4.12 Permission / Scope / Deny Strategy Format

`08-权限、数据可见性与异常处置边界说明.md` 定义后端不可绕过的访问决策、数据范围、拒绝分类、异常协助与历史访问策略。

访问决策模型：

```text
已认证用户
+ 目标动作
+ 目标资源
+ 租户 / 项目 / 资源 / 业务范围
+ 业务资格
+ 当前业务状态
+ 当前数据域
```

拒绝类型只允许：

```text
authentication_denied
authorization_denied
scope_denied
state_guard_denied
legacy_source_denied
data_domain_denied
external_capability_blocked
```

定义：

- `authentication_denied`：未认证或会话无效。
- `authorization_denied`：无角色或业务资格。
- `scope_denied`：不在租户、项目、资源、任务等可访问范围。
- `state_guard_denied`：业务前置、业务状态或迁移守卫不满足。
- `legacy_source_denied`：旧对象、旧状态、旧审批、旧入口试图影响新流程。
- `data_domain_denied`：测试、预发布、生产等数据域隔离违规。
- `external_capability_blocked`：定位、图片、外部平台等能力失败，需恢复或人工协助。

不得把这些全部笼统写成“权限不足”或“异常”。

范围词典：

```text
SELF_TASK
ASSIGNED_REGION
MANAGED_PROJECT
CURRENT_TENANT
TEST_DOMAIN
PRODUCTION_DOMAIN
HISTORICAL_READONLY
```

如项目有其他稳定范围，使用同样结构扩展；禁止自然语言模糊表达。

权限策略格式：

```markdown
PERM-ID：

关联 FLOW：
关联 API：
关联 DOMAIN：
关联 STATE：

动作：

资源：

允许主体：

允许范围：

业务资格：

业务状态前置：

数据域前置：

允许结果：

拒绝类型：

拒绝原因码：

是否允许只读：

是否允许人工协助：

旧流程禁止来源：

关联 TEST：
```

规则：

- 前端隐藏、禁用或不展示按钮，只是体验。
- 08 定义的 PERM 决策，必须由后端或服务端边界实际执行。
- 任何前端、接口参数、来源参数、旧审批记录、旧入口、管理员身份都不得绕过 PERM 决策。

工作人员协助边界：

```text
工作人员协助 = 诊断、技术恢复、引导用户回到正常路径

工作人员协助 ≠ 代替用户提交业务动作
工作人员协助 ≠ 直接修改正常业务状态
工作人员协助 ≠ 代替业务资格主体生效
工作人员协助 ≠ 代替资源负责人、业务负责人或其他业务角色完成关键动作
```

每一项工作人员协助必须定义：

- 能读取什么诊断信息。
- 可执行什么技术动作。
- 不能修改什么业务事实。
- 协助完成后用户回到哪个合法场景。

若确实需要人工改变业务事实，必须回到 01、02、06 定义新的合法业务事件，不得由 08 默认放行。

旧流程与历史访问边界：

- 旧对象没有任何新流程 COMMAND 权限。
- 历史记录只有在满足 HISTORICAL_READONLY 范围时允许读取。
- 旧对象、旧审批、旧状态不得作为新流程状态、资格、前置或生效来源。
- 具体用户跳转、阻断页面、只读页面由 03 / 05 定义。
- 具体接口实现、旧路由删除、旧服务迁移由 09 定义逻辑切断位置，并由 13/14 和执行层承接。

## 4.13 06/07/08 Test Mapping Format

06、07、08 都必须成为 11 自动化测试设计的上游依据，但不得把 11 重写为测试执行文档。

每条关键 `STATE`、`API`、`PERM` 必须明确关联 TEST-ID，并至少覆盖：

- 正向业务规则测试
- 非法输入测试
- 非法状态迁移测试
- 资格拒绝测试
- 范围拒绝测试
- 数据域隔离测试
- 幂等测试
- 并发冲突测试
- 旧流程来源拒绝测试
- 历史只读测试
- 工作人员协助越界测试

自动化等级只允许：

```text
mandatory_automated
automated_preferred
manual_or_real_environment_required
```

原则：

- API 合同、状态迁移、权限、范围、幂等、并发、旧流程隔离默认必须自动化。
- 视觉一致性、复杂体验、真机硬件能力、外部真实环境可标记为人工或真实环境验证。

## 4.14 Architecture Decision / Binding Format

`09-架构设计与关键决策.md` 将已确认的业务语义、状态、接口和权限绑定到项目内部逻辑架构、边界和切换策略中。

09 启动前必须读取并引用：

```text
PROJECT-CURRENT-BASELINE.md
```

09 必须明确区分：

- 当前生产中真实生效的模块、入口、调用链。
- 已开发但未发布的模块。
- 仓库中存在但已废弃的模块。
- 仅用于历史追溯的模块。
- 本期允许复用的技术基础。
- 本期禁止复用的旧业务语义。

ARCH 决策记录最小格式：

```markdown
### ARCH-XXX：<架构决策名称>

关联 FLOW：
关联 MODULE：
关联 STATE / EVENT：
关联 API：
关联 PERM：
关联 CAP：

架构当前基线：

目标逻辑架构：

逻辑承接位置：

允许复用的技术基础：

禁止复用的旧语义：

旧流程切断位置：

数据域、部署与发布架构边界：

切换策略：

回退策略：

对 10 / 11 / 13 的输入：

架构风险移交项：
```

09 必须包含：

```markdown
## Canonical Contract—Architecture Binding

| FLOW | MODULE | STATE / EVENT | Canonical API | 目标逻辑承接层 | 可复用技术基础 | 禁止复用旧语义 | 旧流程切断位置 | 关联 CAP | 下游 TASK |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

规则：

- 每条 P0 FLOW 最终必须有逻辑层承接。
- 每个 Canonical API Contract 必须有 Architecture Binding。
- 可复用技术基础必须写清楚“复用什么”。
- 禁止复用旧语义必须写清楚“绝不复用什么”。
- 不得使用“按实现时决定”“视情况复用”“后续再看”。

09 必须包含：

```markdown
## Legacy Semantic Firewall

| 旧模块 / 旧对象 / 旧状态 | 是否可读取 | 是否可写入 | 是否可进入新 Command | 是否可影响新 State | 是否可影响 Decision View | 是否可作为生效来源 | 处理策略 |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

处理策略只允许：

```text
inherit
adapt
create
deprecate
block
readonly
cleanup
```

规则：

- 旧审批、旧申请、旧入口、旧状态不得通过“技术复用”重新进入新流程。
- 旧对象若允许历史读取，只允许 `readonly`。
- 历史只读旧对象不得成为新流程前置、状态来源、下一步动作来源或生效来源。
- 09 只定义内部是否需要某类能力端口、依赖方向和隔离边界。
- 具体地图服务、云服务、企业协作平台、AI Provider、SDK、版本或鉴权方式由 10 决定。
- 外部能力未完成 10 选型确认时，09 只能定义 `CAPABILITY PORT`、`ARCHITECTURE REQUIREMENT`、`ADAPTER BOUNDARY`，不得把具体 Provider 绑定标记为 `confirmed`。
- 架构风险只移交 12；09 不创建正式 `RISK-ID`、风险等级或风险闭环。

## 4.15 Capability Decision Card

`10-外部能力选型与接入决策.md` 是外部能力的选型与接入决策合同。若项目保留旧文件路径 `10-外部能力与集成治理.md`，正文标题和职责必须使用“外部能力选型与接入决策”。

文档确认状态与能力就绪状态必须分开：

```text
文档确认状态：
草案 / 已确认

CAP 选型状态：
identified
candidate
confirmed
rejected
superseded
deprecated

CAP 真实就绪状态：
not_ready
official_sot_verified
preconditions_ready
real_environment_verified
release_ready
blocked
```

规则：

- 10 已确认不等于能力已接入。
- 10 已确认不等于能力已真实验证。
- 10 已确认不等于能力可上线。
- 未完成 Capability Development-Entry Evidence Gate 的 CAP，不得进入相关开发任务。
- planning 阶段允许写入 `identified`、`candidate`、`confirmed`、`official_sot_verified`、`preconditions_ready`、`blocked`。
- planning 阶段禁止写入 `real_environment_verified` 或 `release_ready`。
- Adapter、真实调用、代码证据、真实设备和真实环境验证只属于后续执行 / 测试 / 验收要求。
- 页面可打开、JSSDK ready、Mock 成功、代码存在，均不得视为真实能力成功。

能力格式：

```markdown
### CAP-XXX：<能力名称>

关联 FLOW：
关联 MODULE：
关联 SCN：
关联 ARCH：

业务需要：

能力边界：
- 必须支持：
- 明确不支持：

候选方案：
- Candidate A：
- Candidate B：

当前选型：
- 状态：
- 选择结果：

选择理由：

官方事实：
- 官方来源：
- SDK / API / Provider 版本：
- 官方更新时间或访问日期：

适用端与运行前提：
- 运行环境：
- 鉴权：
- 权限 / Scope：
- 网络：
- 额度 / 限流：
- 计费：
- 合规：

能力失败影响：
- 影响 FLOW：
- 影响范围：
- 上游业务处理引用：

Capability Development-Entry Evidence Gate：

Capability Realization Requirement：

Capability Acceptance Requirement：

关联 TEST：
关联 RISK：
关联下游 TASK：
```

边界：

- 10 可以定义能力失败类型、技术前提、真实可用验证要求，以及能力失败影响哪个 FLOW 或 SCN。
- 10 不得自行决定用户进入哪个页面、用户补什么资料、用户是否完成业务闭环、谁代替谁提交业务动作或某个业务状态是否迁移。
- `source`、容器来源、JSSDK ready、页面打开、Mock 返回、历史代码存在，不得成为身份、资格、权限、业务状态或真实能力成功依据。
- 10 不定义 Adapter 代码、SDK 调用代码、接口字段映射、具体实现文件、开发任务、实际接入结果或最终验收结果。

## 4.16 Test Design Format

`11-测试设计与验收用例.md` 以 01 的 FLOW 为主线，将业务、状态、接口、权限、旧流程隔离、外部能力和 UI/UX 结论转化为可执行、可自动化、可验收的测试设计合同。

测试类型：

```text
business_flow
state_transition
api_contract
permission_scope
legacy_boundary
capability_real_environment
ui_behavior
ux_interaction
visual_review
regression
release_gate
```

自动化等级：

```text
mandatory_automated
automated_preferred
manual_or_real_environment_required
```

单条测试设计格式：

```markdown
### TEST-XXX：<测试名称>

测试类型：

关联 REQ：
关联 FLOW：
关联 SCN：
关联 DOMAIN：
关联 STATE：
关联 API：
关联 PERM：
关联 CAP：
关联 PAGE / UI-MOD / UX-SCN：

测试目标：

业务前置：
- 身份 / 会话：
- 组织 / 租户：
- 角色与资格：
- 项目 / 区域范围：
- 任务与业务事实：
- 数据域：

逻辑测试步骤：
1.
2.
3.

预期业务结果：

预期状态结果：

预期接口结果：

预期用户可见结果：

反向 / 禁止路径：

自动化等级：
- mandatory_automated
- automated_preferred
- manual_or_real_environment_required

真实环境要求：

预期证据要求：

关联 RISK：
```

11 必须包含：

```markdown
## FLOW—测试覆盖矩阵

| FLOW | 正向流程 | 状态测试 | API 测试 | 权限测试 | 旧流程测试 | CAP 测试 | UI/UX 测试 | 自动化等级 | 最终验收来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

业务测试顺序必须继承 01 的 FLOW：

```text
身份 / 会话 / 访问上下文
-> 进入工作台或业务入口
-> 核心业务动作
-> 异常与恢复
-> 当前周期闭环
-> 后续周期动作
-> 旧流程和历史对象隔离
-> 外部能力与发布门禁
```

每条 P0 FLOW 至少必须覆盖：

- 正向业务流程。
- 状态与前置阻断。
- API 合同。
- 权限与范围。
- 旧流程隔离。
- 回归测试。

涉及外部能力时，增加：

- `capability_real_environment`

涉及页面和 UX 时，增加：

- `ui_behavior`
- `ux_interaction`
- `visual_review`

默认必须标记为 `mandatory_automated`：

- 状态迁移。
- 业务前置阻断。
- API 合同。
- 输入非法。
- 权限与范围。
- 幂等。
- 并发冲突。
- 旧流程隔离。
- 历史只读边界。
- 测试与生产数据域隔离。

允许标记为 `manual_or_real_environment_required`：

- 真实设备定位、相机、麦克风、企业协作平台或其他平台容器能力。
- 视觉一致性与信息层级。
- 复杂 UX 使用体验。
- 真实网络、权限、配额、限流和 Provider 行为。

规则：

- 每一条 P0 FLOW 必须有完整测试覆盖。
- 若某个 FLOW 的关键测试缺失，11 不得确认。
- 若某项测试无法自动化，必须明确原因、真实环境要求和最终验收方式。
- 自动化测试通过不等于真实环境能力已验收。
- 视觉评审通过不等于接口、权限、状态与旧流程隔离已证明。
- 11 不记录测试命令、测试代码、fixture 脚本、执行调度、重试命令、实际执行状态或实际测试结果。

## 4.17 Risk / Task / Execution / Acceptance Framework Format

### 12 RISK / DEP / OPEN Format

`12-风险、依赖与待决策事项.md` 是正式 RISK / DEP / OPEN 的唯一 SoT。若项目保留旧路径 `12-风险、依赖与待确认项.md`，正文标题和职责必须使用“风险、依赖与待决策事项”。

01–11 只能输出：

- 风险信号。
- 风险移交项。
- 阻断提示。
- 待确认问题。

12 必须归并信号，并为每个独立风险生成唯一正式 `RISK-ID`。同一外部能力未验证问题、同一旧流程重新进入新主流程问题，不得在多个文档中拥有多个正式 `RISK-ID`。

类型定义：

| 类型 | 定义 | 是否允许进入 13 |
| --- | --- | --- |
| `RISK` | 某个不确定条件可能造成业务、数据、安全、交付或上线损害 | 可以，但必须有治理策略 |
| `DEP` | 某任务或目标成立前必须满足的外部、环境、顺序、事实或跨团队前提 | 可以，但必须明确阻断范围 |
| `OPEN` | 尚未拍板，且会影响业务语义、交互路径、架构边界、能力选型或验收标准的问题 | 不可以直接进入任务 |

RISK 格式：

```markdown
### RISK-XXX

风险类别：
风险等级：
Priority：

来源信号：
关联 FLOW：
关联 DOMAIN / STATE / API / PERM / ARCH / CAP / TEST：

风险描述：

触发条件：

影响范围：

阻断阶段：
- planning_confirmation
- task_generation
- execution_start
- acceptance
- release
- baseline_update

处理策略：
- avoid
- mitigate
- transfer
- accept_deferred

关联 DEP：
关联 OPEN：
关联 TASK：
关联 TEST：

关闭条件：

关闭证据类型：

风险状态：
- identified
- planned
- mitigating
- verification_pending
- closed
- accepted_deferred
- reopened
```

DEP 格式：

```markdown
### DEP-XXX

依赖对象：

依赖类型：
- external_provider
- external_decision
- project_baseline
- environment
- sequencing
- cross_team
- release

必须满足的事实：

阻断范围：

验证来源：

最晚解除阶段：

关联 RISK：

状态：
- unknown
- pending
- verified
- unavailable
- superseded
```

OPEN 格式：

```markdown
### OPEN-XXX

待决问题：

为什么不能默认：

影响的 SoT：

候选方案：

推荐方案：

需要确认的主体：

最晚确认阶段：

未确认时阻断什么：

确认后回写目标：

状态：
- open
- awaiting_user
- confirmed
- rejected
- superseded
```

规则：

- 已确认且已有正式 SoT 承接的业务规则，不得再次作为 RISK 或 OPEN 进入 12。
- 关键 OPEN 未关闭，不得生成对应 TASK。
- OPEN 的关闭必须先回写真正拥有该事实的上游 SoT；上游结论确认后，12 才能记录 resolved / confirmed 及其来源。
- 12 不重复定义已确认业务规则、状态、接口、权限或 UI 事实。

### 13 Task Contract Format

`13-开发任务合同与落地清单.md` 将已确认、可执行、可验证的规划结论整理为任务合同、依赖关系、并行边界、完成证明要求与后续执行记录框架的输入。若项目保留旧路径 `13-开发任务拆分与落地清单.md`，正文标题和职责必须使用“开发任务合同与落地清单”。

13 只能接收：

- 已确认 FLOW / DOMAIN / SCN / MODULE / PAGE。
- 已确认 STATE / API / PERM。
- 已确认 ARCH / CAP。
- 已定义 TEST。
- 已定义 RISK / DEP。
- 已关闭或不影响本任务的 OPEN。

13 输入闭包：

- 只要本期需要生成 13 TASK，就必须同时具备 11 测试设计与验收用例、12 风险/依赖/待决策事项，以及所有被 TASK 引用且已确认的上游 SoT。
- TASK 不得引用不存在、未装配或未确认的 FLOW / STATE / API / PERM / ARCH / CAP / TEST 结论。
- 15 不得作为可独立装配的孤立文档；只能由已确认的 13 连同 14 一起自动派生。

禁止：

- 关键 OPEN 未关闭时生成 TASK。
- 能力选型未确认时生成 `capability_integration` TASK。
- 接口合同未确认时生成接口实现 TASK。
- 旧流程处理方式未确认时生成 `legacy_cutover` TASK。

TASK 格式：

```markdown
### TASK-XXX：<任务名称>

任务类型：
- implementation
- legacy_cutover
- capability_integration
- test_enablement
- release_readiness_automation
- verification_handoff

Priority：

承接业务目标：
- FLOW：
- SCN：
- MODULE：

执行输入：
- DOMAIN：
- STATE / EVENT：
- API：
- PERM：
- ARCH：
- CAP：
- TEST：
- RISK：
- DEP：

任务目标：

允许复用的技术基础：

禁止复用的旧语义：

逻辑影响面：
- backend:
- frontend:
- platform:
- operations:

候选影响文件：
- 路径：
- 可信度：
- 是否必须在执行前核实：

任务前置：
- 已确认 SoT：
- 已解除 DEP：
- 不允许存在的 OPEN：
- 上游 TASK：

并行边界：
- 可并行：
- 不可并行：
- 共享资源：

Task Ready Gate：

完成合同：
- 应实现的能力：
- 应保持的禁止关系：
- 必须覆盖的 TEST：
- 应进入 14 的预期验证项：
- 发现偏差时的回写目标：
```

Task Ready Gate 必须明确：

- 上游 SoT 已确认。
- 不存在阻断本任务的 OPEN。
- 必要 DEP 已验证，或阻断机制已明确。
- 必要 CAP 已完成开发前门禁。
- 上游 TASK 已满足，或并行边界已明确。

Task Completion Contract 必须明确：

- 应实现的目标能力。
- 应保持的禁止关系。
- 必须具备执行条件的 TEST。
- 必须预留的验证与交接信息。
- 发现规划偏差时的回写目标。

规则：

- 候选文件路径不等于已确认实现事实。
- 规划阶段只确认逻辑影响面。
- 文件、目录、代码位置和具体实现方式只能作为候选影响面，必须在后续执行前核实。
- 不得在 TASK 中使用“按实现时决定”“可选 A / B / C”“视情况复用”“后续再看”。
- Task Completion 不等于最终验收、真实环境能力通过、已发布或 PROJECT-CURRENT-BASELINE 已更新。

13 必须显式识别并写明：

- 共享 STATE。
- 共享 API Contract。
- 共享权限边界。
- 共享路由入口。
- 共享旧流程切断点。
- 共享数据域。
- 共享发布配置。
- 哪些 TASK 可并行。
- 哪些 TASK 必须串行。
- 哪些 TASK 完成前下游不可开始。
- 哪些 TASK 完成前其他 TASK 不得声明完成。

13 确认规则：

- Task Contract Gate 只校验 13 自身及其上游 01–12。
- 14、15 的预先存在不得作为 13 确认前置。
- 13 被用户确认并回写 `状态: 已确认` 后，才触发 14、15 框架派生。

### 13 to 14 / 15 Framework Derivation Rule

唯一顺序：

```text
12 已确认
-> 生成 13 草案
-> 用户确认 13
-> 回写 13：已确认
-> 自动触发 14、15 框架派生
-> 自动生成 14 与 15 的正式框架
-> 对 14、15 运行 Execution and Acceptance Framework Derivation Gate
-> 汇总实际已生成的 assembled_documents
-> 基于实际路径生成 handoff_role_mapping
```

14、15 是从已确认 13 自动派生的框架对：

- 不触发“每次只能生成一份正式文档”的限制。
- 不需要分别进行生成前协作确认。
- 不需要把 14、15 的独立用户确认作为 Planning 完成前提。
- 自动生成后只向用户输出简洁说明：已生成执行记录框架与验收框架，当前只预置待填事实位置，不代表开发完成、测试通过、可发布或已发布。
- 框架状态必须和实际事实状态分离。
- 14、15 自动派生后不得写入 `文档状态：已确认`。

### 14 Execution Record Framework Format

`14-开发执行与联调变更记录.md` 是后续执行事实的承载框架。planning skill 在 13 被确认后必须自动创建 14 的正式框架，但不得填写任何实际发生的事实。

固定结构：

```text
1. 文档边界
2. 执行基线
3. TASK 执行状态矩阵
4. 预期执行合同
5. 实际执行记录区
6. 自动化验证索引区
7. 偏差、阻断与回写请求区
8. 外部能力、环境与真实验证待补项
9. 测试交接区
```

文档必须包含：

```text
框架生成状态：generated
框架完整性：complete
用户独立确认：not_required
实际事实状态：not_started
```

解释必须写入：

```text
框架生成状态：generated
框架完整性：complete
用户独立确认：not_required
实际事实状态：not_started
= 执行框架和预期合同已经由已确认 13 自动派生且预置完整

不代表
= 实际开发已经开始或完成
```

每个 TASK 必须自动预置：

```markdown
### EXEC-<TASK-ID>

关联 TASK：
关联 FLOW：
关联 STATE / API / PERM / ARCH / CAP / TEST：

执行基线：
- 任务版本：
- 上游 SoT：

预期实现目标：

预期验证范围：

实际改动：
- 待填写

实际结果：
- not_started

验证覆盖：
- 待填写

联调等级：
- 待填写

与计划差异：
- 待填写

回写要求：
- 待填写

交接：
- 待填写
```

不得把“待填写”替换成推测性的实际结果。
所有 EXEC、TEST、CAP、发布与基线事实初始只能是 `not_started` 或空白待填；不得因框架生成而使用“通过、失败、已验收、可发布、已发布、生产已更新、基线已更新”等状态。

### 15 Acceptance and Retrospective Framework Format

`15-验收结果与复盘.md` 是后续验收、真实环境验证、发布判定与复盘事实的承载框架。planning skill 在 13 被确认后必须自动创建 15 的正式框架，但不得填写任何实际验收或发布结论。

固定结构：

```text
1. 文档边界
2. 验收基线
3. FLOW 验收矩阵
4. TEST 实际结果区
5. CAP 真实环境验证区
6. RISK / DEP 关闭判定区
7. P0 / P1 / P2 发布门禁区
8. 发布判定与发布事实区
9. PROJECT-CURRENT-BASELINE 更新条件与结果区
10. 复盘
11. 下一期输入
```

文档必须包含：

```text
框架生成状态：generated
框架完整性：complete
用户独立确认：not_required
实际事实状态：not_started
```

解释必须写入：

```text
框架生成状态：generated
框架完整性：complete
用户独立确认：not_required
实际事实状态：not_started
= 验收框架与预期验收对象已经由已确认 13 自动派生且预置完整

不代表
= 本期已经验收、发布或完成基线更新
```

FLOW 验收矩阵：

```markdown
| FLOW | 关联 TEST | 自动化证据 | 人工 / 真实环境证据 | RISK 关闭条件 | 验收状态 | 发布影响 |
| --- | --- | --- | --- | --- | --- | --- |
```

planning skill 只允许预填：

- FLOW。
- 关联 TEST。
- 预期证据类型。
- 风险关闭条件。
- 发布影响。
- 验收状态初始值。

禁止预填：

- 通过。
- 失败。
- 已验收。
- 真实环境已通过。
- 可发布。
- 已发布。
- 生产已更新。
- PROJECT-CURRENT-BASELINE 已更新。

规则：

- 15 不得独立装配或提前生成。
- 15 只能在 13 已确认后与 14 一起自动派生。
- 15 初始验收状态只能是 `not_started` 或空白待填。
- 15 不得因框架生成写入通过、失败、已验收、真实环境已通过、可发布、已发布、生产已更新或 PROJECT-CURRENT-BASELINE 已更新。

### 12/13/14/15 State Separation Rule

必须始终区分：

```text
框架已生成且完整
≠ 实际开发完成
≠ 自动化验证通过
≠ 真实环境通过
≠ 最终验收通过
≠ 已发布
≠ 项目当前基线已更新
```

## 5. 引用规范

关键结论必须使用显式引用。

```markdown
## 关联需求

- REQ-USER-001
- REQ-ORDER-002

## 上游依赖

- 02-业务域模型.md#DOMAIN-USER-001

## 下游影响

- 07-接口设计与前后端契约.md#API-ORDER-001

## SoT来源

- 01-需求范围与验收标准.md#REQ-ORDER-001
```

规则：

- 所有关键结论必须可追踪
- 禁止隐式依赖
- 禁止自然语言模糊引用

## 6. 状态机格式规范

```markdown
## 状态定义

状态：STATE-ORDER-REVIEWING
状态值：REVIEWING

允许来源：
- CREATED

允许去向：
- APPROVED
- REJECTED

非法迁移：
- ARCHIVED -> REVIEWING

回滚规则：
- APPROVED 可回滚至 REVIEWING
```

规则：

- 所有状态必须显式定义
- 所有迁移必须可验证
- 禁止隐式状态流

## 7. 风险等级规范

风险等级：

```text
LOW
MEDIUM
HIGH
BLOCKER
```

说明：

- 正式 `RISK-ID` 只能由 12 创建。
- 12 的正式 RISK / DEP / OPEN 格式见 `## 4.17 Risk / Task / Execution / Acceptance Framework Format`。
- 下列格式仅用于非正式风险信号或历史兼容读取，不得替代 12 的正式格式。

风险信号格式：

```markdown
风险ID：
风险等级：
影响范围：
触发条件：
应对策略：
确认状态：
```

规则：

- 风险必须带等级
- 风险必须带影响范围
- 风险必须带触发条件

## 8. 下游验证结果引用规范

本规范只用于 14/15 等下游执行/验收文档引用结果结构。
planning-layer-runtime 不生成、填写或推断执行结果。

```markdown
验证项：
验证来源：
预期结果：
实际结果：
验证状态：
证据：
```

规则：

- 验收必须结构化
- 禁止仅写“已完成”
- 禁止无证据验收

## 9. 流程格式

使用：

```text
步骤A
-> 步骤B
-> 步骤C
```

## 10. 接口格式

使用：

```http
GET /api/example
```

## 11. JSON 格式

使用：

```json
{
  "success": true
}
```

## 12. 命令格式

使用：

```powershell
pnpm test
```

## 13. 企业级 SaaS 固定检查项

仅补充字段，不写实现方案。

### 02-业务域模型.md

```markdown
## 业务域权限关系

业务域：
角色：
权限：
数据可见范围：
越权策略：
```

检查：

- RBAC扩展
- ABAC扩展
- 多租户扩展
- 权限与业务域绑定
- 角色与权限动态绑定
- 禁止数据库实现、代码逻辑、前端行为

### 05-前端页面与UI/UX交互设计.md

```markdown
## 交互合同确认

关联 SCN：
关联 MODULE：
PAGE / UI-MOD / UX-SCN：
合法进入条件：
主操作：
禁用或隐藏操作：
异常恢复：
旧入口处理：

## 设计资产索引

ASSET：
PROMPT：
资产状态：

## 覆盖矩阵

FLOW—SCN—MODULE—PAGE—设计资产覆盖矩阵
```

检查：

- UI进入SoT链路
- 交互合同与视觉资产分开确认
- 设计提示词和资产索引可追踪
- 用户未提供图时，资产只能是 `planned` 或 `prompt_ready`
- 不得把设计资产状态写成已开发、已测试、已验收或已上线

### 06-数据模型与状态流转.md

```markdown
## 业务事实与状态合法性

核心业务数据事实：

业务事件：

状态分类：

状态唯一来源：

迁移守卫：

旧对象 / 旧状态隔离映射：

数据域治理边界：

下游 API / PERM / TEST 映射：
```

检查：

- 状态分类清晰
- 状态唯一来源可追踪
- 迁移守卫完整
- 旧状态隔离明确
- 数据域边界明确
- 禁止生成表名、字段类型、索引、外键、SQL、ORM Schema 或迁移脚本

### 08-权限、数据可见性与异常处置边界说明.md

```markdown
## 访问决策与拒绝边界

PERM-ID：
动作：
资源：
允许主体：
允许范围：
业务资格：
业务状态前置：
数据域前置：
拒绝类型：
拒绝原因码：
工作人员协助边界：
旧流程禁止来源：
```

检查：

- 测试数据也是权限
- 权限决策可追踪
- 数据范围结构化
- 拒绝类型不得混写
- 后端必须执行 PERM 决策
- 历史对象只读边界明确

### 09-架构设计与关键决策.md

```markdown
## Canonical Contract—Architecture Binding

| FLOW | MODULE | STATE / EVENT | Canonical API | 目标逻辑承接层 | 可复用技术基础 | 禁止复用旧语义 | 旧流程切断位置 | 关联 CAP | 下游 TASK |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Legacy Semantic Firewall

| 旧模块 / 旧对象 / 旧状态 | 是否可读取 | 是否可写入 | 是否可进入新 Command | 是否可影响新 State | 是否可影响 Decision View | 是否可作为生效来源 | 处理策略 |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

检查：

- 必须读取并引用 PROJECT-CURRENT-BASELINE。
- 每条 P0 FLOW 都有逻辑架构承接位置。
- 每个 Canonical API Contract 都有 Architecture Binding。
- 允许复用的技术基础与禁止复用的旧业务语义必须分开写。
- 旧审批、旧入口、旧状态无法进入新 Command、新 State 或新 Decision View。
- 外部能力未完成 10 选型时，只能定义能力端口和边界，不得确认具体 Provider。
- 09 只移交架构风险给 12，不重复定义正式 RISK。

### 10-外部能力选型与接入决策.md

旧文件路径可继续使用 `10-外部能力与集成治理.md`，但正文标题和职责必须使用“外部能力选型与接入决策”。

```markdown
### CAP-XXX：<能力名称>

关联 FLOW：
关联 MODULE：
关联 SCN：
关联 ARCH：
业务需要：
能力边界：
候选方案：
当前选型：
选择理由：
官方事实：
适用端与运行前提：
能力失败影响：
Capability Development-Entry Evidence Gate：
Capability Realization Requirement：
Capability Acceptance Requirement：
关联 TEST：
关联 RISK：
关联下游 TASK：
```

检查：

- CAP-ID 全局唯一
- CAP 选型状态与 CAP 真实就绪状态分开
- 官方 SoT 可追踪
- SDK/API/OpenAPI/MCP 版本明确
- 鉴权方式明确
- 权限、Scope、网络、额度、限流、计费、合规和目标端兼容性明确
- Capability Development-Entry Evidence Gate、Capability Realization Requirement 和 Capability Acceptance Requirement 明确
- 能力失败影响的 FLOW / SCN 可追踪
- 10 已确认不等于能力已接入、已真实验证或已上线
- 禁止用 Mock 替代生产真实能力验证

### 11-测试设计与验收用例.md

11 的正式格式见 `## 4.16 Test Design Format`。

规则：

- 11 定义业务逻辑测试顺序、测试依赖关系、测试前置业务事实、测试类型、自动化等级、真实环境要求和预期证明结果。
- 11 不定义测试命令、测试代码、fixture 脚本、测试执行调度、失败重试命令、实际执行状态、实际证据内容或测试通过/失败结果。
- P0 FLOW 必须覆盖正向流程、状态测试、API 测试、权限测试、旧流程测试和回归测试。
- 涉及外部能力时，必须包含真实环境能力测试。
- 涉及页面和交互时，必须包含 UI 行为或 UX 测试。
- API 合同、状态迁移、权限、范围、幂等、并发和旧流程隔离默认必须自动化。
- 真机、外部 Provider、视觉和复杂 UX 可标记为真实环境或人工验证，但不能省略业务与接口自动化。
- Planning 不得输出最终验收通过、测试已执行、测试通过或测试失败结论。

## 测试方案完整性门禁

生成 `11-测试方案与验收用例.md` 时必须检查：

- 每条 P0 FLOW 是否都有正向业务流程测试。
- 每条 P0 FLOW 是否都有前置阻断、状态、接口、权限、旧流程和回归测试。
- 涉及外部能力的 FLOW 是否有真实环境能力测试。
- 涉及页面和交互的 FLOW 是否有 UI 行为或 UX 测试。
- 每条 TEST 是否明确自动化等级。
- 11 中的测试顺序是否与 01 FLOW 顺序一致。
- 是否未记录实际测试结果、实际证据、测试命令或测试代码。

任一缺失时，`11` 不得视为完成。

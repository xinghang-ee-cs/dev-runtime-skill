# Capability Governance Layer

## 1. 目标

Capability Governance Layer 用于在 Planning 阶段识别、确认和治理外部能力、AI 能力、SDK、OpenAPI、MCP、基础设施和人工能力。

核心规则：

- 功能不等于本地代码。
- 功能由能力组合形成。
- 外部能力不得默认由 AI 本地伪实现。
- 外部能力不得凭经验、历史记忆、旧示例或非官方教程直接接入。
- 涉及真实外部调用的能力，必须先完成 Capability Development-Entry Evidence Gate，再生成开发任务。
- Development-Entry Evidence Gate 只验证官方事实、选型前提和可进入开发的条件，不要求 Adapter、真实调用、代码证据、真实设备验证或真实环境结果已经存在。

## 2. Capability 定义

Capability 不等于 Module。

Module 表示系统内的模块边界。

Capability 表示完成某项功能所依赖的能力来源。

功能组成：

```text
功能 =
内部能力
+ 外部 SaaS 能力
+ AI 能力
+ SDK 能力
+ MCP 能力
+ 平台生态能力
+ 基础设施能力
+ 人工能力
```

### 2.1 10 外部能力选型与接入决策边界

`10-外部能力选型与接入决策.md` 是外部能力的选型与接入决策合同。若项目保留旧文件路径 `10-外部能力与集成治理.md`，正文标题和职责必须使用“外部能力选型与接入决策”。

10 负责决定：

- 是否需要某项外部能力。
- 选什么 Provider 或能力来源。
- 为什么选。
- 能力边界、关键限制、官方事实、接入前提与开发前门槛。
- 未满足什么就不得进入开发或发布。

10 不负责：

- Adapter 文件位置。
- SDK 初始化代码。
- 具体调用代码。
- 环境配置命名或具体变量名。
- 接口字段实现。
- 数据库实现。
- 开发任务拆分。
- 实际接入过程。
- 实际测试结果。
- 上线结论。

依赖方向：

```text
09 先定义 CAPABILITY PORT / ARCHITECTURE REQUIREMENT / ADAPTER BOUNDARY
-> 10 再决定具体外部能力选型与接入前提
-> 11 设计验证该能力结论的测试
-> 13 才能生成满足门槛的开发任务
```

规则：

- 09 不得替 10 确认具体 Provider。
- 10 的选型改变、无法满足或要求改变 09 架构边界时，必须触发相关 ARCH 决策 review。
- 文档确认状态、CAP 选型状态和 CAP 真实就绪状态必须分开。
- 10 已确认不等于能力已接入、已真实验证或可上线。
- 页面可打开、JSSDK ready、Mock 成功、代码存在，不得视为真实能力成功。
- Capability Registry 只记录选型与前提事实；Capability Realization Requirement 与 Capability Acceptance Requirement 只能作为后续执行/验收需要证明的要求，不得让 10 写入 Adapter 代码、具体实现文件、实际接入结果或最终验收结论。

## 3. Capability 分类

| 类型 | 说明 | 是否触发 Development-Entry Evidence Gate |
| --- | --- | --- |
| Internal Capability | 项目内已有或可本地实现的能力 | 否，按常规规划治理 |
| External SaaS Capability | 第三方 SaaS 或开放平台能力 | 是 |
| AI Capability | 大模型、语音、OCR、Agent、视觉等 AI 服务 | 是 |
| SDK Capability | 官方或第三方 SDK 接入能力 | 是 |
| MCP Capability | MCP Server 暴露的工具或资源能力 | 是 |
| Platform Capability | 移动平台、企业协作平台、电商平台、CRM 平台等生态能力 | 是 |
| Infrastructure Capability | 对象存储、消息队列、推送、地图、支付、CDN 等基础设施能力 | 按外部依赖判断 |
| Human Capability | 人工审核、运营、客服、线下确认等人工能力 | 否，但必须定义介入边界 |

触发关键词示例：

- 地图
- 支付
- OCR
- AI
- 语音
- 推送
- 对象存储
- 第三方平台
- 短信
- 邮件
- 文件预览
- 电子签章
- 外部审批
- 移动平台开放能力
- 平台容器能力
- 企业协作平台开放能力
- 企业通信平台开放能力
- 电商平台开放能力
- CRM 平台开放能力
- 其他第三方平台能力

## 4. Capability Discovery

当识别到以下能力，但 Capability Registry 尚不存在时，允许执行 Capability Discovery：

- External Capability
- SDK Capability
- AI Capability
- MCP Capability
- OpenAPI Capability
- Infrastructure Capability
- Platform Capability

允许：

- 搜索官方文档
- 搜索官方 SDK
- 搜索 OpenAPI
- 搜索官方 GitHub
- 搜索官方控制台
- 搜索 MCP Server

生成 Capability Candidate：

```markdown
能力名称：
能力分类：
候选提供方：
候选官方来源：
发现时间：
发现方式：
CAP 选型状态：candidate
```

规则：

- Capability Discovery 不等于 Capability Confirmation。
- Discovery 结果只能作为候选信息。
- Discovery 完成后，必须进入 Capability Decision Card、Capability Registry 与 Capability Development-Entry Evidence Gate。

禁止：

- 生成开发任务。
- 编写生产代码。
- 写成已确认事实。

## 5. Capability ID 规范

格式：

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

规则：

- 全局唯一。
- 稳定引用。
- 不允许使用自然语言替代。
- 开发任务、测试范围条目、风险项必须引用相关 CAP-ID。

## 6. Capability Registry 模板

```markdown
能力ID：
能力名称：
能力分类：
能力提供方：
能力来源：
接入方式：
官方文档来源：
文档访问日期：
官方文档版本：
官方文档最后更新时间：
SDK名称：
SDK版本：
API版本：
OpenAPI：
MCP：
鉴权方式：
核心接口：
请求结构来源：
响应结构来源：
错误码来源：
额度限制：
限流策略：
计费规则：
环境配置要求：
回调要求：
网络要求：
最小能力确认要求：
最小能力确认结果：
失败降级策略：
人工介入策略：
SoT来源：
负责人：
CAP 选型状态：
```

环境配置要求只允许描述：

- 密钥 / Token / App 凭证类型。
- 权限或 Scope 前提。
- 网络、回调、域名、白名单、运行环境要求。
- 安全与保密约束。
- 是否需要配置项。

禁止记录：

- 实际环境变量名称。
- 配置文件路径。
- 代码读取方式。
- SDK 初始化代码。
- 部署命令。

10 正式状态模型：

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

旧治理材料中的“已验证”只能作为历史证据描述，不得替代 `real_environment_verified` 或 `release_ready`。

阶段限制：

- planning 阶段允许写入：`identified`、`candidate`、`confirmed`、`official_sot_verified`、`preconditions_ready`、`blocked`。
- planning 阶段禁止写入：`real_environment_verified`、`release_ready`。
- 只有后续真实执行与验收事实已经产生，并按其所属承接方完成验证后，才可能使用 `real_environment_verified` 或 `release_ready`。

## 7. 官方 SoT 优先级

官方来源优先级：

1. 官方文档
2. 官方 SDK
3. 官方 OpenAPI
4. 官方 GitHub
5. 官方控制台
6. 官方技术支持

禁止作为唯一 SoT：

- 博客
- AI 回答
- 历史经验
- StackOverflow
- 非官方教程
- 旧项目代码
- 过期示例

规则：

- 非官方资料只能作为线索，不得作为唯一事实来源。
- 官方文档必须记录访问日期、文档版本和官方文档最后更新时间；若官方未提供版本或更新时间，必须显式标注 `官方未提供`。
- SDK、API、OpenAPI、MCP 必须记录版本或确认无版本号。

## 8. Capability Development-Entry Evidence Gate

凡能力分类为 External Capability、SDK Capability、OpenAPI Capability、MCP Capability、AI Capability、Platform Capability 或等价外部真实能力时，必须完成：

- 官方 Provider / 官方文档来源已确认。
- SDK、API、OpenAPI、MCP 或 Provider 版本事实已确认。
- 适用端、运行环境与兼容性已确认。
- 鉴权模式、权限 / Scope、网络要求已确认。
- 额度、限流、计费、合规约束已确认。
- 请求、响应、错误与限制的官方合同已确认。
- 能力边界与不支持范围已确认。
- 失败影响和降级原则已确认。
- 架构承接边界已确认。
- 11 中的真实环境验证要求已设计。
- 12 中的关键 RISK / DEP / OPEN 已收口。
- 不存在阻断该 TASK 的关键 OPEN。

否则：

```text
禁止生成开发任务。
```

Development-Entry Evidence Gate 不得要求：

```text
实际 Adapter 已存在
实际 runtime binding 已存在
实际 SDK 调用已发生
代码证据已存在
真实设备验证已通过
真实 API 请求已完成
执行命令、操作步骤、响应截图或失败截图已存在
实际测试结果已产生
实际验收结论已产生
```

Development-Entry Evidence Gate 通过后，允许生成 13 TASK。

## 9. Capability Realization and Acceptance Requirements

Capability 不允许抽象存在。

平台环境正常不等于平台能力完成。

例如，OAuth、客户端识别、容器识别、页面打开或 SDK ready 只能证明环境或入口可用，不能证明平台 API、runtime adapter、录音、定位、摄像头、推送等真实能力已接入。

以下属于后续执行和验收要证明的事实，不得作为生成 TASK 前置：

- Adapter 已实现。
- runtime binding 已实现。
- SDK API 已真实调用。
- 权限处理已实现。
- fallback 已实现。
- 真实环境验证完成。
- 真实设备验证完成。
- 代码证据存在。
- 错误、超时、限流和降级行为已验证。
- CAP 已达到 `real_environment_verified` 或 `release_ready`。

planning-layer-runtime 可以定义：

- 这些事实未来需要被证明。
- 它们关联哪个 CAP / FLOW / TASK / TEST。
- 应满足什么验收标准。
- 需要何种真实环境要求。
- 应在 14、15 中预置哪些待填事实位置。

planning-layer-runtime 不得定义：

- 如何写 Adapter。
- Adapter 放在哪个文件。
- 如何初始化 SDK。
- 如何调用 SDK。
- 具体环境变量名。
- 测试命令。
- 测试数据。
- 测试调度。
- 证据保存目录。
- 实际回写机制。
- 其他 skill 如何执行或验收。

Capability Realization Requirement 可以记录：

- Adapter 需要实现什么能力。
- SDK API 需要真实调用什么官方能力。
- 权限处理需要覆盖什么 Scope 或授权前提。
- fallback 需要覆盖哪些能力失败路径。
- 错误、超时、限流和降级需要证明什么结果。

Capability Acceptance Requirement 可以记录：

- CAP-ID。
- FLOW / TASK / TEST。
- 真实环境要求。
- 真实设备要求。
- 预期证据类型。
- 14 Execution Fact Placeholder。
- 15 Acceptance Fact Placeholder。

## 10. Capability Realization Requirement

下列内容保留为后续实现与验收必须证明的要求，不得写为生成 TASK 前的 BLOCKER：

- adapter 存在。
- runtime binding 存在。
- sdk api 真实调用存在。
- permission binding 存在。
- fallback 存在。
- test binding 存在。
- acceptance binding 存在。
- code evidence 已存在。

这些要求只能进入：

```text
Capability Realization Requirement
Capability Acceptance Requirement
TASK Completion Contract
TEST Requirement
14 Execution Fact Placeholder
15 Acceptance Fact Placeholder
```

## 11. Capability Revalidation

以下条件触发 Capability Revalidation：

- SDK 升级
- API 升级
- OpenAPI 变更
- MCP 变更
- Provider 切换
- 官方文档重大更新

触发后，必须重新执行 Capability Development-Entry Evidence Gate，并重新确认：

- SDK 版本
- API 版本
- 鉴权
- 请求结构
- 响应结构
- 错误码
- 额度、限流、计费、合规和能力边界
- 11 的真实环境验证要求
- 12 的 RISK / DEP / OPEN 收口

规则：

- Revalidation 完成前，不得将能力状态标记为 `real_environment_verified` 或 `release_ready`。
- Revalidation 未完成时，相关开发任务不得以旧能力确认结果作为通过依据。

## 12. Capability Code Evidence Requirement

Capability 声称达到 `real_environment_verified` 或 `release_ready` 时，后续执行与验收事实必须证明：

- adapter 实现
- runtime binding
- sdk import
- capability api usage
- permission handling
- fallback handling
- test evidence

planning 阶段只能把这些写成：

```text
Capability Realization Requirement
Capability Acceptance Requirement
TASK Completion Contract
TEST Requirement
14 Execution Fact Placeholder
15 Acceptance Fact Placeholder
```

示例：

```ts
type PlatformCapabilityName =
  | "deviceInfo"
```

上述代码只证明某个平台能力名称被类型声明覆盖，不证明真实设备定位、录音或其他运行时能力已经完成。

若目标平台 API、对应 adapter、runtime binding 和真实调用证据尚未产生，planning 阶段只能标记为：

```text
待后续实现与验收证明
```

## 13. AI 禁止规则

AI 禁止：

- 凭经验写 SDK。
- 猜测 API。
- 猜测鉴权。
- 猜测返回结构。
- 使用历史记忆直接实现。
- 使用旧版本示例直接开发。
- 使用博客作为唯一 SoT。
- Mock 真实生产逻辑。
- 在未确认官方能力前进入开发。
- 用可编译代码替代真实外部能力验证。
- 用平台环境验证替代平台能力绑定。
- 用 OAuth、UA、容器识别、页面打开或 JSSDK ready 替代 JSAPI、adapter、permission、fallback 和真实设备验证。

Mock 允许范围：

- 仅用于 UI 原型、离线演示或测试替身。
- 必须标注 `非生产真实能力`。
- 必须指向真实 Capability Registry。
- 不得作为验收通过依据。

## 14. Capability Development-Entry Gate

| 条件 | 风险等级 |
| --- | --- |
| 外部能力未登记 | BLOCKER |
| SDK 或 API 版本不明确 | BLOCKER |
| 鉴权方式不明确 | BLOCKER |
| 请求或响应结构未确认 | BLOCKER |
| 官方 SoT 不存在 | BLOCKER |
| 架构承接边界未确认 | BLOCKER |
| 11 未设计真实环境验证要求 | BLOCKER |
| 12 未收口关键 RISK / DEP / OPEN | BLOCKER |
| 存在阻断该 TASK 的关键 OPEN | BLOCKER |
| 额度、限流、计费未确认 | HIGH |
| 降级策略未定义 | HIGH |
| 人工介入边界未定义 | MEDIUM |

BLOCKER 未解除前：

- 不得生成开发任务。
- 不得进入代码实现。
- 不得写成已确认事实。

下列内容不是生成 TASK 前的 BLOCKER，只能作为后续实现与验收要求：

- adapter 不存在。
- runtime binding 不存在。
- sdk api 未真实调用。
- permission binding 不存在。
- fallback 不存在。
- test binding 不存在。
- acceptance binding 不存在。
- code evidence 尚未产生。
- 真实设备验证尚未完成。
- 真实环境验证尚未完成。

## 15. 文档装配规则

不要固定生成全量文档。

先识别需求特征，再装配必要文档。

下表文件名是当前建议命名，不是跨 skill handoff 的稳定协议。跨 skill handoff 必须传递职责名与实际路径。

| 需求特征 | 必须加载文档 |
| --- | --- |
| UI、页面、交互 | `05-前端页面与UI交互设计.md` |
| External Capability、SDK、OpenAPI、MCP、AI Provider | `10-外部能力选型与接入决策.md`（可兼容旧路径 `10-外部能力与集成治理.md`） |
| Permission、角色、数据可见性、越权 | `08-权限与异常边界说明.md` |
| 数据模型、状态机、兼容迁移 | `06-数据模型与状态流转.md` |
| 接口、前后端契约、错误码 | `07-接口设计与前后端契约.md` |
| 架构边界、复用策略、关键决策 | `09-架构设计与关键决策.md` |
| AI Agent | Agent 治理文档，若项目未建立则先登记为待建 SoT |

规则：

- L 级跨模块变更仍可完整走 00-13，并在 13 确认后自动派生 14、15。
- S/M 级变更只加载必要文档。
- 未触发的文档不强制生成。
- 文档装配结论必须写入 `涉及文档`。
- handoff 给后续承接方时必须输出 `handoff_role -> actual_path`，禁止下游按编号猜测。
- 只要本期需要生成 13 TASK，就必须同时装配并确认 11、12，以及 TASK 引用的全部上游 SoT。
- 15 不得作为可独立装配的孤立文档；只能由已确认的 13 连同 14 一起自动派生。
- `assembled_documents` 与 `handoff_role_mapping` 只能包含实际已生成的文档和角色，不得为了“看起来完整”伪造路径或角色。

handoff 角色：

```text
Capability Governance
Test and Acceptance Plan
Risk, Dependency, and Open Questions
Development Landing Checklist
Execution and Integration Record
Acceptance and Retrospective Record
```

## 16. 任务拆分规则

凡涉及外部能力的开发任务，必须引用：

- CAP-ID
- 官方文档
- SDK 版本
- API 版本
- Capability Development-Entry Evidence Gate
- 降级策略

否则：

```text
不得进入执行。
```

能力相关任务进入 13 前还必须满足：

- 相关 CAP 已完成 10 的选型确认和 Capability Development-Entry Evidence Gate。
- 相关 RISK / DEP / OPEN 已进入 12，且阻断该任务的 OPEN 已关闭。
- 11 已定义验证该能力结论的 TEST，且 12 已定义相关风险、依赖或待决策事项。
- 任务引用的 FLOW / STATE / API / PERM / ARCH / CAP / TEST 均已装配且确认。
- 任务必须按 13 的 Task Contract Format 生成，不得以能力待办、环境适配或平台兼容性描述替代。
- 候选文件路径、adapter 名称或 SDK 线索不得写成已确认实现事实。
- 实际 Adapter、真实 SDK 调用、代码证据、真机结果和真实环境结果不得作为生成 TASK 的前置。

任务格式补充：

```markdown
关联能力：
官方 SoT：
SDK版本：
API版本：
Capability Development-Entry Evidence Gate：
Capability Realization Requirement：
Capability Acceptance Requirement：
降级策略：
```

涉及 Platform Capability 时，必须拆分：

- Capability Realization Requirement
- Capability Acceptance Requirement
- TASK Completion Contract
- TEST Requirement
- 14 Execution Fact Placeholder
- 15 Acceptance Fact Placeholder

禁止使用以下模糊任务替代真实 Capability：

- 移动端可用性
- 平台兼容性
- 环境适配

错误示例：

```text
移动端兼容性优化
```

正确示例：

```text
TASK-PLATFORM-CAPABILITY-REALIZATION-CONTRACT
TASK-PLATFORM-LOCATION-REQUIREMENT
TASK-PLATFORM-RECORDING-REQUIREMENT
TASK-PLATFORM-PERMISSION-REQUIREMENT
TASK-PLATFORM-FALLBACK-REQUIREMENT
```

真实设备验证不得作为开发实现任务；应进入 `11-测试方案与验收用例.md` 的测试范围条目，并由后续测试与验收承接方承接。

## 17. Capability Acceptance Scope 规则

外部能力验收范围必须覆盖：

- SDK 初始化证明要求
- 鉴权结果证明要求
- 最小真实调用证明要求
- 错误码处理证明要求
- 超时处理证明要求
- 限流处理证明要求
- 日志追踪证明要求
- 降级策略证明要求
- 网络失败恢复证明要求
- adapter binding 证明要求
- runtime binding 证明要求
- sdk api 调用证明要求
- permission binding 证明要求
- fallback 证明要求
- 14 Execution Fact Placeholder
- 15 Acceptance Fact Placeholder

涉及 Capability 的 P0 测试范围必须生成结构化测试范围条目，并绑定：

- CAP-ID
- Capability Realization Requirement
- Capability Acceptance Requirement
- real device required
- TEST Requirement

Capability Acceptance Matrix 不能替代结构化测试范围条目。
结构化测试范围条目也不能替代 Capability Acceptance Matrix。
二者必须同时存在。

禁止：

- 仅验证代码可编译。
- 仅验证 Mock 成功。
- 仅验证 UI 有按钮或页面。
- 使用“平台环境验证通过”替代 capability-level acceptance。

平台能力必须拆分验收范围：

- OAuth 对象
- JSSDK ready 对象
- 定位 JSAPI 对象
- 录音 API 对象
- 权限对象
- fallback 对象
- 真实设备要求

Capability Acceptance Matrix：

```markdown
Capability：
Acceptance Item：
Capability Realization Requirement：
SDK API Requirement：
Permission Requirement：
Fallback Requirement：
Real Device Required：
Acceptance Scope：
```

## 18. 文档职责边界

`10-外部能力选型与接入决策.md` 负责：

- 是否需要某项外部能力。
- CAP-ID。
- 能力服务的 FLOW / MODULE / SCN。
- 候选能力来源。
- 最终选型或候选状态。
- 选型理由。
- 官方事实来源。
- SDK / API / Provider 版本事实。
- 适用端与运行环境要求。
- 鉴权、权限、Scope、网络、额度、限流、计费、合规约束。
- 能力边界与不支持范围。
- 能力不可用时影响哪些业务路径。
- 进入开发前的 Capability Development-Entry Evidence Gate。
- 进入发布前的真实能力验证要求。
- 关联 ARCH / TEST / RISK。

`10` 可引用 Capability Registry、Capability Realization Requirement、Capability Acceptance Requirement、TASK Completion Contract、TEST Requirement、14 Execution Fact Placeholder 或 15 Acceptance Fact Placeholder 作为后续证明要求，但这些不能把 `10` 变成 SDK 实施文档、测试执行日志或上线验收记录。

禁止定义：

- UI 设计
- 数据模型
- 权限矩阵
- 数据库实现
- 页面逻辑
- 业务流程
- Adapter 文件位置
- SDK 初始化代码
- 具体调用代码
- 环境变量命名或具体变量名
- 配置文件路径
- 代码读取方式
- 部署命令
- 接口字段实现
- 开发任务拆分
- 实际接入过程
- 实际测试结果
- 上线结论

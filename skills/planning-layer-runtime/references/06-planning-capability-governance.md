# Capability Governance Layer

## 1. 目标

Capability Governance Layer 用于在 Planning 阶段识别、确认和治理外部能力、AI 能力、SDK、OpenAPI、MCP、基础设施和人工能力。

核心规则：

- 功能不等于本地代码。
- 功能由能力组合形成。
- 外部能力不得默认由 AI 本地伪实现。
- 外部能力不得凭经验、历史记忆、旧示例或非官方教程直接接入。
- 涉及真实外部调用的能力，必须先完成 Evidence Gate，再生成开发任务。

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

## 3. Capability 分类

| 类型 | 说明 | 是否触发 Evidence Gate |
| --- | --- | --- |
| Internal Capability | 项目内已有或可本地实现的能力 | 否，按常规规划治理 |
| External SaaS Capability | 第三方 SaaS 或开放平台能力 | 是 |
| AI Capability | 大模型、语音、OCR、Agent、视觉等 AI 服务 | 是 |
| SDK Capability | 官方或第三方 SDK 接入能力 | 是 |
| MCP Capability | MCP Server 暴露的工具或资源能力 | 是 |
| Platform Capability | 微信开放平台、微信小程序、飞书开放平台、企业微信、Shopify、Salesforce、钉钉开放平台等平台生态能力 | 是 |
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
- 微信开放平台
- 微信小程序
- 飞书开放平台
- 企业微信
- Shopify
- Salesforce
- 钉钉开放平台

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
确认状态：待确认
```

规则：

- Capability Discovery 不等于 Capability Confirmation。
- Discovery 结果只能作为候选信息。
- Discovery 完成后，必须进入 Capability Registry 与 Evidence Gate。

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
环境变量：
回调要求：
网络要求：
最小能力确认要求：
最小能力确认结果：
失败降级策略：
人工介入策略：
SoT来源：
负责人：
确认状态：
```

确认状态：

```text
未识别
待确认
已确认
已验证
阻塞
废弃
```

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

## 8. External Capability Evidence Gate

凡能力分类为 External Capability、SDK Capability、OpenAPI Capability、MCP Capability、AI Capability、Platform Capability 或等价外部真实能力时，必须完成：

- 官方文档确认
- SDK 确认
- 版本确认
- 鉴权确认
- 请求结构确认
- 响应结构确认
- 错误码确认
- 额度、限流、计费确认
- 最小真实调用验证

否则：

```text
禁止生成开发任务。
```

最小真实调用验证必须说明：

```markdown
验证环境：
验证命令或操作：
请求样例来源：
响应证据：
失败证据：
验证结论：
验证日期：
```

## 9. Capability Binding

Capability 不允许抽象存在。

平台环境正常不等于平台能力完成。

例如，OAuth、UA 识别、容器识别、页面打开、JSSDK ready 只能证明环境或入口可用，不能证明平台 JSAPI、runtime adapter、RecorderManager、定位、摄像头、推送等真实能力已接入。

每个 Capability 必须绑定：

- runtime
- adapter
- sdk api
- permission
- fallback
- test
- acceptance
- code evidence

否则 Capability 不得标记为：

- 已完成
- 已验证

Capability Binding Matrix：

```yaml
CAP-XXX-001:
  runtime:
    - xxx-runtime
  adapter:
    - xxx-adapter.ts
  sdk_api:
    - sdk.api
  permission:
    - location
    - microphone
  validation:
    - sdk-ready
    - permission-granted
    - real-device-success
  acceptance:
    - TEST-XXX-001
  fallback:
    - browser-fallback
  code_evidence:
    - import sdk
    - adapter implementation
    - runtime binding
    - api invocation
```

Platform Capability 必须定义：

- runtime adapter
- platform adapter
- sdk binding
- permission binding

禁止仅验证以下内容就判定平台能力完成：

- OAuth
- UA
- 容器识别
- 页面打开
- JSSDK ready

## 10. Capability Binding Gate

必须验证：

- adapter 存在
- runtime binding 存在
- sdk api 真实调用存在
- permission binding 存在
- fallback 存在
- test binding 存在
- acceptance binding 存在

任一缺失：

```text
BLOCKER
```

## 11. Capability Revalidation

以下条件触发 Capability Revalidation：

- SDK 升级
- API 升级
- OpenAPI 变更
- MCP 变更
- Provider 切换
- 官方文档重大更新

触发后，必须重新执行 Evidence Gate，并重新确认：

- SDK 版本
- API 版本
- 鉴权
- 请求结构
- 响应结构
- 错误码
- 最小真实调用验证

规则：

- Revalidation 完成前，不得将能力状态标记为 `已验证`。
- Revalidation 未完成时，相关开发任务不得以旧能力确认结果作为通过依据。

## 12. Code Evidence Gate

Capability 声称已完成时，必须存在：

- adapter 实现
- runtime binding
- sdk import
- capability api usage
- permission handling
- fallback handling
- test evidence

否则不得：

- 关闭 P0
- 标记 capability 为已验证
- 输出“功能完成”
- 进入验收通过

代码自检阶段必须验证：

- capability api 是否真实存在
- adapter 是否真实实现
- sdk api 是否真实调用
- fallback 是否真实实现

示例：

```ts
type FeishuJsApiName =
  | "getSystemInfo"
```

上述代码只证明 `getSystemInfo` 被类型声明覆盖，不证明飞书定位能力或飞书录音能力完成。

若未发现定位 JSAPI、RecorderManager、对应 adapter、runtime binding 和真实调用证据，必须判定：

```text
BLOCKER
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

## 14. Runtime Gate

| 条件 | 风险等级 |
| --- | --- |
| 外部能力未登记 | BLOCKER |
| SDK 或 API 版本不明确 | BLOCKER |
| 鉴权方式不明确 | BLOCKER |
| 请求或响应结构未确认 | BLOCKER |
| 官方 SoT 不存在 | BLOCKER |
| 最小真实调用未验证 | BLOCKER |
| Capability 未完成 Binding | BLOCKER |
| Capability Binding Gate 未通过 | BLOCKER |
| adapter 不存在 | BLOCKER |
| runtime binding 不存在 | BLOCKER |
| sdk api 未真实调用 | BLOCKER |
| permission binding 不存在 | BLOCKER |
| Code Evidence Gate 未通过 | BLOCKER |
| 额度、限流、计费未确认 | HIGH |
| 降级策略未定义 | HIGH |
| fallback 不存在 | HIGH |
| acceptance 未拆分 | HIGH |
| 人工介入边界未定义 | MEDIUM |

BLOCKER 未解除前：

- 不得生成开发任务。
- 不得进入代码实现。
- 不得写成已确认事实。

## 15. 文档装配规则

不要固定生成全量文档。

先识别需求特征，再装配必要文档。

下表文件名是当前建议命名，不是跨 skill handoff 的稳定协议。跨 skill handoff 必须传递职责名与实际路径。

| 需求特征 | 必须加载文档 |
| --- | --- |
| UI、页面、交互 | `05-前端页面与UI交互设计.md` |
| External Capability、SDK、OpenAPI、MCP、AI Provider | `10-外部能力与集成治理.md` |
| Permission、角色、数据可见性、越权 | `08-权限与异常边界说明.md` |
| 数据模型、状态机、兼容迁移 | `06-数据模型与状态流转.md` |
| 接口、前后端契约、错误码 | `07-接口设计与前后端契约.md` |
| 架构边界、复用策略、关键决策 | `09-架构设计与关键决策.md` |
| AI Agent | Agent 治理文档，若项目未建立则先登记为待建 SoT |

规则：

- L 级跨模块变更仍可完整走 00-15。
- S/M 级变更只加载必要文档。
- 未触发的文档不强制生成。
- 文档装配结论必须写入 `涉及文档`。
- handoff 给执行 skill 时必须输出 `handoff_role -> actual_path`，禁止下游按编号猜测。

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
- 最小能力确认要求
- 降级策略

否则：

```text
不得进入执行。
```

任务格式补充：

```markdown
关联能力：
官方 SoT：
SDK版本：
API版本：
Evidence Gate：
最小能力确认要求：
降级策略：
Runtime Gate：
```

涉及 Platform Capability 时，必须拆分：

- runtime adapter
- platform adapter
- sdk binding
- permission handling
- fallback
- capability acceptance

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
TASK-FEISHU-JSSDK-READY
TASK-FEISHU-LOCATION-ADAPTER
TASK-FEISHU-RECORDER-ADAPTER
TASK-FEISHU-PERMISSION-BINDING
TASK-FEISHU-FALLBACK
```

真实设备验证不得作为 long 开发任务；应进入 `11-测试方案与验收用例.md` 的测试范围条目，并由 testing-layer-runtime 接管。

## 17. Capability Acceptance Scope 规则

外部能力验收范围必须覆盖：

- SDK 初始化对象
- 鉴权结果对象
- 最小真实调用对象
- 错误码处理对象
- 超时处理对象
- 限流处理对象
- 日志追踪对象
- 降级策略对象
- 网络失败恢复对象
- adapter binding 对象
- runtime binding 对象
- sdk api 调用对象
- permission binding 对象
- fallback 对象
- testing handoff 对象
- acceptance 对象

涉及 Capability 的 P0 测试范围必须生成结构化测试范围条目，并绑定：

- CAP-ID
- runtime
- adapter
- sdk api
- permission
- fallback
- real device required
- acceptance

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
- RecorderManager 对象
- 权限对象
- fallback 对象
- 真实设备要求

Capability Acceptance Matrix：

```markdown
Capability：
Acceptance Item：
Runtime：
Adapter：
SDK API：
Permission：
Fallback：
Real Device Required：
Acceptance Scope：
```

## 18. 文档职责边界

`10-外部能力与集成治理.md` 负责：

- 外部能力来源
- SDK 治理
- OpenAPI 治理
- MCP 治理
- 官方 SoT 治理
- Capability Registry
- Capability Binding Matrix
- Capability Binding Gate
- Code Evidence Gate
- Capability Acceptance Matrix
- 外部能力接入限制
- 降级策略
- Mock 治理
- 真实能力验证
- Runtime Gate

禁止定义：

- UI 设计
- 数据模型
- 权限矩阵
- 数据库实现
- 页面逻辑
- 业务流程

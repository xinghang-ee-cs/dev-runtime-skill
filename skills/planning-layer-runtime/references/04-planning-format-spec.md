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
DOMAIN-xxx
MODULE-xxx
CAP-xxx
PAGE-xxx
STATE-xxx
API-xxx
PERM-xxx
TASK-xxx
RISK-xxx
TEST-xxx
```

规则：

- 全局唯一
- 稳定
- 不允许同义重复
- 不允许自然语言替代

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

风险格式：

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

### 05-前端页面与UI交互设计.md

```markdown
## 设计来源

Figma：
设计版本：
设计负责人：

## 页面状态

未开始
设计中
待确认
开发中
已验收

## 交互确认状态

是否完成交互确认：
是否完成异常态确认：
是否完成空状态确认：
是否完成加载态确认：
```

检查：

- UI进入SoT链路
- 设计来源可追踪
- 页面状态显式

### 06-数据模型与状态流转.md

```markdown
## 测试数据治理

是否存在测试数据：

测试数据隔离策略：
- 同库隔离
- 同表隔离
- 独立库
- 独立环境

测试数据标识：

生产数据泄露防护：
- API隔离
- 权限隔离
- 导出隔离
- 审计隔离

## 历史模型兼容分析

涉及实体：

是否复用已有模型：

新增字段：

废弃字段：

迁移方案：

兼容策略：

数据归属：
```

检查：

- 不固定测试数据实现方案
- 兼容SaaS多租户
- 避免重复模型
- 保持领域边界稳定
- 禁止生成数据库迁移代码

### 08-权限与异常边界说明.md

```markdown
## 数据可见性边界

角色：
可访问业务域：
可见数据范围：
测试数据权限：
导出权限：
越权处理：
```

检查：

- 测试数据也是权限
- 权限可追踪
- 数据可见性结构化

### 09-架构设计与关键决策.md

```markdown
## 数据治理决策

是否新增实体：

是否复用已有实体：

是否违反领域边界：

是否产生重复模型：

是否影响历史数据：
```

### 10-外部能力与集成治理.md

Capability Registry 使用 `06-planning-capability-governance.md#6-Capability-Registry-模板`。

检查：

- CAP-ID 全局唯一
- 官方 SoT 可追踪
- SDK/API/OpenAPI/MCP 版本明确
- 鉴权方式明确
- 请求、响应、错误码来源明确
- 最小真实调用验证有证据
- Capability Binding Matrix 可追踪
- Code Evidence Gate 可追踪
- Capability Acceptance Matrix 可追踪
- Runtime Binding 可追踪
- Adapter Binding 可追踪
- SDK API Binding 可追踪
- Permission Binding 可追踪
- Fallback Binding 可追踪
- 降级策略和人工介入边界明确
- 禁止用 Mock 替代生产真实能力验证

## 14. 测试范围格式规范

`11-测试方案与验收用例.md` 只定义测试范围，不定义测试执行生命周期。

测试范围统一字段规范：

```markdown
测试范围ID：
测试域：
验收对象：
关联需求：
关联 Capability：
Priority：
业务断言：
范围内：
范围外：
错误/超时/限流/降级覆盖对象：
```

禁止字段：

```text
验证方式
执行人
测试顺序
执行状态
测试结果
自动化/人工边界
证据采集过程
```

## 15. 结构化测试范围条目格式规范

每个 P0 验收项不得只写测试点，必须使用结构化测试范围条目。

最小字段：

测试范围ID：
关联需求：
关联 Capability：
关联接口：
关联风险：
Priority：
验收对象：
测试目标：
范围内：
范围外：
断言点：

规则：

- P0 测试范围条目必须覆盖主流程、异常流程、权限边界、数据归属、状态流、历史兼容和外部能力验收对象。
- 涉及外部能力时，必须标明能力验收对象和需要覆盖的错误码、超时、限流、降级场景。
- Planning 不得输出最终验收通过、测试已执行、测试通过或测试失败结论。
- 禁止只写“验证项、验证方式、预期结果”作为完整测试范围条目。
- 禁止在 planning 中定义前置条件、测试数据、操作步骤、自动化验证方式、人工验证方式、证据要求、执行顺序、执行状态或测试结果。

## 测试方案完整性门禁

生成 `11-测试方案与验收用例.md` 时必须检查：

- 是否只定义测什么。
- 是否包含测试域总览。
- 是否每个 P0 验收项都有结构化测试范围条目。
- 是否包含关联需求、关联 Capability、Priority、验收对象、业务断言、范围内、范围外。
- 是否包含 Capability-level Acceptance Matrix。
- 是否未定义怎么测、谁来测、测试顺序、执行状态、测试结果、自动化/人工边界、证据采集过程。

任一缺失时，`11` 不得视为完成。

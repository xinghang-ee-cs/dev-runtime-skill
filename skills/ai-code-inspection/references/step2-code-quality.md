# Step 2: 代码质量

本 Step 用于发现常见实现错误和日常质量问题。检查应务实，不等同于严格 release gate。

## 通用检查

- 检查范围内未使用的 import、变量、死分支和过期 TODO。
- 已有共享类型或契约时，不要重复定义局部契约。
- 函数职责应清晰，不要把多种职责混在一个大函数中。
- 不要静默吞掉请求、外部能力、数据访问、文件系统或持久化失败。
- 已有窄类型、schema 或公共契约时，不要无依据地放宽数据 shape。
- 异步 loading/error 或等价状态在成功和失败路径都应完整复位。
- 对可能为 `null` / `undefined` / 空数组的数据，先做保护再访问集合方法或深层属性。
- 校验和 normalization 应靠近输入边界。

在 `standards_compliance_correction` 中，只有同时满足以下条件时才允许移除检查到的项目：

- 归类为 `safe_standard_correction`。
- 位于明确 `editable_scope`。
- 用户已经确认具体 `issue_id` 或批次。
- 能证明不会改变行为。
- 能通过静态检查、构建或测试验证。

## 组件边界检查

按当前范围涉及的组件和项目既有结构执行：

- 用户界面或页面单元不应绕过项目已有请求封装、共享客户端或状态边界。
- 共享状态已有明确承载位置时，不要在无关单元重复维护同一状态。
- 外部响应进入内部状态前应完成必要的 normalization 和 shape check。
- 默认值或 fallback 如会改变业务流，必须有明确依据；不合理但依据不足时只报告。
- 路由或入口处理器、请求传输边界、应用服务/use case、数据访问边界和外部能力 adapter 只有在项目真实存在时才检查职责；不得强制新增特定分层。
- 输入校验应使用项目已有的 schema、类型或声明，错误语义应与现有公共契约一致。
- 除非项目既有契约如此，不要把持久化或 generated shape 直接泄漏到公共响应。
- test double 尽量复用生产契约，避免局部测试通过但 build、typecheck 或契约验证失败。

## 持久化检查

当环境档案声明的 schema、migration、mapping 或持久化字段发生变化时执行：

- 持久化字段、mapping、公共契约、调用端数据 shape、契约文档和测试应保持一致。
- 如果任一 `persistence.schema_paths` 或 `migration_paths` 中的文件发生变化，最终报告必须记录数据库迁移状态：
  - `created_only`：migration 文件存在，但未验证或未应用。
  - `validated`：schema validation 通过，但 runtime DB 应用未确认。
  - `applied`：开发者明确确认目标数据库后，migration 已应用。
  - `not_confirmed`：runtime 数据库状态未检查。
- 除非开发者明确确认目标数据库和命令，否则不得执行 migration 命令。
- build/test/schema validation 通过，不代表当前 runtime 数据库已经应用对应字段或枚举变化。

## 规范矫正安全边界

本 Step 的问题统一使用 `../SKILL.md` 定义的六种分类；原有质量检查项继续执行，但“应移除/应调整”不等于规范矫正自动获得修改权限。

### 可安全矫正

仅将下列问题归为 `safe_standard_correction`：

- 当前改动产生的未使用 import。
- 当前改动中可被编译器明确证明未使用的局部变量。
- 明确类型错误或明确错误字段引用。
- 明确漏掉的空值保护，且不会改变合法输入行为。
- async loading/error 状态明确无法复位。
- 与既有公共契约明确冲突的局部重复类型。
- 当前新增、明确不可达且无动态调用可能的死分支。

以上项目仍必须同时满足 `../SKILL.md` 的全局无行为、无语义、无实现路径变化条件；空值保护或状态复位如会改变外部结果、错误语义或业务流程，应改归 `confirmed_bug` 或 `incremental_design_required`。

### 只能报告或路由

- 历史死代码、过期 TODO、无法证明无调用的代码、错误处理不统一或可能不合理的默认值/fallback：归为 `report_only_risk`。
- 有明确运行错误、失败测试、契约冲突或可证明错误行为：归为 `confirmed_bug`，只在 `confirmed_bugfix` 处理。
- 业务判断、异常语义、默认值或 fallback 需要补充规则：归为 `incremental_design_required`。
- 大函数、多职责函数、重复业务逻辑、共享状态位置不合理，或为“更优雅”而拆分/重写实现：归为 `refactor_assessment_required`。
- 涉及权限、数据库执行、生产、安全策略或 Breaking API：归为 `blocked_out_of_boundary`。

历史 TODO 和历史死代码只报告，不自动删除；无法证明无调用的代码只报告。禁止以职责过多、函数过大、代码重复、重复定义或错误处理不统一为理由重构实现、改变公共契约或改变异常语义。

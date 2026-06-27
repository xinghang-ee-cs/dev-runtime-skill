# Step 2: 代码质量

本 Step 用于发现常见实现错误和日常质量问题。检查应务实，不等同于严格 release gate。

## 通用检查

- 移除范围内未使用的 import、变量、死分支和过期 TODO。
- 已有共享 type/contract 时，不要重复定义局部契约。
- 函数职责应清晰，不要把多种职责混在一个大函数中。
- 不要静默吞掉 API、SDK、repository、filesystem 或 database 失败。
- 已有 union/interface/DTO 时，不要把窄契约放宽成普通 `string`、`any` 或无类型 object。
- async loading/error 状态在成功和失败路径都应复位。
- 对可能为 `null` / `undefined` / 空数组的数据，先做保护再访问集合方法或深层属性。
- 校验和 normalization 应靠近输入边界。

## Frontend 检查

当 frontend 文件在范围内时执行：

- page/component 不应绕过已有 API wrapper 或共享 client utility。
- 已有 store/composable/module 承接共享状态时，不要在无关 view 中重复维护状态。
- API response 进入 UI state 前应完成 unwrap 和 shape check。
- UI fallback 行为如果改变业务流，应在代码中明确表达。
- test mock 尽量使用导出的生产类型，避免 unit test 通过但 typecheck/build 失败。
- 只有环境档声明 frontend framework 为 `Vue` 时，才执行 Vue 相关检查。

## Backend 检查

当 backend 文件在范围内时执行：

- controller 只处理 transport：route、params、query、body、auth decorator/guard。
- service 负责业务编排，调用 repository/provider，不重复 data access 细节。
- DTO 负责 request shape 校验；当应用使用 strict validation pipe 时，应拒绝不支持字段。
- repository/provider 负责 data access、mapping 和外部 IO 边界。
- invalid ID、missing record、unauthorized access 和 unsupported operation 应一致使用 Nest exception 或 domain error。
- 除非项目既有契约如此，不要把 ORM/generated persistence shape 泄漏到 public API response。

## Prisma 与数据库检查

当 Prisma schema、migration、repository mapping 或持久化字段发生变化时执行：

- schema field、repository mapping、DTO/domain type、frontend type、OpenAPI/docs 和 test 应保持一致。
- 如果 `backend/prisma/schema.prisma` 或 `backend/prisma/migrations/` 发生变化，最终报告必须记录数据库迁移状态：
  - `created_only`：migration 文件存在，但未验证或未应用。
  - `validated`：schema validation 通过，但 runtime DB 应用未确认。
  - `applied`：开发者明确确认目标数据库后，migration 已应用。
  - `not_confirmed`：runtime 数据库状态未检查。
- 除非开发者明确确认目标数据库和命令，否则不得执行 migration 命令。
- build/test/schema validation 通过，不代表当前 runtime 数据库已经存在新增 column 或 enum。

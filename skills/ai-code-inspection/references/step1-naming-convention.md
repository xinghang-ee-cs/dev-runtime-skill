# Step 1: 命名与放置

本 Step 检查文件名、符号名、路由名、DTO/type 名、模块放置和术语一致性。

## 输入

- `../project-environment-profile.md`
- 已声明的检查边界。
- 变更文件或范围内文件。
- 所属目录中相邻的现有文件。

## 通用检查

- 遵循所属目录已有命名风格。
- 优先使用当前代码库中的清晰领域名词和动词，避免 `helper`、`common2`、`newService`、`dataUtil`、`temp` 等模糊名称。
- 前端和后端同时变更时，契约术语必须一致。
- 测试文件名应与被测文件或被测行为对应。
- 已有模块或目录能承接该职责时，不要新增顶层目录。
- 除非是明确的 adapter/infrastructure 类型，否则不要把实现技术名泄漏进领域类型。

## Frontend 检查

当 frontend 文件在范围内时执行：

- Vue component 应遵循本项目组件命名风格，通常为 `PascalCase.vue`。
- route/page/view 文件应保留在现有路由或视图结构下。
- API wrapper 文件应使用 resource/domain 名称，并对 page/component 隐藏 HTTP client 细节。
- 共享类型应放在已有 frontend type 或 API type 目录中；只有真正局部使用时才放在单个 view 内。
- 框架相关代码应放在项目已有分层中，例如 component、view、composable、router、platform 等。

## Backend 检查

当 backend 文件在范围内时执行：

- NestJS module 应保持常规命名，例如 `*.module.ts`、`*.controller.ts`、`*.service.ts`、DTO、provider、repository 和 test。
- controller、service、DTO、repository、adapter 应放在所属 module 或已有 shared infrastructure 目录中。
- DTO 和 request/response type 名称应描述传输契约，不应混入 UI 细节。
- repository 或 data-source 名称必须真实反映实现类型。
- route root 应符合现有 resource 命名风格。

## 数据与持久化检查

当 schema、repository、migration、entity/model 或 generated type 使用发生变化时执行：

- Prisma model 和 field 应遵循现有 schema 命名和 mapping 风格。
- 数据库 table/column 名称应遵循现有 migration/schema 风格。
- enum-like 值在 frontend type、backend DTO/domain type、Prisma schema、OpenAPI/docs 和 test 中应保持一致。

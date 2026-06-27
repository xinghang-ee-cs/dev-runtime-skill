# Step 3: 架构与分层

本 Step 检查变更代码是否留在正确的架构层。

## 通用检查

- 判断架构前先确认真实调用路径，例如 route/view -> API/store/composable -> backend controller/service/repository/provider。
- transport、业务编排、data access、外部能力 adapter 应保持分离。
- 已有公开边界时，不要新增跨层 import。
- 修复局部问题时，不要顺手移动无关职责。
- 优先沿用项目既有模式，而不是创造新抽象。
- 只有在能消除真实重复或隔离真实边界时，才新增抽象。

## Frontend 分层检查

当 frontend 文件在范围内时执行：

- route/page/view 文件负责 workflow 协调和页面组合。
- component 负责可复用 UI，并通过清晰 props/events 或本项目等价约定交互。
- composable/store/module 负责可复用状态或 workflow 逻辑。
- API module 负责 HTTP 细节和 response normalization。
- 如果项目已有 platform/SDK/browser adapter 边界，普通 UI 文件不应直接承接这些能力。
- 框架相关检查由 `project-environment-profile.md` 决定。

## Backend 分层检查

当 backend 文件在范围内时执行：

- NestJS `main.ts` / app module 负责 bootstrap 和全局配置。
- module 应明确声明所有权和依赖。
- controller 不应包含业务 mutation 逻辑。
- 已有 repository/provider 边界时，service 不应复制 query 细节。
- repository/provider 应向 controller 和 public DTO 隐藏 ORM 或外部 IO 细节。
- guard/interceptor/filter 应专注横切关注点，不承接业务 workflow。

## API 契约边界

当 frontend/backend 或共享契约同时变化时执行：

- request/response shape 应在 client wrapper、DTO、server handler、docs/OpenAPI 和 test 中一致。
- error behavior 应在 frontend handling 和 backend exception 中一致表达。
- optional/nullable 字段从 persistence 到 UI 应保持一致处理。

## 持久化边界

当 ORM/schema/repository 文件在范围内时执行：

- 如果项目已有 repository/provider mapping，应把 persistence-specific model 隔离在该边界后。
- schema/migration 变化不应直接把 raw generated type 泄漏到 UI-facing contract，除非项目既有模式如此。
- runtime repository wiring 应明确且可测试。

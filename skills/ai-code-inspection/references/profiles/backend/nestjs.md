# NestJS Profile

```yaml
profile_type: backend_framework
profile_id: nestjs
activation:
  component.framework:
    - NestJS
applies_to_steps: [1, 2, 3, 4, 5, 6, 7]
```

## 触发条件

仅当当前范围涉及的组件声明 `NestJS`，且依赖、decorator、module metadata 或 bootstrap 入口能够验证时加载。

## 命名与目录

- 沿用项目已有 `*.module.ts`、`*.controller.ts`、`*.service.ts`、DTO、provider、repository 和测试文件约定。
- controller、service、DTO、provider、repository、guard、interceptor 和 filter 只在项目真实使用时检查其所属 module 和目录。

## 架构边界

- `main.ts` 或项目实际 bootstrap 入口只承接启动与全局配置。
- controller 处理 transport；service 承接已有业务编排；repository/provider 隔离已有数据访问或外部 IO。
- guard、interceptor 和 filter 专注项目赋予的横切关注点，不承接业务 workflow。
- 不因本 Profile 要求项目新增 controller/service/repository 分层。

## 质量与错误处理

- DTO 或等价输入契约与 request shape 一致；项目启用 strict validation pipe 时覆盖未知字段的既有拒绝语义。
- invalid ID、missing record、unauthorized access 和 unsupported operation 使用项目已有 Nest exception 或 domain error 体系，不静默转换错误语义。

## 测试要求

项目已有对应测试层时，controller、service、guard、filter、DTO 和数据 mapping 变化覆盖成功路径及关键拒绝路径。

## 构建与验证

执行环境档案中该组件的 build、typecheck、lint 和 test 命令；module wiring 或 decorator metadata 变化后必须运行能够验证启动/依赖装配的现有命令。

## Generated Artifact 或迁移

本 Profile 不定义持久化迁移。由匹配的 persistence Profile 和环境档案处理。

## 不适用时

激活条件不满足时跳过本 Profile，不把 NestJS 的对象或文件后缀应用到其他后端框架。

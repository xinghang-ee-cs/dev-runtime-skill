# Vue Profile

```yaml
profile_type: frontend_framework
profile_id: vue
activation:
  component.framework:
    - Vue
    - Nuxt
applies_to_steps: [1, 2, 3, 4, 6, 7]
```

## 触发条件

仅当当前范围涉及的组件在环境档案中声明上述框架，且仓库 manifest、配置或源码事实一致时加载。

## 命名与目录

- 组件文件沿用项目现有风格；项目采用单文件组件和 PascalCase 约定时使用 `PascalCase.vue`，否则不得强制改名。
- 页面、路由、composable、store 和共享类型保留在项目已有目录，不新增平行结构。
- composable 命名沿用项目已采用的前缀和导出方式。

## 架构边界

- 页面与组件不绕过已有 API client、composable 或 store 边界重复维护共享逻辑。
- props、emits、route params 和共享 state 的类型/契约保持一致。
- 响应式数据的读取、解包和生命周期处理遵循当前框架版本与项目已有模式。

## 测试要求

- 组件、composable、store 或页面流程变化时，在项目已有测试层覆盖关键分支。
- 测试 runner 的具体命令和断言规则由匹配的 testing Profile 与环境档案决定。

## 构建与验证

- 使用组件的 `scripts.typecheck`、`scripts.build`、`scripts.test` 或工作区等价命令。
- 模板、props/emits 或共享类型变化后，单元测试不能替代可用的类型检查或构建。

## Generated Artifact

框架或路由工具生成的声明、客户端或路由文件应通过项目已有生成命令更新；确认是 generated artifact 时不直接手改。

## 不适用时

激活条件不满足时跳过本 Profile，继续执行通用 Step；不得据此推断项目使用其他前端框架。

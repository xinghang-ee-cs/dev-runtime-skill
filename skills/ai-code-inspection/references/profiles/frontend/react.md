# React Profile

```yaml
profile_type: frontend_framework
profile_id: react
activation:
  component.framework:
    - React
    - Next.js
applies_to_steps: [1, 2, 3, 4, 6, 7]
```

## 触发条件

仅当当前范围涉及的组件在环境档案中声明上述框架，且仓库 manifest、配置或源码事实一致时加载。

## 命名与目录

- 组件、页面和 hook 文件沿用所属目录已有命名及导出方式，不强制项目统一为某一种文件名后缀。
- 自定义 hook 遵循项目已有 `use*` 命名和放置约定。

## 架构边界

- 展示、状态、数据请求和外部能力只有在项目已有边界时才按该边界检查；不为套用 Profile 新增层。
- effect 的依赖、cleanup 和异步竞态处理必须与实际生命周期一致。
- context、共享 state 或请求缓存已有 owner 时，不在无关组件复制同一状态源。

## 测试要求

- 组件、hook 或页面流程变化时，使用项目已有测试层覆盖用户可观察行为和关键失败路径。
- 不把实现细节断言当作业务契约；具体 runner 规则由匹配的 testing Profile 提供。

## 构建与验证

执行环境档案声明的 build、typecheck、lint 和 test 命令；类型或路由契约变化后，局部测试不能替代可用构建/类型检查。

## Generated Artifact

路由、服务端/客户端边界或构建工具生成的文件只通过项目已有生成命令更新，不直接修改确认的 generated output。

## 不适用时

激活条件不满足时跳过本 Profile，继续执行通用 Step。

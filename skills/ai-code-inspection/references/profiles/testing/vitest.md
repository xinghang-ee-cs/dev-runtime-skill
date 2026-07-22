# Vitest Profile

```yaml
profile_type: testing
profile_id: vitest
activation:
  component.test_runners:
    - Vitest
applies_to_steps: [4, 7]
```

## 触发条件

仅当当前范围涉及的组件声明 `Vitest`，且 manifest、配置或测试文件能够验证时加载。

## 命名与目录

测试文件、fixture、mock 和 setup 文件沿用项目现有命名与目录；不为统一风格移动历史测试。

## 架构边界

测试与被测组件的归属、共享 test utility 和 integration 边界沿用项目现有结构；本 Profile 不要求生产代码为测试便利新增层或改变依赖方向。

## 测试要求

- 使用项目已有 environment、setup、alias 和 test utility。
- 针对当前行为覆盖成功、失败和边界路径，mock 保持与生产契约一致。
- 组件、hook、composable、store、service 等对象仅在项目真实存在时作为测试对象，不由本 Profile 强制创建。
- 不把单个 focused test 结果描述为完整测试通过。

## 构建与验证

- 优先运行环境档案中组件的 `scripts.test`、`scripts.coverage` 或工作区等价命令。
- 类型或构建契约变化时，Vitest 通过不能替代可用的 typecheck/build。

## Generated Artifact

coverage、snapshot 更新和其他生成输出遵循项目现有脚本与提交约定；不得仅为让测试通过无依据地更新 snapshot。

## 不适用时

激活条件不满足时跳过本 Profile，继续使用项目实际测试框架和通用 Step 4/7。

# TypeScript Profile

```yaml
profile_type: language
profile_id: typescript
activation:
  component.language:
    - TypeScript
applies_to_steps: [1, 2, 4, 7]
```

## 触发条件

仅当当前范围涉及的组件声明 `TypeScript`，且源码、manifest 或编译配置能够验证时加载。

## 命名与目录

类型、interface、enum、module 和声明文件沿用项目已有导出、命名和目录约定；公共名称变化按高风险契约变化处理。

## 质量与契约

- 优先收窄未知数据并在输入边界验证，不无依据使用 `any`、宽泛 `string` 或无结构 object 替代已有窄契约。
- optional、nullable、union 和 readonly 语义与 runtime 数据 shape 保持一致。
- test double 尽量复用导出的生产类型。

## 架构边界

公共类型、内部类型和 generated type 沿用项目已有共享边界；不得仅为统一类型组织而新增跨组件依赖或把持久化表示泄漏到公共契约。

## 测试要求

类型层通过不代替行为测试；行为测试通过也不代替可用的编译或 typecheck。

## 构建与验证

typed source、公共类型或配置变化时执行环境档案声明的 typecheck 或 build；如果两者都存在，按项目既有 verify 流程选择并报告覆盖关系。

## Generated Artifact

generated declaration、client type 或 codegen output 只通过项目已有生成命令更新，不直接修改确认的生成文件。

## 不适用时

激活条件不满足时跳过本 Profile，不把 TypeScript 类型规则强加给其他语言。

# OpenAPI Profile

```yaml
profile_type: contract
profile_id: openapi
activation:
  contracts.type:
    - OpenAPI
    - Swagger
applies_to_steps: [1, 2, 3, 4, 5, 7]
```

## 触发条件

仅当当前范围关联的契约条目声明上述类型，且 `contracts.paths` 或项目生成配置能够验证时加载。

## 命名与目录

operation、schema、parameter、response 和 error 名称沿用现有契约风格；公共名称变化按高风险处理。

## 架构边界

- 请求/响应 shape、nullable/required、枚举和错误语义在契约、入口处理、调用端与测试之间保持一致。
- generated client 或 server stub 与手写 adapter 的边界沿用项目已有结构。

## 测试要求

契约行为变化时使用项目已有 contract test、schema validation 或集成测试；没有该测试层时只报告缺口，不引入新工具。

## 构建与验证

从环境档案的 `contracts.validation_commands` 和 `generation_commands` 读取命令。契约变化后，局部单元测试不能替代可用的契约验证或生成检查。

## Generated Artifact

generated SDK、client、server stub 或 type 通过声明的生成命令更新；不直接修改确认的生成输出。生成命令不可用时报告剩余风险。

## 不适用时

激活条件不满足时跳过本 Profile；通用 Step 5 仍检查项目实际采用的其他公共契约描述。

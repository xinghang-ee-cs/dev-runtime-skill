# Prisma Profile

```yaml
profile_type: persistence
profile_id: prisma
activation:
  persistence.orm_or_client:
    - Prisma
applies_to_steps: [1, 2, 3, 4, 5, 7]
```

## 触发条件

仅当当前范围关联的持久化条目声明 `Prisma`，且 schema、依赖或生成配置能够验证时加载。路径必须来自环境档案，不假定固定目录。

## 命名与目录

- model、field、enum、relation 和 mapping 沿用当前 schema 的命名与映射风格。
- schema、migration 和 generated client 路径以 `persistence.schema_paths`、`migration_paths`、`generated_paths` 为准。

## 架构边界

- 项目已有 repository/provider 或 mapping 边界时，在该边界内隔离 Prisma model 与公共契约。
- 不把 generated persistence shape 无依据地泄漏到公共响应或跨组件契约。

## 测试要求

- mapping、nullable、relation、enum 或 transaction 行为变化时，使用项目已有单元或集成测试层验证。
- 没有既有集成测试时，不强制连接真实数据库。

## 构建与验证

- schema 变化时执行环境档案声明的 Prisma schema validation；需要 generated client 时使用项目已有 generate 命令。
- build/test 通过不代表 runtime 数据库已应用 migration。

## Generated Artifact 与迁移

- 不直接修改 generated client。
- schema 与 migration 状态分开记录为 `created_only`、`validated`、`applied` 或 `not_confirmed`。
- migration 命令只从环境档案读取；没有用户对目标数据库、环境和具体命令的明确确认时不得执行。

## 不适用时

激活条件不满足时跳过本 Profile，仍按通用持久化规则检查环境档案声明的 schema 和 migration 路径。

# Step 4: 测试覆盖

本 Step 检查变更行为是否具备足够的日常自动化覆盖。

## 测试发现

先读取 `../project-environment-profile.md`，再检查 package script，最后选择命令。

优先使用已有 package script，不要优先拼装 ad hoc runner 命令。

## 通用覆盖检查

- 新行为应有相邻 unit、component、service、repository 或 integration test；前提是项目已有该测试层。
- validation 逻辑变化应覆盖接受和拒绝输入。
- error handling 变化应覆盖失败路径。
- data mapping 变化应覆盖 optional、null、missing field 和 enum-like 值。
- async UI 或 service flow 变化应尽量覆盖 loading、success 和 failure 状态。
- test mock 应尽量贴近生产 interface/type。
- 除非开发者要求扩展测试系统，否则不要引入新 test runner。

## Frontend 覆盖检查

当 frontend 文件在范围内时执行：

- 项目使用 Vitest 时，Vue component/composable/store 变化应有 Vitest 覆盖。
- API wrapper 变化应测试 response unwrap、异常 payload、error normalization 和 request payload shape。
- UI workflow 变化应覆盖关键业务分支，不只测试 happy path。
- 影响类型的 frontend 变化应执行可用的 build/typecheck。

## Backend 覆盖检查

当 backend 文件在范围内时执行：

- NestJS service/controller/guard/filter 变化应测试成功路径和关键拒绝路径。
- DTO 变化应在项目已有 DTO validation test 时覆盖校验行为。
- repository/data mapping 变化应测试 persistence-to-domain mapping；除非项目已有 integration test，否则不要强制连接 live database。
- external provider/adapter 变化应使用 fake client 测试 adapter 边界行为。

## Prisma 与 Generated Artifact

当 schema、migration、generated client、OpenAPI type、SDK output 或 codegen dependency 变化时执行：

- 如存在 schema validation 命令，必须执行。
- build/test script 应自行生成必要 artifact，不得依赖本机旧的 generated output。
- migration 状态必须与 schema validation 分开记录。

## CI/CD 检查

仅当 `ci_cd.ci_enabled: true` 时执行：

- 检查 workflow 文件是否对相关变更区域覆盖 clean install、build、test、schema/migration 步骤。
- 不得从本 Skill 执行 deployment 或 release job。

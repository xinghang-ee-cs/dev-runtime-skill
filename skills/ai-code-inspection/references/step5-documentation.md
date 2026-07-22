# Step 5: 文档一致性

本 Step 检查代码变化是否需要同步文档。

## 通用检查

- 文档应匹配真实项目命令、路径、端口、入口名、公共契约、schema 行为和环境要求。
- 本 Skill 不新增业务规划内容。
- 不得把每次运行的检查记录写入稳定环境文档。
- 只实现了部分行为或未完成 runtime 验证时，不要把文档写成“已完整完成”。
- 面向使用者的 setup 指令应使用 manifest 或项目配置中真实存在的路径和命令。

## 需要更新文档的情况

- 启动命令、端口或环境变量变化。
- 公共接口、request、response、event、message 或 error behavior 变化。
- 用户入口、workflow 或用户可见行为变化。
- 组件边界、persistence wiring 或外部能力行为变化。
- database schema、migration、generated client 行为或 runtime migration 要求变化。
- test command 或 CI workflow 行为变化。

## API 文档检查

公共接口行为变化时，如果项目存在公共契约描述工具或文档，例如但不限于 API notes、schema 或接口定义文件，则检查：

- method 和 path。
- request body / query params。
- response shape。
- error behavior。
- 调用端封装路径。
- 入口处理器或业务 owner。

## 数据模型与迁移检查

persistent field 或 migration 变化时：

- 更新项目中用于描述数据模型变化的 schema/migration 引用。
- 明确区分 schema 变化、migration 生成、schema validation 结果和 runtime DB 应用确认情况。
- 除非 migration 应用已经明确确认，不得暗示 runtime 数据库已经拥有新增 column/enum。

## 环境文档检查

- `.env.example` 可以记录代码要求的环境变量。
- 本 Skill 不编辑 `.env.local` 或其他本地密钥文件。

## 事实优先级与规范矫正边界

本 Step 的问题统一使用 `../SKILL.md` 定义的六种分类。判断文档与实现冲突时使用以下事实优先级：

```text
明确用户确认或正式需求
→ 公共契约
→ 已确认自动化测试
→ 稳定现有行为
→ 文档
→ 本次新增实现
```

### 可安全矫正

- 只有事实来源明确、错误一方唯一且修改不引入业务规则时，才归为 `safe_standard_correction` 并修正明确错误的一方。
- 文档修改仍必须位于授权范围，不得把部分实现描述为完整完成，也不得把未确认 migration 描述为已应用。

### 只能报告或路由

- 文档与代码冲突但无法确认事实来源：归为 `report_only_risk`，不得修改代码或文档。
- 已有公共契约或已确认测试证明实现错误：归为 `confirmed_bug`，代码修复转入 `confirmed_bugfix`。
- 需要补充业务规则、验收标准、兼容要求或新的产品说明：归为 `incremental_design_required`。
- 需要改变模块边界、实现路径或架构后才能消除文档冲突：归为 `refactor_assessment_required`。
- 涉及生产状态、数据库执行、发布、安全策略或 Breaking API：归为 `blocked_out_of_boundary`。

禁止默认以代码为真覆盖文档，禁止默认以文档为真修改代码，禁止借文档修正引入新的业务规划。

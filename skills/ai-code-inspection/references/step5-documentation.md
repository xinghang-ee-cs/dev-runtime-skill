# Step 5: 文档一致性

本 Step 检查代码变化是否需要同步文档。

## 通用检查

- 文档应匹配真实 package script、路径、端口、route name、API contract、schema 行为和环境要求。
- 本 Skill 不新增业务规划内容。
- 不得把每次运行的检查记录写入稳定环境文档。
- 只实现了部分行为或未完成 runtime 验证时，不要把文档写成“已完整完成”。
- 面向使用者的 setup 指令应使用 manifest 中真实存在的路径和 package script。

## 需要更新文档的情况

- 启动命令、端口或环境变量变化。
- public API endpoint、request、response 或 error behavior 变化。
- frontend route、workflow 或用户可见行为变化。
- backend module 边界、persistence wiring 或 external provider 行为变化。
- database schema、migration、generated client 行为或 runtime migration 要求变化。
- test command 或 CI workflow 行为变化。

## API 文档检查

endpoint 行为变化时，如项目存在 docs/OpenAPI/API notes，应检查：

- method 和 path。
- request body / query params。
- response shape。
- error behavior。
- frontend API wrapper 路径。
- backend controller/service owner。

## 数据模型与迁移检查

persistent field 或 migration 变化时：

- 更新项目中用于描述数据模型变化的 schema/migration 引用。
- 明确区分 schema 变化、migration 生成、schema validation 结果和 runtime DB 应用确认情况。
- 除非 migration 应用已经明确确认，不得暗示 runtime 数据库已经拥有新增 column/enum。

## 环境文档检查

- `.env.example` 可以记录代码要求的环境变量。
- 本 Skill 不编辑 `.env.local` 或其他本地密钥文件。

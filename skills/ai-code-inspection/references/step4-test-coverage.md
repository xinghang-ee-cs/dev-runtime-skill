# Step 4: 测试覆盖

本 Step 检查变更行为是否具备足够的日常自动化覆盖。

## 测试发现

先读取项目根目录 `.runtime/ai-code-inspection/project-environment-profile.md`，再检查项目 manifest、脚本和测试配置，最后选择命令。

项目使用什么测试框架，就优先使用该框架和已有项目命令；不要优先拼装 ad hoc runner 命令。

## 通用覆盖检查

- 新行为应在项目已有测试层中获得相邻且适当的覆盖；不得仅因 Skill 偏好引入新的测试层。
- validation 逻辑变化应覆盖接受和拒绝输入。
- error handling 变化应覆盖失败路径。
- data mapping 变化应覆盖 optional、null、missing field 和 enum-like 值。
- 异步交互或业务流程变化应尽量覆盖 loading、success 和 failure 等项目中存在的状态。
- test double 应尽量贴近生产契约。
- 除非开发者要求扩展测试系统，否则不要引入新 test runner。

## 测试对象检查

按项目实际存在的测试对象和测试层执行：

- 用户界面单元或页面流程变化应覆盖关键业务分支，不只测试 happy path。
- 路由或入口处理器变化应覆盖成功路径、关键拒绝路径和错误契约。
- 应用服务、use case 或业务编排单元变化应覆盖核心规则与异常路径。
- 数据访问 mapping 变化应覆盖持久化表示到内部表示的转换；除非项目已有集成测试，否则不要强制连接真实数据库。
- 外部能力 adapter 变化应使用项目已有的 fake、mock 或等价隔离方式验证边界行为。
- 输入校验契约变化应在项目已有校验测试层中覆盖接受与拒绝行为。
- 具体 runner、框架对象和测试约定只从当前范围匹配的 Profile 加载。

## Schema 与 Generated Artifact

当持久化 schema、migration、generated client、公共契约 type、SDK output 或 codegen dependency 变化时执行：

- 如存在 schema validation 命令，必须执行。
- build/test script 应自行生成必要 artifact，不得依赖本机旧的 generated output。
- migration 状态必须与 schema validation 分开记录。

## CI/CD 检查

仅当环境档案确认存在 CI/CD workflow 时执行：

- 检查相关 workflow 是否覆盖项目实际需要的 clean install、build、test、schema/migration 步骤。
- 不得从本 Skill 执行 deployment 或 release job。

## 预期行为来源与规范矫正边界

本 Step 的问题统一使用 `../SKILL.md` 定义的六种分类。新增确定断言前，必须为问题记录一个明确的 `expected_behavior_source`：

```yaml
expected_behavior_source:
  - existing_test
  - confirmed_requirement
  - public_contract
  - approved_document
  - stable_existing_behavior
  - explicit_user_confirmation
```

### 可安全矫正

- 只有预期行为可追溯到上述明确来源，且不需要创造业务规则时，测试缺口才可归为 `safe_standard_correction` 并补充确定断言。
- 测试修改不得改变生产行为、公共契约、测试框架或数据访问方式。

### 只能报告或路由

- 已有失败测试或可证明错误行为指向生产缺陷：归为 `confirmed_bug`，不得在本模式自动修改生产代码。
- 有覆盖风险但预期或安全修正方式不唯一：归为 `report_only_risk`。
- 文档、代码与测试冲突，或需要决定状态、输入接受/拒绝、异常跳转/提示/重试、默认值或 fallback：归为 `incremental_design_required`，只输出待确认场景、预期行为和建议验收条件。
- 需要引入测试框架、重构生产结构或建立新测试层：归为 `refactor_assessment_required`。
- 强制连接真实数据库、执行发布/生产验证或触发其他硬边界：归为 `blocked_out_of_boundary`。

禁止因新增测试失败而自动修改生产代码；禁止为补测试自行创造业务规则；禁止引入新测试框架；禁止强制连接真实数据库；禁止把测试实现细节当成业务事实。

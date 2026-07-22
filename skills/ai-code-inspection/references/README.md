# 代码检查与规范矫正路线图

本文件只提供 `ai-code-inspection` 的轻量执行路线。运行状态、范围、权限、修正和 `继续` gate 以 `../SKILL.md` 为唯一事实源。

## 启动

1. 读取 `../project-environment-profile.md` 和 `../inspection-runtime-state.md`。
2. 从 11 种模式中选择任务入口；普通“检查代码”默认 `changed_code_review`，全量检查固定 `full_readonly_audit`。
3. 分别解析 `scope`、`editable_scope` 和 `remediation_policy`；读取范围不得替代修改授权。
4. 按模式加载 Step：规范矫正以交互方式完整执行 Step 1–7；全量只读审计以单次只读方式完整执行 Step 1–7；其余 9 种模式按任务加载适用 Step。
5. 根据当前范围涉及的组件、语言、框架、测试、持久化和契约工具，只加载 `profiles/` 中匹配的附加规则。

环境档案未初始化时，先依据目标仓库真实文件、配置和脚本初始化；不得从示例或其他项目复制。没有匹配 Profile 时仍完整执行通用 Step，并报告专用 Profile 未覆盖，不猜测框架规则。

## 两种执行方式

- 前 10 种模式使用 `single_run`：一次请求完成全部适用检查或执行、验证和最终反馈，不等待用户反复输入 `继续`。
- `full_readonly_audit` 虽完整执行 Step 1–7，仍在单次运行中连续完成并一次性报告，不能进入修复。
- 第 11 种 `standards_compliance_correction` 使用 `interactive_seven_step`：按 Step 1–7 分步只读检查，问题需要用户明确确认。
- 其余 9 种模式使用 `single_run`，按任务加载并连续执行适用 Step。

`confirmed_bugfix` 只有在预期行为、根因证据和具体根因文件均明确时才获得精确文件修改权限；否则保持只读并转入诊断、增量设计或重构评估。它不使用授权批次、`继续` gate 或 Step 间暂停。

规范矫正不改变业务逻辑、外部行为或实现方式。已确认 Bug 修复允许在明确根因文件内，将已经证明错误的行为最小修正为有明确依据的预期行为。

## 规范矫正入口

- `standards_compliance_correction` 默认先检查并报告，不直接获得修改权限。
- Step 问题统一按 `../SKILL.md` 中的六种分类记录。
- 只有用户确认具体问题编号或批次后，才进入一个明确授权批次的修正阶段。
- `继续` 有授权批次时只执行一个批次；没有待执行批次且当前 Step 已报告时，只进入下一 Step 的只读检查。
- 普通 `继续` 不能确认批次、创建权限或扩大权限。
- 涉及业务行为、预期设计、架构重构或硬边界的问题，必须路由到对应模式，不在规范矫正中处理。

## 模式入口

- 日常与专项：`changed_code_review`、`targeted_diagnosis`、`confirmed_bugfix`、`regression_verification`、`implementation_completeness_review`。
- 设计与风险：`incremental_design`、`refactor_risk_assessment`。
- 交付检查：`merge_readiness_review`、`hotfix_patch_review`。
- 全量只读：`full_readonly_audit`。
- 完整七步规范矫正：`standards_compliance_correction`。

## Step 顺序

1. `step1-naming-convention.md`：命名、文件放置、术语一致性。
2. `step2-code-quality.md`：常见 Bug、死代码、错误处理、数据 shape、类型契约。
3. `step3-architecture-layer.md`：项目既有入口、传输、业务编排、数据访问、外部能力和共享契约边界。
4. `step4-test-coverage.md`：测试影响、边界用例、验证命令选择。
5. `step5-documentation.md`：docs/API/schema/README 与代码行为一致性。
6. `step6-comment-standard.md`：注释和本地文件头规范。
7. `step7-code-commit.md`：git 状态、验证摘要、提交准备和 CI/CD 配置轻量检查。

技术栈附加规则入口见 `profiles/README.md`。Profile 只补充技术细节，不定义 Runtime、模式、权限或问题分类。

## 常用证据命令

```bash
git status --short
git diff --name-only
git diff --cached --name-status
git ls-files --others --exclude-standard
git diff -- <scoped-files>
```

## 收口

`single_run` 只输出一次最终报告；`interactive_seven_step` 输出当前 Step 或单个修正批次的阶段报告。报告应展示模式、执行策略、范围、权限、问题分类、修改、验证和风险；交互式修正还必须展示授权批次。

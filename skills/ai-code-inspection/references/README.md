# 真实工作场景路线图

本文件只提供 `ai-code-inspection` 的场景概览、轻量路由和执行路线。`../SKILL.md` 是完整场景定义、冲突规则、Runtime、范围、权限、切换、gate 和报告要求的唯一事实源。

## 10 个用户场景

1. `changed_code_review`：当前改动日常检查；只读检查当前 Git 变更。
2. `targeted_diagnosis`：具体问题根因诊断；建立证据链，不修改代码。
3. `confirmed_bugfix`：已确认问题的修复与回归闭环；准入满足后最小修复并自动回归。
4. `implementation_completeness_review`：需求实现完整性核查；对照正式依据建立实现矩阵。
5. `incremental_design`：业务规则与验收边界补全；只补规则、流程与验收依据。
6. `full_readonly_audit`：全项目现状审计；一次性只读完成 Step 1–7。
7. `refactor_risk_assessment`：重构前影响与风险评估；不执行重构。
8. `merge_readiness_review`：代码合并前交付就绪检查；不执行 Git 写操作。
9. `hotfix_patch_review`：关键阻断问题的紧急修复闭环；先只读诊断，准入后仅做最小补丁。
10. `standards_compliance_correction`：规范性检查与受控矫正；交互式执行 Step 1–7。

`regression_verification` 不是用户入口，只能在场景 3 实际完成代码修复和基础验证后自动进入；进入前撤销修改权限。用户场景来源保留在 `scene_source`，内部回归来源另记为 `internal_phase_source: automatic_internal_phase`。

## 执行路线

- 场景 1–9 使用 `single_run`；在范围和权限内完成全部适用工作后只输出一次最终报告。
- 场景 6 虽完整执行 Step 1–7，内部 Step 也不是交互 gate，且全程只读。
- 只有场景 10 使用 `interactive_seven_step`；每个 Step 先只读报告，用户明确确认具体问题批次后才能受控矫正。
- 普通 `继续` 只能消费已有精确授权批次或推进下一个只读 Step，不能创建权限、扩范围或切换场景。
- 项目已有的不连接目标数据库的 schema validation/codegen 可作为本地验证执行；真实数据库连接、migration 和数据写入仍需单独授权。代码修改权限与真实数据库操作权限相互独立。

## 轻量路由

- 当前变更普通 Review → 场景 1；具体异常且根因未知 → 场景 2。
- 明确问题并要求修复 → 请求场景 3；准入不足时保留 `repair` 意图进入诊断，条件补齐后在同一 `single_run` 自动返回修复闭环。
- 明确需求/验收依据并检查完成度 → 场景 4；规则或预期不明 → 场景 5。
- 全项目摸底 → 场景 6；明确结构对象并评估风险 → 场景 7。
- commit、PR/MR 或合并准备 → 场景 8；阻断故障 + 修复意图 + 紧急性 → 场景 9。
- 核心判断依据是工程规范 → 场景 10。
- 场景 10 优先使用明确文件/模块，其次当前改动，再次明确全项目；没有可靠范围时使用 `scope.target: unresolved` 并停止，不扫描全项目。

场景语义优先于单词匹配。“对修改的代码做规范性检查”进入场景 10；“检查修改的代码”进入场景 1；“快速检查代码”不等于紧急修复；“提交表单前检查”不等于代码合并检查。

## 环境与 Profile

1. 从项目根目录 `.runtime/ai-code-inspection/` 读取环境档案和运行状态；缺失时从 `../assets/runtime-templates/` 按当前任务需要初始化。
2. 先加载当前场景需要的通用 Step reference。
3. 根据当前范围涉及的组件、语言、框架、测试、持久化和契约工具，只加载 `profiles/` 中匹配的附加规则。
4. 没有匹配 Profile 时仍执行通用 Step，并报告专用 Profile 未覆盖，不猜测框架规则。

## Step 顺序

1. `step1-naming-convention.md`：命名、文件放置、术语一致性。
2. `step2-code-quality.md`：常见 Bug、死代码、错误处理、数据 shape、类型契约。
3. `step3-architecture-layer.md`：项目既有入口、业务编排、数据访问、外部能力和公共契约边界。
4. `step4-test-coverage.md`：测试影响、边界用例、验证命令选择。
5. `step5-documentation.md`：docs/API/schema/README 与代码行为一致性。
6. `step6-comment-standard.md`：注释和项目本地文件头规范。
7. `step7-code-commit.md`：Git 状态、验证摘要、提交准备和 CI/CD 配置检查。

## 常用证据命令

```bash
git status --short
git diff --name-only
git diff --cached --name-status
git ls-files --others --exclude-standard
git diff -- <scoped-files>
```

## 收口

`single_run` 只输出一次最终报告；`interactive_seven_step` 输出当前 Step 或单个修正批次的阶段报告。报告展示请求场景、实际场景、执行策略、范围、权限、问题分类、修改、验证和风险；交互式修正还展示授权批次。

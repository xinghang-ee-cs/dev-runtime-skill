# Skill 仓库与外部项目使用入口

本文件负责 Skill 的发现、安装、初始化、选择、路由、项目适配和统一安全原则。它不复制各 Skill 的完整规则，也不建立第二套 Runtime 治理。

## 1. 文件作用域

- 本顶层 `AGENTS.md` 对本仓库及其全部子目录生效。
- 更靠近目标文件的子目录 `AGENTS.md` 可以补充局部规则；发生冲突时遵循更近且更高优先级的有效指令。
- 本文件不要求每次读取全部 Skill 或全部 references。
- 选中 Skill 后，以该 Skill 的 `SKILL.md` 作为具体运行规则来源，并只按其路由加载必要 reference、Profile、模板和 Runtime 文件。

## 2. Skill 发现

Agent 必须扫描目标仓库实际存在的 Skill 目录，先读取每个候选 Skill 的 `SKILL.md` frontmatter 或等价元数据，再根据用户目标选择最匹配项。不得虚构不存在的 Skill，不得同时混用职责冲突的 Skill。

本仓库当前真实 Skill 清单如下：

| Skill | 主要用途 | 典型触发语句 | 是否允许修改文件 | 是否需要项目初始化 | 依赖档案或 reference | 不适用场景 |
| --- | --- | --- | --- | --- | --- | --- |
| `ai-code-inspection` | 路由代码检查与根因诊断；在四 Skill 流程中创建 Bugfix Case | “定位这个报错”“为已确认 Bug 建立修复合同”“检查 PR 合并准备” | Fast Lane 只诊断并形成 Case，由 Long 修改 | 是；首次使用初始化项目级环境档案 | 环境档案、`bugfix-fast-lane.md`、Step references | 上线、生产门禁、无准入猜测修复 |
| `planning-layer-runtime` | 正式规划与 Change Set；治理 Bugfix Case 的合同边界和最终生产基线更新 | “先做开发规划”“判定这个问题是否需要改规划” | 可写正式规划；Fast Lane 不改原 00–15 | 是；绑定正式规划目录和当前基线 | `references/00`–`14`、当前基线、正式规划目录 | 直接实现、测试执行、发布 |
| `long-task-orchestrator` | 执行正式 handoff；也消费 `bugfix-case/v1` 完成不限单元数的精确补丁 | “按计划实现”“修复这个 Bugfix Case” | 通过合同和门禁后可修改实现、测试及 Case 结果 | 是；需要 handoff 或已确认 Case | Runtime kernel、planning handoff 或 Bugfix Case | 未分流合同变化、人工/云端测试、上线 |
| `testing-layer-runtime` | 管理期次验收；也负责 Bugfix 定向测试、生产复验和上线后同类型问题验证 | “开始验收”“验证 Bugfix Case”“继续同类型问题测试” | 只写 Testing Runtime 或 Bugfix Case，不改业务代码/Planning SoT | 是；定位期次或 Case 并读取 Long 证据 | Long 交接/补丁结果、测试合同或 Bugfix Case | 开发实现、无理由重跑 Long 自动化、直接发布 |

发现流程：

```text
扫描真实 Skill 目录
→ 读取候选元数据
→ 按用户目标筛选
→ 只完整读取选中 Skill 的 SKILL.md
→ 按其路由加载必要资源
```

## 3. 版本检查、同步与期次锁定

- `skills-manifest.json` 是仓库当前版本事实的唯一来源；不得从 `package.json`、README、`SKILL.md` 或文件修改时间推断 Skill 版本。
- 目标项目必须提交根目录 `runtime-skills.lock.json`。它记录来源 Release、commit、每个 Skill 版本、全部安装位置和内容摘要；不同 Agent 平台不得维护彼此独立的版本事实。
- 目标项目存在锁文件时，每个 Agent 会话第一次使用任一 Runtime Skill 前，先运行 `python .runtime-skills/runtime-skills.py sync --project .`。同一会话且锁文件未变化时不重复检查。
- `sync` 只在无本地漂移、无期次锁定且更新为兼容补丁版本时自动更新。次版本或主版本变化必须先展示版本差异并取得用户确认。
- 同一 `主版本.次版本` 系列发布新修订版本后，只向用户公开最新的 Release 和 Tag；旧修订版 Release 转为 Draft 保留维护记录，公开 Tag 删除。不同 `主版本.次版本` 系列继续公开保留，用于梯度灰度。
- 任何受管 Skill 或同步工具与锁文件摘要不一致时，停止自动覆盖，先运行 `diff` 并让用户决定保留本地修改还是采用发布版本。
- 新期次开始前先完成同步，再运行 `pin --reason <期次或任务标识>`。从 Planning 建立期次开始，到 Long、Testing 和期次关闭之间保持同一版本；不得在活动期次中途自动换版。
- 只有期次已经关闭，或用户明确批准迁移并接受重新校验现有 Runtime/合同后，才运行 `unpin` 并更新。
- 网络或 GitHub 不可用时，至少运行 `verify`。本地副本全部匹配锁文件时可以继续使用已锁版本，但必须报告没有完成远端更新检查。

## 4. 安装到外部项目

1. 优先运行 `scripts/runtime-skills.py install --release latest`，由同步工具从最新稳定 Release 复制完整 Skill 目录、安装目标项目级同步入口并生成锁文件；不要以手工复制作为正常安装流程。只有维护者明确验证未发布内容时才使用 `--source`。
2. 安装时同时复制 `SKILL.md`、`agents/` 元数据、references、Profiles、模板和必要 Runtime bootstrap 资产；不要只复制单个 `SKILL.md`。
3. 多平台共用时，在同一次安装中传入全部目标 Skill 根目录。工具必须把所有副本绑定到同一锁文件和同一 Release。
4. 不复制其他项目已经填写的环境事实或运行状态。`ai-code-inspection` 安装包中的 `assets/runtime-templates/` 只作为初始化源；首次使用时在目标项目根目录创建 `.runtime/ai-code-inspection/`，环境档案从 `uninitialized` 模板开始，运行状态从空闲模板开始。
5. 目标项目已有 `AGENTS.md` 时合并适用规则，不得直接覆盖。
6. 根据目标 Agent 平台和项目约定选择项目级 Skill 目录。可能的目录例如但不限于 `.skills/`、`.agents/skills/`、`.claude/skills/`、`.codex/skills/`。
7. 实际路径由所使用的 Agent 平台和项目约定决定；不得把任一示例目录视为唯一安装方式。
8. 平台没有固定 Skill 目录时，在目标项目的 `AGENTS.md` 中声明每个 Skill 的真实位置和发现方式。

## 5. 首次项目初始化

Agent 第一次在目标项目使用需要环境事实的 Skill 时，先执行：

```text
扫描仓库
→ 识别语言、框架、构建工具和包管理器
→ 识别前端、后端、服务、共享包、worker、CLI 和其他组件
→ 识别测试框架与测试层
→ 识别持久化方案、schema 和 migration 路径
→ 识别公共契约与生成工具
→ 识别 CI/CD 平台和全部相关 workflow
→ 识别真实 build/test/lint/typecheck/verify 命令
→ 初始化该 Skill 的项目环境档案或项目运行目录
→ 再运行 Skill
```

初始化只使用当前仓库证据和用户明确提供的约束。不得从 Skill 示例或其他项目推断技术栈；不得默认使用 Vue、React、NestJS、Prisma、TypeScript、某个 package manager、测试命令或数据库迁移命令。无法可靠确认的事实保持未确认并报告。

## 6. Skill 选择规则

```text
用户请求
→ 判断任务目标
→ 查找职责最直接的 Skill
→ 阅读该 Skill 的 SKILL.md
→ 加载必要环境档案和 reference
→ 确认检查范围、修改范围与权限
→ 执行任务
```

多个 Skill 都可能适用时：

- 选择职责最直接的 Skill 作为当前主治理 Skill。
- 不让检查 Skill 承担规划、发布或安全验收。
- 不让规划 Skill 直接修改生产代码。
- 不让实现 Skill 代替人工验收，也不让测试 Skill 重新承担开发期自动化。
- 不让发布流程代替日常代码检查。
- 必要时按 `planning → implementation → testing → 项目发布/安全流程` 顺序切换；每个阶段只保留一个主治理 Skill，完成明确 handoff 后再切换。

### Bugfix Fast Lane

已确认 `implementation_defect` 且当前 Planning 合同仍有效时，不创建新期次，也不修改原 00–15。使用追加式 `bugfix-case/v1`：

```text
Issue + ai-code-inspection 诊断/合同
→ fix/<BUG-ID>-short + Long 精确补丁
→ Testing 定向验证
→ PR/CI/仅经 PR 合并
→ 部署与原 Bug 生产复验
→ Testing 同类型问题扫描与定向验证
→ 关闭 Case 和 Issue
```

每次进入项目或收到部署返回时扫描未完成 `bugfix-case.json`。`deployed` 和 `original_bug_production_verified` 都不等于闭环；若状态为 `awaiting_similar_defect_verification`，必须突出提醒用户当前唯一下一步是继续 Testing，不能先宣告完成。新发现的同类型问题必须新建 Bug ID、Issue 和 Case，不得静默扩大原补丁。

## 7. 项目适配原则

通用 Skill 源文件不得存放目标项目的业务参数和长期环境事实。项目特定信息只写入：

- 目标项目的环境档案或 Runtime 目录；
- 目标项目已有配置和正式契约；
- 项目局部 `AGENTS.md`；
- 用户明确提供的需求和约束。

不得把项目名称、业务模块、企业名称、固定端口、固定域名、私有路径、用户名、密钥、真实数据库地址、真实部署环境或单个项目的 package script 回写到通用 Skill 源文件。

## 8. 规则优先级

在不与 Agent 平台或其他更高优先级指令冲突的前提下，仓库内按以下顺序解释：

```text
用户当前明确要求
→ 目标文件最近的 AGENTS.md
→ 当前选中的 SKILL.md
→ 当前 Skill 的 references 和 Profiles
→ 项目环境档案
→ 项目现有代码、配置、正式契约和测试事实
```

补充约束：

- 环境档案是稳定事实索引，不得覆盖更新、更直接的真实仓库事实；发现冲突时按选中 Skill 的规则纠正档案并报告。
- reference 不得覆盖 `SKILL.md` 的权限和 Runtime 治理。
- 技术栈 Profile 不得重新定义场景、范围、授权、问题分类或生命周期。
- 项目代码与正式契约冲突时，按选中 Skill 定义的事实优先级取证；没有明确依据时不得自行猜测。

## 9. 安全与修改原则

- 先识别检查范围与修改范围；读取权限不等于修改权限。
- 不修改范围外文件，不覆盖或清理用户未提交改动。
- 不自动执行发布、部署、数据库迁移或真实数据修改。
- 不自动读取、修改或输出真实密钥和环境变量。
- 未经用户明确要求，不执行 stage、commit、push、reset、checkout、stash 或创建/切换分支。
- 修改后运行目标项目已有的适用 build、test、lint、typecheck、schema 或契约验证命令。
- 无法验证时明确报告未执行项、原因和剩余风险。

## 10. GitHub 交付铁律

本仓库任何需要写入 GitHub 的变更都必须通过以下链路交付，不得跳步：

```text
创建或关联 Issue
→ 从最新默认分支创建专用分支
→ 仅向专用分支提交和推送
→ 创建关联 Issue 的 Pull Request
→ 等待全部适用 CI 检查完成并通过
→ 仅通过 Pull Request 合并
→ 合并后同步本地默认分支
```

强制约束：

- PR 正文必须关联对应 Issue；适合自动关闭时使用 `Closes #<issue-number>`。
- 禁止通过 Git CLI、GitHub API、Contents API、Git Data API、网页自动化或其他方式直接向 `main`、`master` 或仓库实际默认分支提交、推送、创建提交或移动 ref。
- README、文档、配置、测试、紧急修复、版本调整和 Release 准备同样适用，不得以改动较小、情况紧急或自动发布为理由绕过。
- 合并前必须核对 PR 范围、提交内容和全部适用 CI 结果。仓库未配置覆盖该改动的 CI 时，必须如实报告“无适用检查”，仍然只能通过 PR 合并，不得把未运行写成通过。
- Tag 和 GitHub Release 只能基于已经通过 PR 合并进入默认分支的提交，由仓库既有发布流程生成；不得用直接更新默认分支的方式触发发布。
- 工具、凭据、权限、分支保护或 CI 阻塞任一步时，立即停止并向用户报告；禁止退化为直接写默认分支，也禁止事后补建空 Issue 或无实际审查意义的 PR 伪造流程记录。

## 11. 外部用户快速开始

1. 使用同步工具安装所需 Skill，并把 `runtime-skills.lock.json` 提交到目标项目。
2. 在项目顶层放置或合并本 `AGENTS.md` 的适用入口规则。
3. 运行 `verify`，确认所有 Agent 平台副本与锁文件一致。
4. 让 Agent 扫描项目并初始化各已选 Skill 需要的环境档案或 Runtime 目录。
5. 先运行只读检查验证适配结果。
6. 确认识别出的技术栈、命令、范围和权限正确。
7. 再执行明确允许修改的任务。

通用示例指令：

```text
扫描当前项目，并初始化所有已安装 Skill 需要的项目环境档案，不修改业务代码。

列出当前项目可用的 Skill，以及每个 Skill 适合处理的任务。

使用 ai-code-inspection 检查当前 Git 变更，只读并一次性反馈。

使用 ai-code-inspection 对当前项目做全量只读审计。

使用适合的 Skill 处理这个任务，并先说明选择理由和执行边界。
```

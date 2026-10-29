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

## 3. 版本检查与期次锁定

- skills-manifest.json 是版本事实源；skills/ 是唯一规范规则源码，distribution/ 只包含平台元数据，生成包不回写源码。
- 默认使用 INSTALL.md 的用户全局安装入口。Codex/Copilot/dsh 共用受支持的用户 .agents/skills；Claude Code 用 .claude/skills。豆包工作/WorkBuddy 使用生成的单 Skill 导入包。不得猜测未知平台目录。
- Agent 发现目录只放短版本路由，精确规则缓存放在发现范围外。首次真实任务 session 绑定项目 schema 2 锁，返回 skill-root 和 runtime-tool，后续所有相对资源以返回目录解析。
- 项目事实和 Runtime 留在项目；不得向项目安装第二份静态 Skill，不向全局写项目记忆。安装阶段不创建项目锁或 Runtime，只有真实任务才绑定版本。
- 全局默认更新不改变已绑定项目。全局模式 sync 只 verify；显式 adopt 在期次外采用新默认。缺失/漂移精确缓存时停止，restore-cache 必须匹配完整摘要，不能回退 latest。
- 活动期次先 verify，缺 pin 时先 pin 已有期次；新期次在第一份状态前 pin。Planning → Long → Testing 使用同一项目锁。期次关闭或用户批准受控迁移后才能 unpin/adopt。
- schema 1 项目锁及旧项目命令保持兼容；全局路由不自动接管。显式 bind --migrate-project 前关闭期次并验证无漂移，事务性归档旧受管副本和工具；不移动项目记忆，不处理未受管文件。
- 旧补丁版本归档规则继续有效，精确缓存不自动回收。换机器需保留相同源包，不能把相同版本号视为相同内容。

## 4. 安装与分发

1. 按 INSTALL.md 明确当前实际 Agent，只安装对应用户包；不因多个历史目录而安装所有平台。auto 无法唯一识别时要求明确当前平台。
2. 普通用户从稳定 Release 获取 install.py 和 SHA256SUMS 校验后的 Agent ZIP；未发布产物不能用 main 冒充稳定版。维护者验证未发布源码才用 install-agent --source。
3. scripts/build-install-packages.py 从规范源码生成所有安装/导入包及校验索引；WorkBuddy frontmatter 仅在生成时扩展。导入包携带运行工具和精确规则，不依赖项目 .runtime-skills 脚本。
4. 安装检查已知项目、Git 祖先及用户发现根；未受管同名副本、漂移或不完整检查先解决，不覆盖、自动删除或新增一份规避。额外平台目录由配置证据单独检查。
5. 默认不创建 AGENTS.md/CLAUDE.md，不复制本文件或其他项目事实。已安装规则首次使用时只为当前职责补齐项目事实，不预建全部 Runtime。
6. 本次实现不自动提交市场审核或部署。Release 产物仍只能基于经 PR 合并到默认分支的代码。

### 入口说明的最小化与幂等

- 路由说明最多一个块，使用 `<!-- runtime-skills:begin -->` 和 `<!-- runtime-skills:end -->` 标记，最多 10 个非空行、1200 字符；只说明同步入口、按任务选择已安装 Skill，以及读取其 `SKILL.md`。
- 写入前检查目标文件及已生效的项目指令；已有等价说明且没有变化时不写入，已有标记块时只在原位置更新，不反复追加，不按 Skill 或安装目录分别创建入口。
- 不复制 Skill 正文、references、完整生命周期、项目扫描结果或本仓库的维护与 GitHub 发布规则到入口文件。安装位置与版本以 `runtime-skills.lock.json` 为准，不另建清单事实源。
- 日常调用、恢复会话和 Runtime 初始化不重新生成入口文件。发现历史重复文件或大段内容时先报告路径与差异，不自动删除或覆盖项目指令。

## 5. 首次项目初始化

安装与业务初始化分开。安装只部署所选静态包、同步工具和锁文件，doctor/verify 后停止，不扫描业务源码或预建四套 Runtime。首次实际任务只读取一个 Skill 入口，按当前范围补齐缺失的项目事实和必要状态；未涉及的组件、数据库、前端、CI/CD 不提前调研。后续复用已有事实，状态变化时精确更新。

大规则使用 session 返回的 runtime-tool 的 context 的 outline/section/offset 分段读取，单次最多 6000 字符；首轮静态规则目标不超过 12000 字符，后续按当前 gate 有理由扩展，不省略适用门禁。不要整读全部 references、历史日志或其他阶段。原入口完整规则保留在各 Skill 的 references/runtime-governance.md。

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

1. 让当前 AI 阅读 INSTALL.md 并安装对应用户全局包，校验后停止。
2. 另行提出真实任务，选中一个 Skill，经 session 绑定真实项目和精确规则。
3. 提交项目 runtime-skills.lock.json，按当前 gate 初始化必要事实，确认范围与权限后执行。
4. 不复制静态规则到项目，不重复添加路由，不预读其他 Skill。安装、诊断和业务执行保持各自边界。

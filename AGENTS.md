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
| `ai-code-inspection` | 按 10 种真实工作场景路由通用代码检查、诊断、只读审计、已确认 Bug/紧急补丁闭环和受控规范矫正 | “检查当前 Git 变更”“定位这个报错”“核查需求是否实现完整”“修复这个已确认 Bug”“检查 PR 合并准备”“按规范矫正这些文件” | 依场景决定；场景 1–9 单次完成，只有场景 10 交互执行七步；代码与真实数据库权限独立 | 是；首次使用从模板初始化项目级 `.runtime/ai-code-inspection/` | 项目级环境档案和 Runtime、Step references、按需 Profiles | 上线发布、生产门禁、严格安全验收、无准入的猜测修复或大规模重构 |
| `planning-layer-runtime` | 实现前的业务发现、Planning Context、正式规划文档和 planning handoff | “先做开发规划”“创建这一期规划文档”“梳理需求和验收边界” | 仅允许其定义的项目级规划启动上下文、正式规划文档与 planning runtime；不改生产代码 | 是；按需建立最小 `.runtime/planning-layer-runtime/`，并绑定目标项目已有的正式规划目录与当前事实基线路径 | `references/00`–`10`、`.runtime/planning-layer-runtime/`、项目当前基线和正式规划目录 | 直接实现、测试执行、发布或生产操作 |
| `long-task-orchestrator` | 根据已确认 handoff 执行至少 4 个实现单元的完整功能，并交付到 `ready_for_local_test`；也处理已确认缺陷 patch | “按已确认计划完成这个模块”“继续长任务实现并写自动化测试”“修复 testing 已确认缺陷” | 通过 Source of Truth 与 Runtime Gate 后可修改实现、测试和其 Runtime 资产 | 是；必须确认 handoff、通过 preflight 并创建/恢复 Phase Runtime Directory | Runtime kernel references、planning handoff、Phase Runtime Directory | 小于 4 个实现单元、缺少已确认 SoT、人工验收、云端验证、上线放行 |
| `testing-layer-runtime` | 继承 long 自动化结果并管理人工、真实设备、服务器、外部能力和最终验收，输出 release handoff | “开始这一期人工测试”“继承 long handoff 做验收”“整理服务器验证和上线移交” | 只写其 `testing-runtime/` 输出；不改业务产物或 planning SoT | 是；必须定位测试期次、读取 long handoff 和测试范围 | 项目环境事实源、long testing handoff、测试方案、`references/01`–`05` | 开发实现、重跑已有通过自动化、定义新需求、直接发布或安全门禁 |

发现流程：

```text
扫描真实 Skill 目录
→ 读取候选元数据
→ 按用户目标筛选
→ 只完整读取选中 Skill 的 SKILL.md
→ 按其路由加载必要资源
```

## 3. 安装到外部项目

1. 复制所需 Skill 的完整目录并保持内部相对路径不变。
2. 同时复制 `SKILL.md`、`agents/` 元数据、references、Profiles、模板和必要 Runtime bootstrap 资产；不要只复制单个 `SKILL.md`。
3. 不复制其他项目已经填写的环境事实或运行状态。`ai-code-inspection` 安装包中的 `assets/runtime-templates/` 只作为初始化源；首次使用时在目标项目根目录创建 `.runtime/ai-code-inspection/`，环境档案从 `uninitialized` 模板开始，运行状态从空闲模板开始。
4. 目标项目已有 `AGENTS.md` 时合并适用规则，不得直接覆盖。
5. 根据目标 Agent 平台和项目约定选择项目级 Skill 目录。可能的目录例如但不限于 `.skills/`、`.agents/skills/`、`.claude/skills/`、`.codex/skills/`。
6. 实际路径由所使用的 Agent 平台和项目约定决定；不得把任一示例目录视为唯一安装方式。
7. 平台没有固定 Skill 目录时，在目标项目的 `AGENTS.md` 中声明每个 Skill 的真实位置和发现方式。

## 4. 首次项目初始化

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

## 5. Skill 选择规则

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

## 6. 项目适配原则

通用 Skill 源文件不得存放目标项目的业务参数和长期环境事实。项目特定信息只写入：

- 目标项目的环境档案或 Runtime 目录；
- 目标项目已有配置和正式契约；
- 项目局部 `AGENTS.md`；
- 用户明确提供的需求和约束。

不得把项目名称、业务模块、企业名称、固定端口、固定域名、私有路径、用户名、密钥、真实数据库地址、真实部署环境或单个项目的 package script 回写到通用 Skill 源文件。

## 7. 规则优先级

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

## 8. 安全与修改原则

- 先识别检查范围与修改范围；读取权限不等于修改权限。
- 不修改范围外文件，不覆盖或清理用户未提交改动。
- 不自动执行发布、部署、数据库迁移或真实数据修改。
- 不自动读取、修改或输出真实密钥和环境变量。
- 未经用户明确要求，不执行 stage、commit、push、reset、checkout、stash 或创建/切换分支。
- 修改后运行目标项目已有的适用 build、test、lint、typecheck、schema 或契约验证命令。
- 无法验证时明确报告未执行项、原因和剩余风险。

## 9. 外部用户快速开始

1. 将需要的 Skill 完整复制到项目。
2. 在项目顶层放置或合并本 `AGENTS.md` 的适用入口规则。
3. 让 Agent 扫描项目并初始化各已选 Skill 需要的环境档案或 Runtime 目录。
4. 先运行只读检查验证适配结果。
5. 确认识别出的技术栈、命令、范围和权限正确。
6. 再执行明确允许修改的任务。

通用示例指令：

```text
扫描当前项目，并初始化所有已安装 Skill 需要的项目环境档案，不修改业务代码。

列出当前项目可用的 Skill，以及每个 Skill 适合处理的任务。

使用 ai-code-inspection 检查当前 Git 变更，只读并一次性反馈。

使用 ai-code-inspection 对当前项目做全量只读审计。

使用适合的 Skill 处理这个任务，并先说明选择理由和执行边界。
```

# AI 开发全流程 Runtime Skills

[English](README.md) | [简体中文](README.zh-CN.md)

这是一套与具体项目无关的 Agent Skills，负责开发规划、实现、测试和代码检查。仓库只保存可复用治理；目标项目的命令、账号、路径和环境事实必须留在目标项目中。

只有 `skills/` 下被选中的目录属于可安装 Skill 包；`AGENTS.md` 是可复用的项目入口模板。`src/`、`public/`、`package*.json`、`astro.config.mjs`、`tsconfig.json` 和文档部署 workflow 只用于构建本仓库的 Astro/Starlight 文档站，不能复制到目标项目。

## 五个 Skill

| Skill | 适用任务 | 边界 |
| --- | --- | --- |
| [`dev-runtime`](skills/dev-runtime/SKILL.md) | 为完整或模糊开发请求动态发现并路由已安装的 Runtime Skill；先进入规划，并保留各阶段当前的进入和交接门禁。 | 不替代阶段治理，不处理单一阶段请求，不假设固定 Skill 目录，也不批准发布；少于 4 个实现单元时使用普通 Agent 分支，不强行进入 long。 |
| [`planning-layer-runtime`](skills/planning-layer-runtime/SKILL.md) | 开发前梳理需求并产出已确认的规划交接。 | 不写生产代码，不执行测试。 |
| [`long-task-orchestrator`](skills/long-task-orchestrator/SKILL.md) | 根据已确认规划实现至少 4 个实现单元，执行自动化验证，并交接到 `ready_for_local_test`。 | 不负责人工验收和上线批准。 |
| [`testing-layer-runtime`](skills/testing-layer-runtime/SKILL.md) | 继承 long 的自动化证据，管理人工、设备、服务器、外部能力和最终验收。 | 不修改业务代码，不批准生产上线。 |
| [`ai-code-inspection`](skills/ai-code-inspection/SKILL.md) | 按 10 种真实工作场景路由改动检查、根因诊断、确认修复、完整性核查、审计、重构评估、合并检查、hotfix 和规范治理。 | 场景 1–9 单次完成；只有规范治理使用交互式七步。项目运行态位于 `.runtime/ai-code-inspection/`。它不是发布或安全门禁。 |

完整请求由 `dev-runtime` 动态发现已安装 Skill，并按以下链路分流：

```text
dev-runtime
  -> planning-layer-runtime
  -> 已确认规划交接
  -> planning_only：规划完成后停止
  -> execution_ready 且少于 4 个实现单元：普通 Agent 实现并执行项目验证
  -> execution_ready 且至少 4 个实现单元：
     long-task-orchestrator
     -> ready_for_local_test
     -> testing-layer-runtime
  -> 按实际请求选择可选的 ai-code-inspection 场景
  -> 目标项目自己的发布/安全流程
```

`ai-code-inspection` 是独立流程，可单独用于代码检查、根因诊断、确认修复、需求完整性核查、审计、重构评估、合并准备、hotfix 或规范治理。场景 1–9 使用 `single_run`；只有 `standards_compliance_correction` 使用交互式七步。

## 部署到 Agent 项目

不需要用户手动复制文件。只需让 Agent 同时拥有本仓库的读取权限和目标项目的写入权限，然后运行下方初始化 Prompt。

用户只需提供目标项目名称、本地路径或仓库地址，以及 Agent 平台和需要安装的 Skill。有足够权限时，Agent 会自行定位项目、完整复制所选 Skill 并完成适配，不要求用户手动搬运或编辑文件。

| Agent | 项目级 Skill 目录 | 项目指令文件 | 官方文档 |
| --- | --- | --- | --- |
| OpenAI Codex | `.agents/skills/<skill-name>/` | 根目录 `AGENTS.md` | [Codex Skills](https://developers.openai.com/codex/skills)、[AGENTS.md](https://developers.openai.com/codex/guides/agents-md) |
| Claude Code | `.claude/skills/<skill-name>/` | `CLAUDE.md`；用 `@AGENTS.md` 导入本仓库规则 | [Claude Code Skills](https://code.claude.com/docs/en/skills)、[CLAUDE.md 与 AGENTS.md](https://code.claude.com/docs/en/memory#agents-md) |
| GitHub Copilot | 与 Codex 共用时推荐 `.agents/skills/<skill-name>/`；也支持 `.github/skills/` 和 `.claude/skills/` | 根目录或就近的 `AGENTS.md` | [Copilot Agent Skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)、[仓库指令](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions) |

同时使用三种 Agent 时，Agent 自动生成的目标结构可以是：

```text
your-project/
├── AGENTS.md
├── CLAUDE.md                   # 仅 Claude Code 需要
├── .agents/skills/             # Codex + GitHub Copilot
│   ├── ai-code-inspection/
│   ├── dev-runtime/
│   ├── planning-layer-runtime/
│   ├── long-task-orchestrator/
│   └── testing-layer-runtime/
└── .claude/skills/             # Claude Code
    ├── ai-code-inspection/
    ├── dev-runtime/
    ├── planning-layer-runtime/
    ├── long-task-orchestrator/
    └── testing-layer-runtime/
```

Agent 只安装所选平台需要的目录。目标项目已有 `AGENTS.md` 或 `CLAUDE.md` 时，由 Agent 合并指令而不是覆盖；只安装部分 Skill 时，由 Agent 从安装后的 `AGENTS.md` 清单中移除未安装项。

使用完整生命周期时，需要同时安装 `dev-runtime` 和它动态发现的四个阶段 Skill。某个阶段 Skill 未安装时，`dev-runtime` 必须报告缺失依赖，不猜测路径，也不假装该阶段已经执行。

Claude Code 不会直接读取 `AGENTS.md`，因此 Agent 会创建或合并这个最小项目文件：

```markdown
# CLAUDE.md

@AGENTS.md
```

## 安装并初始化目标项目

在本 Skill 仓库中运行下面的 Prompt。整个安装与适配过程由 AI 完成，用户无需手动复制文件：

```text
请为以下目标项目安装并初始化 Runtime Skills：
- 目标项目：<必填，项目名称、本地路径或仓库地址>
- Agent 平台：<Codex / Claude Code / GitHub Copilot>
- 需要安装的 Skill：<一个或多个准确的 Skill 名称>

请完整负责本次初始化，不要要求我手动复制、粘贴或编辑安装文件。
根据我提供的项目名称或地址，在你有权限访问的工作区和仓库中搜索目标项目。只找到一个匹配的本地项目时直接继续；仅在找不到目标、存在多个匹配或权限不足时再询问我。
写入前自行确认来源是当前 Skill 仓库，目标是搜索到的目标项目。
从本仓库中只复制 skills/ 下已选择 Skill 的完整目录，并放入该 Agent 平台支持的项目级 Skill 目录。
将本仓库 AGENTS.md 中适用的路由与安全规则合并到目标项目的 AGENTS.md，绝不覆盖目标项目已有指令。使用 Claude Code 时，还要创建或合并 CLAUDE.md，使其导入 AGENTS.md。
不要复制本仓库的 README、src/、public/、package.json、package-lock.json、astro.config.mjs、tsconfig.json、.github/workflows/ 或任何其他文档站文件。
只扫描目标项目，列出已安装 Skill，并根据该项目的真实事实适配 Skill 自有的稳定环境档案或启动文件。
在对应 Skill 的进入条件满足前，不要创建任务或期次 Runtime 状态。
不要修改业务代码，不执行数据库迁移、部署、commit 或 push。
报告本次复制、合并和初始化的文件；识别出的组件、语言、框架、持久化方案、测试工具、CI workflow 和验证命令；以及仍未确认的事实。
```

AI 初始化只包括：定位指定目标、安装选中的 Skill 包、合并 Agent 入口指令，以及适配 Skill 自有的环境档案或启动文件。它不代表迁移本仓库，更不会把本仓库的文档站搬进目标项目。

## 开始使用

可以直接使用自然语言；支持显式调用的平台也可以直接点名 Skill。Codex 可通过 `/skills` 或 `$skill-name` 调用，Claude Code 使用 `/skill-name`，Copilot 根据请求和 Skill 描述自动选择。

```text
使用 dev-runtime，让这个完整开发请求通过已安装的 Runtime Skill 按门禁推进。

使用 planning-layer-runtime 规划这个功能，暂时不要实现。

使用 long-task-orchestrator 执行已经确认的规划交接。

使用 testing-layer-runtime 接管当前测试交接。

使用 ai-code-inspection 只读检查当前 Git 改动，并一次性反馈。

使用 ai-code-inspection 对当前项目做全量只读审计。
```

部署完成后，先让 Agent 列出当前加载的项目指令和已发现的 Skill。发现缺失时，检查目录名和完整 `SKILL.md` 路径；平台需要重新发现时，重启或新开一个 Agent 会话。

本仓库不提供生产发布批准或企业级安全验收，这些仍由目标项目自己的流程负责。

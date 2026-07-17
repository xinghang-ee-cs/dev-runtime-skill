# AI 开发全流程 Runtime Skills

[English](README.md) | [简体中文](README.zh-CN.md)

这是一套面向 Codex、与具体项目无关的开发 Skill，分别负责规划、实现、测试和日常代码检查。

其中三个 Skill 组成一条有明确交接点的开发流程：

```text
规划 -> 开发和自动化验证 -> 人工及真实环境测试
```

`ai-code-inspection` 是独立的代码检查流程，适合提交前或需要检查当前改动时单独使用。

本仓库不包含生产发布或安全放行 Skill。`testing-layer-runtime` 只负责整理发布移交材料，最终能不能上线，仍由目标项目自己的发布和安全流程决定。

## 包含哪些 Skill

| Skill | 什么时候用 | 不负责什么 |
|---|---|---|
| [`planning-layer-runtime`](skills/planning-layer-runtime/SKILL.md) | 功能还没有聊清楚，需要在写代码前确认需求、范围、架构、验收标准或产出规划文档。 | 写代码、执行测试、填写真实测试结果。 |
| [`long-task-orchestrator`](skills/long-task-orchestrator/SKILL.md) | 已经有确认过的规划交接，并且工作包含至少 4 个实现单元；或者测试反馈已经确认，需要按流程修复。 | 人工测试、真实设备测试、服务器验收、最终验收和上线放行。 |
| [`testing-layer-runtime`](skills/testing-layer-runtime/SKILL.md) | 开发已经到达 `ready_for_local_test`，需要继续做人工、设备、云端、外部能力或最终验收测试。 | 默认重跑 long 已经通过的自动化测试、修改业务代码或批准生产上线。 |
| [`ai-code-inspection`](skills/ai-code-inspection/SKILL.md) | 需要对已修改的前后端代码做日常检查，覆盖命名、质量、架构、测试、文档、注释和提交准备。 | 发布就绪检查、生产门禁或企业级安全验收。 |

## 整体流程怎么衔接

```text
planning-layer-runtime
  -> 已确认的规划交接
  -> long-task-orchestrator
  -> ready_for_local_test + 自动化测试证据
  -> testing-layer-runtime
  -> 发布/安全移交
  -> 目标项目自己的发布流程
```

几个容易混淆的边界：

- `ready_for_local_test` 只表示代码和要求的自动化验证已经完成并留下记录，不代表人工验收通过，更不代表可以上线。
- 测试层会继承 long 交接中有效的自动化结果，并记录为 `reused_from_long`，不会为了再拿一个“通过”而重复跑一遍。
- 规划层定义“需要证明什么”，long 负责写代码和跑自动化，testing 负责组织人工与真实环境证据。
- 代码检查先报告问题。发现可以修的内容后，需要用户再次输入 `继续`，才会修复并验证当前 Step。

## 部署到 Codex 项目

### 1. 复制 Skill

把完整的 `skills/` 目录复制到目标项目根目录。每个 Skill 下面的 `SKILL.md`、`references/`、`agents/` 和模板文件都要保留，不能只复制入口文件。

目标项目大致应该是这个结构：

```text
your-project/
  AGENTS.md
  skills/
    ai-code-inspection/
    planning-layer-runtime/
    long-task-orchestrator/
    testing-layer-runtime/
```

### 2. 填写目标项目自己的信息

首次使用 `ai-code-inspection` 前，要根据目标项目的真实框架、包管理器、数据库、常用命令和 CI 情况，填写 `skills/ai-code-inspection/project-environment-profile.md`。

不要从其他项目复制环境结论。规划 Skill 会在需要时为目标项目创建最小的 `.plan/` 启动文件；当前用户画像写在 `.plan/user-profile.yaml`，不再使用旧的 `runtime-user-profile.md` 模板作为入口。

### 3. 创建 `AGENTS.md`

在目标项目根目录创建 `AGENTS.md`。这是 Codex 长期读取的项目说明，用来告诉它这个仓库有哪些本地规则。仅仅复制 Skill 文件夹还不够；在这种可移植的目录结构里，需要通过 `AGENTS.md` 明确告诉 Codex：什么任务应该读哪个 Skill。

可以从下面这份模板开始：

```markdown
# Codex 项目说明

## 本地 Runtime Skills

执行任务前，先判断是否命中下面的本地 Skill。命中后，必须先完整读取对应的 `SKILL.md`，再按该文件的路由读取本次任务需要的 references。

- `skills/planning-layer-runtime/SKILL.md`
  - 用于开发前的需求访谈、范围和架构决策、验收设计及规划文档。
  - 不得在这个 Skill 中写代码、执行测试或填写真实测试结果。

- `skills/long-task-orchestrator/SKILL.md`
  - 用于承接已经确认的规划交接，完成至少包含 4 个实现单元的完整功能或模块；也用于承接已经确认的测试修复。
  - 负责实现、迁移、自动化测试代码、自动化执行、证据记录，以及到 `ready_for_local_test` 或 `ready_for_local_retest` 为止的交接。
  - 不负责人工验收、真实设备测试、服务器验收或上线放行。

- `skills/testing-layer-runtime/SKILL.md`
  - 用于 long 交接后的人工测试、真实设备测试、云端或服务器验证、外部能力验证、最终验收和发布移交。
  - 继承 long 中有效的自动化测试证据。除非符合 Skill 里的例外条件，否则不要重跑已经通过的自动化测试。
  - 不修改业务代码，也不批准生产上线。

- `skills/ai-code-inspection/SKILL.md`
  - 用于已修改前后端代码的日常检查和提交准备。
  - 必须先报告问题。用户再次输入 `继续` 后，才允许修复当前 Step 并执行验证。
  - 不得把它当成发布、生产或企业级安全门禁。

## 流程边界

- 正常顺序：planning -> long 开发 -> testing -> 项目自己的发布/安全流程。
- 同一时间只让一个 Skill 负责当前任务，除非当前 Skill 明确要求交接给下一个 Skill。
- `ready_for_local_test` 是开发交接状态，不是最终验收或上线批准。
- 项目事实、账号、服务器信息和运行证据只能写在目标项目自己的文件里，不能回写到通用 Skill 规则中。
- 保留无关的工作区改动。除非用户明确要求，否则不要暂存、提交、推送、部署或执行破坏性操作。
```

然后把目标项目自己的命令、环境事实来源、Git 规则和发布流程补充在这段内容下面。这些内容应该属于目标项目的 `AGENTS.md` 或项目文档，不应该写进这个通用 Skill 仓库。

### 4. 从目标项目启动 Codex

在 Codex 中打开目标项目，并明确说出当前要进入哪个阶段。例如：

```text
使用 planning-layer-runtime，先规划这个功能，不要开始实现。
使用 long-task-orchestrator，执行已经确认的规划交接。
使用 testing-layer-runtime，接管当前期次的测试。
使用 ai-code-inspection，只检查当前 Git 改动。
```

只要 `AGENTS.md` 的路由写得清楚，直接用自然语言描述任务也可以。但 Codex 仍然必须遵守 Skill 的进入条件。一句“开始开发”不能跳过规划确认、开发预检或测试交接。

### 5. 检查是否部署完整

确认目标项目中至少存在这些文件：

```text
AGENTS.md
skills/ai-code-inspection/SKILL.md
skills/planning-layer-runtime/SKILL.md
skills/long-task-orchestrator/SKILL.md
skills/testing-layer-runtime/SKILL.md
```

然后让 Codex 根据一个示例任务说明“应该使用哪个 Skill，为什么”。这样可以在正式开发前发现路径写错或 `AGENTS.md` 使用范围不清楚的问题。

## 适合什么项目

- 个人或小团队使用 Codex 完成多步骤开发任务。
- 希望规划、开发记录和人工验收证据都能追溯的项目。
- 涉及前端、后端、数据库、设备、云端或外部平台的功能。
- 希望在多个项目复用同一流程，又不想把某个项目的私有信息带过去的团队。

如果只是改几行代码，不需要规划和正式测试流程，直接用普通 Codex 指令即可，不必强行启动整套流程。

## 去项目化边界

本仓库只保存通用流程、模板和中性示例。不要写入：

- 真实姓名、邮箱、账号、token、密钥或内部身份。
- 客户名称、私有仓库路径、服务器地址或生产环境信息。
- 某个项目专属的技术结论、CI/CD 命令、迁移命令或运维事实。
- 某个项目专属的测试编号、页面名称、业务对象或审批流程。

这些事实应该写在目标项目自己的规划文档、runtime 输出、环境档案或 `AGENTS.md` 中。

## 兼容性

本仓库以 Codex 为主要使用环境，每个 `SKILL.md` 旁边都带有 `agents/openai.yaml` 元数据。其他 AI 编程工具如果支持加载 Markdown 规则，也可能复用这些内容，但具体如何发现和执行 Skill 取决于对应工具，本仓库不保证行为完全一致。

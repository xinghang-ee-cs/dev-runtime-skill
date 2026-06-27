# 前后端全流程开发

一套 AI 编程助手的技能集合，把软件开发拆成「规划 → 实现 → 测试」三个阶段，每个阶段由一个专门的 Skill 负责。你只需要说"开始开发"，AI 就会按流程走完核心生命周期。

完整、连贯、不跳步。

## 拿了这套东西能干嘛

从"做一个功能"到"上线"中间有很多步骤：需求对齐、写代码、跑测试、安全检查……很容易漏掉或者顺序搞乱，尤其用 AI 写代码的时候——它很会写，但不太会"想着整个流程走"。

这套技能把核心开发生命周期固化成 **3 个独立又衔接的 Skill**，像流水线一样依次执行：

```
聊需求、出规划  →  写代码、跑自动化测试  →  人工验收、设备验证
       │                    │                    │
       ▼                    ▼                    ▼
  规划层运行时         长任务编排器           测试层运行时
```

每个 Skill 只在自己该出场的时候触发，不越界、不重复。

---

## 四个核心 Skill 分别做什么

### 1. 规划层运行时 `planning-layer-runtime`

**一句话：帮你把"想做什么"聊清楚、写成文档。**

- 你说"开始第一期开发"，它会先确认你是谁、你关心什么
- 然后和你聊需求、范围、数据模型、权限、UI、验收标准
- 最后产出结构化的规划文档（存到 `docs/计划安排/` 下面）
- 只定义"要什么"，不涉及"怎么实现"

### 2. 长任务编排器 `long-task-orchestrator`

**一句话：根据规划文档，把代码写完、测试跑完。**

- 读取规划文档，拆解成一个个开发任务
- 按顺序实现代码、写数据迁移、写自动化测试
- 跑 vitest、jest、integration 等自动化测试
- 做完后输出 `ready_for_local_test` 信号，交接给测试层
- 如果测试发现 bug，还能回来修（patch runtime）

### 3. 测试层运行时 `testing-layer-runtime`

**一句话：接管测试，引导你完成人工验证。**

- 继承编排器跑过的自动化测试结果（不复跑）
- 规划测试顺序，引导你一步步做人工操作
- 覆盖真实设备验证、云端环境验证、外部能力验证

### 4. AI 代码检查 `ai-code-inspection`

**一句话：日常快速扫一遍代码，找找有没有明显问题。**

- 命名不规范、代码异味、分层乱了、缺测试、注释过期
- 分 7 个 Step 逐项检查，发现问题可以自动修复
- 适合每次提交前跑一遍，不上线也能用

---

## 整体流程

```
你: "开始第一期开发"
  → 规划层: 聊需求 → 出规划文档

你: "继续"
  → 编排器: 读规划 → 写代码 → 跑自动化测试 → ready_for_local_test

你: "继续"
  → 测试层: 继承自动化结果 → 引导人工验证 → 服务器验证

随时可用:
  → 代码检查: 扫一遍代码有没有问题
```

## 适用场景

- 用 AI 编程助手（Claude Code、Codex、Cline 等）做开发的个人或小团队
- 希望 AI 不只是"写代码"，而是按完整流程走
- 需要结构化规划文档、可追溯的测试记录
- 项目较复杂（前后端分离、有数据库、有外部平台集成）

## 不适用场景

- 只需要 AI 帮忙写几行代码，不需要完整流程
- 超大型企业级项目（这套 Skill 按小团队效率设计）
- 不需要规划文档、只想直接开干的场景

## 支持哪些 AI 编程工具

这套技能基于 **Claude Code 的 Skill 规范**编写（`SKILL.md` + `references/` 结构）。

- **Claude Code**：原生支持，直接放入 `skills/` 目录即可
- **其他支持自定义 Skill 的 AI 编程工具**：只要工具支持加载 Markdown 格式的技能描述，就可以适配。核心是 `SKILL.md` 中的规则文本，不依赖任何 Claude 私有 API

如果你的工具不支持 Skill 机制，可以把每个 Skill 的 `SKILL.md` 当作系统提示词（system prompt）直接喂给 AI，效果相同。

## 快速开始

1. 把 `skills/` 目录复制到你的项目根目录
2. 在你的 AI 编程工具的配置文件中添加技能引用
3. 说"开始开发"即可触发规划层

详见各 Skill 目录下的 `SKILL.md` 了解详细规则。

---

## English Summary

**fullstack-dev-runtime** is a collection of AI coding assistant skills that turn ad-hoc AI coding sessions into a disciplined, phase-gated development lifecycle — from planning to tested implementation.

### The Pipeline

```
Planning → Implementation → Testing
    │           │               │
    ▼           ▼               ▼
  Planning   Long-Task      Testing
  Layer      Orchestrator   Layer
```

### Four Core Skills

| Skill | Role |
|---|---|
| `planning-layer-runtime` | Conversational planning — turns vague ideas into structured specs (requirements, data model, permissions, UI, acceptance criteria) |
| `long-task-orchestrator` | Autonomous implementation — reads the plan, writes code, runs automated tests, and hands off at `ready_for_local_test` |
| `testing-layer-runtime` | Test lifecycle management — inherits automated results, orchestrates manual/device/server verification |
| `ai-code-inspection` | Quick code health check — catches naming issues, architecture drift, dead code, and missing tests in a structured 7-step pass |

### Why it exists

AI coding assistants are great at writing code but bad at "remembering the full process." This skill set enforces the discipline that gets a feature from idea to tested code: plan first, implement with tests, then validate with humans.

### Compatibility

Written against the **Claude Code Skill specification** (`SKILL.md` + `references/`). Works natively in Claude Code. Any AI coding tool that loads Markdown skill descriptions can use it — the core logic lives in plain-text rules, no vendor-specific APIs required.

---

这套技能是从真实项目的开发流程中打磨出来的，但 Skill 本身不绑定具体业务，可以复用于任何项目。

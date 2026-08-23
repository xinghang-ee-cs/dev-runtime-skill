---
title: 安装 Runtime Skills
description: 使用版本锁和同步工具，把 Runtime Skills 部署到一个或多个 Agent 平台。
sidebar:
  order: 1
---

## 准备条件

目标项目应当能被所选 Agent 打开，并允许在项目根目录维护 Agent 指令、Skill 目录和 `runtime-skills.lock.json`。执行安装的 Agent 还需要读取本仓库并运行 Python 3 标准库脚本。

## 1. 运行受管安装

不要手工复制整个 `skills/`。从本仓库运行同步工具，明确选择 Skill 和每个 Agent 平台的目标根目录：

```bash
python scripts/runtime-skills.py install \
  --release latest \
  --project /path/to/your-project \
  --skill planning-layer-runtime \
  --skill long-task-orchestrator \
  --destination .agents/skills \
  --destination .claude/skills
```

同步工具复制完整 Skill 包，不会漏掉 references、模板和 agent 元数据。多次提供 `--skill` 和 `--destination` 即可安装多个 Skill 和平台。

```text
your-project/
  AGENTS.md
  runtime-skills.lock.json
  .runtime-skills/
    runtime-skills.py
  .runtime/
    ai-code-inspection/        # 首次使用时按需初始化，不从其他项目复制
  .agents/skills/
    planning-layer-runtime/
    long-task-orchestrator/
  .claude/skills/
    planning-layer-runtime/
    long-task-orchestrator/
```

## 2. 添加项目路由

在目标项目的 `AGENTS.md` 中说明每个 Skill 的适用任务、进入条件和禁止边界。至少需要表达以下路由：

| 任务意图 | 应读取的入口 |
|---|---|
| 开发前的需求和方案规划 | 已安装的 `planning-layer-runtime/SKILL.md` |
| 执行已确认的完整开发任务 | 已安装的 `long-task-orchestrator/SKILL.md` |
| 人工、设备、云端和最终验收 | 已安装的 `testing-layer-runtime/SKILL.md` |
| 检查当前代码改动 | 已安装的 `ai-code-inspection/SKILL.md` |

项目自己的命令、账号边界、环境事实和发布流程应继续写在项目文档中，不要回填进通用 Skill。

## 3. 让首次运行发现项目事实

第一次运行 `ai-code-inspection` 时，Agent 从已安装的 `ai-code-inspection/assets/runtime-templates/` 初始化项目根目录 `.runtime/ai-code-inspection/`，再检查目标仓库的真实组件、语言、框架、包管理器、脚本、持久化、契约和 CI 配置，填写稳定环境事实。

只有无法从仓库可靠判断的信息才需要询问。不要从另一个项目复制环境结论。

## 4. 验证部署与版本

首先运行：

```bash
python .runtime-skills/runtime-skills.py verify --project .
```

确认锁文件、同步工具和所选 Skill 的完整路径存在，例如：

```text
AGENTS.md
runtime-skills.lock.json
.runtime-skills/runtime-skills.py
.agents/skills/planning-layer-runtime/SKILL.md
```

然后给 Codex 一个示例任务，让它只回答“应该使用哪个 Skill，以及为什么”。如果路由和边界正确，再进入真实任务。

每个新会话第一次使用 Runtime Skill 前运行 `sync`。新期次开始前同步并执行 `pin --reason <期次标识>`；期次关闭后执行 `unpin`。详细规则见[版本与更新机制](../../reference/versioning-and-updates/)。

## 下一步

继续阅读[选择正确的 Skill](../choosing-a-skill/)，了解四个入口之间的区别。

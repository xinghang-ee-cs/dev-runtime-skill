---
title: 安装 Runtime Skills
description: 把 Runtime Skills 完整部署到一个 Codex 项目中。
sidebar:
  order: 1
---

## 准备条件

目标项目应当能够被 Codex 打开，并允许在项目根目录维护 `AGENTS.md` 和 `skills/`。

## 1. 复制完整目录

复制仓库中的整个 `skills/` 目录。不要只复制入口 `SKILL.md`，因为运行时会按任务需要读取 references、模板和 agent 元数据。

```text
your-project/
  AGENTS.md
  .runtime/
    ai-code-inspection/        # 首次使用时按需初始化，不从其他项目复制
  skills/
    ai-code-inspection/
    planning-layer-runtime/
    long-task-orchestrator/
    testing-layer-runtime/
```

## 2. 添加项目路由

在目标项目的 `AGENTS.md` 中说明每个 Skill 的适用任务、进入条件和禁止边界。至少需要表达以下路由：

| 任务意图 | 应读取的入口 |
|---|---|
| 开发前的需求和方案规划 | `skills/planning-layer-runtime/SKILL.md` |
| 执行已确认的完整开发任务 | `skills/long-task-orchestrator/SKILL.md` |
| 人工、设备、云端和最终验收 | `skills/testing-layer-runtime/SKILL.md` |
| 检查当前代码改动 | `skills/ai-code-inspection/SKILL.md` |

项目自己的命令、账号边界、环境事实和发布流程应继续写在项目文档中，不要回填进通用 Skill。

## 3. 让首次运行发现项目事实

第一次运行 `ai-code-inspection` 时，Codex 从 `skills/ai-code-inspection/assets/runtime-templates/` 初始化项目根目录 `.runtime/ai-code-inspection/`，再检查目标仓库的真实组件、语言、框架、包管理器、脚本、持久化、契约和 CI 配置，填写稳定环境事实。

只有无法从仓库可靠判断的信息才需要询问。不要从另一个项目复制环境结论。

## 4. 验证部署

确认以下文件存在：

```text
AGENTS.md
skills/ai-code-inspection/SKILL.md
skills/ai-code-inspection/assets/runtime-templates/project-environment-profile.md
skills/ai-code-inspection/assets/runtime-templates/inspection-runtime-state.md
skills/planning-layer-runtime/SKILL.md
skills/long-task-orchestrator/SKILL.md
skills/testing-layer-runtime/SKILL.md
```

然后给 Codex 一个示例任务，让它只回答“应该使用哪个 Skill，以及为什么”。如果路由和边界正确，再进入真实任务。

## 下一步

继续阅读[选择正确的 Skill](../choosing-a-skill/)，了解四个入口之间的区别。

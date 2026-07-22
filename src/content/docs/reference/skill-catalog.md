---
title: Skill 目录
description: 四个 Runtime Skill 的用途、入口和规则源文件。
---

教程用于解释常见使用方式。实际执行必须先完整读取对应入口，再按照入口路由读取本次任务需要的 references。

## planning-layer-runtime

- 用途：开发前的需求访谈、范围确认、架构和验收设计。
- 入口：[`skills/planning-layer-runtime/SKILL.md`](https://github.com/xinghang-ee-cs/dev-runtime-skill/blob/main/skills/planning-layer-runtime/SKILL.md)
- 不负责：写业务代码、执行测试、填写真实测试结果。

## long-task-orchestrator

- 用途：执行已确认且包含至少 4 个实现单元的功能或模块。
- 入口：[`skills/long-task-orchestrator/SKILL.md`](https://github.com/xinghang-ee-cs/dev-runtime-skill/blob/main/skills/long-task-orchestrator/SKILL.md)
- 不负责：人工测试、真实设备验证、最终验收和上线批准。

## testing-layer-runtime

- 用途：long 交接后的人工、设备、云端、外部能力和最终验收测试。
- 入口：[`skills/testing-layer-runtime/SKILL.md`](https://github.com/xinghang-ee-cs/dev-runtime-skill/blob/main/skills/testing-layer-runtime/SKILL.md)
- 不负责：默认重跑 long 已通过的自动化、修改业务代码或批准上线。

## ai-code-inspection

- 用途：已修改前后端代码的日常检查和提交准备。
- 入口：[`skills/ai-code-inspection/SKILL.md`](https://github.com/xinghang-ee-cs/dev-runtime-skill/blob/main/skills/ai-code-inspection/SKILL.md)
- 不负责：发布就绪检查、生产门禁和企业级安全验收。

:::caution[规则优先级]
教程与 Skill 源文件不一致时，以当前版本的 `SKILL.md` 和它路由的 references 为准，并修订教程。
:::

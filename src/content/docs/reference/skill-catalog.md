---
title: Skill 目录
description: 五个 Runtime Skill 的用途、入口和规则源文件。
---

教程用于解释常见使用方式。实际执行必须先完整读取对应入口，再按照入口路由读取本次任务需要的 references。

## dev-runtime

- 用途：完整或模糊开发请求的统一阶段路由；先规划，再按真实 handoff、实现单元数量和当前任务意图切换实现、测试与代码检查。
- 入口：[`skills/dev-runtime/SKILL.md`](https://github.com/xinghang-ee-cs/dev-runtime-skill/blob/main/skills/dev-runtime/SKILL.md)
- 路径：运行时动态发现同级 Skill，不假设 `.agents/skills/`、`.claude/skills/` 或其他固定安装目录。
- 不负责：复制阶段规则、建立第二套 Runtime、处理单一阶段请求、批准发布或生产操作。

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

- 用途：按 10 种真实工作场景处理改动检查、根因诊断、确认修复与内部回归、需求完整性、业务规则、全项目审计、重构评估、合并准备、hotfix 和规范治理。
- 入口：[`skills/ai-code-inspection/SKILL.md`](https://github.com/xinghang-ee-cs/dev-runtime-skill/blob/main/skills/ai-code-inspection/SKILL.md)
- 运行态：首次使用时从 Skill 模板初始化到项目根目录 `.runtime/ai-code-inspection/`。
- 不负责：上线发布、生产门禁、企业级安全验收、无准入的猜测修复或大规模重构。

:::caution[规则优先级]
教程与 Skill 源文件不一致时，以当前版本的 `SKILL.md` 和它路由的 references 为准，并修订教程。
:::

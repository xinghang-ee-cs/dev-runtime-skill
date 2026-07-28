---
title: Skill 目录
description: 四个 Runtime Skill 的用途、入口和规则源文件。
---

教程用于解释常见使用方式。实际执行必须先完整读取对应入口，再按照入口路由读取本次任务需要的 references。

## planning-layer-runtime

- 用途：需求访谈、范围确认、架构和验收设计、Planning Execution Baseline 冻结、初始/增量 Handoff，以及 triage 准入后的精确规划重入。
- 入口：[`skills/planning-layer-runtime/SKILL.md`](https://github.com/xinghang-ee-cs/dev-runtime-skill/blob/main/skills/planning-layer-runtime/SKILL.md)
- 不负责：写业务代码、执行测试、填写真实测试结果。

## long-task-orchestrator

- 用途：校验初始/增量 Handoff revision，按增量执行队列实现已确认且包含至少 4 个实现单元的功能或模块，并保护未受影响和已完成事实。
- 入口：[`skills/long-task-orchestrator/SKILL.md`](https://github.com/xinghang-ee-cs/dev-runtime-skill/blob/main/skills/long-task-orchestrator/SKILL.md)
- 不负责：人工测试、真实设备验证、最终验收和上线批准。

## testing-layer-runtime

- 用途：核对并继承 long 交接后的自动化证据，管理人工、设备、云端、外部能力和最终验收测试，并对发现做 Execution/Test Change Triage。
- 运行态：所有期次状态、证据、队列和恢复数据写入项目绑定的 `<phase_testing_runtime_directory>`；根 `.runtime/` 不保存期次实例。
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

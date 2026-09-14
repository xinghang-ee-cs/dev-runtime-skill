---
title: Skill 目录
description: 四个 Runtime Skill 的用途、入口和规则源文件。
---

教程用于解释常见使用方式。实际执行必须先完整读取对应入口，再按照入口路由读取本次任务需要的 references。

## planning-layer-runtime

- 用途：需求访谈、范围确认、架构和验收设计、Planning Execution Baseline 冻结、初始/增量 Handoff、triage 准入后的精确规划重入，以及 Bugfix Case 的合同边界和最终基线更新。
- 入口：[`skills/planning-layer-runtime/SKILL.md`](https://github.com/xinghang-ee-cs/dev-runtime-skill/blob/main/skills/planning-layer-runtime/SKILL.md)
- 不负责：写业务代码、执行测试、填写真实测试结果。

## long-task-orchestrator

- 用途：校验初始/增量 Handoff revision 并实现至少 4 个单元的功能；或消费 `bugfix-case/v1` 完成不限单元数的精确补丁。
- 入口：[`skills/long-task-orchestrator/SKILL.md`](https://github.com/xinghang-ee-cs/dev-runtime-skill/blob/main/skills/long-task-orchestrator/SKILL.md)
- 不负责：人工测试、真实设备验证、最终验收和上线批准。

## testing-layer-runtime

- 用途：核对并继承 Long 自动化证据，管理期次验收；同时负责 Bugfix 定向验证、原 Bug 生产复验和上线后同类型问题验证。
- 运行态：所有期次状态、证据、队列和恢复数据写入项目绑定的 `<phase_testing_runtime_directory>`；根 `.runtime/` 不保存期次实例。
- 入口：[`skills/testing-layer-runtime/SKILL.md`](https://github.com/xinghang-ee-cs/dev-runtime-skill/blob/main/skills/testing-layer-runtime/SKILL.md)
- 不负责：默认重跑 long 已通过的自动化、修改业务代码或批准上线。

## ai-code-inspection

- 用途：按 10 种真实工作场景处理检查与诊断；在四 Skill 项目中为确认的实现缺陷创建 `bugfix-case/v1` 和 Bug Contract，再交给 Long。
- 入口：[`skills/ai-code-inspection/SKILL.md`](https://github.com/xinghang-ee-cs/dev-runtime-skill/blob/main/skills/ai-code-inspection/SKILL.md)
- 运行态：首次使用时从 Skill 模板初始化到项目根目录 `.runtime/ai-code-inspection/`。
- 不负责：上线发布、生产门禁、企业级安全验收、无准入的猜测修复或大规模重构。

:::caution[规则优先级]
教程与 Skill 源文件不一致时，以当前版本的 `SKILL.md` 和它路由的 references 为准，并修订教程。
:::

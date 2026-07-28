---
title: 完整开发流程
description: 从开发前规划推进到测试和发布移交的完整 Runtime Skill 工作流。
---

import { Steps } from '@astrojs/starlight/components';

这条流程适合需要明确规划、完整实现和真实环境验收的功能。小范围的几行修改不必强制启动整套运行时。

<Steps>

1. **确认规划意图**

   使用 `planning-layer-runtime` 理解业务目标、发现缺失信息，并逐步形成可确认的规划上下文和文档。

2. **形成执行交接**

   规划层定义实现范围、约束、风险和“需要证明什么”，冻结 Planning Execution Baseline，并生成带 `planning_baseline_revision` 和增量执行合同的交接。在用户确认前，不进入实现。

3. **执行实现与自动化验证**

   `long-task-orchestrator` 校验初始/增量 Handoff revision，只消费 `execute_only`、`resume_only`、`reexecute_affected_part`，保护 `context_only`、`completed_locked` 和 `cancelled`，再完成实现、迁移和自动化验证。

4. **到达开发交接状态**

   实现完成后形成 Long Testing Handoff，并将状态推进到 `ready_for_local_test`。这个状态不等于最终验收。

5. **组织人工和真实环境测试**

   `testing-layer-runtime` 核对 Planning/Long revision，继承有效自动化结果，再安排人工、真实设备、服务器、云端或外部能力验证。所有期次状态和证据写入绑定的 phase testing runtime，不写入根 `.runtime/`。

6. **整理发布移交材料**

   测试层汇总状态、证据和阻塞项，交给目标项目自己的发布和安全门禁。最终是否上线由目标项目决定。

</Steps>

## 交接链

```text
planning-layer-runtime
  -> confirmed planning handoff
  -> long-task-orchestrator
  -> ready_for_local_test + automated evidence
  -> testing-layer-runtime
  -> release/security handoff
  -> target project's release process
```

## 流程中断时

- 规划未确认：停留在规划层，不用一句“开始开发”绕过确认。
- 实现预检失败：报告阻塞项，不隐式打开 execution gate。
- 自动化失败：由 long 保留失败状态和证据，不交给 testing 掩盖。
- 人工测试发现偏差：先执行 Change Triage。实现缺陷交回 Long；测试缺陷留在 Testing；规划缺口、需求变化或合同级设计漂移重入 Planning。
- Planning 重入：追加 Change Set，只修订受影响合同并生成增量 Handoff；已完成和未受影响工作保持锁定或继续。
- 发布条件不满足：测试层记录阻塞并移交，不自行批准上线。

:::tip[保持单一负责人]
同一时间只让一个 Skill 负责当前阶段。跨阶段时通过明确交接切换负责人，而不是同时加载所有规则。
:::

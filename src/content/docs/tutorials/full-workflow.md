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

   规划层定义实现范围、约束、风险和“需要证明什么”。在用户确认前，不进入实现。

3. **执行实现与自动化验证**

   `long-task-orchestrator` 读取唯一的 Source of Truth，完成预检、实现、迁移以及项目要求的自动化测试，并记录验证证据。

4. **到达开发交接状态**

   实现完成后形成 Long Testing Handoff，并将状态推进到 `ready_for_local_test`。这个状态不等于最终验收。

5. **组织人工和真实环境测试**

   `testing-layer-runtime` 继承 long 的有效自动化结果，再安排人工、真实设备、服务器、云端或外部能力验证。

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
- 人工测试发现缺陷：确认反馈后交回 long 修复，再生成 `ready_for_local_retest` 交接。
- 发布条件不满足：测试层记录阻塞并移交，不自行批准上线。

:::tip[保持单一负责人]
同一时间只让一个 Skill 负责当前阶段。跨阶段时通过明确交接切换负责人，而不是同时加载所有规则。
:::

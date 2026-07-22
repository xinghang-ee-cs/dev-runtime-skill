---
title: 选择正确的 Skill
description: 根据任务阶段判断当前应该由哪个 Runtime Skill 负责。
sidebar:
  order: 2
---

同一个任务在不同阶段会由不同 Skill 接管。选择的关键不是任务规模本身，而是当前是否已有确认过的输入和可验证的交接。

## 快速判断

| 当前情况 | 使用 | 关键边界 |
|---|---|---|
| 需求、范围或验收方式还没有确认 | `planning-layer-runtime` | 只规划，不产生执行层产物 |
| 已有确认的规划交接，并且包含至少 4 个实现单元 | `long-task-orchestrator` | 实现和自动化验证截止到 `ready_for_local_test` |
| 已有 long 测试交接，需要人工或真实环境验证 | `testing-layer-runtime` | 默认继承已通过的自动化证据，不修改业务代码 |
| 需要检查当前代码改动 | `ai-code-inspection` | 先报告问题，获得新的 `继续` 后才修复当前 Step |

## 三个常见误区

### 把 `ready_for_local_test` 当成验收通过

这个状态只证明实现和要求的自动化验证已经完成并留下交接。人工测试、真实设备、服务器验证和发布批准仍未完成。

### 在测试层重复跑已通过的自动化

当 long 交接提供了有效状态和证据时，测试层应记录为 `reused_from_long`。只有环境变化、证据缺失、结果失败或过期等明确条件才能重新执行。

### 用代码检查代替发布门禁

`ai-code-inspection` 适合高频日常检查，不承担生产上线、安全验收或企业级 release gate。

## 示例

```text
使用 planning-layer-runtime，先规划这个功能，不要开始实现。
```

```text
使用 long-task-orchestrator，执行已经确认的规划交接。
```

```text
使用 testing-layer-runtime，接管当前期次的人工和真实环境测试。
```

```text
使用 ai-code-inspection，只检查当前 Git 改动。
```

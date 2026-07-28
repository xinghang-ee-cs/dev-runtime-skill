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
| 需求、范围或验收方式还没有确认，或 triage 判定合同需要变化 | `planning-layer-runtime` | 冻结/增量修订规划合同，不产生执行层产物 |
| 已有确认的初始或增量规划交接，并且包含至少 4 个实现单元 | `long-task-orchestrator` | 只消费允许执行的队列，截止到 `ready_for_local_test` |
| 已有 revision 一致的 long 测试交接，需要人工或真实环境验证 | `testing-layer-runtime` | 继承有效自动化证据，分类测试发现，不修改业务代码 |
| 需要检查、诊断、审计或受控修复代码 | `ai-code-inspection` | 按 10 种工作场景路由；场景 1–9 单次完成，只有规范治理交互执行七步 |

## 三个常见误区

### 把 `ready_for_local_test` 当成验收通过

这个状态只证明实现和要求的自动化验证已经完成并留下交接。人工测试、真实设备、服务器验证和发布批准仍未完成。

### 在测试层重复跑已通过的自动化

当 long 交接提供了有效状态和证据时，测试层应记录为 `reused_from_long`。只有环境变化、证据缺失、结果失败或过期等明确条件才能重新执行。

### 把所有测试发现都当成开发 Bug

实现偏离仍有效的合同才交回 Long 修复；测试资产错误留在 Testing；Planning 缺口、已接受的需求变化或改变正式合同的设计漂移必须重入 Planning，形成新的增量交接。分类只失效受影响范围，不默认重开整个期次。

### 用代码检查代替发布门禁

`ai-code-inspection` 适合高频日常检查、根因诊断、确认修复、完整性核查、审计、重构评估、合并检查、hotfix 和规范治理，不承担生产上线、安全验收或企业级 release gate。

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

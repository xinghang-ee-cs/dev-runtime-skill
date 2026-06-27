# 落地清单前置检查

本文件只定义 Preflight Gate：检查、停止条件、输出。

## 1. Preflight 用途

```text
confirm_source_of_truth
confirm_plan_readiness
confirm_capability_handoff
confirm_environment_baseline
confirm_task_generation_inputs
```

## 2. Step 1 检查清单

检查落地文档：

- 用户指定的计划、落地清单或实现清单可读。
- Source of Truth 已由 planning handoff 或用户确认，且只有一个当前有效路径。
- 默认 Source of Truth 为 planning handoff 指定的 `Development Landing Checklist`；不得通过文件编号猜测路径。
- 计划目录任务的上游文档存在、非占位、无阻塞待确认项。
- 清单包含用户旅程、验收步骤、端到端闭环、使用者视角验收、高风险流程和验证门禁。
- 清单中的任务必须可追溯到 planning 文档 ID，包括 REQ、MODULE、API、PERM、TEST、RISK；涉及外部能力时还必须包含 CAP-ID。
- 清单足以指导环境确认和任务生成。

检查 Capability Handoff：

- 若任务涉及外部能力、SDK、OpenAPI、MCP、AI Provider、基础设施依赖或第三方平台，必须存在并读取 planning handoff 指定的 `Capability Governance` 文档。
- Capability Registry 已登记相关 CAP-ID。
- 官方 SoT、SDK/API/OpenAPI/MCP 版本、鉴权、请求结构、响应结构、错误码来源已确认。
- Evidence Gate 已通过，或明确标注不适用。
- 最小真实调用验证已有证据，或在 planning 层标记为 BLOCKER 且不得执行 implementation。
- 降级策略和人工介入策略已定义。
- Mock 只能作为测试替身，不得作为生产真实能力验收证据。

## 3. Step 2 检查清单

检查项目环境：

- 项目结构、模块边界、路由、前后端拆分、legacy 边界已确认。
- 本地外部工具、数据库、Prisma、测试命令、开发/测试共享库、云端生产环境信息已确认。
- 当前工作区状态已确认。
- 不可回退的本地改动已确认。
- 清单对应的代码区域、已有实现、明显缺口和风险已确认。
- 涉及外部能力时，环境变量、网络要求、回调要求、额度限制、限流策略、计费规则已按 planning handoff 明确。

## 4. Step 3 检查清单

检查 task generation 输入：

- `delegation-rules.md` 可读。
- `task-state-machine.md` 可读。
- `context-lifecycle.md` 可读。
- `system-topology.md` 可读。
- Source of Truth 可派生 `task.md`。
- 执行单元可追溯到 Source of Truth。
- 执行顺序、依赖、所有权、共享边界、验证方式和完成证明具备生成依据。
- 涉及外部能力的执行单元必须带 CAP-ID、官方 SoT、SDK/API 版本、最小验证方式和降级策略。

## 5. 停止条件

```text
missing_source_of_truth -> STOP
upstream_plan_blocked -> STOP
plan_conflict -> STOP
missing_user_journey -> STOP
missing_acceptance_path -> STOP
missing_capability_registry -> STOP
capability_evidence_gate_blocked -> STOP
external_capability_version_unclear -> STOP
external_capability_auth_unclear -> STOP
external_capability_contract_unclear -> STOP
external_capability_real_validation_missing -> STOP
missing_environment_baseline -> STOP
unclear_ownership_boundary -> STOP
unclear_shared_boundary -> STOP
unreadable_required_reference -> STOP
```

## 6. 完成条件

```text
source_of_truth_confirmed
upstream_plan_ready
capability_handoff_passed_or_not_applicable
environment_baseline_confirmed
task_generation_inputs_ready
no_blocking_question
```

```text
preflight_not_passed -> execution_gate_closed
execution_gate_closed -> DO_NOT_IMPLEMENT
```

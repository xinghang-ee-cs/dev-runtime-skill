# Test Writeback

## 回写目标目录

`docs/计划安排/<当前期次>/testing-runtime/`

Testing Runtime 只写 Runtime 输出目录；不得修改 planning SoT 或业务产物。

## 必须维护的文件

- `test-runtime-state.md`：当前阶段、当前环境、总状态、阻塞项、最后更新时间。
- `test-execution-events.md`：测试阶段事件，不写长日志。
- `test-validation-results.md`：每个 `case_id` 的结果、环境、证据、是否阻塞。
- `test-evidence-index.md`：证据路径、截图路径、命令摘要、人工证据来源、long evidence 来源。
- `manual-test-queue.md`：待人工执行、待补证据、已确认/未确认的人工测试操作；不是 case 清单，而是用户实际操作队列。同一用户操作只能出现一次；多个 case 可以挂载到同一个操作项下。
- `test-execution-order.md`：测试顺序、依赖、阻塞关系。

## Long Testing Handoff 回写

读取 `testing-handoff.md` 或 `long-runtime-testing-summary.md` 后，必须记录：

```yaml
long_testing_handoff:
  source:
  verified:
  automated_passed:
  automated_failed:
  automated_skipped:
  manual_required:
  coverage:
```

继承结果写法：

```yaml
result: reused_from_long
source: long testing handoff
evidence: <long evidence ref>
rerun_required: false
```

## test-execution-order.md 格式

```yaml
TEST-001:
  depends_on: []
  status: reused_from_long

TEST-002:
  depends_on:
    - TEST-001
  status: pending_manual

TEST-003:
  depends_on:
    - TEST-002
  status: blocked_by_dependency
```

规则：

- `depends_on` 全部通过后，当前测试才能执行。
- `reused_from_long` 视为通过。
- 前置失败时当前测试必须写 `blocked_by_dependency`，不得执行。
- 前置被用户移出当前范围时，当前测试可继续，但必须记录 `dependency_deferred_out_of_scope`。

## manual-test-queue.md 推荐格式

```yaml
MANUAL-OP-001:
  operation_signature: system_admin|admin-maintenance-config|project-exists|create-or-stop-region|test-domain
  user_facing_operation: 打开配置页，创建/停用区域并确认列表状态
  depends_on:
    - TEST-P7-CONFIG-001
  blocked_by: []
  user_guidance:
    role_or_account: 系统管理员账号
    entry: 后台维护配置页
    precondition: 项目已存在，当前使用测试数据
    steps:
      - 打开维护配置页
      - 创建或停用一个区域
      - 返回列表查看区域状态和团队绑定状态
    observe:
      - 区域列表可见
      - 停用状态可见
      - 团队绑定可见
    feedback_hint: 可以自然反馈“列表状态正常”“停用状态没显示”或直接发截图
  covers:
    - TEST-P7-REGION-001
    - TEST-P7-TEAM-001
    - TEST-P7-PERM-001
  evidence_need:
    - region list visible
    - stopped state visible
    - team binding visible
  status: pending_manual

TEST-P7-PERM-001:
  covered_by:
    - MANUAL-OP-001
  evidence_reuse: true
  status: verified_by_user_report
```

字段含义：

- `depends_on`：当前人工操作执行前必须已经通过或完成的 case、manual operation 或环境前置项。
- `blocked_by`：当前人工操作无法执行时的阻塞项；无阻塞时为空数组。
- 当 `depends_on` 未通过或 `blocked_by` 非空时，AI 不得引导用户执行该人工操作。
- 当 `depends_on` 全部通过、`blocked_by` 为空、`status` 未验证且未被 `evidence_reuse` 覆盖时，AI 可以选择该操作作为下一个人工测试操作。
- `user_guidance` 只用于 AI 生成用户态引导，不要求用户填写。它必须帮助非专业用户知道下一步怎么做。

## 状态枚举

常用状态：

- `reused_from_long`
- `pending_manual`
- `pending_real_device`
- `pending_server`
- `pending_release_handoff`
- `verified`
- `verified_by_user_report`
- `blocked`
- `blocked_by_dependency`
- `evidence_insufficient`
- `deferred`
- `deferred_to_p2`

## 回写时机

- Long Testing Handoff 读取后。
- Test Intake Gate 完成后。
- Test Planning Phase 完成后。
- `test-execution-order.md` 生成或更新后。
- 继承 long 自动化结果后。
- 每个人工测试操作发起后。
- 每次人工证据回传后。
- 每个服务器验证阶段开始/结束后。
- Release Handoff 前。
- 最终报告输出前。

## 禁止项

- 禁止只在对话中报告，不写 Runtime 文档。
- 禁止把测试结果写回规划 SoT。
- 禁止把截图或日志当成唯一通过证据。
- 禁止 append 巨长日志。
- 禁止多个文件重复定义同一测试状态。
- 禁止重新执行 long 已通过且证据完整的自动化测试。
- 禁止把同一 operation_signature 拆成多个重复人工测试操作。
- 禁止因不同 case_id 而要求用户重复已经验证过的完整操作流程。
- 禁止人工测试引导只写测试任务名称，不写具体操作步骤。
- 禁止完成一个人工测试后，在仍存在可执行下一项时不主动引导。
- 禁止在 `manual-test-queue.md` 中生成无法判断依赖状态的人工操作项。

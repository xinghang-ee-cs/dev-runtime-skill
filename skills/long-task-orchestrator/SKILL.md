---
name: long-task-orchestrator
description: 执行已确认的 Planning handoff 或 `bugfix-case/v1`，完成实现、必要的自动化验证、结果记录和交接。用于功能、模块、重构、数据迁移和精确补丁；负责交付可供本地测试或 Bug 验证的结果，不负责规划合同、人工或云端测试、最终验收或上线。
---

# long-task-orchestrator

## 安装与启动边界

- 用户只要求安装/更新时，只运行安装工具、诊断和校验，报告后停止；不启动业务访谈、全项目调研或其他 Skill，不预建四套 Runtime。
- 项目级安装是默认方式。先根据平台实际发现路径检查同名全局/祖先/项目副本；不能只看锁文件，也不能假设项目副本覆盖全局副本。冲突先诊断，禁止通过再复制一份解决。
- 目标项目有 `runtime-skills.lock.json` 时，本会话首次使用前运行 `python .runtime-skills/runtime-skills.py doctor --project .`。同名副本/不可完整检查/摘要漂移必须解决；`instruction_review` 只报告旧指令待人工审阅，不自动删除或改写。
- 恢复已有活动期次时，先本地 `verify`；未锁定时先执行 `pin --reason <已有期次标识>`，再 `sync`，禁止先升级。新期次则先 `sync`，通过后在创建第一份期次状态前 `pin --reason <期次标识>`。Planning → Long → Testing 使用同一锁；仅期次已关闭或用户明确批准受控迁移后执行 `unpin`。三个命令均通过 `python .runtime-skills/runtime-skills.py <命令> --project .` 调用。
- 同一会话且锁未变化时不重复同步。工具缺失、漂移或旧版工具缺少新命令时，先报告受管安装待修复；不要绕过锁、自动重装或修改期次状态。无受管锁时先识别来源，由用户选择受管安装；不要默默增设项目副本。
- 不为安装、首次使用、恢复或初始化新建 `AGENTS.md`/`CLAUDE.md`。已有等价路由不重复写；项目特定事实只保留在项目中。

## 有界读取协议

本入口是启动路由。原入口的完整规则在 `references/runtime-governance.md`；它与其明确引用的专题文件保留所有合同、门禁和边界。先选模式/阶段，再读取当前阶段必要规则，禁止预读其他三项 Skill、整套 references、全部历史或完整治理文件。

从项目根运行以下命令，将 `<skill>` 替换为本入口 frontmatter 的名称：

```bash
python .runtime-skills/runtime-skills.py context --project . --skill <skill> --file references/runtime-governance.md --outline
python .runtime-skills/runtime-skills.py context --project . --skill <skill> --file <当前规则路径> --outline
python .runtime-skills/runtime-skills.py context --project . --skill <skill> --file <当前规则路径> --section <节编号>
```

- `--section` 使用 outline 返回的编号，只返回该标题下到下一标题之前的文字；子标题是独立节，必须按当前 gate 的适用性继续选择。有 `next_offset` 时用相同参数加 `--offset <next_offset>` 续读，`done` 前不得宣称该节完整。
- 每次规则正文最多输出 6000 字符；首次路由只读本入口和必要的当前节，静态规则目标上限 12000 字符。实际 token 消耗取决于客户端和模型；这不是整个会话的 token 保证。
- 不得因节选省略适用门禁。执行、状态变更或交接前加载该动作所需的全部章节及子节；超出首轮预算时明确加载原因，按当前 gate 分段补齐，不转为整文件读取。
- 已读且内容/锁未变的节不重复读取。压缩恢复先读取项目紧凑检查点和当前状态，再补缺失规则；历史事件只按证据引用读取。
- 脚本是可执行工具，不把脚本源码、模板全集、原始日志或批量扫描结果注入上下文。未知事实只检查与当前任务直接相关的 manifest、入口及配置。

## 当前模式路由

| 当前任务 | 按需读取的章节来源 |
| --- | --- |
| 接收交接 | `runtime-governance.md` 的用途/Runtime Gate；`00-runtime-priority-rules.md`；`landing-checklist-preflight.md` 的启动顺序和 Planning Handoff Intake |
| 首次 Bootstrap | Intake 通过后读取 `context-lifecycle.md` 的目录所有权、首次 Bootstrap，以及当前状态文件的字段章节；未通过不得建 Runtime |
| 已有执行恢复 | `context-lifecycle.md` 的恢复一致性；只读取当前 Context、Checkpoint、Handoff、Baseline、TASK；Events 按证据引用定位 |
| 当前实现单元 | `task-state-machine.md`、`task-execution.md`、`system-topology.md` 的适用状态/合同/承接规则 |
| 整期验证与交接 | `validation-gates.md`、`validation-results.md` 的当前 Matrix、机器执行证据、完成条件和 Handoff 格式 |
| UI/UX 或依赖变化 | 适用时读取 `frontend-experience-execution.md` 或 Preflight 的依赖治理章节 |
| `bugfix-case/v1` | 直接选择 `bugfix-patch-runtime.md`；不套用完整期次 Bootstrap 或至少四个单元要求 |

路径相对于 `references/`。首轮先核对交接模式与真实输入；无有效 Handoff/Case 时只报告缺项，不扫描整个项目、不读完整 Kernel 集合。

## 不可跳过的完成条件

`execution_prerequisite_readiness` 必须明确 `before_long_status: passed` 与 `unresolved_before_long: []`。合同、revision、承接位置和权限未确认时不得实现；不复制 DEP 配置正文或秘密。

以“本期”为唯一正式闭环；当前 TASK 的检查不替代整期验证。交接前必须满足 `required_validation_matrix_current_and_complete`、`all_required_automated_validation_passed`、`local_runnable_gate_passed`，使用 `scripts/run-long-validation.sh` 或 `.ps1` 产生并对账 machine execution receipt，通过 readiness validator 后才能输出 ready。任何 failed/blocked/not_run 不得伪装通过。自动化验证属于 Long；人工、真机、云端、最终验收和发布不属于 Long。

---
name: testing-layer-runtime
description: 通用测试治理 Skill。用于在 Long 交接后管理期次验收，或验证 `bugfix-case/v1` 的原 Bug、受影响路径、相邻风险、生产复验和上线后同类型问题。负责测试证据与 Case 收尾，不负责业务实现、规划合同或直接发布。
---

# testing-layer-runtime

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
| 接收 Long 交接 | `runtime-governance.md` 路径绑定/准入；`01-test-runtime-core.md` 的 Long readiness 与测试规划门禁 |
| 开始或继续当前测试项 | `01-test-runtime-core.md` 当前步骤；`02-test-environment-gates.md` 适用环境；`03-evidence-format.md` 当前证据格式 |
| 回写结果与闭环 finding | `05-test-writeback.md` 的当前状态、测试项检查点、结果及失败回流章节 |
| 服务器/破坏性测试 | 触发前读取 `04-destructive-boundaries.md`；没有精确授权不得执行 |
| 发布后复验与恢复 | `runtime-governance.md` 当前门禁；01/05 的部署身份和云端证据章节，不读取全部历史 |
| `bugfix-case/v1` | 直接读取 `06-bugfix-verification.md` 当前阶段；只测原 Bug、受影响与相邻风险，不建立整期 Test Plan |

路径相对于 `references/`。首次路由只判断期次或 Case，以及当前 next_required_action；缺少有效交接时报告缺项，不预读全部测试规则或重新执行 Long 自动化。

## 不可跳过的验证边界

接收 Long 的 `required_validation_gate.result` 必须为 `passed`，且绑定当前有效的 machine execution receipt 与 revision；历史 ready/pass 声明不算证据。每个正式 `item_type` 必须有绑定版本/环境的持久检查点；状态只向前推进，finding 必须复测关闭。

复用 Long 已完成且仍有效的自动化，不无理由重跑。测试合同只消费实际 Handoff 路径，不猜测编号；UI/UX 仅消费精确 revision。Testing 不修改业务代码、不补规划合同、不直接发布。

Bugfix 的 `deployed` 或 `original_bug_production_verified` 不代表闭环；`awaiting_similar_defect_verification` 时突出提醒并恢复同类型问题验证。原 00–15 保持只读，新问题建立新 Case。只有所有必要证据、生产复验和同类型验证完成才关闭 Case/Issue。

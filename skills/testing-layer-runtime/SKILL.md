---
name: testing-layer-runtime
description: 通用测试治理 Skill。用于在 Long 交接后管理期次验收，或验证 `bugfix-case/v1` 的原 Bug、受影响路径、相邻风险、生产复验和上线后同类型问题。负责测试证据与 Case 收尾，不负责业务实现、规划合同或直接发布。
---

# testing-layer-runtime

## 安装与启动边界

- 静态规则默认安装到当前 Agent 的用户全局入口，项目只保存 `runtime-skills.lock.json`、项目事实和 Runtime。不得再向项目复制同名 Skill。导入平台使用生成的自包含包。
- 从版本路由返回的 `skill-root` 解析本入口及相对资源；将返回的 `runtime-tool` 绝对路径作为下文 `<runtime-tool>`，将用户选定的真实项目根作为 `<project-root>`。直接使用源码时先按仓库 INSTALL.md 完成全局安装；不能猜测 cwd 就是规则目录。
- 本会话首次使用先运行 doctor 诊断已知发现目录与旧指令，再运行 `python "<runtime-tool>" verify --project "<project-root>"`。缺失缓存、同名发现冲突、摘要漂移必须先解决，不回退默认最新版。`sync` 在全局模式只校验；升级全局默认不改变已绑定项目，采用新版需在期次外显式 `adopt --allow patch|minor|major`。
- 恢复活动期次时先 verify，再为尚未锁定的已有期次运行 `pin --reason <期次标识>`；新期次在第一份期次状态前 pin。Planning → Long → Testing 保持同一项目锁；仅期次关闭或用户批准受控迁移后 unpin。命令统一用 `python "<runtime-tool>" <命令> --project "<project-root>"`。不得覆盖其他活动期次的 pin。
- 从旧 schema 1 项目副本进入时，以锁登记的 tool.path 和当前 destinations 解析工具/规则目录，继续原 verify/context/pin/unpin 流程；不运行 session/adopt 隐式迁移。
- 旧项目级安装不自动复制或删除，关闭期次、验证无漂移后才显式迁移；工具不自动清理用户指令。不为安装、初始化或恢复新建 AGENTS.md/CLAUDE.md，不重复写路由。
- 只要求安装/更新时，诊断校验后停止；不启动业务访谈、全项目调研或其他 Skill，不预建四套 Runtime。真实任务只初始化当前必要状态，项目记忆禁止写入全局规则/导入目录。

## 有界读取协议

本入口是启动路由。原入口的完整规则在 `references/runtime-governance.md`；它与其明确引用的专题文件保留所有合同、门禁和边界。先选模式/阶段，再读取当前阶段必要规则，禁止预读其他三项 Skill、整套 references、全部历史或完整治理文件。

使用解析得到的工具运行以下命令，将 `<skill>` 替换为本入口 frontmatter 的名称：

```bash
python "<runtime-tool>" context --project "<project-root>" --skill <skill> --file references/runtime-governance.md --outline
python "<runtime-tool>" context --project "<project-root>" --skill <skill> --file <当前规则路径> --outline
python "<runtime-tool>" context --project "<project-root>" --skill <skill> --file <当前规则路径> --section <节编号>
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

---
name: planning-layer-runtime
description: 交互式规划运行时。用于核实项目事实、创建和维护开发规划、Planning Context、需求与变更合同及 Long Handoff，并处理范围准入、设计漂移和 Bugfix 增量治理。负责规划与交接边界，不负责业务实现、测试执行、验收或发布。
---

# planning-layer-runtime

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
| 首次需求访谈 | 本入口与 `discovery-entry.md` 的首轮最小合同；意图边界读取 09，首次首问前不扩展到完整 00/01/04/07 |
| 保存当前访谈检查点 | 首问使用 `discovery-entry.md` 列明的最小字段；后续反馈和复杂字段才读取 04 的对应格式 |
| 已有项目或后续期次 | `01-planning-core-rules.md` 当前基线/需求池；`07-planning-conversation-runtime.md` 当前状态门禁和需求池相关性检查 |
| 生成/确认当前文档 | `03-planning-doc-responsibility.md` 对应文档；`04-planning-format-spec.md` 对应格式；`10-planning-document-interaction-runtime.md` 当前交互步骤 |
| 数据库、UI/UX、外部能力 | 仅适用时加载 `13-planning-database-persistence-contract.md`、`11-planning-ui-ux-execution-contract.md`、`06-planning-capability-governance.md` 的当前合同章节；示例 12 不默认加载 |
| 冻结与交接 | `07-planning-conversation-runtime.md` 的 Baseline/Handoff/Gate，及 `10-planning-document-interaction-runtime.md` 的最终确认 |
| 变更/恢复/关闭 | 分别读取 02、08 或 01/07 的适用章节；已确认实现缺陷走 14，不重新规划 |

表中路径均相对于 `references/`。每次用户输入先应用 `09-execution-intent-guard.md` 的意图边界；实现意图转向执行层，不在 Planning 写业务代码。

首轮只复用已知项目事实，提出当前最关键的一个业务问题，逐轮保存并回读 `discovery_checkpoint`；不要把安装或环境扫描变成访谈主体。仅在当前动作真实需要时创建最小项目文件。不得预建全部档案或生成整期文档。文档模式、正式交接、恢复和关闭的进入条件以对应章节为准，未通过不得跳过。

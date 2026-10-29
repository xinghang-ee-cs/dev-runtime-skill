---
name: ai-code-inspection
description: 通用代码检查与诊断 Skill。用于审查当前改动、定位已确认问题、需求与规则核查、全项目审计、重构风险评估、合并准备和规范检查，并为确认的实现缺陷建立 `bugfix-case/v1`。负责检查与 Bug 合同，不负责规划、业务实现、发布、生产门禁或严格安全验收。
---

# ai-code-inspection

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

## 当前场景路由

先根据完整用户意图，在 `references/runtime-governance.md` 的“10 个用户场景”表和当前场景章节中确定场景、范围及权限；随后只读该场景的准入/停止/报告规则，不加载其他场景正文。

| 用户目标 | 场景与当前规则 |
| --- | --- |
| 检查当前改动 | `changed_code_review`；适用 Step，不扩大为全项目 |
| 定位具体异常 | `targeted_diagnosis`；Step 2 为主，先只读取证 |
| 已确认修复/hotfix | `confirmed_bugfix` / `hotfix_patch_review`；先准入与精确 editable_scope，再适用 Step 2/4/7 |
| 需求完整性/规则缺口 | `implementation_completeness_review` / `incremental_design`；需求来源、矩阵与行为边界 |
| 全项目现状/重构风险 | `full_readonly_audit` / `refactor_risk_assessment`；前者只读 Step 1–7，后者只读影响链 |
| 合并准备 | `merge_readiness_review`；Step 7，不授予 Git 写权限 |
| 按规范检查或矫正 | `standards_compliance_correction`；只加载当前 Step，按批次确认与执行，不把“继续”解释为授权 |

项目级 `.runtime/ai-code-inspection/` 只按当前范围需要初始化。环境档案先读最小已知事实，未知字段保留未确认；不为局部问题全面调研每个组件。Runtime 不能积累跨运行聊天。

适用 Step 与技术栈 Profile 按 `runtime-governance.md` 的路由读取；无匹配 Profile 不猜测。修复请求在同次诊断补齐准入后自动返回精确修复；证据不足只报告。采用四 Skill 交付链时，已确认实现缺陷读取 `references/bugfix-fast-lane.md`，建立持久 Case 并交给 Long，不在检查层实现。

任何修改都需核对精确 diff、全部适用验证和授权边界；只读诊断不创建修改授权，不自行提交、部署、执行真实数据库操作或清理用户文件。最终报告后撤销临时权限并重置本次 Runtime。

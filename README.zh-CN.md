# AI 开发全流程 Runtime Skills

[English](README.md) | [简体中文](README.zh-CN.md)

用于项目规划、实现、验收和代码诊断的四项独立 Skill。版本事实只来自 `skills-manifest.json`，目标项目的实际安装事实只来自 `runtime-skills.lock.json`。文档站的 `package.json` 不代表 Skill 版本。

## 快速安装

把下列请求发给正在目标项目中工作的 Agent：

```text
请从 https://github.com/xinghang-ee-cs/dev-runtime-skill 为当前项目安装 Runtime Skills。
需要安装：planning-layer-runtime、long-task-orchestrator、testing-layer-runtime、ai-code-inspection。
只完成安装，不开始开发规划、业务访谈或全项目环境初始化。

确认目标项目根目录和当前实际使用的平台。默认只安装当前平台：Codex 使用 .agents/skills；Claude Code 使用 .claude/skills；Copilot 复用项目实际支持的目录。只有我明确要求多平台，或当前任务明确需要这些平台时，才提供多个 --destination；旧平台目录存在本身不代表还在使用。不要安装到用户全局目录。
把来源 Release 下载到平台不会发现 Skill 的临时目录，不把来源仓库放进目标项目的 Skill 搜索范围，不复制来源 AGENTS.md、README、文档站或 CI。
使用可信来源工具运行 doctor --project "<项目根目录>"，新项目用重复的 --skill 指定上述名称。检查已知项目、Git 祖先和用户级同名副本；嵌套或额外发现目录需按当前平台配置单独确认。存在同名冲突、漂移或无法完整检查时停止并报告路径；不自动删除旧副本。历史过大的入口文件只报告，不改写。
没有冲突时运行：
python scripts/runtime-skills.py install --release latest --project "<项目根目录>" --skill planning-layer-runtime --skill long-task-orchestrator --skill testing-layer-runtime --skill ai-code-inspection --destination "<当前平台目录>"
已有锁文件时先 verify/status/diff。新增平台目录必须明确使用 --add-destination；变更位置使用 relocate，不通过重装累加。遇到次/主版本更新或本地修改时展示差异并等待确认，不绕过活动期次 pin。
安装不创建 AGENTS.md/CLAUDE.md，不预建 Runtime，不扫描业务源码。运行项目内工具 verify，报告 Release、版本、安装位置、诊断与校验结果，然后停止。不要修改业务代码、部署、提交或推送。
```

只需要部分 Skill 时删去不需要的名称。工具只管理项目级安装，拒绝把 Home 或 Codex 用户根目录当作目标项目。已有个人/全局 Skill 由对应平台管理；不能把全局和项目两份同名正文同时作为事实源。

## 四个入口与首次使用

| Skill | 任务 | 边界 |
| --- | --- | --- |
| [planning-layer-runtime](skills/planning-layer-runtime/SKILL.md) | 需求发现、规划、合同及 Handoff | 不写业务实现或测试执行事实 |
| [long-task-orchestrator](skills/long-task-orchestrator/SKILL.md) | 执行已确认 Handoff 或 Bugfix Case，整期自动化验证 | 不代替人工/真机/云端验收或发布 |
| [testing-layer-runtime](skills/testing-layer-runtime/SKILL.md) | 期次验收、Bugfix 和发布后复验 | 不修改业务代码，不直接发布 |
| [ai-code-inspection](skills/ai-code-inspection/SKILL.md) | 代码检查、诊断及持久 Bug Contract | 只读范围不等于修改授权 |

安装完成后再单独发出业务请求，例如：

```text
使用 planning-layer-runtime 开始本期需求访谈，只处理当前阶段。
```

Agent 只加载选中的一个入口，按任务补齐最少项目事实。完整治理条款保存在各 Skill 的 `references/runtime-governance.md` 和原有专题文件中，按章节与阶段消费；不在首轮读取完整治理文件、全部 references、四个 Skill 或历史日志。普通链路为 Planning → 已确认 Handoff → Long → Testing → 项目发布流程。合同仍有效的已确认实现缺陷使用 Bugfix Case，不重开原 00–15；原 Bug 生产复验与同类型问题验证完成前不关闭 Case。

## 安装、重复运行与迁移

```bash
python scripts/runtime-skills.py doctor --project /path/to/project --skill planning-layer-runtime
python scripts/runtime-skills.py install --release latest --project /path/to/project --skill planning-layer-runtime --destination .agents/skills
python /path/to/project/.runtime-skills/runtime-skills.py verify --project /path/to/project
```

相同版本和目标重复安装不重写 Skill 或锁文件。安装只复制所选 Skill 完整包、项目内同步工具和锁文件，不初始化业务环境。若需要增加第二个实际使用的平台：

```bash
python scripts/runtime-skills.py install --release latest --project /path/to/project --skill planning-layer-runtime --destination .claude/skills --add-destination
```

每个新目标都检查未受管内容，即使已有锁文件也不能静默覆盖。确认采用发布内容后才使用 `--overwrite-local-changes`；该选项不能绕过全局/项目同名冲突。

将现有受管副本移动到另一个位置：

```bash
python .runtime-skills/runtime-skills.py relocate --project . --skill planning-layer-runtime --from .agents/skills --to .claude/skills
```

`relocate` 在无漂移、无活动 pin、目标不存在时更新同一锁文件，将旧副本归档到 `.runtime-skills/retired/`，并移除旧发现路径；事务失败会恢复原位置。它不升级版本、不移动项目 Runtime，也不自动处理未受管或全局副本。只有明确要求移动时才调用；不能以归档代替用户对本地修改的决定。

## 历史安装诊断

`doctor` 只读取有限的已知发现目录、Skill 元数据和入口文件大小，不递归扫描业务源码或输出指令全文。它报告：未登记同名副本、受管摘要漂移、无法完整检查的目录、超过 12 KB 的入口文件和重复路由标记。后两项是人工审阅提示，不证明文件一定有错，也不自动删除。平台额外配置的目录、嵌套 monorepo Skill 需额外检查；诊断通过不等于整台电脑不存在其他副本。

已有入口文件只在确需时复用最多一个不超过 10 个非空行、1200 字符的标记块；内容相同不写入。没有入口文件时不要新建。同步与 pin/unpin 已包含在每个分发 Skill 的入口，不依赖 AGENTS.md。

## 同步与活动期次

每个会话首次使用前运行 doctor。新期次：sync → pin → 建立期次。恢复已有活动期次：verify → 缺失时先 pin 原期次 → sync（仅验证，不升级）。同一会话锁未变化不重复同步。期次已关闭，或用户明确批准受控迁移后才 unpin。

```bash
python .runtime-skills/runtime-skills.py sync --project .
python .runtime-skills/runtime-skills.py pin --project . --reason phase-01
# 期次关闭后：
python .runtime-skills/runtime-skills.py unpin --project .
```

sync 只自动应用兼容 PATCH；MINOR/MAJOR 需要明确确认。稳定来源使用 `--release latest`，维护者验证未发布代码才用 `--source`。更新前查看 `status --check-remote` 和 `diff`；文件包更新不意味着要扫描全部历史期次、迁移 Runtime 或重跑全部验证。只有明确的 Runtime/schema 迁移任务才进入相应 recovery 与 validator，已关闭历史保持只读。

## 有界规则读取

```bash
python .runtime-skills/runtime-skills.py context --project . --skill planning-layer-runtime --file references/07-planning-conversation-runtime.md --outline
python .runtime-skills/runtime-skills.py context --project . --skill planning-layer-runtime --file references/07-planning-conversation-runtime.md --section 1
```

每次正文最多 6000 字符；`next_offset` 表示还有内容，必须用同样参数加 `--offset` 续读到 `done` 才算读完该节。子标题是独立节，按当前 gate 选择必要子节，不因分页跳过门禁。入口与首轮必要节的静态规则目标为 12000 字符，后续按当前阶段补齐并说明扩展原因。此限制不是整个会话 token 保证；项目资料、工具输出和客户端自动注入仍需控制。相同且已读的规则不重复读，恢复以紧凑 checkpoint 和当前状态为先。

## 验证与文档

```bash
python scripts/validate-skill-manifest.py
python -m unittest discover -s tests -p 'test_*.py'
```

完整教程在 `src/content/docs/`。`package*.json`、`src/`、`public/` 和文档站配置仅供构建文档，不属于安装包。所有 GitHub 变更遵循本仓库 AGENTS.md 的 Issue → 专用分支 → PR → CI → PR 合并流程；这些维护规则不复制到用户项目。

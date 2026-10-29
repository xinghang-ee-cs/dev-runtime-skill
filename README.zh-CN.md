# Runtime Skills

一套源码，生成各 Agent 的安装包与平台导入包。静态规则放在用户全局，项目事实、进度、检查点和版本锁留在项目中。四项 Skill 分别负责规划、实现、验收与代码诊断。

把下面的请求发给你正在使用的 AI：

> 阅读 https://github.com/xinghang-ee-cs/dev-runtime-skill/blob/main/INSTALL.md ，为当前 Agent 安装最新稳定版 Runtime Skills。明确当前平台后只安装对应的用户全局包，先检查已有同名副本；不向项目复制 Skill，不创建 AGENTS.md，不开始业务初始化。若稳定版尚无安装产物，报告缺口，不改用 main 冒充稳定版。

本次变更合并发布前，新的正式安装链接尚不可用。维护者可在仓库中验证源码：

```bash
python scripts/runtime-skills.py install-agent --source . --agent codex --project /path/to/project
```

正式发布后下载 [install.py](https://github.com/xinghang-ee-cs/dev-runtime-skill/releases/latest/download/install.py)，审阅并执行：

```bash
python install.py --agent codex --project /path/to/project
# 可替换为 claude、copilot 或 dsh；重复 --skill 名称可只装选中项
```

`auto` 只在 RUNTIME_SKILLS_AGENT 已指定或 PATH 上只有一个支持的 CLI 时自动选择。AI 知道当前平台时应显式传参。目录存在不代表当前使用，不能据此安装全部平台。

| 平台 | 默认安装/导入方式 |
| --- | --- |
| Codex、GitHub Copilot | 用户 `~/.agents/skills`，共用一个版本路由 |
| DeepSeek Harness（dsh） | 共用 `~/.agents/skills`；DSH_AGENTS_HOME 覆盖共享根 |
| Claude Code | 用户 `~/.claude/skills` |
| 豆包工作 | 下载 `runtime-skills-doubao-<skill>.zip`，通过应用支持的上传技能入口逐个导入 |
| WorkBuddy | 下载 `runtime-skills-workbuddy-<skill>.zip`，通过“添加技能 → 上传技能”逐个导入 |

豆包/WorkBuddy 包包含自己的工具和规则，市场元数据在构建时生成。市场上架需另行使用官方开发平台及审核；本仓库不会代替账号入驻或上传审核。没有已验证的其他 Agent 路径时不猜测安装。

首次实际任务由全局入口执行 session，在真实项目中创建精确版本锁。它返回当前项目的 skill-root 和 runtime-tool，资源按前者解析，工具用后者绝对路径执行。全局缓存为 `~/.runtime-skills/bundles/<sha256>`，不会被当作另一个发现目录；RUNTIME_SKILLS_HOME 可覆盖缓存位置。项目不需要静态 Skill 副本或同步工具。

| Skill | 职责 |
| --- | --- |
| planning-layer-runtime | 需求访谈、规划、基线及开发交接 |
| long-task-orchestrator | 按合同实现并保存执行进度 |
| testing-layer-runtime | 验收、Bugfix 复验及同类问题检查 |
| ai-code-inspection | 代码检查、根因诊断与 Bugfix Case |

安装结束就停止，不扫描业务、不预建四套 Runtime。真实任务只加载所需 Skill 和当前阶段。正文读取用 context 的 outline/section/offset，单次最多 6000 字符；不代表整个会话的 token 保证。

更新全局默认不会改变已绑定项目。全局模式的 sync 只验证；已有期次先 verify、再 pin 原期次；新期次在写第一份状态前 pin。期次完成后 unpin，再用 adopt --allow patch|minor|major 显式接受新默认。旧缓存不自动回收。缺失/漂移的精确缓存必须恢复，不能回退 latest。换机器需要相同的源包/缓存；旧补丁 Tag 可能被归档，应保留精确源包。

旧项目级锁与命令保持兼容，但不再是推荐入口。迁移先关闭期次并 verify，显式 bind --migrate-project --allow major，受管旧副本归档到 `.runtime-skills/retired/`，项目记忆不移动。无版本副本与用户指令只诊断、不自动删除或覆盖。完整安装合同见 [INSTALL.md](INSTALL.md)。

维护者构建：

```bash
python scripts/build-install-packages.py --output /tmp/runtime-packages
python -m unittest discover -s tests -p 'test_*.py'
python scripts/validate-skill-manifest.py
```

产物含四种原生安装 ZIP、八个独立导入 ZIP、install.py、INSTALL.md、install-manifest.json 和 SHA256SUMS。只维护 skills/ 源码与 distribution/ 平台元数据，不维护生成包的第二套提示词。CI 保存可审阅产物；正式 Release 仅由 PR 合并后的既有发布流程生成。

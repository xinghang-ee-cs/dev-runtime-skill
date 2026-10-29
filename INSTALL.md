# Runtime Skills — AI 安装入口

本页是给 AI 和用户的安装合同。只维护仓库 `skills/` 一套源代码；安装器与导入包均从它生成。最低环境 Python 3.10+，并具有当前用户目录和真实项目目录的读写权限。平台是否授予工具权限由平台决定。

1. 识别当前实际运行的 Agent。明确是 Codex、Claude Code、GitHub Copilot 或 DeepSeek Harness（dsh）时，显式传入对应 `--agent codex|claude|copilot|dsh`。不要仅凭目录存在就给全部平台安装。`auto` 只接受 RUNTIME_SKILLS_AGENT，或 PATH 上唯一一个支持的 CLI；无法唯一识别则询问当前平台，停止写入。
2. 下载稳定 Release 附件中的 `install.py`，审阅后用 Python 执行。它下载对应安装包并验证 SHA256SUMS。不要把远程文本直接通过管道执行，不从 main ZIP 冒充稳定版本。安装器及本页在本次变更合并、发布后才成为正式下载入口：
   - https://github.com/xinghang-ee-cs/dev-runtime-skill/releases/latest/download/install.py
   - https://github.com/xinghang-ee-cs/dev-runtime-skill/releases/latest/download/INSTALL.md
   - https://github.com/xinghang-ee-cs/dev-runtime-skill/releases/latest/download/install-manifest.json
3. 运行 `python install.py --agent <当前平台> --project "<已有项目绝对路径>"`；可重复 `--skill <名称>` 只安装选中项，省略则安装四项。安装是用户级，不在项目复制 Skill、不创建 AGENTS.md/CLAUDE.md、不初始化业务或 Runtime。项目参数仅用于冲突检查。
4. Codex/Copilot/dsh 默认共用 `~/.agents/skills`，Claude Code 使用 `~/.claude/skills`。dsh 设置 DSH_AGENTS_HOME 时使用该目录下的 skills；DSH_HOME/skills 中已有同名副本需先处理。平台额外 customSkillDirs、插件或企业托管目录由使用者显式检查。不要虚构其他 Agent 的默认目录。
5. 首次真实任务通过已加载 Skill 的 session 命令绑定项目精确版本。静态源码缓存于 `~/.runtime-skills/bundles/<sha256>`，不在 Agent 的发现目录下；RUNTIME_SKILLS_HOME 可指定同用途的用户缓存位置。项目只新增版本锁；事实、进度和检查点仍在项目，初始化按当前 Skill 的阶段执行。
6. 旧项目级安装会阻止同名全局安装。关闭活动期次、verify 无漂移后，先准备全局缓存（在不受旧项目影响的目录安装），然后运行全局路由工具 `bind --project "<项目>" --migrate-project --allow major`。它验证旧锁，把受管旧副本和工具归档到项目 `.runtime-skills/retired/`，事务性切换锁。未受管副本与指令文件只报告，不自动删除。
7. 更新全局默认不更改旧项目锁，不清理历史缓存。sync 只校验。项目在关闭期次后用 `adopt --allow patch|minor|major` 显式采用新默认。缺失精确缓存必须用 `restore-cache --source <精确源码>` 恢复；不回退 latest。换机器时安装完全一致的 Release 源码/导入包，缺失旧公开 Tag 时需使用保留的精确源包，不能只靠版本号重建不同摘要。

豆包工作与 WorkBuddy 不使用猜测的本地路径。下载 `runtime-skills-doubao-<skill>.zip` 或 `runtime-skills-workbuddy-<skill>.zip`，在应用支持的“添加/上传技能”入口逐个导入。每包只有一个顶层 Skill，携带运行工具和对应规则。首次使用需要平台提供 Python、持久项目目录和文件权限；不满足时应报告受限，不能伪造运行结果。导入权限/市场审核依产品账号而定，不通过本安装器绕过。正式商店发布由维护者在官方开发平台完成。

维护者验证未发布源码：`python scripts/runtime-skills.py install-agent --source . --agent <平台>`。
生成分发包：`python scripts/build-install-packages.py --output <产物目录>`。

平台适配依据（本地文件路径与导入规范）：

- Codex: https://learn.chatgpt.com/docs/build-skills
- Claude Code: https://code.claude.com/docs/en/skills
- Copilot: https://code.visualstudio.com/docs/agent-customization/agent-skills
- dsh: https://deepseek-harness.github.io/deepseek-harness/en/reference/subsystems/skills
- WorkBuddy: https://open.workbuddy.cn/docs/skill
- 豆包工作伙伴: https://aily.feishu.cn/hc/1u7kleqg_zja0qy5v

豆包独立工作端是否具备相同上传能力，以客户端当前入口为准；不把工作伙伴的公开发布后台等同于独立端。

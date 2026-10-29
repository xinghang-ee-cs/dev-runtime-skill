---
title: 安装 Runtime Skills
description: 一套源码生成用户全局安装包与平台导入包，项目只保留版本锁和记忆。
sidebar:
  order: 1
---

## 安装入口

让 AI 阅读仓库 [INSTALL.md](https://github.com/xinghang-ee-cs/dev-runtime-skill/blob/main/INSTALL.md)，识别当前 Agent 并安装对应的稳定用户包。不要向项目重复复制 Skill。正式下载入口在本次变更发布后提供：

```bash
python install.py --agent codex --project /path/to/project
```

支持 codex、claude、copilot、dsh（DeepSeek Harness）。AI 已知平台时显式传参；auto 只接受 RUNTIME_SKILLS_AGENT 或 PATH 上唯一支持的 CLI，多平台不猜测。安装器下载对应 ZIP 并检查 SHA256SUMS；不要直接管道执行远程脚本。

| 平台 | 位置或导入方式 |
| --- | --- |
| Codex/Copilot/dsh | 用户 ~/.agents/skills 共用薄路由；dsh 支持 DSH_AGENTS_HOME |
| Claude Code | 用户 ~/.claude/skills |
| 豆包工作/WorkBuddy | 分别下载 doubao/workbuddy 的每个 Skill ZIP，通过官方上传入口导入 |

导入包自带工具与规范规则，需要 Python 3.10+、文件读写权限和持久项目目录。没有能力时报告限制，不模拟运行。市场审核另行进行；不猜测应用安装路径。

## 首次真实任务

安装不扫描业务、不初始化 Runtime、不创建 AGENTS.md/CLAUDE.md。真实任务只选一个 Skill，通过其 session 命令绑定项目锁。它返回精确规则目录 skill-root 和工具路径 runtime-tool；相对资源按 skill-root 解析，事实、检查点、进度仍在项目。

默认缓存 ~/.runtime-skills/bundles/<sha256>，与 Agent 发现入口分开。项目只维护 runtime-skills.lock.json 及真实项目状态。全局默认升级不改变已绑定项目；缺失精确缓存时停止，不能回退最新。

规则使用 context --outline/--section/--offset 按阶段读取，每次最多 6000 字符。选中 gate 的全部必要子节必须读完，但不提前整读其他阶段。详见[版本与更新机制](../../reference/versioning-and-updates/)。

## 旧项目迁移

旧 schema 1 项目锁和命令保持兼容。关闭活动期次并 verify 后，显式 bind --migrate-project --allow major；受管 Skill 和旧工具归档到项目 .runtime-skills/retired，记忆不动。先在旧项目发现范围外安装全局包准备缓存，再迁移旧项目。未受管副本及用户指令不自动清理。

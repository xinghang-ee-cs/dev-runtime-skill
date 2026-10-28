---
title: 安装 Runtime Skills
description: 使用版本锁和同步工具，把 Runtime Skills 部署到一个或多个 Agent 平台。
sidebar:
  order: 1
---

## 准备条件

目标项目应当能被所选 Agent 打开，并允许在项目根目录维护 Skill 目录和 `runtime-skills.lock.json`。已有 Agent 指令文件时可以更新；没有时不需要为了安装 Runtime Skills 创建 `AGENTS.md`。执行安装的 Agent 还需要读取本仓库并运行 Python 3 标准库脚本。

## 1. 先诊断，再运行项目级安装

不要手工复制整个 `skills/`，不要同时部署到用户全局和项目。默认只选择当前实际使用的平台；只有明确需要多平台时才提供多个目录。把来源仓库放在发现范围外的临时目录，先执行 `python scripts/runtime-skills.py doctor --project /path/to/your-project --skill planning-layer-runtime`；同名副本/漂移/无法完整检查时先报告并解决，不自动删除。然后从本仓库运行：

```bash
python scripts/runtime-skills.py install \
  --release latest \
  --project /path/to/your-project \
  --skill planning-layer-runtime \
  --skill long-task-orchestrator \
  --destination .agents/skills
```

同步工具复制所选完整包、项目内同步工具和锁文件，不初始化业务。相同版本和位置重复安装不写文件。已有安装新增平台位置必须用 `--add-destination`；移动位置使用 `relocate --from <旧根目录> --to <新根目录> --skill <名称>`，旧副本归档到发现范围外并更新锁。每个新目标的未受管内容始终需要明确审阅，不能因为已有锁而覆盖。

```text
your-project/
  runtime-skills.lock.json
  .runtime-skills/
    runtime-skills.py
  .agents/skills/
    planning-layer-runtime/
    long-task-orchestrator/
```

## 2. 复用已有项目路由

如果目标项目已有 `AGENTS.md`、`CLAUDE.md` 或其他入口文件，先复用已有等价路由；确实缺失时，只在当前平台实际读取的一个文件中维护 `<!-- runtime-skills:begin -->` 与 `<!-- runtime-skills:end -->` 短块，最多 10 个非空行、1200 字符。原位置更新，内容相同则不写入；不要复制本仓库完整 `AGENTS.md`，不要按 Skill 或安装目录重复创建入口。没有入口文件时直接使用 Skill 的目录和描述，安装、更新、首次使用和 Runtime 初始化都不自动创建 `AGENTS.md` 或 `CLAUDE.md`。路由只需表达以下内容：

| 任务意图 | 应读取的入口 |
|---|---|
| 开发前的需求和方案规划 | 已安装的 `planning-layer-runtime/SKILL.md` |
| 执行已确认的完整开发任务 | 已安装的 `long-task-orchestrator/SKILL.md` |
| 人工、设备、云端和最终验收 | 已安装的 `testing-layer-runtime/SKILL.md` |
| 检查当前代码改动 | 已安装的 `ai-code-inspection/SKILL.md` |

项目自己的命令、账号边界、环境事实和发布流程应继续写在项目文档中，不要回填进通用 Skill。

## 3. 安装后停止，真实任务按需初始化

安装阶段不扫描业务源码、不访谈、不创建四套 Runtime。另行发出实际业务任务后，只加载一个选中的 SKILL.md，按当前范围补齐缺失的项目事实；已知事实复用，未涉及组件不调研。初始化 ai-code-inspection 时只从未填写模板创建当前职责必要的项目文件，不复制其他项目事实。

规则通过 `context --skill <名称> --file <规则路径> --outline` 定位，使用 `--section <编号>` 分段读取；每次正文最多 6000 字符，`next_offset` 未到 done 则必须续读该节。子标题独立编号，适用 gate 的全部章节必须补齐；禁止预读其他阶段、完整治理大文件或所有 references。各入口独立包含同步与 pin 生命周期，不依赖项目指令文件。

## 4. 验证部署与版本

首先运行：

```bash
python .runtime-skills/runtime-skills.py verify --project .
```

确认锁文件、同步工具和所选 Skill 的完整路径存在，例如：

```text
runtime-skills.lock.json
.runtime-skills/runtime-skills.py
.agents/skills/planning-layer-runtime/SKILL.md
```

然后给 Codex 一个示例任务，让它只回答“应该使用哪个 Skill，以及为什么”。如果路由和边界正确，再进入真实任务。

每个新会话首次使用前运行 doctor；新期次先 sync 后 pin，再建立状态。已有活动期次先 verify，缺 pin 时先 pin 原期次，再 sync（仅校验），不能先升级；期次关闭或明确批准受控迁移后才 unpin。详细规则见[版本与更新机制](../../reference/versioning-and-updates/)。

## 下一步

继续阅读[选择正确的 Skill](../choosing-a-skill/)，了解四个入口之间的区别。

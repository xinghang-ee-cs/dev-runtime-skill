---
title: 版本与更新机制
description: Runtime Skills 的版本事实、安装锁、使用前同步、期次锁定和发布规则。
sidebar:
  order: 2
---

## 单一事实源

| 文件或对象 | 职责 | 禁止承担的职责 |
|---|---|---|
| `skills-manifest.json` | 当前仓库 Release 版本、同步工具版本、每个 Skill 的独立版本和路径 | 不记录某个目标项目装了什么 |
| GitHub tag / Release | 固定一组仓库快照和人类可读更新记录；由 Release 的预发布标记区分验证版与稳定版 | 不表示目标项目已经升级 |
| 目标项目 `runtime-skills.lock.json` | 记录实际安装 Release、commit、Skill 版本、全部目标位置和内容摘要 | 不定义最新版本 |
| README 和教程 | 解释安装、更新与版本规则 | 不保存当前版本数字 |
| `SKILL.md` | Skill 的触发条件、工作流和边界 | 不增加 `version` frontmatter |

`package.json` 只属于 Astro/Starlight 文档站，它的版本不得用于判断 Skill 新旧。

## 安装

从本仓库执行：

```bash
python scripts/runtime-skills.py install \
  --release latest \
  --project /path/to/project \
  --skill planning-layer-runtime \
  --destination .agents/skills
```

默认只为当前实际使用的平台安装。明确需要同时支持 Claude Code 时，新安装再传入 `--destination .claude/skills`；已有安装必须加 `--add-destination`。位置移动使用 `relocate`，旧副本归档而非继续暴露在发现目录中。所有副本写入同一个锁文件；后续更新始终把已安装 Skill 作为一个 Release 快照共同处理，不允许只更新其中一个平台副本。

`--release latest` 是普通用户的稳定入口，只解析 GitHub 标记为稳定的最新 Release，不会选中预发布或 Draft 版本。当前稳定版本以 GitHub 最新公开稳定 Release 为准，可通过 `latest` 获取。维护者需要验证尚未发布的本地内容时，才使用 `--source /path/to/dev-runtime-skill`，此时锁文件会记录实际分支和 commit，而不会伪装成 Release。

### 迁移已有的无版本副本

任何目标目录已存在且未登记到锁文件时，`install` 都不会直接覆盖，包括已有锁文件后新增的目标位置。工具会列出发布版相对旧副本将新增、修改和删除的文件。用户确认愿意采用发布版后，再运行同一安装命令并增加：

```bash
--overwrite-local-changes
```

工具随后统一替换所有目标副本、安装项目内同步入口并生成锁文件，不创建或改写 `AGENTS.md`、`CLAUDE.md`。Agent 复用已有等价路由；确实缺失时只在当前平台实际读取的一个已有指令文件中维护最多 10 个非空行、1200 字符的 `<!-- runtime-skills:begin -->` / `<!-- runtime-skills:end -->` 短块，原位置更新且相同内容不写入。不复制本仓库的完整入口规则，不重复创建、追加或覆盖项目原文；没有指令文件时，不为安装或更新自动创建。

## 使用前同步

目标项目中的入口为：

```bash
python .runtime-skills/runtime-skills.py sync --project .
```

每个 Agent 会话首次使用前先运行 doctor 检查已知同名副本及历史指令；同步工具只读取有限元数据，不扫描业务代码。新期次首次使用时执行一次 sync。恢复已有活动期次时先 verify，缺失 pin 时先 pin 原期次，再执行 sync（仅校验），避免先升级后发现期次仍活动。同一会话中，锁文件没有变化时不重复执行。

`sync` 的判断顺序：

1. 校验登记目录和工具摘要，并检查已知项目、Git 祖先及用户发现根中的未登记同名副本；额外或嵌套目录按平台配置单独确认。
2. 如果存在本地修改或平台间漂移，停止覆盖。
3. 如果存在活动期次锁定，只验证当前版本，不远端更新。
4. 查询最新稳定 GitHub Release。
5. 自动安装兼容的补丁版本。
6. 次版本或主版本只报告变化，等待明确确认。
7. 更新成功后一次性替换全部受管副本和锁文件。

远端不可用时，已安装副本全部通过本地校验即可继续使用锁定版本，但 Agent 必须说明没有完成最新版本检查。

## 活动期次锁定

Planning、Long 和 Testing 会共同消费带 revision 的合同与 Runtime 状态。中途升级可能让新规则解释旧状态，因此新期次应先同步，再锁定：

```bash
python .runtime-skills/runtime-skills.py sync --project .
python .runtime-skills/runtime-skills.py pin --project . --reason phase-01
```

保持该锁直到期次关闭：

```bash
python .runtime-skills/runtime-skills.py unpin --project .
```

如必须中途迁移，先让用户确认，再解除锁定、查看差异、升级，并重新验证受影响的 Planning Baseline、Handoff 和 Runtime 状态。

## 手动检查和升级

```bash
# 只校验本地副本
python .runtime-skills/runtime-skills.py verify --project .

# 校验并检查最新 Release
python .runtime-skills/runtime-skills.py status --project . --check-remote

# 列出即将新增、修改和删除的文件
python .runtime-skills/runtime-skills.py diff --project . --release latest

# 明确接受次版本更新
python .runtime-skills/runtime-skills.py update --project . --release latest --allow minor

# 明确接受主版本更新
python .runtime-skills/runtime-skills.py update --project . --release latest --allow major
```

检测到本地修改时，先执行 `diff`。只有用户明确决定放弃本地修改后，才可使用 `--overwrite-local-changes`；不得由 Agent 自行推断。

常用返回码：

| 返回码 | 含义 |
|---|---|
| `0` | 本地版本可用；也可能是远端暂时不可用但本地校验通过 |
| `1` | 命令参数、版本门禁、期次锁定或来源校验失败 |
| `2` | 检测到文件缺失、本地修改或多平台副本漂移 |
| `10` | 检测到更新，但需要用户确认次版本或主版本变化 |

## 版本升级口径

| 级别 | 适用变化 |
|---|---|
| PATCH | 表达修正、缺陷修复，以及不改变持久化结构、输出合同、门禁或交接兼容性的调整 |
| MINOR | 向后兼容的新能力、新可选字段或新工作流分支 |
| MAJOR | Runtime 文件结构、状态枚举、门禁、安装布局或跨 Skill 交接合同的破坏性变化 |

每次修改 `skills/<name>/`，必须同时提升清单中该 Skill 的版本和仓库 `release_version`。修改同步工具时必须提升工具版本和 `release_version`。CI 会阻止内容已变化但对应版本未提升的 PR。

修订版本是同一 `主版本.次版本` 系列中的直接替代版本：用户侧 `sync` 检测到兼容的 PATCH 变化后自动更新。GitHub 只向用户公开每个系列最新的 PATCH Release 和 Tag；新的修订版本成功发布后，工作流把同系列旧 Release 转为 Draft 以保留记录，并删除其公开 Tag。主版本或次版本变化时保留旧系列，使不同系列可以并存并用于梯度灰度。

## 发布

1. 修改受影响的 Skill 或同步工具版本，并同步提升 `release_version`。
2. 通过清单校验和同步工具测试。
3. 合并发布变更到 `main`。
4. Release workflow 重新校验 `main`，自动创建与 `skills-manifest.json` 中 `release_version` 一致的 tag。
5. workflow 根据清单中的 `repository.channel` 创建稳定版或预发布版 GitHub Release，并生成 Release Notes；Release 已存在时，工作流仍会校正其预发布标记。
6. 新 Release 成功发布后，workflow 把同一 `主版本.次版本` 系列中更旧的 Release 转为 Draft，并删除其公开 Tag；不同系列不受影响。

不需要维护者在终端手工推送 tag。缺失 Release 时，可以在 GitHub Actions 中手动运行 `Release Runtime Skills` workflow；它仍以最新 `main` 和清单版本为准。

稳定 Release 是普通用户的使用入口。预发布 Release 只供显式指定版本的验证者使用，不会被 `latest` 自动选中。Draft 仅保留维护记录，不提供给普通用户，同系列旧 PATCH 的公开 Tag 被删除后也不能再用于安装或回退；需要灰度保留时应提升 MINOR 或 MAJOR。`main` 可以包含尚未发布的下一版内容，但目标项目的自动同步只消费公开的 GitHub Release，不直接追随移动的 `main`。

## 安装与上下文诊断

`doctor --project . --json` 只报告路径、问题和大小，不输出指令全文、不删除或改写用户文件。超过 12 KB 或含重复路由块的指令是人工审阅提示，不等于文件损坏；副本冲突/无法完整检查会阻断安装与同步。`verify` 证明登记内容一致并未发现已知范围冲突，不证明整台电脑不存在额外副本。

安装不启动业务初始化，文件包升级也不自动迁移 Runtime、扫描全部期次或重跑验证。真正的 schema 迁移需明确任务范围并遵循受控恢复，历史关闭期次保持不变。

四个 SKILL.md 是精简启动路由，完整原治理在各自 references/runtime-governance.md。`context --skill <名称> --file <路径> --outline` 返回章节索引；按 --section/--offset 加载最多 6000 字符正文。子标题是独立节；当前 gate 所需父节、子节和分页读完后才能动作。首轮静态规则目标 12000 字符，其余阶段有理由扩展；不是整个会话的 token 保证。

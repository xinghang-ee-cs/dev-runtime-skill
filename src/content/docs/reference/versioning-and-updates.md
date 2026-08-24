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
| GitHub tag / Release | 固定一组经过验证的仓库快照和人类可读更新记录 | 不表示目标项目已经升级 |
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

需要同时支持 Claude Code 时，再传入 `--destination .claude/skills`。所有副本写入同一个锁文件；后续更新始终把已安装 Skill 作为一个 Release 快照共同处理，不允许只更新其中一个平台副本。

`--release latest` 是普通用户的稳定入口。维护者需要验证尚未发布的本地内容时，才使用 `--source /path/to/dev-runtime-skill`，此时锁文件会记录实际分支和 commit，而不会伪装成 Release。

### 迁移已有的无版本副本

目标目录已经存在但没有 `runtime-skills.lock.json` 时，首次 `install` 不会直接覆盖。工具会列出发布版相对旧副本将新增、修改和删除的文件。用户确认愿意采用发布版后，再运行同一安装命令并增加：

```bash
--overwrite-local-changes
```

工具随后统一替换所有目标副本、安装项目内同步入口并生成锁文件。目标项目原有 `AGENTS.md` 或 `CLAUDE.md` 仍由 Agent 合并适用规则，不能整体覆盖。

## 使用前同步

目标项目中的入口为：

```bash
python .runtime-skills/runtime-skills.py sync --project .
```

每个 Agent 会话第一次使用任一 Runtime Skill 前执行一次。同一会话中，锁文件没有变化时不重复执行。

`sync` 的判断顺序：

1. 校验所有安装目录和同步工具是否匹配锁文件摘要。
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

## 发布

1. 修改受影响的 Skill 或同步工具版本，并同步提升 `release_version`。
2. 通过清单校验和同步工具测试。
3. 合并发布变更到 `main`。
4. Release workflow 重新校验 `main`，自动创建与清单一致的 tag，例如 `v0.2.0`。
5. workflow 自动创建 GitHub Release 和 Release Notes；对应 tag 或 Release 已存在时安全跳过。

不需要维护者在终端手工推送 tag。缺失 Release 时，可以在 GitHub Actions 中手动运行 `Release Runtime Skills` workflow；它仍以最新 `main` 和清单版本为准。

Release 是稳定使用入口。`main` 可以包含尚未发布的下一版内容，但目标项目的自动同步只消费 GitHub Release，不直接追随移动的 `main`。

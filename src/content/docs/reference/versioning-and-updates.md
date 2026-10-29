---
title: 版本与更新机制
description: 用户全局规则、精确项目锁、期次隔离与生成包发布。
sidebar:
  order: 2
---

## 版本与存储

| 对象 | 职责 |
| --- | --- |
| skills-manifest.json | Release、工具和各 Skill 的唯一源码版本事实 |
| skills/ | 规范规则、脚本、模板的唯一源码 |
| distribution/ | 平台展示元数据，不复制规则 |
| 用户发现目录 | 版本路由与启动工具 |
| ~/.runtime-skills/bundles/&lt;sha256&gt; | 不可变精确规则缓存，位于发现目录外 |
| 项目 runtime-skills.lock.json schema 2 | 各 Skill 的精确版本、Release 与内容/缓存摘要 |
| 项目 Runtime | 项目事实、需求、进度、检查点和证据 |

package.json 只用于文档站，不能推断 Skill 版本。安装产物由同一源码生成：四种全局 ZIP、豆包工作与 WorkBuddy 的八个独立导入 ZIP、安装器、安装合同、索引和校验清单。

## 安装与更新

按仓库 INSTALL.md 获取经过校验的稳定包。安装只写用户目录，真实任务才由 session 绑定项目。Codex/Copilot/dsh 共用受支持的 ~/.agents/skills；Claude Code 用 ~/.claude/skills。导入平台使用自包含单 Skill ZIP，不猜测用户目录。

session 输出真实 skill-root 和 runtime-tool。下列命令中的路径必须替换为该实际绝对路径：

```bash
python "<runtime-tool>" verify --project /path/to/project
python "<runtime-tool>" doctor --project /path/to/project
python "<runtime-tool>" sync --project /path/to/project
python "<runtime-tool>" pin --project /path/to/project --reason phase-01
python "<runtime-tool>" unpin --project /path/to/project
python "<runtime-tool>" adopt --project /path/to/project --allow minor
```

全局模式 sync 只验证。全局安装新默认不改变既有项目锁，也不回收旧缓存。恢复活动期次时先 verify，缺 pin 时先 pin 原期次；新期次在写状态前 pin。不同活动期次不能覆盖现有 pin。期次关闭或用户批准受控迁移后才能 unpin/adopt。

采用新版需要显式 adopt，默认只允许补丁，minor/major 必须相应参数。活动 pin 阻止 adoption；同版本内容不同、降级、漂移或缺失精确缓存都阻止。restore-cache 仅恢复与锁中完整摘要相同的源包，不改锁、不回退 latest。换机器应保留精确源包；旧补丁 Tag 可能归档，只有版本号不足以重建缓存。

## 兼容与诊断

旧 schema 1 项目锁仍由原命令校验/更新；旧流程不作为新安装默认。迁移必须关闭期次、验证无漂移，显式 bind --migrate-project --allow major，事务性归档所有旧受管发现副本和工具，再切换 schema 2。项目记忆保持原位；未受管文件和指令不自动删除。

doctor 只检查有界已知项目/Git 祖先/用户根及指令元数据，不扫描业务或输出指令全文。大指令与重复路由属于人工审阅提示；副本冲突、读不全或漂移会阻断执行。平台自定义/企业目录需要依实际配置检查。context 每次最多 6000 字符，不能保证整会话 token 总量。

## 版本与发布治理

PATCH 为兼容修复；MINOR 为向后兼容能力；MAJOR 用于安装布局、状态或跨 Skill 合同破坏性变化。新全局布局使用新的主版本。修改规范 Skill 或工具均需提升对应版本和 release_version；平台元数据/安装器/构建器修改也受 CI 版本门禁约束。

所有改动通过 Issue → 专用分支 → PR → CI → PR 合并。既有 Release workflow 基于 main 校验和测试，再生成确定性产物，打 Tag、创建 Release 并上传附件。已有同版本 Tag 指向不同代码时必须提升版本，不能覆盖；已有附件须逐字节相同才可重跑。公开市场提交另行通过官方平台，不属于自动 Release。

同一主次系列仅公开最新补丁，旧补丁 Release 转 Draft、公开 Tag 删除；不同主次系列保留。缓存不自动回收，既有项目不会因此漂移。预发布不作为稳定 latest；main 中尚未发布的内容只供维护者显式 --source 验证。

---
title: 编写新教程
description: 在当前 Starlight 站点中添加和维护 Skill 教程。
---

## 新建页面

在 `src/content/docs/` 下创建 Markdown 或 MDX 文件。目录就是页面路由：

```text
src/content/docs/
  tutorials/
    my-tutorial.md
```

每个页面至少包含标题和说明：

```yaml
---
title: 教程标题
description: 一句话说明读者完成后能得到什么。
---
```

## 教程写作结构

一篇可执行的 Skill 教程建议依次说明：

1. 读者要解决的真实问题。
2. 进入该 Skill 前必须满足的条件。
3. 可以直接使用的自然语言指令。
4. 运行过程中会生成或更新的产物。
5. 正确的停止点和下一个交接对象。
6. 容易越过的职责边界。

不要把整份 `SKILL.md` 复制进教程。教程应该帮助读者理解选择和操作，完整规则仍保留在 `skills/` 中。

## 本地预览

```bash
npm install
npm run dev
```

生产构建：

```bash
npm run build
```

## 加入导航

在 `astro.config.mjs` 的 `sidebar` 中添加页面 slug。例如文件：

```text
src/content/docs/tutorials/my-tutorial.md
```

对应：

```js
{ label: '教程标题', slug: 'tutorials/my-tutorial' }
```

## 提交前检查

- 页面中的命令能够直接执行，不用伪命令占位。
- 状态名称和交接边界与当前 Skill 源文件一致。
- 内部链接在 `/dev-runtime-skill/` Pages 基础路径下可用。
- `npm run build` 通过，没有失效链接或内容集合错误。

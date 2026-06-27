# Step 6: 注释与本地文件头规范

本 Step 在实现、测试和文档检查后执行，用于确认注释和项目本地文件头是否仍然有用。

## 通用规则

- 只有代码意图无法从命名和结构直接看出时，才添加注释。
- 删除或更新与当前行为矛盾的注释。
- 不添加重复下一行代码含义的注释。
- 不虚构作者、日期、历史修改或业务决策。
- 除非当前项目已有文件头约定，否则不强制新增文件头。
- 如果项目已有文件头，保留既有 author/developer 字段，只更新本次范围内必要内容。

## 适合保留的注释

以下情况可以使用简短注释：

- 不明显的 fallback 行为。
- 保护真实 workflow 的边界条件。
- 外部格式或持久化格式到内部 contract 的 mapping 逻辑。
- concurrency、transaction、retry 或 cleanup 规则。
- 有意保留的兼容行为。

## Frontend 检查

当 frontend 文件在范围内时执行：

- comment 应只在命名不足以说明 component/composable/store 行为时补充。
- 除非属于产品 UX，不要新增可见的 in-app instructional text。
- 如果项目已有 platform/browser/SDK adapter 层，相关注释应留在 adapter/platform 层，不散落到普通 UI 文件。

## Backend 检查

当 backend 文件在范围内时执行：

- DTO validation 通常应通过 decorator 或 schema definition 自解释。
- service comment 应解释业务规则或编排约束，而不是复述 controller route。
- repository/provider comment 可以解释 mapping、transaction、migration 或 external IO 意图。
- test 应优先通过名称和断言说明行为，不要依赖大量注释。

## 文件头检查

如果项目有标准文件头：

- 确认变更过的手写 source 文件符合本地文件头形态。
- 新增修改记录必须来自可观察变更，不得写泛泛描述。
- 不更新 generated output、build artifact、dependency folder、lockfile、binary asset 或 generated SDK/client 文件。

如果项目没有标准文件头约定，文件头检查不适用。

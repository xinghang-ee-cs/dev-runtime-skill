# 技术栈 Profile 路由

本目录保存通用 Step 之外的技术栈附加规则。运行治理、10 个用户场景、`scope`、`editable_scope`、修改授权、问题分类和 Runtime 生命周期只由 `../../SKILL.md` 定义；Profile 不得重定义。

## 加载顺序

1. 读取项目根目录 `.runtime/ai-code-inspection/project-environment-profile.md`。
2. 根据当前检查范围识别涉及的组件、持久化项和公共契约项。
3. 先加载当前场景需要的通用 Step reference。
4. 根据相关组件的 `language`、`framework`、`test_runners`，以及相关持久化项的 `orm_or_client` 和契约项的 `type`，只加载匹配 Profile。
5. 没有匹配 Profile 时继续执行全部适用通用规则，记录专用 Profile 未覆盖，不猜测技术栈规则。

同一范围涉及多个组件或工具时可以加载多个 Profile；不得无差别加载与当前范围无关的全部文件。Profile 的激活条件必须同时得到环境档案和当前仓库事实支持。

## 当前 Profile

- `frontend/vue.md`
- `frontend/react.md`
- `backend/nestjs.md`
- `persistence/prisma.md`
- `testing/vitest.md`
- `language/typescript.md`
- `contract/openapi.md`

新增 Profile 时从 `profile-template.md` 开始，只写该技术栈特有规则；通用检查应回到对应 Step reference。

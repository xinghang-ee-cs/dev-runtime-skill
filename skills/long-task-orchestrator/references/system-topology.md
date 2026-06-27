# 系统拓扑

本文件只定义 boundary classification、parallel constraints、delegation constraints 和 topology escalation。

## 边界等级

| 等级 | 含义 | 默认策略 |
| --- | --- | --- |
| P0 | 核心共享边界 | 串行 |
| P1 | 高风险共享边界 | 受限 |
| P2 | 模块边界 | 可委派 |
| P3 | 低风险独立边界 | 可并行 |

## P0 核心边界

| 边界 | 风险 |
| --- | --- |
| database schema | 数据结构冲突、迁移冲突 |
| tenant isolation | 数据越权访问 |
| permission matrix | 权限绕过 |
| state machine | 非法状态流转 |
| API contract | 前后端合同漂移 |
| route registration | 入口冲突 |
| auth chain | 安全失败 |
| audit chain | 操作不可追踪 |
| delete/cleanup chain | 数据丢失 |
| lockfile/dependency | 构建不稳定 |

```text
parallel = forbidden
delegation = forbidden
validation = required
```

## P1 高风险边界

| 边界 | 风险 |
| --- | --- |
| domain service | 公共行为漂移 |
| API client | 合同不匹配 |
| shared component | 跨页面回归 |
| shared utility | 语义漂移 |
| config file | 全局构建影响 |
| test infrastructure | 测试结果失真 |

```text
parallel = restricted
delegation = restricted
public_semantic_change -> P0
```

## P2 模块边界

| 边界 | 风险 |
| --- | --- |
| isolated page | 局部 UI 回归 |
| feature component | feature 内部回归 |
| module test | 局部测试漂移 |
| feature document | 文档漂移 |
| isolated adapter | adapter 行为漂移 |

```text
parallel = allowed
delegation = allowed
P0/P1_boundary_touch -> forbidden
```

## P3 低风险边界

| 边界 | 风险 |
| --- | --- |
| copy change | 低产品歧义 |
| local style adjustment | 局部视觉回归 |
| local display order | 局部体验回归 |
| non-core test addition | 低测试漂移 |
| non-plan README note | 文档噪声 |

```text
parallel = allowed
delegation = allowed
validation = required
```

## 禁止并行

```text
database_schema
migration
seed
OpenAPI
permission_matrix
state_enum
state_flow
auth_middleware
tenant_isolation
audit_log
route_registration
module_registration
lockfile
dependency_install
local_service_port
real_external_service
production_like_data
```

## 允许并行

```text
isolated_page_ui
feature_internal_component
read_only_code_analysis
single_module_test_addition
isolated_document_draft
style_change_without_shared_config
frontend_display_without_contract_change
copy_change_without_state_change
```

## 委派约束

```text
touches_P0 -> delegation_forbidden
touches_P1 -> delegation_restricted
only_P2_or_P3 -> delegation_allowed
shared_file_conflict -> parallel_forbidden
real_external_service_or_port_or_database -> parallel_forbidden
```

## 拓扑升级

| 条件 | 升级 |
| --- | --- |
| P2 touches shared component | P1 |
| P2 touches route registration | P0 |
| P2 touches API field | P0 |
| P1 changes public method signature | P0 |
| any task touches permission matrix | P0 |
| any task touches state flow | P0 |
| any task touches database schema | P0 |
| any task touches real external service | P0 |

## 例外协议

P0/P1 parallel exception requires:

- boundary
- isolation
- conflict_detection
- validation
- responsible_agent

缺少例外记录 -> parallel forbidden。

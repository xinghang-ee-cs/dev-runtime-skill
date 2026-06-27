# 委派规则

本文件只定义 delegation constraints。

## 委派拓扑约束

委派前必须读取 `references/system-topology.md`。

```text
topology_verdict = system-topology.md
delegation_forbidden -> DO_NOT_DELEGATE
delegation_restricted -> REQUIRE_BOUNDARY_AND_ISOLATION
delegation_allowed -> DELEGATE_WITH_BOUNDED_SCOPE
higher_boundary_detected -> RETURN_BLOCKED
```

## 并行冲突约束

```text
same_file_parallel_write -> STOP
shared_contract_parallel_write -> STOP
route_table_parallel_write -> STOP
module_registry_parallel_write -> STOP
migration_parallel_write -> STOP
lockfile_parallel_write -> STOP
generated_output_parallel_write -> STOP
local_server_parallel_use -> STOP
port_parallel_use -> STOP
database_parallel_write -> STOP
external_service_parallel_call -> STOP
real_machine_interface_parallel_use -> STOP
external_changes_must_be_preserved
```

## 交接 Schema

```yaml
required:
  - goal
  - ownership_boundary
  - dependency
  - editable_scope
  - forbidden_scope
  - expected_output
  - validation
  - completion_proof
  - report_format
  - return_status
```

## 结果状态协议

```text
DONE -> REVIEW_BEFORE_MARK_DONE
DONE_WITH_CONCERNS -> RESOLVE_OR_ACCEPT_CONCERNS
NEEDS_CONTEXT -> PROVIDE_CONTEXT_WITHIN_SAME_BOUNDARY
BLOCKED -> SPLIT_OR_REASSIGN_OR_SKIP_OR_ESCALATE
```

## 决策记录

```text
subagent_accepted -> agent-decisions.md
subagent_rejected -> agent-decisions.md
subagent_deferred -> agent-decisions.md
subagent_corrected -> agent-decisions.md
risk_accepted -> agent-decisions.md
```

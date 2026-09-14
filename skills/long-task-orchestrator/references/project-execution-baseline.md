# 项目执行基线

## 目录

- 使用规则
- 恢复与失效规则
- Baseline 模板
- Required Validation Matrix

本文件是 Runtime State Template。

实例化位置：

```text
<phase_runtime_directory>/project-execution-baseline.md
```

禁止在本文件保存某个项目或期次的执行基线。在落地清单前置准备 Step 2“查看项目环境”结束后，只更新当前 Phase Runtime Directory 中的实例；后续只有当执行、委派、验证或复盘需要反查环境事实时读取该实例。

本文件只保存当前运行可复用的稳定环境事实；不记录阶段日志、事故过程、subAgent 反馈流水或临时决策。

## 使用规则

- 当前期次新 Runtime 开始时，创建或覆盖当前 Phase Runtime Directory 中的 Baseline 实例；不得覆盖 Skill 静态模板，也不得跨期复用实例。
- 只记录会影响后续拆分、委派、验证和复盘的事实，以及由这些事实派生的当前期 `required_validation_matrix`。
- 不在此文件定义验证通过标准；验证证据口径由 `validation-gates.md` 定义。
- 不在此文件定义执行顺序或状态机规则；执行闭环由 `task-state-machine.md` 和 `task-execution.md` 定义。
- 如果基线在任务期间过期，先更新当前 Baseline，再继续执行。
- 本实例必须由 `current-runtime-context.md.project_execution_baseline_file` 指向，并在 `checkpoint-runtime.md.project_execution_baseline_status` 中记录 `current | stale | missing | invalidated`。
- Runtime 恢复必须读取当前期次 Baseline 实例；不得从本 Skill 静态模板恢复项目环境事实。

## 恢复与失效规则

依赖新增/升级/降级/替换、lockfile、Runtime/框架版本、构建工具、测试框架、交付单元拓扑、构建/启动命令、运行配置要求、环境变量或外部工具依赖发生变化时，必须校验 Baseline，并重新派生 `required_validation_matrix`。旧 matrix revision 的结果不得默认继续使用；只允许未受影响且 requirement id、命令/探针、成功后置条件和安全边界完全不变的结果通过 `validation-results.md` 显式兼容映射继续生效，其余精确失效并重跑。

```text
project_execution_baseline_missing_or_stale
-> STOP
-> refresh_environment_baseline
-> update_current_phase_runtime_baseline
-> rerun_recovery_consistency_gate
```

Baseline 未恢复为 `current` 前不得继续实现。依赖相关任务必须确保 Baseline 的 package manager、lockfile、版本与政策事实同 Runtime Context、Checkpoint 和 Active Task 依赖字段一致。

## Baseline: <date> <plan-name>

- baseline_status: <current | stale | missing | invalidated>
- last_confirmed:
- 源计划：
- 当前分支/状态：
- 开发工具：
- package_manager:
- lockfile:
- runtime_versions:
- framework_versions:
- dependency_policy:
- official_registry_sources:
- 前端测试框架/命令：
- 前端覆盖率命令：
- 前端设计体系/Token 来源：
- 现有共享组件来源：
- 截图/视觉回归能力：
- 可访问性自动化能力：
- 后端测试框架/命令：
- 后端覆盖率命令：
- API 文档工具：
- 交付单元拓扑：
- 构建、打包与直接源码运行方式：
- 启动、装载与最小行为探针：
- 运行配置键及加载方式（只记录键名、来源类型和是否必需，不记录值）：
- 本地/受控测试依赖及安全就绪探针：
- 数据库、Schema 与 Migration 的非破坏性就绪检查：
- 架构边界：
- 当前协议：
- 相关已有模块：
- 验证命令：
- 已知本地约束：
- known_environment_constraints:

## Required Validation Matrix

本区块是当前期必要验证集合的唯一实例事实源；字段与通过规则只引用 `validation-gates.md#required-validation-matrix-and-local-runnable-gate`，不得在其他 Runtime 文件复制另一份要求清单。

```yaml
required_validation_matrix:
  matrix_revision: <revision>
  derived_from:
    - <Planning Handoff / project evidence / command source>
  completeness_audit:
    repository_scan_revision: <current code/config snapshot revision>
    delivery_unit_inventory_refs: []
    changed_or_required_delivery_unit_ids: []
    mapped_delivery_unit_ids: []
    locally_automatable_planning_test_refs: []
    mapped_planning_test_refs: []
    manual_or_real_environment_planning_test_refs: []
    handoff_manual_test_refs: []
    open_gaps: []
    result: <passed | blocked>
  delivery_units:
    - unit_id: <stable runtime-local id>
      unit_type: <service | web_client | worker | job | cli | library | package | migration_or_schema | other>
      scope_relation: <changed | required_by_changed_scope>
      local_execution_mode: <runnable | loadable | migration_only | not_applicable>
      runtime_dependencies:
        - dependency_id: <id>
          required_for: <build | boot | minimum_behavior | schema_or_migration>
          readiness_probe: <safe command/probe or unresolved>
          credential_evidence: <presence_only | not_applicable>
      requirements:
        - requirement_id: <stable within matrix revision>
          planning_test_refs: []
          validation_type: <allowed validation_type>
          validation_focus: <allowed validation_focus>
          requirement_level: <required | optional | not_applicable>
          binding_status: <existing | planned_in_confirmed_task | unresolved>
          planned_task_revision: <required only for planned_in_confirmed_task; TASK-ID@revision>
          command_or_probe: <给人阅读的项目派生命令/探针摘要；machine_execution 才是机器执行事实源>
          success_postconditions: []
          safe_execution_boundary: <Agent 依据当前授权与项目事实声明的 local | isolated | controlled；是 Prompt/流程约束，不是 runner 对环境安全的机器证明>
          machine_execution:
            working_directory_ref: <从 project_root_ref 指向的项目根目录开始计算的相对目录>
            default_timeout_seconds: <1..3600>
            postcondition_probes:
              - postcondition: <必须与 success_postconditions 中一项逐字一致>
                probe_kind: <argv | path_exists>
                argv: [<仅 argv 探针使用；逐参数列表，不经过 shell>]
                path_ref: <仅 path_exists 使用；相对 working_directory_ref>
                expected_type: <仅 path_exists 使用；file | directory | any>
                nonempty: <仅 path_exists 使用；true | false>
          not_applicable_reason: <reason or null>
```

`completeness_audit` 是完成边界重新扫描的最小机器可校验摘要，不是第二份 Matrix：

- `delivery_unit_inventory_refs` 中每个文件必须包含下列唯一结构。每个交付单元必须声明覆盖其完整代码与公开配置边界的 `source_roots`；`source_refs` 只用于补充根目录之外的单文件。禁止引用 `.env`、密钥、凭证或秘密文件：

```yaml
delivery_unit_inventory:
  units:
    - unit_id: <与 Matrix 一致>
      source_roots: [<完整、已存在、非秘密的代码/公开配置目录>]
      source_refs: [<可选：根目录之外的已存在非秘密文件>]
```

- 先运行 `validate-long-readiness.sh <runtime> --print-repository-revision`，把脚本递归展开 `source_roots`、应用固定生成物排除项并依据所有实际文件内容计算的 SHA-256 写入 `repository_scan_revision`；不得自行填写 revision。符号链接、秘密路径、相互重叠但使用不同 ref 的 roots、空 source root、inventory unit 集合与 Matrix 不一致均阻断。Ready receipt 同时冻结展开后的源码、Planning 合同以及 Validation Results 引用的外部 evidence/compatibility evidence。只有标题、抽样文件、空清单或自报集合一律无效。
- Matrix 中本地与人工 TEST 引用的并集必须覆盖 Planning Test and Acceptance Plan 的全部 TEST 合同；`mandatory_automated` 必须留在 Long required requirement，`manual_or_real_environment_required` 才能进入人工移交。
- `changed_or_required_delivery_unit_ids` 必须与 `mapped_delivery_unit_ids` 集合完全一致，并与 Matrix 中唯一 `unit_id` 集合一致。
- `locally_automatable_planning_test_refs` 必须与 `mapped_planning_test_refs` 集合完全一致。
- `manual_or_real_environment_planning_test_refs` 必须与最终 Long Handoff `manual_required[].planning_test_refs` 的并集完全一致。
- 任一重复 ID、无法解析引用、集合差异或 `open_gaps` 非空时，`result` 必须为 `blocked`，Local Runnable Gate 不得通过。
- 每个交付单元必须在同一 `requirements` 列表完整实例化 `validation-gates.md` 定义的适用性要求；缺项与无理由的 `not_applicable` 都属于 `open_gaps`。
- 每个 `required` 项必须让 `machine_execution.postcondition_probes` 与 `success_postconditions` 一一对应。命令使用 `argv` 参数数组并由 runner 以 `shell=False` 执行；产物存在性使用 `path_exists`，不能把“构建命令退出 0”替代为产物/装载成功。工作目录和探针路径必须留在 `project_root_ref` 声明的项目根目录内。

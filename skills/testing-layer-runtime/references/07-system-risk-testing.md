# 系统风险、线上运行与部署验证

## 目录

- 职责与测试分层
- 风险识别与按需 Profile
- 部署范围与既有排除项
- 覆盖矩阵唯一格式
- 证据、CI 对账与完成门禁
- 旧 Runtime 和 Bugfix

## 职责与测试分层

Planning 解释问题与价值、排除伪需求、明确需求边界和可观察验收合同；Long 忠实实现、完成单测和必要开发自动化；Testing 设计并管理证明整体系统符合合同的测试。

| 类型 | 主 owner 与证明目标 |
| --- | --- |
| 单测/开发自动化 | Long；函数、模块及必要本地行为正确，现有有效证据直接继承 |
| 联合测试 | Testing；模块、服务、协议和外部依赖组合后的合同、失败传播与业务闭环 |
| 线上运行测试 | Testing；精确部署环境下的运行边界、隔离、异常恢复、数据与稳定性 |
| 上线部署测试 | Testing 设计和核验证据；验证配置、挂载、启动、健康检查、版本切换、升级/回滚及部署后行为，实际部署操作由项目发布流程负责 |

分层描述验证目标，不新增 workflow stage。联合测试的代码与本地可自动化执行仍可交给 Long；测试工具名称不决定归属。线上指真实部署环境，可以是隔离预发布环境；必须报告实际验证环境，不把预发布结果称为生产已通过。

允许从当前需求、架构、接口、实际配置和运行机制派生技术检查，不要求 Planning 预先列出每个技术用例。不允许凭空设定 SLA、容量、配额、重试次数、响应体上限或新业务行为；标准不明确且会改变实现时记录 `planning_gap`，只回流对应合同。仓库测试代码/测试入口/CI 配置缺失或错误统一使用 `test_defect -> fix_in_execution`，以精确测试资产 allowlist 交 Long test-only patch；仅测试数据、临时执行配置、证据或 Testing Runtime 修正使用 `test_defect -> fix_in_test`。准入与返回沿用 `01-test-runtime-core.md`，不得借测试修复改变业务实现或业务合同。

## 风险识别与按需 Profile

Test Planning 时读取当前范围涉及的源码/架构、部署清单、CI 和已脱敏环境事实，记录特征及证据。每个类别必须显式 `required` 或 `not_applicable` 并说明原因；未知不等于不适用，需补事实或阻断。以下是最低分类，项目发现的新风险仍需追加检查或分类，不因清单外而忽略：

| 类别 | 识别信号与必查方向 |
| --- | --- |
| `integration_contracts` | 多组件/外部依赖：协议、序列化、超时与错误传播，完整链路 |
| `resource_bounds` | 容器/插件/子进程：CPU、内存、进程数、并发及输出边界和清理 |
| `credential_isolation` | 插件/隔离执行：凭据、文件、挂载和跨实例可见范围 |
| `health_semantics` | 常驻服务：启动/就绪/存活含义，非成功状态码、依赖失败是否正确判错 |
| `external_io_bounds` | 外部请求：响应大小、流式累计量、时限、取消、重试及错误处理 |
| `failure_recovery` | 故障传播、崩溃/重启、连接断开、恢复、幂等和资源释放 |
| `data_integrity` | 持久化：写入失败、一致性、迁移、重复提交、恢复及已有隔离合同 |
| `environment_binding` | 配置/路由/挂载/依赖是否进入目标进程并实际生效 |
| `deployment_lifecycle` | 发布版本、启动顺序、健康门禁、升级、回滚及部署后核验 |

特征词固定为 `multi_component | container | plugin_execution | service_process | external_io | persistent_data | deployment`；逐项核对是否存在，`features` 只列已证实存在者，不能因没有专用 Profile 而省略特征。其他特征写在 reason/检查依据中。

- 容器、插件或子进程执行：读取 `profiles/isolated-runtime.md`。
- 外部网络/流式请求或常驻服务健康检查：读取 `profiles/external-io-and-health.md`。
- 没有匹配 Profile 时按通用风险分类与当前项目/官方技术资料形成检查，记录专用 Profile 未覆盖；不得默认不适用，也不加载全部其他 Profile。

## 部署范围与既有排除项

首次新增部署、改变部署形态、配置/挂载边界或接入外部依赖时，重新检查原“不包含部署/生产验收”、云端 `not_applicable`、故障测试排除项和 CI 覆盖。

合同已包含当前部署目标、只是补充证明方式时保持 `scope_alignment: aligned`；确需扩大需求/验收范围时写 `reconfirmation_required`，经 Change Triage 定向回 Planning，取得增量合同后才恢复对应验证。不得静默把旧排除项改为适用，或用旧排除项跳过当前风险。仅代码/部署 revision 更新而合同不变时，复用已有 Deployment Revision Reconciliation Gate。

## 覆盖矩阵唯一格式

在现有 `business-journey-test-matrix.md` 的 YAML 中追加以下块，不新建风险 Runtime。示例只有一个类别；实际须覆盖上表全部类别，可追加其他唯一类别。

```yaml
system_risk_coverage:
  schema_version: 1
  deployment_in_scope: true
  scope_alignment: aligned
  fact_evidence_refs: [E-SCOPE]
  features: [container, service_process, deployment]
  categories:
    - category: resource_bounds
      applicability: required
      reason: 目标容器承载隔离执行，需证明已确认资源边界
      checks:
        - check_id: SYS-RESOURCE-1
          test_layer: online_runtime
          contract_refs: [approved-architecture.md#runtime-boundaries]
          assertion: 已确认的资源限制生效，超限受控且资源被回收
          verification_kind: behavioral_test
          result_refs: [RESULT-RESOURCE-1]
          regression:
            requirement: required
            reason: 资源隔离缺陷需持续防回归
            ci_provider: github_actions
            workflow_job_ref: .github/workflows/ci.yml#runtime-tests
            command_or_binding: 已核实的目标测试命令或脚本绑定
            verification_kind: behavioral_test
            ci_result_refs: [RESULT-CI-1]
```

- `fact_evidence_refs` 引用现有证据索引内、覆盖当前范围/特征判定及合同对齐依据的脱敏记录；不得只写“已检查”。记录真实来源路径/revision、观察结果及排除理由，禁止秘密值。
- `deployment_in_scope` 是本次测试范围事实，不是新需求；无部署且当前部署身份为 `not_applicable` 时使用 `false`。有部署必须包含 `deployment` 特征，未知身份不能关闭线上检查。
- 不适用类别写 `applicability: not_applicable`、具体 `reason`、`checks: []`。已识别特征触发的必需类别不能改为不适用；确有特殊实现应以检查证据说明，而不是删类别。
- 检查必须具有唯一 `check_id`、`integration | online_runtime | deployment` 分层、真实合同引用、可观察断言、`behavioral_test | configuration_check` 验证类型和正式 `result_refs`。一个结果可以证明多个明确断言，但每个断言都需被其 `covers` 引用。
- 正式状态仍只在 `test-validation-results.md`；沿用完整结果格式和现有 item_type（如 `case`、`server_verification`），`covers` 加入 check_id。线上项使用当前部署身份，不能只引用静态代码、配置存在性或本地通过。
- 部署适用时，除 `integration_contracts` 外的每个 required 通用风险类别，至少有一项 `online_runtime | deployment` 检查及当前完整部署身份证据；不能把整类改标 `integration` 后仅用本地结果关闭。允许同类同时有本地故障注入与目标环境生效核验，不要求将危险故障注入搬到真实目标。

## 证据、CI 对账与完成门禁

每个检查开始前/完成后沿用 Per-Test Durable Writeback、依赖和 finding 闭环规则。证据沿用现有索引字段、持久文件和摘要；线上/部署证据另外填写 `deployment_identity_digest`，与当前完整部署身份一致。组件集合证据填写实际经过的 `component_revision_refs`。

CI 回归对账由 Testing 决定覆盖需求并核验，Long 落地测试代码与配置：

- 对每个检查明确 `regression.requirement` 和原因。可自动化且需要持续防回归的检查为 `required`，必须绑定真实 workflow/job、实际测试命令/脚本，以及本次当前代码 revision 的 CI 正式结果和持久证据。
- 核对 job 的触发事件、path filter、条件、矩阵、测试筛选、跳过/allow-failure 配置；“存在 test 步骤”“所有现有检查绿了”不能代替覆盖对账。workflow/job 引用和命令必须与事实证据一致。
- `ci_provider` 显式为 `github_actions | gitlab_ci | provider_export`，CI 证据索引使用同值。前两者仅从受支持的 YAML 显式映射位置识别 job，忽略注释、单行引号字符串与 `|`/`>` 多行脚本。跨行单/双引号、跨行 flow 集合、tag、anchor/alias 等无法可靠解析时，明确报告 unsupported 并阻断，转 `provider_export`，不能继续将后续字符串内容猜作 job；include 或动态 job 同样使用导出证据。普通 shell 命令中的引号不作为 YAML 引号处理；不支持的语法不等于配置本身无效。
- CI 证据索引的 `evidence_type: ci_job_run`，并填写与矩阵一致的 `ci_provider`、`ci_job_ref`、`command_or_binding`、`verification_kind`；持久文件记录真实运行链接/ID、代码 revision、实际执行/未跳过与失败传播结果。机器检查引用/摘要和绑定一致性，job 条件是否真正覆盖对应断言仍由 Testing 审阅证据正文。
- Jenkins 或其他 CI、动态/复合 YAML 使用 `provider_export` 并在 regression 绑定 `definition_evidence_ref`。该引用仍用现有证据索引和当前代码 revision，持久 JSON 的唯一格式为：`schema_version: ci-job-definition/v1`、实际 `provider`、提供方导出的 `source_ref`、与矩阵一致的 `workflow_job_ref`/`job_id`、当前配置文件字节摘要 `configuration_sha256`，以及非空对象 `definition`。通过提供方 API/编译后配置或批准渠道取得真实、脱敏的 job 定义；不得用手写通过声明代替导出。配置摘要或 job 身份不匹配即阻断；结构化定义证据不能代替同一代码 revision 的真实 CI 运行证据。
- 行为/故障恢复要求不能由 build/typecheck/static check 代替；例如 `cargo check` 不证明 Rust 测试执行。不要硬编码通用 Rust 命令，从真实 workspace 和测试目标派生命令。
- 不适合 CI 的真实设备/环境一次性验证可写 `not_applicable`，reason 必须说明原因、替代复验安排、责任主体和触发时点；无 CI 配置、权限不足或 job 被跳过不是自动豁免理由。当前 required CI 结果缺失就保留阻断，不能伪造通过。
- CI 可在隔离环境证明回归能力，但不能替代线上检查自身的精确部署证据；两种 result_refs 分开绑定。

System Risk Coverage Gate 要求所有类别完成适用性判断、所有 required 检查及 CI 映射具有当前有效结果/证据、范围对齐且无相关未闭环 finding。`validate_testing_runtime.py --expect-final` 和 current Release Handoff 均核对此块；风险结果必须同时进入 Release Handoff 的 `required_result_refs`，冻结其引用。校验器只验证覆盖/证据合同，不证明 Agent 已穷尽所有风险或证据正文中的技术断言必然正确。

线上没有安全故障注入条件时，先使用等价隔离环境验证，并单列真实目标的只读配置/生效证据；不得把隔离结果标成真实生产故障注入通过。压测、重启、断网、秘密边界探测、迁移、发布/回滚仍遵守既有授权边界；未授权项保持未验证并移交。

## 旧 Runtime 和 Bugfix

旧 Runtime 缺少本块时，Intake 和未完成阶段仍可恢复，但新版本下不能输出最终通过或 current Release Handoff。只补充同一矩阵、结果与证据；原有效证据可复用，不重写 Planning 00–15 或历史事实，不倒拨 workflow。受影响已有发布快照先按原规则失效，再开启合适的前向复测 cycle。

Bugfix 只在 `02-test-verification.md` / `03-release-verification.md` 中记录根因和补丁命中的风险检查及回归映射，遵循 `06-bugfix-verification.md`；不套用整期九类矩阵。整期校验器的新增机器门禁不等于 Bugfix Case 的专项运行证明。

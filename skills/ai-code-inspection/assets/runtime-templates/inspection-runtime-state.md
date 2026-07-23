status: idle
run_started_at: null
modifier: null
modifier_source: null

routing:
  requested_scene: null
  effective_scene: null
  scene_source: null
  matched_signals: []
  preserved_intent: null
  fallback_reason: null

execution:
  strategy: null
  current_phase: null
  internal_phase: null
  internal_phase_source: null

scope:
  target: null
  specified_files: []
  related_paths: []

editable_scope:
  type: none
  files: []
  paths: []

remediation_policy: report_only
production_code_editable: false
database_operation_authorized: false
cleanup_forbidden: true
refactor_forbidden: true

steps: {}
issues: []
current_authorized_batch: null
authorization: null
remediation:
  pending: []
  active: null
  completed: []
validation: []
remaining_risks: []
suggested_next_scenes: []

notes:
  - 本文件只保存一次 ai-code-inspection 运行期间的临时状态和权限快照。
  - 初始化时将本模板复制到目标项目根目录 .runtime/ai-code-inspection/inspection-runtime-state.md。
  - 每次新运行开始、场景切换开始、临时权限完成或失败，以及最终报告输出后，都恢复安全默认状态。
  - 场景 1–9 使用 single_run；只有场景 10 使用 interactive_seven_step。
  - regression_verification 只能作为场景 3 修复后的内部阶段，不得写入 requested_scene。
  - steps、授权批次和 remediation 队列只在场景 10 使用。
  - scope 只定义读取和检查范围；editable_scope 才定义修改范围。
  - production_code_editable 与 database_operation_authorized 相互独立，不得互相推导或撤销。
  - cleanup_forbidden 与 refactor_forbidden 始终恢复为 true。
  - 不得在这里保存稳定环境事实、业务产物或跨运行上下文。

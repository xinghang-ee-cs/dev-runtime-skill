status: idle
run_started_at: null

mode: null
mode_source: null
execution_strategy: null

scope:
  target: null
  selection_source: null
  specified_files: []
  related_paths: []

editable_scope:
  type: none
  files: []
  paths: []

remediation_policy: report_only
production_code_editable: false
cleanup_forbidden: false
refactor_forbidden: false

modifier: null
modifier_source: null
environment_profile_loaded: false
ci_cd_checked: false
database_migration_status: not_applicable

current_step: null
current_phase: null
current_authorized_batch: null

issue_classification:
  - safe_standard_correction
  - confirmed_bug
  - report_only_risk
  - incremental_design_required
  - refactor_assessment_required
  - blocked_out_of_boundary

steps: []
issues: []
remediation:
  pending: []
  active: null
  completed: []
authorization:
  issue_ids: []
  allowed_files: []
  allowed_actions: []
  granted_by: null
  consumed: false
blocked: []
next_step_candidate: []
modified_files: []
validations: []
risks: []

notes:
  - 本文件只保存一次 ai-code-inspection 运行期间的临时状态和权限快照。
  - 每次新运行开始和最终报告输出后，都必须重置为本初始模板。
  - 模式切换时先清空 editable_scope、待修正批次和上一模式权限，再按新请求重新授权。
  - 前 10 种模式使用 single_run；standards_compliance_correction 使用 interactive_seven_step。模式切换时必须重新计算 execution_strategy。
  - single_run 不创建 Step 间等待状态，不读取或消费继续 gate，也不使用 current_authorized_batch 驱动普通流程。
  - single_run 必须在当前运行中完成全部适用检查、执行、验证和最终报告。
  - 只有 interactive_seven_step 才使用授权批次、Step 间暂停和继续 gate。
  - confirmed_bugfix 只有在预期行为、根因证据和具体根因文件均明确时，才允许将 production_code_editable 设为 true，且 editable_scope.files 必须是具体文件。
  - confirmed_bugfix 条件不足时必须保持只读，并切换到 targeted_diagnosis、incremental_design 或 refactor_risk_assessment。
  - confirmed_bugfix 不使用 current_authorized_batch、authorization、继续 gate 或 Step 间暂停。
  - 不同 mode 对行为变化的权限不同，必须按当前 mode 的明确边界判断修改是否允许。
  - standards_compliance_correction 必须保持无业务行为、无外部语义和无实现路径变化。
  - confirmed_bugfix 在预期行为、根因证据和具体根因文件明确时，可以将错误行为修正为已确认的正确行为，但只允许在具体根因文件内做最小范围修改。
  - scope 只定义检查范围；editable_scope 才定义修改范围，读取上下文不代表获得修改权限。
  - standards_compliance_correction 每个 Step 默认 report_only；用户确认具体 issue_id 或批次后才记录修改授权。
  - interactive_seven_step 中，继续只执行一个授权批次；没有待执行批次时，只进入下一 Step 的只读检查。
  - 普通“继续”不得确认问题、创建授权、扩大范围、提升权限或切换模式。
  - 一个修正阶段只能消费一个授权批次；完成或失败后 authorization.consumed 必须为 true，修改权限立即失效。
  - 授权不得继承到下一 Step；模式切换时必须清空 current_authorized_batch、remediation.active 和 authorization。
  - 不得在这里保存长期环境事实、业务产物或跨运行上下文。
  - 技术栈事实和 Profile 匹配依据只来自项目环境档案与当前仓库证据；本 Runtime 不保存技术栈参数。

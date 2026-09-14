from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (REPOSITORY_ROOT / relative).read_text(encoding="utf-8")


def section(body: str, start: str, end: str) -> str:
    return body.split(start, 1)[1].split(end, 1)[0]


class CrossRuntimeReadinessContractTests(unittest.TestCase):
    def test_forward_state_ledger_implementations_cannot_drift(self) -> None:
        long_state = read(
            "skills/long-task-orchestrator/scripts/forward_state.py"
        ).replace('STATE_FILE = "long-workflow-state.json"', 'STATE_FILE = "<state-file>"')
        testing_state = read(
            "skills/testing-layer-runtime/scripts/forward_state.py"
        ).replace('STATE_FILE = "testing-workflow-state.json"', 'STATE_FILE = "<state-file>"')
        self.assertEqual(long_state, testing_state)

    def test_breaking_runtime_contract_changes_require_major_update(self) -> None:
        manifest = json.loads(read("skills-manifest.json"))
        self.assertGreaterEqual(int(manifest["release_version"].split(".")[0]), 1)
        for skill in (
            "planning-layer-runtime",
            "long-task-orchestrator",
            "testing-layer-runtime",
        ):
            self.assertGreaterEqual(
                int(manifest["skills"][skill]["version"].split(".")[0]), 1
            )

    def test_planning_dep_schema_is_canonical_and_has_complete_migration(self) -> None:
        formats = read(
            "skills/planning-layer-runtime/references/04-planning-format-spec.md"
        )
        responsibility = read(
            "skills/planning-layer-runtime/references/03-planning-doc-responsibility.md"
        )
        dep = section(formats, "DEP 格式：", "OPEN 格式：")

        for field in (
            "上游合同引用：",
            "required_for：",
            "target_environment：",
            "owner：",
            "earliest_required_stage：",
            "blocking_scope：",
            "safe_verification：",
            "ready_evidence_refs：",
            "superseded_by：",
            "status：",
        ):
            self.assertIn(field, dep)
        for status in (
            "ready_verified",
            "user_confirmed_ready",
            "pending_user_action",
            "external_pending",
            "blocked",
            "not_applicable",
            "superseded",
        ):
            self.assertIn(f"- {status}", dep)
        for legacy_status in ("- unknown\n", "- pending\n", "- verified\n", "- unavailable\n"):
            self.assertNotIn(legacy_status, dep)
        for old_status in ("`pending`", "`verified`", "`unknown`", "`unavailable`", "`superseded`"):
            self.assertIn(old_status, dep)
        self.assertIn("retired_without_replacement", dep)
        self.assertIn(
            "04-planning-format-spec.md#12-risk--dep--open-format", responsibility
        )

    def test_only_before_long_dependencies_block_long_readiness(self) -> None:
        responsibility = read(
            "skills/planning-layer-runtime/references/03-planning-doc-responsibility.md"
        )
        handoff = read(
            "skills/planning-layer-runtime/references/07-planning-conversation-runtime.md"
        )

        self.assertIn(
            "只有当前有效且 `earliest_required_stage: before_long` 的 DEP",
            responsibility,
        )
        self.assertIn(
            "`before_cloud_test | before_release` DEP 只阻断其 `blocking_scope`",
            responsibility,
        )
        self.assertIn("`superseded` DEP 必须先沿 `superseded_by` 解析", handoff)

    def test_new_runtime_schemas_have_one_canonical_definition(self) -> None:
        planning = "\n".join(
            read(str(path.relative_to(REPOSITORY_ROOT)))
            for path in (REPOSITORY_ROOT / "skills/planning-layer-runtime").rglob("*.md")
        )
        testing = "\n".join(
            read(str(path.relative_to(REPOSITORY_ROOT)))
            for path in (REPOSITORY_ROOT / "skills/testing-layer-runtime").rglob("*.md")
        )
        long = "\n".join(
            read(str(path.relative_to(REPOSITORY_ROOT)))
            for path in (REPOSITORY_ROOT / "skills/long-task-orchestrator").rglob("*.md")
        )

        self.assertEqual(planning.count("DEP 格式："), 1)
        self.assertEqual(planning.count("database_persistence_contract:"), 1)
        self.assertEqual(testing.count("## business-journey-test-matrix.md 格式"), 1)
        self.assertEqual(testing.count("## release-handoff.md 格式"), 1)
        self.assertEqual(testing.count("## Deployment Revision Reconciliation Gate"), 1)
        self.assertEqual(long.count("required_validation_matrix:"), 1)

    def test_planning_stage_two_owns_safe_before_long_readiness(self) -> None:
        interaction = read(
            "skills/planning-layer-runtime/references/10-planning-document-interaction-runtime.md"
        )
        handoff = read(
            "skills/planning-layer-runtime/references/07-planning-conversation-runtime.md"
        )

        for term in (
            "before_long / before_cloud_test / before_release",
            "agent_provisionable_in_confirmed_task",
            "user_or_external_prerequisite",
            "不读取、输出或持久化值",
            "user_confirmed_ready",
            "准备 13 时仍有 `before_long` 未就绪项",
        ):
            self.assertIn(term, interaction)
        self.assertIn("execution_prerequisite_readiness:", handoff)
        self.assertIn("before_long_status: passed", handoff)
        self.assertIn("unresolved_before_long: []", handoff)

    def test_operational_profile_is_reused_without_polluting_discovery(self) -> None:
        formats = read(
            "skills/planning-layer-runtime/references/04-planning-format-spec.md"
        )
        interaction = read(
            "skills/planning-layer-runtime/references/07-planning-conversation-runtime.md"
        )

        self.assertIn("deployment_identity:", formats)
        self.assertIn("runtime_observation:", formats)
        self.assertIn("只在没有可靠身份时识别一次", formats)
        self.assertIn("不得每期重复询问", formats)
        self.assertIn("不保存原始日志", interaction)
        self.assertIn("不得改变第一阶段问法", interaction)
        self.assertIn("09 架构/容量、11 运行验证、12 风险和 13 任务边界", interaction)

    def test_physical_data_contract_reaches_long_without_a_second_schema(self) -> None:
        planning_gate = read(
            "skills/planning-layer-runtime/references/07-planning-conversation-runtime.md"
        )
        long_preflight = read(
            "skills/long-task-orchestrator/references/landing-checklist-preflight.md"
        )
        long_execution = read(
            "skills/long-task-orchestrator/references/task-execution.md"
        )

        self.assertIn("physical_data_design", planning_gate)
        self.assertIn("contract_refs.architecture_and_database", long_preflight)
        self.assertIn("prohibited_extra_storage_units: true", long_preflight)
        self.assertIn("数据库合同外持久化单元", long_execution)

    def test_long_refuses_unready_planning_prerequisites(self) -> None:
        long_skill = read("skills/long-task-orchestrator/SKILL.md")
        preflight = read(
            "skills/long-task-orchestrator/references/landing-checklist-preflight.md"
        )
        context = read(
            "skills/long-task-orchestrator/references/current-runtime-context.md"
        )

        for body in (long_skill, preflight):
            self.assertIn("execution_prerequisite_readiness", body)
            self.assertIn("before_long_status: passed", body)
            self.assertIn("unresolved_before_long: []", body)
        self.assertIn("execution_prerequisite_readiness_status", context)
        self.assertIn("不复制配置步骤、秘密或 DEP 正文", context)

    def test_testing_uses_business_journeys_and_keeps_one_result_source(self) -> None:
        core = read("skills/testing-layer-runtime/references/01-test-runtime-core.md")
        writeback = read("skills/testing-layer-runtime/references/05-test-writeback.md")

        self.assertIn("business-journey-test-matrix.md", core)
        self.assertIn("每个适用 P0/P1 FLOW", core)
        self.assertIn("本地业务/E2E", core)
        self.assertIn("云端业务/E2E", core)
        self.assertIn("每个 P0 FLOW 的正向旅程都要求云端 E2E", core)
        self.assertIn("受当前变更影响", core)
        self.assertIn("exact deployed revision", core)
        self.assertIn("不保存测试项正式状态", writeback)
        self.assertIn("test-validation-results.md", writeback)
        self.assertIn("单元测试、组件测试、接口片段", core)
        self.assertIn("不能独立关闭 FLOW", core)

    def test_downstream_prerequisite_status_has_explicit_owner_and_release_snapshot(self) -> None:
        planning = read(
            "skills/planning-layer-runtime/references/07-planning-conversation-runtime.md"
        )
        core = read("skills/testing-layer-runtime/references/01-test-runtime-core.md")
        writeback = read("skills/testing-layer-runtime/references/05-test-writeback.md")

        self.assertIn("Planning 截止状态快照", planning)
        self.assertIn("实际核验状态由 Testing Runtime 的正式结果项承载", planning)
        self.assertIn("item_type: environment_prerequisite", writeback)
        self.assertIn("dependency_ref:", writeback)
        self.assertIn("required_stage: before_cloud_test", writeback)
        self.assertIn("不回写 Planning SoT", core)
        self.assertIn("## release-handoff.md 格式", writeback)
        self.assertIn("before_release_dependency_refs", writeback)
        self.assertIn("release_gate_owner:", writeback)
        self.assertIn("不承担发布后的持续状态", writeback)

    def test_cloud_required_evidence_is_bound_to_current_deployment_revision(self) -> None:
        core = read("skills/testing-layer-runtime/references/01-test-runtime-core.md")
        environments = read(
            "skills/testing-layer-runtime/references/02-test-environment-gates.md"
        )
        writeback = read("skills/testing-layer-runtime/references/05-test-writeback.md")

        self.assertIn("current_deployment_revision:", writeback)
        self.assertIn("identity_mode:", writeback)
        self.assertIn("component_revisions:", writeback)
        self.assertIn("deployment_set_digest", writeback)
        self.assertIn(
            "deployment_revision_ref: test-runtime-state.md#current_deployment_revision",
            writeback,
        )
        self.assertIn("environment_revision_ref:", writeback)
        for field in (
            "target_environment:",
            "revision_kind:",
            "revision:",
            "deployment_identity_ref:",
            "component_revision_refs:",
            "flow_refs:",
            "valid:",
            "invalidated_by:",
        ):
            self.assertIn(field, writeback)
        gate_ref = "05-test-writeback.md#deployment-revision-reconciliation-gate"
        self.assertIn(gate_ref, core)
        self.assertIn(gate_ref, environments)
        self.assertNotIn("只有明确证明未受影响的 journey refs 才能保留", environments)
        self.assertIn("`stale` 是证据有效性，不是测试项 `status`", writeback)

    def test_deployment_revision_reconciliation_is_ordered_and_recoverable(self) -> None:
        writeback = read("skills/testing-layer-runtime/references/05-test-writeback.md")
        gate = section(
            writeback,
            "## Deployment Revision Reconciliation Gate",
            "## release-handoff.md 格式",
        )

        ordered_steps = (
            "收敛当前项",
            "写事务意图",
            "失效旧关闭关系",
            "验证中间状态",
            "提交新身份",
        )
        positions = [gate.index(step) for step in ordered_steps]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(writeback.count("唯一持久化顺序："), 1)
        for field in (
            "transition_id",
            "from_identity",
            "candidate_identity",
            "invalidated_evidence_refs",
            "removed_result_refs",
            "opened_gap_refs",
        ):
            self.assertIn(field, writeback)
        for event_type in (
            "environment_switched",
            "deployment_revision_reconciliation_started",
            "deployment_revision_reconciliation_completed",
            "deployment_revision_reconciliation_blocked",
        ):
            self.assertIn(f"- `{event_type}`", writeback)
        self.assertIn("in_progress | blocked", gate)
        self.assertIn("禁止任何 cloud-required 测试", writeback)
        self.assertIn("不得根据当前 revision、对话记忆或部分失效结果猜测事务已完成", gate)

    def test_release_handoff_treats_every_non_pass_status_as_unresolved(self) -> None:
        core = read("skills/testing-layer-runtime/references/01-test-runtime-core.md")
        writeback = read("skills/testing-layer-runtime/references/05-test-writeback.md")
        status_section = section(core, "## 状态枚举", "## MANUAL-OP 覆盖 Case")
        release_section = section(
            writeback, "## release-handoff.md 格式", "## 回写时机"
        )
        statuses = re.findall(r"\| `([^`]+)` \|", status_section)
        pass_statuses = {"verified", "verified_by_user_report"}

        self.assertEqual(pass_statuses, set(statuses) & pass_statuses)
        for status in set(statuses) - pass_statuses:
            with self.subTest(status=status):
                self.assertIn(status, release_section)

    def test_every_formal_test_item_uses_durable_revision_bound_checkpoint(self) -> None:
        skill = read("skills/testing-layer-runtime/SKILL.md")
        core = read("skills/testing-layer-runtime/references/01-test-runtime-core.md")
        writeback = read("skills/testing-layer-runtime/references/05-test-writeback.md")

        for item_type in (
            "case",
            "manual_op",
            "real_device",
            "deployed_e2e",
            "server_verification",
            "environment_prerequisite",
        ):
            self.assertIn(item_type, writeback)
        self.assertIn("每个正式 `item_type`", skill)
        checkpoint = section(core, "### 测试开始前检查点", "### 测试完成后检查点")
        self.assertIn("environment_revision_ref:", checkpoint)
        self.assertIn("唯一枚举", core)

    def test_testing_consumes_long_gate_and_closes_retest_loop(self) -> None:
        testing_skill = read("skills/testing-layer-runtime/SKILL.md")
        writeback = read("skills/testing-layer-runtime/references/05-test-writeback.md")

        self.assertIn("required_validation_gate.result", testing_skill)
        self.assertIn("必须为 `passed`", testing_skill)
        self.assertIn("machine execution receipt", testing_skill)
        self.assertIn("long-readiness-receipt/v2", writeback)
        self.assertIn("execution_receipt_ref", writeback)
        self.assertIn("waiting_redeploy", writeback)
        self.assertIn("replacement_required_validation_gate_ref", writeback)
        self.assertIn("retest_result_refs", writeback)
        self.assertIn("只记录“代码已改”", writeback)


if __name__ == "__main__":
    unittest.main()

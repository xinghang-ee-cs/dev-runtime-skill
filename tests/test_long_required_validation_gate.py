from __future__ import annotations

import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
LONG_ROOT = REPOSITORY_ROOT / "skills/long-task-orchestrator"


def read(relative: str) -> str:
    return (LONG_ROOT / relative).read_text(encoding="utf-8")


class LongRequiredValidationGateContractTests(unittest.TestCase):
    def test_completion_requires_current_passed_evidence(self) -> None:
        skill = read("SKILL.md")
        execution = read("references/task-execution.md")

        for body in (skill, execution):
            self.assertIn("required_validation_matrix_current_and_complete", body)
            self.assertIn("all_required_automated_validation_passed", body)
            self.assertIn("local_runnable_gate_passed", body)
            self.assertNotIn("minimum_capability_validation_passed_or_blocked", body)
            self.assertNotIn("automated_validation_recorded", body)

    def test_required_matrix_has_one_instance_source_and_one_evidence_source(self) -> None:
        baseline = read("references/project-execution-baseline.md")
        gates = read("references/validation-gates.md")
        results = read("references/validation-results.md")

        self.assertIn("required_validation_matrix:", baseline)
        self.assertIn(
            "current phase required_validation_matrix -> Phase Runtime Directory/project-execution-baseline.md",
            gates,
        )
        self.assertIn(
            "executed evidence -> Phase Runtime Directory/validation-results.md", gates
        )
        self.assertIn(
            "本文件不重新定义要求", results
        )

    def test_required_validation_cannot_be_skipped_or_deferred_to_testing(self) -> None:
        gates = read("references/validation-gates.md")
        state_machine = read("references/task-state-machine.md")
        handoff = read("references/validation-results.md")

        self.assertIn("required result in failed|blocked|not_run", gates)
        self.assertIn("required validation skipped with a reason", gates)
        self.assertIn("任一 `required` 项不可执行、失败、阻断或缺失时转入 `BLOCKED`", state_machine)
        self.assertIn("required_validation_gate:", handoff)
        self.assertIn("不得进入 `ready_for_local_test`", handoff)

    def test_local_business_e2e_scope_is_mapped_or_explicitly_handed_off(self) -> None:
        baseline = read("references/project-execution-baseline.md")
        gates = read("references/validation-gates.md")

        self.assertIn("planning_test_refs", baseline)
        self.assertIn("P0/P1 业务/E2E TEST", gates)
        self.assertIn("Long Handoff `manual_required`", gates)
        self.assertIn("不得既遗漏于 Matrix，又遗漏于 `manual_required`", gates)

    def test_original_false_positive_shape_is_rejected_generically(self) -> None:
        gates = read("references/validation-gates.md")

        self.assertIn("typecheck used as build evidence", gates)
        self.assertIn(
            "build exit zero without required artifact/loadability postcondition", gates
        )
        self.assertIn(
            "process compiler/watch reports zero errors but target process never becomes ready",
            gates,
        )
        self.assertIn(
            "config helper exists but required keys are not proven bound to the target process",
            gates,
        )

    def test_gate_is_project_derived_not_incident_specific(self) -> None:
        generic_contract = "\n".join(
            [
                read("references/project-execution-baseline.md"),
                read("references/validation-gates.md"),
                read("references/validation-results.md"),
            ]
        )

        for incident_specific_term in (
            "NestJS",
            "Prisma",
            "DATABASE_URL",
            "dist/main",
            "localhost:5173",
        ):
            self.assertNotIn(incident_specific_term, generic_contract)

    def test_required_pass_is_bound_to_machine_executed_postconditions(self) -> None:
        skill = read("SKILL.md")
        baseline = read("references/project-execution-baseline.md")
        gates = read("references/validation-gates.md")
        results = read("references/validation-results.md")
        runner = read("scripts/run_long_validation.py")

        self.assertIn("run-long-validation.sh", skill)
        self.assertIn("machine_execution:", baseline)
        self.assertIn("postcondition_probes:", baseline)
        self.assertIn("shell=False", gates)
        self.assertIn("execution_receipt_ref", results)
        self.assertIn("execute_requirement", runner)

    def test_formal_validation_closes_the_phase_not_each_task(self) -> None:
        skill = read("SKILL.md")
        execution = read("references/task-execution.md")
        state_machine = read("references/task-state-machine.md")

        self.assertIn("以“本期”为唯一正式闭环", skill)
        self.assertIn("不把 TASK 单独闭环", execution)
        self.assertIn("等待本期验证", state_machine)
        self.assertNotIn("必须逐项调用 `scripts/run-long-validation.sh|ps1`", execution.split("当前期所有 scope 内实现均进入", 1)[0])

    def test_safe_boundary_is_an_agent_prompt_declaration(self) -> None:
        baseline = read("references/project-execution-baseline.md")
        gates = read("references/validation-gates.md")

        self.assertIn("Prompt/流程约束", baseline)
        self.assertIn("runner 只校验枚举并记录", gates)
        self.assertIn("不承担代码级环境隔离", gates)


if __name__ == "__main__":
    unittest.main()

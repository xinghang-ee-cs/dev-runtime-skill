from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = (
    REPOSITORY_ROOT
    / "skills/testing-layer-runtime/scripts/validate_testing_runtime.py"
)
sys.path.insert(0, str(VALIDATOR.parent))
from forward_state import advance_ledger, canonical_digest  # noqa: E402
from validate_testing_runtime import (  # noqa: E402
    Result,
    TESTING_WORKFLOW,
    anchored_records,
    canonical_release_snapshot_digest,
    ci_yaml_job_ids,
    entries,
    system_risk_digest,
    testing_result_records,
    testing_transition_allowed,
    validate_evidence_content,
    validate_yaml_subset,
)


LONG_REPOSITORY_REVISION = "sha256:" + "1" * 64


def multiline_ci_config(provider: str, quote: str) -> str:
    if provider == "github_actions":
        return (
            "name: build\non: push\njobs:\n  build:\n"
            "    runs-on: ubuntu-latest\n    env:\n"
            f"      EXAMPLE: {quote}sample\n  runtime-tests:\n    steps: []\n{quote}\n"
            "    steps:\n      - run: cargo check\n"
        )
    return (
        f"variables:\n  EXAMPLE: {quote}sample\nruntime-tests:\n"
        f"  script: echo fake\n{quote}\nbuild:\n  script: cargo check\n"
    )


def system_risks(deployed: bool = False) -> str:
    categories = (
        "integration_contracts", "resource_bounds", "credential_isolation",
        "health_semantics", "external_io_bounds", "failure_recovery",
        "data_integrity", "environment_binding", "deployment_lifecycle",
    )
    body = (
        "system_risk_coverage:\n"
        "  schema_version: 1\n"
        f"  deployment_in_scope: {'true' if deployed else 'false'}\n"
        "  scope_alignment: aligned\n"
        "  fact_evidence_refs: [EVIDENCE-LOCAL-1]\n"
        f"  features: {'[deployment]' if deployed else '[]'}\n"
        "  categories:\n"
    )
    for category in categories:
        body += f"    - category: {category}\n"
        if deployed and category in {"environment_binding", "deployment_lifecycle"}:
            body += (
                "      applicability: required\n"
                "      reason: deployment target requires runtime verification\n"
                "      checks:\n"
                f"        - check_id: SYS-{category}\n"
                "          test_layer: deployment\n"
                "          contract_refs: [requirement-and-scope.md]\n"
                "          assertion: approved deployment behavior is effective\n"
                "          verification_kind: configuration_check\n"
                "          result_refs: [TEST-CLOUD-1]\n"
                "          regression:\n"
                "            requirement: not_applicable\n"
                "            reason: release owner rechecks target bindings after each deployment change\n"
            )
        else:
            body += (
                "      applicability: not_applicable\n"
                "      reason: inspected fixture has no relevant runtime mechanism\n"
                "      checks: []\n"
            )
    return body


def identity_digest(deployment: str, configuration: str) -> str:
    payload = {
        "target_environment": "staging",
        "identity_mode": "aggregate_deployment",
        "revision_kind": "deployment_id",
        "revision": deployment,
        "component_revisions": [],
        "runtime_configuration_identity": {
            "status": "known",
            "revision_kind": "platform_configuration_revision",
            "revision": configuration,
        },
    }
    serialized = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(serialized).hexdigest()


def known_identity_fields(deployment: str, configuration: str) -> str:
    return textwrap.dedent(
        f"""
        status: known
        target_environment: staging
        identity_mode: aggregate_deployment
        revision_kind: deployment_id
        revision: {deployment}
        identity_digest: {identity_digest(deployment, configuration)}
        evidence_ref: deploy-evidence.md
        component_revisions: []
        runtime_configuration_identity:
          status: known
          revision_kind: platform_configuration_revision
          revision: {configuration}
          evidence_ref: config-evidence.md
          secret_values_included: false
        """
    ).strip()


def state(
    deployment_status: str = "not_applicable",
    deployment: str = "not_applicable",
    configuration: str = "not_applicable",
    active_release_status: str = "not_generated",
    release_digest: str = "not_applicable",
    reconciliation_status: str = "not_required",
) -> str:
    if deployment_status == "known":
        digest = identity_digest(deployment, configuration)
        deployment_fields = known_identity_fields(deployment, configuration)
    else:
        digest = "not_applicable"
        deployment_fields = textwrap.dedent(
            """
              status: not_applicable
              target_environment: not_applicable
              identity_mode: not_applicable
              revision_kind: not_applicable
              revision: not_applicable
              identity_digest: not_applicable
              evidence_ref: not_applicable
              component_revisions: []
              runtime_configuration_identity:
                status: not_applicable
                revision_kind: not_applicable
                revision: not_applicable
                evidence_ref: not_applicable
                secret_values_included: false
            """
        ).strip()

    transition_id = "TRANSITION-1" if reconciliation_status != "not_required" else "not_applicable"
    candidate_digest = digest if reconciliation_status == "completed" else "not_applicable"
    completed_at = "2026-08-25T10:00:00Z" if reconciliation_status == "completed" else "null"
    overall_status = "blocked" if reconciliation_status in {"in_progress", "blocked"} else "in_progress"
    snapshot_ref = "release-handoff.md" if active_release_status != "not_generated" else "not_applicable"
    snapshot_id = "RELEASE-1" if active_release_status != "not_generated" else "not_applicable"
    invalidated_by = "TRANSITION-1" if active_release_status == "invalidated" else "null"
    bound_digest = release_digest if active_release_status != "not_generated" else "not_applicable"
    snapshot_digest = "not_applicable"
    if active_release_status != "not_generated":
        snapshot_digest = re.search(
            r"(?m)^snapshot_digest:\s*(\S+)",
            release_handoff(deployment, configuration, active_release_status),
        ).group(1)
    if active_release_status in {"current", "invalidated"}:
        current_phase = "release_handoff"
    elif deployment_status == "known":
        current_phase = "cloud_testing"
    else:
        current_phase = "manual_testing"
    if reconciliation_status == "completed":
        reconciliation_identities = (
            "  from_identity:\n"
            + textwrap.indent(known_identity_fields("deploy-1", "config-1"), "    ")
            + "\n  candidate_identity:\n"
            + textwrap.indent(deployment_fields, "    ")
            + f"\n  from_identity_digest: {identity_digest('deploy-1', 'config-1')}\n"
        )
        started_at = "2026-08-25T09:50:00Z"
    else:
        reconciliation_identities = (
            "  from_identity: not_applicable\n"
            "  candidate_identity: not_applicable\n"
            "  from_identity_digest: not_applicable\n"
        )
        started_at = "null"

    return (
        "intake_binding:\n"
        "  current_test_epoch: phase-01\n"
        "  writeback_target: .\n"
        "  planning_handoff_ref: planning-handoff.yaml\n"
        "  planning_baseline_revision: PLAN-1\n"
        "  long_testing_handoff_ref: testing-handoff.md\n"
        "  long_runtime_epoch: LONG-1\n"
        "  required_validation_matrix_ref: project-execution-baseline.md#required_validation_matrix\n"
        "  required_validation_matrix_revision: MATRIX-1\n"
        "  required_validation_gate_result: passed\n"
        "  intake_verified_at: 2026-08-25T09:00:00Z\n"
        f"current_phase: {current_phase}\n"
        "current_environment: staging\n"
        "business_journey_matrix_ref: business-journey-test-matrix.md\n"
        "business_journey_matrix_revision: JOURNEY-1\n"
        "current_deployment_revision:\n"
        f"{textwrap.indent(deployment_fields, '  ')}\n"
        "deployment_revision_reconciliation:\n"
        f"  status: {reconciliation_status}\n"
        f"  transition_id: {transition_id}\n"
        f"{reconciliation_identities}"
        f"  candidate_identity_digest: {candidate_digest}\n"
        "  invalidated_evidence_refs: []\n"
        "  removed_result_refs: []\n"
        "  opened_gap_refs: []\n"
        "  invalidated_release_handoff_ref: not_applicable\n"
        f"  started_at: {started_at}\n"
        f"  completed_at: {completed_at}\n"
        "active_release_handoff:\n"
        f"  status: {active_release_status}\n"
        f"  snapshot_id: {snapshot_id}\n"
        f"  snapshot_ref: {snapshot_ref}\n"
        f"  bound_deployment_identity_digest: {bound_digest}\n"
        f"  snapshot_digest: {snapshot_digest}\n"
        f"  invalidated_by: {invalidated_by}\n"
        "current_item: null\n"
        "current_item_status: null\n"
        "last_completed_item: TEST-1\n"
        "next_executable_item: null\n"
        "last_durable_checkpoint_at: 2026-08-25T10:00:00Z\n"
        "resume_required: false\n"
        f"overall_status: {overall_status}\n"
        "blockers: []\n"
        "last_updated_at: 2026-08-25T10:00:00Z\n"
    )


def release_handoff(
    deployment: str,
    configuration: str,
    status: str = "current",
) -> str:
    digest = identity_digest(deployment, configuration)
    invalidated_by = "TRANSITION-1" if status == "invalidated" else "null"
    invalidated_at = "2026-08-25T10:00:00Z" if status == "invalidated" else "null"
    body = textwrap.dedent(
        f"""
        handoff_type: release_prerequisite_snapshot
        snapshot_id: RELEASE-1
        snapshot_digest: __SNAPSHOT_DIGEST__
        snapshot_status: {status}
        generated_at: 2026-08-25T09:30:00Z
        invalidated_by: {invalidated_by}
        invalidated_at: {invalidated_at}
        current_test_epoch: phase-01
        planning_handoff_ref: planning-handoff.yaml
        planning_baseline_revision: PLAN-1
        testing_runtime_ref: test-runtime-state.md
        long_testing_handoff_ref: testing-handoff.md
        required_validation_gate_ref: testing-handoff.md#required_validation_gate
        business_journey_matrix_ref: business-journey-test-matrix.md
        business_journey_matrix_revision: JOURNEY-1
        current_deployment_revision_ref: test-runtime-state.md#current_deployment_revision
        deployment_identity_snapshot:
          status: known
          target_environment: staging
          identity_mode: aggregate_deployment
          revision_kind: deployment_id
          revision: {deployment}
          identity_digest: {digest}
          evidence_ref: deploy-evidence.md
          component_revisions: []
          runtime_configuration_identity:
            status: known
            revision_kind: platform_configuration_revision
            revision: {configuration}
            evidence_ref: config-evidence.md
            secret_values_included: false
        business_journey_coverage_status: verified
        system_risk_coverage_digest: {system_risk_digest(entries(system_risks(True)))}
        release_readiness_status: ready
        required_result_refs: [TEST-LOCAL-1, TEST-CLOUD-1]
        open_finding_refs: []
        dependencies: []
        unresolved_dependency_refs: []
        """
    ).strip() + "\n"
    digest_value = canonical_release_snapshot_digest(entries(body))
    return body.replace("__SNAPSHOT_DIGEST__", digest_value)


def long_testing_handoff() -> str:
    return textwrap.dedent(
        """
        runtime_epoch: LONG-1
        planning_handoff_ref: planning-handoff.yaml
        planning_baseline_revision: PLAN-1
        executed_task_contract_revisions: [TASK-1@1]
        automated_passed:
          - id: AUTO-1
            source_validation_id: VALIDATION-1
        automated_failed: []
        automated_skipped: []
        manual_required: []
        required_validation_gate:
          matrix_ref: project-execution-baseline.md#required_validation_matrix
          matrix_revision: MATRIX-1
          effective_validation_ids: [VALIDATION-1]
          result: passed
        formal_acceptance_record_path: acceptance.md
        acceptance_status: not_started
        owner_runtime: testing-layer-runtime
        validator_receipt_ref: long-readiness-receipt.json
        """
    ).strip() + "\n"


def write_long_readiness_receipt(
    runtime: Path, planning_handoff_path: Path | None = None
) -> None:
    validation_text = (runtime / "validation-results.md").read_text(encoding="utf-8")
    validation_matrix_match = re.search(
        r"(?m)^matrix_revision:\s*(\S+)", validation_text
    )
    validation_matrix_revision = (
        validation_matrix_match.group(1) if validation_matrix_match else "MATRIX-1"
    )
    machine_receipt = {
        "schema_version": "long-machine-execution-receipt/v2",
        "generated_by": "long-machine-runner/v2",
        "runtime_epoch": "LONG-1",
        "matrix_revision": validation_matrix_revision,
        "repository_revision": LONG_REPOSITORY_REVISION,
        "requirement_id": "REQ-1",
        "delivery_unit_id": "UNIT-1",
        "validation_id": "VALIDATION-1",
        "attempt": 1,
        "safe_execution_boundary": "local",
        "machine_execution": {
            "working_directory_ref": ".",
            "default_timeout_seconds": 30,
            "postcondition_probes": [],
        },
        "postcondition_results": [],
        "result": "passed",
        "generated_at": "2026-08-25T08:59:00Z",
    }
    machine_receipt["receipt_digest"] = canonical_digest(machine_receipt)
    machine_path = runtime / "machine-execution-receipts/VALIDATION-1.json"
    machine_path.parent.mkdir(parents=True, exist_ok=True)
    machine_path.write_text(
        json.dumps(machine_receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    history = []
    previous_digest = "genesis"
    previous_stage = "not_started"
    for sequence, stage_name in enumerate(
        ("preflight", "execution", "completion_validation", "ready_for_local_test"),
        start=1,
    ):
        event = {
            "sequence": sequence,
            "cycle": 1,
            "cycle_kind": "initial",
            "from_stage": previous_stage,
            "to_stage": stage_name,
            "transitioned_at": f"2026-08-25T09:0{sequence}:00Z",
            "previous_digest": previous_digest,
        }
        event["event_digest"] = canonical_digest(event)
        history.append(event)
        previous_stage = stage_name
        previous_digest = event["event_digest"]
    workflow = {
        "schema_version": "forward-workflow/v1",
        "workflow": "long-task-orchestrator",
        "runtime_id": "LONG-1",
        "current_stage": "ready_for_local_test",
        "current_cycle": 1,
        "current_cycle_kind": "initial",
        "history_digest": previous_digest,
        "history": history,
    }
    (runtime / "long-workflow-state.json").write_text(
        json.dumps(workflow, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    artifact_names = (
        "project-execution-baseline.md",
        "validation-results.md",
        "testing-handoff.md",
        "long-workflow-state.json",
        "machine-execution-receipts/VALIDATION-1.json",
    )
    artifacts = [
        {
            "kind": "runtime",
            "ref": name,
            "sha256": hashlib.sha256((runtime / name).read_bytes()).hexdigest(),
        }
        for name in artifact_names
    ]
    artifacts.append(
        {
            "kind": "source",
            "ref": "planning-handoff.yaml",
            "sha256": hashlib.sha256(
                (planning_handoff_path or runtime / "planning-handoff.yaml").read_bytes()
            ).hexdigest(),
        }
    )
    receipt = {
        "schema_version": "long-readiness-receipt/v2",
        "runtime_epoch": "LONG-1",
        "planning_baseline_revision": "PLAN-1",
        "active_change_revision": "not_applicable",
        "matrix_revision": "MATRIX-1",
        "repository_revision": LONG_REPOSITORY_REVISION,
        "effective_validation_ids": ["VALIDATION-1"],
        "workflow_history_digest": previous_digest,
        "artifacts": artifacts,
    }
    receipt["receipt_digest"] = canonical_digest(receipt)
    (runtime / "long-readiness-receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


class TestingRuntimeValidatorTests(unittest.TestCase):
    def run_validator(
        self,
        state_body: str,
        release_body: str | None = None,
        extra_files: dict[str, str] | None = None,
        expect_final: bool = False,
        materialize_evidence: bool = True,
        omit_long_receipt: bool = False,
        long_receipt_schema: str | None = None,
        post_receipt_files: dict[str, str] | None = None,
        mutate_evidence_after_freeze: bool = False,
        workflow_deployment_digest: str | None = None,
        tamper_release_after_seal: bool = False,
        advance_stage: str | None = None,
        sibling_long_runtime: bool = False,
        print_system_risk: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            runtime = workspace / "testing-runtime" if sibling_long_runtime else workspace
            runtime.mkdir(exist_ok=True)
            long_runtime = workspace / "long-runtime" if sibling_long_runtime else runtime
            long_runtime.mkdir(exist_ok=True)
            planning_handoff_path = (
                workspace / "planning-handoff.yaml"
                if sibling_long_runtime else runtime / "planning-handoff.yaml"
            )
            if sibling_long_runtime:
                state_body = state_body.replace(
                    "long_testing_handoff_ref: testing-handoff.md",
                    "long_testing_handoff_ref: ../long-runtime/testing-handoff.md",
                ).replace(
                    "required_validation_matrix_ref: project-execution-baseline.md",
                    "required_validation_matrix_ref: ../long-runtime/project-execution-baseline.md",
                )
            (runtime / "test-runtime-state.md").write_text(
                state_body, encoding="utf-8"
            )
            long_handoff = long_testing_handoff()
            if sibling_long_runtime:
                long_handoff = long_handoff.replace(
                    "matrix_ref: project-execution-baseline.md",
                    "matrix_ref: ../long-runtime/project-execution-baseline.md",
                )
            (long_runtime / "testing-handoff.md").write_text(long_handoff, encoding="utf-8")
            base_files = {
                "planning-handoff.yaml": """```yaml
handoff_type: execution_ready
requires_execution_handoff: true
planning_baseline_revision: PLAN-1
execution_prerequisite_readiness:
  before_long_status: passed
  before_release_dependency_refs: []
  unresolved_before_long: []
incremental_execution_contract:
  planning_baseline_revision: PLAN-1
  execute_only: [TASK-1@1]
  resume_only: []
  reexecute_affected_part: []
  context_only: []
  completed_locked: []
  cancelled: []
handoff_role_mapping:
  - role: Requirement and Scope
    path: requirement-and-scope.md
  - role: Test and Acceptance Plan
    path: planning-test-plan.md
```
""",
                "requirement-and-scope.md": """### FLOW-1：核心业务旅程

关联后续测试：
- TEST-PLAN-1

Priority：P0
""",
                "planning-test-plan.md": """### TEST-PLAN-1：核心业务旅程测试

关联 FLOW：FLOW-1

环境证明要求：
- 本地业务 / E2E：required，从真实入口到终态
- 部署后云端业务 / E2E：not_applicable，本期无部署目标
""",
                "project-execution-baseline.md": """```yaml
required_validation_matrix:
  matrix_revision: MATRIX-1
```
""",
                "validation-results.md": """```yaml
validation_id: VALIDATION-1
result: passed
matrix_revision: MATRIX-1
execution_receipt_ref: machine-execution-receipts/VALIDATION-1.json
evidence: [machine-execution-receipts/VALIDATION-1.json]
```
""",
                "test-execution-events.md": """```yaml
- event_type: deployment_revision_reconciliation_started
  transition_id: TRANSITION-1
- event_type: deployment_revision_reconciliation_completed
  transition_id: TRANSITION-1
```
""",
            }
            def fixture_path(name: str) -> Path:
                if name == "planning-handoff.yaml":
                    return planning_handoff_path
                if name in {"project-execution-baseline.md", "validation-results.md"}:
                    return long_runtime / name
                return runtime / name

            for name, body in base_files.items():
                fixture_path(name).write_text(body, encoding="utf-8")
            if release_body is not None:
                release_body = re.sub(
                    r"(?m)^snapshot_digest:\s*\S+",
                    "snapshot_digest: __SNAPSHOT_DIGEST__",
                    release_body,
                )
                release_body = release_body.replace(
                    "__SNAPSHOT_DIGEST__",
                    canonical_release_snapshot_digest(entries(release_body)),
                )
                (runtime / "release-handoff.md").write_text(
                    release_body, encoding="utf-8"
                )
                sealed_digest = re.search(
                    r"(?m)^snapshot_digest:\s*(\S+)", release_body
                ).group(1)
                state_path = runtime / "test-runtime-state.md"
                state_path.write_text(
                    re.sub(
                        r"(?m)^(  snapshot_digest:)\s*\S+",
                        rf"\1 {sealed_digest}",
                        state_path.read_text(encoding="utf-8"),
                    ),
                    encoding="utf-8",
                )
                if tamper_release_after_seal:
                    release_path = runtime / "release-handoff.md"
                    release_path.write_text(
                        release_path.read_text(encoding="utf-8").replace(
                            "generated_at: 2026-08-25T09:30:00Z",
                            "generated_at: 2026-08-25T09:31:00Z",
                        ),
                        encoding="utf-8",
                    )
            for name, body in (extra_files or {}).items():
                if sibling_long_runtime and name == "business-journey-test-matrix.md":
                    body = body.replace("testing-handoff.md", "../long-runtime/testing-handoff.md")
                fixture_path(name).parent.mkdir(parents=True, exist_ok=True)
                fixture_path(name).write_text(body, encoding="utf-8")
            write_long_readiness_receipt(long_runtime, planning_handoff_path)
            if long_receipt_schema is not None:
                long_receipt_path = long_runtime / "long-readiness-receipt.json"
                long_receipt = json.loads(
                    long_receipt_path.read_text(encoding="utf-8")
                )
                long_receipt["schema_version"] = long_receipt_schema
                long_receipt.pop("receipt_digest", None)
                long_receipt["receipt_digest"] = canonical_digest(long_receipt)
                long_receipt_path.write_text(
                    json.dumps(long_receipt, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            if omit_long_receipt:
                (long_runtime / "long-readiness-receipt.json").unlink()
            for name, body in (post_receipt_files or {}).items():
                (runtime / name).write_text(body, encoding="utf-8")
            if materialize_evidence:
                for markdown_path in runtime.glob("*.md"):
                    for evidence_ref in re.findall(
                        r"(?m)^\s*path:\s*((?:evidence|manual-evidence)/[^\s#]+)",
                        markdown_path.read_text(encoding="utf-8"),
                    ):
                        evidence_path = runtime / evidence_ref
                        evidence_path.parent.mkdir(parents=True, exist_ok=True)
                        if not evidence_path.is_file():
                            evidence_path.write_text(
                                f"durable evidence for {evidence_ref}\n", encoding="utf-8"
                            )
                evidence_index = runtime / "test-evidence-index.md"
                if evidence_index.is_file():
                    evidence_body = evidence_index.read_text(encoding="utf-8")

                    def freeze_evidence(match: re.Match[str]) -> str:
                        indent, evidence_ref = match.groups()
                        evidence_path = runtime / evidence_ref
                        if not evidence_path.is_file():
                            return match.group(0)
                        digest = "sha256:" + hashlib.sha256(
                            evidence_path.read_bytes()
                        ).hexdigest()
                        return f"{indent}path: {evidence_ref}\n{indent}content_sha256: {digest}"

                    evidence_body = re.sub(
                        r"(?m)^(\s*)path:\s*([^\s#]+)$",
                        freeze_evidence,
                        evidence_body,
                    )
                    evidence_index.write_text(evidence_body, encoding="utf-8")
                    if mutate_evidence_after_freeze:
                        evidence_path = runtime / "evidence/local-trace.zip"
                        evidence_path.write_text(
                            "mutated after evidence index freeze\n", encoding="utf-8"
                        )
            phase_match = re.search(r"(?m)^current_phase:\s*(\S+)", state_body)
            phase = phase_match.group(1) if phase_match else "manual_testing"
            workflow_stages = ["intake", "local_testing"]
            if phase in {"server_testing", "cloud_testing", "release_handoff"} and "status: known" in state_body:
                workflow_stages.append("cloud_testing")
            if phase == "release_handoff":
                workflow_stages.append("release_handoff")
            for stage_name in ([] if advance_stage else workflow_stages):
                digest_match = re.search(
                    r"(?m)^\s+identity_digest:\s*(\S+)", state_body
                )
                event_digest = workflow_deployment_digest or (
                    digest_match.group(1) if digest_match else "not_applicable"
                )
                advance_ledger(
                    runtime,
                    workflow=TESTING_WORKFLOW,
                    runtime_id="phase-01",
                    to_stage=stage_name,
                    cycle_kind="initial",
                    event_metadata={
                        "deployment_identity_digest": event_digest
                    },
                    transition_allowed=testing_transition_allowed,
                )
            command = [sys.executable, str(VALIDATOR), str(runtime)]
            if advance_stage:
                command.extend(["--advance-workflow", advance_stage])
            if expect_final:
                command.append("--expect-final")
            if print_system_risk:
                command.append("--print-system-risk-digest")
            return subprocess.run(
                command,
                capture_output=True,
                text=True,
            )

    def final_files(
        self,
        gap: str = "[]",
        evidence_valid: str = "true",
        cloud_required: bool = False,
    ) -> dict[str, str]:
        cloud_requirement = "required" if cloud_required else "not_applicable"
        cloud_reason = "p0_success_journey" if cloud_required else "no_deployment_in_scope"
        cloud_refs = "[TEST-CLOUD-1]" if cloud_required else "[]"
        cloud_count = "1" if cloud_required else "0"
        cloud_result = (
            """
```yaml
item_id: TEST-CLOUD-1
item_type: deployed_e2e
attempt: 1
environment: staging
environment_revision_ref: test-runtime-state.md#current_deployment_revision
status: verified
started_at: 2026-08-25T10:01:00Z
completed_at: 2026-08-25T10:05:00Z
depends_on_check: passed
expected_evidence: deployed business journey trace
result_summary: deployed journey reached the expected terminal state
evidence_refs: [EVIDENCE-CLOUD-1]
covers: [TEST-PLAN-1]
covered_by: []
evidence_reuse: false
writeback_status: updated
```
"""
            if cloud_required
            else ""
        )
        cloud_evidence = (
            """
EVIDENCE-CLOUD-1:
  item_id: TEST-CLOUD-1
  evidence_type: deployed_e2e_trace
  source: testing_runtime
  path: evidence/cloud-trace.zip
  target_environment: staging
  revision_kind: deployment_id
  revision: deploy-1
  valid: true
  deployment_identity_ref: test-runtime-state.md#current_deployment_revision
  component_revision_refs: []
  flow_refs: [FLOW-1]
  description: deployed business journey evidence
  added_at: 2026-08-25T10:05:00Z
  invalidated_by: null
"""
            if cloud_required
            else ""
        )
        files = {
            "planning-test-plan.md": f"""### TEST-PLAN-1：核心业务旅程测试

关联 FLOW：FLOW-1

环境证明要求：
- 本地业务 / E2E：required，从真实入口到终态
- 部署后云端业务 / E2E：{cloud_requirement}，{cloud_reason}
""",
            "business-journey-test-matrix.md": f"""```yaml
matrix_revision: JOURNEY-1
planning_scope_refs: [FLOW-1]
long_handoff_ref: testing-handoff.md
required_validation_gate_ref: testing-handoff.md#required_validation_gate
deployment_revision_ref: test-runtime-state.md#current_deployment_revision
journeys:
  - flow_ref: FLOW-1
    priority: P0
    success_journey_test_refs: [TEST-PLAN-1]
    contract_defined_negative_test_refs: []
    local_business_e2e:
      requirement: required
      result_refs: [TEST-LOCAL-1]
    deployed_environment_e2e:
      requirement: {cloud_requirement}
      selection_reason: {cloud_reason}
      deployment_sensitivity: []
      result_refs: {cloud_refs}
    open_coverage_gaps: {gap}
coverage_summary:
  required_flow_count: 1
  locally_covered_flow_count: 1
  cloud_required_flow_count: {cloud_count}
  cloud_covered_flow_count: {cloud_count}
  open_required_gaps: {gap}
```
""",
            "test-validation-results.md": """```yaml
item_id: TEST-LOCAL-1
item_type: case
attempt: 1
environment: local
environment_revision_ref: not_applicable
status: verified
started_at: 2026-08-25T09:01:00Z
completed_at: 2026-08-25T09:05:00Z
depends_on_check: passed
expected_evidence: local business journey trace
result_summary: local journey reached the expected terminal state
evidence_refs: [EVIDENCE-LOCAL-1]
covers: [TEST-PLAN-1]
covered_by: []
evidence_reuse: false
writeback_status: updated
```
"""
            + cloud_result,
            "test-evidence-index.md": f"""```yaml
EVIDENCE-LOCAL-1:
  item_id: TEST-LOCAL-1
  evidence_type: local_e2e_trace
  source: testing_runtime
  path: evidence/local-trace.zip
  target_environment: local
  revision_kind: git_commit
  revision: {LONG_REPOSITORY_REVISION}
  valid: {evidence_valid}
  deployment_identity_ref: not_applicable
  component_revision_refs: []
  flow_refs: [FLOW-1]
  description: local business journey evidence
  added_at: 2026-08-25T09:05:00Z
  invalidated_by: null
{cloud_evidence}```
""",
            "change-triage.md": "# Change Triage\n",
        }
        files["business-journey-test-matrix.md"] += system_risks(cloud_required)
        if cloud_required:
            files["test-validation-results.md"] = files["test-validation-results.md"].replace(
                "covers: [TEST-PLAN-1]",
                "covers: [TEST-PLAN-1, SYS-environment_binding, SYS-deployment_lifecycle]",
            )
            files["test-evidence-index.md"] = files["test-evidence-index.md"].replace(
                "  revision: deploy-1\n",
                f"  revision: deploy-1\n  deployment_identity_digest: {identity_digest('deploy-1', 'config-1')}\n",
            )
        return files

    def risk_check_files(self, ci: bool = False) -> dict[str, str]:
        files = self.final_files()
        files["business-journey-test-matrix.md"] = files["business-journey-test-matrix.md"].replace(
            "    - category: integration_contracts\n"
            "      applicability: not_applicable\n"
            "      reason: inspected fixture has no relevant runtime mechanism\n"
            "      checks: []\n",
            "    - category: integration_contracts\n"
            "      applicability: required\n"
            "      reason: approved boundary has a behavioral contract\n"
            "      checks:\n"
            "        - check_id: SYS-INTEGRATION-1\n"
            "          test_layer: integration\n"
            "          contract_refs: [requirement-and-scope.md]\n"
            "          assertion: expected boundary behavior\n"
            "          verification_kind: behavioral_test\n"
            "          result_refs: [TEST-LOCAL-1]\n"
            "          regression:\n"
            f"            requirement: {'required' if ci else 'not_applicable'}\n"
            "            reason: maintained in CI or release owner checks every environment change\n"
            + ("            ci_provider: github_actions\n"
               "            workflow_job_ref: ci.yml#runtime-tests\n"
               "            command_or_binding: python -m unittest\n"
               "            verification_kind: behavioral_test\n"
               "            ci_result_refs: [TEST-CI-1]\n" if ci else ""),
        )
        files["test-validation-results.md"] = files["test-validation-results.md"].replace(
            "covers: [TEST-PLAN-1]", "covers: [TEST-PLAN-1, SYS-INTEGRATION-1]"
        )
        if ci:
            files["ci.yml"] = "jobs:\n  runtime-tests:\n    steps:\n      - run: python -m unittest\n"
            files["test-validation-results.md"] += files["test-validation-results.md"].replace(
                "TEST-LOCAL-1", "TEST-CI-1"
            ).replace("EVIDENCE-LOCAL-1", "EVIDENCE-CI-1")
            files["test-evidence-index.md"] += files["test-evidence-index.md"].replace(
                "EVIDENCE-LOCAL-1", "EVIDENCE-CI-1"
            ).replace("TEST-LOCAL-1", "TEST-CI-1").replace(
                "evidence_type: local_e2e_trace",
                "evidence_type: ci_job_run\n  ci_provider: github_actions\n  ci_job_ref: ci.yml#runtime-tests\n  command_or_binding: python -m unittest\n  verification_kind: behavioral_test"
            ).replace("local-trace.zip", "ci-run.txt")
        return files

    def test_local_runtime_without_deployment_passes(self) -> None:
        result = self.run_validator(state())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_system_risk_and_ci_behavioral_regression_pass(self) -> None:
        result = self.run_validator(state(), extra_files=self.risk_check_files(ci=True), expect_final=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_final_closure_cannot_omit_system_risk_coverage(self) -> None:
        files = self.final_files()
        files["business-journey-test-matrix.md"] = files["business-journey-test-matrix.md"].split("system_risk_coverage:")[0]
        result = self.run_validator(state(), extra_files=files, expect_final=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("system_risk_coverage schema_version", result.stderr)

    def test_system_risk_cannot_omit_a_category_or_na_reason(self) -> None:
        for omitted in ("    - category: resource_bounds\n      applicability: not_applicable\n      reason: inspected fixture has no relevant runtime mechanism\n      checks: []\n", "      reason: inspected fixture has no relevant runtime mechanism\n"):
            with self.subTest(omitted=omitted):
                files = self.final_files()
                files["business-journey-test-matrix.md"] = files["business-journey-test-matrix.md"].replace(omitted, "", 1)
                result = self.run_validator(state(), extra_files=files, expect_final=True)
                self.assertEqual(result.returncode, 1)
                self.assertIn("system risk", result.stderr)

    def test_detected_container_cannot_skip_resource_isolation(self) -> None:
        files = self.final_files()
        files["business-journey-test-matrix.md"] = files["business-journey-test-matrix.md"].replace("  features: []", "  features: [container]")
        result = self.run_validator(state(), extra_files=files, expect_final=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("resource_bounds: detected system features", result.stderr)
        self.assertIn("credential_isolation: detected system features", result.stderr)

    def test_system_risk_rejects_missing_or_unrelated_check_result(self) -> None:
        for mutation in ("missing_ref", "unrelated"):
            with self.subTest(mutation=mutation):
                files = self.risk_check_files()
                if mutation == "missing_ref":
                    files["business-journey-test-matrix.md"] = files["business-journey-test-matrix.md"].replace("result_refs: [TEST-LOCAL-1]", "result_refs: [MISSING]")
                else:
                    files["test-validation-results.md"] = files["test-validation-results.md"].replace(
                        "covers: [TEST-PLAN-1, SYS-INTEGRATION-1]", "covers: [TEST-PLAN-1]"
                    )
                result = self.run_validator(state(), extra_files=files, expect_final=True)
                self.assertEqual(result.returncode, 1)
                self.assertIn("system risk", result.stderr)

    def test_ci_static_check_cannot_replace_behavioral_regression(self) -> None:
        files = self.risk_check_files(ci=True)
        files["business-journey-test-matrix.md"] = files["business-journey-test-matrix.md"].replace(
            "            verification_kind: behavioral_test", "            verification_kind: static_check"
        )
        result = self.run_validator(state(), extra_files=files, expect_final=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("CI verification kind cannot replace", result.stderr)

    def test_ci_mapping_requires_existing_job_and_actual_run_evidence(self) -> None:
        for mutation in ("job_missing", "no_run", "local_only", "stale_revision", "failed_run", "wrong_binding"):
            with self.subTest(mutation=mutation):
                files = self.risk_check_files(ci=True)
                if mutation == "job_missing":
                    files["ci.yml"] = "jobs:\n  different-job:\n    steps: []\n"
                elif mutation == "no_run":
                    files["business-journey-test-matrix.md"] = files["business-journey-test-matrix.md"].replace("ci_result_refs: [TEST-CI-1]", "ci_result_refs: []")
                elif mutation == "local_only":
                    files["test-evidence-index.md"] = files["test-evidence-index.md"].replace("evidence_type: ci_job_run", "evidence_type: local_e2e_trace")
                elif mutation == "stale_revision":
                    files["test-evidence-index.md"] = files["test-evidence-index.md"].replace(LONG_REPOSITORY_REVISION, "old-revision")
                elif mutation == "failed_run":
                    before, after = files["test-validation-results.md"].rsplit("status: verified", 1)
                    files["test-validation-results.md"] = before + "status: failed" + after
                else:
                    files["test-evidence-index.md"] = files["test-evidence-index.md"].replace("ci_job_ref: ci.yml#runtime-tests", "ci_job_ref: ci.yml#different-job")
                result = self.run_validator(state(), extra_files=files, expect_final=True)
                self.assertEqual(result.returncode, 1)

    def test_system_risk_digest_command_matches_release_binding(self) -> None:
        files = self.final_files()
        result = self.run_validator(state(), extra_files=files, print_system_risk=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), system_risk_digest(entries(files["business-journey-test-matrix.md"])))
        files["business-journey-test-matrix.md"] = files["business-journey-test-matrix.md"].split("system_risk_coverage:")[0]
        missing = self.run_validator(state(), extra_files=files, print_system_risk=True)
        self.assertEqual(missing.returncode, 1)
        self.assertIn("system_risk_coverage is missing", missing.stderr)

    def test_deployment_scope_conflict_blocks_final_closure(self) -> None:
        files = self.final_files(cloud_required=True)
        files["business-journey-test-matrix.md"] = files["business-journey-test-matrix.md"].replace("scope_alignment: aligned", "scope_alignment: reconfirmation_required")
        result = self.run_validator(state("known", "deploy-1", "config-1"), extra_files=files, expect_final=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("reconcile deployment exclusions", result.stderr)

    def test_review_deployed_risk_cannot_close_using_only_local_integration(self) -> None:
        files = self.final_files(cloud_required=True)
        head, risk = files["business-journey-test-matrix.md"].split("system_risk_coverage:", 1)
        risk = risk.replace("test_layer: deployment", "test_layer: integration").replace(
            "result_refs: [TEST-CLOUD-1]", "result_refs: [TEST-LOCAL-1]"
        )
        files["business-journey-test-matrix.md"] = head + "system_risk_coverage:" + risk
        result = self.run_validator(state("known", "deploy-1", "config-1"), extra_files=files, expect_final=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("requires current deployed proof", result.stderr)

    def test_review_ci_job_name_in_comment_or_string_is_not_a_definition(self) -> None:
        for body in (
            "jobs:\n  build-only:\n    steps:\n      - run: cargo check\n# runtime-tests was removed\n",
            "name: runtime-tests\njobs:\n  build-only:\n    steps: []\n",
            "jobs:\n  build-only:\n    steps:\n      - run: |\n          runtime-tests:\n            steps: []\n",
        ):
            with self.subTest(body=body):
                files = self.risk_check_files(ci=True)
                files["ci.yml"] = body
                result = self.run_validator(state(), extra_files=files, expect_final=True)
                self.assertEqual(result.returncode, 1)
                self.assertIn("CI job does not exist", result.stderr)

    def test_deployed_category_can_combine_local_fault_and_target_binding_proofs(self) -> None:
        files = self.final_files(cloud_required=True)
        matrix = files["business-journey-test-matrix.md"]
        marker = "    - category: deployment_lifecycle\n"
        before, after = matrix.split(marker, 1)
        # Add a local assertion alongside the existing target-environment check.
        before += (
            "        - check_id: SYS-LOCAL-SUPPLEMENT\n"
            "          test_layer: integration\n"
            "          contract_refs: [requirement-and-scope.md]\n"
            "          assertion: isolated fault behavior is correct\n"
            "          verification_kind: behavioral_test\n"
            "          result_refs: [TEST-LOCAL-1]\n"
            "          regression:\n"
            "            requirement: not_applicable\n"
            "            reason: release owner reruns this isolated scenario on binding changes\n"
        )
        files["business-journey-test-matrix.md"] = before + marker + after
        files["test-validation-results.md"] = files["test-validation-results.md"].replace(
            "SYS-environment_binding, SYS-deployment_lifecycle]",
            "SYS-environment_binding, SYS-deployment_lifecycle, SYS-LOCAL-SUPPLEMENT]"
        )
        result = self.run_validator(state("known", "deploy-1", "config-1"), extra_files=files, expect_final=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_ci_job_definition_supports_github_quotes_and_gitlab_jobs(self) -> None:
        for provider, body in (
            ("github_actions", "jobs:\n  'runtime-tests':\n    steps:\n      - run: python -m unittest\n"),
            ("gitlab_ci", "stages: [test]\n'runtime-tests':\n  stage: test\n  script: python -m unittest\n"),
        ):
            with self.subTest(provider=provider):
                files = self.risk_check_files(ci=True)
                files["ci.yml"] = body
                for name in ("business-journey-test-matrix.md", "test-evidence-index.md"):
                    files[name] = files[name].replace("ci_provider: github_actions", "ci_provider: " + provider)
                result = self.run_validator(state(), extra_files=files, expect_final=True)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_ci_provider_cannot_be_guessed(self) -> None:
        files = self.risk_check_files(ci=True)
        files["business-journey-test-matrix.md"] = files["business-journey-test-matrix.md"].replace("            ci_provider: github_actions\n", "")
        result = self.run_validator(state(), extra_files=files, expect_final=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("CI provider must be explicit", result.stderr)

    def test_multiline_quoted_yaml_cannot_create_a_ci_job(self) -> None:
        for provider in ("github_actions", "gitlab_ci"):
            for quote in ("'", '"'):
                with self.subTest(provider=provider, quote=quote):
                    files = self.risk_check_files(ci=True)
                    files["ci.yml"] = multiline_ci_config(provider, quote)
                    for name in ("business-journey-test-matrix.md", "test-evidence-index.md"):
                        files[name] = files[name].replace("ci_provider: github_actions", "ci_provider: " + provider)
                    result = self.run_validator(state(), extra_files=files, expect_final=True)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn("unsupported CI YAML", result.stderr)
                    self.assertIn("provider_export", result.stderr)

    def test_dynamic_ci_requires_matching_definition_export_and_run(self) -> None:
        for mutation in (None, "multiline_yaml", "missing_export", "wrong_digest", "wrong_job", "missing_run", "empty_definition"):
            with self.subTest(mutation=mutation):
                files = self.risk_check_files(ci=True)
                workflow = "pipeline { stages { loadGeneratedStages() } }\n"
                if mutation == "multiline_yaml":
                    workflow = multiline_ci_config("github_actions", '"').replace(
                        "  build:\n", "  runtime-tests:\n", 1
                    )
                files["ci.yml"] = workflow
                for name in ("business-journey-test-matrix.md", "test-evidence-index.md"):
                    files[name] = files[name].replace("ci_provider: github_actions", "ci_provider: provider_export")
                files["business-journey-test-matrix.md"] = files["business-journey-test-matrix.md"].replace(
                    "ci_provider: provider_export\n", "ci_provider: provider_export\n            definition_evidence_ref: EVIDENCE-DEFINITION-1\n"
                )
                definition = {
                    "schema_version": "ci-job-definition/v1",
                    "provider": "github_actions" if mutation == "multiline_yaml" else "jenkins",
                    "source_ref": "https://ci.example.invalid/job/runtime-tests/api/json",
                    "workflow_job_ref": "ci.yml#runtime-tests",
                    "job_id": "runtime-tests",
                    "configuration_sha256": "sha256:" + hashlib.sha256(workflow.encode()).hexdigest(),
                    "definition": {"name": "runtime-tests", "steps": ["python -m unittest"]},
                }
                if mutation == "wrong_digest":
                    definition["configuration_sha256"] = "sha256:" + "0" * 64
                elif mutation == "wrong_job":
                    definition["job_id"] = "build-only"
                elif mutation == "empty_definition":
                    definition["definition"] = {}
                if mutation != "missing_export":
                    files["evidence/ci-definition.json"] = json.dumps(definition)
                    files["test-evidence-index.md"] += (
                        "\n```yaml\nEVIDENCE-DEFINITION-1:\n"
                        "  item_id: TEST-CI-1\n"
                        "  evidence_type: ci_job_definition\n"
                        "  source: provider_export\n"
                        "  path: evidence/ci-definition.json\n"
                        "  revision_kind: workspace_snapshot\n"
                        f"  revision: {LONG_REPOSITORY_REVISION}\n"
                        "  deployment_identity_ref: not_applicable\n"
                        "  valid: true\n"
                        "  invalidated_by: null\n```\n"
                    )
                if mutation == "missing_run":
                    files["business-journey-test-matrix.md"] = files["business-journey-test-matrix.md"].replace("ci_result_refs: [TEST-CI-1]", "ci_result_refs: []")
                result = self.run_validator(state(), extra_files=files, expect_final=True)
                self.assertEqual(result.returncode, 0 if mutation in {None, "multiline_yaml"} else 1, result.stderr)

    def test_online_risk_evidence_binds_full_configuration_identity(self) -> None:
        files = self.final_files(cloud_required=True)
        files["test-evidence-index.md"] = files["test-evidence-index.md"].replace(
            f"deployment_identity_digest: {identity_digest('deploy-1', 'config-1')}",
            f"deployment_identity_digest: {identity_digest('deploy-1', 'old-config')}",
        )
        result = self.run_validator(state("known", "deploy-1", "config-1"), extra_files=files, expect_final=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("system risk deployment identity mismatch", result.stderr)

    def test_release_snapshot_freezes_system_risk_coverage(self) -> None:
        files = self.final_files(cloud_required=True)
        files["business-journey-test-matrix.md"] = files["business-journey-test-matrix.md"].replace(
            "reason: deployment target requires runtime verification", "reason: changed coverage decision"
        )
        result = self.run_validator(
            state("known", "deploy-1", "config-1", "current", identity_digest("deploy-1", "config-1")),
            release_handoff("deploy-1", "config-1"), extra_files=files,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("system risk coverage digest mismatch", result.stderr)

    def test_intake_stage_does_not_require_future_business_matrix(self) -> None:
        result = self.run_validator(state(), advance_stage="intake")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_current_release_snapshot_for_complete_identity_passes(self) -> None:
        digest = identity_digest("deploy-1", "config-1")
        result = self.run_validator(
            state("known", "deploy-1", "config-1", "current", digest),
            release_handoff("deploy-1", "config-1"),
            extra_files=self.final_files(cloud_required=True),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_config_only_change_invalidates_old_release_snapshot(self) -> None:
        old_digest = identity_digest("deploy-1", "config-1")
        result = self.run_validator(
            state("known", "deploy-1", "config-2", "current", old_digest),
            release_handoff("deploy-1", "config-1"),
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("deployment identity", result.stderr)

    def test_invalidated_release_snapshot_requires_matching_reason(self) -> None:
        digest = identity_digest("deploy-1", "config-1")
        valid = self.run_validator(
            state("known", "deploy-1", "config-1", "invalidated", digest),
            release_handoff("deploy-1", "config-1", "invalidated"),
        )
        self.assertEqual(valid.returncode, 0, valid.stderr)

        invalid = self.run_validator(
            state("known", "deploy-1", "config-1", "invalidated", digest),
            release_handoff("deploy-1", "config-1", "current"),
        )
        self.assertEqual(invalid.returncode, 1)

    def test_invalidated_release_snapshot_preserves_old_deployment_identity(self) -> None:
        old_digest = identity_digest("deploy-1", "config-1")
        result = self.run_validator(
            state(
                "known",
                "deploy-2",
                "config-2",
                "invalidated",
                old_digest,
                "completed",
            ),
            release_handoff("deploy-1", "config-1", "invalidated"),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_intake_identity_fails(self) -> None:
        body = state().replace("  current_test_epoch: phase-01\n", "")
        result = self.run_validator(body)
        self.assertEqual(result.returncode, 1)
        self.assertIn("current_test_epoch", result.stderr)

    def test_stale_long_handoff_binding_fails_intake(self) -> None:
        result = self.run_validator(state().replace("long_runtime_epoch: LONG-1", "long_runtime_epoch: LONG-OLD"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("runtime_epoch does not match Testing intake", result.stderr)

    def test_reconciliation_cannot_keep_current_release(self) -> None:
        digest = identity_digest("deploy-1", "config-1")
        result = self.run_validator(
            state(
                "known",
                "deploy-1",
                "config-1",
                "current",
                digest,
                "in_progress",
            ),
            release_handoff("deploy-1", "config-1"),
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("may not retain a current release handoff", result.stderr)

    def test_duplicate_state_key_fails(self) -> None:
        body = state().replace(
            "overall_status: in_progress",
            "overall_status: in_progress\noverall_status: blocked",
        )
        result = self.run_validator(body)
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate test runtime key", result.stderr)

    def test_not_generated_release_envelope_cannot_keep_stale_pointer(self) -> None:
        body = state().replace(
            "  snapshot_ref: not_applicable", "  snapshot_ref: release-handoff.md"
        )
        result = self.run_validator(body)
        self.assertEqual(result.returncode, 1)
        self.assertIn("snapshot_ref must be not_applicable", result.stderr)

    def test_final_closure_with_reconciled_local_business_journey_passes(self) -> None:
        result = self.run_validator(
            state(), extra_files=self.final_files(), expect_final=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_final_closure_rejects_open_journey_gap(self) -> None:
        result = self.run_validator(
            state(),
            extra_files=self.final_files(gap="[GAP-1]"),
            expect_final=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("open coverage gaps remain", result.stderr)
        self.assertIn("still has required gaps", result.stderr)

    def test_final_closure_rejects_invalid_evidence(self) -> None:
        result = self.run_validator(
            state(),
            extra_files=self.final_files(evidence_valid="false"),
            expect_final=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("evidence is not valid", result.stderr)

    def test_cloud_required_closure_requires_known_deployment_identity(self) -> None:
        result = self.run_validator(
            state(),
            extra_files=self.final_files(cloud_required=True),
            expect_final=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("known deployment identity", result.stderr)

    def test_final_closure_rejects_open_finding(self) -> None:
        files = self.final_files()
        files["change-triage.md"] = """```yaml
finding_id: FINDING-1
finding_status: retest_required
retest_result_refs: []
closure_evidence_refs: []
```
"""
        result = self.run_validator(state(), extra_files=files, expect_final=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("finding is not closed", result.stderr)

    def test_documented_dictionary_results_pass_final_closure(self) -> None:
        files = self.final_files()
        body = files["test-validation-results.md"].replace("```yaml\n", "").replace("```\n", "")
        files["test-validation-results.md"] = "TEST-LOCAL-1:\n" + textwrap.indent(body, "  ")
        result = self.run_validator(state(), extra_files=files, expect_final=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_dictionary_open_finding_cannot_be_ignored(self) -> None:
        files = self.final_files()
        files["change-triage.md"] = """FINDING-1:
  finding_id: FINDING-1
  finding_status: open
  retest_result_refs: []
  closure_evidence_refs: []
"""
        result = self.run_validator(state(), extra_files=files, expect_final=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("finding is not closed", result.stderr)

    def test_dictionary_closed_finding_requires_resolved_closure(self) -> None:
        for valid_refs in (True, False):
            with self.subTest(valid_refs=valid_refs):
                files = self.final_files()
                files["change-triage.md"] = """FINDING-1:
  finding_id: FINDING-1
  finding_status: closed
  retest_result_refs: [TEST-LOCAL-1]
  closure_evidence_refs: [EVIDENCE-LOCAL-1]
"""
                if not valid_refs:
                    files["change-triage.md"] = files["change-triage.md"].replace(
                        "EVIDENCE-LOCAL-1", "EVIDENCE-MISSING"
                    )
                result = self.run_validator(state(), extra_files=files, expect_final=True)
                self.assertEqual(result.returncode, 0 if valid_refs else 1, result.stderr)
                if not valid_refs:
                    self.assertIn("closure evidence ref does not resolve", result.stderr)

    def test_unrecognized_findings_cannot_be_ignored(self) -> None:
        for body in (
            "FINDING-1:\n  finding_status: open\n",
            "FINDING-1:\n  finding_id = FINDING-1\n  finding_status: open\n",
            "finding_id = FINDING-1\nfinding_status = open\n",
            "VALID:\n  finding_id: VALID\n  finding_status: closed\n"
            "  retest_result_refs: [TEST-LOCAL-1]\n"
            "  closure_evidence_refs: [EVIDENCE-LOCAL-1]\n"
            "FINDING-1:\n  finding_status: open\n",
            "finding_id: VALID\nfinding_status: closed\n"
            "retest_result_refs: [TEST-LOCAL-1]\n"
            "closure_evidence_refs: [EVIDENCE-LOCAL-1]\n"
            "FINDING-1:\n  finding_status: open\n",
            "```yaml\nfinding_id: VALID\nfinding_status: closed\n"
            "retest_result_refs: [TEST-LOCAL-1]\n"
            "closure_evidence_refs: [EVIDENCE-LOCAL-1]\n```\n"
            "FINDING-1:\n  finding_id: FINDING-1\n  finding_status: open\n",
        ):
            with self.subTest(body=body):
                files = self.final_files()
                files["change-triage.md"] = body
                result = self.run_validator(state(), extra_files=files, expect_final=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("unrecognized finding record", result.stderr)

    def test_runtime_rejects_yaml_anchors_aliases_and_merge_keys(self) -> None:
        for declaration in (
            "success_journey_test_refs: &tests\n      - TEST-PLAN-1",
            "success_journey_test_refs: *tests",
            "success_journey_test_refs: [*tests]",
            "success_journey_test_refs: [TEST-PLAN-1]\n    <<: *defaults",
        ):
            with self.subTest(declaration=declaration):
                files = self.final_files()
                files["business-journey-test-matrix.md"] = files[
                    "business-journey-test-matrix.md"
                ].replace("success_journey_test_refs: [TEST-PLAN-1]", declaration)
                result = self.run_validator(state(), extra_files=files, expect_final=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("unsupported YAML anchor, alias or merge key", result.stderr)

    def test_sibling_long_receipt_passes_final_closure(self) -> None:
        files = self.final_files()
        files["test-validation-results.md"] = files["test-validation-results.md"].replace(
            "status: verified", "status: reused_from_long"
        ).replace("evidence_reuse: false", "source_validation_id: VALIDATION-1\nevidence_reuse: true")
        files["test-evidence-index.md"] = files["test-evidence-index.md"].replace(
            "source: testing_runtime", "source: long_readiness_receipt"
        ).replace("path: evidence/local-trace.zip", "path: ../long-runtime/long-readiness-receipt.json")
        result = self.run_validator(
            state(), extra_files=files, expect_final=True, sibling_long_runtime=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_testing_intake_requires_real_long_validation_evidence(self) -> None:
        result = self.run_validator(
            state(),
            extra_files={"validation-results.md": "# no Long validation evidence\n"},
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("effective validation id does not resolve", result.stderr)

    def test_long_executed_task_revisions_cannot_be_omitted(self) -> None:
        handoff = long_testing_handoff().replace(
            "executed_task_contract_revisions: [TASK-1@1]\n", ""
        )
        result = self.run_validator(
            state(), extra_files={"testing-handoff.md": handoff}
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("executed_task_contract_revisions is missing", result.stderr)

    def test_p0_local_business_journey_cannot_be_declared_not_applicable(self) -> None:
        files = self.final_files()
        files["business-journey-test-matrix.md"] = files[
            "business-journey-test-matrix.md"
        ].replace(
            "local_business_e2e:\n      requirement: required\n      result_refs: [TEST-LOCAL-1]",
            "local_business_e2e:\n      requirement: not_applicable\n      result_refs: []",
        ).replace("locally_covered_flow_count: 1", "locally_covered_flow_count: 0")
        result = self.run_validator(state(), extra_files=files, expect_final=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("local business/E2E requirement does not match Planning", result.stderr)

    def test_required_validation_gate_ref_must_be_exact(self) -> None:
        files = self.final_files()
        files["business-journey-test-matrix.md"] = files[
            "business-journey-test-matrix.md"
        ].replace(
            "testing-handoff.md#required_validation_gate",
            "unrelated.md#invented-gate",
        )
        result = self.run_validator(state(), extra_files=files, expect_final=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("not bound to the current Long gate", result.stderr)

    def test_result_and_evidence_must_bind_planning_journey_and_revision(self) -> None:
        files = self.final_files()
        files["test-validation-results.md"] = files["test-validation-results.md"].replace(
            "covers: [TEST-PLAN-1]", "covers: []"
        )
        files["test-evidence-index.md"] = files["test-evidence-index.md"].replace(
            f"  revision: {LONG_REPOSITORY_REVISION}\n", ""
        ).replace("  flow_refs: [FLOW-1]", "  flow_refs: []")
        result = self.run_validator(state(), extra_files=files, expect_final=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("not bound to the Planning TEST", result.stderr)
        self.assertIn("missing evidence field revision", result.stderr)
        self.assertIn("evidence is not bound to FLOW-1", result.stderr)

    def test_writeback_target_must_be_the_runtime_directory(self) -> None:
        result = self.run_validator(
            state().replace("writeback_target: .", "writeback_target: somewhere/else")
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not resolve to this Testing Runtime", result.stderr)

    def test_completed_reconciliation_requires_full_identity_objects(self) -> None:
        body = state(
            "known", "deploy-2", "config-2", reconciliation_status="completed"
        ).replace("  from_identity:\n    status: known", "  from_identity: not_applicable", 1)
        result = self.run_validator(body)
        self.assertEqual(result.returncode, 1)
        self.assertIn("from_identity.status is invalid", result.stderr)

    def test_release_dependencies_are_reconciled_from_planning_and_results(self) -> None:
        planning = """```yaml
handoff_type: execution_ready
requires_execution_handoff: true
planning_baseline_revision: PLAN-1
execution_prerequisite_readiness:
  before_long_status: passed
  before_release_dependency_refs: [DEP-1]
  unresolved_before_long: []
incremental_execution_contract:
  planning_baseline_revision: PLAN-1
  execute_only: [TASK-1@1]
  resume_only: []
  reexecute_affected_part: []
  context_only: []
  completed_locked: []
  cancelled: []
handoff_role_mapping:
  - role: Requirement and Scope
    path: requirement-and-scope.md
  - role: Test and Acceptance Plan
    path: planning-test-plan.md
```
"""
        release = release_handoff("deploy-1", "config-1").replace(
            "dependencies: []\nunresolved_dependency_refs: []",
            """dependencies:
  - dependency_ref: DEP-1
    planning_snapshot_status: pending
    testing_result_ref: DEP-RESULT-1
    evidence_refs: []
    owner: platform-team
    blocking_scope: release
    release_gate_owner: release-process
unresolved_dependency_refs: []""",
        )
        files = self.final_files(cloud_required=True)
        files["planning-handoff.yaml"] = planning
        files["test-validation-results.md"] += """```yaml
item_id: DEP-RESULT-1
item_type: environment_prerequisite
dependency_ref: DEP-1
status: pending
```
"""
        digest = identity_digest("deploy-1", "config-1")
        result = self.run_validator(
            state("known", "deploy-1", "config-1", "current", digest),
            release,
            extra_files=files,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("unresolved_dependency_refs do not reconcile", result.stderr)
        self.assertIn("readiness status does not reconcile", result.stderr)

        blocked_release = release.replace(
            "release_readiness_status: ready", "release_readiness_status: blocked"
        ).replace(
            "unresolved_dependency_refs: []", "unresolved_dependency_refs: [DEP-1]"
        )
        blocked = self.run_validator(
            state("known", "deploy-1", "config-1", "current", digest),
            blocked_release,
            extra_files=files,
        )
        self.assertEqual(blocked.returncode, 0, blocked.stderr)
        self.assertIn("release readiness: blocked", blocked.stdout)

    def test_testing_requires_the_frozen_long_readiness_receipt(self) -> None:
        missing = self.run_validator(state(), omit_long_receipt=True)
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("validator_receipt_ref", missing.stderr)

        mutated = self.run_validator(
            state(),
            post_receipt_files={
                "validation-results.md": """```yaml
validation_id: VALIDATION-1
result: passed
matrix_revision: MATRIX-1
```
# changed after Long readiness
"""
            },
        )
        self.assertNotEqual(mutated.returncode, 0)
        self.assertIn("receipt artifact changed", mutated.stderr)

    def test_testing_rejects_pre_machine_receipt_long_runtime(self) -> None:
        legacy = self.run_validator(
            state(), long_receipt_schema="long-readiness-receipt/v1"
        )
        self.assertNotEqual(legacy.returncode, 0)
        self.assertIn("Long readiness receipt schema is invalid", legacy.stderr)

    def test_local_evidence_revision_must_match_long_repository_snapshot(self) -> None:
        files = self.final_files()
        files["test-evidence-index.md"] = files["test-evidence-index.md"].replace(
            LONG_REPOSITORY_REVISION,
            "sha256:" + "9" * 64,
        )
        result = self.run_validator(state(), extra_files=files, expect_final=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("frozen Long repository revision", result.stderr)

    def test_verified_evidence_requires_a_real_durable_file(self) -> None:
        result = self.run_validator(
            state(),
            extra_files=self.final_files(),
            expect_final=True,
            materialize_evidence=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("durable evidence file is missing or empty", result.stderr)

    def test_evidence_content_change_after_indexing_is_rejected(self) -> None:
        result = self.run_validator(
            state(),
            extra_files=self.final_files(),
            expect_final=True,
            mutate_evidence_after_freeze=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match content_sha256", result.stderr)

    def test_closed_finding_refs_must_resolve_to_retest_and_evidence(self) -> None:
        files = self.final_files()
        files["change-triage.md"] = """```yaml
finding_id: FINDING-1
finding_status: closed
retest_result_refs: [DOES-NOT-EXIST]
closure_evidence_refs: [EVIDENCE-DOES-NOT-EXIST]
```
"""
        result = self.run_validator(state(), extra_files=files, expect_final=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("retest result ref does not resolve", result.stderr)
        self.assertIn("closure evidence ref does not resolve", result.stderr)

    def test_reused_long_result_must_bind_effective_validation_and_receipt(self) -> None:
        files = self.final_files()
        files["test-validation-results.md"] = files[
            "test-validation-results.md"
        ].replace("status: verified", "status: reused_from_long").replace(
            "evidence_reuse: false",
            "source_validation_id: DOES-NOT-EXIST\nevidence_reuse: true",
        )
        files["test-evidence-index.md"] = files[
            "test-evidence-index.md"
        ].replace("source: testing_runtime", "source: long_readiness_receipt").replace(
            "path: evidence/local-trace.zip", "path: long-readiness-receipt.json"
        )
        result = self.run_validator(state(), extra_files=files, expect_final=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not bind a current effective Long validation", result.stderr)

    def test_testing_accepts_long_result_explicitly_carried_forward(self) -> None:
        carried = """```yaml
validation_id: VALIDATION-1
result: passed
matrix_revision: MATRIX-0
matrix_compatibility: carried_forward_unchanged
compatibility_evidence: [compatibility-evidence.md]
execution_receipt_ref: machine-execution-receipts/VALIDATION-1.json
evidence: [machine-execution-receipts/VALIDATION-1.json]
```
"""
        result = self.run_validator(
            state(),
            extra_files={
                "validation-results.md": carried,
                "compatibility-evidence.md": "# Compatibility evidence\n",
            },
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_workflow_rejects_direct_deployment_identity_replacement(self) -> None:
        result = self.run_validator(
            state("known", "deploy-2", "config-2"),
            workflow_deployment_digest=identity_digest("deploy-1", "config-1"),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not bound to the current deployment identity", result.stderr)

    def test_release_snapshot_payload_mutation_is_rejected(self) -> None:
        deployment_digest = identity_digest("deploy-1", "config-1")
        result = self.run_validator(
            state("known", "deploy-1", "config-1", "current", deployment_digest),
            release_handoff("deploy-1", "config-1"),
            extra_files=self.final_files(cloud_required=True),
            tamper_release_after_seal=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("snapshot_digest does not match", result.stderr)

    def test_release_dependency_cannot_reuse_an_unrelated_business_result(self) -> None:
        files = self.final_files(cloud_required=True)
        files["planning-handoff.yaml"] = files.get(
            "planning-handoff.yaml",
            """```yaml
handoff_type: execution_ready
requires_execution_handoff: true
planning_baseline_revision: PLAN-1
execution_prerequisite_readiness:
  before_long_status: passed
  before_release_dependency_refs: [DEP-1]
  unresolved_before_long: []
incremental_execution_contract:
  planning_baseline_revision: PLAN-1
  execute_only: [TASK-1@1]
  resume_only: []
  reexecute_affected_part: []
  context_only: []
  completed_locked: []
  cancelled: []
handoff_role_mapping:
  - role: Requirement and Scope
    path: requirement-and-scope.md
  - role: Test and Acceptance Plan
    path: planning-test-plan.md
```
""",
        )
        release = release_handoff("deploy-1", "config-1").replace(
            "dependencies: []\nunresolved_dependency_refs: []",
            """dependencies:
  - dependency_ref: DEP-1
    planning_snapshot_status: pending
    testing_result_ref: TEST-LOCAL-1
    evidence_refs: [EVIDENCE-LOCAL-1]
    owner: platform-team
    blocking_scope: release
    release_gate_owner: release-process
unresolved_dependency_refs: []""",
        )
        digest = identity_digest("deploy-1", "config-1")
        result = self.run_validator(
            state("known", "deploy-1", "config-1", "current", digest),
            release,
            extra_files=files,
            expect_final=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("environment_prerequisite", result.stderr)

    def test_completed_deployment_reconciliation_cannot_leave_old_evidence_valid(self) -> None:
        files = self.final_files(cloud_required=True)
        files["test-evidence-index.md"] = files["test-evidence-index.md"].replace(
            "revision: deploy-1", "revision: deploy-2"
        )
        body = files["test-evidence-index.md"]
        files["test-evidence-index.md"] = body.rsplit("```", 1)[0] + """
EVIDENCE-STALE-CLOUD:
  item_id: TEST-OLD-CLOUD
  evidence_type: deployed_e2e_trace
  source: testing_runtime
  path: evidence/old-cloud-trace.zip
  target_environment: staging
  revision_kind: deployment_id
  revision: deploy-1
  valid: true
  deployment_identity_ref: test-runtime-state.md#current_deployment_revision
  component_revision_refs: []
  flow_refs: [FLOW-1]
  description: stale evidence from the prior deployment
  added_at: 2026-08-25T09:05:00Z
  invalidated_by: null
```
"""
        result = self.run_validator(
            state("known", "deploy-2", "config-2", reconciliation_status="completed"),
            extra_files=files,
            expect_final=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("prior deployment identity remains valid", result.stderr)

    def test_testing_forward_workflow_rejects_skip_and_backward_transition(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            runtime = Path(temporary)
            with self.assertRaises(ValueError):
                advance_ledger(
                    runtime,
                    workflow=TESTING_WORKFLOW,
                    runtime_id="phase-01",
                    to_stage="local_testing",
                    cycle_kind="initial",
                    transition_allowed=testing_transition_allowed,
                )
            advance_ledger(
                runtime,
                workflow=TESTING_WORKFLOW,
                runtime_id="phase-01",
                to_stage="intake",
                cycle_kind="initial",
                transition_allowed=testing_transition_allowed,
            )
            advance_ledger(
                runtime,
                workflow=TESTING_WORKFLOW,
                runtime_id="phase-01",
                to_stage="local_testing",
                cycle_kind="initial",
                transition_allowed=testing_transition_allowed,
            )
            with self.assertRaises(ValueError):
                advance_ledger(
                    runtime,
                    workflow=TESTING_WORKFLOW,
                    runtime_id="phase-01",
                    to_stage="intake",
                    cycle_kind="initial",
                    transition_allowed=testing_transition_allowed,
                )
            advance_ledger(
                runtime,
                workflow=TESTING_WORKFLOW,
                runtime_id="phase-01",
                to_stage="release_handoff",
                cycle_kind="initial",
                transition_allowed=testing_transition_allowed,
            )
            with self.assertRaisesRegex(ValueError, "explicit new cycle"):
                advance_ledger(
                    runtime,
                    workflow=TESTING_WORKFLOW,
                    runtime_id="phase-01",
                    to_stage="cloud_testing",
                    cycle_kind="deployment_revision",
                    transition_allowed=testing_transition_allowed,
                )
            advanced = advance_ledger(
                runtime,
                workflow=TESTING_WORKFLOW,
                runtime_id="phase-01",
                to_stage="cloud_testing",
                cycle_kind="deployment_revision",
                start_new_cycle=True,
                transition_allowed=testing_transition_allowed,
            )
            self.assertEqual(advanced["current_cycle"], 2)
            advance_ledger(
                runtime,
                workflow=TESTING_WORKFLOW,
                runtime_id="phase-01",
                to_stage="release_handoff",
                cycle_kind="deployment_revision",
                transition_allowed=testing_transition_allowed,
            )
            with self.assertRaises(ValueError):
                advance_ledger(
                    runtime,
                    workflow=TESTING_WORKFLOW,
                    runtime_id="phase-01",
                    to_stage="local_testing",
                    cycle_kind="deployment_revision",
                    transition_allowed=testing_transition_allowed,
                )

    def test_release_retest_uses_a_new_forward_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            runtime = Path(temporary)
            for stage_name in ("intake", "local_testing", "release_handoff"):
                advance_ledger(
                    runtime,
                    workflow=TESTING_WORKFLOW,
                    runtime_id="phase-01",
                    to_stage=stage_name,
                    cycle_kind="initial",
                    event_metadata={"deployment_identity_digest": "not_applicable"},
                    transition_allowed=testing_transition_allowed,
                )
            retest = advance_ledger(
                runtime,
                workflow=TESTING_WORKFLOW,
                runtime_id="phase-01",
                to_stage="local_testing",
                cycle_kind="retest",
                start_new_cycle=True,
                event_metadata={"deployment_identity_digest": "not_applicable"},
                transition_allowed=testing_transition_allowed,
            )
            self.assertEqual(retest["current_cycle"], 2)
            self.assertEqual(retest["current_stage"], "local_testing")
            completed = advance_ledger(
                runtime,
                workflow=TESTING_WORKFLOW,
                runtime_id="phase-01",
                to_stage="release_handoff",
                cycle_kind="retest",
                event_metadata={"deployment_identity_digest": "not_applicable"},
                transition_allowed=testing_transition_allowed,
            )
            self.assertEqual(completed["current_stage"], "release_handoff")


class CIJobDefinitionTests(unittest.TestCase):
    def test_only_actual_yaml_job_definitions_are_selected(self) -> None:
        cases = (
            ("github_actions", 'jobs:\n  "runtime-tests":\n    runs-on: ubuntu-latest\n    steps: []\n', {"runtime-tests"}),
            ("github_actions", 'jobs :\n  runtime-tests :\n    steps: []\n', {"runtime-tests"}),
            ("github_actions", "name: runtime-tests\njobs:\n  build:\n    name: runtime-tests\n", {"build"}),
            ("github_actions", "jobs:\n  build:\n    steps:\n      - run: |\n          runtime-tests:\n            steps: []\n", {"build"}),
            ("github_actions", "jobs: |\n  runtime-tests:\n    steps: []\n", set()),
            ("gitlab_ci", "stages: [test]\nvariables:\n  runtime-tests: ignored\n.hidden:\n  script: echo template\n'runtime-tests':\n  script: echo test\n", {"runtime-tests"}),
            ("gitlab_ci", "build:\n  script: >\n    runtime-tests:\n      script: echo fake\n# runtime-tests:\n", {"build"}),
        )
        for provider, body, expected in cases:
            with self.subTest(provider=provider, body=body):
                result = Result()
                self.assertEqual(ci_yaml_job_ids(body, provider, result), expected)
                self.assertEqual(result.errors, [])

    def test_duplicate_job_definitions_are_rejected(self) -> None:
        result = Result()
        ci_yaml_job_ids("jobs:\n  runtime-tests:\n    steps: []\n  runtime-tests:\n    steps: []\n", "github_actions", result)
        self.assertTrue(any("duplicate CI job" in error for error in result.errors))

    def test_unsupported_quoted_or_complex_scalars_stop_job_discovery(self) -> None:
        bodies = [
            multiline_ci_config(provider, quote)
            for provider in ("github_actions", "gitlab_ci")
            for quote in ("'", '"')
        ] + [
            'jobs:\n  build:\n    name: "sample\n  runtime-tests:\n    steps: []\n"\n',
            'jobs:\n  build:\n    env: {EXAMPLE: "sample\n  runtime-tests:\n    steps: []\n"}\n',
            'jobs:\n  "runtime-tests\n  continued":\n    steps: []\n',
            'jobs:\n  build:\n    steps:\n      - "sample\n  runtime-tests:\n    steps: []\n"\n',
            'jobs:\n  build:\n    env: [\n      "sample"\n    ]\n',
            'jobs:\n  build: &shared\n    runtime-tests:\n      steps: []\n',
            'jobs:\n  build:\n    name: !!str "sample\n  runtime-tests:\n    steps: []\n"\n',
            '? "sample\njobs:\n  runtime-tests:\n    steps: []\n"\n: value\n',
            '!custom "sample\njobs:\n  runtime-tests:\n    steps: []\n"\n',
        ]
        for body in bodies:
            with self.subTest(body=body):
                result = Result()
                self.assertEqual(ci_yaml_job_ids(body, "github_actions", result), set())
                self.assertTrue(any("unsupported CI YAML" in error and "provider_export" in error for error in result.errors))

    def test_single_line_quoting_does_not_change_shell_or_block_scalar_handling(self) -> None:
        values = (
            'name: "say \\"hello\\""',
            r'name: "ends with a backslash \\"',
            r'name: "escaped backslash and quote \\\" remain inside"',
            "name: 'it''s a job'",
            'name: plain # comment with an unmatched "',
            'run: printf "%s" "don\'t"',
            'env: {KEY: "can\'t", MORE: \'it\'\'s fine\'}',
            'runs-on: ["ubuntu-latest", self-hosted]',
            'run: |\n      text with unclosed " and \' is literal',
            'run: >-\n      runtime-tests: "literal only',
        )
        for value in values:
            with self.subTest(value=value):
                result = Result()
                body = "jobs:\n  build:\n    " + value + "\n"
                self.assertEqual(ci_yaml_job_ids(body, "github_actions", result), {"build"})
                self.assertEqual(result.errors, [])


class TestingRecordFormatTests(unittest.TestCase):
    def test_yaml_alias_list_items_are_rejected_but_quoted_literals_are_allowed(self) -> None:
        for body in ("items:\n  - *record\n", "*record\n", "items: &record.name\n  - TEST-1\n"):
            with self.subTest(body=body):
                result = Result()
                validate_yaml_subset(body, result, "matrix")
                self.assertTrue(any("unsupported YAML" in error for error in result.errors))
        result = Result()
        validate_yaml_subset('description: "*literal"\nitems: ["*literal"]\n', result, "matrix")
        self.assertEqual(result.errors, [])

    def test_root_list_and_dictionary_records_are_all_recognized(self) -> None:
        for body in (
            "item_id: TEST-1\nstatus: verified\n",
            "- item_id: TEST-1\n  status: verified\n",
            "TEST-1:\n  item_id: TEST-1\n  status: verified\n",
        ):
            with self.subTest(body=body):
                records = anchored_records(body, "item_id")
                self.assertEqual(len(records), 1)

    def test_dictionary_duplicates_and_unrecognized_results_fail(self) -> None:
        for body, message in (
            ("A:\n  item_id: TEST-1\nB:\n  item_id: TEST-1\n", "duplicate test result item_id"),
            ("TEST-1:\n  status: verified\n", "unrecognized test result record"),
            ("TEST-1:\n  item_id: TEST-1\nTEST-2:\n  status: failed\n", "unrecognized test result record"),
        ):
            with self.subTest(body=body):
                result = Result()
                testing_result_records(body, result)
                self.assertTrue(any(message in error for error in result.errors), result.errors)

    def test_long_evidence_exception_is_bound_to_the_frozen_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = root / "testing-runtime"
            runtime.mkdir()
            long_runtime = root / "long-runtime"
            long_runtime.mkdir()
            frozen = long_runtime / "long-readiness-receipt.json"
            frozen.write_text('{"frozen": true}', encoding="utf-8")
            unrelated = long_runtime / "unrelated.json"
            unrelated.write_text("{}", encoding="utf-8")
            for source, path, trusted, accepted in (
                ("long_readiness_receipt", frozen, frozen, True),
                ("long_readiness_receipt", unrelated, frozen, False),
                ("long_readiness_receipt", frozen, None, False),
                ("testing_runtime", frozen, frozen, False),
            ):
                with self.subTest(source=source, path=path, trusted=trusted):
                    parsed = entries(
                        f"E:\n  source: {source}\n  path: {path}\n"
                        f"  content_sha256: sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}\n"
                    )
                    result = Result()
                    resolved = validate_evidence_content(
                        runtime, "E", parsed, ("E",), result, long_receipt_path=trusted
                    )
                    self.assertEqual(not result.errors, accepted, result.errors)
                    if accepted:
                        self.assertEqual(resolved, frozen)

    def test_external_long_receipt_still_requires_matching_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = root / "testing-runtime"
            runtime.mkdir()
            receipt = root / "long-readiness-receipt.json"
            receipt.write_text("{}", encoding="utf-8")
            parsed = entries(
                "E:\n  source: long_readiness_receipt\n"
                f"  path: {receipt}\n  content_sha256: sha256:{'0' * 64}\n"
            )
            result = Result()
            validate_evidence_content(
                runtime, "E", parsed, ("E",), result, long_receipt_path=receipt
            )
            self.assertTrue(any("does not match content_sha256" in error for error in result.errors))

    def test_long_receipt_exception_does_not_allow_symbolic_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = root / "testing-runtime"
            runtime.mkdir()
            receipt = root / "long-readiness-receipt.json"
            receipt.write_text("{}", encoding="utf-8")
            link = root / "linked-receipt.json"
            try:
                link.symlink_to(receipt)
            except OSError:
                self.skipTest("symbolic links are unavailable")
            parsed = entries(
                "E:\n  source: long_readiness_receipt\n"
                f"  path: {link}\n  content_sha256: sha256:{hashlib.sha256(receipt.read_bytes()).hexdigest()}\n"
            )
            result = Result()
            validate_evidence_content(
                runtime, "E", parsed, ("E",), result, long_receipt_path=receipt
            )
            self.assertTrue(any("symbolic link" in error for error in result.errors), result.errors)


if __name__ == "__main__":
    unittest.main()

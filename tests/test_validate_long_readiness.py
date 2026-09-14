from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPOSITORY_ROOT
    / "skills/long-task-orchestrator/scripts/validate_long_readiness.py"
)
RUNNER = (
    REPOSITORY_ROOT
    / "skills/long-task-orchestrator/scripts/run_long_validation.py"
)
MACHINE_RUNNER = (
    REPOSITORY_ROOT
    / "skills/long-task-orchestrator/scripts/machine_execution_receipt.py"
)


def load_machine_runner():
    spec = importlib.util.spec_from_file_location("long_machine_runner_test", MACHINE_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load machine execution runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LongReadinessValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.runtime = Path(self.temp.name)
        self.write_valid_runtime()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, name: str, body: str) -> None:
        path = self.runtime / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")

    def write_valid_runtime(self) -> None:
        self.write(
            "current-runtime-context.md",
            """```yaml
runtime_epoch: phase-01-development-20260825
project_root_ref: .
planning_handoff_source: docs/planning/phase-01/planning-handoff.yaml
planning_baseline_revision: PLAN-3
incremental_execution_contract_snapshot:
  execute_only:
    - TASK-001@3
    - TASK-002@2
  resume_only: []
  reexecute_affected_part: []
  context_only: []
  completed_locked: []
  cancelled: []
execution_prerequisite_readiness_status: passed
current_effective_status: ready_for_local_test
ready_for_local_test_since: 2026-08-25T10:00:00Z
ready_for_local_retest_since: null
open_blockers: []
project_execution_baseline_file: project-execution-baseline.md
validation_results_file: validation-results.md
testing_handoff_file: testing-handoff.md
```
""",
        )
        self.replace(
            "current-runtime-context.md",
            "planning_handoff_source: docs/planning/phase-01/planning-handoff.yaml",
            "planning_handoff_source: planning-handoff.yaml",
        )
        self.write(
            "planning-handoff.yaml",
            """```yaml
handoff_type: execution_ready
requires_execution_handoff: true
planning_baseline_revision: PLAN-3
execution_prerequisite_readiness:
  contract_refs:
    architecture_and_database:
      - architecture.md
    capabilities: []
    dependencies: []
  before_long_status: passed
  ready_evidence_refs: []
  unresolved_before_long: []
incremental_execution_contract:
  planning_baseline_revision: PLAN-3
  execute_only:
    - TASK-001@3
    - TASK-002@2
  resume_only: []
  reexecute_affected_part: []
  context_only: []
  completed_locked: []
  cancelled: []
handoff_role_mapping:
  - role: Requirement and Scope
    path: requirement.md
  - role: Development Landing Checklist
    path: landing-checklist.md
  - role: Test and Acceptance Plan
    path: test-plan.md
  - role: Acceptance and Retrospective Record
    path: acceptance.md
```
""",
        )
        self.write(
            "test-plan.md",
            """### TEST-LOCAL-1：本地业务旅程

自动化等级：mandatory_automated

### TEST-CLOUD-1：部署后业务旅程

自动化等级：manual_or_real_environment_required
""",
        )
        self.write("requirement.md", "# Requirement and Scope\n")
        self.write("landing-checklist.md", "# Development Landing Checklist\n")
        self.write("acceptance.md", "# Acceptance Framework\n")
        self.write("architecture.md", "# Architecture and database contract\n")
        self.write("backend/source.txt", "backend delivery source\n")
        self.write("frontend/source.txt", "frontend delivery source\n")
        self.write(
            "topology.md",
            """```yaml
delivery_unit_inventory:
  units:
    - unit_id: backend
      source_roots:
        - backend
      source_refs:
        - backend/source.txt
    - unit_id: frontend
      source_roots:
        - frontend
      source_refs:
        - frontend/source.txt
```
""",
        )
        self.write(
            "project-execution-baseline.md",
            f"""```yaml
required_validation_matrix:
  matrix_revision: MATRIX-2
  completeness_audit:
    repository_scan_revision: sha256:repository-snapshot
    delivery_unit_inventory_refs:
      - topology.md
    changed_or_required_delivery_unit_ids:
      - backend
      - frontend
    mapped_delivery_unit_ids:
      - backend
      - frontend
    locally_automatable_planning_test_refs:
      - TEST-LOCAL-1
    mapped_planning_test_refs:
      - TEST-LOCAL-1
    manual_or_real_environment_planning_test_refs:
      - TEST-CLOUD-1
    handoff_manual_test_refs:
      - TEST-CLOUD-1
    open_gaps: []
    result: passed
  delivery_units:
    - unit_id: backend
      unit_type: service
      scope_relation: changed
      local_execution_mode: runnable
      requirements:
        - requirement_id: REQ-BUILD
          planning_test_refs: []
          validation_type: build
          validation_focus: artifact_readiness
          requirement_level: required
          binding_status: existing
          command_or_probe: pnpm backend:build
          success_postconditions:
            - artifact exists
            - artifact loads
          safe_execution_boundary: local
          machine_execution:
            working_directory_ref: .
            default_timeout_seconds: 30
            postcondition_probes:
              - postcondition: artifact exists
                probe_kind: path_exists
                path_ref: backend/source.txt
                expected_type: file
                nonempty: true
              - postcondition: artifact loads
                probe_kind: argv
                argv:
                  - {sys.executable}
                  - -c
                  - from pathlib import Path; raise SystemExit(0 if Path('backend/source.txt').read_text() else 1)
          not_applicable_reason: null
        - requirement_id: REQ-BACKEND-CONFIG
          planning_test_refs: []
          validation_type: smoke
          validation_focus: runtime_configuration
          requirement_level: not_applicable
          binding_status: existing
          command_or_probe: not_applicable
          success_postconditions: []
          safe_execution_boundary: local
          not_applicable_reason: no runtime configuration is required by this fixture
        - requirement_id: REQ-BACKEND-DEPENDENCY
          planning_test_refs: []
          validation_type: smoke
          validation_focus: dependency_readiness
          requirement_level: not_applicable
          binding_status: existing
          command_or_probe: not_applicable
          success_postconditions: []
          safe_execution_boundary: local
          not_applicable_reason: no external dependency is required by this fixture
        - requirement_id: REQ-BACKEND-PROCESS
          planning_test_refs: []
          validation_type: smoke
          validation_focus: process_readiness
          requirement_level: required
          binding_status: existing
          command_or_probe: pnpm backend:smoke
          success_postconditions:
            - process becomes ready
          safe_execution_boundary: local
          machine_execution:
            working_directory_ref: .
            default_timeout_seconds: 30
            postcondition_probes:
              - postcondition: process becomes ready
                probe_kind: argv
                argv:
                  - {sys.executable}
                  - -c
                  - raise SystemExit(0)
          not_applicable_reason: null
        - requirement_id: REQ-BACKEND-BEHAVIOR
          planning_test_refs: []
          validation_type: test
          validation_focus: business_rule
          requirement_level: required
          binding_status: existing
          command_or_probe: pnpm backend:behavior
          success_postconditions:
            - minimum behavior succeeds
          safe_execution_boundary: local
          machine_execution:
            working_directory_ref: .
            default_timeout_seconds: 30
            postcondition_probes:
              - postcondition: minimum behavior succeeds
                probe_kind: argv
                argv:
                  - {sys.executable}
                  - -c
                  - raise SystemExit(0)
          not_applicable_reason: null
    - unit_id: frontend
      unit_type: web_client
      scope_relation: changed
      local_execution_mode: runnable
      requirements:
        - requirement_id: REQ-FRONTEND-ARTIFACT
          planning_test_refs: []
          validation_type: build
          validation_focus: artifact_readiness
          requirement_level: not_applicable
          binding_status: existing
          command_or_probe: not_applicable
          success_postconditions: []
          safe_execution_boundary: local
          not_applicable_reason: fixture uses direct source execution
        - requirement_id: REQ-FRONTEND-CONFIG
          planning_test_refs: []
          validation_type: smoke
          validation_focus: runtime_configuration
          requirement_level: not_applicable
          binding_status: existing
          command_or_probe: not_applicable
          success_postconditions: []
          safe_execution_boundary: local
          not_applicable_reason: no runtime configuration is required by this fixture
        - requirement_id: REQ-FRONTEND-DEPENDENCY
          planning_test_refs: []
          validation_type: smoke
          validation_focus: dependency_readiness
          requirement_level: not_applicable
          binding_status: existing
          command_or_probe: not_applicable
          success_postconditions: []
          safe_execution_boundary: local
          not_applicable_reason: no external dependency is required by this fixture
        - requirement_id: REQ-FRONTEND-PROCESS
          planning_test_refs: []
          validation_type: smoke
          validation_focus: process_readiness
          requirement_level: required
          binding_status: existing
          command_or_probe: pnpm frontend:ready
          success_postconditions:
            - frontend process becomes ready
          safe_execution_boundary: local
          machine_execution:
            working_directory_ref: .
            default_timeout_seconds: 30
            postcondition_probes:
              - postcondition: frontend process becomes ready
                probe_kind: argv
                argv:
                  - {sys.executable}
                  - -c
                  - raise SystemExit(0)
          not_applicable_reason: null
        - requirement_id: REQ-SMOKE
          planning_test_refs:
            - TEST-LOCAL-1
          validation_type: playwright
          validation_focus: user_flow
          requirement_level: required
          binding_status: existing
          command_or_probe: pnpm frontend:smoke
          success_postconditions:
            - primary flow succeeds
          safe_execution_boundary: local
          machine_execution:
            working_directory_ref: .
            default_timeout_seconds: 30
            postcondition_probes:
              - postcondition: primary flow succeeds
                probe_kind: argv
                argv:
                  - {sys.executable}
                  - -c
                  - raise SystemExit(0)
          not_applicable_reason: null
```
""",
        )
        self.write(
            "validation-results.md",
            """```yaml
validation_id: VAL-BUILD-1
time: 2026-08-25T09:55:00Z
attempt: 1
related_task: TASK-001
validation_type: build
validation_focus: artifact_readiness
command:
  - pnpm backend:build
scope: backend
result: passed
matrix_revision: MATRIX-2
code_config_revision: sha256:repository-snapshot
requirement_id: REQ-BUILD
delivery_unit_id: backend
requirement_level: required
execution_receipt_ref: machine-execution-receipts/VAL-BUILD-1.json
postcondition_results:
  - postcondition: artifact exists
    result: passed
    evidence: machine-execution-receipts/VAL-BUILD-1.json
  - postcondition: artifact loads
    result: passed
    evidence: machine-execution-receipts/VAL-BUILD-1.json
matrix_compatibility: current
compatibility_evidence: []
evidence:
  - machine-execution-receipts/VAL-BUILD-1.json
  - evidence/backend-build.txt
```

```yaml
validation_id: VAL-BACKEND-PROCESS-1
time: 2026-08-25T09:56:00Z
attempt: 1
related_task: TASK-001
validation_type: smoke
validation_focus: process_readiness
command: [pnpm backend:smoke]
scope: backend
result: passed
matrix_revision: MATRIX-2
code_config_revision: sha256:repository-snapshot
requirement_id: REQ-BACKEND-PROCESS
delivery_unit_id: backend
requirement_level: required
execution_receipt_ref: machine-execution-receipts/VAL-BACKEND-PROCESS-1.json
postcondition_results:
  - postcondition: process becomes ready
    result: passed
    evidence: machine-execution-receipts/VAL-BACKEND-PROCESS-1.json
matrix_compatibility: current
compatibility_evidence: []
evidence: [machine-execution-receipts/VAL-BACKEND-PROCESS-1.json, evidence/backend-ready.txt]
```

```yaml
validation_id: VAL-BACKEND-BEHAVIOR-1
time: 2026-08-25T09:57:00Z
attempt: 1
related_task: TASK-001
validation_type: test
validation_focus: business_rule
command: [pnpm backend:behavior]
scope: backend
result: passed
matrix_revision: MATRIX-2
code_config_revision: sha256:repository-snapshot
requirement_id: REQ-BACKEND-BEHAVIOR
delivery_unit_id: backend
requirement_level: required
execution_receipt_ref: machine-execution-receipts/VAL-BACKEND-BEHAVIOR-1.json
postcondition_results:
  - postcondition: minimum behavior succeeds
    result: passed
    evidence: machine-execution-receipts/VAL-BACKEND-BEHAVIOR-1.json
matrix_compatibility: current
compatibility_evidence: []
evidence: [machine-execution-receipts/VAL-BACKEND-BEHAVIOR-1.json, evidence/backend-behavior.txt]
```

```yaml
validation_id: VAL-FRONTEND-PROCESS-1
time: 2026-08-25T09:57:30Z
attempt: 1
related_task: TASK-002
validation_type: smoke
validation_focus: process_readiness
command: [pnpm frontend:ready]
scope: frontend
result: passed
matrix_revision: MATRIX-2
code_config_revision: sha256:repository-snapshot
requirement_id: REQ-FRONTEND-PROCESS
delivery_unit_id: frontend
requirement_level: required
execution_receipt_ref: machine-execution-receipts/VAL-FRONTEND-PROCESS-1.json
postcondition_results:
  - postcondition: frontend process becomes ready
    result: passed
    evidence: machine-execution-receipts/VAL-FRONTEND-PROCESS-1.json
matrix_compatibility: current
compatibility_evidence: []
evidence: [machine-execution-receipts/VAL-FRONTEND-PROCESS-1.json, evidence/frontend-ready.txt]
```

```yaml
validation_id: VAL-SMOKE-1
time: 2026-08-25T09:58:00Z
attempt: 1
related_task: TASK-002
validation_type: playwright
validation_focus: user_flow
command:
  - pnpm frontend:smoke
scope: frontend
result: passed
matrix_revision: MATRIX-2
code_config_revision: sha256:repository-snapshot
requirement_id: REQ-SMOKE
delivery_unit_id: frontend
requirement_level: required
execution_receipt_ref: machine-execution-receipts/VAL-SMOKE-1.json
postcondition_results:
  - postcondition: primary flow succeeds
    result: passed
    evidence: machine-execution-receipts/VAL-SMOKE-1.json
matrix_compatibility: current
compatibility_evidence: []
evidence:
  - machine-execution-receipts/VAL-SMOKE-1.json
  - evidence/frontend-smoke.txt
```
""",
        )
        self.write(
            "testing-handoff.md",
            """```yaml
runtime_epoch: phase-01-development-20260825
planning_handoff_ref: planning-handoff.yaml
planning_baseline_revision: PLAN-3
executed_task_contract_revisions:
  - TASK-001@3
  - TASK-002@2
automated_passed:
  - id: AUTO-1
    source_validation_id: VAL-BUILD-1
  - id: AUTO-2
    source_validation_id: VAL-SMOKE-1
  - id: AUTO-3
    source_validation_id: VAL-BACKEND-PROCESS-1
  - id: AUTO-4
    source_validation_id: VAL-BACKEND-BEHAVIOR-1
  - id: AUTO-5
    source_validation_id: VAL-FRONTEND-PROCESS-1
manual_required:
  - id: MANUAL-CLOUD-1
    planning_test_refs:
      - TEST-CLOUD-1
    scope: deployed primary flow
    owner_runtime: testing-layer-runtime
required_validation_gate:
  matrix_ref: project-execution-baseline.md#required_validation_matrix
  matrix_revision: MATRIX-2
  effective_validation_ids:
    - VAL-BUILD-1
    - VAL-BACKEND-PROCESS-1
    - VAL-BACKEND-BEHAVIOR-1
    - VAL-FRONTEND-PROCESS-1
    - VAL-SMOKE-1
  result: passed
formal_acceptance_record_path: acceptance.md
acceptance_status: not_started
owner_runtime: testing-layer-runtime
validator_receipt_ref: long-readiness-receipt.json
```
""",
        )
        inventory_records = []
        for unit_id, source_ref in (
            ("backend", "backend/source.txt"),
            ("frontend", "frontend/source.txt"),
        ):
            source_digest = hashlib.sha256(
                (self.runtime / source_ref).read_bytes()
            ).hexdigest()
            inventory_records.append(
                {
                    "unit_id": unit_id,
                    "sources": [{"ref": source_ref, "sha256": source_digest}],
                }
            )
        repository_revision = "sha256:" + hashlib.sha256(
            json.dumps(
                inventory_records,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        self.replace(
            "project-execution-baseline.md",
            "sha256:repository-snapshot",
            repository_revision,
        )
        self.replace(
            "validation-results.md",
            "sha256:repository-snapshot",
            repository_revision,
        )
        evidence_refs = set(
            re.findall(
                r"\bevidence/[A-Za-z0-9._/-]+",
                (self.runtime / "validation-results.md").read_text(encoding="utf-8"),
            )
        )
        for evidence_ref in evidence_refs:
            evidence_path = self.runtime / evidence_ref
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            evidence_path.write_text(
                f"recorded validation evidence for {evidence_ref}\n", encoding="utf-8"
            )
        for stage in ("preflight", "execution"):
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(self.runtime),
                    "--advance-workflow",
                    stage,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode:
                raise AssertionError(completed.stderr)
        for requirement_id, validation_id in (
            ("REQ-BUILD", "VAL-BUILD-1"),
            ("REQ-BACKEND-PROCESS", "VAL-BACKEND-PROCESS-1"),
            ("REQ-BACKEND-BEHAVIOR", "VAL-BACKEND-BEHAVIOR-1"),
            ("REQ-FRONTEND-PROCESS", "VAL-FRONTEND-PROCESS-1"),
            ("REQ-SMOKE", "VAL-SMOKE-1"),
        ):
            executed = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    str(self.runtime),
                    "--requirement-id",
                    requirement_id,
                    "--validation-id",
                    validation_id,
                    "--attempt",
                    "1",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if executed.returncode:
                raise AssertionError(executed.stderr)
        for stage in ("completion_validation", "ready_for_local_test"):
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(self.runtime),
                    "--advance-workflow",
                    stage,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode:
                raise AssertionError(completed.stderr)
        receipt = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(self.runtime),
                "--expect-ready",
                "--write-receipt",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if receipt.returncode:
            raise AssertionError(receipt.stderr)

    def run_validator(self, expect_ready: bool = True) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(SCRIPT), str(self.runtime)]
        if expect_ready:
            command.append("--expect-ready")
        return subprocess.run(command, capture_output=True, text=True, check=False)

    def replace(self, filename: str, old: str, new: str) -> None:
        path = self.runtime / filename
        path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    def test_valid_runtime_passes_candidate_and_ready_checks(self) -> None:
        self.assertEqual(self.run_validator(expect_ready=False).returncode, 0)
        ready = self.run_validator(expect_ready=True)
        self.assertEqual(ready.returncode, 0, ready.stderr)

    def test_source_root_freezes_files_not_repeated_as_source_refs(self) -> None:
        self.write("backend/new-module.ts", "export const changed = true;\n")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("repository_scan_revision", result.stderr)

    def test_handoff_cannot_add_a_non_effective_automated_result(self) -> None:
        self.replace(
            "testing-handoff.md",
            "automated_passed:\n",
            "automated_passed:\n  - id: AUTO-EXTRA\n    source_validation_id: DOES-NOT-EXIST\n",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exactly the effective required validations", result.stderr)

    def test_validation_timestamp_without_timezone_is_rejected_without_crash(self) -> None:
        self.replace(
            "validation-results.md",
            "time: 2026-08-25T09:55:00Z",
            "time: 2026-08-25T09:55:00",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("timezone-aware ISO-8601", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_source_tree_symbolic_link_is_rejected(self) -> None:
        outside = self.runtime / "outside-source.txt"
        outside.write_text("outside\n", encoding="utf-8")
        link = self.runtime / "backend" / "linked-source.txt"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symbolic links are unavailable on this platform")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symbolic link", result.stderr)

    def test_ready_receipt_rejects_an_unfrozen_runtime_artifact(self) -> None:
        self.write("late-artifact.txt", "created after readiness\n")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("artifact inventory", result.stderr)

    def test_ready_receipt_never_hashes_a_secret_bearing_runtime_path(self) -> None:
        self.write(".env", "DATABASE_URL=must-not-be-read-into-receipt\n")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("secret-bearing path", result.stderr)

    def test_missing_required_result_is_rejected(self) -> None:
        body = (self.runtime / "validation-results.md").read_text(encoding="utf-8")
        body = body.split("\n```\n\n```yaml\nvalidation_id: VAL-SMOKE-1", 1)[0] + "\n```\n"
        self.write("validation-results.md", body)
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("REQ-SMOKE: current validation result is missing", result.stderr)

    def test_latest_failed_result_overrides_prior_pass(self) -> None:
        path = self.runtime / "validation-results.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + """
```yaml
validation_id: VAL-BUILD-2
time: 2026-08-25T10:01:00Z
attempt: 2
related_task: TASK-001
validation_type: build
validation_focus: artifact_readiness
command:
  - pnpm backend:build
scope: backend
result: failed
matrix_revision: MATRIX-2
code_config_revision: sha256:repository-snapshot
requirement_id: REQ-BUILD
delivery_unit_id: backend
requirement_level: required
postcondition_results:
  - postcondition: artifact exists
    result: failed
    evidence: evidence/backend-build-failed.txt
  - postcondition: artifact loads
    result: blocked
    evidence: evidence/backend-load-blocked.txt
matrix_compatibility: current
compatibility_evidence: []
evidence:
  - evidence/backend-build-failed.txt
```
""",
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("REQ-BUILD: latest result must be passed", result.stderr)
        self.assertIn("effective validation ids", result.stderr)

    def test_postcondition_coverage_must_match_matrix(self) -> None:
        self.replace(
            "validation-results.md",
            "  - postcondition: artifact loads\n    result: passed\n    evidence: machine-execution-receipts/VAL-BUILD-1.json\n",
            "",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("postcondition coverage does not match", result.stderr)

    def test_delivery_unit_omission_is_rejected(self) -> None:
        self.replace(
            "project-execution-baseline.md",
            "    mapped_delivery_unit_ids:\n      - backend\n      - frontend\n",
            "    mapped_delivery_unit_ids:\n      - backend\n",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("delivery-unit completeness collections do not match", result.stderr)

    def test_claimed_planning_test_mapping_requires_actual_requirement_binding(self) -> None:
        self.replace("project-execution-baseline.md", "            - TEST-LOCAL-1\n", "")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required Matrix requirement bindings", result.stderr)

    def test_manual_planning_test_handoff_must_reconcile(self) -> None:
        self.replace("testing-handoff.md", "TEST-CLOUD-1", "TEST-CLOUD-OTHER")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("manual Planning TEST refs do not match", result.stderr)

    def test_handoff_epoch_and_matrix_must_match(self) -> None:
        self.replace("testing-handoff.md", "phase-01-development-20260825", "wrong-epoch")
        self.replace("testing-handoff.md", "matrix_revision: MATRIX-2", "matrix_revision: MATRIX-OLD")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("handoff.runtime_epoch", result.stderr)
        self.assertIn("handoff matrix revision mismatch", result.stderr)

    def test_duplicate_validation_ids_are_rejected(self) -> None:
        self.replace("validation-results.md", "VAL-SMOKE-1", "VAL-BUILD-1")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("validation ids must contain unique values", result.stderr)

    def test_ready_state_requires_timestamp_and_no_blockers(self) -> None:
        self.replace("current-runtime-context.md", "ready_for_local_test_since: 2026-08-25T10:00:00Z", "ready_for_local_test_since: null")
        self.replace("current-runtime-context.md", "open_blockers: []", "open_blockers: [BLOCK-1]")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ready_for_local_test_since", result.stderr)
        self.assertIn("open_blockers", result.stderr)

    def test_context_pointer_must_resolve_to_this_runtime(self) -> None:
        self.replace(
            "current-runtime-context.md",
            "testing_handoff_file: testing-handoff.md",
            "testing_handoff_file: ../stale-runtime/testing-handoff.md",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must resolve exactly", result.stderr)

    def test_planning_handoff_must_exist_and_match(self) -> None:
        self.replace(
            "current-runtime-context.md",
            "planning_handoff_source: planning-handoff.yaml",
            "planning_handoff_source: missing-planning-handoff.yaml",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not resolve to an existing file", result.stderr)

    def test_executed_task_revisions_are_required_and_exact(self) -> None:
        self.replace(
            "testing-handoff.md",
            "executed_task_contract_revisions:\n  - TASK-001@3\n  - TASK-002@2\n",
            "executed_task_contract_revisions: []\n",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("executed_task_contract_revisions must not be empty", result.stderr)

    def test_runnable_unit_cannot_use_artifact_check_as_whole_gate(self) -> None:
        self.replace(
            "project-execution-baseline.md",
            "validation_focus: process_readiness\n          requirement_level: required",
            "validation_focus: process_readiness\n          requirement_level: optional",
        )
        self.replace(
            "project-execution-baseline.md",
            "validation_focus: business_rule\n          requirement_level: required",
            "validation_focus: business_rule\n          requirement_level: optional",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("runnable unit requires process_readiness", result.stderr)
        self.assertIn("minimum behavior validation", result.stderr)

    def test_inventory_reference_must_exist(self) -> None:
        self.replace("project-execution-baseline.md", "- topology.md", "- missing-topology.md")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("delivery unit inventory ref", result.stderr)

    def test_code_config_revision_must_match_repository_scan(self) -> None:
        path = self.runtime / "validation-results.md"
        path.write_text(
            re.sub(
                r"code_config_revision: sha256:[0-9a-f]+",
                "code_config_revision: sha256:stale-snapshot",
                path.read_text(encoding="utf-8"),
                count=1,
            ),
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("code/config revision", result.stderr)

    def test_attempt_order_cannot_hide_a_newer_failure(self) -> None:
        path = self.runtime / "validation-results.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + """
```yaml
validation_id: VAL-BUILD-2
time: 2026-08-25T09:00:00Z
attempt: 2
related_task: TASK-001
validation_type: build
validation_focus: artifact_readiness
command: [pnpm backend:build]
scope: backend
result: passed
matrix_revision: MATRIX-2
code_config_revision: sha256:repository-snapshot
requirement_id: REQ-BUILD
delivery_unit_id: backend
requirement_level: required
postcondition_results:
  - postcondition: artifact exists
    result: passed
    evidence: evidence/old-build.txt
  - postcondition: artifact loads
    result: passed
    evidence: evidence/old-load.txt
matrix_compatibility: current
compatibility_evidence: []
evidence: [evidence/old-build.txt]
```
""",
            encoding="utf-8",
        )
        self.replace("testing-handoff.md", "VAL-BUILD-1", "VAL-BUILD-2")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("attempt order conflicts", result.stderr)

    def test_mandatory_automated_planning_test_cannot_be_deferred_to_manual(self) -> None:
        self.replace(
            "project-execution-baseline.md",
            "    locally_automatable_planning_test_refs:\n      - TEST-LOCAL-1\n    mapped_planning_test_refs:\n      - TEST-LOCAL-1\n    manual_or_real_environment_planning_test_refs:\n      - TEST-CLOUD-1\n    handoff_manual_test_refs:\n      - TEST-CLOUD-1",
            "    locally_automatable_planning_test_refs: []\n    mapped_planning_test_refs: []\n    manual_or_real_environment_planning_test_refs:\n      - TEST-LOCAL-1\n      - TEST-CLOUD-1\n    handoff_manual_test_refs:\n      - TEST-LOCAL-1\n      - TEST-CLOUD-1",
        )
        self.replace(
            "project-execution-baseline.md",
            "          planning_test_refs:\n            - TEST-LOCAL-1\n          validation_type: playwright",
            "          planning_test_refs: []\n          validation_type: playwright",
        )
        self.replace(
            "testing-handoff.md",
            "    planning_test_refs:\n      - TEST-CLOUD-1",
            "    planning_test_refs:\n      - TEST-LOCAL-1\n      - TEST-CLOUD-1",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mandatory_automated", result.stderr)

    def test_inventory_must_be_structured_and_bound_to_real_sources(self) -> None:
        self.write("topology.md", "# Delivery Unit Inventory\n")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("delivery_unit_inventory", result.stderr)

    def test_planning_prerequisite_contract_and_evidence_envelope_is_required(self) -> None:
        self.replace(
            "planning-handoff.yaml",
            "  contract_refs:\n    architecture_and_database:\n      - architecture.md\n    capabilities: []\n    dependencies: []\n",
            "",
        )
        self.replace("planning-handoff.yaml", "  ready_evidence_refs: []\n", "")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contract_refs", result.stderr)
        self.assertIn("ready_evidence_refs", result.stderr)

    def test_validation_evidence_must_resolve_to_a_durable_file(self) -> None:
        (self.runtime / "evidence/backend-build.txt").unlink()
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("validation evidence", result.stderr)

    def test_agent_written_pass_without_machine_receipt_is_rejected(self) -> None:
        self.replace(
            "validation-results.md",
            "execution_receipt_ref: machine-execution-receipts/VAL-BUILD-1.json",
            "execution_receipt_ref: null",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("execution_receipt_ref is required", result.stderr)

    def test_tampered_machine_receipt_is_rejected(self) -> None:
        path = self.runtime / "machine-execution-receipts/VAL-BUILD-1.json"
        receipt = json.loads(path.read_text(encoding="utf-8"))
        receipt["repository_revision"] = "sha256:tampered"
        path.write_text(json.dumps(receipt), encoding="utf-8")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("execution receipt digest is invalid", result.stderr)
        self.assertIn("execution receipt repository_revision mismatch", result.stderr)

    def test_machine_runner_fails_when_success_path_is_missing_and_never_overwrites(self) -> None:
        advanced = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(self.runtime),
                "--advance-workflow",
                "patch_execution",
                "--cycle-kind",
                "patch",
                "--new-cycle",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(advanced.returncode, 0, advanced.stderr)
        self.replace(
            "project-execution-baseline.md",
            "path_ref: backend/source.txt",
            "path_ref: backend/missing-build-artifact.js",
        )
        command = [
            sys.executable,
            str(RUNNER),
            str(self.runtime),
            "--requirement-id",
            "REQ-BUILD",
            "--validation-id",
            "VAL-BUILD-FAIL",
            "--attempt",
            "2",
        ]
        failed = subprocess.run(
            command, capture_output=True, text=True, check=False
        )
        self.assertNotEqual(failed.returncode, 0)
        receipt_path = (
            self.runtime / "machine-execution-receipts/VAL-BUILD-FAIL.json"
        )
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(receipt["result"], "failed")
        self.assertEqual(
            receipt["postcondition_results"][0]["observed_type"], "missing"
        )
        repeated = subprocess.run(
            command, capture_output=True, text=True, check=False
        )
        self.assertNotEqual(repeated.returncode, 0)
        self.assertIn("receipt already exists", repeated.stderr)

    def test_argv_runner_streams_output_and_records_bounded_metadata(self) -> None:
        machine_runner = load_machine_runner()
        result = machine_runner._run_argv(
            [
                sys.executable,
                "-c",
                "import sys; sys.stdout.buffer.write(b'x' * 2097152); sys.stderr.buffer.write(b'y' * 1048576)",
            ],
            self.runtime,
            10,
        )
        self.assertEqual(result["result"], "passed")
        self.assertEqual(result["stdout_bytes"], 2097152)
        self.assertEqual(result["stderr_bytes"], 1048576)
        self.assertEqual(result["process_tree_cleanup"], "not_required")

    def test_argv_runner_timeout_closes_the_process_tree(self) -> None:
        machine_runner = load_machine_runner()
        result = machine_runner._run_argv(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            self.runtime,
            1,
        )
        self.assertEqual(result["result"], "failed")
        self.assertEqual(result["error_kind"], "timeout")
        self.assertIn(
            result["process_tree_cleanup"],
            {"terminated", "terminated_direct_process_only"},
        )

    @unittest.skipIf(sys.platform == "win32", "POSIX process-group fixture")
    def test_argv_runner_rejects_a_leaked_background_process(self) -> None:
        machine_runner = load_machine_runner()
        result = machine_runner._run_argv(
            [
                sys.executable,
                "-c",
                "import subprocess,sys; subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); print('parent done')",
            ],
            self.runtime,
            10,
        )
        self.assertEqual(result["result"], "failed")
        self.assertEqual(result["error_kind"], "inherited_output_pipe_open")
        self.assertIn(
            result["process_tree_cleanup"],
            {"terminated", "terminated_direct_process_only"},
        )

    def test_forward_workflow_rejects_stage_skip_and_backward_transition(self) -> None:
        (self.runtime / "long-workflow-state.json").unlink()
        skipped = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(self.runtime),
                "--advance-workflow",
                "execution",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(skipped.returncode, 0)
        self.assertIn("not a legal forward transition", skipped.stderr)

        first = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.runtime), "--advance-workflow", "preflight"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        repeated = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.runtime), "--advance-workflow", "preflight"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(repeated.returncode, 0)
        self.assertIn("not a legal forward transition", repeated.stderr)

    def test_execution_entry_does_not_require_future_delivery_files(self) -> None:
        (self.runtime / "long-workflow-state.json").unlink()
        (self.runtime / "backend/source.txt").unlink()
        (self.runtime / "frontend/source.txt").unlink()
        self.replace(
            "project-execution-baseline.md",
            "binding_status: existing",
            "binding_status: planned_in_confirmed_task\n          planned_task_revision: TASK-001@3",
        )
        self.replace(
            "project-execution-baseline.md",
            "    result: passed",
            "    result: pending",
        )
        for stage in ("preflight", "execution"):
            advanced = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(self.runtime),
                    "--advance-workflow",
                    stage,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(advanced.returncode, 0, advanced.stderr)

        completion = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(self.runtime),
                "--advance-workflow",
                "completion_validation",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(completion.returncode, 0)
        self.assertIn("source_ref", completion.stderr)

    def test_patch_uses_a_new_forward_cycle_and_cannot_reenter_initial_stages(self) -> None:
        for stage, extra in (
            ("patch_execution", ["--cycle-kind", "patch", "--new-cycle"]),
            ("patch_validation", ["--cycle-kind", "patch"]),
        ):
            advanced = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(self.runtime),
                    "--advance-workflow",
                    stage,
                    *extra,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(advanced.returncode, 0, advanced.stderr)

        self.replace(
            "current-runtime-context.md",
            "current_effective_status: ready_for_local_test",
            "current_effective_status: ready_for_local_retest",
        )
        self.replace(
            "current-runtime-context.md",
            "ready_for_local_retest_since: null",
            "ready_for_local_retest_since: 2026-08-25T11:00:00Z",
        )
        ready = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(self.runtime),
                "--advance-workflow",
                "ready_for_local_retest",
                "--cycle-kind",
                "patch",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(ready.returncode, 0, ready.stderr)

        backward = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(self.runtime),
                "--advance-workflow",
                "execution",
                "--cycle-kind",
                "patch",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(backward.returncode, 0)
        self.assertIn("not a legal forward transition", backward.stderr)

    def test_validation_stage_repair_opens_a_new_forward_patch_cycle(self) -> None:
        (self.runtime / "long-workflow-state.json").unlink()
        for stage in ("preflight", "execution", "completion_validation"):
            advanced = subprocess.run(
                [sys.executable, str(SCRIPT), str(self.runtime), "--advance-workflow", stage],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(advanced.returncode, 0, advanced.stderr)

        repaired = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(self.runtime),
                "--advance-workflow",
                "patch_execution",
                "--cycle-kind",
                "patch",
                "--new-cycle",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(repaired.returncode, 0, repaired.stderr)
        ledger = json.loads((self.runtime / "long-workflow-state.json").read_text(encoding="utf-8"))
        self.assertEqual(ledger["current_cycle"], 2)
        self.assertEqual(ledger["current_stage"], "patch_execution")


if __name__ == "__main__":
    unittest.main()

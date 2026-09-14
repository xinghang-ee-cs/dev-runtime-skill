import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = (
    ROOT
    / "skills"
    / "testing-layer-runtime"
    / "scripts"
    / "validate_bugfix_case.py"
)
TEMPLATE_DIRECTORY = (
    ROOT
    / "skills"
    / "ai-code-inspection"
    / "assets"
    / "bugfix-case-template"
)
SPEC = importlib.util.spec_from_file_location("validate_bugfix_case", VALIDATOR_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


RECORDS = (
    "00-bug-contract.md",
    "01-long-patch-result.md",
    "02-test-verification.md",
    "03-release-verification.md",
    "04-similar-bug-review.md",
)


def diagnosed_case() -> dict:
    data = json.loads(
        (TEMPLATE_DIRECTORY / "bugfix-case.json").read_text(encoding="utf-8")
    )
    data.update(
        {
            "bug_id": "BUG-20260914-001",
            "release_status": "not_started",
            "original_bug_status": "pending",
            "bugfix_status": "diagnosed",
            "workflow_completed": False,
        }
    )
    data["issue"].update(
        {
            "provider": "github",
            "number": 123,
            "url": "https://github.com/example/project/issues/123",
            "status": "open",
        }
    )
    data["origin"].update(
        {
            "phase_ref": "docs/planning/phase-1",
            "planning_contract_ref": "docs/planning/phase-1/13-task.md@rev-1",
            "expected_behavior_source": "TEST-LOGIN-1@rev-1",
            "observed_environment": "production",
            "deployed_revision": "abc123",
        }
    )
    data["triage"].update(
        {
            "finding_type": "implementation_defect",
            "disposition": "fix_in_execution",
            "current_planning_contract_valid": True,
        }
    )
    data["scope"].update(
        {
            "allowed_paths": ["src/login.ts", "tests/login.test.ts"],
            "regression_targets": ["expired session redirects to login"],
            "adjacent_risk_targets": ["valid session remains authenticated"],
        }
    )
    data["timestamps"].update(
        {
            "created_at": "2026-09-14T09:00:00Z",
            "updated_at": "2026-09-14T09:00:00Z",
        }
    )
    return data


class BugfixCaseValidatorTests(unittest.TestCase):
    def write_case(self, root: Path, data: dict) -> Path:
        case = root / data["bug_id"]
        case.mkdir()
        (case / "bugfix-case.json").write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
        for record in RECORDS:
            (case / record).write_text(
                (TEMPLATE_DIRECTORY / record).read_text(encoding="utf-8"),
                encoding="utf-8",
            )
        return case

    def test_diagnosed_case_is_valid_and_routes_to_long(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            case = self.write_case(Path(directory), diagnosed_case())
            result = MODULE.validate_case(case, "diagnosed")
        self.assertEqual(result.errors, [])

    def test_awaiting_similar_verification_is_not_completed(self) -> None:
        data = diagnosed_case()
        data.update(
            {
                "release_status": "deployed",
                "original_bug_status": "production_verified",
                "bugfix_status": "awaiting_similar_defect_verification",
                "next_required_action": {
                    "action": "post_release_similar_defect_verification",
                    "primary_owner": "testing-layer-runtime",
                    "supporting_skill": "ai-code-inspection",
                    "target_record": "04-similar-bug-review.md",
                    "status": "pending",
                },
            }
        )
        data["delivery"].update(
            {
                "branch": "fix/BUG-20260914-001-session",
                "pull_request_url": "https://github.com/example/project/pull/124",
                "ci_status": "passed",
                "merge_commit": "def456",
                "deployed_revision": "def456",
                "version": "1.2.4",
                "rollback_ref": "abc123",
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            case = self.write_case(Path(directory), data)
            result = MODULE.validate_case(case)
        self.assertEqual(result.errors, [])
        self.assertFalse(data["workflow_completed"])
        self.assertEqual(data["issue"]["status"], "open")

    def test_deployed_case_cannot_claim_completion(self) -> None:
        data = diagnosed_case()
        data["bugfix_status"] = "deployed"
        data["workflow_completed"] = True
        data["issue"]["status"] = "closed"
        data["release_status"] = "deployed"
        data["next_required_action"] = None
        data["delivery"].update(
            {
                "branch": "fix/BUG-20260914-001-session",
                "pull_request_url": "https://github.com/example/project/pull/124",
                "ci_status": "passed",
                "merge_commit": "def456",
                "deployed_revision": "def456",
                "version": "1.2.4",
                "rollback_ref": "abc123",
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            case = self.write_case(Path(directory), data)
            result = MODULE.validate_case(case)
        self.assertIn(
            "workflow_completed may be true only when bugfix_status is closed",
            result.errors,
        )
        self.assertIn("Issue must stay open until the Case is closed", result.errors)

    def test_contract_change_is_rejected_from_fast_lane(self) -> None:
        data = diagnosed_case()
        data["triage"]["finding_type"] = "requirement_change"
        data["triage"]["current_planning_contract_valid"] = False
        with tempfile.TemporaryDirectory() as directory:
            case = self.write_case(Path(directory), data)
            result = MODULE.validate_case(case)
        self.assertIn("Fast Lane requires implementation_defect", result.errors)
        self.assertIn("current Planning contract must remain valid", result.errors)

    def test_closed_case_requires_reviewed_similar_defects_and_closed_issue(self) -> None:
        data = diagnosed_case()
        data.update(
            {
                "release_status": "deployed",
                "original_bug_status": "production_verified",
                "bugfix_status": "closed",
                "workflow_completed": True,
                "next_required_action": None,
            }
        )
        data["issue"]["status"] = "closed"
        data["similar_defect_review"]["status"] = "reviewed"
        data["delivery"].update(
            {
                "branch": "fix/BUG-20260914-001-session",
                "pull_request_url": "https://github.com/example/project/pull/124",
                "ci_status": "passed",
                "merge_commit": "def456",
                "deployed_revision": "def456",
                "version": "1.2.4",
                "rollback_ref": "abc123",
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            case = self.write_case(Path(directory), data)
            result = MODULE.validate_case(case, "closed")
        self.assertEqual(result.errors, [])


if __name__ == "__main__":
    unittest.main()

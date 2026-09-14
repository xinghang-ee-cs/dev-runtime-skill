#!/usr/bin/env python3
"""Validate the durable Bugfix Fast Lane lifecycle."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "bugfix-case/v1"
BUG_ID = re.compile(r"^BUG-\d{8}-\d{3,}$")
STATES = (
    "diagnosed",
    "patching",
    "ready_for_bug_verification",
    "bug_verifying",
    "verified_for_release",
    "merged",
    "deployed",
    "original_bug_production_verified",
    "awaiting_similar_defect_verification",
    "similar_defect_verifying",
    "similar_defect_reviewed",
    "closed",
)
STATE_RANK = {state: rank for rank, state in enumerate(STATES)}
REQUIRED_RECORDS = (
    "bugfix-case.json",
    "00-bug-contract.md",
    "01-long-patch-result.md",
    "02-test-verification.md",
    "03-release-verification.md",
    "04-similar-bug-review.md",
)


@dataclass
class Result:
    errors: list[str] = field(default_factory=list)

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(nonempty(item) for item in value)
    )


def rank_at_least(state: str, minimum: str) -> bool:
    return state in STATE_RANK and STATE_RANK[state] >= STATE_RANK[minimum]


def validate_next_action(
    data: dict[str, Any],
    result: Result,
    *,
    action: str,
    owner: str,
    target: str,
    status: str,
) -> None:
    next_action = mapping(data.get("next_required_action"))
    result.require(next_action.get("action") == action, f"next action must be {action}")
    result.require(
        next_action.get("primary_owner") == owner,
        f"next action owner must be {owner}",
    )
    result.require(
        next_action.get("target_record") == target,
        f"next action target must be {target}",
    )
    result.require(
        next_action.get("status") == status,
        f"next action status must be {status}",
    )


def validate_case(case_directory: Path, expected_state: str | None = None) -> Result:
    result = Result()
    state_path = case_directory / "bugfix-case.json"
    if not state_path.is_file():
        result.errors.append(f"missing file: {state_path}")
        return result

    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        result.errors.append(f"invalid bugfix-case.json: {error}")
        return result

    result.require(isinstance(data, dict), "bugfix-case.json root must be an object")
    if not isinstance(data, dict):
        return result

    state = data.get("bugfix_status")
    result.require(data.get("schema_version") == SCHEMA_VERSION, f"schema_version must be {SCHEMA_VERSION}")
    result.require(isinstance(state, str) and state in STATE_RANK, "bugfix_status is invalid")
    if expected_state:
        result.require(state == expected_state, f"bugfix_status must be {expected_state}")

    bug_id = data.get("bug_id")
    result.require(isinstance(bug_id, str) and BUG_ID.fullmatch(bug_id) is not None, "bug_id must match BUG-YYYYMMDD-NNN")
    result.require(case_directory.name == bug_id, "case directory name must equal bug_id")

    issue = mapping(data.get("issue"))
    result.require(issue.get("provider") == "github", "issue.provider must be github")
    result.require(isinstance(issue.get("number"), int) and issue.get("number", 0) > 0, "issue.number must be positive")
    result.require(nonempty(issue.get("url")) and str(issue.get("url")).startswith("https://github.com/"), "issue.url must be a GitHub URL")
    result.require(issue.get("status") in {"open", "closed"}, "issue.status must be open or closed")

    origin = mapping(data.get("origin"))
    for key in ("phase_ref", "expected_behavior_source", "observed_environment"):
        result.require(nonempty(origin.get(key)), f"origin.{key} is required")

    triage = mapping(data.get("triage"))
    result.require(triage.get("finding_type") == "implementation_defect", "Fast Lane requires implementation_defect")
    result.require(triage.get("disposition") == "fix_in_execution", "Fast Lane requires fix_in_execution")
    result.require(triage.get("current_planning_contract_valid") is True, "current Planning contract must remain valid")

    scope = mapping(data.get("scope"))
    result.require(string_list(scope.get("allowed_paths")), "scope.allowed_paths must be a non-empty string list")
    result.require(string_list(scope.get("regression_targets")), "scope.regression_targets must be a non-empty string list")
    result.require(string_list(scope.get("adjacent_risk_targets")), "scope.adjacent_risk_targets must be a non-empty string list")

    delivery = mapping(data.get("delivery"))
    result.require(delivery.get("issue_link_mode") == "refs", "product Bug PR must use Refs, not an auto-close link")

    timestamps = mapping(data.get("timestamps"))
    result.require(nonempty(timestamps.get("created_at")), "timestamps.created_at is required")
    result.require(nonempty(timestamps.get("updated_at")), "timestamps.updated_at is required")

    if not isinstance(state, str) or state not in STATE_RANK:
        return result

    for record in REQUIRED_RECORDS:
        result.require((case_directory / record).is_file(), f"missing record: {record}")

    workflow_completed = data.get("workflow_completed")
    result.require(isinstance(workflow_completed, bool), "workflow_completed must be boolean")
    result.require(workflow_completed is (state == "closed"), "workflow_completed may be true only when bugfix_status is closed")
    result.require(issue.get("status") == ("closed" if state == "closed" else "open"), "Issue must stay open until the Case is closed")

    if state == "diagnosed":
        validate_next_action(data, result, action="long_bugfix_patch", owner="long-task-orchestrator", target="01-long-patch-result.md", status="pending")
    if state == "ready_for_bug_verification":
        validate_next_action(data, result, action="bugfix_verification", owner="testing-layer-runtime", target="02-test-verification.md", status="pending")

    if rank_at_least(state, "merged"):
        for key in ("branch", "pull_request_url", "merge_commit"):
            result.require(nonempty(delivery.get(key)), f"delivery.{key} is required after merge")
        result.require(delivery.get("ci_status") == "passed", "delivery.ci_status must be passed after merge")
        result.require(data.get("release_status") in {"merged", "deployed"}, "release_status must reflect merged or deployed")

    if rank_at_least(state, "deployed"):
        result.require(data.get("release_status") == "deployed", "release_status must be deployed")
        for key in ("deployed_revision", "version", "rollback_ref"):
            result.require(nonempty(delivery.get(key)), f"delivery.{key} is required after deployment")

    if state == "deployed":
        validate_next_action(data, result, action="original_bug_production_verification", owner="testing-layer-runtime", target="03-release-verification.md", status="pending")

    if rank_at_least(state, "original_bug_production_verified"):
        result.require(data.get("original_bug_status") == "production_verified", "original_bug_status must be production_verified")

    if state in {"original_bug_production_verified", "awaiting_similar_defect_verification"}:
        validate_next_action(data, result, action="post_release_similar_defect_verification", owner="testing-layer-runtime", target="04-similar-bug-review.md", status="pending")

    similar = mapping(data.get("similar_defect_review"))
    if state == "awaiting_similar_defect_verification":
        result.require(similar.get("status") == "not_started", "similar review must be not_started while awaiting")
    if state == "similar_defect_verifying":
        result.require(similar.get("status") == "in_progress", "similar review must be in_progress")
        validate_next_action(data, result, action="post_release_similar_defect_verification", owner="testing-layer-runtime", target="04-similar-bug-review.md", status="in_progress")
    if rank_at_least(state, "similar_defect_reviewed"):
        result.require(similar.get("status") == "reviewed", "similar review must be reviewed before closure")

    if state == "similar_defect_reviewed":
        validate_next_action(data, result, action="close_bugfix_case", owner="testing-layer-runtime", target="04-similar-bug-review.md", status="pending")
    if state == "closed":
        result.require(data.get("next_required_action") is None, "closed Case must not have a next_required_action")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_directory", type=Path)
    parser.add_argument("--expect-state", choices=STATES)
    args = parser.parse_args()
    result = validate_case(args.case_directory.resolve(), args.expect_state)
    if result.errors:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Bugfix Case valid: {args.case_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

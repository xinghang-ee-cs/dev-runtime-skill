#!/usr/bin/env python3
"""Validate the database and persistence decision contract in planning document 09."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


CONTRACT_START = re.compile(r"(?m)^\s*database_persistence_contract:\s*$")
SCALAR_PATTERN = r"(?m)^\s*{key}:\s*([^#\n]+?)\s*$"
PLACEHOLDER_PATTERN = re.compile(
    r"<[^>\n]+>|\b(?:TODO|TBD|UNKNOWN)\b|待补|待确认", re.IGNORECASE
)
CREDENTIAL_PATTERN = re.compile(
    r"(?i)(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?):\/\/[^\s:@]+:[^\s@]+@"
    r"|(?:password|passwd|pwd|token|secret|private_key)\s*[:=]\s*(?!<|\[|\{|not_applicable\b|none\b)[^\s#]+"
)


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_text(path: Path, result: ValidationResult) -> str:
    if not path.is_file():
        result.errors.append(f"file does not exist: {path}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        result.errors.append(f"file is not UTF-8: {path}")
        return ""


def extract_contract(text: str) -> str:
    start = CONTRACT_START.search(text)
    if not start:
        return ""
    fenced_end = re.search(r"(?m)^```\s*$", text[start.end() :])
    if fenced_end:
        return text[start.start() : start.end() + fenced_end.start()]
    heading_end = re.search(r"(?m)^#{1,3}\s+", text[start.end() :])
    if heading_end:
        return text[start.start() : start.end() + heading_end.start()]
    return text[start.start() :]


def scalar(block: str, key: str) -> str:
    match = re.search(SCALAR_PATTERN.format(key=re.escape(key)), block)
    return match.group(1).strip().strip("'\"") if match else ""


def has_key(block: str, key: str) -> bool:
    return re.search(rf"(?m)^\s*{re.escape(key)}:\s*", block) is not None


def list_has_item(block: str, key: str) -> bool:
    match = re.search(
        rf"(?ms)^\s*{re.escape(key)}:\s*(?:\[\s*\]|$)(.*?)(?=^\s*[a-z_]+:\s*|\Z)",
        block,
    )
    if not match:
        inline = scalar(block, key)
        return bool(inline and inline not in {"[]", "none", "not_applicable"})
    return re.search(r"(?m)^\s*-\s*\S+", match.group(1)) is not None


def validate_contract(path: Path, allow_blocked: bool) -> ValidationResult:
    result = ValidationResult()
    text = read_text(path, result)
    if not text:
        return result

    block = extract_contract(text)
    result.require(bool(block), "missing database_persistence_contract block")
    if not block:
        return result

    required_fields = [
        "contract_version",
        "applicable",
        "decision_status",
        "decision_source",
        "current_baseline",
        "evidence_status",
        "existing_database",
        "engine_and_version",
        "location_mode",
        "evidence_refs",
        "reuse_decision",
        "target_engine_and_version",
        "environment_topology",
        "local_development",
        "test",
        "staging",
        "production",
        "remote_database",
        "availability",
        "purpose",
        "owner_or_provider",
        "provision_or_access_evidence",
        "existing_assets",
        "schema_or_migrations",
        "sanitized_data_or_backup",
        "access_mode",
        "migration",
        "required",
        "source_and_scope",
        "compatibility_strategy",
        "rollback_boundary",
        "data_governance",
        "environment_isolation",
        "backup_restore",
        "retention_deletion",
        "sensitive_data",
        "credential_boundary",
        "blocking_items",
        "delegation_boundary",
        "verification_requirements",
    ]
    for key in required_fields:
        result.require(has_key(block, key), f"missing field '{key}'")

    result.require(
        scalar(block, "contract_version") == "database-persistence/v1",
        "contract_version must be database-persistence/v1",
    )
    applicable = scalar(block, "applicable").lower()
    result.require(applicable in {"true", "false"}, "applicable must be true or false")

    status = scalar(block, "decision_status")
    allowed_statuses = {"confirmed", "explicitly_delegated", "not_applicable"}
    if allow_blocked:
        allowed_statuses.add("blocking_open")
    result.require(
        status in allowed_statuses,
        "decision_status is not ready; use --allow-blocked only for a blocked draft",
    )

    if applicable == "false":
        result.require(
            status == "not_applicable",
            "applicable: false requires decision_status: not_applicable",
        )
    if applicable == "true":
        result.require(
            status != "not_applicable",
            "applicable: true may not use decision_status: not_applicable",
        )

    if status == "blocking_open":
        result.require(
            list_has_item(block, "blocking_items"),
            "blocking_open requires at least one blocking_items entry",
        )

    delegation = scalar(block, "delegation_boundary")
    if status == "explicitly_delegated":
        result.require(
            bool(delegation)
            and delegation.lower() not in {"not_applicable", "none", "[]"}
            and not PLACEHOLDER_PATTERN.search(delegation),
            "explicitly_delegated requires a concrete delegation_boundary",
        )
        result.require(
            list_has_item(block, "verification_requirements"),
            "explicitly_delegated requires verification_requirements",
        )

    if status in {"confirmed", "explicitly_delegated"}:
        result.require(
            not PLACEHOLDER_PATTERN.search(block),
            f"{status} contract may not contain placeholders or pending markers",
        )

    result.require(
        CREDENTIAL_PATTERN.search(block) is None,
        "contract appears to contain a credential or credential-bearing connection string",
    )
    credential_boundary = scalar(block, "credential_boundary")
    result.require(bool(credential_boundary), "credential_boundary must be non-empty")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument(
        "--allow-blocked",
        action="store_true",
        help="allow decision_status: blocking_open during draft assembly",
    )
    args = parser.parse_args()
    result = validate_contract(args.document, args.allow_blocked)
    if result.errors:
        print("Database persistence contract validation failed:", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Database persistence contract validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Deterministically validate the Long local-runnable completion boundary."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from forward_state import advance_ledger, read_ledger, validate_ledger
from machine_execution_receipt import (
    RECEIPT_DIRECTORY as MACHINE_RECEIPT_DIRECTORY,
    load_receipt as load_machine_receipt,
    machine_spec_errors,
    normalized_machine_spec,
    resolve_project_root,
)


FENCE = re.compile(r"```(?:yaml|yml)?\s*\n(.*?)```", re.I | re.S)
PLACEHOLDER = re.compile(r"<[^>\n]+>|\b(?:TODO|TBD|unresolved)\b|待补|待确认", re.I)
EMPTY = {"", "null", "none", "[]", "{}"}
VALIDATION_TYPES = {
    "test",
    "build",
    "lint",
    "smoke",
    "openapi",
    "typecheck",
    "api-test",
    "playwright",
    "capability_real_call",
    "capability_binding",
    "execution_constraint_compliance",
    "frontend_contract_compliance",
}
VALIDATION_FOCUSES = {
    "unit",
    "business_rule",
    "contract",
    "user_flow",
    "state_transition",
    "permission_boundary",
    "capability_binding",
    "implementation_naming",
    "implementation_placement",
    "delegated_parameter_boundary",
    "dependency_governance",
    "ui_contract",
    "ux_contract",
    "responsive_behavior",
    "accessibility_behavior",
    "visual_asset_consistency",
    "artifact_readiness",
    "runtime_configuration",
    "dependency_readiness",
    "process_readiness",
    "schema_readiness",
}
EXECUTABLE_QUEUES = {"execute_only", "resume_only", "reexecute_affected_part"}
NON_EXECUTABLE_QUEUES = {"context_only", "completed_locked", "cancelled"}
ALL_QUEUES = EXECUTABLE_QUEUES | NON_EXECUTABLE_QUEUES
TASK_REVISION = re.compile(r"^TASK-[A-Z0-9-]+@[^\s@]+$", re.I)
TEST_ID = re.compile(r"(?m)^###\s+(TEST-[A-Z0-9-]+)(?:：|:|\s|$)", re.I)
TEST_HEADING = re.compile(r"(?m)^###\s+(TEST-[A-Z0-9-]+)(?:：|:|\s|$).*$", re.I)
AUTOMATION_LEVEL = re.compile(
    r"(?mi)^\s*(?:-\s*)?自动化等级\s*[：:]\s*"
    r"(mandatory_automated|automated_preferred|manual_or_real_environment_required)\b"
)
SENSITIVE_SOURCE_PARTS = {
    ".env",
    "credentials",
    "credential",
    "secrets",
    "secret",
    "private-key",
    "private_key",
}
SOURCE_TREE_EXCLUDES = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "__pycache__",
}
LONG_WORKFLOW = "long-task-orchestrator"
LONG_INITIAL_EDGES = {
    ("not_started", "preflight"),
    ("preflight", "execution"),
    ("execution", "completion_validation"),
    ("completion_validation", "ready_for_local_test"),
}
LONG_PATCH_EDGES = {
    ("patch_execution", "patch_validation"),
    ("patch_validation", "ready_for_local_retest"),
}
READINESS_RECEIPT = "long-readiness-receipt.json"
READINESS_RECEIPT_SCHEMA = "long-readiness-receipt/v2"


@dataclass
class Result:
    errors: list[str] = field(default_factory=list)

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


@dataclass(frozen=True)
class Token:
    indent: int
    content: str
    line: int


class ParseError(ValueError):
    pass


def strip_comment(value: str) -> str:
    quote: str | None = None
    for index, character in enumerate(value):
        if character in {"'", '"'}:
            quote = None if quote == character else character if quote is None else quote
        if character == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.rstrip()


def scalar(value: str) -> Any:
    value = strip_comment(value).strip()
    if not value:
        return None
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        return [scalar(part) for part in body.split(",") if part.strip()]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.lower() in {"null", "none", "~"}:
        return None
    if value[:1] in {"'", '"'} and value[-1:] == value[:1]:
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value[1:-1]
    return value


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    for line_number, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise ParseError(f"line {line_number}: tabs are not allowed for indentation")
        content = strip_comment(raw.lstrip())
        if not content:
            continue
        tokens.append(Token(len(raw) - len(raw.lstrip()), content, line_number))
    return tokens


def split_mapping(token: Token, content: str | None = None) -> tuple[str, str]:
    body = token.content if content is None else content
    if ":" not in body:
        raise ParseError(f"line {token.line}: expected mapping entry")
    key, value = body.split(":", 1)
    key = key.strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", key):
        raise ParseError(f"line {token.line}: invalid mapping key {key!r}")
    return key, value.strip()


def add_mapping(target: dict[str, Any], key: str, value: Any, line: int) -> None:
    if key in target:
        raise ParseError(f"line {line}: duplicate mapping key {key!r}")
    target[key] = value


def parse_node(tokens: list[Token], index: int, indent: int) -> tuple[Any, int]:
    if tokens[index].indent != indent:
        raise ParseError(f"line {tokens[index].line}: unexpected indentation")
    if tokens[index].content.startswith("-"):
        return parse_list(tokens, index, indent)
    return parse_mapping(tokens, index, indent)


def parse_mapping(
    tokens: list[Token], index: int, indent: int, initial: dict[str, Any] | None = None
) -> tuple[dict[str, Any], int]:
    result = {} if initial is None else initial
    while index < len(tokens) and tokens[index].indent == indent:
        token = tokens[index]
        if token.content.startswith("-"):
            break
        key, raw_value = split_mapping(token)
        index += 1
        if raw_value:
            value = scalar(raw_value)
        elif index < len(tokens) and tokens[index].indent > indent:
            value, index = parse_node(tokens, index, tokens[index].indent)
        else:
            value = None
        add_mapping(result, key, value, token.line)
    return result, index


def parse_list(tokens: list[Token], index: int, indent: int) -> tuple[list[Any], int]:
    result: list[Any] = []
    while index < len(tokens) and tokens[index].indent == indent:
        token = tokens[index]
        if not token.content.startswith("-"):
            break
        body = token.content[1:].strip()
        index += 1
        if not body:
            if index >= len(tokens) or tokens[index].indent <= indent:
                result.append(None)
            else:
                value, index = parse_node(tokens, index, tokens[index].indent)
                result.append(value)
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:(?:\s|$)", body) is None:
            result.append(scalar(body))
            continue

        item: dict[str, Any] = {}
        key_indent = indent + 2
        key, raw_value = split_mapping(token, body)
        if raw_value:
            value = scalar(raw_value)
        elif index < len(tokens) and tokens[index].indent > key_indent:
            value, index = parse_node(tokens, index, tokens[index].indent)
        else:
            value = None
        add_mapping(item, key, value, token.line)
        if index < len(tokens) and tokens[index].indent == key_indent:
            item, index = parse_mapping(tokens, index, key_indent, item)
        result.append(item)
    return result, index


def parse_document(text: str) -> dict[str, Any]:
    tokens = tokenize(text)
    if not tokens:
        return {}
    value, index = parse_node(tokens, 0, tokens[0].indent)
    if index != len(tokens):
        token = tokens[index]
        raise ParseError(f"line {token.line}: unparsed or inconsistent indentation")
    if not isinstance(value, dict):
        raise ParseError("document root must be a mapping")
    return value


def candidate_blocks(text: str) -> list[str]:
    blocks = FENCE.findall(text)
    return blocks if blocks else [text]


def load_anchored(path: Path, anchors: tuple[str, ...], result: Result) -> dict[str, Any]:
    if not path.is_file():
        result.errors.append(f"missing file: {path}")
        return {}
    text = path.read_text(encoding="utf-8")
    candidates = [block for block in candidate_blocks(text) if all(re.search(rf"(?m)^\s*{re.escape(anchor)}\s*:", block) for anchor in anchors)]
    if len(candidates) != 1:
        result.errors.append(f"{path.name}: expected exactly one document containing {', '.join(anchors)}")
        return {}
    try:
        return parse_document(candidates[0])
    except ParseError as error:
        result.errors.append(f"{path.name}: {error}")
        return {}


def load_validation_entries(path: Path, result: Result) -> list[dict[str, Any]]:
    if not path.is_file():
        result.errors.append(f"missing file: {path}")
        return []
    text = path.read_text(encoding="utf-8")
    records: list[dict[str, Any]] = []
    for block in candidate_blocks(text):
        if not re.search(r"(?m)^\s*(?:-\s*)?validation_id\s*:", block):
            continue
        try:
            document = parse_document(block)
        except ParseError as error:
            result.errors.append(f"{path.name}: {error}")
            continue
        if "validation_id" in document:
            records.append(document)
        elif isinstance(document.get("validations"), list):
            records.extend(item for item in document["validations"] if isinstance(item, dict))
    if not records:
        result.errors.append(f"{path.name}: no validation entries found")
    return records


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip().strip("'\"")


def concrete(value: Any) -> bool:
    text = clean(value)
    return text.lower() not in EMPTY and PLACEHOLDER.search(text) is None


def string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [clean(item) for item in value if concrete(item)]
    return [clean(value)] if concrete(value) else []


def without_fragment(reference: Any) -> str:
    return clean(reference).split("#", 1)[0]


def candidate_paths(runtime: Path, reference: Any) -> set[Path]:
    text = without_fragment(reference)
    if not concrete(text):
        return set()
    path = Path(text.replace("\\", "/"))
    if path.is_absolute():
        return {path.resolve()}
    bases = [runtime, Path.cwd(), *runtime.parents]
    return {(base / path).resolve() for base in bases}


def raw_candidate_paths(runtime: Path, reference: Any) -> list[tuple[Path, Path]]:
    text = without_fragment(reference)
    if not concrete(text):
        return []
    path = Path(text.replace("\\", "/"))
    if path.is_absolute():
        return [(path, path.anchor and Path(path.anchor) or path.parent)]
    return [(base / path, base) for base in (runtime, Path.cwd(), *runtime.parents)]


def path_uses_symlink(path: Path, boundary: Path) -> bool:
    current = path
    boundary = boundary.absolute()
    while True:
        if current.is_symlink():
            return True
        if current.absolute() == boundary or current.parent == current:
            return False
        current = current.parent


def resolve_source_file(
    runtime: Path, reference: Any, label: str, result: Result
) -> Path | None:
    existing: set[Path] = set()
    symlinked = False
    for raw_path, boundary in raw_candidate_paths(runtime, reference):
        if raw_path.is_file():
            if path_uses_symlink(raw_path, boundary):
                symlinked = True
                continue
            existing.add(raw_path.resolve())
    if symlinked:
        result.errors.append(f"{label} may not traverse a symbolic link")
    if not existing:
        if not symlinked:
            result.errors.append(f"{label} does not resolve to an existing file")
        return None
    if len(existing) != 1:
        result.errors.append(f"{label} resolves ambiguously")
        return None
    return existing.pop()


def resolve_source_directory(
    runtime: Path, reference: Any, label: str, result: Result
) -> Path | None:
    existing: set[Path] = set()
    symlinked = False
    for raw_path, boundary in raw_candidate_paths(runtime, reference):
        if raw_path.is_dir():
            if path_uses_symlink(raw_path, boundary):
                symlinked = True
                continue
            existing.add(raw_path.resolve())
    if symlinked:
        result.errors.append(f"{label} may not traverse a symbolic link")
    if not existing:
        if not symlinked:
            result.errors.append(f"{label} does not resolve to an existing directory")
        return None
    if len(existing) != 1:
        result.errors.append(f"{label} resolves ambiguously")
        return None
    return existing.pop()


def require_nonempty_file(path: Path | None, label: str, result: Result) -> Path | None:
    if path is None:
        return None
    try:
        result.require(path.stat().st_size > 0, f"{label} resolves to an empty file")
    except OSError as error:
        result.errors.append(f"{label} cannot be inspected: {error}")
        return None
    return path


def source_is_sensitive(reference: str) -> bool:
    parts = {part.lower() for part in Path(reference.replace("\\", "/")).parts}
    name = Path(reference.replace("\\", "/")).name.lower()
    return bool(parts & SENSITIVE_SOURCE_PARTS) or name.startswith(".env") or name.endswith(
        (".pem", ".key", ".p12", ".pfx")
    )


def inventory_snapshot(
    runtime: Path, inventory_refs: list[str], result: Result
) -> tuple[set[str], str, dict[str, Path]]:
    records: list[dict[str, object]] = []
    unit_ids: list[str] = []
    expanded_sources: dict[str, Path] = {}
    expanded_paths: dict[Path, str] = {}
    for inventory_ref in inventory_refs:
        inventory_path = resolve_source_file(
            runtime, inventory_ref, f"delivery unit inventory ref {inventory_ref}", result
        )
        if inventory_path is None:
            continue
        document = load_anchored(inventory_path, ("delivery_unit_inventory",), result)
        inventory = document.get("delivery_unit_inventory")
        if not isinstance(inventory, dict):
            result.errors.append(f"{inventory_path.name}: delivery_unit_inventory must be a mapping")
            continue
        units = inventory.get("units")
        if not isinstance(units, list) or not units:
            result.errors.append(f"{inventory_path.name}: inventory units must not be empty")
            continue
        for unit in units:
            if not isinstance(unit, dict):
                result.errors.append(f"{inventory_path.name}: inventory unit must be a mapping")
                continue
            unit_id = clean(unit.get("unit_id"))
            source_refs = string_list(unit.get("source_refs"))
            source_roots = string_list(unit.get("source_roots"))
            result.require(concrete(unit_id), f"{inventory_path.name}: inventory unit_id must be concrete")
            result.require(bool(source_roots), f"{unit_id}: inventory source_roots must not be empty")
            unique(source_refs, f"{unit_id} inventory source_refs", result)
            unique(source_roots, f"{unit_id} inventory source_roots", result)
            unit_ids.append(unit_id)
            sources: list[dict[str, str]] = []
            expanded_refs: dict[str, Path] = {}
            for source_root in sorted(source_roots):
                result.require(
                    not source_is_sensitive(source_root),
                    f"{unit_id}: inventory source_root may not read a secret-bearing path: {source_root}",
                )
                root_path = resolve_source_directory(
                    runtime, source_root, f"{unit_id} source_root {source_root}", result
                )
                if root_path is None:
                    continue
                for source_path in sorted(root_path.rglob("*")):
                    relative = source_path.relative_to(root_path)
                    if any(part.lower() in SOURCE_TREE_EXCLUDES for part in relative.parts):
                        continue
                    expanded_ref = (Path(source_root.replace("\\", "/")) / relative).as_posix()
                    if source_path.is_symlink():
                        result.errors.append(f"{unit_id}: source tree may not contain a symbolic link: {expanded_ref}")
                        continue
                    if not source_path.is_file():
                        continue
                    if source_is_sensitive(expanded_ref):
                        result.errors.append(f"{unit_id}: source tree contains a secret-bearing path: {expanded_ref}")
                        continue
                    expanded_refs[expanded_ref] = source_path.resolve()
            for source_ref in sorted(source_refs):
                result.require(
                    not source_is_sensitive(source_ref),
                    f"{unit_id}: inventory source_ref may not read a secret-bearing path: {source_ref}",
                )
                source_path = require_nonempty_file(
                    resolve_source_file(runtime, source_ref, f"{unit_id} source_ref {source_ref}", result),
                    f"{unit_id} source_ref {source_ref}",
                    result,
                )
                if source_path is None:
                    continue
                expanded_refs[source_ref.replace("\\", "/")] = source_path.resolve()
            result.require(bool(expanded_refs), f"{unit_id}: inventory source roots contain no source files")
            for source_ref, source_path in sorted(expanded_refs.items()):
                sources.append(
                    {
                        "ref": source_ref,
                        "sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
                    }
                )
                previous = expanded_sources.get(source_ref)
                result.require(
                    previous is None or previous == source_path,
                    f"inventory source ref is ambiguous across delivery units: {source_ref}",
                )
                expanded_sources[source_ref] = source_path
                previous_ref = expanded_paths.get(source_path)
                result.require(
                    previous_ref is None or previous_ref == source_ref,
                    f"inventory source roots overlap for the same file: {previous_ref} and {source_ref}",
                )
                expanded_paths[source_path] = source_ref
            records.append({"unit_id": unit_id, "sources": sources})
    unique(unit_ids, "inventory unit ids", result)
    records.sort(key=lambda item: str(item["unit_id"]))
    payload = json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return set(unit_ids), "sha256:" + hashlib.sha256(payload).hexdigest(), expanded_sources


def resolve_evidence_ref(runtime: Path, reference: Any, label: str, result: Result) -> None:
    text = clean(reference)
    result.require(concrete(text), f"{label} must be concrete")
    if not concrete(text):
        return
    require_nonempty_file(resolve_source_file(runtime, text, label, result), label, result)


def runtime_file(
    runtime: Path,
    reference: Any,
    allowed_names: set[str],
    label: str,
    result: Result,
) -> Path:
    text = clean(reference)
    if not concrete(text):
        result.errors.append(f"context.{label} must be concrete")
        return runtime / sorted(allowed_names)[0]
    name = Path(without_fragment(text).replace("\\", "/")).name
    if name not in allowed_names:
        result.errors.append(
            f"context.{label} must identify one of: {', '.join(sorted(allowed_names))}"
        )
        return runtime / sorted(allowed_names)[0]
    expected = (runtime / name).resolve()
    reference_path = Path(without_fragment(text).replace("\\", "/"))
    if reference_path.name == str(reference_path):
        return expected
    if expected not in candidate_paths(runtime, text):
        result.errors.append(
            f"context.{label} must resolve exactly to {expected}"
        )
    return expected


def unique(values: list[str], label: str, result: Result) -> None:
    result.require(len(values) == len(set(values)), f"{label} must contain unique values")


def validate_context(context: dict[str, Any], expect_ready: bool, result: Result) -> None:
    result.require(concrete(context.get("runtime_epoch")), "context.runtime_epoch must be concrete")
    result.require(concrete(context.get("planning_handoff_source")), "context.planning_handoff_source must be concrete")
    result.require(concrete(context.get("planning_baseline_revision")), "context.planning_baseline_revision must be concrete")
    result.require(concrete(context.get("project_root_ref")), "context.project_root_ref must be concrete")
    result.require(context.get("execution_prerequisite_readiness_status") == "passed", "Planning execution prerequisites are not passed")
    if expect_ready:
        status = context.get("current_effective_status")
        result.require(status in {"ready_for_local_test", "ready_for_local_retest"}, "context is not in a ready-for-local-test state")
        timestamp_key = "ready_for_local_retest_since" if status == "ready_for_local_retest" else "ready_for_local_test_since"
        result.require(concrete(context.get(timestamp_key)), f"context.{timestamp_key} must be concrete")
        result.require(not string_list(context.get("open_blockers")), "context.open_blockers must be empty")


def role_paths(handoff: dict[str, Any]) -> dict[str, str]:
    records = handoff.get("handoff_role_mapping")
    if not isinstance(records, list):
        return {}
    return {
        clean(record.get("role")): clean(record.get("path"))
        for record in records
        if isinstance(record, dict) and concrete(record.get("role"))
    }


def planning_test_contracts(path: Path, result: Result) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    matches = list(TEST_HEADING.finditer(text))
    contracts: dict[str, str] = {}
    for index, match in enumerate(matches):
        test_id = match.group(1).upper()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.start() : end]
        automation = AUTOMATION_LEVEL.search(block)
        if automation is None:
            result.errors.append(f"{test_id}: Planning TEST automation level is missing or invalid")
            continue
        contracts[test_id] = automation.group(1).lower()
    result.require(bool(contracts), "Planning Test and Acceptance Plan contains no TEST contract")
    return contracts


def validate_queue_snapshot(
    planning: dict[str, Any], context: dict[str, Any], result: Result
) -> set[str]:
    planning_contract = planning.get("incremental_execution_contract")
    context_contract = context.get("incremental_execution_contract_snapshot")
    if not isinstance(planning_contract, dict):
        result.errors.append("Planning Handoff incremental_execution_contract is missing")
        planning_contract = {}
    if not isinstance(context_contract, dict):
        result.errors.append("context.incremental_execution_contract_snapshot is missing")
        context_contract = {}
    all_values: list[str] = []
    executable: set[str] = set()
    for queue in sorted(ALL_QUEUES):
        planned = string_list(planning_contract.get(queue))
        current = string_list(context_contract.get(queue))
        result.require(planned == current, f"context execution queue {queue} does not match Planning Handoff")
        result.require(all(TASK_REVISION.fullmatch(item) for item in planned), f"Planning queue {queue} contains an invalid TASK revision")
        all_values.extend(planned)
        if queue in EXECUTABLE_QUEUES:
            executable.update(planned)
    unique(all_values, "Planning execution queue TASK revisions", result)
    result.require(
        clean(planning_contract.get("planning_baseline_revision"))
        == clean(planning.get("planning_baseline_revision")),
        "Planning Handoff baseline revision is inconsistent inside incremental_execution_contract",
    )
    result.require(
        clean(planning_contract.get("active_change_revision"))
        == clean(planning.get("active_change_revision")),
        "Planning Handoff active change revision is inconsistent inside incremental_execution_contract",
    )
    return executable


def validate_planning_handoff(
    runtime: Path,
    planning_path: Path | None,
    planning: dict[str, Any],
    context: dict[str, Any],
    result: Result,
) -> tuple[set[str], dict[str, str], str | None]:
    result.require(planning.get("handoff_type") == "execution_ready", "Planning Handoff must be execution_ready")
    result.require(planning.get("requires_execution_handoff") is True, "Planning Handoff requires_execution_handoff must be true")
    result.require(
        planning.get("planning_baseline_revision") == context.get("planning_baseline_revision"),
        "Planning Handoff baseline revision does not match Long Context",
    )
    result.require(
        clean(planning.get("active_change_revision")) == clean(context.get("active_change_revision")),
        "Planning Handoff active change revision does not match Long Context",
    )
    readiness = planning.get("execution_prerequisite_readiness")
    if not isinstance(readiness, dict):
        result.errors.append("Planning Handoff execution_prerequisite_readiness is missing")
    else:
        result.require(readiness.get("before_long_status") == "passed", "Planning before_long_status is not passed")
        result.require(not string_list(readiness.get("unresolved_before_long")), "Planning unresolved_before_long must be empty")
        contract_refs = readiness.get("contract_refs")
        if not isinstance(contract_refs, dict):
            result.errors.append("Planning execution prerequisite contract_refs is missing")
            contract_refs = {}
        for key in ("architecture_and_database", "capabilities", "dependencies"):
            result.require(key in contract_refs, f"Planning prerequisite contract_refs.{key} is missing")
        architecture_refs = string_list(contract_refs.get("architecture_and_database"))
        result.require(bool(architecture_refs), "Planning prerequisite architecture/database contract refs must not be empty")
        all_contract_refs: list[str] = []
        for value in contract_refs.values():
            all_contract_refs.extend(string_list(value))
        unique(all_contract_refs, "Planning prerequisite contract refs", result)
        for reference in all_contract_refs:
            resolve_source_file(runtime, reference, f"Planning prerequisite contract ref {reference}", result)
        result.require("ready_evidence_refs" in readiness, "Planning prerequisite ready_evidence_refs is missing")
        ready_evidence_refs = string_list(readiness.get("ready_evidence_refs"))
        unique(ready_evidence_refs, "Planning prerequisite ready evidence refs", result)
        if string_list(contract_refs.get("dependencies")):
            result.require(bool(ready_evidence_refs), "Planning dependency contracts require ready evidence refs")
        for reference in ready_evidence_refs:
            resolve_evidence_ref(runtime, reference, f"Planning prerequisite ready evidence ref {reference}", result)
    executable = validate_queue_snapshot(planning, context, result)
    roles = role_paths(planning)
    required_roles = (
        "Requirement and Scope",
        "Development Landing Checklist",
        "Test and Acceptance Plan",
        "Acceptance and Retrospective Record",
    )
    for role in required_roles:
        role_ref = roles.get(role, "")
        result.require(concrete(role_ref), f"Planning Handoff role is missing: {role}")
        if role not in {"Test and Acceptance Plan", "Acceptance and Retrospective Record"}:
            resolve_source_file(runtime, role_ref, f"Planning {role}", result)
    test_path: Path | None = None
    test_contracts: dict[str, str] = {}
    if planning_path is not None:
        raw_test_path = roles.get("Test and Acceptance Plan", "")
        test_path = resolve_source_file(runtime, raw_test_path, "Planning Test and Acceptance Plan", result)
        if test_path is not None:
            test_contracts = planning_test_contracts(test_path, result)
    acceptance_ref = roles.get("Acceptance and Retrospective Record", "")
    acceptance_path = resolve_source_file(runtime, acceptance_ref, "Planning Acceptance and Retrospective Record", result)
    return executable, test_contracts, str(acceptance_path) if acceptance_path else None


def matrix_requirements(
    runtime: Path,
    baseline: dict[str, Any],
    planning_tests: dict[str, str],
    result: Result,
    *,
    require_materialized_delivery: bool = True,
    executable_task_revisions: set[str] | None = None,
) -> tuple[str, str, list[dict[str, Any]], set[str]]:
    matrix = baseline.get("required_validation_matrix")
    if not isinstance(matrix, dict):
        result.errors.append("baseline.required_validation_matrix is missing")
        return "", "", [], set()
    revision = clean(matrix.get("matrix_revision"))
    result.require(concrete(revision), "matrix_revision must be concrete")
    audit = matrix.get("completeness_audit")
    if not isinstance(audit, dict):
        result.errors.append("matrix.completeness_audit is missing")
        audit = {}
    repository_revision = clean(audit.get("repository_scan_revision"))
    inventory_refs = string_list(audit.get("delivery_unit_inventory_refs"))
    result.require(bool(inventory_refs), "completeness_audit.delivery_unit_inventory_refs must not be empty")
    inventory_unit_ids: set[str] = set()
    if require_materialized_delivery:
        result.require(concrete(repository_revision), "completeness_audit.repository_scan_revision must be concrete")
        inventory_unit_ids, computed_repository_revision, _ = inventory_snapshot(runtime, inventory_refs, result)
        result.require(
            repository_revision == computed_repository_revision,
            "repository_scan_revision does not match the machine-computed delivery inventory snapshot",
        )
        result.require(audit.get("result") == "passed", "completeness_audit.result must be passed")
        result.require(not string_list(audit.get("open_gaps")), "completeness_audit.open_gaps must be empty")
    else:
        result.require(
            audit.get("result") in {"pending", "passed", "blocked"},
            "execution entry requires completeness_audit.result to be pending, passed, or blocked",
        )

    units = matrix.get("delivery_units")
    if not isinstance(units, list):
        result.errors.append("matrix.delivery_units must be a list")
        units = []
    unit_ids = [clean(unit.get("unit_id")) for unit in units if isinstance(unit, dict)]
    result.require(bool(unit_ids) and all(unit_ids), "matrix delivery unit ids must be non-empty")
    unique(unit_ids, "matrix delivery unit ids", result)
    changed = string_list(audit.get("changed_or_required_delivery_unit_ids"))
    mapped = string_list(audit.get("mapped_delivery_unit_ids"))
    unique(changed, "changed_or_required_delivery_unit_ids", result)
    unique(mapped, "mapped_delivery_unit_ids", result)
    result.require(set(changed) == set(mapped) == set(unit_ids), "delivery-unit completeness collections do not match")
    if require_materialized_delivery:
        result.require(inventory_unit_ids == set(unit_ids), "delivery-unit inventory does not match Matrix unit ids")
    local_tests = string_list(audit.get("locally_automatable_planning_test_refs"))
    mapped_tests = string_list(audit.get("mapped_planning_test_refs"))
    unique(local_tests, "locally_automatable_planning_test_refs", result)
    unique(mapped_tests, "mapped_planning_test_refs", result)
    result.require(set(local_tests) == set(mapped_tests), "locally automatable Planning TEST collections do not match")
    manual_refs = set(string_list(audit.get("manual_or_real_environment_planning_test_refs")))
    planning_test_ids = set(planning_tests)
    if planning_test_ids:
        result.require(set(local_tests) | manual_refs == planning_test_ids, "Long Matrix does not classify every Planning TEST contract")
        result.require((set(local_tests) | manual_refs) <= planning_test_ids, "Long Matrix references an unknown Planning TEST contract")
        mandatory = {test_id for test_id, level in planning_tests.items() if level == "mandatory_automated"}
        manual_only = {
            test_id
            for test_id, level in planning_tests.items()
            if level == "manual_or_real_environment_required"
        }
        result.require(mandatory <= set(local_tests), "mandatory_automated Planning TEST was not kept in Long automation")
        result.require(not (mandatory & manual_refs), "mandatory_automated Planning TEST may not be deferred to manual testing")
        result.require(manual_only <= manual_refs, "manual/real-environment Planning TEST is missing from manual handoff")
        result.require(not (manual_only & set(local_tests)), "manual/real-environment Planning TEST may not be claimed as Long automation")

    required: list[dict[str, Any]] = []
    all_requirement_ids: list[str] = []
    required_planning_test_refs: list[str] = []
    for unit in units:
        if not isinstance(unit, dict):
            result.errors.append("matrix.delivery_units contains a non-mapping item")
            continue
        unit_id = clean(unit.get("unit_id"))
        requirements = unit.get("requirements")
        mode = clean(unit.get("local_execution_mode"))
        result.require(mode in {"runnable", "loadable", "migration_only", "not_applicable"}, f"{unit_id}: local_execution_mode is invalid")
        if not isinstance(requirements, list):
            result.errors.append(f"delivery unit {unit_id!r} has no requirements list")
            continue
        for requirement in requirements:
            if not isinstance(requirement, dict):
                result.errors.append(f"delivery unit {unit_id!r} contains a non-mapping requirement")
                continue
            requirement_id = clean(requirement.get("requirement_id"))
            all_requirement_ids.append(requirement_id)
            result.require(concrete(requirement_id), f"{unit_id}: requirement_id must be concrete")
            result.require(
                requirement.get("requirement_level")
                in {"required", "optional", "not_applicable"},
                f"{requirement_id}: requirement_level is invalid",
            )
            result.require(requirement.get("validation_type") in VALIDATION_TYPES, f"{requirement_id}: validation_type is invalid")
            result.require(requirement.get("validation_focus") in VALIDATION_FOCUSES, f"{requirement_id}: validation_focus is invalid")
            if requirement.get("requirement_level") == "not_applicable":
                result.require(concrete(requirement.get("not_applicable_reason")), f"{requirement_id}: not_applicable requires a reason")
            if requirement.get("requirement_level") != "required":
                continue
            requirement = dict(requirement)
            requirement["_unit_id"] = unit_id
            required.append(requirement)
            required_planning_test_refs.extend(
                string_list(requirement.get("planning_test_refs"))
            )
            if require_materialized_delivery:
                result.require(requirement.get("binding_status") == "existing", f"{requirement_id}: binding_status must be existing at completion")
            else:
                result.require(
                    requirement.get("binding_status") in {"planned_in_confirmed_task", "existing"},
                    f"{requirement_id}: binding_status must be planned_in_confirmed_task or existing before execution",
                )
                if requirement.get("binding_status") == "planned_in_confirmed_task":
                    planned_task_revision = clean(
                        requirement.get("planned_task_revision")
                    )
                    result.require(
                        TASK_REVISION.fullmatch(planned_task_revision) is not None,
                        f"{requirement_id}: planned binding requires planned_task_revision",
                    )
                    if executable_task_revisions is not None:
                        result.require(
                            planned_task_revision in executable_task_revisions,
                            f"{requirement_id}: planned_task_revision is not in the confirmed executable queue",
                        )
            result.require(concrete(requirement.get("command_or_probe")), f"{requirement_id}: command_or_probe must be concrete")
            result.require(bool(string_list(requirement.get("success_postconditions"))), f"{requirement_id}: success_postconditions must not be empty")
            result.require(concrete(requirement.get("safe_execution_boundary")), f"{requirement_id}: safe_execution_boundary must be concrete")
            result.errors.extend(machine_spec_errors(requirement))
        typed_requirements = [item for item in requirements if isinstance(item, dict)]
        represented_focuses = {clean(item.get("validation_focus")) for item in typed_requirements}
        required_focuses = {
            clean(item.get("validation_focus"))
            for item in typed_requirements
            if item.get("requirement_level") == "required"
        }
        for focus in {"artifact_readiness", "runtime_configuration", "dependency_readiness", "process_readiness"}:
            result.require(focus in represented_focuses, f"{unit_id}: applicability for {focus} is not declared")
        behavior_focuses = {"user_flow", "business_rule", "contract"}
        if mode == "runnable":
            result.require("process_readiness" in required_focuses, f"{unit_id}: runnable unit requires process_readiness")
            result.require(bool(required_focuses & behavior_focuses), f"{unit_id}: runnable unit requires a minimum behavior validation")
        elif mode == "loadable":
            result.require("artifact_readiness" in required_focuses, f"{unit_id}: loadable unit requires artifact_readiness")
            result.require(bool(required_focuses & behavior_focuses), f"{unit_id}: loadable unit requires a real consumption validation")
        elif mode == "migration_only":
            result.require("schema_readiness" in required_focuses, f"{unit_id}: migration-only unit requires schema_readiness")
        elif mode == "not_applicable":
            result.require(not required_focuses, f"{unit_id}: not_applicable unit may not contain required validations")
    result.require(bool(required), "matrix must contain at least one required requirement")
    unique(all_requirement_ids, "Matrix requirement ids", result)
    unique(required_planning_test_refs, "required requirement Planning TEST refs", result)
    result.require(
        set(required_planning_test_refs) == set(mapped_tests),
        "mapped Planning TEST refs do not match required Matrix requirement bindings",
    )
    handoff_refs = string_list(audit.get("handoff_manual_test_refs"))
    unique(handoff_refs, "handoff_manual_test_refs", result)
    result.require(set(handoff_refs) == manual_refs, "baseline manual Planning TEST collections do not match")
    return revision, repository_revision, required, manual_refs


def latest_required_results(entries: list[dict[str, Any]], required_ids: set[str], result: Result) -> dict[str, dict[str, Any]]:
    validation_ids = [clean(entry.get("validation_id")) for entry in entries]
    result.require(all(validation_ids), "all validation_id values must be concrete")
    unique(validation_ids, "validation ids", result)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        requirement_id = clean(entry.get("requirement_id"))
        if requirement_id in required_ids:
            grouped.setdefault(requirement_id, []).append(entry)
    latest: dict[str, dict[str, Any]] = {}
    for requirement_id, records in grouped.items():
        attempts: list[int] = []
        timestamps: list[datetime] = []
        for entry in records:
            try:
                attempt = int(entry.get("attempt"))
            except (TypeError, ValueError):
                attempt = -1
                result.errors.append(f"{requirement_id}: every validation result requires an integer attempt")
            result.require(attempt > 0, f"{requirement_id}: validation attempt must be positive")
            attempts.append(attempt)
            raw_time = clean(entry.get("time"))
            try:
                timestamp = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
                if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                    raise ValueError("timezone is required")
                timestamp = timestamp.astimezone(timezone.utc)
            except (TypeError, ValueError, OverflowError):
                timestamp = datetime.min.replace(tzinfo=timezone.utc)
                result.errors.append(
                    f"{requirement_id}: validation time must be timezone-aware ISO-8601"
                )
            timestamps.append(timestamp)
        unique([str(item) for item in attempts], f"{requirement_id} validation attempts", result)
        ordered = sorted(zip(attempts, timestamps), key=lambda item: item[0])
        result.require(all(ordered[index][1] <= ordered[index + 1][1] for index in range(len(ordered) - 1)), f"{requirement_id}: attempt order conflicts with validation timestamps")
        latest[requirement_id] = max(records, key=lambda item: int(item.get("attempt", -1)) if str(item.get("attempt", "")).isdigit() else -1)
    return latest


def validate_required_evidence(
    runtime: Path,
    runtime_epoch: str,
    revision: str,
    repository_revision: str,
    requirements: list[dict[str, Any]],
    entries: list[dict[str, Any]],
    result: Result,
) -> set[str]:
    required_by_id = {clean(item.get("requirement_id")): item for item in requirements}
    latest = latest_required_results(entries, set(required_by_id), result)
    effective_ids: set[str] = set()
    for requirement_id, requirement in required_by_id.items():
        entry = latest.get(requirement_id)
        if entry is None:
            result.errors.append(f"{requirement_id}: current validation result is missing")
            continue
        validation_id = clean(entry.get("validation_id"))
        effective_ids.add(validation_id)
        result.require(entry.get("result") == "passed", f"{requirement_id}: latest result must be passed")
        result.require(clean(entry.get("code_config_revision")) == repository_revision, f"{requirement_id}: code/config revision does not match the current repository scan")
        result.require(clean(entry.get("delivery_unit_id")) == requirement.get("_unit_id"), f"{requirement_id}: delivery_unit_id mismatch")
        result.require(entry.get("requirement_level") == "required", f"{requirement_id}: requirement_level mismatch")
        result.require(entry.get("validation_type") == requirement.get("validation_type"), f"{requirement_id}: validation_type mismatch")
        result.require(entry.get("validation_focus") == requirement.get("validation_focus"), f"{requirement_id}: validation_focus mismatch")
        commands = string_list(entry.get("command"))
        result.require(bool(commands) and all("not_run" not in command.lower() and "skipped" not in command.lower() for command in commands), f"{requirement_id}: executed command/probe is missing")
        entry_revision = clean(entry.get("matrix_revision"))
        if entry_revision == revision:
            result.require(entry.get("matrix_compatibility") == "current", f"{requirement_id}: current-revision result must declare matrix_compatibility: current")
        else:
            result.require(entry.get("matrix_compatibility") == "carried_forward_unchanged", f"{requirement_id}: stale matrix result lacks explicit carry-forward")
            compatibility_evidence = string_list(entry.get("compatibility_evidence"))
            result.require(bool(compatibility_evidence), f"{requirement_id}: carry-forward compatibility evidence is missing")
            for reference in compatibility_evidence:
                resolve_evidence_ref(runtime, reference, f"{requirement_id} compatibility evidence {reference}", result)
        expected = string_list(requirement.get("success_postconditions"))
        unique(expected, f"{requirement_id} Matrix success postconditions", result)
        actual_records = entry.get("postcondition_results")
        if not isinstance(actual_records, list):
            result.errors.append(f"{requirement_id}: postcondition_results must be a list")
            continue
        actual: list[str] = []
        for item in actual_records:
            if not isinstance(item, dict):
                result.errors.append(f"{requirement_id}: invalid postcondition result")
                continue
            actual.append(clean(item.get("postcondition")))
            result.require(item.get("result") == "passed", f"{requirement_id}: every postcondition must pass")
            result.require(concrete(item.get("evidence")), f"{requirement_id}: every postcondition requires evidence")
            if concrete(item.get("evidence")):
                resolve_evidence_ref(
                    runtime,
                    item.get("evidence"),
                    f"{requirement_id} postcondition evidence {clean(item.get('evidence'))}",
                    result,
                )
        unique(actual, f"{requirement_id} postconditions", result)
        result.require(set(actual) == set(expected), f"{requirement_id}: postcondition coverage does not match the Matrix")
        evidence_refs = string_list(entry.get("evidence"))
        result.require(bool(evidence_refs), f"{requirement_id}: validation evidence is missing")
        for reference in evidence_refs:
            resolve_evidence_ref(runtime, reference, f"{requirement_id} validation evidence {reference}", result)
        validate_machine_execution_receipt(
            runtime,
            runtime_epoch,
            requirement,
            entry,
            repository_revision,
            actual_records,
            evidence_refs,
            result,
        )
    return effective_ids


def validate_machine_execution_receipt(
    runtime: Path,
    runtime_epoch: str,
    requirement: dict[str, Any],
    entry: dict[str, Any],
    repository_revision: str,
    entry_postconditions: list[dict[str, Any]],
    entry_evidence_refs: list[str],
    result: Result,
) -> None:
    requirement_id = clean(requirement.get("requirement_id"))
    receipt_ref = clean(entry.get("execution_receipt_ref"))
    result.require(
        concrete(receipt_ref),
        f"{requirement_id}: execution_receipt_ref is required",
    )
    if not concrete(receipt_ref):
        return
    relative = Path(receipt_ref.replace("\\", "/"))
    result.require(
        not relative.is_absolute()
        and len(relative.parts) == 2
        and relative.parts[0] == MACHINE_RECEIPT_DIRECTORY
        and relative.suffix == ".json",
        f"{requirement_id}: execution_receipt_ref must be a JSON file under {MACHINE_RECEIPT_DIRECTORY}/",
    )
    raw_receipt_path = runtime / relative
    receipt_path = raw_receipt_path.resolve()
    try:
        receipt_path.relative_to(runtime)
    except ValueError:
        result.errors.append(f"{requirement_id}: execution receipt escapes the Phase Runtime Directory")
        return
    if path_uses_symlink(raw_receipt_path, runtime) or not receipt_path.is_file():
        result.errors.append(f"{requirement_id}: machine execution receipt is missing or symbolic")
        return
    receipt, receipt_errors = load_machine_receipt(receipt_path)
    result.errors.extend(f"{requirement_id}: {error}" for error in receipt_errors)
    if receipt is None:
        return
    result.require(receipt.get("runtime_epoch") == runtime_epoch, f"{requirement_id}: execution receipt runtime_epoch mismatch")
    result.require(receipt.get("matrix_revision") == clean(entry.get("matrix_revision")), f"{requirement_id}: execution receipt matrix_revision mismatch")
    result.require(receipt.get("repository_revision") == repository_revision, f"{requirement_id}: execution receipt repository_revision mismatch")
    result.require(receipt.get("requirement_id") == requirement_id, f"{requirement_id}: execution receipt requirement_id mismatch")
    result.require(receipt.get("delivery_unit_id") == requirement.get("_unit_id"), f"{requirement_id}: execution receipt delivery_unit_id mismatch")
    result.require(receipt.get("validation_id") == clean(entry.get("validation_id")), f"{requirement_id}: execution receipt validation_id mismatch")
    try:
        entry_attempt = int(entry.get("attempt"))
    except (TypeError, ValueError):
        entry_attempt = -1
    result.require(receipt.get("attempt") == entry_attempt, f"{requirement_id}: execution receipt attempt mismatch")
    result.require(receipt.get("safe_execution_boundary") == requirement.get("safe_execution_boundary"), f"{requirement_id}: execution receipt safety boundary mismatch")
    try:
        expected_spec = normalized_machine_spec(requirement)
    except ValueError as error:
        result.errors.append(f"{requirement_id}: {error}")
        return
    result.require(receipt.get("machine_execution") == expected_spec, f"{requirement_id}: execution receipt machine specification mismatch")
    result.require(receipt.get("result") == "passed", f"{requirement_id}: machine execution receipt must be passed")
    try:
        generated_at = datetime.fromisoformat(
            clean(receipt.get("generated_at")).replace("Z", "+00:00")
        )
        if generated_at.tzinfo is None or generated_at.utcoffset() is None:
            raise ValueError("timezone is required")
    except (TypeError, ValueError, OverflowError):
        result.errors.append(f"{requirement_id}: execution receipt generated_at is invalid")
    receipt_records = receipt.get("postcondition_results")
    if not isinstance(receipt_records, list):
        result.errors.append(f"{requirement_id}: execution receipt postcondition_results must be a list")
        return
    expected_probes = {
        clean(item.get("postcondition")): item
        for item in expected_spec["postcondition_probes"]
        if isinstance(item, dict)
    }
    receipt_by_postcondition = {
        clean(item.get("postcondition")): item
        for item in receipt_records
        if isinstance(item, dict)
    }
    result.require(
        len(receipt_by_postcondition) == len(receipt_records)
        and set(receipt_by_postcondition) == set(expected_probes),
        f"{requirement_id}: execution receipt postconditions do not match the machine specification",
    )
    digest_pattern = re.compile(r"^sha256:[0-9a-f]{64}$")
    for postcondition, probe in expected_probes.items():
        record = receipt_by_postcondition.get(postcondition, {})
        result.require(record.get("probe_kind") == probe.get("probe_kind"), f"{requirement_id}: {postcondition} probe kind mismatch")
        result.require(record.get("result") == "passed", f"{requirement_id}: {postcondition} machine probe must pass")
        if probe.get("probe_kind") == "argv":
            result.require(record.get("exit_code") == 0, f"{requirement_id}: {postcondition} command exit code must be zero")
            result.require(bool(digest_pattern.fullmatch(clean(record.get("stdout_sha256")))), f"{requirement_id}: {postcondition} stdout digest is invalid")
            result.require(bool(digest_pattern.fullmatch(clean(record.get("stderr_sha256")))), f"{requirement_id}: {postcondition} stderr digest is invalid")
            result.require(isinstance(record.get("stdout_bytes"), int) and record.get("stdout_bytes", -1) >= 0, f"{requirement_id}: {postcondition} stdout_bytes is invalid")
            result.require(isinstance(record.get("stderr_bytes"), int) and record.get("stderr_bytes", -1) >= 0, f"{requirement_id}: {postcondition} stderr_bytes is invalid")
            result.require(record.get("process_tree_cleanup") == "not_required", f"{requirement_id}: {postcondition} successful command must not require forced process cleanup")
            result.require(record.get("error_kind") is None, f"{requirement_id}: {postcondition} command contains an execution error")
            for timestamp_field in ("started_at", "completed_at"):
                try:
                    timestamp = datetime.fromisoformat(
                        clean(record.get(timestamp_field)).replace("Z", "+00:00")
                    )
                    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                        raise ValueError("timezone is required")
                except (TypeError, ValueError, OverflowError):
                    result.errors.append(
                        f"{requirement_id}: {postcondition} {timestamp_field} is invalid"
                    )
            result.require(
                isinstance(record.get("duration_ms"), int)
                and record.get("duration_ms", -1) >= 0,
                f"{requirement_id}: {postcondition} duration_ms is invalid",
            )
        else:
            result.require(record.get("observed_exists") is True, f"{requirement_id}: {postcondition} required path was not observed")
            expected_type = probe.get("expected_type")
            observed_type = record.get("observed_type")
            result.require(expected_type == "any" or observed_type == expected_type, f"{requirement_id}: {postcondition} observed path type mismatch")
            if probe.get("nonempty") and expected_type == "file":
                result.require(isinstance(record.get("observed_size_bytes"), int) and record.get("observed_size_bytes", 0) > 0, f"{requirement_id}: {postcondition} required file is empty")
    result.require(
        receipt_ref in entry_evidence_refs,
        f"{requirement_id}: validation evidence must include execution_receipt_ref",
    )
    for item in entry_postconditions:
        if isinstance(item, dict):
            result.require(
                clean(item.get("evidence")) == receipt_ref,
                f"{requirement_id}: every passed postcondition must cite the machine execution receipt",
            )


def manual_handoff_refs(handoff: dict[str, Any], result: Result) -> set[str]:
    records = handoff.get("manual_required")
    if records in (None, []):
        return set()
    if not isinstance(records, list):
        result.errors.append("handoff.manual_required must be a list")
        return set()
    refs: list[str] = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            result.errors.append(f"handoff.manual_required item {index} must be a mapping")
            continue
        item_refs = string_list(record.get("planning_test_refs"))
        if not item_refs:
            result.require(clean(record.get("planning_test_refs")) == "not_applicable", f"handoff.manual_required item {index} must bind Planning TEST refs or declare not_applicable")
        refs.extend(item_refs)
    return set(refs)


def validate_handoff(
    runtime: Path,
    handoff: dict[str, Any],
    context: dict[str, Any],
    revision: str,
    effective_ids: set[str],
    expected_manual_refs: set[str],
    expected_executed_task_revisions: set[str],
    expected_acceptance_path: str | None,
    result: Result,
) -> None:
    result.require(handoff.get("runtime_epoch") == context.get("runtime_epoch"), "handoff.runtime_epoch does not match Long Runtime")
    result.require(handoff.get("planning_handoff_ref") == context.get("planning_handoff_source"), "handoff.planning_handoff_ref does not match Long Runtime")
    result.require(handoff.get("planning_baseline_revision") == context.get("planning_baseline_revision"), "handoff Planning baseline revision mismatch")
    context_change = clean(context.get("active_change_revision"))
    handoff_change = clean(handoff.get("active_change_revision"))
    result.require(context_change == handoff_change, "handoff active change revision mismatch")
    result.require(handoff.get("acceptance_status") == "not_started", "handoff.acceptance_status must be not_started")
    result.require(handoff.get("owner_runtime") == "testing-layer-runtime", "handoff.owner_runtime must be testing-layer-runtime")
    result.require(
        clean(handoff.get("validator_receipt_ref")) == READINESS_RECEIPT,
        f"handoff.validator_receipt_ref must be {READINESS_RECEIPT}",
    )
    result.require(concrete(handoff.get("formal_acceptance_record_path")), "handoff.formal_acceptance_record_path must be concrete")
    executed = set(string_list(handoff.get("executed_task_contract_revisions")))
    result.require(bool(executed), "handoff.executed_task_contract_revisions must not be empty")
    result.require(all(TASK_REVISION.fullmatch(item) for item in executed), "handoff contains an invalid executed TASK revision")
    result.require(executed == expected_executed_task_revisions, "handoff executed TASK revisions do not match Planning executable queues")
    if expected_acceptance_path is not None:
        handoff_acceptance = resolve_source_file(runtime, handoff.get("formal_acceptance_record_path"), "handoff.formal_acceptance_record_path", result)
        if handoff_acceptance is not None:
            result.require(handoff_acceptance == Path(expected_acceptance_path).resolve(), "handoff formal acceptance path does not match Planning Handoff")
    gate = handoff.get("required_validation_gate")
    if not isinstance(gate, dict):
        result.errors.append("handoff.required_validation_gate is missing")
    else:
        result.require(gate.get("result") == "passed", "handoff required validation gate is not passed")
        result.require(clean(gate.get("matrix_ref")).endswith("project-execution-baseline.md#required_validation_matrix"), "handoff matrix_ref must point to the canonical Matrix")
        result.require(gate.get("matrix_revision") == revision, "handoff matrix revision mismatch")
        result.require(set(string_list(gate.get("effective_validation_ids"))) == effective_ids, "handoff effective validation ids do not match current required evidence")
    automated = handoff.get("automated_passed")
    result.require(
        isinstance(automated, list)
        and all(isinstance(item, dict) for item in automated),
        "handoff.automated_passed must be a list of mappings",
    )
    automated_ids = [
        clean(item.get("id")) for item in automated if isinstance(item, dict)
    ] if isinstance(automated, list) else []
    result.require(all(automated_ids), "handoff automated_passed ids must be concrete")
    unique(automated_ids, "handoff automated_passed ids", result)
    source_id_list = [
        clean(item.get("source_validation_id"))
        for item in automated
        if isinstance(item, dict)
    ] if isinstance(automated, list) else []
    unique(source_id_list, "handoff automated_passed source_validation_ids", result)
    result.require(
        set(source_id_list) == effective_ids,
        "handoff automated_passed must expose exactly the effective required validations",
    )
    result.require(manual_handoff_refs(handoff, result) == expected_manual_refs, "handoff manual Planning TEST refs do not match completeness audit")


def long_transition_allowed(
    previous: dict[str, object] | None, event: dict[str, object]
) -> bool:
    cycle_kind = event.get("cycle_kind")
    edge = (str(event.get("from_stage")), str(event.get("to_stage")))
    if previous is None:
        return cycle_kind == "initial" and event.get("cycle") == 1 and edge == ("not_started", "preflight")
    previous_cycle = previous.get("cycle")
    cycle = event.get("cycle")
    if cycle == previous_cycle:
        if cycle_kind != previous.get("cycle_kind"):
            return False
        return edge in (LONG_INITIAL_EDGES if cycle_kind == "initial" else LONG_PATCH_EDGES)
    return (
        isinstance(previous_cycle, int)
        and cycle == previous_cycle + 1
        and cycle_kind == "patch"
        and previous.get("to_stage")
        in {
            "completion_validation",
            "patch_validation",
            "ready_for_local_test",
            "ready_for_local_retest",
        }
        and edge == (str(previous.get("to_stage")), "patch_execution")
    )


def validate_long_workflow(
    runtime: Path, context: dict[str, Any], expect_ready: bool, result: Result
) -> None:
    runtime_id = clean(context.get("runtime_epoch"))
    ledger = read_ledger(runtime)
    if ledger is None:
        result.errors.append("missing long-workflow-state.json; Long stages must advance through the state-machine script")
        return
    result.errors.extend(
        validate_ledger(
            ledger,
            workflow=LONG_WORKFLOW,
            runtime_id=runtime_id,
            transition_allowed=long_transition_allowed,
        )
    )
    if not isinstance(ledger, dict):
        return
    stage = clean(ledger.get("current_stage"))
    if expect_ready:
        expected = clean(context.get("current_effective_status"))
        result.require(stage == expected, "Long workflow stage does not match the ready Context status")
    else:
        result.require(
            stage in {
                "completion_validation",
                "ready_for_local_test",
                "patch_validation",
                "ready_for_local_retest",
            },
            "Long candidate validation requires the forward workflow to reach completion validation",
        )


def validate_runtime(
    runtime: Path, *, expect_ready: bool, require_workflow: bool = True
) -> tuple[Result, dict[str, Any], str, set[str]]:
    result = Result()
    context = load_anchored(runtime / "current-runtime-context.md", ("runtime_epoch", "current_effective_status"), result)
    baseline_path = runtime_file(runtime, context.get("project_execution_baseline_file"), {"project-execution-baseline.md"}, "project_execution_baseline_file", result)
    validation_path = runtime_file(runtime, context.get("validation_results_file"), {"validation-results.md"}, "validation_results_file", result)
    handoff_path = runtime_file(runtime, context.get("testing_handoff_file"), {"testing-handoff.md", "long-runtime-testing-summary.md"}, "testing_handoff_file", result)
    planning_path = resolve_source_file(runtime, context.get("planning_handoff_source"), "context.planning_handoff_source", result)
    planning = load_anchored(planning_path, ("handoff_type", "planning_baseline_revision"), result) if planning_path else {}
    baseline = load_anchored(baseline_path, ("required_validation_matrix",), result)
    entries = load_validation_entries(validation_path, result)
    handoff = load_anchored(handoff_path, ("runtime_epoch", "required_validation_gate"), result)

    validate_context(context, expect_ready, result)
    executable_revisions, planning_tests, acceptance_path = validate_planning_handoff(runtime, planning_path, planning, context, result)
    revision, repository_revision, requirements, manual_refs = matrix_requirements(runtime, baseline, planning_tests, result)
    try:
        resolve_project_root(runtime, context.get("project_root_ref"))
    except ValueError as error:
        result.errors.append(f"invalid project_root_ref: {error}")
    effective_ids = validate_required_evidence(
        runtime,
        clean(context.get("runtime_epoch")),
        revision,
        repository_revision,
        requirements,
        entries,
        result,
    )
    validate_handoff(runtime, handoff, context, revision, effective_ids, manual_refs, executable_revisions, acceptance_path, result)
    if require_workflow:
        validate_long_workflow(runtime, context, expect_ready, result)
    return result, context, repository_revision, effective_ids


def validate_stage_gate(runtime: Path, target: str) -> tuple[Result, dict[str, Any]]:
    if target in {"completion_validation", "patch_validation"}:
        result, context, _, _ = validate_runtime(runtime, expect_ready=False, require_workflow=False)
        return result, context
    if target in {"ready_for_local_test", "ready_for_local_retest"}:
        result, context, _, _ = validate_runtime(runtime, expect_ready=True, require_workflow=False)
        result.require(
            clean(context.get("current_effective_status")) == target,
            f"Context must be {target} before advancing the workflow ledger",
        )
        return result, context
    result = Result()
    context = load_anchored(runtime / "current-runtime-context.md", ("runtime_epoch", "current_effective_status"), result)
    planning_path = resolve_source_file(runtime, context.get("planning_handoff_source"), "context.planning_handoff_source", result)
    planning = load_anchored(planning_path, ("handoff_type", "planning_baseline_revision"), result) if planning_path else {}
    validate_context(context, False, result)
    try:
        resolve_project_root(runtime, context.get("project_root_ref"))
    except ValueError as error:
        result.errors.append(f"invalid project_root_ref: {error}")
    executable_revisions, planning_tests, _ = validate_planning_handoff(runtime, planning_path, planning, context, result)
    if target in {"execution", "patch_execution"}:
        baseline_path = runtime_file(
            runtime,
            context.get("project_execution_baseline_file"),
            {"project-execution-baseline.md"},
            "project_execution_baseline_file",
            result,
        )
        baseline = load_anchored(baseline_path, ("required_validation_matrix",), result)
        matrix_requirements(
            runtime,
            baseline,
            planning_tests,
            result,
            require_materialized_delivery=False,
            executable_task_revisions=executable_revisions,
        )
    return result, context


def print_errors(result: Result) -> int:
    if not result.errors:
        return 0
    for error in result.errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1


def readiness_receipt_payload(
    runtime: Path,
    context: dict[str, Any],
    repository_revision: str,
    effective_ids: set[str],
) -> dict[str, object]:
    artifacts: list[dict[str, str]] = []
    seen_paths: set[Path] = set()
    for path in sorted(runtime.rglob("*")):
        if path.is_symlink():
            raise ValueError(
                f"Runtime receipt may not follow a symlink: {path.relative_to(runtime).as_posix()}"
            )
        if not path.is_file() or path.name == READINESS_RECEIPT or path.name.endswith(".tmp"):
            continue
        relative_ref = path.relative_to(runtime).as_posix()
        if source_is_sensitive(relative_ref):
            raise ValueError(f"Runtime receipt may not hash a secret-bearing path: {relative_ref}")
        artifacts.append(
            {
                "kind": "runtime",
                "ref": relative_ref,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
        seen_paths.add(path.resolve())

    external_refs: set[str] = set()
    planning_ref = clean(context.get("planning_handoff_source"))
    if planning_ref:
        external_refs.add(planning_ref)
        planning_path = resolve_source_file(runtime, planning_ref, "receipt Planning Handoff", Result())
        if planning_path is not None:
            planning = load_anchored(
                planning_path, ("handoff_type", "planning_baseline_revision"), Result()
            )
            external_refs.update(role_paths(planning).values())
            readiness = planning.get("execution_prerequisite_readiness")
            if isinstance(readiness, dict):
                contract_refs = readiness.get("contract_refs")
                if isinstance(contract_refs, dict):
                    for value in contract_refs.values():
                        external_refs.update(string_list(value))
                external_refs.update(string_list(readiness.get("ready_evidence_refs")))
    ledger = read_ledger(runtime)
    history_digest = ledger.get("history_digest") if isinstance(ledger, dict) else None
    baseline = load_anchored(
        runtime / "project-execution-baseline.md", ("required_validation_matrix",), Result()
    )
    matrix = baseline.get("required_validation_matrix")
    matrix_revision = clean(matrix.get("matrix_revision")) if isinstance(matrix, dict) else ""
    if isinstance(matrix, dict):
        audit = matrix.get("completeness_audit")
        if isinstance(audit, dict):
            inventory_refs = string_list(audit.get("delivery_unit_inventory_refs"))
            external_refs.update(inventory_refs)
            inventory_result = Result()
            _, _, expanded_sources = inventory_snapshot(
                runtime, inventory_refs, inventory_result
            )
            if inventory_result.errors:
                raise ValueError("; ".join(inventory_result.errors))
            external_refs.update(expanded_sources)
    validation_result = Result()
    validation_entries = load_validation_entries(
        runtime / "validation-results.md", validation_result
    )
    if validation_result.errors:
        raise ValueError("; ".join(validation_result.errors))
    for entry in validation_entries:
        external_refs.update(string_list(entry.get("evidence")))
        external_refs.update(string_list(entry.get("compatibility_evidence")))
        postconditions = entry.get("postcondition_results")
        if isinstance(postconditions, list):
            for postcondition in postconditions:
                if isinstance(postcondition, dict):
                    external_refs.update(string_list(postcondition.get("evidence")))
    for reference in sorted(external_refs):
        if source_is_sensitive(reference):
            raise ValueError(
                f"Long readiness receipt may not hash a secret-bearing source: {reference}"
            )
        source_path = resolve_source_file(runtime, reference, f"receipt source {reference}", Result())
        if source_path is None or source_path.resolve() in seen_paths:
            continue
        artifacts.append(
            {
                "kind": "source",
                "ref": reference.replace("\\", "/"),
                "sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
            }
        )
        seen_paths.add(source_path.resolve())
    artifacts.sort(key=lambda item: (item["kind"], item["ref"]))
    return {
        "schema_version": READINESS_RECEIPT_SCHEMA,
        "runtime_epoch": clean(context.get("runtime_epoch")),
        "planning_baseline_revision": clean(context.get("planning_baseline_revision")),
        "active_change_revision": clean(context.get("active_change_revision")) or "not_applicable",
        "matrix_revision": matrix_revision,
        "repository_revision": repository_revision,
        "effective_validation_ids": sorted(effective_ids),
        "workflow_history_digest": history_digest,
        "artifacts": artifacts,
    }


def write_readiness_receipt(
    runtime: Path,
    context: dict[str, Any],
    repository_revision: str,
    effective_ids: set[str],
) -> Path:
    payload = readiness_receipt_payload(runtime, context, repository_revision, effective_ids)
    payload["receipt_digest"] = "sha256:" + hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    target = runtime / READINESS_RECEIPT
    handle, temporary_name = tempfile.mkstemp(
        prefix=f".{READINESS_RECEIPT}.", suffix=".tmp", dir=runtime
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, target)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
    return target


def validate_readiness_receipt(
    runtime: Path,
    context: dict[str, Any],
    repository_revision: str,
    effective_ids: set[str],
    result: Result,
) -> None:
    path = runtime / READINESS_RECEIPT
    if not path.is_file():
        result.errors.append(f"missing {READINESS_RECEIPT}; ready state has no deterministic receipt")
        return
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        result.errors.append(f"invalid {READINESS_RECEIPT}: {error}")
        return
    if not isinstance(receipt, dict):
        result.errors.append(f"invalid {READINESS_RECEIPT}: root must be an object")
        return
    declared_digest = receipt.get("receipt_digest")
    unsigned = {key: value for key, value in receipt.items() if key != "receipt_digest"}
    expected_digest = "sha256:" + hashlib.sha256(
        json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    result.require(declared_digest == expected_digest, "Long readiness receipt digest is invalid")
    result.require(receipt.get("schema_version") == READINESS_RECEIPT_SCHEMA, "Long readiness receipt schema is invalid")
    try:
        expected = readiness_receipt_payload(
            runtime, context, repository_revision, effective_ids
        )
    except (OSError, ValueError) as error:
        result.errors.append(f"Long readiness receipt cannot be reconstructed safely: {error}")
        return
    for field in (
        "runtime_epoch",
        "planning_baseline_revision",
        "active_change_revision",
        "matrix_revision",
        "repository_revision",
        "effective_validation_ids",
        "workflow_history_digest",
    ):
        result.require(
            receipt.get(field) == expected.get(field),
            f"Long readiness receipt {field} does not match the current validated state",
        )
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        result.errors.append("Long readiness receipt artifacts must not be empty")
        return
    for item in artifacts:
        if not isinstance(item, dict) or item.get("kind") not in {"runtime", "source"}:
            result.errors.append("Long readiness receipt contains an invalid artifact record")
            continue
        reference = clean(item.get("ref"))
        if item.get("kind") == "runtime":
            candidate = (runtime / reference).resolve()
            try:
                candidate.relative_to(runtime)
            except ValueError:
                result.errors.append(f"Long readiness receipt artifact escapes Runtime: {reference}")
                continue
        else:
            candidate = resolve_source_file(runtime, reference, f"Long readiness receipt source {reference}", result)
            if candidate is None:
                continue
        if not candidate.is_file():
            result.errors.append(f"Long readiness receipt artifact is missing: {reference}")
            continue
        result.require(
            item.get("sha256") == hashlib.sha256(candidate.read_bytes()).hexdigest(),
            f"Long readiness receipt artifact changed: {reference}",
        )
    result.require(
        artifacts == expected.get("artifacts"),
        "Long readiness receipt artifact inventory does not match the current validated state",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase_runtime_directory", type=Path)
    parser.add_argument("--expect-ready", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--print-repository-revision", action="store_true")
    parser.add_argument(
        "--advance-workflow",
        choices=(
            "preflight",
            "execution",
            "completion_validation",
            "ready_for_local_test",
            "patch_execution",
            "patch_validation",
            "ready_for_local_retest",
        ),
    )
    parser.add_argument("--cycle-kind", choices=("initial", "patch"), default="initial")
    parser.add_argument("--new-cycle", action="store_true")
    args = parser.parse_args()
    runtime = args.phase_runtime_directory.resolve()
    if args.print_repository_revision:
        result = Result()
        context = load_anchored(
            runtime / "current-runtime-context.md",
            ("runtime_epoch", "current_effective_status"),
            result,
        )
        baseline_path = runtime_file(
            runtime,
            context.get("project_execution_baseline_file"),
            {"project-execution-baseline.md"},
            "project_execution_baseline_file",
            result,
        )
        baseline = load_anchored(baseline_path, ("required_validation_matrix",), result)
        matrix = baseline.get("required_validation_matrix")
        audit = matrix.get("completeness_audit") if isinstance(matrix, dict) else None
        inventory_refs = string_list(audit.get("delivery_unit_inventory_refs")) if isinstance(audit, dict) else []
        result.require(bool(inventory_refs), "delivery_unit_inventory_refs must not be empty")
        _, revision, _ = inventory_snapshot(runtime, inventory_refs, result)
        if print_errors(result):
            return 1
        print(revision)
        return 0
    if args.advance_workflow:
        result, context = validate_stage_gate(runtime, args.advance_workflow)
        if print_errors(result):
            return 1
        try:
            ledger = advance_ledger(
                runtime,
                workflow=LONG_WORKFLOW,
                runtime_id=clean(context.get("runtime_epoch")),
                to_stage=args.advance_workflow,
                cycle_kind=args.cycle_kind,
                start_new_cycle=args.new_cycle,
                transition_allowed=long_transition_allowed,
            )
        except ValueError as error:
            print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(
            f"Long workflow advanced to {ledger['current_stage']} "
            f"(cycle {ledger['current_cycle']})."
        )
        return 0

    result, context, repository_revision, effective_ids = validate_runtime(
        runtime, expect_ready=args.expect_ready
    )
    if args.write_receipt:
        result.require(args.expect_ready, "--write-receipt requires --expect-ready")
        if print_errors(result):
            return 1
        try:
            receipt_path = write_readiness_receipt(
                runtime, context, repository_revision, effective_ids
            )
        except (OSError, ValueError) as error:
            print(f"ERROR: Long readiness receipt cannot be written safely: {error}", file=sys.stderr)
            return 1
        print(f"Long readiness receipt written: {receipt_path.name}")
        return 0
    if args.expect_ready:
        validate_readiness_receipt(
            runtime, context, repository_revision, effective_ids, result
        )

    if print_errors(result):
        return 1
    print("Long local-runnable readiness contract: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

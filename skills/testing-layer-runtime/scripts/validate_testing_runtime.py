#!/usr/bin/env python3
"""Validate Testing Runtime identity, deployment, and Release Handoff gates."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from forward_state import advance_ledger, read_ledger, validate_ledger


MAPPING_KEY = re.compile(r"^(\s*)([a-z_][a-z0-9_-]*):(?:\s*(.*))?$", re.I)
LIST_MAPPING_KEY = re.compile(
    r"^(\s*)-\s+([a-z_][a-z0-9_-]*):(?:\s*(.*))?$", re.I
)
LIST_SCALAR = re.compile(r"^(\s*)-\s+([^#\n]+?)\s*$")
FENCE = re.compile(r"```(?:yaml|yml)?\s*\n(.*?)```", re.I | re.S)
PLACEHOLDER = re.compile(r"<[^>\n]+>|\b(?:TODO|TBD)\b|待补|待确认", re.I)
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
EMPTY_VALUES = {"", "null", "none", "not_applicable", "[]", "{}"}
ITEM_TYPES = {
    "case",
    "manual_op",
    "real_device",
    "deployed_e2e",
    "server_verification",
    "environment_prerequisite",
}
PASS_STATUSES = {"reused_from_long", "verified", "verified_by_user_report"}
LOCAL_REVISION_KINDS = {"git_commit", "git_worktree_snapshot", "build_id", "workspace_snapshot"}
FLOW_HEADING = re.compile(r"(?m)^###\s+(FLOW-[A-Z0-9-]+)(?:：|:|\s|$).*$", re.I)
TEST_HEADING = re.compile(r"(?m)^###\s+(TEST-[A-Z0-9-]+)(?:：|:|\s|$).*$", re.I)
TASK_REVISION = re.compile(r"^TASK-[A-Z0-9-]+@[^\s@]+$", re.I)
TESTING_WORKFLOW = "testing-layer-runtime"
TESTING_INITIAL_EDGES = {
    ("not_started", "intake"),
    ("intake", "local_testing"),
    ("local_testing", "cloud_testing"),
    ("local_testing", "release_handoff"),
    ("cloud_testing", "release_handoff"),
}
TESTING_DEPLOYMENT_EDGES = {("cloud_testing", "release_handoff")}
TESTING_RETEST_EDGES = {
    ("local_testing", "cloud_testing"),
    ("local_testing", "release_handoff"),
    ("cloud_testing", "release_handoff"),
}
TESTING_PHASE_TO_STAGE = {
    "test_intake": "intake",
    "manual_testing": "local_testing",
    "local_testing": "local_testing",
    "server_testing": "cloud_testing",
    "cloud_testing": "cloud_testing",
    "release_handoff": "release_handoff",
}
LONG_RECEIPT_SCHEMA = "long-readiness-receipt/v2"
LONG_MACHINE_RECEIPT_SCHEMA = "long-machine-execution-receipt/v2"
LONG_MACHINE_RUNNER = "long-machine-runner/v2"
LONG_RECEIPT_REQUIRED_ARTIFACTS = {
    "project-execution-baseline.md",
    "validation-results.md",
    "testing-handoff.md",
    "long-workflow-state.json",
}
RELEASE_MUTABLE_FIELDS = {"snapshot_status", "invalidated_by", "invalidated_at"}


@dataclass
class Result:
    errors: list[str] = field(default_factory=list)

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


@dataclass(frozen=True)
class Entry:
    path: tuple[str, ...]
    value: str
    line: int


def read(path: Path, result: Result) -> str:
    if not path.is_file():
        result.errors.append(f"missing file: {path}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        result.errors.append(f"file is not UTF-8: {path}")
        return ""


def entries(text: str) -> list[Entry]:
    parsed: list[Entry] = []
    stack: list[tuple[int, str]] = []
    item_counts: collections.Counter[tuple[str, ...]] = collections.Counter()
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith(("#", "```")):
            continue
        list_match = LIST_MAPPING_KEY.match(raw_line)
        if list_match:
            indent = len(list_match.group(1))
            while stack and indent <= stack[-1][0]:
                stack.pop()
            parent = tuple(key for _, key in stack)
            item_index = item_counts[parent]
            item_counts[parent] += 1
            marker = f"[{item_index}]"
            stack.append((indent, marker))
            key = list_match.group(2)
            value = (list_match.group(3) or "").strip()
            parsed.append(Entry(parent + (marker, key), value, line_number))
            if not value:
                stack.append((indent + 1, key))
            continue
        scalar_match = LIST_SCALAR.match(raw_line)
        if scalar_match:
            indent = len(scalar_match.group(1))
            while stack and indent <= stack[-1][0]:
                stack.pop()
            parent = tuple(key for _, key in stack)
            item_index = item_counts[parent]
            item_counts[parent] += 1
            parsed.append(
                Entry(
                    parent + (f"[{item_index}]",),
                    scalar_match.group(2).strip(),
                    line_number,
                )
            )
            continue
        match = MAPPING_KEY.match(raw_line)
        if not match:
            continue
        indent = len(match.group(1))
        while stack and indent <= stack[-1][0]:
            stack.pop()
        key = match.group(2)
        value = (match.group(3) or "").strip()
        path = tuple(parent for _, parent in stack) + (key,)
        parsed.append(Entry(path, value, line_number))
        if not value:
            stack.append((indent, key))
    return parsed


def clean(value: str) -> str:
    return value.strip().strip("'\"")


def value_at(parsed: list[Entry], path: tuple[str, ...]) -> str:
    values = [entry.value for entry in parsed if entry.path == path]
    return clean(values[0]) if values else ""


def path_present(parsed: list[Entry], path: tuple[str, ...]) -> bool:
    return any(entry.path == path for entry in parsed)


def duplicate_paths(parsed: list[Entry]) -> list[tuple[tuple[str, ...], list[int]]]:
    grouped: dict[tuple[str, ...], list[int]] = collections.defaultdict(list)
    for entry in parsed:
        grouped[entry.path].append(entry.line)
    return [(path, lines) for path, lines in grouped.items() if len(lines) > 1]


def canonical_release_snapshot_digest(parsed: list[Entry]) -> str:
    frozen = [
        {"path": list(entry.path), "value": clean(entry.value)}
        for entry in parsed
        if entry.path
        and entry.path[0] not in RELEASE_MUTABLE_FIELDS | {"snapshot_digest"}
    ]
    frozen.sort(key=lambda item: (item["path"], item["value"]))
    payload = json.dumps(
        frozen, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def list_values(text: str, key: str) -> list[str]:
    match = re.search(rf"(?m)^(\s*){re.escape(key)}:\s*(.*?)\s*$", text)
    if not match:
        return []
    inline = clean(match.group(2))
    if inline.startswith("[") and inline.endswith("]"):
        body = inline[1:-1].strip()
        return [clean(part) for part in body.split(",") if part.strip()]
    base_indent = len(match.group(1))
    values: list[str] = []
    for line in text[match.end() :].splitlines():
        if line.strip() and len(line) - len(line.lstrip()) <= base_indent:
            break
        item = re.match(r"^\s*-\s*([^#\n]+?)\s*$", line)
        if item:
            values.append(clean(item.group(1)))
    return values


def list_at(parsed: list[Entry], path: tuple[str, ...]) -> list[str]:
    inline = value_at(parsed, path)
    if inline.startswith("[") and inline.endswith("]"):
        body = inline[1:-1].strip()
        return [clean(part) for part in body.split(",") if part.strip()]
    values = [
        clean(entry.value)
        for entry in parsed
        if len(entry.path) == len(path) + 1
        and entry.path[: len(path)] == path
        and entry.path[-1].startswith("[")
    ]
    return [value for value in values if value]


def text_blocks(text: str) -> list[str]:
    blocks = FENCE.findall(text)
    return blocks if blocks else [text]


def anchored_records(text: str, anchor: str) -> list[tuple[list[Entry], tuple[str, ...]]]:
    records: list[tuple[list[Entry], tuple[str, ...]]] = []
    for block in text_blocks(text):
        parsed = entries(block)
        if value_at(parsed, (anchor,)):
            records.append((parsed, ()))
        prefixes = {
            entry.path[:-1]
            for entry in parsed
            if entry.path[-1:] == (anchor,)
            and entry.path[:-1]
            and entry.path[-2].startswith("[")
        }
        records.extend((parsed, prefix) for prefix in sorted(prefixes))
    return records


def has_concrete(value: str) -> bool:
    return value.lower() not in EMPTY_VALUES and not PLACEHOLDER.search(value)


def component_records(parsed: list[Entry], prefix: tuple[str, ...]) -> list[dict[str, str]]:
    records: dict[str, dict[str, str]] = collections.defaultdict(dict)
    for entry in parsed:
        if len(entry.path) != len(prefix) + 2 or entry.path[: len(prefix)] != prefix:
            continue
        marker, key = entry.path[-2:]
        if marker.startswith("["):
            records[marker][key] = clean(entry.value)
    return [records[key] for key in sorted(records, key=lambda item: int(item[1:-1]))]


def record_prefixes(parsed: list[Entry], prefix: tuple[str, ...]) -> list[tuple[str, ...]]:
    return sorted(
        {
            entry.path[: len(prefix) + 1]
            for entry in parsed
            if len(entry.path) > len(prefix)
            and entry.path[: len(prefix)] == prefix
            and entry.path[len(prefix)].startswith("[")
        },
        key=lambda item: int(item[-1][1:-1]),
    )


def markdown_heading_blocks(text: str, pattern: re.Pattern[str]) -> dict[str, str]:
    matches = list(pattern.finditer(text))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks[match.group(1).upper()] = text[match.start() : end]
    return blocks


def contract_requirement(block: str, label: str) -> str:
    match = re.search(
        rf"(?mi)^\s*-?\s*{re.escape(label)}\s*[：:]\s*(required|not_applicable)\b",
        block,
    )
    return match.group(1).lower() if match else ""


def role_paths(parsed: list[Entry]) -> dict[str, str]:
    return {
        record.get("role", ""): record.get("path", "")
        for record in component_records(parsed, ("handoff_role_mapping",))
        if record.get("role")
    }


def planning_contracts(
    runtime_directory: Path, state_entries: list[Entry], result: Result
) -> dict[str, object]:
    intake = ("intake_binding",)
    planning_ref = value_at(state_entries, intake + ("planning_handoff_ref",))
    planning_path = resolve_source_ref(
        runtime_directory, planning_ref, "intake_binding.planning_handoff_ref", result
    )
    contracts: dict[str, object] = {
        "path": planning_path,
        "flows": {},
        "tests": {},
        "before_release_dependency_refs": set(),
        "executable_task_revisions": set(),
    }
    if planning_path is None:
        return contracts
    planning_text = read(planning_path, result)
    candidates = [
        block
        for block in text_blocks(planning_text)
        if re.search(r"(?m)^\s*handoff_type\s*:", block)
        and re.search(r"(?m)^\s*planning_baseline_revision\s*:", block)
    ]
    if len(candidates) != 1:
        result.errors.append("Planning Handoff must contain exactly one execution-ready document")
        return contracts
    planning = entries(candidates[0])
    result.require(value_at(planning, ("handoff_type",)) == "execution_ready", "Testing requires an execution_ready Planning Handoff")
    result.require(value_at(planning, ("requires_execution_handoff",)).lower() == "true", "Planning Handoff requires_execution_handoff must be true")
    result.require(
        value_at(planning, ("planning_baseline_revision",))
        == value_at(state_entries, intake + ("planning_baseline_revision",)),
        "Planning Handoff baseline revision does not match Testing intake",
    )
    result.require(
        value_at(planning, ("execution_prerequisite_readiness", "before_long_status")) == "passed"
        and not list_at(planning, ("execution_prerequisite_readiness", "unresolved_before_long")),
        "Planning execution prerequisites are not closed",
    )
    before_release = set(
        list_at(
            planning,
            ("execution_prerequisite_readiness", "before_release_dependency_refs"),
        )
    )
    contracts["before_release_dependency_refs"] = before_release
    executable: set[str] = set()
    forbidden: set[str] = set()
    for queue in ("execute_only", "resume_only", "reexecute_affected_part"):
        executable.update(list_at(planning, ("incremental_execution_contract", queue)))
    for queue in ("context_only", "completed_locked", "cancelled"):
        forbidden.update(list_at(planning, ("incremental_execution_contract", queue)))
    result.require(not (executable & forbidden), "Planning executable and non-executable TASK queues overlap")
    result.require(all(TASK_REVISION.fullmatch(item) for item in executable | forbidden), "Planning Handoff contains an invalid TASK contract revision")
    contracts["executable_task_revisions"] = executable

    roles = role_paths(planning)
    requirement_path = resolve_source_ref(
        runtime_directory,
        roles.get("Requirement and Scope", ""),
        "Planning Requirement and Scope",
        result,
    )
    test_plan_path = resolve_source_ref(
        runtime_directory,
        roles.get("Test and Acceptance Plan", ""),
        "Planning Test and Acceptance Plan",
        result,
    )
    if requirement_path is not None:
        flow_text = read(requirement_path, result)
        flows: dict[str, dict[str, object]] = {}
        for flow_ref, block in markdown_heading_blocks(flow_text, FLOW_HEADING).items():
            priority_match = re.search(r"(?mi)^\s*Priority\s*[：:]\s*(P[0-2])\b", block)
            tests = set(re.findall(r"\bTEST-[A-Z0-9-]+\b", block, re.I))
            flows[flow_ref] = {
                "priority": priority_match.group(1).upper() if priority_match else "",
                "test_refs": {item.upper() for item in tests},
            }
        result.require(bool(flows), "Planning Requirement and Scope contains no FLOW contract")
        result.require(all(item["priority"] in {"P0", "P1", "P2"} for item in flows.values()), "every Planning FLOW requires a priority")
        contracts["flows"] = flows
    if test_plan_path is not None:
        tests: dict[str, dict[str, object]] = {}
        for test_ref, block in markdown_heading_blocks(read(test_plan_path, result), TEST_HEADING).items():
            tests[test_ref] = {
                "flow_refs": {item.upper() for item in re.findall(r"\bFLOW-[A-Z0-9-]+\b", block, re.I)},
                "local_requirement": contract_requirement(block, "本地业务 / E2E"),
                "cloud_requirement": contract_requirement(block, "部署后云端业务 / E2E"),
            }
        result.require(bool(tests), "Planning Test and Acceptance Plan contains no TEST contract")
        contracts["tests"] = tests
    return contracts


def identity(parsed: list[Entry], prefix: tuple[str, ...]) -> dict[str, object]:
    config_prefix = prefix + ("runtime_configuration_identity",)
    components = component_records(parsed, prefix + ("component_revisions",))
    return {
        "status": value_at(parsed, prefix + ("status",)),
        "target_environment": value_at(parsed, prefix + ("target_environment",)),
        "identity_mode": value_at(parsed, prefix + ("identity_mode",)),
        "revision_kind": value_at(parsed, prefix + ("revision_kind",)),
        "revision": value_at(parsed, prefix + ("revision",)),
        "identity_digest": value_at(parsed, prefix + ("identity_digest",)),
        "evidence_ref": value_at(parsed, prefix + ("evidence_ref",)),
        "component_revisions": components,
        "runtime_configuration_identity": {
            "status": value_at(parsed, config_prefix + ("status",)),
            "revision_kind": value_at(parsed, config_prefix + ("revision_kind",)),
            "revision": value_at(parsed, config_prefix + ("revision",)),
            "evidence_ref": value_at(parsed, config_prefix + ("evidence_ref",)),
            "secret_values_included": value_at(
                parsed, config_prefix + ("secret_values_included",)
            ).lower(),
        },
    }


def computed_identity_digest(current: dict[str, object]) -> str:
    config = current["runtime_configuration_identity"]
    assert isinstance(config, dict)
    components = current["component_revisions"]
    assert isinstance(components, list)
    payload = {
        "target_environment": current["target_environment"],
        "identity_mode": current["identity_mode"],
        "revision_kind": current["revision_kind"],
        "revision": current["revision"],
        "component_revisions": sorted(
            [
                {
                    "component_id": item.get("component_id", ""),
                    "revision_kind": item.get("revision_kind", ""),
                    "revision": item.get("revision", ""),
                }
                for item in components
            ],
            key=lambda item: item["component_id"],
        ),
        "runtime_configuration_identity": {
            "status": config.get("status", ""),
            "revision_kind": config.get("revision_kind", ""),
            "revision": config.get("revision", ""),
        },
    }
    serialized = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(serialized).hexdigest()


def validate_identity(current: dict[str, object], label: str, result: Result) -> None:
    status = str(current["status"])
    mode = str(current["identity_mode"])
    kind = str(current["revision_kind"])
    components = current["component_revisions"]
    config = current["runtime_configuration_identity"]
    assert isinstance(components, list)
    assert isinstance(config, dict)

    result.require(status in {"known", "unknown", "not_applicable"}, f"{label}.status is invalid")
    result.require(
        config.get("secret_values_included") == "false",
        f"{label} must set secret_values_included: false",
    )
    if status == "known":
        for field_name in (
            "target_environment",
            "identity_mode",
            "revision_kind",
            "revision",
            "identity_digest",
            "evidence_ref",
        ):
            result.require(
                has_concrete(str(current[field_name])),
                f"{label}.{field_name} must be concrete when status is known",
            )
        result.require(DIGEST.fullmatch(str(current["identity_digest"])) is not None, f"{label}.identity_digest is invalid")
        result.require(
            str(current["identity_digest"]) == computed_identity_digest(current),
            f"{label}.identity_digest does not match the canonical non-secret identity",
        )
        allowed_mode_kind = {
            "single_revision": {"commit", "build", "image_digest"},
            "aggregate_deployment": {"deployment_id", "build"},
            "component_set": {"deployment_set_digest"},
        }
        result.require(mode in allowed_mode_kind, f"{label}.identity_mode is invalid")
        result.require(kind in allowed_mode_kind.get(mode, set()), f"{label} mode/kind combination is invalid")
        if mode == "component_set":
            result.require(bool(components), f"{label}.component_revisions must not be empty")
        else:
            result.require(not components, f"{label}.component_revisions must be empty for {mode}")
        component_ids = [item.get("component_id", "") for item in components]
        result.require(
            all(component_ids) and len(component_ids) == len(set(component_ids)),
            f"{label}.component_id values must be non-empty and unique",
        ) if components else None
        for index, item in enumerate(components, start=1):
            for field_name in ("component_id", "revision_kind", "revision", "evidence_ref"):
                result.require(
                    has_concrete(item.get(field_name, "")),
                    f"{label}.component_revisions item {index} missing {field_name}",
                )
        config_status = str(config.get("status", ""))
        result.require(config_status in {"known", "not_applicable"}, f"{label}.runtime_configuration_identity.status must be known or not_applicable")
        if config_status == "known":
            result.require(
                config.get("revision_kind")
                in {"platform_configuration_revision", "sanitized_manifest_digest"},
                f"{label}.runtime_configuration_identity.revision_kind is invalid",
            )
            for field_name in ("revision", "evidence_ref"):
                result.require(
                    has_concrete(str(config.get(field_name, ""))),
                    f"{label}.runtime_configuration_identity.{field_name} must be concrete",
                )
        else:
            result.require(
                config.get("revision_kind") == "not_applicable"
                and config.get("revision") == "not_applicable",
                f"{label}.runtime_configuration_identity not_applicable fields are inconsistent",
            )
    elif status == "not_applicable":
        for field_name in ("target_environment", "identity_mode", "revision_kind", "revision", "identity_digest", "evidence_ref"):
            result.require(
                current[field_name] == "not_applicable",
                f"{label}.{field_name} must be not_applicable",
            )
        result.require(not components, f"{label}.component_revisions must be empty")
        result.require(
            config.get("status") == "not_applicable",
            f"{label}.runtime_configuration_identity.status must be not_applicable",
        )


def resolve_runtime_ref(
    runtime_directory: Path, raw_ref: str, result: Result, label: str = "snapshot_ref"
) -> Path | None:
    if not has_concrete(raw_ref):
        result.errors.append(f"{label} must be concrete")
        return None
    candidate = Path(raw_ref.split("#", 1)[0])
    if not candidate.is_absolute():
        candidate = runtime_directory / candidate
    current = candidate
    boundary = runtime_directory.absolute()
    while current.absolute() != boundary and current.parent != current:
        if current.is_symlink():
            result.errors.append(f"{label} may not traverse a symbolic link")
            return None
        current = current.parent
    resolved = candidate.resolve()
    try:
        resolved.relative_to(runtime_directory.resolve())
    except ValueError:
        result.errors.append(f"{label} must stay inside the Testing Runtime directory")
        return None
    return resolved


def integer(value: str, label: str, result: Result) -> int:
    try:
        number = int(value)
    except ValueError:
        result.errors.append(f"{label} must be an integer")
        return -1
    result.require(number >= 0, f"{label} must not be negative")
    return number


def read_runtime_document(
    runtime_directory: Path, raw_ref: str, label: str, result: Result
) -> tuple[str, list[Entry]]:
    path = resolve_runtime_ref(runtime_directory, raw_ref, result, label)
    if path is None:
        return "", []
    body = read(path, result)
    parsed = entries(body) if body else []
    for duplicate_path, lines in duplicate_paths(parsed):
        result.errors.append(
            f"duplicate {label} key {'.'.join(duplicate_path)} at lines {lines}"
        )
    return body, parsed


def resolve_source_ref(
    runtime_directory: Path, raw_ref: str, label: str, result: Result
) -> Path | None:
    if not has_concrete(raw_ref):
        result.errors.append(f"{label} must be concrete")
        return None
    reference = Path(raw_ref.split("#", 1)[0])
    candidate_pairs = (
        [(reference, Path(reference.anchor))]
        if reference.is_absolute()
        else [
            *((parent / reference, parent) for parent in (runtime_directory, *runtime_directory.parents)),
            (Path.cwd() / reference, Path.cwd()),
        ]
    )
    existing: set[Path] = set()
    symlinked = False
    for candidate, boundary in candidate_pairs:
        if not candidate.is_file():
            continue
        current = candidate
        while current.absolute() != boundary.absolute() and current.parent != current:
            if current.is_symlink():
                symlinked = True
                break
            current = current.parent
        else:
            existing.add(candidate.resolve())
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


def validate_long_intake(
    runtime_directory: Path,
    state_entries: list[Entry],
    planning: dict[str, object],
    result: Result,
) -> None:
    intake = ("intake_binding",)
    handoff_ref = value_at(state_entries, intake + ("long_testing_handoff_ref",))
    handoff_path = resolve_source_ref(
        runtime_directory, handoff_ref, "intake_binding.long_testing_handoff_ref", result
    )
    if handoff_path is None:
        return
    handoff_text = read(handoff_path, result)
    candidates = [
        block
        for block in text_blocks(handoff_text)
        if re.search(r"(?m)^\s*runtime_epoch\s*:", block)
        and re.search(r"(?m)^\s*required_validation_gate\s*:", block)
    ]
    if len(candidates) != 1:
        result.errors.append(
            "Long Testing Handoff must contain exactly one runtime/gate document"
        )
        return
    handoff = entries(candidates[0])
    for path, lines in duplicate_paths(handoff):
        result.errors.append(
            f"duplicate Long Testing Handoff key {'.'.join(path)} at lines {lines}"
        )
    comparisons = (
        ("runtime_epoch", "long_runtime_epoch"),
        ("planning_handoff_ref", "planning_handoff_ref"),
        ("planning_baseline_revision", "planning_baseline_revision"),
        ("active_change_revision", "active_change_revision"),
    )
    for handoff_field, intake_field in comparisons:
        result.require(
            value_at(handoff, (handoff_field,))
            == value_at(state_entries, intake + (intake_field,)),
            f"Long Testing Handoff {handoff_field} does not match Testing intake",
        )
    executed = set(list_at(handoff, ("executed_task_contract_revisions",)))
    expected_executed = planning.get("executable_task_revisions", set())
    result.require(bool(executed), "Long Testing Handoff executed_task_contract_revisions is missing")
    result.require(executed == expected_executed, "Long executed TASK revisions do not match Planning executable queues")
    gate = ("required_validation_gate",)
    result.require(
        value_at(handoff, gate + ("result",))
        == value_at(state_entries, intake + ("required_validation_gate_result",)),
        "Long required validation gate result does not match Testing intake",
    )
    result.require(
        value_at(handoff, gate + ("matrix_revision",))
        == value_at(
            state_entries, intake + ("required_validation_matrix_revision",)
        ),
        "Long required validation Matrix revision does not match Testing intake",
    )
    result.require(
        value_at(handoff, gate + ("matrix_ref",))
        == value_at(state_entries, intake + ("required_validation_matrix_ref",)),
        "Long required validation Matrix ref does not match Testing intake",
    )
    result.require(
        value_at(handoff, ("acceptance_status",)) == "not_started"
        and value_at(handoff, ("owner_runtime",)) == "testing-layer-runtime",
        "Long Testing Handoff acceptance ownership is invalid",
    )
    effective_ids = set(list_at(handoff, gate + ("effective_validation_ids",)))
    result.require(bool(effective_ids), "Long required validation gate has no effective validation ids")
    automated_prefixes = record_prefixes(handoff, ("automated_passed",))
    result.require(
        not list_at(handoff, ("automated_passed",)),
        "Long automated_passed may not contain scalar entries",
    )
    automated_ids = [
        value_at(handoff, prefix + ("source_validation_id",))
        for prefix in automated_prefixes
    ]
    result.require(
        len(automated_ids) == len(set(automated_ids)),
        "Long automated_passed source_validation_ids must be unique",
    )
    result.require(
        set(automated_ids) == effective_ids,
        "Long automated_passed must expose exactly the effective validation ids",
    )
    matrix_ref = value_at(handoff, gate + ("matrix_ref",))
    matrix_path = resolve_source_ref(
        handoff_path.parent, matrix_ref, "Long required validation Matrix ref", result
    )
    if matrix_path is not None:
        matrix_text = read(matrix_path, result)
        matrix_entries = entries(matrix_text)
        result.require(
            value_at(matrix_entries, ("required_validation_matrix", "matrix_revision"))
            == value_at(handoff, gate + ("matrix_revision",)),
            "Long required validation Matrix document revision mismatch",
        )
    validation_path = handoff_path.parent / "validation-results.md"
    validation_text = read(validation_path, result)
    validation_records = {
        value_at(parsed, prefix + ("validation_id",)): (parsed, prefix)
        for parsed, prefix in anchored_records(validation_text, "validation_id")
    } if validation_text else {}
    compatible_validation_ids: set[str] = set()
    machine_receipt_refs: dict[str, str] = {}
    validation_matrix_revisions: dict[str, str] = {}
    current_matrix_revision = value_at(handoff, gate + ("matrix_revision",))
    for validation_id in effective_ids:
        record = validation_records.get(validation_id)
        if record is None:
            result.errors.append(f"Long effective validation id does not resolve: {validation_id}")
            continue
        parsed_record, prefix = record
        result.require(value_at(parsed_record, prefix + ("result",)) == "passed", f"{validation_id}: Long effective validation result is not passed")
        result_matrix_revision = value_at(parsed_record, prefix + ("matrix_revision",))
        validation_matrix_revisions[validation_id] = result_matrix_revision
        machine_receipt_ref = value_at(
            parsed_record, prefix + ("execution_receipt_ref",)
        )
        result.require(
            re.fullmatch(
                r"machine-execution-receipts/[A-Za-z0-9._-]+\.json",
                machine_receipt_ref,
            )
            is not None,
            f"{validation_id}: Long execution_receipt_ref is missing or invalid",
        )
        result.require(
            machine_receipt_ref
            in list_at(parsed_record, prefix + ("evidence",)),
            f"{validation_id}: Long validation evidence does not include its machine receipt",
        )
        if machine_receipt_ref:
            machine_receipt_refs[validation_id] = machine_receipt_ref
        compatibility = value_at(parsed_record, prefix + ("matrix_compatibility",))
        compatibility_evidence = list_at(
            parsed_record, prefix + ("compatibility_evidence",)
        )
        matrix_is_current = result_matrix_revision == current_matrix_revision
        carried_forward = (
            result_matrix_revision != current_matrix_revision
            and compatibility == "carried_forward_unchanged"
            and bool(compatibility_evidence)
        )
        result.require(
            matrix_is_current or carried_forward,
            f"{validation_id}: Long effective validation Matrix revision is neither current nor explicitly carried forward",
        )
        if matrix_is_current or carried_forward:
            compatible_validation_ids.add(validation_id)
    planning["long_effective_validation_ids"] = effective_ids
    planning["long_compatible_validation_ids"] = compatible_validation_ids
    receipt_ref = value_at(handoff, ("validator_receipt_ref",))
    receipt_path = resolve_source_ref(
        handoff_path.parent, receipt_ref, "Long validator_receipt_ref", result
    )
    if receipt_path is None:
        return
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        result.errors.append(f"Long readiness receipt is invalid: {error}")
        return
    if not isinstance(receipt, dict):
        result.errors.append("Long readiness receipt root must be an object")
        return
    declared_digest = receipt.get("receipt_digest")
    unsigned = {key: value for key, value in receipt.items() if key != "receipt_digest"}
    expected_digest = "sha256:" + hashlib.sha256(
        json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    result.require(declared_digest == expected_digest, "Long readiness receipt digest is invalid")
    result.require(receipt.get("schema_version") == LONG_RECEIPT_SCHEMA, "Long readiness receipt schema is invalid")
    result.require(
        receipt.get("runtime_epoch") == value_at(handoff, ("runtime_epoch",)),
        "Long readiness receipt runtime epoch mismatch",
    )
    result.require(
        receipt.get("matrix_revision") == value_at(handoff, gate + ("matrix_revision",)),
        "Long readiness receipt Matrix revision mismatch",
    )
    receipt_ids = receipt.get("effective_validation_ids")
    result.require(
        isinstance(receipt_ids, list) and set(receipt_ids) == effective_ids,
        "Long readiness receipt effective validation ids mismatch",
    )
    repository_revision = str(receipt.get("repository_revision", ""))
    result.require(DIGEST.fullmatch(repository_revision) is not None, "Long readiness receipt repository revision is invalid")
    planning["long_repository_revision"] = repository_revision
    planning["long_receipt_path"] = receipt_path
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, list):
        result.errors.append("Long readiness receipt artifacts must be a list")
        return
    seen_refs: set[str] = set()
    source_refs: set[str] = set()
    long_workflow: dict[str, object] | None = None
    for item in artifacts:
        if not isinstance(item, dict) or item.get("kind") not in {"runtime", "source"}:
            result.errors.append("Long readiness receipt contains an invalid artifact record")
            continue
        reference = str(item.get("ref", ""))
        if item.get("kind") == "runtime":
            seen_refs.add(reference)
            raw_candidate = handoff_path.parent / reference
            current_candidate = raw_candidate
            symlinked = False
            while (
                current_candidate.absolute() != handoff_path.parent.absolute()
                and current_candidate.parent != current_candidate
            ):
                if current_candidate.is_symlink():
                    symlinked = True
                    break
                current_candidate = current_candidate.parent
            if symlinked:
                result.errors.append(
                    f"Long readiness receipt runtime artifact may not be a symlink: {reference}"
                )
                continue
            candidate = raw_candidate.resolve()
            try:
                candidate.relative_to(handoff_path.parent.resolve())
            except ValueError:
                result.errors.append(f"Long readiness receipt artifact escapes Runtime: {reference}")
                continue
        else:
            source_refs.add(reference)
            resolved_source = resolve_source_ref(
                handoff_path.parent,
                reference,
                f"Long readiness receipt source {reference}",
                result,
            )
            if resolved_source is None:
                continue
            candidate = resolved_source
        if not candidate.is_file():
            result.errors.append(f"Long readiness receipt artifact is missing: {reference}")
            continue
        result.require(
            item.get("sha256") == hashlib.sha256(candidate.read_bytes()).hexdigest(),
            f"Long readiness receipt artifact changed: {reference}",
        )
        if reference == "long-workflow-state.json":
            try:
                candidate_workflow = json.loads(candidate.read_text(encoding="utf-8"))
                if isinstance(candidate_workflow, dict):
                    long_workflow = candidate_workflow
            except json.JSONDecodeError:
                result.errors.append("Long workflow state is not valid JSON")
    result.require(
        LONG_RECEIPT_REQUIRED_ARTIFACTS <= seen_refs,
        "Long readiness receipt does not freeze every required Long artifact",
    )
    result.require(
        set(machine_receipt_refs.values()) <= seen_refs,
        "Long readiness receipt does not freeze every effective machine execution receipt",
    )
    for validation_id, machine_receipt_ref in machine_receipt_refs.items():
        machine_path = (handoff_path.parent / machine_receipt_ref).resolve()
        try:
            machine_receipt = json.loads(machine_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            result.errors.append(
                f"{validation_id}: Long machine execution receipt is invalid: {error}"
            )
            continue
        if not isinstance(machine_receipt, dict):
            result.errors.append(
                f"{validation_id}: Long machine execution receipt root must be an object"
            )
            continue
        machine_unsigned = {
            key: value
            for key, value in machine_receipt.items()
            if key != "receipt_digest"
        }
        machine_digest = "sha256:" + hashlib.sha256(
            json.dumps(
                machine_unsigned,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        result.require(
            machine_receipt.get("receipt_digest") == machine_digest,
            f"{validation_id}: Long machine execution receipt digest is invalid",
        )
        result.require(
            machine_receipt.get("schema_version") == LONG_MACHINE_RECEIPT_SCHEMA
            and machine_receipt.get("generated_by") == LONG_MACHINE_RUNNER,
            f"{validation_id}: Long machine execution receipt producer is invalid",
        )
        result.require(
            machine_receipt.get("runtime_epoch")
            == value_at(handoff, ("runtime_epoch",))
            and machine_receipt.get("validation_id") == validation_id
            and machine_receipt.get("matrix_revision")
            == validation_matrix_revisions.get(validation_id)
            and machine_receipt.get("repository_revision") == repository_revision
            and machine_receipt.get("result") == "passed",
            f"{validation_id}: Long machine execution receipt binding is invalid",
        )
    result.require(bool(source_refs), "Long readiness receipt contains no frozen source artifacts")
    result.require(
        value_at(state_entries, intake + ("planning_handoff_ref",)) in source_refs,
        "Long readiness receipt does not freeze the Planning Handoff source",
    )
    if long_workflow is not None:
        result.require(
            long_workflow.get("current_stage") in {"ready_for_local_test", "ready_for_local_retest"},
            "Long workflow receipt is not at a ready stage",
        )
        result.require(
            long_workflow.get("history_digest") == receipt.get("workflow_history_digest"),
            "Long workflow history digest does not match the readiness receipt",
        )


def testing_result_records(text: str, result: Result) -> dict[str, tuple[list[Entry], tuple[str, ...]]]:
    records: dict[str, tuple[list[Entry], tuple[str, ...]]] = {}
    for block in text_blocks(text):
        for path, lines in duplicate_paths(entries(block)):
            result.errors.append(
                f"duplicate test result key {'.'.join(path)} at lines {lines}"
            )
    for parsed, prefix in anchored_records(text, "item_id"):
        item_id = value_at(parsed, prefix + ("item_id",))
        if not has_concrete(item_id):
            result.errors.append("test result item_id must be concrete")
        elif item_id in records:
            result.errors.append(f"duplicate test result item_id: {item_id}")
        else:
            records[item_id] = (parsed, prefix)
    return records


def evidence_records(text: str, result: Result) -> dict[str, tuple[list[Entry], tuple[str, ...]]]:
    records: dict[str, tuple[list[Entry], tuple[str, ...]]] = {}
    for block in text_blocks(text):
        parsed = entries(block)
        for path, lines in duplicate_paths(parsed):
            result.errors.append(
                f"duplicate evidence key {'.'.join(path)} at lines {lines}"
            )
        for entry in parsed:
            if entry.path[-1:] != ("item_id",) or not entry.path[:-1]:
                continue
            prefix = entry.path[:-1]
            evidence_id = prefix[-1]
            if evidence_id.startswith("["):
                evidence_id = value_at(parsed, prefix + ("evidence_id",))
            if not has_concrete(evidence_id):
                result.errors.append("evidence id must be concrete")
            elif evidence_id in records:
                result.errors.append(f"duplicate evidence id: {evidence_id}")
            else:
                records[evidence_id] = (parsed, prefix)
    return records


def validate_evidence_content(
    runtime_directory: Path,
    evidence_id: str,
    parsed: list[Entry],
    prefix: tuple[str, ...],
    result: Result,
) -> Path | None:
    declared_digest = value_at(parsed, prefix + ("content_sha256",))
    result.require(
        DIGEST.fullmatch(declared_digest) is not None,
        f"{evidence_id}: content_sha256 must be a sha256 digest",
    )
    durable_path = resolve_runtime_ref(
        runtime_directory,
        value_at(parsed, prefix + ("path",)),
        result,
        f"{evidence_id}.path",
    )
    if durable_path is None:
        return None
    result.require(
        durable_path.is_file() and durable_path.stat().st_size > 0,
        f"{evidence_id}: durable evidence file is missing or empty",
    )
    if durable_path.is_file():
        actual_digest = "sha256:" + hashlib.sha256(durable_path.read_bytes()).hexdigest()
        result.require(
            declared_digest == actual_digest,
            f"{evidence_id}: durable evidence content does not match content_sha256",
        )
    return durable_path


def validate_final_closure(
    runtime_directory: Path,
    state_entries: list[Entry],
    state_identity: dict[str, object],
    planning: dict[str, object],
    result: Result,
) -> None:
    matrix_ref = value_at(state_entries, ("business_journey_matrix_ref",))
    matrix_text, matrix = read_runtime_document(
        runtime_directory, matrix_ref, "business_journey_matrix_ref", result
    )
    if not matrix:
        return
    result.require(
        value_at(matrix, ("matrix_revision",))
        == value_at(state_entries, ("business_journey_matrix_revision",)),
        "business journey matrix revision mismatch",
    )
    result.require(
        value_at(matrix, ("long_handoff_ref",))
        == value_at(state_entries, ("intake_binding", "long_testing_handoff_ref")),
        "business journey matrix Long Handoff mismatch",
    )
    expected_gate_ref = (
        value_at(state_entries, ("intake_binding", "long_testing_handoff_ref"))
        + "#required_validation_gate"
    )
    result.require(
        value_at(matrix, ("required_validation_gate_ref",)) == expected_gate_ref,
        "business journey matrix required_validation_gate_ref is not bound to the current Long gate",
    )
    result.require(
        value_at(matrix, ("deployment_revision_ref",))
        == "test-runtime-state.md#current_deployment_revision",
        "business journey matrix deployment_revision_ref is invalid",
    )

    journey_prefixes = sorted(
        {
            entry.path[:2]
            for entry in matrix
            if len(entry.path) >= 3
            and entry.path[0] == "journeys"
            and entry.path[1].startswith("[")
        }
    )
    flow_refs: list[str] = []
    local_required: dict[str, list[str]] = {}
    cloud_required: dict[str, list[str]] = {}
    expected_flows = planning.get("flows", {})
    expected_tests = planning.get("tests", {})
    assert isinstance(expected_flows, dict)
    assert isinstance(expected_tests, dict)
    result.require(
        set(list_at(matrix, ("planning_scope_refs",))) == set(expected_flows),
        "business journey planning_scope_refs do not match Planning FLOW contracts",
    )
    journey_test_refs: dict[str, set[str]] = {}
    for prefix in journey_prefixes:
        flow_ref = value_at(matrix, prefix + ("flow_ref",))
        flow_refs.append(flow_ref)
        result.require(has_concrete(flow_ref), "every business journey requires a concrete flow_ref")
        flow_contract = expected_flows.get(flow_ref, {})
        if not isinstance(flow_contract, dict):
            flow_contract = {}
        expected_priority = str(flow_contract.get("priority", ""))
        result.require(
            value_at(matrix, prefix + ("priority",)) == expected_priority
            and expected_priority in {"P0", "P1", "P2"},
            f"{flow_ref}: priority does not match Planning",
        )
        result.require(
            not list_at(matrix, prefix + ("open_coverage_gaps",)),
            f"{flow_ref}: open coverage gaps remain",
        )
        local_requirement = value_at(
            matrix, prefix + ("local_business_e2e", "requirement")
        )
        cloud_requirement = value_at(
            matrix, prefix + ("deployed_environment_e2e", "requirement")
        )
        linked_tests = {
            test_ref
            for test_ref, test_contract in expected_tests.items()
            if isinstance(test_contract, dict)
            and flow_ref in test_contract.get("flow_refs", set())
        } | set(flow_contract.get("test_refs", set()))
        linked_tests &= set(expected_tests)
        success_test_refs = set(
            list_at(matrix, prefix + ("success_journey_test_refs",))
        )
        journey_test_refs[flow_ref] = success_test_refs
        result.require(bool(success_test_refs), f"{flow_ref}: success journey TEST refs are missing")
        result.require(success_test_refs <= linked_tests, f"{flow_ref}: journey references TEST contracts not linked by Planning")
        plan_local_required = any(
            isinstance(expected_tests.get(test_ref), dict)
            and expected_tests[test_ref].get("local_requirement") == "required"
            for test_ref in linked_tests
        )
        expected_local = "required" if expected_priority in {"P0", "P1"} or plan_local_required else "not_applicable"
        plan_cloud_required = any(
            isinstance(expected_tests.get(test_ref), dict)
            and expected_tests[test_ref].get("cloud_requirement") == "required"
            for test_ref in linked_tests
        )
        expected_cloud = "required" if plan_cloud_required or (expected_priority == "P0" and state_identity["status"] == "known") else "not_applicable"
        result.require(
            local_requirement == expected_local,
            f"{flow_ref}: local business/E2E requirement does not match Planning",
        )
        result.require(
            cloud_requirement == expected_cloud,
            f"{flow_ref}: deployed E2E requirement does not match Planning/deployment scope",
        )
        selection_reason = value_at(
            matrix, prefix + ("deployed_environment_e2e", "selection_reason")
        )
        if expected_cloud == "required" and expected_priority == "P0":
            result.require(selection_reason == "p0_success_journey", f"{flow_ref}: P0 cloud journey selection reason is invalid")
        elif expected_cloud == "not_applicable":
            result.require(selection_reason in {"no_deployment_in_scope", "not_applicable"}, f"{flow_ref}: not-applicable cloud journey requires an explicit reason")
        if local_requirement == "required":
            refs = list_at(matrix, prefix + ("local_business_e2e", "result_refs"))
            result.require(bool(refs), f"{flow_ref}: required local business/E2E result is missing")
            local_required[flow_ref] = refs
        if cloud_requirement == "required":
            refs = list_at(
                matrix, prefix + ("deployed_environment_e2e", "result_refs")
            )
            result.require(bool(refs), f"{flow_ref}: required deployed E2E result is missing")
            cloud_required[flow_ref] = refs
    result.require(
        len(flow_refs) == len(set(flow_refs)), "business journey flow_ref values must be unique"
    )
    result.require(set(flow_refs) == set(expected_flows), "business journey Matrix does not cover every Planning FLOW")
    result.require(
        not list_at(matrix, ("coverage_summary", "open_required_gaps")),
        "business journey coverage summary still has required gaps",
    )
    required_flows = set(local_required) | set(cloud_required)
    required_result_refs = {
        item_ref
        for refs in list(local_required.values()) + list(cloud_required.values())
        for item_ref in refs
    }
    result.require(
        integer(
            value_at(matrix, ("coverage_summary", "required_flow_count")),
            "coverage_summary.required_flow_count",
            result,
        )
        == len(required_flows),
        "coverage_summary.required_flow_count does not reconcile",
    )
    result.require(
        integer(
            value_at(matrix, ("coverage_summary", "locally_covered_flow_count")),
            "coverage_summary.locally_covered_flow_count",
            result,
        )
        == len(local_required),
        "coverage_summary.locally_covered_flow_count does not reconcile",
    )
    result.require(
        integer(
            value_at(matrix, ("coverage_summary", "cloud_required_flow_count")),
            "coverage_summary.cloud_required_flow_count",
            result,
        )
        == len(cloud_required),
        "coverage_summary.cloud_required_flow_count does not reconcile",
    )
    result.require(
        integer(
            value_at(matrix, ("coverage_summary", "cloud_covered_flow_count")),
            "coverage_summary.cloud_covered_flow_count",
            result,
        )
        == len(cloud_required),
        "coverage_summary.cloud_covered_flow_count does not reconcile",
    )
    if cloud_required:
        result.require(
            state_identity["status"] == "known",
            "required deployed E2E closure requires a known deployment identity",
        )

    results_text = read(runtime_directory / "test-validation-results.md", result)
    result_records = testing_result_records(results_text, result) if results_text else {}
    evidence_text = read(runtime_directory / "test-evidence-index.md", result)
    evidence = evidence_records(evidence_text, result) if evidence_text else {}
    required_result_groups = [
        (flow_ref, refs, False) for flow_ref, refs in local_required.items()
    ] + [(flow_ref, refs, True) for flow_ref, refs in cloud_required.items()]
    for flow_ref, refs, is_cloud in required_result_groups:
        for item_ref in refs:
            record = result_records.get(item_ref)
            if record is None:
                result.errors.append(f"{flow_ref}: unresolved test result ref {item_ref}")
                continue
            parsed, prefix = record
            item_type = value_at(parsed, prefix + ("item_type",))
            result.require(item_type in ITEM_TYPES, f"{item_ref}: item_type is invalid")
            for field_name in (
                "attempt",
                "environment",
                "started_at",
                "completed_at",
                "depends_on_check",
                "expected_evidence",
                "result_summary",
                "evidence_reuse",
                "writeback_status",
            ):
                result.require(has_concrete(value_at(parsed, prefix + (field_name,))), f"{item_ref}: missing required result field {field_name}")
            result.require(integer(value_at(parsed, prefix + ("attempt",)), f"{item_ref}.attempt", result) > 0, f"{item_ref}: attempt must be positive")
            result.require(value_at(parsed, prefix + ("depends_on_check",)) == "passed", f"{item_ref}: dependency check is not passed")
            covers = set(list_at(parsed, prefix + ("covers",)))
            result.require(bool(covers & journey_test_refs.get(flow_ref, set())), f"{item_ref}: result is not bound to the Planning TEST contract for {flow_ref}")
            result.require(
                value_at(parsed, prefix + ("status",)) in PASS_STATUSES,
                f"{item_ref}: required journey result is not verified",
            )
            result.require(
                value_at(parsed, prefix + ("writeback_status",)) == "updated",
                f"{item_ref}: writeback_status must be updated",
            )
            status = value_at(parsed, prefix + ("status",))
            if status == "reused_from_long":
                source_validation_id = value_at(
                    parsed, prefix + ("source_validation_id",)
                )
                result.require(
                    source_validation_id
                    in planning.get("long_effective_validation_ids", set())
                    and source_validation_id
                    in planning.get("long_compatible_validation_ids", set()),
                    f"{item_ref}: reused_from_long does not bind a current effective Long validation",
                )
                result.require(
                    value_at(parsed, prefix + ("evidence_reuse",)).lower() == "true",
                    f"{item_ref}: reused_from_long requires evidence_reuse: true",
                )
            if is_cloud:
                result.require(
                    value_at(parsed, prefix + ("environment_revision_ref",))
                    == "test-runtime-state.md#current_deployment_revision",
                    f"{item_ref}: deployed E2E result is not bound to current deployment identity",
                )
            evidence_refs = list_at(parsed, prefix + ("evidence_refs",))
            result.require(bool(evidence_refs), f"{item_ref}: verified result requires evidence refs")
            for evidence_ref in evidence_refs:
                evidence_record = evidence.get(evidence_ref)
                if evidence_record is None:
                    result.errors.append(f"{item_ref}: unresolved evidence ref {evidence_ref}")
                    continue
                evidence_parsed, evidence_prefix = evidence_record
                required_evidence_fields = (
                    "item_id",
                    "evidence_type",
                    "source",
                    "path",
                    "target_environment",
                    "revision_kind",
                    "revision",
                    "deployment_identity_ref",
                    "description",
                    "added_at",
                    "valid",
                    "invalidated_by",
                    "content_sha256",
                )
                for field_name in required_evidence_fields:
                    evidence_path = evidence_prefix + (field_name,)
                    result.require(path_present(evidence_parsed, evidence_path), f"{evidence_ref}: missing evidence field {field_name}")
                    if field_name not in {"deployment_identity_ref", "invalidated_by"}:
                        result.require(has_concrete(value_at(evidence_parsed, evidence_path)), f"{evidence_ref}: evidence field {field_name} must be concrete")
                durable_evidence_path = validate_evidence_content(
                    runtime_directory,
                    evidence_ref,
                    evidence_parsed,
                    evidence_prefix,
                    result,
                )
                result.require(path_present(evidence_parsed, evidence_prefix + ("component_revision_refs",)), f"{evidence_ref}: component_revision_refs is missing")
                evidence_flows = set(list_at(evidence_parsed, evidence_prefix + ("flow_refs",)))
                result.require(flow_ref in evidence_flows, f"{evidence_ref}: evidence is not bound to {flow_ref}")
                result.require(
                    value_at(evidence_parsed, evidence_prefix + ("item_id",)) == item_ref,
                    f"{evidence_ref}: evidence item_id mismatch",
                )
                result.require(
                    value_at(evidence_parsed, evidence_prefix + ("valid",)).lower()
                    == "true",
                    f"{evidence_ref}: evidence is not valid",
                )
                if status == "reused_from_long":
                    receipt_path = planning.get("long_receipt_path")
                    result.require(
                        value_at(evidence_parsed, evidence_prefix + ("source",))
                        == "long_readiness_receipt"
                        and isinstance(receipt_path, Path)
                        and durable_evidence_path == receipt_path,
                        f"{evidence_ref}: reused Long evidence must bind the frozen Long readiness receipt",
                    )
                if is_cloud:
                    result.require(
                        value_at(
                            evidence_parsed,
                            evidence_prefix + ("deployment_identity_ref",),
                        )
                        == "test-runtime-state.md#current_deployment_revision",
                        f"{evidence_ref}: cloud evidence is not bound to current deployment identity",
                    )
                    result.require(
                        value_at(evidence_parsed, evidence_prefix + ("target_environment",))
                        == str(state_identity["target_environment"]),
                        f"{evidence_ref}: cloud evidence target environment mismatch",
                    )
                    result.require(
                        value_at(evidence_parsed, evidence_prefix + ("revision_kind",))
                        == str(state_identity["revision_kind"])
                        and value_at(evidence_parsed, evidence_prefix + ("revision",))
                        == str(state_identity["revision"]),
                        f"{evidence_ref}: cloud evidence revision mismatch",
                    )
                else:
                    result.require(
                        value_at(evidence_parsed, evidence_prefix + ("target_environment",)) == "local"
                        and value_at(evidence_parsed, evidence_prefix + ("revision_kind",)) in LOCAL_REVISION_KINDS,
                        f"{evidence_ref}: local evidence lacks a reproducible local revision",
                    )
                    result.require(
                        value_at(evidence_parsed, evidence_prefix + ("revision",))
                        == planning.get("long_repository_revision", ""),
                        f"{evidence_ref}: local evidence revision does not match the frozen Long repository revision",
                    )
                    result.require(
                        value_at(evidence_parsed, evidence_prefix + ("deployment_identity_ref",)) == "not_applicable",
                        f"{evidence_ref}: local evidence deployment identity must be not_applicable",
                    )

    triage_text = read(runtime_directory / "change-triage.md", result)
    if triage_text:
        for block in text_blocks(triage_text):
            for path, lines in duplicate_paths(entries(block)):
                result.errors.append(
                    f"duplicate finding key {'.'.join(path)} at lines {lines}"
                )
        for parsed, prefix in anchored_records(triage_text, "finding_id"):
            finding_id = value_at(parsed, prefix + ("finding_id",))
            result.require(
                value_at(parsed, prefix + ("finding_status",)) == "closed",
                f"{finding_id}: finding is not closed",
            )
            retest_refs = set(list_at(parsed, prefix + ("retest_result_refs",)))
            closure_refs = set(list_at(parsed, prefix + ("closure_evidence_refs",)))
            result.require(
                bool(retest_refs) and bool(closure_refs),
                f"{finding_id}: closed finding lacks retest or closure evidence",
            )
            for retest_ref in retest_refs:
                retest_record = result_records.get(retest_ref)
                if retest_record is None:
                    result.errors.append(
                        f"{finding_id}: retest result ref does not resolve: {retest_ref}"
                    )
                    continue
                retest_parsed, retest_prefix = retest_record
                result.require(
                    value_at(retest_parsed, retest_prefix + ("status",))
                    in {"verified", "verified_by_user_report"}
                    and value_at(
                        retest_parsed, retest_prefix + ("writeback_status",)
                    )
                    == "updated",
                    f"{finding_id}: retest result is not verified and written back: {retest_ref}",
                )
            for closure_ref in closure_refs:
                closure_record = evidence.get(closure_ref)
                if closure_record is None:
                    result.errors.append(
                        f"{finding_id}: closure evidence ref does not resolve: {closure_ref}"
                    )
                    continue
                closure_parsed, closure_prefix = closure_record
                result.require(
                    value_at(closure_parsed, closure_prefix + ("item_id",))
                    in retest_refs
                    and value_at(closure_parsed, closure_prefix + ("valid",)).lower()
                    == "true",
                    f"{finding_id}: closure evidence is not valid evidence for a declared retest",
                )
                validate_evidence_content(
                    runtime_directory,
                    closure_ref,
                    closure_parsed,
                    closure_prefix,
                    result,
                )

    if value_at(state_entries, ("active_release_handoff", "status")) == "current":
        release_path = resolve_runtime_ref(
            runtime_directory,
            value_at(state_entries, ("active_release_handoff", "snapshot_ref")),
            result,
            "active_release_handoff.snapshot_ref",
        )
        if release_path is not None:
            release_text = read(release_path, result)
            release_entries = entries(release_text) if release_text else []
            result.require(
                value_at(release_entries, ("business_journey_coverage_status",))
                == "verified",
                "current Release Handoff business journey coverage is not verified",
            )
            result.require(
                set(list_at(release_entries, ("required_result_refs",)))
                == required_result_refs,
                "current Release Handoff required_result_refs do not match the business journey closure",
            )


def validate_release_handoff(
    runtime_directory: Path,
    state_text: str,
    state_entries: list[Entry],
    state_identity: dict[str, object],
    planning: dict[str, object],
    result: Result,
) -> None:
    active_prefix = ("active_release_handoff",)
    active_status = value_at(state_entries, active_prefix + ("status",))
    result.require(
        active_status in {"not_generated", "current", "invalidated"},
        "active_release_handoff.status is invalid",
    )
    if active_status == "not_generated":
        for field_name in (
            "snapshot_id",
            "snapshot_ref",
            "bound_deployment_identity_digest",
            "snapshot_digest",
        ):
            result.require(
                value_at(state_entries, active_prefix + (field_name,))
                == "not_applicable",
                f"active_release_handoff.{field_name} must be not_applicable",
            )
        result.require(
            value_at(state_entries, active_prefix + ("invalidated_by",)).lower()
            in {"null", "none"},
            "not-generated release handoff may not have invalidated_by",
        )
        return

    for field_name in (
        "snapshot_id",
        "snapshot_ref",
        "bound_deployment_identity_digest",
        "snapshot_digest",
    ):
        result.require(
            has_concrete(value_at(state_entries, active_prefix + (field_name,))),
            f"active_release_handoff.{field_name} must be concrete",
        )

    snapshot_path = resolve_runtime_ref(
        runtime_directory,
        value_at(state_entries, active_prefix + ("snapshot_ref",)),
        result,
    )
    if snapshot_path is None:
        return
    release_text = read(snapshot_path, result)
    if not release_text:
        return
    release_entries = entries(release_text)
    for path, lines in duplicate_paths(release_entries):
        result.errors.append(f"duplicate release handoff key {'.'.join(path)} at lines {lines}")

    state_snapshot_id = value_at(state_entries, active_prefix + ("snapshot_id",))
    release_snapshot_id = value_at(release_entries, ("snapshot_id",))
    release_status = value_at(release_entries, ("snapshot_status",))
    result.require(has_concrete(release_snapshot_id), "release handoff snapshot_id must be concrete")
    result.require(state_snapshot_id == release_snapshot_id, "release handoff snapshot_id mismatch")
    result.require(active_status == release_status, "release handoff status mismatch")
    computed_snapshot_digest = canonical_release_snapshot_digest(release_entries)
    result.require(
        value_at(release_entries, ("snapshot_digest",)) == computed_snapshot_digest,
        "release handoff snapshot_digest does not match its frozen payload",
    )
    result.require(
        value_at(state_entries, active_prefix + ("snapshot_digest",))
        == computed_snapshot_digest,
        "active release handoff snapshot_digest mismatch",
    )
    release_identity = identity(release_entries, ("deployment_identity_snapshot",))
    validate_identity(release_identity, "deployment_identity_snapshot", result)
    result.require(
        value_at(state_entries, active_prefix + ("bound_deployment_identity_digest",))
        == str(release_identity["identity_digest"]),
        "active release handoff deployment identity digest mismatch",
    )

    if active_status == "current":
        current_comparisons = (
            (
                ("current_test_epoch",),
                ("intake_binding", "current_test_epoch"),
                "test epoch",
            ),
            (
                ("planning_handoff_ref",),
                ("intake_binding", "planning_handoff_ref"),
                "Planning Handoff ref",
            ),
            (
                ("planning_baseline_revision",),
                ("intake_binding", "planning_baseline_revision"),
                "Planning revision",
            ),
            (
                ("active_change_revision",),
                ("intake_binding", "active_change_revision"),
                "active change revision",
            ),
            (
                ("long_testing_handoff_ref",),
                ("intake_binding", "long_testing_handoff_ref"),
                "Long Handoff ref",
            ),
            (
                ("business_journey_matrix_ref",),
                ("business_journey_matrix_ref",),
                "business journey matrix ref",
            ),
            (
                ("business_journey_matrix_revision",),
                ("business_journey_matrix_revision",),
                "business journey matrix revision",
            ),
        )
        for release_path, state_path, label in current_comparisons:
            result.require(
                value_at(release_entries, release_path)
                == value_at(state_entries, state_path),
                f"release handoff {label} mismatch",
            )
        result.require(
            release_identity == state_identity,
            "release handoff frozen deployment identity does not match current identity",
        )
        result.require(
            value_at(release_entries, ("invalidated_by",)).lower() in {"null", "none"},
            "current release handoff may not have invalidated_by",
        )
        expected_gate_ref = (
            value_at(state_entries, ("intake_binding", "long_testing_handoff_ref"))
            + "#required_validation_gate"
        )
        result.require(
            value_at(release_entries, ("required_validation_gate_ref",))
            == expected_gate_ref,
            "release handoff required validation gate ref mismatch",
        )
        expected_dependencies = planning.get("before_release_dependency_refs", set())
        assert isinstance(expected_dependencies, set)
        dependency_prefixes = record_prefixes(release_entries, ("dependencies",))
        dependency_refs = {
            value_at(release_entries, prefix + ("dependency_ref",))
            for prefix in dependency_prefixes
        }
        result.require(
            dependency_refs == expected_dependencies,
            "release handoff dependencies do not match Planning before-release dependencies",
        )
        result_records: dict[str, tuple[list[Entry], tuple[str, ...]]] = {}
        evidence: dict[str, tuple[list[Entry], tuple[str, ...]]] = {}
        if expected_dependencies:
            results_text = read(runtime_directory / "test-validation-results.md", result)
            evidence_text = read(runtime_directory / "test-evidence-index.md", result)
            result_records = testing_result_records(results_text, result) if results_text else {}
            evidence = evidence_records(evidence_text, result) if evidence_text else {}
        computed_unresolved: set[str] = set()
        for prefix in dependency_prefixes:
            dependency_ref = value_at(release_entries, prefix + ("dependency_ref",))
            for field_name in (
                "planning_snapshot_status",
                "testing_result_ref",
                "owner",
                "blocking_scope",
                "release_gate_owner",
            ):
                result.require(
                    has_concrete(value_at(release_entries, prefix + (field_name,))),
                    f"{dependency_ref}: release dependency field {field_name} must be concrete",
                )
            evidence_refs = list_at(release_entries, prefix + ("evidence_refs",))
            testing_result_ref = value_at(release_entries, prefix + ("testing_result_ref",))
            testing_record = result_records.get(testing_result_ref)
            resolved = testing_record is not None
            if testing_record is not None:
                parsed_record, record_prefix = testing_record
                status = value_at(parsed_record, record_prefix + ("status",))
                resolved = status in {"verified", "verified_by_user_report"}
                resolved = resolved and value_at(
                    parsed_record, record_prefix + ("item_type",)
                ) == "environment_prerequisite"
                resolved = resolved and value_at(
                    parsed_record, record_prefix + ("dependency_ref",)
                ) == dependency_ref
                result.require(
                    value_at(parsed_record, record_prefix + ("item_type",))
                    == "environment_prerequisite",
                    f"{dependency_ref}: testing_result_ref must identify an environment_prerequisite result",
                )
                result.require(
                    value_at(parsed_record, record_prefix + ("dependency_ref",))
                    == dependency_ref,
                    f"{dependency_ref}: testing result dependency_ref mismatch",
                )
                result.require(
                    set(list_at(parsed_record, record_prefix + ("evidence_refs",)))
                    == set(evidence_refs),
                    f"{dependency_ref}: Release Handoff evidence refs do not match the dependency result",
                )
            valid_evidence = bool(evidence_refs)
            for evidence_ref in evidence_refs:
                evidence_record = evidence.get(evidence_ref)
                if evidence_record is None:
                    valid_evidence = False
                    continue
                evidence_parsed, evidence_prefix = evidence_record
                valid_evidence = valid_evidence and value_at(
                    evidence_parsed, evidence_prefix + ("valid",)
                ).lower() == "true"
                valid_evidence = valid_evidence and value_at(
                    evidence_parsed, evidence_prefix + ("item_id",)
                ) == testing_result_ref
                durable_path = validate_evidence_content(
                    runtime_directory,
                    evidence_ref,
                    evidence_parsed,
                    evidence_prefix,
                    result,
                )
                valid_evidence = valid_evidence and durable_path is not None
            if not resolved or not valid_evidence:
                computed_unresolved.add(dependency_ref)
        declared_unresolved = set(list_at(release_entries, ("unresolved_dependency_refs",)))
        result.require(
            declared_unresolved == computed_unresolved,
            "release handoff unresolved_dependency_refs do not reconcile",
        )
        expected_readiness = "ready" if not computed_unresolved else "blocked"
        result.require(
            value_at(release_entries, ("release_readiness_status",))
            == expected_readiness,
            "release handoff readiness status does not reconcile",
        )
        if value_at(release_entries, ("business_journey_coverage_status",)) == "verified":
            result.require(bool(list_values(release_text, "required_result_refs")), "verified release handoff requires required_result_refs")
            result.require(not list_values(release_text, "open_finding_refs"), "verified release handoff may not contain open_finding_refs")
    else:
        state_invalidated_by = value_at(state_entries, active_prefix + ("invalidated_by",))
        release_invalidated_by = value_at(release_entries, ("invalidated_by",))
        result.require(has_concrete(state_invalidated_by), "invalidated active release handoff requires invalidated_by")
        result.require(state_invalidated_by == release_invalidated_by, "release handoff invalidated_by mismatch")
        result.require(
            has_concrete(value_at(release_entries, ("invalidated_at",))),
            "invalidated release handoff requires invalidated_at",
        )


def testing_transition_allowed(
    previous: dict[str, object] | None, event: dict[str, object]
) -> bool:
    cycle_kind = event.get("cycle_kind")
    edge = (str(event.get("from_stage")), str(event.get("to_stage")))
    if previous is None:
        return cycle_kind == "initial" and event.get("cycle") == 1 and edge == ("not_started", "intake")
    previous_cycle = previous.get("cycle")
    cycle = event.get("cycle")
    if cycle == previous_cycle:
        if cycle_kind != previous.get("cycle_kind"):
            return False
        if cycle_kind == "initial":
            return edge in TESTING_INITIAL_EDGES
        if cycle_kind == "deployment_revision":
            return edge in TESTING_DEPLOYMENT_EDGES
        return edge in TESTING_RETEST_EDGES
    if not isinstance(previous_cycle, int) or cycle != previous_cycle + 1:
        return False
    if cycle_kind == "deployment_revision":
        return edge in {
            ("release_handoff", "cloud_testing"),
            ("cloud_testing", "cloud_testing"),
        }
    return (
        cycle_kind == "retest"
        and previous.get("to_stage") == "release_handoff"
        and edge == ("release_handoff", "local_testing")
    )


def validate_testing_workflow(
    runtime_directory: Path, parsed: list[Entry], result: Result
) -> None:
    runtime_id = value_at(parsed, ("intake_binding", "current_test_epoch"))
    ledger = read_ledger(runtime_directory)
    if ledger is None:
        result.errors.append("missing testing-workflow-state.json; Testing stages must advance through the state-machine script")
        return
    result.errors.extend(
        validate_ledger(
            ledger,
            workflow=TESTING_WORKFLOW,
            runtime_id=runtime_id,
            transition_allowed=testing_transition_allowed,
        )
    )
    if not isinstance(ledger, dict):
        return
    current_phase = value_at(parsed, ("current_phase",))
    result.require(
        ledger.get("current_stage") == TESTING_PHASE_TO_STAGE.get(current_phase),
        "Testing workflow stage does not match test-runtime-state.current_phase",
    )
    if value_at(parsed, ("active_release_handoff", "status")) == "current":
        result.require(
            ledger.get("current_stage") == "release_handoff",
            "a current Release Handoff requires the forward workflow to reach release_handoff",
        )
    history = ledger.get("history")
    if isinstance(history, list) and history and isinstance(history[-1], dict):
        last_event = history[-1]
        current_digest = str(
            identity(parsed, ("current_deployment_revision",)).get(
                "identity_digest", ""
            )
        )
        result.require(
            last_event.get("deployment_identity_digest") == current_digest,
            "Testing workflow is not bound to the current deployment identity; record a forward deployment cycle",
        )


def validate_runtime(
    runtime_directory: Path,
    expect_final: bool = False,
    require_workflow: bool = True,
) -> Result:
    result = Result()
    state_path = runtime_directory / "test-runtime-state.md"
    state_text = read(state_path, result)
    if not state_text:
        return result
    parsed = entries(state_text)
    for path, lines in duplicate_paths(parsed):
        result.errors.append(f"duplicate test runtime key {'.'.join(path)} at lines {lines}")

    intake_prefix = ("intake_binding",)
    required_intake = (
        "current_test_epoch",
        "writeback_target",
        "planning_handoff_ref",
        "planning_baseline_revision",
        "long_testing_handoff_ref",
        "long_runtime_epoch",
        "required_validation_matrix_ref",
        "required_validation_matrix_revision",
        "required_validation_gate_result",
        "intake_verified_at",
    )
    for field_name in required_intake:
        result.require(
            has_concrete(value_at(parsed, intake_prefix + (field_name,))),
            f"intake_binding.{field_name} must be concrete",
        )
    result.require(
        value_at(parsed, intake_prefix + ("required_validation_gate_result",)) == "passed",
        "Testing intake requires required_validation_gate_result: passed",
    )
    writeback_ref = value_at(parsed, intake_prefix + ("writeback_target",))
    writeback_candidates = {
        path for path in (
            (runtime_directory / writeback_ref).resolve(),
            (Path.cwd() / writeback_ref).resolve(),
            (runtime_directory.parent / writeback_ref).resolve(),
        )
    } if has_concrete(writeback_ref) else set()
    result.require(runtime_directory.resolve() in writeback_candidates, "intake_binding.writeback_target does not resolve to this Testing Runtime directory")
    planning = planning_contracts(runtime_directory, parsed, result)
    validate_long_intake(runtime_directory, parsed, planning, result)
    result.require(
        has_concrete(value_at(parsed, ("business_journey_matrix_ref",)))
        and has_concrete(value_at(parsed, ("business_journey_matrix_revision",))),
        "current business journey matrix ref and revision are required",
    )

    current_identity = identity(parsed, ("current_deployment_revision",))
    validate_identity(current_identity, "current_deployment_revision", result)

    reconciliation_prefix = ("deployment_revision_reconciliation",)
    reconciliation_status = value_at(parsed, reconciliation_prefix + ("status",))
    overall_status = value_at(parsed, ("overall_status",))
    result.require(
        reconciliation_status in {"not_required", "in_progress", "blocked", "completed"},
        "deployment_revision_reconciliation.status is invalid",
    )
    if reconciliation_status in {"in_progress", "blocked"}:
        result.require(overall_status == "blocked", "active deployment reconciliation requires overall_status: blocked")
        result.require(
            has_concrete(value_at(parsed, reconciliation_prefix + ("transition_id",))),
            "active deployment reconciliation requires transition_id",
        )
        result.require(
            value_at(parsed, ("active_release_handoff", "status")) != "current",
            "active deployment reconciliation may not retain a current release handoff",
        )
    if reconciliation_status in {"in_progress", "blocked", "completed"}:
        transition_id = value_at(parsed, reconciliation_prefix + ("transition_id",))
        result.require(has_concrete(transition_id), "deployment reconciliation requires transition_id")
        from_identity = identity(parsed, reconciliation_prefix + ("from_identity",))
        candidate_identity = identity(parsed, reconciliation_prefix + ("candidate_identity",))
        validate_identity(from_identity, "deployment_revision_reconciliation.from_identity", result)
        validate_identity(candidate_identity, "deployment_revision_reconciliation.candidate_identity", result)
        result.require(
            value_at(parsed, reconciliation_prefix + ("from_identity_digest",))
            == str(from_identity["identity_digest"]),
            "deployment reconciliation from identity digest mismatch",
        )
        result.require(
            value_at(parsed, reconciliation_prefix + ("candidate_identity_digest",))
            == str(candidate_identity["identity_digest"]),
            "deployment reconciliation candidate identity digest mismatch",
        )
        result.require(from_identity != candidate_identity, "deployment reconciliation identities must describe a real change")
        result.require(has_concrete(value_at(parsed, reconciliation_prefix + ("started_at",))), "deployment reconciliation requires started_at")
    if reconciliation_status == "completed":
        candidate_identity = identity(parsed, reconciliation_prefix + ("candidate_identity",))
        result.require(
            value_at(parsed, reconciliation_prefix + ("candidate_identity_digest",))
            == str(current_identity["identity_digest"]),
            "completed deployment reconciliation candidate digest mismatch",
        )
        result.require(
            has_concrete(value_at(parsed, reconciliation_prefix + ("completed_at",))),
            "completed deployment reconciliation requires completed_at",
        )
        result.require(candidate_identity == current_identity, "completed deployment reconciliation candidate identity does not match current identity")
        events_text = read(runtime_directory / "test-execution-events.md", result)
        event_records = anchored_records(events_text, "event_type") if events_text else []
        transition_id = value_at(parsed, reconciliation_prefix + ("transition_id",))
        matching_events = {
            value_at(event_parsed, event_prefix + ("event_type",))
            for event_parsed, event_prefix in event_records
            if value_at(event_parsed, event_prefix + ("transition_id",)) == transition_id
        }
        result.require(
            {"deployment_revision_reconciliation_started", "deployment_revision_reconciliation_completed"}
            <= matching_events,
            "completed deployment reconciliation lacks durable start/completion events",
        )
        evidence_path = runtime_directory / "test-evidence-index.md"
        if evidence_path.is_file():
            evidence_text = read(evidence_path, result)
            evidence = evidence_records(evidence_text, result) if evidence_text else {}
            transition_id = value_at(parsed, reconciliation_prefix + ("transition_id",))
            from_identity = identity(parsed, reconciliation_prefix + ("from_identity",))
            old_revision = str(from_identity.get("revision", ""))
            old_environment = str(from_identity.get("target_environment", ""))
            declared_invalidated = set(
                list_at(parsed, reconciliation_prefix + ("invalidated_evidence_refs",))
            )
            declared_removed = set(
                list_at(parsed, reconciliation_prefix + ("removed_result_refs",))
            )
            invalidated_by_transition: set[str] = set()
            invalidated_item_ids: set[str] = set()
            for evidence_id, (evidence_parsed, evidence_prefix) in evidence.items():
                evidence_revision = value_at(
                    evidence_parsed, evidence_prefix + ("revision",)
                )
                evidence_environment = value_at(
                    evidence_parsed, evidence_prefix + ("target_environment",)
                )
                if evidence_revision != old_revision or evidence_environment != old_environment:
                    continue
                valid = value_at(evidence_parsed, evidence_prefix + ("valid",)).lower()
                invalidated_by = value_at(
                    evidence_parsed, evidence_prefix + ("invalidated_by",)
                )
                result.require(
                    valid == "false",
                    f"{evidence_id}: evidence from the prior deployment identity remains valid",
                )
                if invalidated_by == transition_id:
                    invalidated_by_transition.add(evidence_id)
                    invalidated_item_ids.add(
                        value_at(evidence_parsed, evidence_prefix + ("item_id",))
                    )
            result.require(
                declared_invalidated == invalidated_by_transition,
                "deployment reconciliation invalidated_evidence_refs do not reconcile",
            )
            result.require(
                invalidated_item_ids <= declared_removed,
                "deployment reconciliation removed_result_refs omit invalidated deployment results",
            )
            if invalidated_by_transition:
                result.require(
                    bool(list_at(parsed, reconciliation_prefix + ("opened_gap_refs",))),
                    "deployment reconciliation must record reopened coverage gaps",
                )
    if reconciliation_status == "not_required":
        result.require(
            value_at(parsed, reconciliation_prefix + ("transition_id",)) == "not_applicable"
            and value_at(parsed, reconciliation_prefix + ("from_identity",)) == "not_applicable"
            and value_at(parsed, reconciliation_prefix + ("candidate_identity",)) == "not_applicable",
            "not-required deployment reconciliation fields are inconsistent",
        )
    if current_identity["status"] == "unknown":
        result.require(overall_status == "blocked", "unknown deployment identity requires overall_status: blocked")

    validate_release_handoff(runtime_directory, state_text, parsed, current_identity, planning, result)
    if expect_final or value_at(parsed, ("active_release_handoff", "status")) == "current":
        result.require(
            reconciliation_status not in {"in_progress", "blocked"},
            "final closure requires deployment reconciliation to be settled",
        )
        validate_final_closure(runtime_directory, parsed, current_identity, planning, result)
    if require_workflow:
        validate_testing_workflow(runtime_directory, parsed, result)
    return result


def validate_testing_stage_gate(runtime_directory: Path, target: str) -> Result:
    if target == "intake":
        result = Result()
        state_text = read(runtime_directory / "test-runtime-state.md", result)
        parsed = entries(state_text) if state_text else []
        for path, lines in duplicate_paths(parsed):
            result.errors.append(
                f"duplicate test runtime key {'.'.join(path)} at lines {lines}"
            )
        intake = ("intake_binding",)
        for field_name in (
            "current_test_epoch",
            "writeback_target",
            "planning_handoff_ref",
            "planning_baseline_revision",
            "long_testing_handoff_ref",
            "long_runtime_epoch",
            "required_validation_matrix_ref",
            "required_validation_matrix_revision",
            "required_validation_gate_result",
            "intake_verified_at",
        ):
            result.require(
                has_concrete(value_at(parsed, intake + (field_name,))),
                f"intake_binding.{field_name} must be concrete",
            )
        result.require(
            value_at(parsed, intake + ("required_validation_gate_result",))
            == "passed",
            "Testing intake requires required_validation_gate_result: passed",
        )
        writeback_ref = value_at(parsed, intake + ("writeback_target",))
        writeback_candidates = {
            path
            for path in (
                (runtime_directory / writeback_ref).resolve(),
                (Path.cwd() / writeback_ref).resolve(),
                (runtime_directory.parent / writeback_ref).resolve(),
            )
        } if has_concrete(writeback_ref) else set()
        result.require(
            runtime_directory.resolve() in writeback_candidates,
            "intake_binding.writeback_target does not resolve to this Testing Runtime directory",
        )
        planning = planning_contracts(runtime_directory, parsed, result)
        validate_long_intake(runtime_directory, parsed, planning, result)
        return result
    result = validate_runtime(
        runtime_directory,
        expect_final=target == "release_handoff",
        require_workflow=False,
    )
    state_text = read(runtime_directory / "test-runtime-state.md", result)
    parsed = entries(state_text) if state_text else []
    if target == "local_testing":
        ledger = read_ledger(runtime_directory)
        if isinstance(ledger, dict) and ledger.get("current_stage") == "release_handoff":
            result.require(
                value_at(parsed, ("active_release_handoff", "status"))
                == "invalidated",
                "a release-to-local retest cycle requires the prior Release Handoff to be invalidated first",
            )
    if target == "cloud_testing":
        current_identity = identity(parsed, ("current_deployment_revision",))
        result.require(
            current_identity.get("status") == "known",
            "cloud_testing requires a known current deployment identity",
        )
        result.require(
            value_at(parsed, ("deployment_revision_reconciliation", "status"))
            not in {"in_progress", "blocked"},
            "cloud_testing requires deployment reconciliation to be settled",
        )
        ledger = read_ledger(runtime_directory)
        if isinstance(ledger, dict):
            history = ledger.get("history")
            if isinstance(history, list) and history and isinstance(history[-1], dict):
                previous_digest = history[-1].get("deployment_identity_digest")
                current_digest = current_identity.get("identity_digest")
                if previous_digest not in {None, "not_applicable", current_digest}:
                    result.require(
                        value_at(
                            parsed,
                            ("deployment_revision_reconciliation", "status"),
                        )
                        == "completed",
                        "a changed deployment identity requires completed reconciliation before a new cloud cycle",
                    )
    if target == "release_handoff":
        result.require(
            value_at(parsed, ("active_release_handoff", "status")) == "current",
            "release_handoff stage requires a current Release Handoff snapshot",
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("runtime_directory", type=Path)
    parser.add_argument("--expect-final", action="store_true")
    parser.add_argument("--print-release-snapshot-digest", action="store_true")
    parser.add_argument(
        "--advance-workflow",
        choices=("intake", "local_testing", "cloud_testing", "release_handoff"),
    )
    parser.add_argument(
        "--cycle-kind", choices=("initial", "retest", "deployment_revision"), default="initial"
    )
    parser.add_argument("--new-cycle", action="store_true")
    args = parser.parse_args()
    if args.print_release_snapshot_digest:
        result = Result()
        state_text = read(args.runtime_directory / "test-runtime-state.md", result)
        parsed = entries(state_text) if state_text else []
        snapshot_ref = value_at(parsed, ("active_release_handoff", "snapshot_ref"))
        snapshot_path = resolve_runtime_ref(
            args.runtime_directory.resolve(), snapshot_ref, result,
            "active_release_handoff.snapshot_ref"
        )
        if snapshot_path is not None:
            release_text = read(snapshot_path, result)
        else:
            release_text = ""
        if result.errors:
            for error in result.errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(canonical_release_snapshot_digest(entries(release_text)))
        return 0
    if args.advance_workflow:
        result = validate_testing_stage_gate(args.runtime_directory, args.advance_workflow)
        if result.errors:
            print("Testing Runtime transition blocked:", file=sys.stderr)
            for error in result.errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        state_text = (args.runtime_directory / "test-runtime-state.md").read_text(
            encoding="utf-8"
        )
        runtime_id = value_at(entries(state_text), ("intake_binding", "current_test_epoch"))
        state_entries = entries(state_text)
        deployment_digest = str(
            identity(state_entries, ("current_deployment_revision",)).get(
                "identity_digest", "not_applicable"
            )
        )
        try:
            ledger = advance_ledger(
                args.runtime_directory.resolve(),
                workflow=TESTING_WORKFLOW,
                runtime_id=runtime_id,
                to_stage=args.advance_workflow,
                cycle_kind=args.cycle_kind,
                start_new_cycle=args.new_cycle,
                event_metadata={"deployment_identity_digest": deployment_digest},
                transition_allowed=testing_transition_allowed,
            )
        except ValueError as error:
            print(f"Testing Runtime transition blocked: {error}", file=sys.stderr)
            return 1
        print(
            f"Testing workflow advanced to {ledger['current_stage']} "
            f"(cycle {ledger['current_cycle']})."
        )
        return 0
    result = validate_runtime(args.runtime_directory, expect_final=args.expect_final)
    if result.errors:
        print("Testing Runtime validation failed:", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    state_text = (args.runtime_directory / "test-runtime-state.md").read_text(
        encoding="utf-8"
    )
    state_entries = entries(state_text)
    release_status = value_at(state_entries, ("active_release_handoff", "status"))
    release_readiness = "not_generated"
    if release_status == "current":
        release_path = resolve_runtime_ref(
            args.runtime_directory.resolve(),
            value_at(state_entries, ("active_release_handoff", "snapshot_ref")),
            Result(),
        )
        if release_path is not None and release_path.is_file():
            release_readiness = value_at(entries(release_path.read_text(encoding="utf-8")), ("release_readiness_status",)) or "unknown"
    elif release_status == "invalidated":
        release_readiness = "invalidated"
    print(
        "Testing Runtime contract: valid; "
        f"release readiness: {release_readiness}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

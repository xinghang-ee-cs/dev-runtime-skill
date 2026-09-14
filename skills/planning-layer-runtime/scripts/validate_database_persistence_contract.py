#!/usr/bin/env python3
"""Validate the database and persistence decision contract in planning document 09."""

from __future__ import annotations

import argparse
import collections
import ipaddress
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


CONTRACT_START = re.compile(r"(?m)^\s*database_persistence_contract:\s*$")
SCALAR_PATTERN = r"(?m)^\s*{key}:\s*([^#\n]+?)\s*$"
PLACEHOLDER_PATTERN = re.compile(
    r"<[^>\n]+>|\b(?:TODO|TBD)\b|待补|待确认", re.IGNORECASE
)
MAPPING_KEY_PATTERN = re.compile(r"^(\s*)([a-z_][a-z0-9_]*):(?:\s*(.*))?$", re.I)
LIST_MAPPING_KEY_PATTERN = re.compile(
    r"^(\s*)-\s+([a-z_][a-z0-9_]*):(?:\s*(.*))?$", re.I
)
CREDENTIAL_URI_PATTERN = re.compile(
    r"(?i)\b[a-z][a-z0-9+.-]*:\/\/[^\s/:@]+:[^\s@]+@"
)
ASSIGNMENT_PATTERN = re.compile(
    r"(?i)^\s*(?:-\s*)?([a-z_][a-z0-9_-]*)\s*[:=]\s*(.*?)\s*$"
)
CONNECTION_URI_PATTERN = re.compile(
    r"(?i)\b(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis|rediss|"
    r"amqp|amqps|jdbc|sqlserver|oracle|cockroachdb):\/\/\S+"
)
HOST_TOKEN_PATTERN = re.compile(
    r"(?i)(?<![a-z0-9_-])(?:localhost|[a-z0-9_-]+\.(?:internal|local))(?![a-z0-9_-])"
)
IPV4_PATTERN = re.compile(
    r"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])"
)
SAFE_SENSITIVE_VALUES = {"", "not_applicable", "none", "null", "[]", "{}"}
SAFE_SENSITIVE_PLACEHOLDERS = {
    "<redacted>",
    "<secret_ref>",
    "[redacted]",
    "[secret_ref]",
    "{secret_ref}",
}
SENSITIVE_KEY_PATTERN = re.compile(
    r"(?i)(?:"
    r"(?:^|_)(?:token|password|passwd|pwd|cookie|credentials?|dsn)$|"
    r"^(?:authorization|jwt|database_url|connection_string|session|session_id)$|"
    r"^(?:api|access|private|ssh|client|signing|webhook|secret)(?:_|-)?(?:key|secret)$|"
    r"^secret(?:_|-)?access(?:_|-)?key$"
    r")"
)
UNKNOWN_VALUES = {"unknown", "未知"}
PHYSICAL_NAME_FORBIDDEN = re.compile(
    r"(?i)(?:phase|sprint|iteration)[_-]*\d+|第?\d+[期阶]|(?:迭代|期次|阶段)[_-]*\d+"
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


def mapping_entries(block: str) -> list[tuple[tuple[str, ...], str, int]]:
    """Return indentation-aware paths, scalar text, and line numbers.

    List items receive a synthetic index so repeated field names in different items
    remain legal while duplicate keys inside one item are still rejected.
    """
    entries: list[tuple[tuple[str, ...], str, int]] = []
    stack: list[tuple[int, str]] = []
    list_item_counts: collections.Counter[tuple[str, ...]] = collections.Counter()
    for line_number, raw_line in enumerate(block.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        list_match = LIST_MAPPING_KEY_PATTERN.match(raw_line)
        if list_match:
            indent = len(list_match.group(1))
            while stack and indent <= stack[-1][0]:
                stack.pop()
            parent = tuple(parent_key for _, parent_key in stack)
            item_index = list_item_counts[parent]
            list_item_counts[parent] += 1
            item_key = f"[{item_index}]"
            stack.append((indent, item_key))
            key = list_match.group(2)
            value = (list_match.group(3) or "").strip()
            path = parent + (item_key, key)
            entries.append((path, value, line_number))
            if not value:
                stack.append((indent + 1, key))
            continue
        match = MAPPING_KEY_PATTERN.match(raw_line)
        if not match:
            continue
        indent = len(match.group(1))
        key = match.group(2)
        while stack and indent <= stack[-1][0]:
            stack.pop()
        path = tuple(parent_key for _, parent_key in stack) + (key,)
        value = (match.group(3) or "").strip()
        entries.append((path, value, line_number))
        if not value:
            stack.append((indent, key))
    return entries


def mapping_paths(block: str) -> set[tuple[str, ...]]:
    return {path for path, _, _ in mapping_entries(block)}


def mapping_value(block: str, path: tuple[str, ...]) -> str:
    values = [value for entry_path, value, _ in mapping_entries(block) if entry_path == path]
    if not values:
        return ""
    return values[0].strip().strip("'\"")


def indexed_prefixes(
    entries: list[tuple[tuple[str, ...], str, int]],
    list_path: tuple[str, ...],
) -> list[tuple[str, ...]]:
    prefixes = {
        list_path + (path[len(list_path)],)
        for path, _, _ in entries
        if len(path) > len(list_path)
        and path[: len(list_path)] == list_path
        and path[len(list_path)].startswith("[")
    }
    return sorted(prefixes, key=lambda prefix: int(prefix[-1][1:-1]))


def entry_value(
    entries: list[tuple[tuple[str, ...], str, int]], path: tuple[str, ...]
) -> str:
    for entry_path, value, _ in entries:
        if entry_path == path:
            return value.strip().strip("'\"")
    return ""


def inline_list_values_at(
    entries: list[tuple[tuple[str, ...], str, int]], path: tuple[str, ...]
) -> list[str] | None:
    value = entry_value(entries, path).strip()
    if not (value.startswith("[") and value.endswith("]")):
        return None
    body = value[1:-1].strip()
    if not body:
        return []
    parts: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    for index, character in enumerate(body):
        if character in {"'", '"'}:
            quote = None if quote == character else character if quote is None else quote
        elif quote is None and character in "([{":
            depth += 1
        elif quote is None and character in ")]}" and depth:
            depth -= 1
        elif quote is None and depth == 0 and character == ",":
            part = body[start:index].strip().strip("'\"")
            if part:
                parts.append(part)
            start = index + 1
    final = body[start:].strip().strip("'\"")
    if final:
        parts.append(final)
    return parts


def duplicate_mapping_paths(block: str) -> list[tuple[tuple[str, ...], list[int]]]:
    lines_by_path: dict[tuple[str, ...], list[int]] = collections.defaultdict(list)
    for path, _, line_number in mapping_entries(block):
        lines_by_path[path].append(line_number)
    return [
        (path, line_numbers)
        for path, line_numbers in lines_by_path.items()
        if len(line_numbers) > 1
    ]


def direct_mapping_keys(block: str) -> set[str]:
    """Return keys at the shallowest mapping level in an extracted list item."""
    matches = [
        match
        for line in block.splitlines()
        if (match := MAPPING_KEY_PATTERN.match(line)) is not None
    ]
    if not matches:
        return set()
    shallowest = min(len(match.group(1)) for match in matches)
    return {
        match.group(2)
        for match in matches
        if len(match.group(1)) == shallowest
    }


def is_sensitive_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return SENSITIVE_KEY_PATTERN.search(normalized) is not None


def contains_forbidden_network_or_credential_data(block: str) -> bool:
    if CREDENTIAL_URI_PATTERN.search(block) or CONNECTION_URI_PATTERN.search(block):
        return True
    if HOST_TOKEN_PATTERN.search(block):
        return True
    for candidate in IPV4_PATTERN.findall(block):
        try:
            address = ipaddress.ip_address(candidate)
        except ValueError:
            continue
        if not address.is_global:
            return True
    for line in block.splitlines():
        match = ASSIGNMENT_PATTERN.match(line)
        if not match or not is_sensitive_key(match.group(1)):
            continue
        value = match.group(2).strip().strip("'\"")
        if value.lower() in SAFE_SENSITIVE_VALUES:
            continue
        if value.lower() in SAFE_SENSITIVE_PLACEHOLDERS:
            continue
        return True
    return False


def inline_or_block_list_values(block: str, key: str) -> list[str]:
    inline = scalar(block, key)
    if inline.startswith("[") and inline.endswith("]"):
        body = inline[1:-1].strip()
        if not body:
            return []
        return [part.strip().strip("'\"") for part in body.split(",") if part.strip()]
    match = re.search(
        rf"(?ms)^\s*{re.escape(key)}:\s*$"
        rf"(.*?)(?=^\s*[a-z_]+:\s*|\Z)",
        block,
    )
    if not match:
        return []
    return [
        item.strip().strip("'\"")
        for item in re.findall(r"(?m)^\s*-\s*([^#\n]+?)\s*$", match.group(1))
    ]


def list_has_item(block: str, key: str) -> bool:
    match = re.search(
        rf"(?ms)^\s*{re.escape(key)}:\s*(?:\[\s*\]|$)(.*?)(?=^\s*[a-z_]+:\s*|\Z)",
        block,
    )
    if not match:
        inline = scalar(block, key)
        return bool(inline and inline not in {"[]", "none", "not_applicable"})
    return re.search(r"(?m)^\s*-\s*\S+", match.group(1)) is not None


def list_mapping_items(block: str, key: str) -> list[str]:
    """Extract mapping items from one indented YAML-like list without parsing secrets."""
    lines = block.splitlines()
    start = -1
    base_indent = 0
    for index, line in enumerate(lines):
        match = re.match(rf"^(\s*){re.escape(key)}:\s*(.*)$", line)
        if match:
            if match.group(2).strip() not in {"", "[]"}:
                return []
            start = index + 1
            base_indent = len(match.group(1))
            break
    if start < 0:
        return []

    section: list[str] = []
    for line in lines[start:]:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            if indent <= base_indent:
                break
        section.append(line)

    item_starts = [
        index
        for index, line in enumerate(section)
        if re.match(r"^\s*-\s+[a-z_]+:\s*", line)
    ]
    items: list[str] = []
    for offset, item_start in enumerate(item_starts):
        item_end = (
            item_starts[offset + 1]
            if offset + 1 < len(item_starts)
            else len(section)
        )
        item = "\n".join(section[item_start:item_end])
        items.append(re.sub(r"(?m)^(\s*)-\s+", r"\1  ", item, count=1))
    return items


def validate_contract(path: Path, allow_blocked: bool) -> ValidationResult:
    result = ValidationResult()
    text = read_text(path, result)
    if not text:
        return result

    block = extract_contract(text)
    result.require(bool(block), "missing database_persistence_contract block")
    if not block:
        return result

    root = ("database_persistence_contract",)
    for duplicate_path, line_numbers in duplicate_mapping_paths(block):
        display_path = ".".join(
            segment for segment in duplicate_path[1:] if not segment.startswith("[")
        )
        result.errors.append(
            f"duplicate mapping key '{display_path}' at contract lines "
            + ", ".join(str(line_number) for line_number in line_numbers)
        )

    required_paths = [
        root + ("contract_version",),
        root + ("applicable",),
        root + ("decision_status",),
        root + ("decision_source",),
        root + ("current_baseline",),
        root + ("current_baseline", "evidence_status"),
        root + ("current_baseline", "existing_database"),
        root + ("current_baseline", "engine_and_version"),
        root + ("current_baseline", "location_mode"),
        root + ("current_baseline", "evidence_refs"),
        root + ("reuse_decision",),
        root + ("target_engine_and_version",),
        root + ("environment_topology",),
        root + ("environment_topology", "local_development"),
        root + ("environment_topology", "test"),
        root + ("environment_topology", "staging"),
        root + ("environment_topology", "production"),
        root + ("remote_database",),
        root + ("remote_database", "availability"),
        root + ("remote_database", "purpose"),
        root + ("remote_database", "owner_or_provider"),
        root + ("remote_database", "provision_or_access_evidence"),
        root + ("existing_assets",),
        root + ("existing_assets", "schema_or_migrations"),
        root + ("existing_assets", "sanitized_data_or_backup"),
        root + ("existing_assets", "access_mode"),
        root + ("migration",),
        root + ("migration", "required"),
        root + ("migration", "source_and_scope"),
        root + ("migration", "compatibility_strategy"),
        root + ("migration", "rollback_boundary"),
        root + ("data_governance",),
        root + ("data_governance", "environment_isolation"),
        root + ("data_governance", "backup_restore"),
        root + ("data_governance", "retention_deletion"),
        root + ("data_governance", "sensitive_data"),
        root + ("credential_boundary",),
        root + ("blocking_items",),
        root + ("delegation_boundary",),
        root + ("verification_requirements",),
    ]
    entries = mapping_entries(block)
    present_paths = {path for path, _, _ in entries}
    for path in required_paths:
        result.require(
            path in present_paths,
            f"missing field '{'.'.join(path[1:])}'",
        )

    contract_version = mapping_value(block, root + ("contract_version",))
    result.require(
        contract_version in {"database-persistence/v1", "database-persistence/v2"},
        "contract_version must be database-persistence/v1 or database-persistence/v2",
    )
    if contract_version == "database-persistence/v2":
        for field_path in (
            root + ("physical_data_design",),
            root + ("physical_data_design", "design_mode"),
            root + ("physical_data_design", "storage_model"),
            root + ("physical_data_design", "schema_source_refs"),
            root + ("physical_data_design", "prohibited_extra_storage_units"),
            root + ("physical_data_design", "storage_units"),
            root + ("execution_prerequisites",),
        ):
            result.require(
                field_path in present_paths,
                f"database-persistence/v2 requires field '{'.'.join(field_path[1:])}'",
            )
    applicable = mapping_value(block, root + ("applicable",)).lower()
    result.require(applicable in {"true", "false"}, "applicable must be true or false")

    status = mapping_value(block, root + ("decision_status",))
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

    delegation = mapping_value(block, root + ("delegation_boundary",))
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

    physical_root = root + ("physical_data_design",)
    design_mode = entry_value(entries, physical_root + ("design_mode",))
    storage_model = entry_value(entries, physical_root + ("storage_model",))
    schema_source_refs = inline_list_values_at(
        entries, physical_root + ("schema_source_refs",)
    )
    storage_unit_prefixes = indexed_prefixes(
        entries, physical_root + ("storage_units",)
    )
    if contract_version == "database-persistence/v2":
        result.require(
            design_mode
            in {
                "reuse_existing_unchanged",
                "modify_existing",
                "create_new",
                "not_applicable",
            },
            "physical_data_design.design_mode is invalid",
        )
        result.require(
            storage_model
            in {
                "relational",
                "document",
                "key_value",
                "file_or_object",
                "external_managed",
                "not_applicable",
            },
            "physical_data_design.storage_model is invalid",
        )
        result.require(
            schema_source_refs is not None,
            "physical_data_design.schema_source_refs must be an inline YAML list",
        )
        result.require(
            entry_value(
                entries,
                physical_root + ("prohibited_extra_storage_units",),
            ).lower()
            == "true",
            "physical_data_design.prohibited_extra_storage_units must be true",
        )
        if applicable == "false":
            result.require(
                design_mode == "not_applicable" and storage_model == "not_applicable",
                "applicable: false requires a not_applicable physical data design",
            )
        if applicable == "true" and status in {"confirmed", "explicitly_delegated"}:
            result.require(
                design_mode != "not_applicable" and storage_model != "not_applicable",
                "applicable ready contract requires a concrete physical data design",
            )
            if design_mode == "reuse_existing_unchanged":
                result.require(
                    bool(schema_source_refs),
                    "reuse_existing_unchanged requires at least one schema_source_refs entry",
                )
                result.require(
                    not storage_unit_prefixes,
                    "reuse_existing_unchanged must use schema_source_refs instead of redefining storage_units",
                )
            elif design_mode in {"modify_existing", "create_new"}:
                result.require(
                    bool(storage_unit_prefixes),
                    f"{design_mode} requires at least one physical storage unit",
                )

    unit_fields = (
        "storage_unit_id",
        "unit_kind",
        "physical_name",
        "change_action",
        "business_object_refs",
        "fields",
        "identity_key",
        "unique_constraints",
        "indexes",
        "relations",
        "tenant_and_access_boundary",
        "lifecycle_and_deletion",
        "migration_and_backfill",
    )
    unit_ids: list[str] = []
    physical_names: list[str] = []
    unit_field_names: dict[str, set[str]] = {}
    pending_relations: list[tuple[int, int, str, list[str], list[str]]] = []
    for unit_index, unit_prefix in enumerate(storage_unit_prefixes, start=1):
        for field_name in unit_fields:
            result.require(
                unit_prefix + (field_name,) in present_paths,
                f"physical storage unit {unit_index} missing field '{field_name}'",
            )
        unit_id = entry_value(entries, unit_prefix + ("storage_unit_id",))
        physical_name = entry_value(entries, unit_prefix + ("physical_name",))
        unit_kind = entry_value(entries, unit_prefix + ("unit_kind",))
        change_action = entry_value(entries, unit_prefix + ("change_action",))
        if unit_id:
            unit_ids.append(unit_id)
        if physical_name:
            physical_names.append(physical_name)
        result.require(bool(unit_id), f"physical storage unit {unit_index} requires storage_unit_id")
        result.require(bool(physical_name), f"physical storage unit {unit_index} requires physical_name")
        result.require(
            not PHYSICAL_NAME_FORBIDDEN.search(physical_name),
            f"physical storage unit {unit_index} physical_name may not use Planning or phase naming",
        )
        result.require(
            unit_kind in {"table", "collection", "keyspace", "object_prefix", "external"},
            f"physical storage unit {unit_index} has invalid unit_kind",
        )
        result.require(
            change_action in {"reuse", "create", "alter", "retire"},
            f"physical storage unit {unit_index} has invalid change_action",
        )
        for concrete_field in (
            "tenant_and_access_boundary",
            "lifecycle_and_deletion",
            "migration_and_backfill",
        ):
            result.require(
                bool(entry_value(entries, unit_prefix + (concrete_field,))),
                f"physical storage unit {unit_index} requires concrete {concrete_field}",
            )
        for list_name in (
            "business_object_refs",
            "identity_key",
            "unique_constraints",
            "indexes",
        ):
            result.require(
                inline_list_values_at(entries, unit_prefix + (list_name,)) is not None,
                f"physical storage unit {unit_index} {list_name} must be an inline YAML list",
            )
        business_refs = inline_list_values_at(
            entries, unit_prefix + ("business_object_refs",)
        )
        identity_key = inline_list_values_at(entries, unit_prefix + ("identity_key",))
        if change_action in {"create", "alter"}:
            result.require(
                bool(business_refs),
                f"physical storage unit {unit_index} requires business_object_refs",
            )

        field_prefixes = indexed_prefixes(entries, unit_prefix + ("fields",))
        if unit_kind in {"table", "collection", "keyspace"} and change_action in {
            "create",
            "alter",
        }:
            result.require(
                bool(field_prefixes),
                f"physical storage unit {unit_index} requires concrete fields",
            )
        field_names: list[str] = []
        for field_index, field_prefix in enumerate(field_prefixes, start=1):
            for field_name in (
                "physical_name",
                "storage_type",
                "nullable",
                "default_or_generation",
                "business_meaning",
                "fact_or_state_refs",
                "sensitive_classification",
            ):
                result.require(
                    field_prefix + (field_name,) in present_paths,
                    f"physical storage unit {unit_index} field {field_index} missing '{field_name}'",
                )
            field_name = entry_value(entries, field_prefix + ("physical_name",))
            if field_name:
                field_names.append(field_name)
            result.require(
                bool(field_name),
                f"physical storage unit {unit_index} field {field_index} requires physical_name",
            )
            result.require(
                not PHYSICAL_NAME_FORBIDDEN.search(field_name),
                f"physical storage unit {unit_index} field {field_index} may not use phase naming",
            )
            for concrete_field in (
                "storage_type",
                "default_or_generation",
                "business_meaning",
            ):
                result.require(
                    bool(entry_value(entries, field_prefix + (concrete_field,))),
                    f"physical storage unit {unit_index} field {field_index} requires concrete {concrete_field}",
                )
            result.require(
                entry_value(entries, field_prefix + ("nullable",)).lower()
                in {"true", "false"},
                f"physical storage unit {unit_index} field {field_index} nullable must be true or false",
            )
            result.require(
                entry_value(entries, field_prefix + ("sensitive_classification",))
                in {"public", "internal", "personal", "sensitive", "secret_reference"},
                f"physical storage unit {unit_index} field {field_index} has invalid sensitive_classification",
            )
            result.require(
                inline_list_values_at(entries, field_prefix + ("fact_or_state_refs",))
                is not None,
                f"physical storage unit {unit_index} field {field_index} fact_or_state_refs must be an inline YAML list",
            )
        for duplicate_name, count in collections.Counter(field_names).items():
            if count > 1:
                result.errors.append(
                    f"physical storage unit {unit_index} has duplicate field physical_name '{duplicate_name}'"
                )
        if unit_kind in {"table", "collection", "keyspace"} and change_action in {
            "create",
            "alter",
        }:
            result.require(
                bool(identity_key),
                f"physical storage unit {unit_index} requires identity_key",
            )
        for identity_field in identity_key or []:
            result.require(
                identity_field in field_names,
                f"physical storage unit {unit_index} identity_key '{identity_field}' is not a declared field",
            )
        if unit_id:
            unit_field_names[unit_id] = set(field_names)

        relation_prefixes = indexed_prefixes(entries, unit_prefix + ("relations",))
        relation_fields = (
            "target_storage_unit_id",
            "local_fields",
            "target_fields",
            "cardinality",
            "on_delete",
            "on_update",
        )
        for relation_index, relation_prefix in enumerate(relation_prefixes, start=1):
            for field_name in relation_fields:
                result.require(
                    relation_prefix + (field_name,) in present_paths,
                    f"physical storage unit {unit_index} relation {relation_index} missing '{field_name}'",
                )
            for list_name in ("local_fields", "target_fields"):
                result.require(
                    bool(inline_list_values_at(entries, relation_prefix + (list_name,))),
                    f"physical storage unit {unit_index} relation {relation_index} {list_name} must be a non-empty inline YAML list",
                )
            target_id = entry_value(
                entries, relation_prefix + ("target_storage_unit_id",)
            )
            local_fields = inline_list_values_at(
                entries, relation_prefix + ("local_fields",)
            ) or []
            target_fields = inline_list_values_at(
                entries, relation_prefix + ("target_fields",)
            ) or []
            for concrete_field in (
                "target_storage_unit_id",
                "cardinality",
                "on_delete",
                "on_update",
            ):
                result.require(
                    bool(entry_value(entries, relation_prefix + (concrete_field,))),
                    f"physical storage unit {unit_index} relation {relation_index} requires concrete {concrete_field}",
                )
            for local_field in local_fields:
                result.require(
                    local_field in field_names,
                    f"physical storage unit {unit_index} relation {relation_index} local field '{local_field}' is not declared",
                )
            pending_relations.append(
                (unit_index, relation_index, target_id, local_fields, target_fields)
            )

    for duplicate_id, count in collections.Counter(unit_ids).items():
        if count > 1:
            result.errors.append(f"duplicate physical storage_unit_id '{duplicate_id}'")
    for duplicate_name, count in collections.Counter(physical_names).items():
        if count > 1:
            result.errors.append(f"duplicate physical storage unit name '{duplicate_name}'")
    for unit_index, relation_index, target_id, _, target_fields in pending_relations:
        result.require(
            target_id in unit_field_names,
            f"physical storage unit {unit_index} relation {relation_index} target '{target_id}' is not declared",
        )
        for target_field in target_fields:
            result.require(
                target_field in unit_field_names.get(target_id, set()),
                f"physical storage unit {unit_index} relation {relation_index} target field '{target_field}' is not declared",
            )

    prerequisite_items = list_mapping_items(block, "execution_prerequisites")
    if (
        contract_version == "database-persistence/v2"
        and applicable == "true"
        and status in {"confirmed", "explicitly_delegated"}
    ):
        result.require(
            bool(prerequisite_items),
            "applicable confirmed contract requires execution_prerequisites",
        )
    prerequisite_fields = [
        "prerequisite_ref",
        "purpose",
        "responsible_party",
        "earliest_required_stage",
        "provision_channel",
        "safe_verification",
        "secret_handling",
        "covers_contract_paths",
    ]
    prerequisite_refs: list[str] = []
    covered_unknown_paths: set[str] = set()
    for index, item in enumerate(prerequisite_items, start=1):
        item_keys = direct_mapping_keys(item)
        for key in prerequisite_fields:
            result.require(
                key in item_keys,
                f"execution_prerequisites item {index} missing field '{key}'",
            )
        prerequisite_ref = scalar(item, "prerequisite_ref")
        if prerequisite_ref:
            prerequisite_refs.append(prerequisite_ref)
        covered_unknown_paths.update(
            inline_or_block_list_values(item, "covers_contract_paths")
        )
        result.require(
            scalar(item, "responsible_party")
            in {"agent_task", "user", "external_party"},
            f"execution_prerequisites item {index} has invalid responsible_party",
        )
        result.require(
            scalar(item, "earliest_required_stage")
            in {"before_long", "before_cloud_test", "before_release"},
            f"execution_prerequisites item {index} has invalid earliest_required_stage",
        )
        result.require(
            scalar(item, "secret_handling")
            in {"never_in_chat_or_planning_docs", "not_applicable"},
            f"execution_prerequisites item {index} has invalid secret_handling",
        )

    duplicate_refs = sorted(
        prerequisite_ref
        for prerequisite_ref, count in collections.Counter(prerequisite_refs).items()
        if count > 1
    )
    for prerequisite_ref in duplicate_refs:
        result.errors.append(
            f"duplicate execution prerequisite ref '{prerequisite_ref}'"
        )

    unknown_paths = {
        ".".join(segment for segment in path[1:] if not segment.startswith("["))
        for path, value, _ in mapping_entries(block)
        if value.strip().strip("'\"").lower() in UNKNOWN_VALUES
    }
    if contract_version == "database-persistence/v1" and unknown_paths:
        result.errors.append(
            "legacy v1 contract with unknown facts must migrate to v2 and bind each "
            "unknown fact to an execution prerequisite"
        )
    if contract_version == "database-persistence/v2":
        for covered_path in sorted(covered_unknown_paths - unknown_paths):
            result.errors.append(
                f"covers_contract_paths entry '{covered_path}' does not resolve an "
                "unknown contract fact"
            )
        for unknown_path in sorted(unknown_paths - covered_unknown_paths):
            result.errors.append(
                f"unknown fact '{unknown_path}' must be listed in exactly one "
                "execution_prerequisite.covers_contract_paths"
            )
        unknown_path_counts = collections.Counter(
            path
            for item in prerequisite_items
            for path in inline_or_block_list_values(item, "covers_contract_paths")
        )
        for unknown_path in sorted(unknown_paths):
            if unknown_path_counts[unknown_path] > 1:
                result.errors.append(
                    f"unknown fact '{unknown_path}' is covered by more than one "
                    "execution prerequisite"
                )

    result.require(
        not contains_forbidden_network_or_credential_data(block),
        "contract appears to contain a credential, connection string, or private network address",
    )
    credential_boundary = mapping_value(block, root + ("credential_boundary",))
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
    block = extract_contract(args.document.read_text(encoding="utf-8"))
    if scalar(block, "contract_version") == "database-persistence/v1":
        print(
            "Database persistence contract validation passed (legacy v1; migrate to v2 when this contract is next changed)."
        )
    else:
        print("Database persistence contract validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

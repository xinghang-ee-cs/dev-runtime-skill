#!/usr/bin/env python3
"""Validate execution-ready UI/UX planning documents and handoff bindings."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


ID_PATTERN = r"(?:PROMPT-(?:STYLE|PAGE|MODULE|UX)|PAGE|UI-MOD|UX-SCN|ASSET)-[A-Z0-9-]+"
PLACEHOLDER_PATTERN = re.compile(r"<[^>\n]+>|\b(?:TODO|TBD|UNKNOWN)\b|待补|待确认", re.IGNORECASE)


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

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


def extract_yaml_mapping_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*([^#\n]+?)\s*$", text)
    if not match:
        return None
    return match.group(1).strip().strip("'\"")


def extract_indented_mapping_blocks(text: str, key: str) -> list[str]:
    lines = text.splitlines(keepends=True)
    blocks: list[str] = []
    key_pattern = re.compile(rf"^(?P<indent>[ \t]*){re.escape(key)}:\s*(?:#.*)?$")
    for index, line in enumerate(lines):
        match = key_pattern.match(line.rstrip("\r\n"))
        if not match:
            continue
        base_indent = len(match.group("indent").expandtabs(2))
        block_lines = [line]
        for following in lines[index + 1 :]:
            stripped = following.strip()
            if not stripped:
                block_lines.append(following)
                continue
            indent = len(following) - len(following.lstrip(" \t"))
            if indent <= base_indent:
                break
            block_lines.append(following)
        blocks.append("".join(block_lines))
    return blocks


def extract_reference_pairs(text: str, section_key: str) -> dict[str, str]:
    sections = extract_indented_mapping_blocks(text, section_key)
    if not sections:
        return {}
    pairs: dict[str, str] = {}
    current_id: str | None = None
    for line in sections[0].splitlines()[1:]:
        id_match = re.match(rf"^\s*-\s*id:\s*({ID_PATTERN})\s*$", line)
        if id_match:
            current_id = id_match.group(1)
            continue
        revision_match = re.match(r"^\s*revision:\s*([^#\s]+)\s*$", line)
        if current_id and revision_match:
            pairs[current_id] = revision_match.group(1).strip("'\"")
            current_id = None
    return pairs


def carries_exact_reference(text: str, ref_id: str, revision: str) -> bool:
    scalar_ref = re.search(
        rf"(?<![A-Za-z0-9._-]){re.escape(ref_id)}@{re.escape(revision)}(?![A-Za-z0-9._-])",
        text,
    )
    if scalar_ref:
        return True
    return extract_all_reference_pairs(text).get(ref_id) == revision


def contains_reference_id(text: str, ref_id: str) -> bool:
    return re.search(rf"(?<![A-Z0-9-]){re.escape(ref_id)}(?![A-Z0-9-])", text) is not None


def extract_all_reference_pairs(text: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    current_id: str | None = None
    for line in text.splitlines():
        id_match = re.match(rf"^\s*-\s*id:\s*({ID_PATTERN})\s*$", line)
        if id_match:
            current_id = id_match.group(1)
            continue
        revision_match = re.match(r"^\s*revision:\s*([^#\s]+)\s*$", line)
        if current_id and revision_match:
            pairs[current_id] = revision_match.group(1).strip("'\"")
            current_id = None
    return pairs


def extract_heading_blocks(text: str, prefix_pattern: str) -> dict[str, str]:
    heading = re.compile(rf"(?m)^###\s+({prefix_pattern})(?:：|:|\s|$).*$")
    matches = list(heading.finditer(text))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.start()
        next_same = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        next_level = re.search(r"(?m)^##\s+", text[match.end() : next_same])
        end = match.end() + next_level.start() if next_level else next_same
        blocks[match.group(1)] = text[start:end]
    return blocks


def require_fields(block_id: str, block: str, fields: list[str], result: ValidationResult) -> None:
    for key in fields:
        result.require(
            re.search(rf"(?m)^\s*{re.escape(key)}:\s*", block) is not None,
            f"{block_id}: missing field '{key}'",
        )


def manifest_block(text: str) -> str:
    match = re.search(r"(?ms)^\s*design_delivery_manifest:\s*$.*?(?=^```\s*$)", text)
    return match.group(0) if match else ""


def validate_manifest(
    text: str,
    allow_design_ready: bool,
    allow_blocked: bool,
    result: ValidationResult,
) -> tuple[str, set[str], str]:
    block = manifest_block(text)
    result.require(bool(block), "missing design_delivery_manifest YAML block")
    if not block:
        return "", set(), ""

    require_fields(
        "design_delivery_manifest",
        block,
        [
            "contract_version",
            "design_document_path",
            "style_mode",
            "baseline_source",
            "prompt_refs",
            "page_contract_refs",
            "module_contract_refs",
            "interaction_contract_refs",
            "confirmed_asset_refs",
            "consistency_test_refs",
            "unresolved_design_refs",
            "execution_readiness",
        ],
        result,
    )
    result.require(
        "contract_version: ui-ux-execution/v1" in block,
        "design_delivery_manifest: contract_version must be ui-ux-execution/v1",
    )
    readiness = extract_yaml_mapping_value(block, "execution_readiness") or ""
    if allow_blocked:
        result.require(
            readiness in {"design_ready", "execution_ready", "blocked"},
            "execution_readiness must be design_ready, execution_ready, or blocked",
        )
    elif allow_design_ready:
        result.require(
            readiness in {"design_ready", "execution_ready"},
            "execution_readiness must be design_ready or execution_ready",
        )
    else:
        result.require(readiness == "execution_ready", "execution_readiness must be execution_ready")

    if readiness in {"design_ready", "execution_ready"}:
        result.require(
            re.search(r"(?m)^\s*unresolved_design_refs:\s*\[\s*\]\s*$", block) is not None,
            f"{readiness} manifest must have unresolved_design_refs: []",
        )
    if readiness == "blocked":
        blocked_reason = extract_yaml_mapping_value(block, "blocked_reason") or ""
        result.require(bool(blocked_reason), "blocked manifest must include a non-empty blocked_reason")
    return block, set(re.findall(ID_PATTERN, block)), readiness


def validate_prompts(text: str, result: ValidationResult) -> dict[str, str]:
    blocks = extract_heading_blocks(text, r"PROMPT-(?:STYLE|PAGE|MODULE|UX)-[A-Z0-9-]+")
    result.require(bool(blocks), "no PROMPT heading found")
    fields = [
        "prompt_revision",
        "prompt_type",
        "target_tool",
        "language",
        "reference_inputs",
        "output_spec",
        "device",
        "viewport",
        "frame_count",
        "aspect_ratio",
        "resolution",
        "required_constraints",
        "negative_constraints",
        "prompt_body",
    ]
    for block_id, block in blocks.items():
        require_fields(block_id, block, fields, result)
        result.require(
            re.search(r"(?ms)^```prompt\s*\n.+?^```\s*$", block) is not None,
            f"{block_id}: missing non-empty fenced prompt_body",
        )
    return blocks


def validate_page_contracts(text: str, result: ValidationResult) -> dict[str, str]:
    blocks = extract_heading_blocks(text, r"(?:PAGE|UI-MOD)-[A-Z0-9-]+")
    page_blocks = {key: value for key, value in blocks.items() if key.startswith("PAGE-")}
    result.require(bool(page_blocks), "no PAGE implementation contract found")
    fields = [
        "contract_revision",
        "source_prompt_refs",
        "source_asset_refs",
        "design_tokens",
        "layout_contract",
        "responsive_contract",
        "component_contract",
        "state_contract",
        "content_contract",
        "accessibility_contract",
        "motion_feedback_contract",
        "implementation_acceptance",
    ]
    for block_id, block in blocks.items():
        require_fields(block_id, block, fields, result)
    return blocks


def validate_interactions(text: str, result: ValidationResult) -> dict[str, str]:
    blocks = extract_heading_blocks(text, r"UX-SCN-[A-Z0-9-]+")
    result.require(bool(blocks), "no UX-SCN interaction contract found")
    expected_columns = [
        "Step",
        "From UI state",
        "Trigger",
        "Preconditions",
        "Domain/API intent ref",
        "Pending feedback",
        "Success UI state",
        "Failure UI state",
        "Recovery / retry",
        "Cancel / back",
        "Forbidden actions",
        "Visible evidence",
    ]
    for block_id, block in blocks.items():
        require_fields(block_id, block, ["contract_revision"], result)
        header = "| " + " | ".join(expected_columns) + " |"
        result.require(header in block, f"{block_id}: missing deterministic interaction table header")
        table_rows = [line for line in block.splitlines() if line.startswith("|")]
        result.require(len(table_rows) >= 3, f"{block_id}: interaction table has no transition row")
    return blocks


def validate_assets(text: str, manifest: str, result: ValidationResult) -> dict[str, str]:
    blocks = extract_heading_blocks(text, r"ASSET-[A-Z0-9-]+")
    result.require(bool(blocks), "no ASSET contract found")
    confirmed_ids = set(re.findall(r"ASSET-[A-Z0-9-]+", manifest))
    for asset_id in confirmed_ids:
        block = blocks.get(asset_id, "")
        result.require(bool(block), f"manifest references missing asset heading: {asset_id}")
        if not block:
            continue
        require_fields(
            asset_id,
            block,
            [
                "asset_revision",
                "asset_type",
                "asset_status",
                "source",
                "asset_path_or_url",
                "applies_to",
                "covered_states",
                "known_gaps",
                "user_confirmation_ref",
                "confirmed_at",
            ],
            result,
        )
        result.require(
            re.search(r"(?m)^\s*asset_status:\s*visual_confirmed\s*$", block) is not None,
            f"{asset_id}: manifest-confirmed asset must be visual_confirmed",
        )
    return blocks


def validate_coverage_matrix(text: str, expected_refs: dict[str, str], result: ValidationResult) -> None:
    expected = (
        "| FLOW | SCN | MODULE | PAGE / UI-MOD | Prompt ref | UI contract revision | "
        "UX-SCN revision | Confirmed asset ref | TEST ref | Execution readiness |"
    )
    result.require(expected in text, "missing execution-grade UI/UX coverage matrix")
    header_index = text.find(expected)
    if header_index < 0:
        return
    next_section = re.search(r"(?m)^##\s+", text[header_index + len(expected) :])
    matrix_end = header_index + len(expected) + next_section.start() if next_section else len(text)
    matrix = text[header_index:matrix_end]
    for ref_id, revision in sorted(expected_refs.items()):
        result.require(
            ref_id in matrix and revision in matrix,
            f"coverage matrix does not carry exact manifest revision: {ref_id}@{revision}",
        )


def validate_manifest_revisions(
    manifest: str,
    prompt_blocks: dict[str, str],
    page_blocks: dict[str, str],
    interaction_blocks: dict[str, str],
    asset_blocks: dict[str, str],
    result: ValidationResult,
) -> dict[str, str]:
    section_contracts = [
        ("prompt_refs", prompt_blocks, "prompt_revision"),
        ("page_contract_refs", page_blocks, "contract_revision"),
        ("module_contract_refs", page_blocks, "contract_revision"),
        ("interaction_contract_refs", interaction_blocks, "contract_revision"),
        ("confirmed_asset_refs", asset_blocks, "asset_revision"),
    ]
    expected_refs: dict[str, str] = {}
    for section_key, blocks, revision_key in section_contracts:
        section_texts = extract_indented_mapping_blocks(manifest, section_key)
        section_text = section_texts[0] if section_texts else ""
        section_ids = set(re.findall(ID_PATTERN, section_text))
        section_pairs = extract_reference_pairs(manifest, section_key)
        for ref_id in section_ids:
            result.require(ref_id in section_pairs, f"manifest {section_key} missing revision for {ref_id}")
        for ref_id, expected_revision in section_pairs.items():
            contract_block = blocks.get(ref_id, "")
            result.require(bool(contract_block), f"manifest {section_key} references missing contract: {ref_id}")
            actual_revision = extract_yaml_mapping_value(contract_block, revision_key) if contract_block else None
            result.require(
                actual_revision == expected_revision,
                f"manifest {ref_id} revision mismatch: expected {expected_revision}, found {actual_revision or 'missing'}",
            )
            expected_refs[ref_id] = expected_revision
    return expected_refs


def validate_internal_contract_references(
    expected_refs: dict[str, str],
    block_groups: list[dict[str, str]],
    result: ValidationResult,
) -> None:
    for blocks in block_groups:
        for block_id, block in blocks.items():
            for ref_id, revision in expected_refs.items():
                if ref_id == block_id or not contains_reference_id(block, ref_id):
                    continue
                result.require(
                    carries_exact_reference(block, ref_id, revision),
                    f"{block_id}: stale or missing internal reference {ref_id}@{revision}",
                )


def validate_no_placeholders(text: str, allow_blocked: bool, result: ValidationResult) -> None:
    if allow_blocked:
        return
    for match in PLACEHOLDER_PATTERN.finditer(text):
        value = match.group(0)
        if re.fullmatch(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s+[^>]*)?>", value):
            continue
        line = text.count("\n", 0, match.start()) + 1
        result.errors.append(f"execution-ready document contains placeholder '{value}' at line {line}")
        return


def validate_handoff(
    handoff_text: str,
    manifest: str,
    expected_refs: dict[str, str],
    manifest_test_ids: set[str],
    result: ValidationResult,
) -> None:
    bindings = extract_indented_mapping_blocks(handoff_text, "frontend_experience_binding")
    result.require(bool(bindings), "handoff missing frontend_experience_binding")
    result.require(len(bindings) == 1, "handoff must contain exactly one frontend_experience_binding")
    binding = bindings[0] if bindings else ""
    result.require(
        re.search(r"(?m)^\s*applicable:\s*true\s*$", binding) is not None,
        "handoff frontend_experience_binding.applicable must be true",
    )
    for key in [
        "design_document_path",
        "design_contract_version",
        "design_manifest_ref",
        "baseline_source",
        "style_mode",
        "reference_pages",
        "required_existing_components",
        "allowed_extensions",
        "prohibited_redefinitions",
        "prompt_refs",
        "page_contract_refs",
        "module_contract_refs",
        "interaction_contract_refs",
        "confirmed_design_assets",
        "consistency_tests",
    ]:
        result.require(
            re.search(rf"(?m)^\s*{re.escape(key)}:\s*", binding) is not None,
            f"handoff frontend_experience_binding missing '{key}'",
        )
    result.require(
        re.search(r"(?m)^\s*-?\s*role:\s*UI/UX Design\s*$", handoff_text) is not None,
        "handoff_role_mapping missing UI/UX Design role",
    )
    design_path = extract_yaml_mapping_value(manifest, "design_document_path")
    handoff_path = extract_yaml_mapping_value(binding, "design_document_path")
    result.require(
        bool(design_path and handoff_path and design_path == handoff_path),
        "handoff design_document_path does not match design manifest",
    )
    for ref_id, revision in sorted(expected_refs.items()):
        result.require(
            carries_exact_reference(binding, ref_id, revision),
            f"handoff binding does not carry exact manifest reference: {ref_id}@{revision}",
        )
    for test_id in sorted(manifest_test_ids):
        result.require(test_id in binding, f"handoff binding does not carry manifest TEST reference: {test_id}")
    result.require(
        "design_contract_version: ui-ux-execution/v1" in binding,
        "handoff design_contract_version must be ui-ux-execution/v1",
    )
    if PLACEHOLDER_PATTERN.search(handoff_text):
        result.errors.append("execution-ready handoff contains placeholder content")


def validate_task_doc(
    task_text: str,
    manifest: str,
    expected_refs: dict[str, str],
    manifest_test_ids: set[str],
    result: ValidationResult,
) -> None:
    bindings = extract_indented_mapping_blocks(task_text, "frontend_contract_binding")
    result.require(bool(bindings), "task document missing frontend_contract_binding")
    required_keys = [
        "design_document_path",
        "design_manifest_ref",
        "baseline_source",
        "reference_pages",
        "prompt_refs",
        "page_contract_refs",
        "module_contract_refs",
        "interaction_contract_refs",
        "confirmed_asset_refs",
        "consistency_test_refs",
        "allowed_extensions",
        "prohibited_redefinitions",
    ]
    design_path = extract_yaml_mapping_value(manifest, "design_document_path")
    for index, binding in enumerate(bindings, start=1):
        for key in required_keys:
            result.require(
                re.search(rf"(?m)^\s*{re.escape(key)}:\s*", binding) is not None,
                f"task frontend_contract_binding #{index} missing '{key}'",
            )
        task_design_path = extract_yaml_mapping_value(binding, "design_document_path")
        result.require(
            bool(design_path and task_design_path and design_path == task_design_path),
            f"task frontend_contract_binding #{index} design_document_path does not match design manifest",
        )
    all_bindings = "\n".join(bindings)
    for ref_id, revision in sorted(expected_refs.items()):
        result.require(
            carries_exact_reference(all_bindings, ref_id, revision),
            f"task bindings do not carry exact manifest reference: {ref_id}@{revision}",
        )
    for test_id in sorted(manifest_test_ids):
        result.require(test_id in all_bindings, f"task bindings do not carry manifest TEST reference: {test_id}")
    if PLACEHOLDER_PATTERN.search(task_text):
        result.errors.append("execution-ready task document contains placeholder content")


def validate_project_paths(
    project_root: Path,
    design_doc: Path,
    manifest: str,
    asset_blocks: dict[str, str],
    result: ValidationResult,
) -> None:
    design_path = extract_yaml_mapping_value(manifest, "design_document_path")
    if design_path:
        manifest_design_path = (project_root / design_path).resolve()
        result.require(manifest_design_path.is_file(), f"manifest design path does not exist: {design_path}")
        result.require(
            manifest_design_path == design_doc.resolve(),
            "--design-doc does not match manifest design_document_path",
        )
    for asset_id in set(re.findall(r"ASSET-[A-Z0-9-]+", manifest)):
        block = asset_blocks.get(asset_id, "")
        path_value = extract_yaml_mapping_value(block, "asset_path_or_url")
        if not path_value or re.match(r"^[a-z]+://", path_value):
            continue
        result.require((project_root / path_value).is_file(), f"asset path does not exist: {asset_id} -> {path_value}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design-doc", required=True, type=Path, help="Path to the formal 05 UI/UX document")
    parser.add_argument("--task-doc", type=Path, help="Path to the formal 13 task contract document")
    parser.add_argument("--handoff", type=Path, help="Path to the planning handoff")
    parser.add_argument("--project-root", type=Path, help="Resolve project-relative design and asset paths")
    parser.add_argument(
        "--allow-design-ready",
        action="store_true",
        help="Validate a confirmed 05 before TEST/TASK/Handoff bindings exist",
    )
    parser.add_argument("--allow-blocked", action="store_true", help="Allow blocked design drafts")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = ValidationResult()
    design_text = read_text(args.design_doc, result)
    if not design_text:
        return report(result)

    for heading in [
        "## UI/UX 执行交付清单",
        "## 可复制设计提示词",
        "## 页面实现合同",
        "## UX 交互合同",
        "## 设计资产索引",
    ]:
        result.require(heading in design_text, f"missing section: {heading}")

    manifest, manifest_ids, readiness = validate_manifest(
        design_text,
        args.allow_design_ready,
        args.allow_blocked,
        result,
    )
    manifest_test_ids = set(re.findall(r"TEST-[A-Z0-9-]+", manifest))
    prompt_blocks = validate_prompts(design_text, result)
    page_blocks = validate_page_contracts(design_text, result)
    interaction_blocks = validate_interactions(design_text, result)
    asset_blocks = validate_assets(design_text, manifest, result)
    expected_refs = validate_manifest_revisions(
        manifest,
        prompt_blocks,
        page_blocks,
        interaction_blocks,
        asset_blocks,
        result,
    )
    validate_coverage_matrix(design_text, expected_refs, result)
    validate_internal_contract_references(
        expected_refs,
        [prompt_blocks, page_blocks, interaction_blocks, asset_blocks],
        result,
    )
    validate_no_placeholders(design_text, readiness == "blocked", result)

    defined_ids = set(prompt_blocks) | set(page_blocks) | set(interaction_blocks) | set(asset_blocks)
    for ref_id in sorted(manifest_ids):
        result.require(ref_id in defined_ids, f"manifest reference has no matching contract heading: {ref_id}")

    if readiness == "execution_ready" and not (args.allow_design_ready or args.allow_blocked):
        result.require(args.task_doc is not None, "execution-ready validation requires --task-doc")
    if args.handoff:
        result.require(args.task_doc is not None, "handoff validation requires --task-doc")

    if args.task_doc:
        task_text = read_text(args.task_doc, result)
        if task_text:
            validate_task_doc(task_text, manifest, expected_refs, manifest_test_ids, result)

    if args.handoff:
        handoff_text = read_text(args.handoff, result)
        if handoff_text:
            validate_handoff(handoff_text, manifest, expected_refs, manifest_test_ids, result)

    if args.project_root:
        validate_project_paths(args.project_root.resolve(), args.design_doc, manifest, asset_blocks, result)

    return report(result)


def report(result: ValidationResult) -> int:
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if result.errors:
        print(f"UI/UX contract validation failed with {len(result.errors)} error(s).", file=sys.stderr)
        return 1
    print("UI/UX contract validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

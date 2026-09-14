#!/usr/bin/env python3
"""Run one Required Validation Matrix item through the machine receipt layer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from forward_state import read_ledger
from machine_execution_receipt import execute_requirement, machine_spec_errors
from validate_long_readiness import (
    Result,
    clean,
    inventory_snapshot,
    load_anchored,
    matrix_requirements,
    print_errors,
    runtime_file,
    string_list,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute one Long required validation and write a machine receipt."
    )
    parser.add_argument("phase_runtime_directory", type=Path)
    parser.add_argument("--requirement-id", required=True)
    parser.add_argument("--validation-id", required=True)
    parser.add_argument("--attempt", required=True, type=int)
    args = parser.parse_args()

    runtime = args.phase_runtime_directory.resolve()
    result = Result()
    context = load_anchored(
        runtime / "current-runtime-context.md",
        ("runtime_epoch", "current_effective_status", "project_root_ref"),
        result,
    )
    ledger = read_ledger(runtime)
    current_stage = clean(ledger.get("current_stage")) if isinstance(ledger, dict) else ""
    result.require(
        current_stage in {"execution", "patch_execution"},
        "machine validation may run only during execution or patch_execution",
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
    inventory_refs = (
        string_list(audit.get("delivery_unit_inventory_refs"))
        if isinstance(audit, dict)
        else []
    )
    _, repository_revision, _ = inventory_snapshot(runtime, inventory_refs, result)
    matrix_revision, declared_repository_revision, requirements, _ = matrix_requirements(
        runtime, baseline, {}, result
    )
    result.require(
        declared_repository_revision == repository_revision,
        "machine execution repository revision does not match the Matrix",
    )
    matching = [
        item
        for item in requirements
        if clean(item.get("requirement_id")) == args.requirement_id
    ]
    result.require(
        len(matching) == 1,
        f"required Matrix item {args.requirement_id} must resolve exactly once",
    )
    if matching:
        result.errors.extend(machine_spec_errors(matching[0]))
    if print_errors(result):
        return 1

    try:
        receipt_path, receipt = execute_requirement(
            runtime=runtime,
            context=context,
            matrix_revision=matrix_revision,
            repository_revision=repository_revision,
            requirement=matching[0],
            validation_id=args.validation_id,
            attempt=args.attempt,
        )
    except (OSError, ValueError) as error:
        print(f"ERROR: machine validation could not run safely: {error}", file=sys.stderr)
        return 1
    print(
        f"Machine validation {args.validation_id}: {receipt['result']} "
        f"({receipt_path.relative_to(runtime).as_posix()})"
    )
    return 0 if receipt["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

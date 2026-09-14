#!/usr/bin/env python3
"""Small append-only, hash-chained workflow ledger used by Runtime validators."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


SCHEMA_VERSION = "forward-workflow/v1"
STATE_FILE = "testing-workflow-state.json"


def canonical_digest(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _event_payload(event: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in event.items() if key != "event_digest"}


def validate_ledger(
    ledger: object,
    *,
    workflow: str,
    runtime_id: str,
    transition_allowed: Callable[[dict[str, object] | None, dict[str, object]], bool],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(ledger, dict):
        return ["workflow ledger root must be an object"]
    if ledger.get("schema_version") != SCHEMA_VERSION:
        errors.append("workflow ledger schema_version is invalid")
    if ledger.get("workflow") != workflow:
        errors.append("workflow ledger workflow does not match this Runtime")
    if ledger.get("runtime_id") != runtime_id:
        errors.append("workflow ledger runtime_id does not match this Runtime")
    history = ledger.get("history")
    if not isinstance(history, list) or not history:
        errors.append("workflow ledger history must not be empty")
        return errors

    previous: dict[str, object] | None = None
    previous_digest = "genesis"
    for index, raw_event in enumerate(history, start=1):
        if not isinstance(raw_event, dict):
            errors.append(f"workflow event {index} must be an object")
            continue
        event = raw_event
        if event.get("sequence") != index:
            errors.append(f"workflow event {index} has a non-monotonic sequence")
        if event.get("previous_digest") != previous_digest:
            errors.append(f"workflow event {index} breaks the hash chain")
        expected_digest = canonical_digest(_event_payload(event))
        if event.get("event_digest") != expected_digest:
            errors.append(f"workflow event {index} digest is invalid")
        if previous is None:
            if event.get("from_stage") != "not_started" or event.get("cycle") != 1:
                errors.append("the first workflow event must start cycle 1 from not_started")
        else:
            previous_cycle = previous.get("cycle")
            cycle = event.get("cycle")
            if not isinstance(previous_cycle, int) or not isinstance(cycle, int):
                errors.append(f"workflow event {index} cycle must be an integer")
            elif cycle not in {previous_cycle, previous_cycle + 1}:
                errors.append(f"workflow event {index} skips or reverses a cycle")
            if event.get("from_stage") != previous.get("to_stage"):
                errors.append(f"workflow event {index} does not continue the prior stage")
        if not transition_allowed(previous, event):
            errors.append(f"workflow event {index} is not an allowed forward transition")
        previous = event
        previous_digest = str(event.get("event_digest", ""))

    assert previous is not None
    if ledger.get("current_stage") != previous.get("to_stage"):
        errors.append("workflow ledger current_stage does not match the last event")
    if ledger.get("current_cycle") != previous.get("cycle"):
        errors.append("workflow ledger current_cycle does not match the last event")
    if ledger.get("current_cycle_kind") != previous.get("cycle_kind"):
        errors.append("workflow ledger current_cycle_kind does not match the last event")
    if ledger.get("history_digest") != previous.get("event_digest"):
        errors.append("workflow ledger history_digest does not match the last event")
    return errors


def read_ledger(runtime_directory: Path) -> object:
    path = runtime_directory / STATE_FILE
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {"_read_error": str(error)}


def advance_ledger(
    runtime_directory: Path,
    *,
    workflow: str,
    runtime_id: str,
    to_stage: str,
    cycle_kind: str,
    start_new_cycle: bool = False,
    event_metadata: dict[str, object] | None = None,
    transition_allowed: Callable[[dict[str, object] | None, dict[str, object]], bool],
) -> dict[str, object]:
    current = read_ledger(runtime_directory)
    if current is None:
        ledger: dict[str, object] = {
            "schema_version": SCHEMA_VERSION,
            "workflow": workflow,
            "runtime_id": runtime_id,
            "current_stage": "not_started",
            "current_cycle": 0,
            "current_cycle_kind": cycle_kind,
            "history_digest": "genesis",
            "history": [],
        }
        previous = None
        cycle = 1
        from_stage = "not_started"
    else:
        errors = validate_ledger(
            current,
            workflow=workflow,
            runtime_id=runtime_id,
            transition_allowed=transition_allowed,
        )
        if errors:
            raise ValueError("; ".join(errors))
        assert isinstance(current, dict)
        ledger = current
        history = ledger["history"]
        assert isinstance(history, list)
        previous = history[-1]
        assert isinstance(previous, dict)
        from_stage = str(previous["to_stage"])
        previous_cycle = int(previous["cycle"])
        if cycle_kind != previous.get("cycle_kind") and not start_new_cycle:
            raise ValueError("changing cycle_kind requires an explicit new cycle")
        cycle = previous_cycle + 1 if start_new_cycle else previous_cycle

    history = ledger["history"]
    assert isinstance(history, list)
    event: dict[str, object] = {
        "sequence": len(history) + 1,
        "cycle": cycle,
        "cycle_kind": cycle_kind,
        "from_stage": from_stage,
        "to_stage": to_stage,
        "transitioned_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "previous_digest": ledger.get("history_digest", "genesis"),
    }
    if event_metadata:
        reserved = set(event) | {"event_digest"}
        overlap = reserved & set(event_metadata)
        if overlap:
            raise ValueError(
                "event metadata may not replace workflow fields: "
                + ", ".join(sorted(overlap))
            )
        event.update(event_metadata)
    if not transition_allowed(previous, event):
        raise ValueError(f"transition {from_stage} -> {to_stage} is not a legal forward transition")
    event["event_digest"] = canonical_digest(_event_payload(event))
    history.append(event)
    ledger["current_stage"] = to_stage
    ledger["current_cycle"] = cycle
    ledger["current_cycle_kind"] = cycle_kind
    ledger["history_digest"] = event["event_digest"]

    runtime_directory.mkdir(parents=True, exist_ok=True)
    target = runtime_directory / STATE_FILE
    handle, temporary_name = tempfile.mkstemp(
        prefix=f".{STATE_FILE}.", suffix=".tmp", dir=runtime_directory
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(ledger, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, target)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
    return ledger

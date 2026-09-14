#!/usr/bin/env python3
"""Execute Long validation probes and emit tamper-evident machine receipts."""

from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from typing import Any


SCHEMA_VERSION = "long-machine-execution-receipt/v2"
RUNNER_VERSION = "long-machine-runner/v2"
RECEIPT_DIRECTORY = "machine-execution-receipts"
SAFE_BOUNDARIES = {"local", "isolated", "controlled"}
PROBE_KINDS = {"argv", "path_exists"}
MAX_TIMEOUT_SECONDS = 3600


def canonical_digest(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def concrete_text(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    lowered = value.strip().lower()
    return lowered not in {"null", "none", "todo", "tbd", "unresolved"} and not (
        value.strip().startswith("<") and value.strip().endswith(">")
    )


def positive_timeout(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        timeout = int(str(value))
    except (TypeError, ValueError):
        return None
    return timeout if 1 <= timeout <= MAX_TIMEOUT_SECONDS else None


def string_argv(value: object) -> list[str] | None:
    if not isinstance(value, list) or not value:
        return None
    argv = [str(item) for item in value]
    return argv if all(concrete_text(item) for item in argv) else None


def machine_spec_errors(requirement: dict[str, Any]) -> list[str]:
    requirement_id = str(requirement.get("requirement_id", "<unknown>"))
    errors: list[str] = []
    if requirement.get("safe_execution_boundary") not in SAFE_BOUNDARIES:
        errors.append(
            f"{requirement_id}: safe_execution_boundary must be local, isolated, or controlled"
        )
    spec = requirement.get("machine_execution")
    if not isinstance(spec, dict):
        return [f"{requirement_id}: machine_execution must be a mapping"] + errors
    if not concrete_text(spec.get("working_directory_ref")):
        errors.append(f"{requirement_id}: machine_execution.working_directory_ref is required")
    default_timeout = positive_timeout(spec.get("default_timeout_seconds"))
    if default_timeout is None:
        errors.append(
            f"{requirement_id}: machine_execution.default_timeout_seconds must be 1..{MAX_TIMEOUT_SECONDS}"
        )
    expected = requirement.get("success_postconditions")
    expected_names = [str(item).strip() for item in expected] if isinstance(expected, list) else []
    probes = spec.get("postcondition_probes")
    if not isinstance(probes, list) or not probes:
        errors.append(f"{requirement_id}: machine_execution.postcondition_probes must not be empty")
        return errors
    actual_names: list[str] = []
    for index, raw_probe in enumerate(probes, start=1):
        label = f"{requirement_id}: machine probe {index}"
        if not isinstance(raw_probe, dict):
            errors.append(f"{label} must be a mapping")
            continue
        postcondition = raw_probe.get("postcondition")
        if not concrete_text(postcondition):
            errors.append(f"{label} requires a concrete postcondition")
        else:
            actual_names.append(str(postcondition).strip())
        kind = raw_probe.get("probe_kind")
        if kind not in PROBE_KINDS:
            errors.append(f"{label} probe_kind must be argv or path_exists")
            continue
        if "timeout_seconds" in raw_probe and positive_timeout(
            raw_probe.get("timeout_seconds")
        ) is None:
            errors.append(f"{label} timeout_seconds is invalid")
        if kind == "argv" and string_argv(raw_probe.get("argv")) is None:
            errors.append(f"{label} argv must be a non-empty argument list")
        if kind == "path_exists":
            if not concrete_text(raw_probe.get("path_ref")):
                errors.append(f"{label} path_ref is required")
            if raw_probe.get("expected_type") not in {"file", "directory", "any"}:
                errors.append(f"{label} expected_type must be file, directory, or any")
            if "nonempty" in raw_probe and not isinstance(raw_probe.get("nonempty"), bool):
                errors.append(f"{label} nonempty must be true or false")
    if len(actual_names) != len(set(actual_names)):
        errors.append(f"{requirement_id}: machine postcondition probes must be unique")
    if set(actual_names) != set(expected_names) or len(actual_names) != len(expected_names):
        errors.append(
            f"{requirement_id}: machine postcondition probes must exactly cover success_postconditions"
        )
    return errors


def normalized_machine_spec(requirement: dict[str, Any]) -> dict[str, object]:
    errors = machine_spec_errors(requirement)
    if errors:
        raise ValueError("; ".join(errors))
    spec = requirement["machine_execution"]
    assert isinstance(spec, dict)
    normalized_probes: list[dict[str, object]] = []
    for raw_probe in spec["postcondition_probes"]:
        assert isinstance(raw_probe, dict)
        probe: dict[str, object] = {
            "postcondition": str(raw_probe["postcondition"]).strip(),
            "probe_kind": raw_probe["probe_kind"],
            "timeout_seconds": positive_timeout(
                raw_probe.get("timeout_seconds", spec["default_timeout_seconds"])
            ),
        }
        if raw_probe["probe_kind"] == "argv":
            probe["argv"] = string_argv(raw_probe["argv"])
        else:
            probe["path_ref"] = str(raw_probe["path_ref"]).strip().replace("\\", "/")
            probe["expected_type"] = raw_probe["expected_type"]
            probe["nonempty"] = bool(raw_probe.get("nonempty", False))
        normalized_probes.append(probe)
    return {
        "working_directory_ref": str(spec["working_directory_ref"])
        .strip()
        .replace("\\", "/"),
        "default_timeout_seconds": positive_timeout(spec["default_timeout_seconds"]),
        "postcondition_probes": normalized_probes,
    }


def _relative_directory(base: Path, reference: object, label: str) -> Path:
    if not concrete_text(reference):
        raise ValueError(f"{label} is missing")
    relative = Path(str(reference).replace("\\", "/"))
    if relative.is_absolute():
        raise ValueError(f"{label} must be relative")
    resolved = (base / relative).resolve()
    try:
        resolved.relative_to(base.resolve())
    except ValueError as error:
        raise ValueError(f"{label} escapes the declared project root") from error
    if not resolved.is_dir():
        raise ValueError(f"{label} does not resolve to an existing directory")
    return resolved


def resolve_project_root(runtime: Path, project_root_ref: object) -> Path:
    if not concrete_text(project_root_ref):
        raise ValueError("current-runtime-context.project_root_ref is required")
    relative = Path(str(project_root_ref).replace("\\", "/"))
    if relative.is_absolute():
        raise ValueError("project_root_ref must be relative to the Phase Runtime Directory")
    project_root = (runtime / relative).resolve()
    if not project_root.is_dir():
        raise ValueError("project_root_ref does not resolve to an existing directory")
    if project_root == Path(project_root.anchor):
        raise ValueError("project_root_ref may not target a filesystem root")
    try:
        runtime.resolve().relative_to(project_root)
    except ValueError as error:
        raise ValueError("project_root_ref must contain the Phase Runtime Directory") from error
    try:
        repository_query = subprocess.run(
            ["git", "-C", str(runtime), "rev-parse", "--show-toplevel"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10,
            check=False,
            shell=False,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        repository_query = None
    if repository_query is not None and repository_query.returncode == 0:
        repository_root = Path(repository_query.stdout.strip()).resolve()
        if project_root != repository_root:
            raise ValueError("project_root_ref must match the repository root")
    return project_root


def resolve_working_directory(
    runtime: Path, project_root_ref: object, working_directory_ref: object
) -> tuple[Path, Path]:
    project_root = resolve_project_root(runtime, project_root_ref)
    return project_root, _relative_directory(
        project_root, working_directory_ref, "machine_execution.working_directory_ref"
    )


class _StreamDigest:
    def __init__(self) -> None:
        self.digest = hashlib.sha256()
        self.byte_count = 0

    def consume(self, stream: Any) -> None:
        try:
            try:
                while True:
                    chunk = stream.read(65536)
                    if not chunk:
                        break
                    self.digest.update(chunk)
                    self.byte_count += len(chunk)
            except (OSError, ValueError):
                pass
        finally:
            try:
                stream.close()
            except OSError:
                pass

    def hexdigest(self) -> str:
        return "sha256:" + self.digest.hexdigest()


def _terminate_process_tree(process: subprocess.Popen[bytes]) -> str:
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
        elif os.name == "nt":
            completed = subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
                check=False,
                shell=False,
            )
            if completed.returncode != 0 and process.poll() is None:
                process.kill()
                process.wait(timeout=5)
        elif process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        return "terminated"
    except (OSError, subprocess.SubprocessError):
        try:
            process.kill()
            process.wait(timeout=5)
        except (OSError, subprocess.SubprocessError):
            return "failed"
        return "terminated_direct_process_only"


def _run_argv(argv: list[str], cwd: Path, timeout: int) -> dict[str, object]:
    started = datetime.now(timezone.utc)
    start_tick = monotonic()
    stdout = _StreamDigest()
    stderr = _StreamDigest()
    exit_code: int | None = None
    error_kind: str | None = None
    cleanup = "not_required"
    process: subprocess.Popen[bytes] | None = None
    try:
        popen_options: dict[str, object] = {}
        if os.name == "posix":
            popen_options["start_new_session"] = True
        elif os.name == "nt":
            popen_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        process = subprocess.Popen(
            argv,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            **popen_options,
        )
        assert process.stdout is not None and process.stderr is not None
        readers = [
            threading.Thread(target=stdout.consume, args=(process.stdout,), daemon=True),
            threading.Thread(target=stderr.consume, args=(process.stderr,), daemon=True),
        ]
        for reader in readers:
            reader.start()
        try:
            exit_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            error_kind = "timeout"
            cleanup = _terminate_process_tree(process)
            exit_code = process.returncode
        for reader in readers:
            reader.join(timeout=1)
        if any(reader.is_alive() for reader in readers):
            error_kind = error_kind or "inherited_output_pipe_open"
            cleanup = _terminate_process_tree(process)
            for stream in (process.stdout, process.stderr):
                if stream is not None and not stream.closed:
                    try:
                        os.close(stream.fileno())
                    except OSError:
                        pass
            for reader in readers:
                reader.join(timeout=1)
    except FileNotFoundError:
        error_kind = "executable_not_found"
    except OSError:
        error_kind = "execution_error"
    completed_at = datetime.now(timezone.utc)
    passed = exit_code == 0 and error_kind is None
    return {
        "result": "passed" if passed else "failed",
        "started_at": started.isoformat().replace("+00:00", "Z"),
        "completed_at": completed_at.isoformat().replace("+00:00", "Z"),
        "duration_ms": max(0, round((monotonic() - start_tick) * 1000)),
        "exit_code": exit_code,
        "error_kind": error_kind,
        "stdout_sha256": stdout.hexdigest(),
        "stderr_sha256": stderr.hexdigest(),
        "stdout_bytes": stdout.byte_count,
        "stderr_bytes": stderr.byte_count,
        "process_tree_cleanup": cleanup,
    }


def _run_path_probe(
    probe: dict[str, object], working_directory: Path, project_root: Path
) -> dict[str, object]:
    reference = Path(str(probe["path_ref"]).replace("\\", "/"))
    if reference.is_absolute():
        raise ValueError("path_exists.path_ref must be relative to the working directory")
    candidate = (working_directory / reference).resolve()
    try:
        candidate.relative_to(project_root)
    except ValueError as error:
        raise ValueError("path_exists.path_ref escapes the declared project root") from error
    expected_type = probe["expected_type"]
    exists = candidate.exists()
    type_matches = (
        exists
        and (
            expected_type == "any"
            or (expected_type == "file" and candidate.is_file())
            or (expected_type == "directory" and candidate.is_dir())
        )
    )
    nonempty_required = bool(probe.get("nonempty"))
    nonempty_matches = True
    observed_size: int | None = None
    try:
        if type_matches and candidate.is_file():
            observed_size = candidate.stat().st_size
            nonempty_matches = not nonempty_required or observed_size > 0
        elif type_matches and candidate.is_dir() and nonempty_required:
            nonempty_matches = next(candidate.iterdir(), None) is not None
    except OSError:
        return {
            "result": "failed",
            "observed_exists": exists,
            "observed_type": "observation_error",
            "observed_size_bytes": None,
        }
    passed = type_matches and nonempty_matches
    return {
        "result": "passed" if passed else "failed",
        "observed_exists": exists,
        "observed_type": (
            "file" if candidate.is_file() else "directory" if candidate.is_dir() else "other" if exists else "missing"
        ),
        "observed_size_bytes": observed_size,
    }


def execute_requirement(
    *,
    runtime: Path,
    context: dict[str, Any],
    matrix_revision: str,
    repository_revision: str,
    requirement: dict[str, Any],
    validation_id: str,
    attempt: int,
) -> tuple[Path, dict[str, object]]:
    if not concrete_text(validation_id):
        raise ValueError("validation_id must be concrete")
    if attempt < 1:
        raise ValueError("attempt must be positive")
    spec = normalized_machine_spec(requirement)
    project_root, working_directory = resolve_working_directory(
        runtime, context.get("project_root_ref"), spec["working_directory_ref"]
    )
    safe_name = "".join(
        character if character.isalnum() or character in {"-", "_", "."} else "-"
        for character in validation_id
    ).strip("-.")
    if not safe_name:
        raise ValueError("validation_id cannot form a safe receipt filename")
    receipt_ref = f"{RECEIPT_DIRECTORY}/{safe_name}.json"
    target = runtime / receipt_ref
    receipt_directory = runtime / RECEIPT_DIRECTORY
    if receipt_directory.is_symlink():
        raise ValueError("machine execution receipt directory may not be a symbolic link")
    try:
        receipt_directory.resolve().relative_to(runtime.resolve())
    except ValueError as error:
        raise ValueError("machine execution receipt directory escapes the Runtime") from error
    if target.exists():
        raise ValueError(
            f"execution receipt already exists for {validation_id}; use a new validation_id and attempt"
        )

    probe_results: list[dict[str, object]] = []
    prior_failed = False
    for raw_probe in spec["postcondition_probes"]:
        assert isinstance(raw_probe, dict)
        record: dict[str, object] = {
            "postcondition": raw_probe["postcondition"],
            "probe_kind": raw_probe["probe_kind"],
        }
        if prior_failed:
            record["result"] = "blocked"
            record["blocked_by"] = "prior_machine_probe_failure"
        else:
            if raw_probe["probe_kind"] == "argv":
                execution = _run_argv(
                    list(raw_probe["argv"]),
                    working_directory,
                    int(raw_probe["timeout_seconds"]),
                )
                record.update(execution)
            else:
                record.update(
                    _run_path_probe(raw_probe, working_directory, project_root)
                )
            prior_failed = record["result"] != "passed"
        probe_results.append(record)

    overall = "passed" if all(item.get("result") == "passed" for item in probe_results) else "failed"
    payload: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "generated_by": RUNNER_VERSION,
        "runtime_epoch": str(context.get("runtime_epoch", "")),
        "matrix_revision": matrix_revision,
        "repository_revision": repository_revision,
        "requirement_id": str(requirement.get("requirement_id", "")),
        "delivery_unit_id": str(requirement.get("_unit_id", "")),
        "validation_id": validation_id,
        "attempt": attempt,
        "safe_execution_boundary": requirement.get("safe_execution_boundary"),
        "machine_execution": spec,
        "postcondition_results": probe_results,
        "result": overall,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    payload["receipt_digest"] = canonical_digest(payload)
    receipt_directory.mkdir(parents=True, exist_ok=True)
    if receipt_directory.is_symlink():
        raise ValueError("machine execution receipt directory may not be a symbolic link")
    handle, temporary_name = tempfile.mkstemp(
        prefix=f".{safe_name}.", suffix=".tmp", dir=receipt_directory
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary_name, target)
    except FileExistsError as error:
        raise ValueError(
            f"execution receipt already exists for {validation_id}; use a new validation_id and attempt"
        ) from error
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
    return target, payload


def load_receipt(path: Path) -> tuple[dict[str, object] | None, list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return None, [f"machine execution receipt is invalid JSON: {error}"]
    if not isinstance(value, dict):
        return None, ["machine execution receipt root must be an object"]
    declared = value.get("receipt_digest")
    unsigned = {key: item for key, item in value.items() if key != "receipt_digest"}
    errors = []
    if declared != canonical_digest(unsigned):
        errors.append("machine execution receipt digest is invalid")
    if value.get("schema_version") != SCHEMA_VERSION:
        errors.append("machine execution receipt schema is invalid")
    if value.get("generated_by") != RUNNER_VERSION:
        errors.append("machine execution receipt generator is invalid")
    return value, errors

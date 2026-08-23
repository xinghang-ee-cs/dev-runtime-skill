#!/usr/bin/env python3
"""Validate the Runtime Skills manifest and required version bumps."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def load_runtime_module(root: Path) -> Any:
    script = root / "scripts/runtime-skills.py"
    spec = importlib.util.spec_from_file_location("runtime_skills", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {script}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise RuntimeError(f"{path} has no YAML frontmatter")
    metadata: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return metadata
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            metadata[match.group(1)] = match.group(2).strip()
    raise RuntimeError(f"{path} has unterminated YAML frontmatter")


def manifest_at_ref(root: Path, ref: str) -> dict[str, Any] | None:
    try:
        payload = run_git(root, "show", f"{ref}:skills-manifest.json")
    except subprocess.CalledProcessError:
        return None
    return json.loads(payload)


def changed_paths(root: Path, ref: str) -> list[str]:
    output = run_git(root, "diff", "--name-only", f"{ref}...HEAD")
    return [line.strip() for line in output.splitlines() if line.strip()]


def validate_repository(root: Path, compare_ref: str | None, release_tag: str | None) -> list[str]:
    runtime = load_runtime_module(root)
    manifest = runtime.read_json(root / runtime.MANIFEST_NAME)
    errors = runtime.validate_manifest(manifest, root)

    if manifest.get("tool", {}).get("version") != runtime.TOOL_VERSION:
        errors.append(
            "manifest tool.version must match TOOL_VERSION in scripts/runtime-skills.py"
        )

    manifest_skills = set(manifest.get("skills", {}))
    directory_skills = {
        path.parent.name for path in (root / "skills").glob("*/SKILL.md")
    }
    if manifest_skills != directory_skills:
        errors.append(
            "manifest skill set differs from skills/*/SKILL.md: "
            f"manifest-only={sorted(manifest_skills - directory_skills)}, "
            f"directory-only={sorted(directory_skills - manifest_skills)}"
        )

    for name, record in sorted(manifest.get("skills", {}).items()):
        skill_file = root / record["path"] / "SKILL.md"
        try:
            metadata = parse_frontmatter(skill_file)
        except RuntimeError as exc:
            errors.append(str(exc))
            continue
        if metadata.get("name") != name:
            errors.append(
                f"{skill_file}: frontmatter name {metadata.get('name')!r} does not match {name!r}"
            )
        unexpected = sorted(set(metadata) - {"name", "description"})
        if unexpected:
            errors.append(
                f"{skill_file}: unsupported frontmatter fields: {', '.join(unexpected)}"
            )

    if release_tag:
        expected = f"v{manifest.get('release_version')}"
        if release_tag != expected:
            errors.append(f"release tag {release_tag!r} must equal {expected!r}")

    if compare_ref:
        previous = manifest_at_ref(root, compare_ref)
        if previous is not None:
            paths = changed_paths(root, compare_ref)
            try:
                if runtime.parse_semver(str(manifest["release_version"])) < runtime.parse_semver(
                    str(previous["release_version"])
                ):
                    errors.append(
                        "release_version may not decrease: "
                        f"{previous['release_version']} -> {manifest['release_version']}"
                    )
            except runtime.RuntimeSkillsError as exc:
                errors.append(str(exc))
            for name, record in sorted(manifest.get("skills", {}).items()):
                prefix = record["path"].rstrip("/") + "/"
                if not any(path.startswith(prefix) for path in paths):
                    continue
                old_record = previous.get("skills", {}).get(name)
                if old_record is None:
                    continue
                old = str(old_record.get("version", ""))
                new = str(record.get("version", ""))
                try:
                    if runtime.parse_semver(new) <= runtime.parse_semver(old):
                        errors.append(
                            f"{name} changed but its version did not increase: {old} -> {new}"
                        )
                except runtime.RuntimeSkillsError as exc:
                    errors.append(str(exc))

            if "scripts/runtime-skills.py" in paths:
                old = str(previous.get("tool", {}).get("version", ""))
                new = str(manifest.get("tool", {}).get("version", ""))
                try:
                    if runtime.parse_semver(new) <= runtime.parse_semver(old):
                        errors.append(
                            f"sync tool changed but tool.version did not increase: {old} -> {new}"
                        )
                except runtime.RuntimeSkillsError as exc:
                    errors.append(str(exc))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--compare-ref")
    parser.add_argument("--release-tag")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        errors = validate_repository(root, args.compare_ref, args.release_tag)
    except (RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("Skill manifest validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Skill manifest validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

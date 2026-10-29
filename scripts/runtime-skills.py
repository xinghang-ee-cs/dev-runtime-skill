#!/usr/bin/env python3
"""Install, verify, and update versioned Runtime Skills without dependencies."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Sequence


TOOL_VERSION = "0.2.0"
SUPPORTED_SCHEMA_VERSION = 1
MANIFEST_NAME = "skills-manifest.json"
LOCK_NAME = "runtime-skills.lock.json"
INSTALLED_TOOL_PATH = ".runtime-skills/runtime-skills.py"
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
IGNORED_FILE_NAMES = {".DS_Store"}
IGNORED_DIRECTORY_NAMES = {"__pycache__"}


class RuntimeSkillsError(RuntimeError):
    """Expected user-facing failure."""


@dataclass
class SourceBundle:
    root: Path
    manifest: dict[str, Any]
    ref: str
    commit: str | None
    temporary_root: Path | None = None

    def close(self) -> None:
        if self.temporary_root:
            shutil.rmtree(self.temporary_root, ignore_errors=True)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeSkillsError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeSkillsError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeSkillsError(f"Expected a JSON object in {path}")
    return value


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def parse_semver(value: str, label: str = "version") -> tuple[int, int, int]:
    match = SEMVER_RE.fullmatch(value)
    if not match:
        raise RuntimeSkillsError(
            f"{label} must use stable SemVer MAJOR.MINOR.PATCH, got {value!r}"
        )
    return tuple(int(part) for part in match.groups())


def version_change(old: str, new: str) -> str:
    before = parse_semver(old, "installed version")
    after = parse_semver(new, "source version")
    if after < before:
        return "downgrade"
    if after == before:
        return "none"
    if after[0] != before[0]:
        return "major"
    if after[1] != before[1]:
        return "minor"
    return "patch"


def validate_manifest(manifest: dict[str, Any], root: Path | None = None) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != SUPPORTED_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {SUPPORTED_SCHEMA_VERSION}, got "
            f"{manifest.get('schema_version')!r}"
        )

    try:
        parse_semver(str(manifest.get("release_version", "")), "release_version")
    except RuntimeSkillsError as exc:
        errors.append(str(exc))

    repository = manifest.get("repository")
    if not isinstance(repository, dict) or not repository.get("url"):
        errors.append("repository.url is required")

    tool = manifest.get("tool")
    if not isinstance(tool, dict):
        errors.append("tool must be an object")
    else:
        try:
            parse_semver(str(tool.get("version", "")), "tool.version")
        except RuntimeSkillsError as exc:
            errors.append(str(exc))
        if not tool.get("path"):
            errors.append("tool.path is required")

    skills = manifest.get("skills")
    if not isinstance(skills, dict) or not skills:
        errors.append("skills must be a non-empty object")
        return errors

    seen_paths: set[str] = set()
    for name, record in sorted(skills.items()):
        if not re.fullmatch(r"[a-z0-9-]+", name):
            errors.append(f"Invalid skill name: {name!r}")
        if not isinstance(record, dict):
            errors.append(f"skills.{name} must be an object")
            continue
        try:
            parse_semver(str(record.get("version", "")), f"skills.{name}.version")
        except RuntimeSkillsError as exc:
            errors.append(str(exc))
        skill_path = record.get("path")
        if not isinstance(skill_path, str) or not skill_path:
            errors.append(f"skills.{name}.path is required")
            continue
        if skill_path in seen_paths:
            errors.append(f"Duplicate skill path: {skill_path}")
        seen_paths.add(skill_path)
        if root is not None:
            resolved = root / skill_path
            if not (resolved / "SKILL.md").is_file():
                errors.append(f"skills.{name}.path has no SKILL.md: {skill_path}")

    if root is not None and isinstance(tool, dict) and tool.get("path"):
        tool_path = root / str(tool["path"])
        if not tool_path.is_file():
            errors.append(f"tool.path does not exist: {tool['path']}")
    return errors


def load_manifest(root: Path) -> dict[str, Any]:
    manifest = read_json(root / MANIFEST_NAME)
    errors = validate_manifest(manifest, root)
    if errors:
        raise RuntimeSkillsError("Invalid manifest:\n- " + "\n- ".join(errors))
    return manifest


def safe_project_path(project: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise RuntimeSkillsError(f"Project paths must be safe and relative: {relative!r}")
    project_resolved = project.resolve()
    resolved = (project / candidate).resolve()
    if resolved == project_resolved or project_resolved not in resolved.parents:
        raise RuntimeSkillsError(f"Path escapes the target project: {relative!r}")
    return resolved


def iter_content_files(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root)
        if any(part in IGNORED_DIRECTORY_NAMES for part in relative.parts):
            continue
        if path.name in IGNORED_FILE_NAMES:
            continue
        if path.is_symlink():
            raise RuntimeSkillsError(f"Symlinks are not supported in managed content: {path}")
        if path.is_file():
            yield path


def content_hash(root: Path) -> str:
    if not root.is_dir():
        raise RuntimeSkillsError(f"Managed directory is missing: {root}")
    digest = hashlib.sha256()
    for path in iter_content_files(root):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        payload = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_inventory(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): file_hash(path)
        for path in iter_content_files(root)
    }


def git_value(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return value or None


def locate_local_source(script_path: Path) -> Path | None:
    for candidate in [script_path.parent.parent, *script_path.parents]:
        if (candidate / MANIFEST_NAME).is_file():
            return candidate.resolve()
    return None


def parse_github_repository(repository: str) -> tuple[str, str]:
    parsed = urllib.parse.urlparse(repository)
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        raise RuntimeSkillsError(
            "Remote release synchronization currently requires an https://github.com/owner/repo URL"
        )
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) != 2:
        raise RuntimeSkillsError(f"Invalid GitHub repository URL: {repository}")
    owner, repo = parts
    if repo.endswith(".git"):
        repo = repo[:-4]
    return owner, repo


def github_request(url: str) -> urllib.request.Request:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "dev-runtime-skill-sync",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers)


def fetch_json(url: str) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(github_request(url), timeout=30) as response:
            value = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeSkillsError(f"Unable to read GitHub release metadata: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeSkillsError("GitHub returned unexpected release metadata")
    return value


def download(url: str, destination: Path) -> None:
    try:
        with urllib.request.urlopen(github_request(url), timeout=60) as response:
            with destination.open("wb") as output:
                shutil.copyfileobj(response, output)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeSkillsError(f"Unable to download release archive: {exc}") from exc


def extract_zip_safely(archive: Path, destination: Path) -> Path:
    destination_resolved = destination.resolve()
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            member_path = (destination / member.filename).resolve()
            if member_path != destination_resolved and destination_resolved not in member_path.parents:
                raise RuntimeSkillsError("Release archive contains an unsafe path")
        bundle.extractall(destination)
    roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise RuntimeSkillsError("Release archive must contain exactly one repository root")
    return roots[0]


def remote_source(repository: str, release_name: str) -> SourceBundle:
    owner, repo = parse_github_repository(repository)
    api_base = f"https://api.github.com/repos/{owner}/{repo}"
    if release_name == "latest":
        release_url = f"{api_base}/releases/latest"
    else:
        release_url = f"{api_base}/releases/tags/{urllib.parse.quote(release_name, safe='')}"
    release = fetch_json(release_url)
    tag = release.get("tag_name")
    archive_url = release.get("zipball_url")
    if not isinstance(tag, str) or not isinstance(archive_url, str):
        raise RuntimeSkillsError("Release metadata is missing tag_name or zipball_url")

    temporary_root = Path(tempfile.mkdtemp(prefix="runtime-skills-release-"))
    try:
        archive = temporary_root / "release.zip"
        extracted = temporary_root / "extracted"
        extracted.mkdir()
        download(archive_url, archive)
        root = extract_zip_safely(archive, extracted)
        manifest = load_manifest(root)
        expected_tag = f"v{manifest['release_version']}"
        if tag != expected_tag:
            raise RuntimeSkillsError(
                f"Release tag {tag!r} does not match manifest release {expected_tag!r}"
            )
        commit_metadata = fetch_json(f"{api_base}/commits/{urllib.parse.quote(tag, safe='')}")
        commit = commit_metadata.get("sha")
        return SourceBundle(
            root=root,
            manifest=manifest,
            ref=tag,
            commit=commit if isinstance(commit, str) else None,
            temporary_root=temporary_root,
        )
    except Exception:
        shutil.rmtree(temporary_root, ignore_errors=True)
        raise


def local_source(root: Path) -> SourceBundle:
    root = root.resolve()
    manifest = load_manifest(root)
    branch = git_value(root, "branch", "--show-current")
    return SourceBundle(
        root=root,
        manifest=manifest,
        ref=branch or "working-tree",
        commit=git_value(root, "rev-parse", "HEAD"),
    )


@contextmanager
def source_bundle(
    *,
    source: str | None,
    release: str | None,
    repository: str | None,
    lock: dict[str, Any] | None,
    script_path: Path,
    default_remote: bool,
) -> Iterator[SourceBundle]:
    if source and release:
        raise RuntimeSkillsError("Use either --source or --release, not both")

    bundle: SourceBundle
    if source:
        bundle = local_source(Path(source))
    elif release or default_remote:
        repository_url = repository
        if not repository_url and lock:
            repository_url = lock.get("source", {}).get("repository")
        if not repository_url:
            local_root = locate_local_source(script_path)
            if local_root:
                repository_url = load_manifest(local_root)["repository"]["url"]
        if not repository_url:
            raise RuntimeSkillsError("--repository is required when no source manifest or lock is available")
        bundle = remote_source(str(repository_url), release or "latest")
    else:
        local_root = locate_local_source(script_path)
        if not local_root:
            raise RuntimeSkillsError("No local source found; use --release latest --repository <url>")
        bundle = local_source(local_root)
    try:
        yield bundle
    finally:
        bundle.close()


def load_lock(project: Path) -> dict[str, Any]:
    lock = read_json(project / LOCK_NAME)
    if lock.get("schema_version") != SUPPORTED_SCHEMA_VERSION:
        raise RuntimeSkillsError(
            f"Unsupported lock schema: {lock.get('schema_version')!r}; refresh the sync tool"
        )
    if not isinstance(lock.get("skills"), dict) or not lock["skills"]:
        raise RuntimeSkillsError("Lock file contains no installed skills")
    return lock


def lock_drift(project: Path, lock: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    for name, record in sorted(lock["skills"].items()):
        expected = record.get("content_sha256")
        destinations = record.get("destinations")
        if not isinstance(destinations, list) or not destinations:
            problems.append(f"{name}: no destinations recorded")
            continue
        for relative in destinations:
            destination = safe_project_path(project, str(relative))
            if not destination.is_dir():
                problems.append(f"{name}: missing {relative}")
                continue
            actual = content_hash(destination)
            if actual != expected:
                problems.append(f"{name}: locally modified or mixed version at {relative}")

    installer = lock.get("tool", {})
    installer_path = installer.get("path", INSTALLED_TOOL_PATH)
    expected_tool_hash = installer.get("content_sha256")
    tool_path = safe_project_path(project, str(installer_path))
    if not tool_path.is_file():
        problems.append(f"sync tool: missing {installer_path}")
    elif expected_tool_hash and file_hash(tool_path) != expected_tool_hash:
        problems.append(f"sync tool: locally modified at {installer_path}")
    return problems


def source_versions(bundle: SourceBundle, installed_names: Sequence[str]) -> dict[str, str]:
    available = bundle.manifest["skills"]
    missing = sorted(set(installed_names) - set(available))
    if missing:
        raise RuntimeSkillsError("Source release removed installed skills: " + ", ".join(missing))
    return {name: str(available[name]["version"]) for name in installed_names}


def changes_against_source(
    lock: dict[str, Any], bundle: SourceBundle
) -> dict[str, str]:
    changes: dict[str, str] = {}
    for name, record in sorted(lock["skills"].items()):
        new_version = str(bundle.manifest["skills"][name]["version"])
        changes[name] = version_change(str(record["version"]), new_version)
    changes["sync-tool"] = version_change(
        str(lock.get("tool", {}).get("version", "0.0.0")),
        str(bundle.manifest["tool"]["version"]),
    )
    return changes


def highest_change(changes: dict[str, str]) -> str:
    order = {"none": 0, "patch": 1, "minor": 2, "major": 3, "downgrade": 4}
    return max(changes.values(), key=lambda value: order[value], default="none")


def copy_to_stage(source: Path, destination: Path) -> None:
    if source.is_dir():
        destination.mkdir(parents=True)
        for source_file in iter_content_files(source):
            target_file = destination / source_file.relative_to(source)
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)
    elif source.is_file():
        if source.is_symlink():
            raise RuntimeSkillsError(f"Symlinks are not supported in managed content: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    else:
        raise RuntimeSkillsError(f"Deployment source is missing: {source}")


def deploy_transaction(project: Path, operations: list[tuple[Path | None, Path]]) -> None:
    if not operations:
        return
    transaction_root = Path(
        tempfile.mkdtemp(prefix=".runtime-skills-transaction-", dir=project)
    )
    staged_root = transaction_root / "staged"
    backup_root = transaction_root / "backup"
    staged_root.mkdir()
    backup_root.mkdir()
    staged: list[tuple[Path | None, Path, Path]] = []
    installed: list[tuple[Path, Path | None]] = []
    try:
        for index, (source, destination) in enumerate(operations):
            staged_path = staged_root / str(index)
            if source is not None:
                copy_to_stage(source, staged_path)
            staged.append((staged_path if source is not None else None, destination, backup_root / str(index)))

        for staged_path, destination, backup in staged:
            destination.parent.mkdir(parents=True, exist_ok=True)
            previous: Path | None = None
            if destination.exists():
                os.replace(destination, backup)
                previous = backup
            try:
                if staged_path is not None:
                    os.replace(staged_path, destination)
            except Exception:
                if previous and previous.exists():
                    os.replace(previous, destination)
                raise
            installed.append((destination, previous))
    except Exception:
        for destination, previous in reversed(installed):
            if destination.is_dir():
                shutil.rmtree(destination, ignore_errors=True)
            elif destination.exists():
                destination.unlink()
            if previous and previous.exists():
                os.replace(previous, destination)
        raise
    finally:
        shutil.rmtree(transaction_root, ignore_errors=True)


def build_lock(
    project: Path,
    bundle: SourceBundle,
    destinations: dict[str, list[str]],
    previous: dict[str, Any] | None,
    auto_update: str,
) -> dict[str, Any]:
    now = utc_now()
    manifest = bundle.manifest
    records: dict[str, Any] = {}
    for name, relative_destinations in sorted(destinations.items()):
        source_record = manifest["skills"][name]
        source_directory = bundle.root / source_record["path"]
        records[name] = {
            "version": source_record["version"],
            "destinations": sorted(dict.fromkeys(relative_destinations)),
            "content_sha256": content_hash(source_directory),
        }

    tool_path = bundle.root / manifest["tool"]["path"]
    return {
        "schema_version": SUPPORTED_SCHEMA_VERSION,
        "source": {
            "repository": manifest["repository"]["url"],
            "release": bundle.ref,
            "commit": bundle.commit,
        },
        "tool": {
            "version": manifest["tool"]["version"],
            "path": INSTALLED_TOOL_PATH,
            "content_sha256": file_hash(tool_path),
        },
        "policy": {
            "check": "first_skill_use_per_session",
            "auto_update": auto_update,
        },
        "phase_pin": (
            previous.get("phase_pin", {"active": False, "reason": None, "set_at": None})
            if previous
            else {"active": False, "reason": None, "set_at": None}
        ),
        "skills": records,
        "installed_at": previous.get("installed_at", now) if previous else now,
        "updated_at": now,
    }


def prepare_deployment(
    project: Path,
    bundle: SourceBundle,
    destinations: dict[str, list[str]],
    lock: dict[str, Any],
) -> tuple[list[tuple[Path | None, Path]], Path]:
    operations: list[tuple[Path | None, Path]] = []
    for name, relative_destinations in sorted(destinations.items()):
        source_directory = bundle.root / bundle.manifest["skills"][name]["path"]
        for relative in relative_destinations:
            operations.append((source_directory, safe_project_path(project, relative)))

    source_tool = bundle.root / bundle.manifest["tool"]["path"]
    operations.append((source_tool, safe_project_path(project, INSTALLED_TOOL_PATH)))

    lock_source_dir = Path(tempfile.mkdtemp(prefix="runtime-skills-lock-"))
    lock_source = lock_source_dir / LOCK_NAME
    lock_source.write_text(
        json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    operations.append((lock_source, project / LOCK_NAME))
    return operations, lock_source_dir


def deploy_bundle(
    project: Path,
    bundle: SourceBundle,
    destinations: dict[str, list[str]],
    previous: dict[str, Any] | None,
    auto_update: str,
) -> dict[str, Any]:
    lock = build_lock(project, bundle, destinations, previous, auto_update)
    operations, temporary_lock_dir = prepare_deployment(project, bundle, destinations, lock)
    try:
        deploy_transaction(project, operations)
    finally:
        shutil.rmtree(temporary_lock_dir, ignore_errors=True)
    return lock


def normalize_destination(skill_root: str, skill_name: str) -> str:
    root = Path(skill_root)
    if root.is_absolute() or ".." in root.parts:
        raise RuntimeSkillsError(f"Destination roots must be relative: {skill_root!r}")
    return (root / skill_name).as_posix()


# Only inspect known discovery roots and explicit managed roots. Never recurse through
# application code, archives, other projects, or arbitrary user directories.
DISCOVERY_ROOTS = (".agents/skills", ".claude/skills", ".github/skills", ".codex/skills", ".skills")
DISCOVERY_LIMIT = 256
REPORT_LIMIT = 20
CONTEXT_LIMIT = 6000


def user_skill_roots() -> list[Path]:
    home = Path.home()
    codex = Path(os.environ.get("CODEX_HOME", str(home / ".codex")))
    return list(dict.fromkeys([
        *(home / root for root in DISCOVERY_ROOTS),
        codex / "skills", codex / "skills/remote-skills",
    ]))


def discovery_roots(project: Path, managed: Sequence[Path]) -> list[tuple[str, Path]]:
    roots = [("project", project / root) for root in DISCOVERY_ROOTS]
    roots.extend(("project", root) for root in managed)
    # Ancestor skills and instructions are relevant up to the containing Git root.
    boundary = git_value(project, "rev-parse", "--show-toplevel")
    stop = Path(boundary).resolve() if boundary else project
    if stop != project and stop in project.parents:
        for parent in project.parents:
            roots.extend(("ancestor", parent / root) for root in DISCOVERY_ROOTS)
            if parent == stop:
                break
    roots.extend(("user", root) for root in user_skill_roots())
    unique: dict[Path, tuple[str, Path]] = {}
    for scope, root in roots:
        unique.setdefault(root.absolute(), (scope, root))
    return list(unique.values())


def declared_skill_name(path: Path) -> str:
    with path.open("rb") as stream:
        text = stream.read(4096).decode("utf-8", errors="replace")
    if text.startswith("---\n"):
        frontmatter = text.split("---", 2)[1]
        match = re.search(r"^name:\s*([^\n]+)", frontmatter, re.MULTILINE)
        if match:
            return match.group(1).strip().strip("\"'")
    return path.parent.name


def installation_findings(
    project: Path, names: Sequence[str], expected: Sequence[Path], *, instructions: bool = True,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    expected_resolved = {path.resolve() for path in expected}
    managed_roots = [path.parent for path in expected]
    for scope, root in discovery_roots(project, managed_roots):
        if not root.is_dir():
            continue
        try:
            # Read at most the bounded discovery inventory, not reference content.
            entries = []
            with os.scandir(root) as scan:
                for entry in scan:
                    entries.append(Path(entry.path))
                    if len(entries) > DISCOVERY_LIMIT:
                        findings.append({"code": "inventory_limit", "path": str(root),
                                         "message": "Discovery inventory exceeds 256 entries; inspect this root explicitly."})
                        break
            for directory in sorted(entries[:DISCOVERY_LIMIT]):
                skill = directory / "SKILL.md"
                if not skill.is_file():
                    continue
                name = declared_skill_name(skill)
                if name in names and directory.resolve() not in expected_resolved:
                    findings.append({"code": "duplicate_skill", "path": str(directory),
                                     "message": f"{name}: unregistered {scope} copy; resolve platform discovery before proceeding."})
        except OSError as exc:
            findings.append({"code": "inventory_unreadable", "path": str(root),
                             "message": f"Cannot inspect discovery root ({type(exc).__name__})."})
    if instructions:
        instruction_roots = [project]
        boundary = git_value(project, "rev-parse", "--show-toplevel")
        if boundary:
            for parent in project.parents:
                if Path(boundary).resolve() not in (parent, *parent.parents):
                    break
                instruction_roots.append(parent)
                if parent == Path(boundary).resolve():
                    break
        instruction_roots.extend([
            Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))),
            Path.home() / ".claude",
        ])
        for directory in dict.fromkeys(instruction_roots):
            for filename in ("AGENTS.md", "AGENTS.override.md", "CLAUDE.md", "CLAUDE.local.md"):
                path = directory / filename
                if not path.is_file():
                    continue
                try:
                    size = path.stat().st_size
                    # Bound inspection itself; do not echo potentially private instructions.
                    with path.open("rb") as stream:
                        excerpt = stream.read(32768).decode("utf-8", errors="replace")
                    begin = excerpt.count("<!-- runtime-skills:begin -->")
                    if size > 12000 or begin > 1:
                        findings.append({"code": "instruction_review", "path": str(path),
                                         "message": f"{size} bytes, {begin} routing blocks; review legacy instructions without automatic rewriting."})
                except OSError:
                    findings.append({"code": "instruction_review", "path": str(path),
                                     "message": "Instruction file cannot be inspected; review manually."})
    return findings


def lock_expected_paths(project: Path, lock: dict[str, Any]) -> list[Path]:
    return [safe_project_path(project, relative) for record in lock["skills"].values()
            for relative in record["destinations"]]


def print_findings(findings: Sequence[dict[str, str]]) -> None:
    for finding in findings[:REPORT_LIMIT]:
        print(f"- {finding['code']}: {finding['path']}: {finding['message']}")
    if len(findings) > REPORT_LIMIT:
        print(f"- {len(findings) - REPORT_LIMIT} additional findings; use doctor --json for the complete bounded inventory.")


def scope_conflicts(project: Path, lock: dict[str, Any]) -> list[str]:
    return [f"{item['code']}: {item['path']}: {item['message']}"
            for item in installation_findings(project, list(lock["skills"]), lock_expected_paths(project, lock), instructions=False)]


def command_doctor(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    lock = load_lock(project) if (project / LOCK_NAME).is_file() else None
    names = list(lock["skills"]) if lock else list(args.skill or [])
    if not names:
        raise RuntimeSkillsError("doctor requires an installed lock or at least one --skill")
    findings = installation_findings(project, names, lock_expected_paths(project, lock) if lock else [])
    if lock:
        findings.extend({"code": "managed_drift", "path": str(project), "message": problem}
                        for problem in lock_drift(project, lock))
    if args.json:
        print(json.dumps({"findings": findings, "scope": "known project, Git ancestors and user discovery roots only"}, ensure_ascii=False))
    else:
        print_findings(findings)
        print(f"Doctor: {len(findings)} finding(s); no files changed. Nested/additional platform directories require explicit inspection.")
    return 2 if findings else 0


def markdown_sections(text: str) -> list[tuple[str, str]]:
    # Fenced examples can contain headings. They are not document sections.
    lines = text.splitlines(keepends=True)
    sections: list[tuple[str, str]] = []
    title = "preamble"
    current: list[str] = []
    fence: str | None = None
    for line in lines:
        stripped = line.lstrip()
        match = re.match(r"(`{3,}|~{3,})", stripped)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not stripped[len(marker):].strip():
                fence = None
        if fence is None and re.match(r"^#{1,6} +", line):
            if current:
                sections.append((title, "".join(current)))
            title, current = line.strip(), []
        current.append(line)
    if current:
        sections.append((title, "".join(current)))
    return sections


def command_context(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    lock = load_lock(project)
    if args.skill not in lock["skills"]:
        raise RuntimeSkillsError("Skill is not installed in this project")
    problems = lock_drift(project, lock) + scope_conflicts(project, lock)
    if problems:
        raise RuntimeSkillsError("Resolve installation findings before reading rules: " + "; ".join(problems[:REPORT_LIMIT]))
    root = safe_project_path(project, lock["skills"][args.skill]["destinations"][0])
    if not 1 <= args.limit <= CONTEXT_LIMIT or args.offset < 0:
        raise RuntimeSkillsError("Context limit must be 1..6000 characters and offset must be nonnegative")
    if args.file:
        path = safe_project_path(root, args.file)
        if path.suffix != ".md" or not path.is_file():
            raise RuntimeSkillsError("Choose an existing Markdown rule file")
        sections = markdown_sections(path.read_text(encoding="utf-8"))
        if args.outline:
            payload = "\n".join(f"{i}: {title} ({len(body)} chars)" for i, (title, body) in enumerate(sections))
        elif args.section is not None:
            if not 0 <= args.section < len(sections):
                raise RuntimeSkillsError("Section index is outside the outline")
            payload = sections[args.section][1]
        else:
            payload = path.read_text(encoding="utf-8")
    else:
        if args.section is not None or args.outline:
            raise RuntimeSkillsError("--section and --outline require --file")
        payload = "\n".join(f"{path.relative_to(root).as_posix()} ({path.stat().st_size} bytes)"
                            for path in iter_content_files(root) if path.suffix == ".md")
    end = min(args.offset + args.limit, len(payload))
    if args.offset > len(payload):
        raise RuntimeSkillsError("Offset is past the selected content")
    print(f"[context chars={end - args.offset} total={len(payload)} next_offset={end if end < len(payload) else 'done'}]")
    print(payload[args.offset:end])
    return 0


def validate_operation_paths(project: Path, destinations: dict[str, list[str]]) -> None:
    paths = [safe_project_path(project, item) for values in destinations.values() for item in values]
    protected = safe_project_path(project, ".runtime-skills")
    for path in paths:
        if path == protected or protected in path.parents or path in protected.parents:
            raise RuntimeSkillsError("Skill destinations may not overlap .runtime-skills")
    for index, path in enumerate(paths):
        if any(path == other or path in other.parents or other in path.parents for other in paths[index + 1:]):
            raise RuntimeSkillsError("Managed Skill destinations may not overlap")


def validate_project_root(project: Path) -> None:
    home = Path.home().resolve()
    user_directories = [(home / name).resolve() for name in (".agents", ".claude", ".github", ".codex", ".skills")]
    user_directories.append(Path(os.environ.get("CODEX_HOME", str(home / ".codex"))).resolve())
    if project in {home, Path(project.anchor)} or any(
        project == root or root in project.parents for root in user_directories
    ):
        raise RuntimeSkillsError(
            "This installer manages project-local Skills; do not use a user/home/platform directory as --project"
        )


def command_relocate(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    validate_project_root(project)
    lock = load_lock(project)
    if lock.get("phase_pin", {}).get("active"):
        raise RuntimeSkillsError("Cannot relocate Skills while an active phase is pinned")
    problems = lock_drift(project, lock) + scope_conflicts(project, lock)
    if problems:
        raise RuntimeSkillsError("Resolve drift/discovery findings before relocation: " + "; ".join(problems[:REPORT_LIMIT]))
    updated = json.loads(json.dumps(lock))
    archive = f".runtime-skills/retired/{uuid.uuid4().hex}"
    operations: list[tuple[Path | None, Path]] = []
    moved_names = list(dict.fromkeys(args.skill))
    for name in moved_names:
        if name not in updated["skills"]:
            raise RuntimeSkillsError(f"Skill is not installed: {name}")
        old = normalize_destination(args.from_root, name)
        new = normalize_destination(args.to_root, name)
        if old == new:
            raise RuntimeSkillsError("Relocation source and destination must differ")
        record = updated["skills"][name]
        if old not in record["destinations"]:
            raise RuntimeSkillsError(f"Source is not a managed destination: {old}")
        old_path, new_path = safe_project_path(project, old), safe_project_path(project, new)
        if new_path.exists():
            raise RuntimeSkillsError(f"Relocation destination already exists; inspect/adopt it explicitly first: {new}")
        record["destinations"] = sorted((set(record["destinations"]) - {old}) | {new})
        operations.extend([(old_path, safe_project_path(project, f"{archive}/{old}")),
                           (old_path, new_path), (None, old_path)])
    # Check every source and final path, including copies retained for another platform.
    operation_destinations = {
        name: sorted(set(record["destinations"]) | set(updated["skills"][name]["destinations"]))
        for name, record in lock["skills"].items()
    }
    validate_operation_paths(project, operation_destinations)
    updated["updated_at"] = utc_now()
    with tempfile.TemporaryDirectory(prefix="runtime-relocate-lock-") as temp:
        staged_lock = Path(temp) / LOCK_NAME
        write_json_atomic(staged_lock, updated)
        operations.append((staged_lock, project / LOCK_NAME))
        deploy_transaction(project, operations)
    print(f"Relocated {len(moved_names)} skill(s); old copies archived at {archive}; no project Runtime or instructions changed.")
    return 0


def command_install(args: argparse.Namespace, script_path: Path) -> int:
    project = Path(args.project).resolve()
    validate_project_root(project)
    project.mkdir(parents=True, exist_ok=True)
    previous = load_lock(project) if (project / LOCK_NAME).is_file() else None
    if previous:
        if previous.get("phase_pin", {}).get("active"):
            raise RuntimeSkillsError(
                "Cannot add or reinstall Skills while an active phase is pinned"
            )
        drift = lock_drift(project, previous)
        if drift and not args.overwrite_local_changes:
            raise RuntimeSkillsError(
                "Refusing to overwrite local changes:\n- " + "\n- ".join(drift)
            )

    with source_bundle(
        source=args.source,
        release=args.release,
        repository=args.repository,
        lock=previous,
        script_path=script_path,
        default_remote=False,
    ) as bundle:
        requested = list(dict.fromkeys(args.skill))
        unknown = sorted(set(requested) - set(bundle.manifest["skills"]))
        if unknown:
            raise RuntimeSkillsError("Unknown skills: " + ", ".join(unknown))
        if previous:
            source_versions(bundle, list(previous["skills"]))
            existing_changes = changes_against_source(previous, bundle)
            existing_level = highest_change(existing_changes)
            if existing_level == "downgrade":
                raise RuntimeSkillsError("Refusing to downgrade installed Skills while adding a Skill")
            if existing_level in {"minor", "major"}:
                raise RuntimeSkillsError(
                    f"Existing Skills require a {existing_level} update; run update with explicit "
                    f"--allow {existing_level} before adding another Skill"
                )

        destinations: dict[str, list[str]] = {}
        if previous:
            destinations.update(
                {
                    name: list(record["destinations"])
                    for name, record in previous["skills"].items()
                }
            )
        for name in requested:
            new_destinations = [
                normalize_destination(root, name) for root in args.destination
            ]
            old_destinations = set(destinations.get(name, []))
            if old_destinations and set(new_destinations) - old_destinations and not args.add_destination:
                raise RuntimeSkillsError("New destination for an installed Skill: use --add-destination for an intentional additional platform, or relocate for a move")
            destinations[name] = sorted(old_destinations | set(new_destinations))

        validate_operation_paths(project, destinations)
        expected = [safe_project_path(project, item) for values in destinations.values() for item in values]
        findings = installation_findings(project, list(destinations), expected)
        conflicts = [item for item in findings if item["code"] != "instruction_review"]
        if conflicts:
            print_findings(conflicts)
            raise RuntimeSkillsError("Resolve duplicate/incomplete discovery inventory before installation; no old copies were removed")
        print_findings([item for item in findings if item["code"] == "instruction_review"])
        unmanaged_conflicts: list[str] = []
        for name, relative_destinations in destinations.items():
            if name not in bundle.manifest["skills"]:
                raise RuntimeSkillsError(f"Installed skill is missing from source: {name}")
            for relative in relative_destinations:
                destination = safe_project_path(project, relative)
                registered = previous and relative in previous["skills"].get(name, {}).get("destinations", [])
                if destination.exists() and not registered and not args.overwrite_local_changes:
                    if not destination.is_dir():
                        unmanaged_conflicts.append(f"{relative}: existing path is not a directory")
                        continue
                    current = file_inventory(destination)
                    incoming = source_inventory(bundle, name)
                    added, modified, removed = inventory_changes(current, incoming)
                    unmanaged_conflicts.append(f"{relative}: unmanaged existing Skill")
                    for label, paths in (
                        ("incoming adds", added),
                        ("incoming modifies", modified),
                        ("incoming removes", removed),
                    ):
                        for path in paths:
                            unmanaged_conflicts.append(f"  {label}: {path}")
                    if not added and not modified and not removed:
                        unmanaged_conflicts.append("  content already matches the selected source")
        if unmanaged_conflicts:
            raise RuntimeSkillsError(
                "Unmanaged Skill directories already exist. Review this comparison, then rerun "
                "with --overwrite-local-changes to adopt the selected Release:\n- "
                + "\n- ".join(unmanaged_conflicts)
            )

        if previous and destinations == {name: record["destinations"] for name, record in previous["skills"].items()} and highest_change(changes_against_source(previous, bundle)) == "none" and not lock_drift(project, previous):
            print("Already installed; no files changed.")
            return 0
        lock = deploy_bundle(
            project,
            bundle,
            destinations,
            previous,
            args.auto_update if not previous else previous["policy"]["auto_update"],
        )
    print(
        f"Installed {len(lock['skills'])} skill(s) from {lock['source']['release']} "
        f"and wrote {LOCK_NAME}."
    )
    return 0


def command_verify(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    lock = load_lock(project)
    drift = lock_drift(project, lock) + scope_conflicts(project, lock)
    if drift:
        print("Verification failed:")
        for problem in drift:
            print(f"- {problem}")
        return 2
    print(
        f"Verified {len(lock['skills'])} skill(s) at {lock['source']['release']}; "
        "all managed copies match the lock."
    )
    return 0


def print_version_status(lock: dict[str, Any], bundle: SourceBundle) -> dict[str, str]:
    source_versions(bundle, list(lock["skills"]))
    changes = changes_against_source(lock, bundle)
    for name, change in changes.items():
        if name == "sync-tool":
            old = str(lock.get("tool", {}).get("version", "0.0.0"))
            new = str(bundle.manifest["tool"]["version"])
        else:
            old = str(lock["skills"][name]["version"])
            new = str(bundle.manifest["skills"][name]["version"])
        print(f"- {name}: {old} -> {new} ({change})")
    return changes


def command_status(args: argparse.Namespace, script_path: Path) -> int:
    project = Path(args.project).resolve()
    lock = load_lock(project)
    drift = lock_drift(project, lock) + scope_conflicts(project, lock)
    if drift:
        print("Local status: attention required")
        for problem in drift:
            print(f"- {problem}")
        return 2
    print(
        f"Local status: ready; {len(lock['skills'])} skill(s) match "
        f"{lock['source']['release']}."
    )
    pin = lock.get("phase_pin", {})
    if pin.get("active"):
        print(f"Phase pin: active ({pin.get('reason') or 'no reason recorded'})")
    else:
        print("Phase pin: inactive")

    if not args.check_remote:
        return 0
    try:
        with source_bundle(
            source=None,
            release="latest",
            repository=args.repository,
            lock=lock,
            script_path=script_path,
            default_remote=True,
        ) as bundle:
            print(f"Latest stable release: {bundle.ref}")
            changes = print_version_status(lock, bundle)
    except RuntimeSkillsError as exc:
        print(f"Remote status: unavailable ({exc})")
        return 0
    return 10 if highest_change(changes) != "none" else 0


def source_inventory(bundle: SourceBundle, skill_name: str) -> dict[str, str]:
    record = bundle.manifest["skills"][skill_name]
    return file_inventory(bundle.root / record["path"])


def inventory_changes(
    current: dict[str, str], incoming: dict[str, str]
) -> tuple[list[str], list[str], list[str]]:
    added = sorted(set(incoming) - set(current))
    removed = sorted(set(current) - set(incoming))
    modified = sorted(
        path for path in set(current) & set(incoming) if current[path] != incoming[path]
    )
    return added, modified, removed


def command_diff(args: argparse.Namespace, script_path: Path) -> int:
    project = Path(args.project).resolve()
    lock = load_lock(project)
    with source_bundle(
        source=args.source,
        release=args.release,
        repository=args.repository,
        lock=lock,
        script_path=script_path,
        default_remote=not bool(args.source),
    ) as bundle:
        source_versions(bundle, list(lock["skills"]))
        print(f"Comparing {lock['source']['release']} with {bundle.ref}:")
        for name, record in sorted(lock["skills"].items()):
            destination = safe_project_path(project, record["destinations"][0])
            current = file_inventory(destination) if destination.is_dir() else {}
            incoming = source_inventory(bundle, name)
            added, modified, removed = inventory_changes(current, incoming)
            old_version = record["version"]
            new_version = bundle.manifest["skills"][name]["version"]
            print(f"- {name}: {old_version} -> {new_version}")
            for label, paths in (("added", added), ("modified", modified), ("removed", removed)):
                for path in paths:
                    print(f"  {label}: {path}")
            if not added and not removed and not modified:
                print("  no content changes")
    return 0


def update_from_bundle(
    args: argparse.Namespace,
    script_path: Path,
    *,
    automatic: bool,
) -> int:
    project = Path(args.project).resolve()
    validate_project_root(project)
    lock = load_lock(project)
    pin = lock.get("phase_pin", {})
    if pin.get("active") and not getattr(args, "ignore_pin", False):
        reason = pin.get("reason") or "no reason recorded"
        raise RuntimeSkillsError(f"Update deferred because the active phase is pinned: {reason}")

    drift = lock_drift(project, lock) + scope_conflicts(project, lock)
    if drift and not getattr(args, "overwrite_local_changes", False):
        raise RuntimeSkillsError(
            "Refusing to overwrite local changes:\n- " + "\n- ".join(drift)
        )

    requested_source = getattr(args, "source", None)
    requested_release = None if requested_source else (getattr(args, "release", None) or "latest")
    with source_bundle(
        source=requested_source,
        release=requested_release,
        repository=getattr(args, "repository", None),
        lock=lock,
        script_path=script_path,
        default_remote=True,
    ) as bundle:
        source_versions(bundle, list(lock["skills"]))
        changes = changes_against_source(lock, bundle)
        level = highest_change(changes)
        if level == "downgrade":
            raise RuntimeSkillsError("Refusing to downgrade an installed Skill or sync tool")
        if level == "none":
            print(f"Already current at {bundle.ref}.")
            return 0

        allowed = "patch" if automatic else getattr(args, "allow", "major")
        order = {"none": 0, "patch": 1, "minor": 2, "major": 3}
        if order[level] > order[allowed]:
            print_version_status(lock, bundle)
            raise RuntimeSkillsError(
                f"The update contains a {level} change; explicit --allow {level} or higher is required"
            )

        destinations = {
            name: list(record["destinations"])
            for name, record in lock["skills"].items()
        }
        updated = deploy_bundle(
            project,
            bundle,
            destinations,
            lock,
            lock["policy"]["auto_update"],
        )
    print(f"Updated {len(updated['skills'])} skill(s) to {updated['source']['release']}.")
    return 0


def command_sync(args: argparse.Namespace, script_path: Path) -> int:
    project = Path(args.project).resolve()
    lock = load_lock(project)
    drift = lock_drift(project, lock) + scope_conflicts(project, lock)
    if drift:
        print("Automatic synchronization stopped because local drift was detected:")
        for problem in drift:
            print(f"- {problem}")
        return 2
    if lock.get("phase_pin", {}).get("active"):
        print(
            "Automatic synchronization deferred by the active phase pin: "
            f"{lock['phase_pin'].get('reason') or 'no reason recorded'}"
        )
        return 0
    if lock.get("policy", {}).get("auto_update") != "patch":
        print("Automatic updates are disabled; local copies are verified.")
        return command_status(
            argparse.Namespace(
                project=args.project,
                check_remote=True,
                repository=args.repository,
            ),
            script_path,
        )
    try:
        return update_from_bundle(args, script_path, automatic=True)
    except RuntimeSkillsError as exc:
        if "explicit --allow" in str(exc):
            print(f"Automatic synchronization needs user confirmation: {exc}")
            return 10
        if "Unable to" in str(exc):
            print(f"Remote update check unavailable; verified local copies remain usable: {exc}")
            return 0
        raise


def command_pin(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    validate_project_root(project)
    lock = load_lock(project)
    lock["phase_pin"] = {
        "active": True,
        "reason": args.reason,
        "set_at": utc_now(),
    }
    lock["updated_at"] = utc_now()
    write_json_atomic(project / LOCK_NAME, lock)
    print(f"Pinned Runtime Skills for the active phase: {args.reason}")
    return 0


def command_unpin(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    validate_project_root(project)
    lock = load_lock(project)
    lock["phase_pin"] = {"active": False, "reason": None, "set_at": None}
    lock["updated_at"] = utc_now()
    write_json_atomic(project / LOCK_NAME, lock)
    print("Removed the active phase pin.")
    return 0


def add_source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source", help="Local dev-runtime-skill checkout")
    parser.add_argument(
        "--release",
        help="GitHub Release tag or 'latest'; defaults to latest for update/diff/sync",
    )
    parser.add_argument("--repository", help="Override the GitHub repository URL")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install and synchronize versioned Runtime Skills."
    )
    parser.add_argument("--version", action="version", version=TOOL_VERSION)
    subparsers = parser.add_subparsers(dest="command", required=True)

    install = subparsers.add_parser("install", help="Install or add managed Skills")
    install.add_argument("--project", required=True, help="Target project root")
    install.add_argument("--skill", action="append", required=True, help="Skill name; repeatable")
    install.add_argument(
        "--destination",
        action="append",
        required=True,
        help="Project-relative Skill root such as .agents/skills; repeatable",
    )
    install.add_argument(
        "--auto-update", choices=["none", "patch"], default="patch"
    )
    install.add_argument("--overwrite-local-changes", action="store_true")
    install.add_argument("--add-destination", action="store_true", help="Explicitly add an additional platform copy; use relocate to move")
    add_source_arguments(install)

    doctor = subparsers.add_parser("doctor", help="Read-only diagnosis of duplicate scopes and oversized instructions")
    doctor.add_argument("--project", default=".")
    doctor.add_argument("--skill", action="append")
    doctor.add_argument("--json", action="store_true")

    context = subparsers.add_parser("context", help="Read a bounded rule section or outline")
    context.add_argument("--project", default=".")
    context.add_argument("--skill", required=True)
    context.add_argument("--file")
    context.add_argument("--outline", action="store_true")
    context.add_argument("--section", type=int)
    context.add_argument("--offset", type=int, default=0)
    context.add_argument("--limit", type=int, default=CONTEXT_LIMIT)

    relocate = subparsers.add_parser("relocate", help="Move managed copies and archive old paths outside discovery")
    relocate.add_argument("--project", default=".")
    relocate.add_argument("--from", dest="from_root", required=True)
    relocate.add_argument("--to", dest="to_root", required=True)
    relocate.add_argument("--skill", action="append", required=True)

    verify = subparsers.add_parser("verify", help="Verify installed copies against the lock")
    verify.add_argument("--project", default=".")

    status = subparsers.add_parser("status", help="Show local and optional remote status")
    status.add_argument("--project", default=".")
    status.add_argument("--check-remote", action="store_true")
    status.add_argument("--repository")

    diff = subparsers.add_parser("diff", help="List incoming Skill file changes")
    diff.add_argument("--project", default=".")
    add_source_arguments(diff)

    update = subparsers.add_parser("update", help="Update all managed copies as one bundle")
    update.add_argument("--project", default=".")
    update.add_argument("--allow", choices=["patch", "minor", "major"], default="patch")
    update.add_argument("--ignore-pin", action="store_true")
    update.add_argument("--overwrite-local-changes", action="store_true")
    add_source_arguments(update)

    sync = subparsers.add_parser(
        "sync", help="Verify and automatically apply compatible patch updates"
    )
    sync.add_argument("--project", default=".")
    add_source_arguments(sync)
    sync.set_defaults(ignore_pin=False, overwrite_local_changes=False)

    pin = subparsers.add_parser("pin", help="Freeze installed versions for an active phase")
    pin.add_argument("--project", default=".")
    pin.add_argument("--reason", required=True)

    unpin = subparsers.add_parser("unpin", help="Remove the active phase freeze")
    unpin.add_argument("--project", default=".")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    script_path = Path(__file__).resolve()
    try:
        if args.command == "install":
            return command_install(args, script_path)
        if args.command == "doctor":
            return command_doctor(args)
        if args.command == "context":
            return command_context(args)
        if args.command == "relocate":
            return command_relocate(args)
        if args.command == "verify":
            return command_verify(args)
        if args.command == "status":
            return command_status(args, script_path)
        if args.command == "diff":
            return command_diff(args, script_path)
        if args.command == "update":
            return update_from_bundle(args, script_path, automatic=False)
        if args.command == "sync":
            return command_sync(args, script_path)
        if args.command == "pin":
            return command_pin(args)
        if args.command == "unpin":
            return command_unpin(args)
        parser.error(f"Unknown command: {args.command}")
    except RuntimeSkillsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

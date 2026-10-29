#!/usr/bin/env python3
"""Generate deterministic Agent installers and single-Skill import packages."""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


def runtime_module(root: Path):
    spec = importlib.util.spec_from_file_location("package_runtime", root / "scripts/runtime-skills.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def zip_tree(root: Path, output: Path, runtime) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in runtime.iter_content_files(root):
            info = zipfile.ZipInfo(path.relative_to(root).as_posix(), date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def copy_payload(source: Path, destination: Path, runtime, names=None) -> None:
    manifest = runtime.load_manifest(source)
    if names is not None:
        manifest["skills"] = {name: manifest["skills"][name] for name in names}
    runtime.write_json_atomic(destination / runtime.MANIFEST_NAME, manifest)
    runtime.copy_to_stage(source / "scripts/runtime-skills.py", destination / "scripts/runtime-skills.py")
    for name, record in manifest["skills"].items():
        runtime.copy_to_stage(source / record["path"], destination / record["path"])


def build(source: Path, output: Path) -> dict:
    runtime = runtime_module(source)
    manifest = runtime.load_manifest(source)
    metadata = runtime.read_json(source / "distribution/platform-metadata.json")
    output.mkdir(parents=True, exist_ok=True)
    artifacts = []
    with tempfile.TemporaryDirectory(prefix="runtime-packages-") as temporary:
        base = Path(temporary)
        for agent in runtime.AGENTS:
            target = base / agent
            copy_payload(source, target, runtime)
            runtime.write_json_atomic(target / "install-target.json", {"agent": agent, "scope": "user", "release": manifest["release_version"]})
            (target / "INSTALL.md").write_text(
                f"# Local global installer\n\nThis package targets {agent}. Run `python install-local.py --project \"<existing-project>\"` to inspect conflicts and install globally. Repeat `--skill <name>` to select only those Skills. Installation stops without business initialization or project copies. Read install-target.json for the selected platform. Do not read the installer source into model context; run --help if needed.\n", encoding="utf-8")
            (target / "install-local.py").write_text(
                "import json, pathlib, subprocess, sys\n"
                "root = pathlib.Path(__file__).resolve().parent\n"
                "agent = json.loads((root / 'install-target.json').read_text())['agent']\n"
                "raise SystemExit(subprocess.run([sys.executable, str(root / 'scripts/runtime-skills.py'), 'install-agent', '--source', str(root), '--agent', agent, *sys.argv[1:]]).returncode)\n", encoding="utf-8")
            filename = f"runtime-skills-{agent}.zip"
            zip_tree(target, output / filename, runtime)
            artifacts.append({"file": filename, "agent": agent, "kind": "global-installer", "sha256": runtime.file_hash(output / filename)})
        for platform in ("doubao", "workbuddy"):
            for name, entry in manifest["skills"].items():
                container = base / platform / name
                target = container / name
                runtime.write_router(source, name, target)
                copy_payload(source, target / "assets/runtime-source", runtime, [name])
                if platform == "workbuddy":
                    local = metadata["skills"][name]
                    text = (target / "SKILL.md").read_text(encoding="utf-8")
                    fields = {**local, "version": entry["version"], "author": metadata["author"]}
                    # JSON strings are also YAML scalars; no YAML dependency or escaping ambiguity.
                    extra = "".join(f"{key}: {json.dumps(value, ensure_ascii=False)}\n" for key, value in fields.items())
                    header, body = text[4:].split("---\n", 1)
                    (target / "SKILL.md").write_text("---\n" + header + extra + "---\n" + body, encoding="utf-8")
                filename = f"runtime-skills-{platform}-{name}.zip"
                zip_tree(container, output / filename, runtime)
                artifacts.append({"file": filename, "platform": platform, "skill": name, "kind": "skill-import", "sha256": runtime.file_hash(output / filename)})
    shutil.copyfile(source / "install.py", output / "install.py")
    shutil.copyfile(source / "INSTALL.md", output / "INSTALL.md")
    for filename in ("install.py", "INSTALL.md"):
        artifacts.append({"file": filename, "kind": "installation-entry", "sha256": runtime.file_hash(output / filename)})
    index = {"schema_version": 1, "release": manifest["release_version"], "repository": manifest["repository"]["url"], "artifacts": artifacts}
    runtime.write_json_atomic(output / "install-manifest.json", index)
    checksums = [f"{item['sha256']}  {item['file']}" for item in artifacts]
    checksums.append(f"{runtime.file_hash(output / 'install-manifest.json')}  install-manifest.json")
    (output / "SHA256SUMS").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    return index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    index = build(Path(args.source).resolve(), Path(args.output).resolve())
    print(f"Built {len(index['artifacts'])} artifacts for {index['release']}; checksums in SHA256SUMS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Download a checksummed, versioned user-global installer for the current Agent."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

REPOSITORY = "xinghang-ee-cs/dev-runtime-skill"
AGENTS = ("codex", "claude", "copilot", "dsh")


def fetch(url: str) -> bytes:
    if not url.startswith("https://"):
        raise ValueError("Only HTTPS downloads are allowed")
    request = urllib.request.Request(url, headers={"User-Agent": "runtime-skills-installer", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if not response.url.startswith("https://"):
            raise ValueError("Insecure redirect")
        return response.read()


def select_agent(value: str) -> str:
    if value != "auto":
        return value
    explicit = os.environ.get("RUNTIME_SKILLS_AGENT")
    if explicit in AGENTS:
        return explicit
    available = [name for name in AGENTS if shutil.which(name)]
    if len(available) != 1:
        raise ValueError("Specify current Agent with --agent codex|claude|copilot|dsh; detection is ambiguous or unavailable")
    return available[0]


def extract(archive: Path, target: Path) -> None:
    with zipfile.ZipFile(archive) as package:
        for info in package.infolist():
            path = Path(info.filename)
            if path.is_absolute() or ".." in path.parts or "\\" in info.filename or (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("Unsafe archive member")
            if target.resolve() not in (target / path).resolve().parents:
                raise ValueError("Archive escapes destination")
        package.extractall(target)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=["auto", *AGENTS], default="auto")
    parser.add_argument("--release", default="latest")
    parser.add_argument("--skill", action="append")
    parser.add_argument("--project", help="Inspect this project for conflicts; installation never populates it")
    args = parser.parse_args()
    try:
        agent = select_agent(args.agent)
        if args.release != "latest" and not __import__('re').fullmatch(r"v\d+\.\d+\.\d+", args.release):
            raise ValueError("--release must be latest or vMAJOR.MINOR.PATCH")
        endpoint = "latest" if args.release == "latest" else "tags/" + args.release
        release = json.loads(fetch(f"https://api.github.com/repos/{REPOSITORY}/releases/{endpoint}"))
        if release.get("draft") or release.get("prerelease"):
            raise ValueError("Only published stable releases can be installed by this entry")
        assets = {item['name']: item['browser_download_url'] for item in release['assets']}
        filename = f"runtime-skills-{agent}.zip"
        for name in (filename, 'SHA256SUMS'):
            expected_prefix = f"https://github.com/{REPOSITORY}/releases/download/{release['tag_name']}/"
            if name not in assets or not assets[name].startswith(expected_prefix):
                raise ValueError(f"Release has no supported {name} asset; do not fall back to project copying")
        sums = dict(line.split('  ', 1)[::-1] for line in fetch(assets['SHA256SUMS']).decode().splitlines() if '  ' in line)
        payload = fetch(assets[filename])
        if hashlib.sha256(payload).hexdigest() != sums.get(filename):
            raise ValueError("Installer checksum mismatch")
        with tempfile.TemporaryDirectory(prefix="runtime-skills-install-") as temporary:
            directory = Path(temporary)
            archive = directory / filename
            archive.write_bytes(payload)
            source = directory / "source"
            source.mkdir()
            extract(archive, source)
            manifest = json.loads((source / "skills-manifest.json").read_text())
            if release['tag_name'] != 'v' + manifest['release_version']:
                raise ValueError("Asset release disagrees with tag")
            command = [sys.executable, str(source / "scripts/runtime-skills.py"), "install-agent", "--source", str(source), "--agent", agent]
            if args.project:
                command.extend(["--project", args.project])
            for skill in args.skill or []:
                command.extend(["--skill", skill])
            return subprocess.run(command, check=False).returncode
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as exc:
        print(f"Installation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

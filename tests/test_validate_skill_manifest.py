from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class ManifestVersionGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "scripts").mkdir(parents=True)
        (self.root / "skills/example-skill").mkdir(parents=True)
        shutil.copy2(
            REPOSITORY_ROOT / "scripts/runtime-skills.py",
            self.root / "scripts/runtime-skills.py",
        )
        shutil.copy2(
            REPOSITORY_ROOT / "scripts/validate-skill-manifest.py",
            self.root / "scripts/validate-skill-manifest.py",
        )
        self.write_manifest("0.1.0")
        self.write_skill("first\n")
        self.git("init")
        self.git("config", "user.name", "Runtime Skills Test")
        self.git("config", "user.email", "runtime-skills@example.invalid")
        self.git("add", ".")
        self.git("commit", "-m", "baseline")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.root), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def write_skill(self, body: str) -> None:
        (self.root / "skills/example-skill/SKILL.md").write_text(
            "---\nname: example-skill\ndescription: Test fixture.\n---\n\n" + body,
            encoding="utf-8",
        )

    def write_manifest(self, skill_version: str) -> None:
        manifest = {
            "schema_version": 1,
            "release_version": "0.1.0",
            "repository": {
                "url": "https://github.com/example/runtime-skills",
                "channel": "stable",
            },
            "tool": {"version": "0.1.0", "path": "scripts/runtime-skills.py"},
            "skills": {
                "example-skill": {
                    "version": skill_version,
                    "path": "skills/example-skill",
                }
            },
        }
        (self.root / "skills-manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )

    def validate(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(self.root / "scripts/validate-skill-manifest.py"),
                "--root",
                str(self.root),
                "--compare-ref",
                self.base,
            ],
            capture_output=True,
            text=True,
        )

    def test_changed_skill_requires_version_bump(self) -> None:
        self.write_skill("changed without version bump\n")
        self.git("add", "skills/example-skill/SKILL.md")
        self.git("commit", "-m", "change skill without version bump")
        failed = self.validate()
        self.assertEqual(failed.returncode, 1)
        self.assertIn("version did not increase", failed.stderr)

        self.write_manifest("0.1.1")
        passed = self.validate()
        self.assertEqual(passed.returncode, 0, passed.stderr)


if __name__ == "__main__":
    unittest.main()

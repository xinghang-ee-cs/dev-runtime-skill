from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY_ROOT / "scripts/runtime-skills.py"


def load_runtime_module():
    spec = importlib.util.spec_from_file_location("runtime_skills_test", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load runtime-skills.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runtime = load_runtime_module()


class RuntimeSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.project = self.root / "project"
        (self.source / "scripts").mkdir(parents=True)
        shutil.copy2(SCRIPT, self.source / "scripts/runtime-skills.py")
        self.write_source("0.1.0", "first\n")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_source(self, version: str, content: str) -> None:
        skill = self.source / "skills/example-skill"
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(
            "---\nname: example-skill\ndescription: Test fixture.\n---\n\n" + content,
            encoding="utf-8",
        )
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
                    "version": version,
                    "path": "skills/example-skill",
                }
            },
        }
        (self.source / "skills-manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )

    def install(self) -> int:
        return runtime.main(
            [
                "install",
                "--source",
                str(self.source),
                "--project",
                str(self.project),
                "--skill",
                "example-skill",
                "--destination",
                ".agents/skills",
                "--destination",
                ".claude/skills",
            ]
        )

    def test_install_and_verify_multiple_destinations(self) -> None:
        self.assertEqual(self.install(), 0)
        self.assertTrue((self.project / "runtime-skills.lock.json").is_file())
        self.assertTrue(
            (self.project / ".agents/skills/example-skill/SKILL.md").is_file()
        )
        self.assertTrue(
            (self.project / ".claude/skills/example-skill/SKILL.md").is_file()
        )
        self.assertTrue(
            (self.project / ".runtime-skills/runtime-skills.py").is_file()
        )
        self.assertEqual(runtime.main(["verify", "--project", str(self.project)]), 0)

    def test_current_repository_bundle_installs_and_verifies(self) -> None:
        actual_project = self.root / "actual-project"
        manifest = json.loads(
            (REPOSITORY_ROOT / "skills-manifest.json").read_text(encoding="utf-8")
        )
        arguments = [
            "install",
            "--source",
            str(REPOSITORY_ROOT),
            "--project",
            str(actual_project),
            "--destination",
            ".agents/skills",
        ]
        for name in manifest["skills"]:
            arguments.extend(["--skill", name])
        self.assertEqual(runtime.main(arguments), 0)
        self.assertEqual(
            runtime.main(["verify", "--project", str(actual_project)]), 0
        )

    def test_verify_detects_local_drift(self) -> None:
        self.assertEqual(self.install(), 0)
        installed = self.project / ".agents/skills/example-skill/SKILL.md"
        installed.write_text(installed.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")
        self.assertEqual(runtime.main(["verify", "--project", str(self.project)]), 2)

    def test_unmanaged_existing_copy_requires_explicit_adoption(self) -> None:
        destination = self.project / ".agents/skills/example-skill"
        destination.mkdir(parents=True)
        (destination / "SKILL.md").write_text("old unmanaged copy\n", encoding="utf-8")
        self.assertEqual(self.install(), 1)
        self.assertFalse((self.project / "runtime-skills.lock.json").exists())

        result = runtime.main(
            [
                "install",
                "--source",
                str(self.source),
                "--project",
                str(self.project),
                "--skill",
                "example-skill",
                "--destination",
                ".agents/skills",
                "--destination",
                ".claude/skills",
                "--overwrite-local-changes",
            ]
        )
        self.assertEqual(result, 0)
        self.assertEqual(runtime.main(["verify", "--project", str(self.project)]), 0)

    def test_patch_update_updates_every_destination(self) -> None:
        self.assertEqual(self.install(), 0)
        self.write_source("0.1.1", "second\n")
        result = runtime.main(
            [
                "update",
                "--source",
                str(self.source),
                "--project",
                str(self.project),
                "--allow",
                "patch",
            ]
        )
        self.assertEqual(result, 0)
        for root in (".agents/skills", ".claude/skills"):
            content = (self.project / root / "example-skill/SKILL.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("second", content)
        lock = json.loads(
            (self.project / "runtime-skills.lock.json").read_text(encoding="utf-8")
        )
        self.assertEqual(lock["skills"]["example-skill"]["version"], "0.1.1")
        self.assertEqual(runtime.main(["verify", "--project", str(self.project)]), 0)

    def test_sync_automatically_applies_patch_from_selected_source(self) -> None:
        self.assertEqual(self.install(), 0)
        self.write_source("0.1.1", "second\n")
        result = runtime.main(
            [
                "sync",
                "--source",
                str(self.source),
                "--project",
                str(self.project),
            ]
        )
        self.assertEqual(result, 0)
        content = (
            self.project / ".agents/skills/example-skill/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("second", content)

    def test_active_phase_pin_blocks_update(self) -> None:
        self.assertEqual(self.install(), 0)
        self.assertEqual(
            runtime.main(
                ["pin", "--project", str(self.project), "--reason", "phase-01"]
            ),
            0,
        )
        self.write_source("0.1.1", "second\n")
        result = runtime.main(
            ["update", "--source", str(self.source), "--project", str(self.project)]
        )
        self.assertEqual(result, 1)
        content = (
            self.project / ".agents/skills/example-skill/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("first", content)


if __name__ == "__main__":
    unittest.main()

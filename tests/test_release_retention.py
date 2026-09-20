from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY_ROOT / "scripts/select-obsolete-patch-tags.py"


def load_release_retention_module():
    spec = importlib.util.spec_from_file_location("release_retention_test", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


release_retention = load_release_retention_module()


class ReleaseRetentionTests(unittest.TestCase):
    def test_selects_only_older_patches_from_current_series(self) -> None:
        tags = [
            "v1.1.2",
            "v1.1.0",
            "v1.1.1",
            "v1.0.9",
            "v1.2.0",
            "v2.0.0",
            "v1.1.3",
        ]

        self.assertEqual(
            release_retention.obsolete_patch_tags("v1.1.2", tags),
            ["v1.1.0", "v1.1.1"],
        )

    def test_ignores_non_semver_and_prerelease_tags(self) -> None:
        tags = [
            "1.1.0",
            "v1.1",
            "v1.1.1-rc.1",
            "v1.01.1",
            "nightly",
        ]

        self.assertEqual(
            release_retention.obsolete_patch_tags("v1.1.2", tags), []
        )

    def test_rejects_invalid_current_tag(self) -> None:
        with self.assertRaisesRegex(ValueError, "vMAJOR.MINOR.PATCH"):
            release_retention.obsolete_patch_tags("1.1.2", ["v1.1.1"])

    def test_release_workflow_archives_records_before_removing_public_tags(self) -> None:
        workflow = (
            REPOSITORY_ROOT / ".github/workflows/release-skills.yml"
        ).read_text(encoding="utf-8")
        publish_step = workflow.index("- name: Publish or reconcile GitHub Release")
        archive_step = workflow.index("- name: Archive superseded patch releases")
        draft_command = workflow.index('gh release edit "$obsolete_tag" --draft')
        delete_tag_command = workflow.index(
            'git push origin ":refs/tags/${obsolete_tag}"'
        )

        self.assertLess(publish_step, archive_step)
        self.assertLess(archive_step, draft_command)
        self.assertLess(draft_command, delete_tag_command)
        self.assertNotIn('gh release delete "$obsolete_tag"', workflow)


if __name__ == "__main__":
    unittest.main()

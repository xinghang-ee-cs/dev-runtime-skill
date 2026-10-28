from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from test_runtime_skills import runtime, REPOSITORY_ROOT, SCRIPT


class InstallationContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / 'project'
        self.source = self.root / 'source'
        self.user_root = self.root / 'user/.agents/skills'
        self.name = 'example-skill'
        (self.source / 'scripts').mkdir(parents=True)
        shutil.copy2(SCRIPT, self.source / 'scripts/runtime-skills.py')
        self.rule = self.source / 'skills' / self.name
        (self.rule / 'references').mkdir(parents=True)
        (self.rule / 'SKILL.md').write_text('---\nname: example-skill\ndescription: fixture\n---\nshort entry\n')
        (self.rule / 'references/rules.md').write_text('# Rules\n\n## First\n' + '规则abc' * 2400 + '\n## Later\nDo not preload this stage.\n')
        (self.source / 'skills-manifest.json').write_text(json.dumps({
            'schema_version': 1, 'release_version': '1.0.0',
            'repository': {'url': 'https://github.com/example/runtime-skills', 'channel': 'stable'},
            'tool': {'version': runtime.TOOL_VERSION, 'path': 'scripts/runtime-skills.py'},
            'skills': {self.name: {'version': '1.0.0', 'path': 'skills/example-skill'}},
        }))
        patch = mock.patch.object(runtime, 'user_skill_roots', return_value=[self.user_root])
        patch.start()
        self.addCleanup(patch.stop)

    def run_tool(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = runtime.main(list(args))
        return code, output.getvalue()

    def install(self, destination='.agents/skills', *flags):
        return self.run_tool('install', '--source', str(self.source), '--project', str(self.project),
                             '--skill', self.name, '--destination', destination, *flags)

    def lock(self):
        return json.loads((self.project / runtime.LOCK_NAME).read_text())

    def make_copy(self, root, body='legacy'):
        target = root / self.name
        target.mkdir(parents=True)
        (target / 'SKILL.md').write_text('---\nname: example-skill\ndescription: legacy\n---\n' + body)
        return target

    def test_global_copy_blocks_install_even_with_overwrite(self):
        old = self.make_copy(self.user_root)
        result, message = self.install('.agents/skills', '--overwrite-local-changes')
        self.assertEqual(result, 1)
        self.assertIn('duplicate_skill', message)
        self.assertFalse((self.project / runtime.LOCK_NAME).exists())
        self.assertIn('legacy', (old / 'SKILL.md').read_text())

    def test_unregistered_project_copy_blocks_verify_and_sync(self):
        self.assertEqual(self.install()[0], 0)
        self.make_copy(self.project / '.claude/skills')
        before = (self.project / runtime.LOCK_NAME).read_bytes()
        for command in ('verify', 'sync'):
            code, output = self.run_tool(command, '--project', str(self.project))
            self.assertEqual(code, 2)
            self.assertIn('duplicate_skill', output)
        self.assertEqual(before, (self.project / runtime.LOCK_NAME).read_bytes())

    def test_new_platform_requires_explicit_addition(self):
        self.assertEqual(self.install()[0], 0)
        self.assertEqual(self.install('.claude/skills')[0], 1)
        self.assertFalse((self.project / '.claude/skills').exists())
        self.assertEqual(self.install('.claude/skills', '--add-destination')[0], 0)
        self.assertEqual(len(self.lock()['skills'][self.name]['destinations']), 2)

    def test_existing_lock_does_not_authorize_overwriting_new_target(self):
        self.assertEqual(self.install()[0], 0)
        old = self.make_copy(self.project / '.claude/skills', 'local work')
        before = (old / 'SKILL.md').read_bytes()
        self.assertEqual(self.install('.claude/skills', '--add-destination')[0], 1)
        self.assertEqual((old / 'SKILL.md').read_bytes(), before)
        self.assertEqual(self.install('.claude/skills', '--add-destination', '--overwrite-local-changes')[0], 0)
        self.assertNotEqual((old / 'SKILL.md').read_bytes(), before)

    def test_identical_install_does_not_rewrite_files_or_lock(self):
        self.assertEqual(self.install()[0], 0)
        paths = [self.project / runtime.LOCK_NAME, self.project / '.agents/skills' / self.name / 'SKILL.md']
        before = [(p.read_bytes(), p.stat().st_mtime_ns, p.stat().st_ino) for p in paths]
        self.assertEqual(self.install()[0], 0)
        self.assertEqual(before, [(p.read_bytes(), p.stat().st_mtime_ns, p.stat().st_ino) for p in paths])

    def test_relocate_archives_old_copy_and_updates_only_installation(self):
        self.assertEqual(self.install()[0], 0)
        state = self.project / '.runtime/phase/state.json'
        state.parent.mkdir(parents=True)
        state.write_text('keep this Runtime')
        old = self.project / '.agents/skills' / self.name
        original = (old / 'SKILL.md').read_bytes()
        code, output = self.run_tool('relocate', '--project', str(self.project), '--skill', self.name,
                                     '--from', '.agents/skills', '--to', '.claude/skills')
        self.assertEqual(code, 0, output)
        self.assertFalse(old.exists())
        self.assertEqual(self.lock()['skills'][self.name]['destinations'], ['.claude/skills/example-skill'])
        archives = list((self.project / '.runtime-skills/retired').rglob('SKILL.md'))
        self.assertEqual(len(archives), 1)
        self.assertEqual(archives[0].read_bytes(), original)
        self.assertEqual(state.read_text(), 'keep this Runtime')
        self.assertEqual(self.run_tool('verify', '--project', str(self.project))[0], 0)

    def test_relocate_failure_rolls_back_paths_and_lock(self):
        self.assertEqual(self.install()[0], 0)
        lock_path = self.project / runtime.LOCK_NAME
        before = lock_path.read_bytes()
        original_replace = runtime.os.replace
        failed = False
        def replace(source, destination):
            nonlocal failed
            if Path(destination) == lock_path and not failed:
                failed = True
                raise OSError('injected final lock failure')
            return original_replace(source, destination)
        with mock.patch.object(runtime.os, 'replace', side_effect=replace):
            with self.assertRaises(OSError):
                self.run_tool('relocate', '--project', str(self.project), '--skill', self.name,
                              '--from', '.agents/skills', '--to', '.claude/skills')
        self.assertEqual(before, lock_path.read_bytes())
        self.assertTrue((self.project / '.agents/skills/example-skill/SKILL.md').is_file())
        self.assertFalse((self.project / '.claude/skills/example-skill').exists())
        self.assertEqual(self.run_tool('verify', '--project', str(self.project))[0], 0)

    def test_pinned_phase_blocks_relocation(self):
        self.assertEqual(self.install()[0], 0)
        self.assertEqual(self.run_tool('pin', '--project', str(self.project), '--reason', 'phase-01')[0], 0)
        self.assertEqual(self.run_tool('relocate', '--project', str(self.project), '--skill', self.name,
                                       '--from', '.agents/skills', '--to', '.claude/skills')[0], 1)

    def test_doctor_reports_legacy_instructions_without_reading_them_into_output(self):
        self.assertEqual(self.install()[0], 0)
        instruction = self.project / 'AGENTS.md'
        instruction.write_text('PRIVATE_SENTINEL\n' * 2000)
        before = instruction.read_bytes()
        code, output = self.run_tool('doctor', '--project', str(self.project), '--json')
        self.assertEqual(code, 2)
        self.assertIn('instruction_review', output)
        self.assertNotIn('PRIVATE_SENTINEL', output)
        self.assertEqual(instruction.read_bytes(), before)

    def test_install_does_not_create_instructions_or_project_runtime(self):
        self.assertEqual(self.install()[0], 0)
        for name in ('AGENTS.md', 'CLAUDE.md', '.runtime', 'docs'):
            self.assertFalse((self.project / name).exists(), name)

    def test_context_pages_are_bounded_and_reconstruct_selected_section(self):
        self.assertEqual(self.install()[0], 0)
        prefix = ('context', '--project', str(self.project), '--skill', self.name, '--file', 'references/rules.md', '--section', '1')
        pieces = []
        for offset in (0, 6000, 12000):
            code, output = self.run_tool(*prefix, '--offset', str(offset))
            self.assertEqual(code, 0, output)
            payload = output.split('\n', 1)[1][:-1]
            self.assertLessEqual(len(payload), 6000)
            pieces.append(payload)
        original = runtime.markdown_sections((self.rule / 'references/rules.md').read_text())[1][1]
        self.assertEqual(''.join(pieces), original)
        self.assertNotIn('Later', ''.join(pieces))
        self.assertIn('next_offset=done', output)
        self.assertEqual(self.run_tool(*prefix, '--limit', '6001')[0], 1)
        self.assertEqual(self.run_tool('context', '--project', str(self.project), '--skill', self.name, '--file', '../outside.md')[0], 1)

    def test_outline_ignores_headings_in_fenced_examples(self):
        sections = runtime.markdown_sections('# Root\n```yaml\n# not a heading\n```\n## Actual\nbody\n')
        self.assertEqual([title for title, _ in sections], ['# Root', '## Actual'])

    def test_language_suffix_is_not_a_closing_fence(self):
        sections = runtime.markdown_sections('# Root\n```markdown\n```python\n# still code\n```\n## Actual\nbody\n')
        self.assertEqual([title for title, _ in sections], ['# Root', '## Actual'])

    def test_inventory_overflow_fails_closed(self):
        self.user_root.mkdir(parents=True)
        for index in range(runtime.DISCOVERY_LIMIT + 1):
            (self.user_root / f'item-{index}').mkdir()
        code, output = self.install()
        self.assertEqual(code, 1)
        self.assertIn('inventory_limit', output)

    def test_installer_rejects_home_as_project(self):
        with mock.patch.object(runtime.Path, 'home', return_value=self.project):
            self.assertEqual(self.install()[0], 1)
        self.assertFalse((self.project / runtime.LOCK_NAME).exists())

    def test_user_platform_subdirectory_cannot_be_used_as_a_project(self):
        home = self.root / 'simulated-home'
        with mock.patch.object(runtime.Path, 'home', return_value=home):
            for suffix in ('.claude', '.claude/skills', '.agents/skills', '.codex/skills/remote-skills'):
                self.project = home / suffix
                self.assertEqual(self.install('skills')[0], 1, suffix)
                self.assertFalse((self.project / runtime.LOCK_NAME).exists())

    def test_git_ancestor_copy_is_not_missed(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.project.mkdir()
        self.make_copy(self.root / '.agents/skills')
        code, output = self.install()
        self.assertEqual(code, 1)
        self.assertIn('ancestor copy', output)
        self.assertFalse((self.project / runtime.LOCK_NAME).exists())

    def test_overlapping_destinations_cannot_destroy_a_managed_copy(self):
        self.assertEqual(self.install()[0], 0)
        before = (self.project / runtime.LOCK_NAME).read_bytes()
        code, _ = self.install('.agents/skills/example-skill/children', '--add-destination')
        self.assertEqual(code, 1)
        self.assertEqual(before, (self.project / runtime.LOCK_NAME).read_bytes())

    def test_planning_initial_contract_fits_startup_budget(self):
        planning = REPOSITORY_ROOT / 'skills/planning-layer-runtime'
        paths = [planning / 'SKILL.md', planning / 'references/discovery-entry.md',
                 planning / 'references/09-execution-intent-guard.md']
        self.assertLessEqual(sum(len(path.read_text()) for path in paths), 12000)
        profile = paths[1].read_text()
        for field in ('discovery_checkpoint', 'active_interaction', 'explanation_adaptation',
                      'event_seq', 'next_action', '回读', '真实回答'):
            self.assertIn(field, profile)

    def test_all_distributed_entrypoints_are_small_and_self_contained(self):
        total = 0
        for entry in (REPOSITORY_ROOT / 'skills').glob('*/SKILL.md'):
            text = entry.read_text()
            total += len(text)
            self.assertLessEqual(len(text), 4000, entry.parent.name)
            for instruction in ('doctor', 'verify', 'sync', 'pin', 'unpin', '--outline', '--section', 'next_offset'):
                self.assertIn(instruction, text)
            self.assertTrue((entry.parent / 'references/runtime-governance.md').is_file())
        self.assertLessEqual(total, 14000)


if __name__ == '__main__':
    unittest.main()

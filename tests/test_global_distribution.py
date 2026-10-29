from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


runtime = module('global_test_runtime', ROOT / 'scripts/runtime-skills.py')
packages = module('global_test_packages', ROOT / 'scripts/build-install-packages.py')
bootstrap = module('global_test_bootstrap', ROOT / 'install.py')


class GlobalDistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.home = self.root / 'home'
        self.home.mkdir()
        self.project = self.root / 'project'
        self.project.mkdir()
        self.source = self.root / 'source'
        packages.copy_payload(ROOT, self.source, runtime)
        self.env = patch.dict(os.environ, {'HOME': str(self.home), 'USERPROFILE': str(self.home), 'CODEX_HOME': str(self.home / '.codex'), 'DSH_HOME': str(self.home / '.dsh'), 'DSH_AGENTS_HOME': str(self.home / '.agents'), 'RUNTIME_SKILLS_HOME': str(self.home / '.runtime-skills')})
        self.env.start()
        self.name = 'planning-layer-runtime'

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def run_cli(self, *args, success=True):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            result = runtime.main(list(args))
        if success:
            self.assertEqual(result, 0, output.getvalue())
        else:
            self.assertNotEqual(result, 0, output.getvalue())
        return output.getvalue()

    def install(self, agent='codex'):
        return self.run_cli('install-agent', '--source', str(self.source), '--agent', agent, '--skill', self.name, '--project', str(self.project))

    def bind(self, project=None):
        return self.run_cli('bind', '--project', str(project or self.project), '--skill', self.name)

    def lock(self, project=None):
        return runtime.read_json((project or self.project) / runtime.LOCK_NAME)

    def upgrade(self):
        manifest = runtime.read_json(self.source / runtime.MANIFEST_NAME)
        manifest['release_version'] = '2.1.0'
        manifest['skills'][self.name]['version'] = '2.1.0'
        runtime.write_json_atomic(self.source / runtime.MANIFEST_NAME, manifest)
        with (self.source / 'skills' / self.name / 'SKILL.md').open('a') as stream:
            stream.write('\nNEW RELEASE SENTINEL\n')

    def test_native_install_is_global_and_noop_preserves_mtimes(self):
        self.install()
        self.assertEqual(list(self.project.iterdir()), [])
        router = self.home / '.agents/skills' / self.name
        self.assertTrue((router / 'scripts/runtime-skills.py').is_file())
        before = {path: path.stat().st_mtime_ns for path in self.home.rglob('*') if path.is_file()}
        self.install()
        self.assertEqual(before, {path: path.stat().st_mtime_ns for path in self.home.rglob('*') if path.is_file()})

    def test_codex_copilot_dsh_share_one_router(self):
        for agent in ('codex', 'copilot', 'dsh'):
            self.install(agent)
        self.assertEqual(len(runtime.global_registry()['routers']), 1)
        self.assertFalse((self.home / '.dsh/skills').exists())
        self.bind()
        self.run_cli('verify', '--project', str(self.project))

    def test_claude_root_and_dsh_agents_override(self):
        self.install('claude')
        self.assertTrue((self.home / '.claude/skills' / self.name).is_dir())
        with patch.dict(os.environ, {'DSH_AGENTS_HOME': str(self.home / 'custom-agents')}):
            self.install('dsh')
            self.assertTrue((self.home / 'custom-agents/skills' / self.name).is_dir())
            self.bind()
            self.run_cli('verify', '--project', str(self.project))

    def test_upgrade_does_not_change_old_project_or_active_phase(self):
        self.install()
        self.bind()
        self.run_cli('pin', '--project', str(self.project), '--reason', 'phase-1')
        original = (self.project / runtime.LOCK_NAME).read_bytes()
        self.upgrade()
        self.install()
        self.assertEqual(original, (self.project / runtime.LOCK_NAME).read_bytes())
        self.run_cli('sync', '--project', str(self.project))
        old = self.run_cli('session', '--project', str(self.project), '--skill', self.name)
        self.assertNotIn('NEW RELEASE SENTINEL', old)
        self.run_cli('adopt', '--project', str(self.project), '--allow', 'major', success=False)
        self.assertEqual(original, (self.project / runtime.LOCK_NAME).read_bytes())
        other = self.root / 'other'; other.mkdir()
        self.bind(other)
        self.assertEqual(self.lock(other)['skills'][self.name]['version'], '2.1.0')
        self.run_cli('unpin', '--project', str(self.project))
        self.run_cli('adopt', '--project', str(self.project), success=False)
        self.run_cli('adopt', '--project', str(self.project), '--allow', 'minor')
        self.assertEqual(self.lock()['skills'][self.name]['version'], '2.1.0')

    def test_missing_cache_never_uses_new_default_and_exact_restore(self):
        self.install(); self.bind()
        original = (self.project / runtime.LOCK_NAME).read_bytes()
        identity = self.lock()['skills'][self.name]['cache_id']
        shutil.rmtree(runtime.global_home() / 'bundles' / identity)
        self.run_cli('session', '--project', str(self.project), '--skill', self.name, success=False)
        self.run_cli('restore-cache', '--project', str(self.project), '--source', str(self.source))
        self.run_cli('verify', '--project', str(self.project))
        self.assertEqual(original, (self.project / runtime.LOCK_NAME).read_bytes())

    def test_wrong_restore_source_does_not_change_cache_or_lock(self):
        self.install(); self.bind(); self.upgrade()
        before = self.lock()
        existing = sorted((runtime.global_home() / 'bundles').iterdir())
        self.run_cli('restore-cache', '--project', str(self.project), '--source', str(self.source), success=False)
        self.assertEqual(before, self.lock())
        self.assertEqual(existing, sorted((runtime.global_home() / 'bundles').iterdir()))

    def test_corrupt_cache_and_router_are_not_silently_overwritten(self):
        self.install(); self.bind()
        root, _ = runtime.cached_skill(self.name, self.lock()['skills'][self.name])
        (root / 'SKILL.md').write_text('corrupted')
        self.run_cli('verify', '--project', str(self.project), success=False)
        self.install_failure()
        self.assertEqual((root / 'SKILL.md').read_text(), 'corrupted')

    def install_failure(self):
        return self.run_cli('install-agent', '--source', str(self.source), '--agent', 'codex', '--skill', self.name, '--project', str(self.project), success=False)

    def test_unmanaged_same_name_and_project_copy_block_install(self):
        for relative in ('.agents/skills', '.dsh/skills', '.copilot/skills'):
            target = self.home / relative / self.name
            target.mkdir(parents=True)
            (target / 'SKILL.md').write_text(f'---\nname: {self.name}\ndescription: existing\n---\n')
            self.install_failure()
            self.assertFalse((runtime.global_home() / 'registry.json').exists())
            shutil.rmtree(target)
        target = self.project / '.claude/skills' / self.name
        target.mkdir(parents=True)
        shutil.copyfile(self.source / 'skills' / self.name / 'SKILL.md', target / 'SKILL.md')
        self.install_failure()

    def test_concurrent_writer_and_different_phase_refused(self):
        self.install(); self.bind()
        guard = runtime.global_home() / '.write-lock'; guard.mkdir()
        self.run_cli('bind', '--project', str(self.project), '--skill', self.name, success=False)
        guard.rmdir()
        self.run_cli('pin', '--project', str(self.project), '--reason', 'A')
        self.run_cli('pin', '--project', str(self.project), '--reason', 'B', success=False)
        self.assertEqual(self.lock()['phase_pin']['reason'], 'A')

    def test_migration_archives_all_project_copies_and_preserves_memory(self):
        self.run_cli('install', '--source', str(self.source), '--project', str(self.project), '--skill', self.name, '--destination', '.agents/skills', '--destination', '.claude/skills')
        memory = self.project / '.runtime/memory.txt'; memory.parent.mkdir(); memory.write_text('project facts')
        elsewhere = self.root / 'neutral'; elsewhere.mkdir()
        self.run_cli('install-agent', '--source', str(self.source), '--agent', 'codex', '--skill', self.name, '--project', str(elsewhere))
        self.run_cli('bind', '--project', str(self.project), '--skill', self.name, success=False)
        self.run_cli('bind', '--project', str(self.project), '--migrate-project', '--allow', 'major')
        self.assertEqual(memory.read_text(), 'project facts')
        self.assertFalse((self.project / '.agents/skills' / self.name).exists())
        self.assertFalse((self.project / '.claude/skills' / self.name).exists())
        self.assertEqual(len(list((self.project / '.runtime-skills/retired').glob('*/[01]/SKILL.md'))), 2)
        self.assertEqual(self.lock()['schema_version'], 2)
        self.run_cli('verify', '--project', str(self.project))

    def test_package_generation_is_reproducible_and_import_executes_offline(self):
        output = self.root / 'packages'
        second = self.root / 'packages2'
        index = packages.build(ROOT, output)
        packages.build(ROOT, second)
        self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()}, {p.name: p.read_bytes() for p in second.iterdir()})
        self.assertEqual(len([a for a in index['artifacts'] if a['kind'] == 'global-installer']), 4)
        for platform in ('doubao', 'workbuddy'):
            extract = self.root / platform; extract.mkdir()
            with zipfile.ZipFile(output / f'runtime-skills-{platform}-{self.name}.zip') as archive:
                archive.extractall(extract)
            skill = extract / self.name
            text = (skill / 'SKILL.md').read_text()
            self.assertIn('session --project', text)
            if platform == 'workbuddy':
                for key in ('display_name:', 'display_name_en:', 'description_zh:', 'description_en:', 'version:', 'author:'):
                    self.assertIn(key, text)
            project = self.root / (platform + '-project'); project.mkdir()
            result = subprocess.run([sys.executable, str(skill / 'scripts/runtime-skills.py'), 'session', '--project', str(project), '--skill', self.name], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('[runtime-tool=', result.stdout)
            self.assertFalse((project / '.agents').exists())
            self.assertEqual(self.lock(project)['storage'], 'global')
            self.assertFalse((skill / runtime.LOCK_NAME).exists())

    def test_detection_requires_one_cli_or_explicit_current_agent(self):
        for implementation in (runtime, bootstrap):
            with patch.object(implementation.shutil, 'which', side_effect=lambda x: '/bin/' + x if x in ('codex', 'dsh') else None):
                with self.assertRaises((ValueError, runtime.RuntimeSkillsError)):
                    implementation.select_agent('auto')
            with patch.dict(os.environ, {'RUNTIME_SKILLS_AGENT': 'dsh'}):
                self.assertEqual(implementation.select_agent('auto'), 'dsh')

    def test_bootstrap_checksum_failure_performs_no_install(self):
        release = {'tag_name': 'v2.0.0', 'assets': [{'name': name, 'browser_download_url': f'https://github.com/{bootstrap.REPOSITORY}/releases/download/v2.0.0/{name}'} for name in ('runtime-skills-dsh.zip', 'SHA256SUMS')]}
        with patch.object(sys, 'argv', ['install.py', '--agent', 'dsh']), patch.object(bootstrap, 'fetch', side_effect=[json.dumps(release).encode(), b'wrong  runtime-skills-dsh.zip', b'payload']), patch.object(bootstrap.subprocess, 'run') as run:
            self.assertEqual(bootstrap.main(), 1)
            run.assert_not_called()

    def test_phase_handoff_adds_only_same_release_skill(self):
        self.run_cli('install-agent', '--source', str(self.source), '--agent', 'codex')
        self.bind()
        self.run_cli('pin', '--project', str(self.project), '--reason', 'phase-1')
        self.run_cli('session', '--project', str(self.project), '--skill', 'long-task-orchestrator')
        self.assertEqual(self.lock()['phase_pin']['reason'], 'phase-1')
        self.assertEqual(len(self.lock()['skills']), 2)
        self.upgrade()
        self.run_cli('install-agent', '--source', str(self.source), '--agent', 'codex')
        before = self.lock()
        self.run_cli('session', '--project', str(self.project), '--skill', 'testing-layer-runtime', success=False)
        self.assertEqual(before, self.lock())

    def test_native_local_installer_runs_without_source_read(self):
        output = self.root / 'packages'
        packages.build(ROOT, output)
        extracted = self.root / 'native'; extracted.mkdir()
        with zipfile.ZipFile(output / 'runtime-skills-dsh.zip') as archive:
            archive.extractall(extracted)
        self.assertIn('install-local.py', (extracted / 'INSTALL.md').read_text())
        result = subprocess.run([sys.executable, str(extracted / 'install-local.py'), '--skill', self.name, '--project', str(self.project)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_import_reimport_new_version_can_be_adopted_without_native_install(self):
        imported = self.root / 'import-source'
        packages.copy_payload(self.source, imported, runtime, [self.name])
        args = runtime.build_parser().parse_args(['bind', '--project', str(self.project), '--skill', self.name])
        runtime.command_bind(args, ROOT / 'scripts/runtime-skills.py', imported=imported)
        before = self.lock()
        self.upgrade()
        shutil.rmtree(imported)
        packages.copy_payload(self.source, imported, runtime, [self.name])
        runtime.command_bind(args, ROOT / 'scripts/runtime-skills.py', imported=imported)
        self.assertEqual(before, self.lock())
        self.run_cli('adopt', '--project', str(self.project), '--allow', 'minor')
        self.assertEqual(self.lock()['skills'][self.name]['version'], '2.1.0')

    def test_global_install_rollback_keeps_router_and_registry(self):
        self.install()
        registry = (runtime.global_home() / 'registry.json').read_bytes()
        router = self.home / '.agents/skills' / self.name
        digest = runtime.content_hash(router)
        self.upgrade()
        replace = runtime.os.replace
        def fail(source, destination):
            if Path(destination) == runtime.global_home() / 'registry.json' and 'staged' in Path(source).parts:
                raise OSError('injected registry replace failure')
            return replace(source, destination)
        with patch.object(runtime.os, 'replace', side_effect=fail), self.assertRaises(OSError):
            self.install()
        self.assertEqual(registry, (runtime.global_home() / 'registry.json').read_bytes())
        self.assertEqual(digest, runtime.content_hash(router))

    def test_bundle_major_requires_acceptance_when_skill_version_is_unchanged(self):
        self.install(); self.bind()
        manifest = runtime.read_json(self.source / runtime.MANIFEST_NAME)
        manifest['release_version'] = '3.0.0'
        runtime.write_json_atomic(self.source / runtime.MANIFEST_NAME, manifest)
        self.install()
        before = self.lock()
        self.run_cli('adopt', '--project', str(self.project), success=False)
        self.assertEqual(before, self.lock())
        self.run_cli('adopt', '--project', str(self.project), '--allow', 'major')
        self.assertEqual(self.lock()['skills'][self.name]['release'], '3.0.0')

    def test_unsafe_zip_member_refused(self):
        archive = self.root / 'unsafe.zip'
        with zipfile.ZipFile(archive, 'w') as zip_file:
            zip_file.writestr('../escape', 'bad')
        with self.assertRaises(ValueError):
            bootstrap.extract(archive, self.root / 'extracted')
        self.assertFalse((self.root / 'escape').exists())


if __name__ == '__main__':
    unittest.main()

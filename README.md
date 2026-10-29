# Runtime Skills

One source tree generates user-global Agent installers and self-contained platform import packages. Static rules and tools live at user scope; project facts, progress, checkpoints and exact version locks stay in each project.

Ask your AI to read [INSTALL.md](INSTALL.md), identify its current Agent, inspect existing same-name copies and install only that Agent's global package. Stop after installation; do not initialize business state or create AGENTS.md/CLAUDE.md.

New stable download paths become available after this change is merged and released. Download and review [install.py](https://github.com/xinghang-ee-cs/dev-runtime-skill/releases/latest/download/install.py), then run:

```bash
python install.py --agent codex --project /path/to/project
```

Choose `codex`, `claude`, `copilot` or DeepSeek Harness `dsh`. Repeat `--skill <name>` to select individual Skills. Auto selection requires RUNTIME_SKILLS_AGENT or exactly one supported CLI on PATH; ambiguous detection makes no installation. Do not infer active Agents from old directories.

| Target | Installation |
| --- | --- |
| Codex / Copilot / dsh | Shared personal `~/.agents/skills`; dsh honors DSH_AGENTS_HOME |
| Claude Code | Personal `~/.claude/skills` |
| Doubao Work | Import each `runtime-skills-doubao-<skill>.zip` through the supported upload UI |
| WorkBuddy | Add Skill → Upload Skill, one `runtime-skills-workbuddy-<skill>.zip` per Skill |

Import packages include tools and canonical rule payloads. They require Python 3.10+, file permissions and a persistent selected project directory. Marketplace onboarding/review is separate; do not guess undocumented local application directories or simulate unsupported capabilities.

Four Skills: planning-layer-runtime (planning), long-task-orchestrator (implementation), testing-layer-runtime (acceptance), ai-code-inspection (diagnosis). Native discovery contains thin version routers. On first real use, session binds the selected Skill to an exact global cache and returns its actual rule/tool paths. Never resolve resources from the project's current working directory. Installation creates no project Skill copies.

Global cache: `~/.runtime-skills/bundles/<sha256>` (override using RUNTIME_SKILLS_HOME). Project lock schema 2 stores exact content identities. Updating global defaults cannot mutate existing projects, including active phases. `sync` verifies only; close/unpin a phase before explicit `adopt --allow patch|minor|major`. Old caches are retained. A missing or modified cache stops execution; restore the exact source, never substitute latest. Keep exact source packages for migration between machines, particularly when old public patch tags are archived.

Legacy project-copy locks remain supported. Close the phase and verify before explicit `bind --migrate-project --allow major`. Managed copies are archived outside discovery transactionally; project memory stays put. Unmanaged copies and user instruction files require an explicit cleanup decision. See [INSTALL.md](INSTALL.md) and [中文说明](README.zh-CN.md).

Maintainer validation of unpublished source:

```bash
python scripts/runtime-skills.py install-agent --source . --agent codex --project /path/to/project
python scripts/build-install-packages.py --output /tmp/runtime-packages
python -m unittest discover -s tests -p 'test_*.py'
python scripts/validate-skill-manifest.py
```

Build output includes four native ZIPs, eight single-Skill import ZIPs, the installer, installation guide, install-manifest.json and SHA256SUMS. Platform metadata is generated from distribution/, with skills/ as the only rule source. CI preserves reviewable artifacts. Existing PR-based release governance applies.

Context remains staged: load one Skill and only its current rules, at most 6,000 characters per context read. This is not a whole-session token guarantee.

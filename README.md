# AI Development Runtime Skills

[English](README.md) | [简体中文](README.zh-CN.md)

Four independent skills for planning, implementation, testing, and code diagnosis. `skills-manifest.json` owns published versions; a project's `runtime-skills.lock.json` owns its actual installed copies. The documentation site's package version is unrelated.

## Install without starting a workflow

Ask the Agent working in your target project:

```text
Install selected Runtime Skills from https://github.com/xinghang-ee-cs/dev-runtime-skill into this project only. Do not start planning, interview me, scan business source, or initialize all Runtime environments.
Select the current actual platform, not every platform suggested by stale directories. Use .agents/skills for Codex, .claude/skills for Claude Code, or the project's supported Copilot location. Add multiple destinations only when explicitly requested or required by this task. Never install another global copy.
Fetch the source Release into temporary storage outside Skill discovery paths. Do not copy the source AGENTS.md, README, docs site, or workflows.
Use the trusted source tool's doctor --project <root>, repeating --skill for selected names on a new project. Resolve duplicate user/ancestor/project copies, incomplete inventories, and drift before installing. Report legacy oversized instructions without deleting or rewriting them. Inspect any platform-specific additional or nested discovery directories separately.
Run scripts/runtime-skills.py install --release latest --project <root> with selected --skill names and the current --destination. For an existing lock, verify and review status/diff first. Additional platform copies require --add-destination; use relocate to move a copy. Do not silently override local changes or an active phase pin. Confirm minor/major updates.
Do not create AGENTS.md or CLAUDE.md, prebuild Runtime state, edit business code, deploy, commit, or push. Run the installed tool's verify, report versions and exact paths, then stop.
```

Available names are `planning-layer-runtime`, `long-task-orchestrator`, `testing-layer-runtime`, and `ai-code-inspection`. Select only what you need. The managed installer is project-local and refuses Home/Codex user roots as projects; native personal/global installations remain the platform's responsibility.

## Deployment and migration

```bash
python scripts/runtime-skills.py doctor --project /path/to/project --skill planning-layer-runtime
python scripts/runtime-skills.py install --release latest --project /path/to/project --skill planning-layer-runtime --destination .agents/skills
python /path/to/project/.runtime-skills/runtime-skills.py verify --project /path/to/project
```

Identical repeated installation does not rewrite files or the lock. Complete selected packages, the project sync tool, and the lock are installed; business initialization is deferred until an actual task needs it.

Add another intentionally used platform with `install ... --destination .claude/skills --add-destination`. Every previously unmanaged target requires review and explicit `--overwrite-local-changes` adoption, even if a lock already exists. This flag never bypasses duplicate-scope conflicts.

Move a managed copy instead of accumulating paths:

```bash
python .runtime-skills/runtime-skills.py relocate --project . --skill planning-layer-runtime --from .agents/skills --to .claude/skills
```

Relocation requires no active pin, no drift or discovery conflicts, and an absent destination. It atomically updates the lock, archives old content under `.runtime-skills/retired/`, and removes the old discovery path, with rollback on failure. It neither upgrades versions nor moves project Runtime data. Global/unmanaged copies require a separate explicit resolution.

## Diagnose legacy installations

`doctor` reads bounded known project, Git-ancestor, and user discovery roots, Skill metadata, and instruction sizes. It does not recursively read application code or echo instruction bodies. It reports unregistered same-name skills, managed drift, incomplete/unreadable inventories, instruction files above 12 KB, and duplicate routing blocks. Instruction size findings require human review; they are not proof of corruption and never trigger automatic rewriting. Additional configured directories and nested monorepo skills must be inspected explicitly.

Reuse existing instructions only if needed, in at most one marked routing block with at most 10 nonempty lines and 1200 characters. Never create a new instruction file merely for installation or first use. Each distributed SKILL.md carries sync/pin/unpin rules independently.

## Start one selected skill

After installation, make a separate request such as “Use planning-layer-runtime to start this phase's discovery.” Load one entrypoint and only the current stage's necessary sections. Planning hands off to Long, then Testing and the project's release process. Confirmed implementation defects with valid contracts use a Bugfix Case without rewriting original 00–15 documents. Production retest and similar-defect verification precede Case closure.

Full governance remains in each `references/runtime-governance.md` and the existing topic references. Do not preload complete governance, all references, other skills, templates, or historical logs. Discover only missing project facts relevant to the current action.

## Synchronize and pin

Run doctor on the first use in a session. New phase: sync → pin → create phase state. Existing active phase: verify → pin the existing phase if missing → sync, which then verifies without updating. Do not repeat synchronization within a session unless the lock changes. Only unpin after closure or explicit controlled-migration approval.

```bash
python .runtime-skills/runtime-skills.py sync --project .
python .runtime-skills/runtime-skills.py pin --project . --reason phase-01
# After phase closure:
python .runtime-skills/runtime-skills.py unpin --project .
```

Sync automatically applies only compatible PATCH updates. MINOR/MAJOR updates need confirmation. Use stable `--release latest`; maintainers use `--source` only for unreleased validation. Review `status --check-remote` and `diff` before updating. Package updates do not automatically migrate all Runtime epochs or rerun whole-phase validation; actual schema migrations are separate scoped recovery tasks, and closed history stays read-only.

## Read bounded rule sections

```bash
python .runtime-skills/runtime-skills.py context --project . --skill planning-layer-runtime --file references/07-planning-conversation-runtime.md --outline
python .runtime-skills/runtime-skills.py context --project . --skill planning-layer-runtime --file references/07-planning-conversation-runtime.md --section 1
```

Rule bodies are limited to 6000 characters per call. Continue with the same arguments and `--offset <next_offset>` until `done`; child headings are separate sections and all applicable gate sections must be read before action. Target at most 12000 static-rule characters for initial routing, then expand by the current gate with a reason. This is not a guarantee about total session tokens, application documents, tool output, or client-injected instructions. Reuse unchanged already-read sections; restore compact checkpoints/current state before reading historical evidence.

## Validate

```bash
python scripts/validate-skill-manifest.py
python -m unittest discover -s tests -p 'test_*.py'
```

Tutorials live under `src/content/docs/`. The docs website files are not installed. Repository changes follow AGENTS.md: Issue → dedicated branch → PR → CI → merge through PR. Do not copy maintenance rules to target projects.
